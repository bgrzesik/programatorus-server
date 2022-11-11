import logging
from concurrent.futures import Future

from server.actor import Runner
from server.comm.connection import ConnectionState
from server.comm.presentation.messenger import IMessenger, IMessageClient, IOutgoingMessage, AbstractOutgoingMessage, \
    IMessengerBuilder
from server.comm.presentation.protocol_pb2 import GenericMessage
from server.comm.transport.transport import ITransport, ITransportClient, IOutgoingPacket, ITransportBuilder


class ProtocolMessenger(IMessenger):

    def __init__(self, transport_builder: ITransportBuilder, client, runner=None):
        client = ProtocolMessenger.Client(client)
        self._transport: ITransport = transport_builder.build(client, runner=runner)

    @property
    def state(self) -> ConnectionState:
        return self._transport.state

    def send(self, message: GenericMessage) -> IOutgoingMessage:
        logging.debug(f"send(): {message.WhichOneof('payload')}")
        packet = self._transport.send(message.SerializeToString())
        return ProtocolMessenger.OutgoingMessage(message, packet)

    def reconnect(self):
        self._transport.reconnect()

    def disconnect(self):
        self._transport.disconnect()

    class OutgoingMessage(AbstractOutgoingMessage):
        def __init__(self, message, packet: IOutgoingPacket):
            super().__init__(message, Future())
            self._packet = packet
            self._packet.future.add_done_callback(self.on_packet_future_done)

        def on_packet_future_done(self, future):
            assert self._packet.future == future

            exception = self._packet.future.exception()
            if not exception:
                self.future.set_result(self._packet.future.result())
            else:
                self.future.set_exception(exception)

    class Client(ITransportClient):

        def __init__(self, client):
            self.client: IMessageClient = client

        def on_packet_received(self, packet: bytes):
            logging.debug(f"on_packet_received(): len = {len(packet)}")
            message = GenericMessage()
            message.ParseFromString(packet)
            logging.debug(f"on_packet_received(): payload {message.WhichOneof('payload')}")
            self.client.on_message_received(message)

        def on_state_changed(self, state: ConnectionState):
            self.client.on_state_changed(state)

    class Builder(IMessengerBuilder):

        def __init__(self, transport=None, runner=None):
            super().__init__(runner=runner)
            self._transport = transport

        def construct(self, client: IMessageClient, runner: Runner = None):
            return ProtocolMessenger(self._transport, client)
