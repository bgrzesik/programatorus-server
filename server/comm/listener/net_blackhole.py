import logging
import threading
from typing import List
from concurrent.futures import Future

from server.comm import protocol
from server.comm.app import RequestRouter
from server.comm.connection import IConnectionClient
from server.comm.listener.listener import IListenerClient
from server.comm.listener.net import NetworkListener
from server.comm.presentation.messenger import Messenger
from server.comm.presentation.protocol_messenger import ProtocolMessenger
from server.comm.transport.transport import ITransportBuilder
from server.comm.session.session import Session


class GetBoardsResponder(protocol.OnGetBoards):

    def on_request(self, request) -> Future[protocol.Boards]:
        future: Future[protocol.Boards] = Future()
        future.set_result(protocol.Boards(
            boards=["test 0", "test 1"]
        ))
        return future


class MobileClient(IConnectionClient):

    def __init__(self, transport: ITransportBuilder):
        self._router = RequestRouter(
            GetBoardsResponder(),
            client=self
        )

        self._session = Session.Builder(
            messenger=Messenger.Builder(
                messenger=ProtocolMessenger.Builder(
                    transport=transport)
            )
        ).build(self._router)

        self._session.reconnect()

    def on_error(self):
        pass

    def on_state_changed(self, state):
        logging.info(f"on_state_changed(): {state}")


class Client(IListenerClient):

    def __init__(self):
        self._clients: List[MobileClient] = []

    def on_connect(self, transport_builder: ITransportBuilder):
        logging.info("on_connect():")
        self._clients.append(MobileClient(transport_builder))


def main():
    event = threading.Event()
    client = Client()

    bt_listener = NetworkListener(client)
    bt_listener.listen()

    event.wait()


if __name__ == "__main__":
    import sys

    logging.basicConfig(stream=sys.stdout,
                        level=logging.DEBUG,
                        format="%(asctime)s,%(msecs)d %(levelname)-8s "
                        "[%(filename)s:%(lineno)d] %(message)s")
    main()
