import unittest
from queue import Empty, Queue

from server.comm.transport.transport import *


class IMockTransportEndpoint(ABC):

    def on_packet(self, packet: bytes) -> Optional[bytes]:
        raise NotImplementedError


class MockTransport(ITransport, AbstractConnection):

    def __init__(self, endpoint, client):
        super().__init__(client)
        self.message_queue: List[MockTransport.PendingPacket] = []
        self.endpoint: IMockTransportEndpoint = endpoint
        self.client: ITransportClient = client

    def send(self, packet: bytes) -> IOutgoingPacket:
        logging.debug("send():")
        pending = MockTransport.PendingPacket(self, packet)
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
        logging.debug(f"pump_pending_messages(): state={self.state}")
        if self.state == ConnectionState.DISCONNECTED:
            self.reconnect()

        while self.message_queue:
            packet = self.message_queue.pop(0)
            packet.send()

    def mock_packet(self, packet: bytes):
        self.client.on_packet_received(packet)

    class PendingPacket(AbstractOutgoingPacket):

        def __init__(self, transport, packet):
            super().__init__(packet, Future())
            self.transport: MockTransport = transport

        def send(self):
            assert self.transport.state == ConnectionState.CONNECTED
            logging.debug("send(): Sending to mocked endpoint")
            response = self.transport.endpoint.on_packet(self.packet)
            self.future.set_result(self)

            if response is not None:
                logging.debug("send(): Sending to mocked endpoint")
                self.transport.mock_packet(response)


class LoopbackTransport(MockTransport):

    def __init__(self, client):
        super().__init__(LoopbackTransport.Endpoint(), client)

    class Endpoint(IMockTransportEndpoint):

        def on_packet(self, packet: bytes) -> Optional[bytes]:
            return packet

    class Builder(ITransportBuilder):
        def construct(self, client: ITransportClient, runner: Runner = None):
            return LoopbackTransport(client)


class PacketLoopbackTest(unittest.TestCase):

    @staticmethod
    def setUpClass(**kwargs) -> None:
        import sys
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                            format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')

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
        transport = Transport.Builder(LoopbackTransport.Builder()).build(client)
        transport.reconnect()

        packets = []

        for i in range(10):
            packet = f"Test {i} packet".encode("utf-8")
            logging.info(f"test: Sending {packet.decode('utf-8')}")
            packets.append(transport.send(packet))

        for packet in packets:
            received: bytes = queue.get()  # timeout=5.0)

            self.assertIsNotNone(packet)
            logging.info(f"test: Dequeued {received.decode('utf-8')}")
            self.assertSequenceEqual(received, packet.packet)

        try:
            queue.get(timeout=1.0)
            self.fail("Received more messages then expected")
        except Empty:
            pass

        transport.disconnect()

        del transport


class SocketPairTransportTest(unittest.TestCase):

    @staticmethod
    def setUpClass(**kwargs) -> None:
        import sys
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                            format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')

    @staticmethod
    def pair_transport(client_a: ITransportClient, client_b: ITransportClient):
        sock_a, sock_b = socket.socketpair()

        transport_a = Transport.Builder(
                transport=SocketTransport.Builder(socket=sock_a, addr=None)).build(client_a)
        transport_b = Transport.Builder(
                transport=SocketTransport.Builder(socket=sock_b, addr=None)).build(client_b)

        return transport_a, transport_b

    def test_both_ways(self):
        class Client(ITransportClient):

            def __init__(self, name: str, queue: Queue):
                self._name = name
                self._queue = queue

            def on_packet_received(self, packet: bytes):
                logging.debug(f"test_socket_pair_transport(): #{self._name} packet = {packet}")
                self._queue.put(packet)

            def on_state_changed(self, state: ConnectionState):
                logging.debug(f"test_socket_pair_transport(): #{self._name} state = {state}")

        queue_a = Queue()
        queue_b = Queue()
        transport_a, transport_b = self.pair_transport(Client("a", queue_a), Client("b", queue_b))
        transport_a.reconnect()
        transport_b.reconnect()
        transport_a.send(b"Test 123")
        transport_b.send(b"Test 321")

        self.assertEqual(queue_a.get(), b"Test 321")
        self.assertEqual(queue_b.get(), b"Test 123")

        transport_a.disconnect()
        transport_b.disconnect()

        del transport_a
        del transport_b

    def test_ping_pong(self):
        class ClientA(ITransportClient):
            def __init__(self, event: threading.Event):
                self.transport = None
                self._event = event
                self._count = 0

            def on_packet_received(self, packet: bytes):
                logging.debug(f"on_packet_received(): count = {self._count} got {packet}")
                if self._count > 100:
                    self._event.set()
                    return

                self._count += 1
                self.transport.send(b"Ping")

            def on_state_changed(self, state: ConnectionState):
                pass

        class ClientB(ITransportClient):
            def __init__(self):
                self.transport = None

            def on_packet_received(self, packet: bytes):
                logging.debug(f"on_packet_received(): got {packet}")
                self.transport.send(b"Pong")

            def on_state_changed(self, state: ConnectionState):
                pass

        event = threading.Event()
        client_a = ClientA(event)
        client_b = ClientB()
        transport_a, transport_b = self.pair_transport(client_a, client_b)
        client_a.transport = transport_a
        client_b.transport = transport_b

        transport_a.reconnect()
        transport_b.reconnect()

        transport_a.send(b"Ping")

        event.wait()

        client_a.transport = None
        client_b.transport = None

        transport_a.disconnect()
        transport_b.disconnect()

        del transport_a
        del transport_b


if __name__ == '__main__':
    import sys

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
    unittest.main()
