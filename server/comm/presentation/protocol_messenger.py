import logging
from concurrent.futures import Future

from server.comm.connection import ConnectionState
from server.comm.presentation.messenger import IMessenger, IMessageClient, IOutgoingMessage, AbstractOutgoingMessage
from server.comm.presentation.protocol_pb2 import GenericMessage
from server.comm.transport.transport import ITransportClient, IOutgoingPacket


class ProtocolMessenger(IMessenger):

    def __init__(self, transport_provider, client):
        client = ProtocolMessenger.Client(client)
        self._transport = transport_provider(client)

    def send(self, message: GenericMessage) -> IOutgoingMessage:
        logging.debug(f"send()")
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
            message = GenericMessage()
            message.ParseFromString(packet)
            self.client.on_message_received(message)

        def on_state_changed(self, state: ConnectionState):
            self.client.on_state_changed(state)
