import logging
import threading
import unittest
from abc import ABC
from concurrent.futures import Future
from queue import Queue, Empty
from threading import Timer
from typing import List, Optional

from server.comm.connection import AbstractConnection, ConnectionState
from server.comm.transport.transport import ITransport, IOutgoingPacket, ITransportClient
from server.comm.transport.transport import Transport


class IMockTransportEndpoint(ABC):

    def on_packet(self, packet: bytes) -> Optional[bytes]:
        raise NotImplementedError


def test_timeout(timeout):
    def decorator(func):
        def wrapper(*args, **kwargs):
            import ctypes
            exception = ctypes.py_object(TimeoutError)
            tid = threading.current_thread().ident
            timer = Timer(timeout,
                          ctypes.pythonapi.PyThreadState_SetAsyncExc,
                          (tid, exception))

            timer.start()
            func(*args, **kwargs)
            timer.cancel()

        return wrapper

    return decorator


class MockTransport(ITransport, AbstractConnection):

    def __init__(self, endpoint, client):
        super().__init__(client)
        self.message_queue: List[MockTransport.PendingPacket] = []
        self.endpoint: IMockTransportEndpoint = endpoint
        self.client: ITransportClient = client

    def send(self, packet: bytes) -> IOutgoingPacket:
        logging.debug("send():")
        pending = MockTransport.PendingPacket(packet)
        self.message_queue.append(pending)
        self.pump_pending_messages()
        return pending

    def reconnect(self):
        logging.debug("reconnect():")
        if self.state == ConnectionState.CONNECTED:
            logging.debug("reconnect(): Already connected")
            self.state = ConnectionState.DISCONNECTING
            self.state = ConnectionState.DISCONNECTED

        assert self.state == ConnectionState.DISCONNECTED

        self.state = ConnectionState.CONNECTING
        self.state = ConnectionState.CONNECTED

    def disconnect(self):
        logging.debug("disconnect():")
        if self.state == ConnectionState.DISCONNECTED:
            logging.debug("reconnect(): Already disconnected")
            return

        assert self.state == ConnectionState.CONNECTED

        self.state = ConnectionState.DISCONNECTING
        self.state = ConnectionState.DISCONNECTED

    def pump_pending_messages(self):
        logging.debug("pump_pending_messages():")
        if self.state == ConnectionState.CONNECTED:
            self.reconnect()

        while self.message_queue:
            packet = self.message_queue.pop(0)
            packet.send()

    def mock_packet(self, packet: bytes):
        self.client.on_packet_received(packet)

    class PendingPacket(IOutgoingPacket):

        def __init__(self, transport, packet):
            self.transport: MockTransport = transport
            self.packet: bytes = packet
            self.future = Future()

        def send(self):
            assert self.transport.state == ConnectionState.CONNECTED
            logging.debug("send(): Sending to mocked endpoint")
            response = self.transport.endpoint.on_packet(self.packet)
            if response is not None:
                logging.debug("send(): Sending to mocked endpoint")
                self.transport.mock_packet(response)


class LoopbackTransport(MockTransport):

    def __init__(self, client):
        super().__init__(LoopbackTransport.Endpoint(), client)

    class Endpoint(IMockTransportEndpoint):

        def on_packet(self, packet: bytes) -> Optional[bytes]:
            return packet


class PacketLoopbackTest(unittest.TestCase):

    def setUp(self) -> None:
        import sys
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    @test_timeout(10.0)
    def test_loopback_send_received(self):
        test_self = self
        queue = Queue()

        class Client(ITransportClient):

            def on_packet_received(self, packet: bytes):
                logging.debug(f"on_packet_received(): packet={packet.decode('utf-8')}")
                queue.put(packet)

            def on_state_changed(self, state: ConnectionState):
                pass

            def on_error(self):
                nonlocal test_self
                test_self.fail("on_error():")

        client = Client()
        transport = Transport(LoopbackTransport, client)

        packets = []

        for i in range(10):
            packet = f"Test {i} packet".encode("utf-8")
            packets.append(transport.send(packet).future.result())

        for packet in packets:
            received: bytes = queue.get(block=True)

            self.assertIsNotNone(packet)
            logging.info(f"dequeued {received.decode('utf-8')}")
            self.assertSequenceEqual(received, packet.packet)

        try:
            queue.get(timeout=1.0)
            self.fail("Received more messages then expected")
        except Empty:
            pass


if __name__ == '__main__':
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    unittest.main()
