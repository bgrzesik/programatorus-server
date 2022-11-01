import functools
import logging

from server.comm.connection import ConnectionState
from server.comm.listener.bt import BluetoothListener
from server.comm.listener.listener import IListenerClient
from server.comm.presentation.messenger import IMessageClient, Messenger
from server.comm.presentation.protocol_messenger import ProtocolMessenger
from server.comm.presentation.protocol_pb2 import GenericMessage, TestMessage


class Client(IListenerClient, IMessageClient):

    def on_message_received(self, message: GenericMessage):
        logging.info(f"on_message_received() message={message}")

    def on_state_changed(self, state: ConnectionState):
        logging.info(f"on_state_changed() state={state}")

    def on_connect(self, transport_getter):
        logging.info("on_connect():")
        messenger = Messenger(functools.partial(ProtocolMessenger, transport_getter), self)
        messenger.send(GenericMessage(requestId=10, sessionId=10, test=TestMessage(value="Test 123")))


def main():
    client = Client()

    bt_listener = BluetoothListener(client)
    bt_listener.listen()


if __name__ == "__main__":
    import sys

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
    main()
