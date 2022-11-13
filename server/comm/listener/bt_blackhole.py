import logging
import threading
from concurrent.futures import Future

from google.protobuf.empty_pb2 import Empty as EmptyProto

from server.comm.connection import ConnectionState
from server.comm.listener.bt import BluetoothListener
from server.comm.listener.listener import IListenerClient
from server.comm.presentation.messenger import Messenger
from server.comm.presentation.protocol_messenger import ProtocolMessenger
from server.comm.presentation.protocol_pb2 import GenericMessage, TestMessage
from server.comm.session.session import ISessionClient, Session
from server.comm.transport.transport import ITransportBuilder


class Client(IListenerClient, ISessionClient):
    def __init__(self):
        self._sessions = []

    def on_request(self, request: GenericMessage) -> Future[GenericMessage]:
        logging.debug(f"on_request(): {request}")

        future: Future[GenericMessage] = Future()
        future.set_result(GenericMessage(ok=EmptyProto()))

        return future

    def on_state_changed(self, state: ConnectionState):
        logging.info(f"on_state_changed() state={state}")

    def on_connect(self, transport_builder: ITransportBuilder):
        logging.info("on_connect():")

        session = Session.Builder(
            messenger=Messenger.Builder(
                messenger=ProtocolMessenger.Builder(
                    transport=transport_builder)
            )
        ).build(self)

        session.request(
            GenericMessage(test=TestMessage(value="Test 123"))
        ).add_done_callback(lambda res: logging.debug(f"response {res}"))
        session.reconnect()

        self._sessions.append(session)


def main():
    event = threading.Event()
    client = Client()

    bt_listener = BluetoothListener(client)
    bt_listener.listen()
    event.wait()


if __name__ == "__main__":
    import sys

    logging.basicConfig(stream=sys.stdout,
                        level=logging.DEBUG,
                        format="%(asctime)s,%(msecs)d %(levelname)-8s "
                        "[%(filename)s:%(lineno)d] %(message)s")
    main()
