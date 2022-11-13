import logging
import socket

from server.actor import Actor
from server.comm.listener.listener import SocketListener


class NetworkListener(SocketListener):
    def __init__(self, client, wrap_transport=True):
        super().__init__(client, wrap_transport=wrap_transport)

    @Actor.assert_executor()
    def create_socket(self):
        logging.info("listen():")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logging.info("listen(): socket created")
        server.bind(("127.0.0.1", 2137))

        # Start listening. One connection
        server.listen(10)

        port = server.getsockname()[1]
        logging.info(f"listen(): listening on {port}")

        return server
