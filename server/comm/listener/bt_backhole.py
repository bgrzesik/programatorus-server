import functools
import logging
from concurrent.futures import Future

from server.comm.connection import ConnectionState
from server.comm.listener.bt import BluetoothListener
from server.comm.listener.listener import IListenerClient
from server.comm.presentation.messenger import Messenger, IMessageClient
from server.comm.presentation.protocol_messenger import ProtocolMessenger
from server.comm.presentation.protocol_pb2 import GenericMessage, TestMessage
from server.comm.session.session import ISessionClient, Session

from google.protobuf.empty_pb2 import Empty as EmptyProto

class Client(IListenerClient, ISessionClient):

    def on_request(self, request: GenericMessage) -> Future[GenericMessage]:
        logging.debug(f"on_request(): {request}")

        future = Future()
        future.set_result(GenericMessage(ok=EmptyProto()))

        return future

    def on_state_changed(self, state: ConnectionState):
        logging.info(f"on_state_changed() state={state}")

    def on_connect(self, transport_getter):
        logging.info("on_connect():")
        session = Session(functools.partial(Messenger, functools.partial(ProtocolMessenger, transport_getter)), self)
        session.request(GenericMessage(test=TestMessage(value="Test 123"))).add_done_callback(lambda res: logging.debug(f"response {res}"))
        session.reconnect()


def main():
    client = Client()

    bt_listener = BluetoothListener(client)
    bt_listener.listen()


if __name__ == "__main__":
    import sys

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
    main()
