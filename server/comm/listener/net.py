import logging
import socket
from abc import ABC

from server.actor import Actor
from server.comm.listener.listener import SocketListener


class NetworkListener(SocketListener, ABC):

    def __init__(self, client, wrap_transport=True):
        super().__init__(client, wrap_transport=wrap_transport)

    @Actor.handler()
    def listen(self):
        logging.info("listen():")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logging.info("listen(): socket created")
        server.bind(('', 1260))

        # Start listening. One connection
        server.listen(1)

        port = server.getsockname()[1]
        logging.info(f"listen(): listening on {port}")

        return server
