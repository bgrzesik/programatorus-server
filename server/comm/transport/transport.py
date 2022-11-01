import functools
import logging
import os
import select
import socket
import threading
from abc import ABC
from concurrent.futures import Future
from typing import List, Optional

from server.actor import Actor
from server.comm.connection import IConnection, IConnectionClient, AbstractConnection, ConnectionState

RECONNECT_TIMEOUT = 2.0  # seconds
MAX_ERROR_COUNT = 4


class IOutgoingPacket(ABC):

    @property
    def packet(self) -> bytes:
        raise NotImplementedError

    @property
    def future(self) -> Future:
        raise NotImplementedError


class AbstractOutgoingPacket(IOutgoingPacket, ABC):

    def __init__(self, packet, future=None):
        self._packet: bytes = packet
        self._future: Future = future or Future()

    @property
    def packet(self) -> bytes:
        return self._packet

    @property
    def future(self) -> Future:
        return self._future


class ITransportClient(IConnectionClient, ABC):

    def on_packet_received(self, packet: bytes):
        raise NotImplementedError


class ProxyTransportClient(ITransportClient, Actor):

    def __init__(self, impl, parent=None, executor=None):
        super().__init__(parent=parent, executor=executor)
        self.impl: ITransportClient = impl

    @Actor.handler()
    def on_packet_received(self, packet: bytes):
        self.impl.on_packet_received(packet)

    @Actor.handler()
    def on_state_changed(self, state: ConnectionState):
        self.impl.on_state_changed(state)

    @Actor.handler()
    def on_error(self):
        self.impl.on_error()


class ITransport(IConnection, ABC):

    def send(self, packet: bytes) -> IOutgoingPacket:
        raise NotImplementedError


class Transport(ITransport, AbstractConnection, Actor):

    def __init__(self, impl_provider, client):
        Actor.__init__(self)
        client = Transport.Client(self, client)
        AbstractConnection.__init__(self, client)
        self._client = client
        self._impl: ITransport = impl_provider(self._client)
        self._been_connected = False
        self.pending_packets: List[Transport.OutgoingPacket] = []
        self.error_count = 0

    @property
    def state(self):
        return self._impl.state

    @property
    def supports_reconnecting(self):
        return self._impl.supports_reconnecting

    def send(self, packet: bytes) -> IOutgoingPacket:
        logging.debug(f"send(): Enqueueing packet for sending pending={len(self.pending_packets)}")
        outgoing = Transport.OutgoingPacket(self, packet)
        self.pending_packets.append(outgoing)

        if not self.is_guarded_pending(self.reconnect):
            self.transport_task()

        return outgoing

    @Actor.handler(guarded=True)
    def reconnect(self):
        logging.debug("reconnect():")
        if self._been_connected and not self.supports_reconnecting:
            # TODO(bgrzesik): some how remove this object
            logging.warning("reconnect(): This transport does not support reconnecting")
            self.disconnect()
            return

        self._impl.reconnect()

    @Actor.handler(guarded=True)
    def disconnect(self):
        logging.debug("disconnect():")
        if self.state != ConnectionState.CONNECTED:
            logging.debug("disconnect(): Transport not connected")
            return

        self._impl.disconnect()

    @Actor.handler(guarded=True, force_schedule=True)
    def transport_task(self):
        state = self.state
        logging.debug(f"transport_task(): state={state}")

        if state == ConnectionState.CONNECTING:
            self.transport_task(timeout=RECONNECT_TIMEOUT)

        elif state == ConnectionState.ERROR:
            if self.error_count < MAX_ERROR_COUNT:
                self.reconnect(timeout=RECONNECT_TIMEOUT)

        elif state == ConnectionState.DISCONNECTING:
            self.transport_task(timeout=RECONNECT_TIMEOUT)

        elif state == ConnectionState.DISCONNECTED:
            self.error_count += 1
            if self.error_count < MAX_ERROR_COUNT:
                self.reconnect(timeout=RECONNECT_TIMEOUT)

        elif state == ConnectionState.CONNECTED:
            self._been_connected = True
            self.pump_pending_packets()

        elif state == ConnectionState.ERROR:
            pass  # Give up

        else:
            assert False

    @Actor.assert_executor()
    def pump_pending_packets(self):
        logging.debug(f"pump_pending_packets(): pending_count={len(self.pending_packets)}")
        if not self.pending_packets:
            return

        outgoing = self.pending_packets[0]
        if outgoing.pending:
            return

        logging.debug("pump_pending_packets(): Sending packet and marking as pending")
        outgoing.pending = True
        impl_outgoing = self._impl.send(outgoing.packet)
        outgoing.set_outgoing_packet(impl_outgoing)

    class OutgoingPacket(AbstractOutgoingPacket):
        def __init__(self, transport, packet):
            super().__init__(packet, Future())
            self._transport: Transport = transport
            self.pending = False
            self._impl: Optional[IOutgoingPacket] = None
            self._last_marker: Optional[object] = None

        def set_outgoing_packet(self, impl: IOutgoingPacket):
            logging.debug("set_outgoing_packet()")

            self._last_marker = object()
            logging.debug(f"set_outgoing_packet(): marker={self._last_marker}")
            self._impl = impl
            done_cb = functools.partial(self.on_impl_future_done, self._last_marker)
            self._impl.future.add_done_callback(done_cb)

        def on_impl_future_done(self, marker: object, future: Future):
            logging.debug(f"on_impl_future_done(): marker={marker}")

            if self._last_marker is not marker:
                # Skip this done notification to avoid zombie execution
                logging.debug("on_impl_future_done(): Stale marker")
                return

            exception = self._impl.future.exception()
            if not exception:
                logging.debug("on_impl_future_done(): Packet delivered")
                self._transport.pending_packets.pop(0)
                self._transport.error_count = 0
                self.future.set_result(self._impl.future.result())
                self._transport.transport_task()
            else:
                logging.error("on_impl_future_done(): Packet failed to deliver", exc_info=exception)
                self._transport.error_count += 1
                self.pending = False
                self._transport.transport_task()
                if self._transport.error_count > MAX_ERROR_COUNT:
                    logging.error("on_impl_future_done() giving up on sending packet")
                    self._transport.pending_packets.pop(0)
                    self.future.set_exception(exception)

    class Client(ITransportClient, Actor):
        def __init__(self, transport, client):
            super().__init__(parent=transport)
            self.transport: Transport = transport
            self.last_state: Optional[ConnectionState] = None
            self.client = client

        @Actor.handler()
        def on_packet_received(self, packet: bytes):
            self.client.on_packet_received(packet)

        @Actor.handler()
        def on_state_changed(self, state: ConnectionState):
            self.transport.assert_executor()
            if self.last_state == state:
                logging.debug(f"on_state_changed(): Discarding on_state_changed {state}")
                return

            self.last_state = state
            self.client.on_state_changed(state)
            self.transport.transport_task(timeout=RECONNECT_TIMEOUT)

        @Actor.handler()
        def on_error(self):
            self.transport.error_count += 1
            # TODO(bgrzesik): consider adding if error > MAX_ERROR_COUNT
            self.client.on_error()


class StreamingTransport(ITransport, AbstractConnection, ABC):
    MAX_SIZE = 1024

    def __init__(self, client, parent=None, executor=None):
        super().__init__(client)

        self._thread: Optional[threading.Thread] = None
        self._client: ITransportClient = client
        self._running = False
        self._output_queue: List[StreamingTransport.OutgoingPacket] = []
        self._running = False

        self._output_buffer: Optional[bytes] = None
        self._input_buffer: Optional[bytes] = None
        self._packet_size = 0

        if self.is_connected:
            # Ensure that state is history is correct
            self.connect()

    def do_connect(self) -> bool:
        raise NotImplementedError

    def input(self, num: int) -> bytes:
        raise NotImplementedError

    def output(self, data: bytes) -> int:
        raise NotImplementedError

    def do_disconnect(self) -> bool:
        raise NotImplementedError

    def wait(self, write: bool) -> (bool, bool, bool):
        raise NotImplementedError

    def notify(self):
        raise NotImplementedError

    def _read(self):
        logging.debug("_read()")
        if self._input_buffer is None:
            self._packet_size = int.from_bytes(self.input(4), "big")
            self._input_buffer = bytes()
            logging.debug(f"_read(): going to read {self._packet_size}")
            return

        remaining = self._packet_size - len(self._input_buffer)
        logging.debug(f"_read(): size = {self._packet_size} remaining = {remaining}")

        read_bytes = self.input(remaining)
        if read_bytes:
            self._input_buffer = self._input_buffer + read_bytes
            logging.debug(f"_read(): read={len(read_bytes)}")

        assert len(self._input_buffer) <= self._packet_size
        if self._packet_size == len(self._input_buffer):
            self._client.on_packet_received(self._input_buffer)
            self._input_buffer = None

    def _write(self):
        logging.debug("_write():")
        if self._output_buffer is None:
            if not self._output_queue:
                return False

            packet = self._output_queue[0]
            size = int.to_bytes(len(packet.packet), 4, "big")

            self._output_buffer = size + packet.packet

        num = self.output(self._output_buffer)
        logging.debug(f"_write(): wrote = {num}")
        self._output_buffer = self._output_buffer[num:]

        if len(self._output_buffer) == 0:
            packet = self._output_queue.pop(0)
            packet.future.set_result(packet)
            self._output_buffer = None

    def _io_thread(self):
        logging.debug(f"_io_thread(): thread={threading.current_thread()} self={self}")
        while self._running:
            poll_write = (self._output_buffer is not None) or (len(self._output_queue) != 0)
            logging.debug(f"_io_thread(): poll_write = {poll_write}")
            read, write, hup = self.wait(poll_write)
            logging.debug(f"_io_thread(): read = {read}, write = {write}, hup={hup}, running = {self._running}")

            if not self._running or hup:
                if hup:
                    self._running = False
                self.disconnect()
                break

            try:
                if read:
                    self._read()
                if write:
                    self._write()
            except BlockingIOError:
                # Ignore this, we don't want any blocking
                pass
            except Exception:
                self._client.on_error()

        logging.debug(f"_io_thread(): Exited")

    @property
    def is_connected(self) -> bool:
        raise NotImplementedError

    def send(self, packet: bytes) -> IOutgoingPacket:
        logging.debug("send():")
        outgoing = StreamingTransport.OutgoingPacket(packet)
        self._output_queue.append(outgoing)

        if self.state == ConnectionState.DISCONNECTED:
            self.reconnect()

        self.notify()

        return outgoing

    def reconnect(self):
        logging.debug("reconnect():")
        if self.is_connected:
            self.disconnect()

        self.connect()

    def connect(self):
        logging.debug("connect()")

        self.state = ConnectionState.CONNECTING
        if (not self.is_connected) and (not self.do_connect()):
            if not self.is_connected:
                self.state = ConnectionState.DISCONNECTING
                self.do_disconnect()
                self.state = ConnectionState.DISCONNECTED
                return

        self._running = True
        self._thread = threading.Thread(target=self._io_thread, name="Streaming IO thread")
        self._thread.daemon = True
        self._thread.start()

        self.state = ConnectionState.CONNECTED

    def disconnect(self):
        logging.debug("disconnect():")
        self.state = ConnectionState.DISCONNECTING
        self._kill_thread()
        self.do_disconnect()
        self.state = ConnectionState.DISCONNECTED

    def __del__(self):
        self._kill_thread()

    def _kill_thread(self):
        logging.debug("_kill_thread():")

        self._running = False

        if threading.current_thread() == self._thread:
            logging.debug("_kill_thread(): Same thread, avoiding dead lock")
            return

        while self._thread and self._thread.is_alive():
            logging.debug("_kill_thread(): Trying to kill thread")
            self.notify()
            try:
                self._thread.join(0.3)
            except RuntimeError:
                pass

        logging.debug("_kill_thread(): Thread is dead")

    class OutgoingPacket(AbstractOutgoingPacket):
        pass


class SocketTransport(StreamingTransport):

    def __init__(self, sock, addr, client):
        self._sock: socket.socket = sock
        self._addr = addr

        self._poll: Optional[select.poll] = None
        self._notify: Optional[int] = None
        self._event: Optional[int] = None

        super().__init__(client)

    def do_connect(self) -> bool:
        logging.debug("do_connect():")

        self._event, self._notify = os.pipe()
        os.set_blocking(self._event, False)

        if hasattr(self._sock, "setblocking"):
            self._sock.setblocking(False)
        else:
            os.set_blocking(self._sock.fileno(), False)

        self._poll = select.poll()
        self._poll.register(self._event, select.POLLIN)
        self._poll.register(self._sock, select.POLLIN)

        return True

    def input(self, num: int) -> bytes:
        return self._sock.recv(num)

    def output(self, data: bytes) -> int:
        return self._sock.send(data)

    def do_disconnect(self) -> bool:
        logging.debug("do_disconnect():")
        if self._poll is not None:
            self._poll.unregister(self._sock)
            self._poll.unregister(self._event)
            self._poll = None

        if self._notify is not None:
            os.close(self._notify)
            self._notify = None

        if self._event is not None:
            os.close(self._event)
            self._event = None

        return True

    def wait(self, write: bool) -> (bool, bool, bool):
        logging.debug(f"wait(): write = {write} event={self._event}")

        mask = select.POLLIN | select.POLLHUP
        if write:
            mask = mask | select.POLLOUT

        self._poll.modify(self._sock.fileno(), mask)
        fds = self._poll.poll()

        logging.debug(f"wait(): polled fds={fds}")
        has_read, has_write, has_hup = False, False, False

        for fd, event in fds:
            if fd == self._event:
                try:
                    while len(os.read(self._event, 1)) > 0:
                        pass
                except BlockingIOError:
                    pass

            elif fd == self._sock.fileno():
                if (event & select.POLLIN) == select.POLLIN:
                    has_read = True

                if (event & select.POLLOUT) == select.POLLOUT:
                    has_write = True

                if (event & select.POLLHUP) == select.POLLHUP:
                    has_hup = True

                if (event & select.POLLERR) == select.POLLERR:
                    has_hup = True

        logging.debug(f"wait(): read={has_read} write={has_write} hup={has_hup}")
        return has_read, has_write, has_hup

    def notify(self):
        if self._notify is not None:
            os.write(self._notify, b"\0")

    @property
    def is_connected(self) -> bool:
        return self._event is not None

    def __del__(self):
        super().__del__()
        os.close(self._notify)
        os.close(self._event)
        self._sock.close()