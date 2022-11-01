import functools
import logging
import socket
from abc import ABC
from typing import Optional

from server.actor import Actor
from server.comm.transport.transport import Transport, SocketTransport


class IListener(ABC):

    def listen(self):
        raise NotImplementedError


class IListenerClient(ABC):

    def on_connect(self, transport_getter):
        raise NotImplementedError


class ProxyListenerClient(IListenerClient, Actor):

    def __init__(self, impl, parent=None, executor=None):
        super().__init__(parent=parent, executor=executor)
        self.impl: IListenerClient = impl

    @Actor.handler()
    def on_connect(self, transport_getter):
        self.impl.on_connect(transport_getter)


class SocketListener(IListener, Actor, ABC):

    def __init__(self, client, wrap_transport=True):
        super().__init__()
        self._client: IListenerClient = client
        self._server: Optional[socket.socket] = None
        self._listening = True
        self._wrap_transport = wrap_transport

    def create_socket(self) -> socket.socket:
        raise NotImplementedError

    def _construct(self, sock, addr, client):
        if self._wrap_transport:
            return Transport(functools.partial(SocketTransport, sock, addr), client)
        else:
            return SocketTransport(sock, addr, client)

    @Actor.handler()
    def listen(self):
        try:
            logging.info("listen():")
            self._server = self.create_socket()

            while self._listening:
                logging.info(f"listen(): Waiting for connection")

                try:
                    client, addr = self._server.accept()
                    logging.info(f"listen(): Pending connection with {addr}")

                    self._client.on_connect(functools.partial(self._construct, client, addr))

                except IOError as error:
                    logging.error("listen(): IO Error ", error)

            logging.info("listen(): Server closing")
            self._server.close()

        except Exception as exception:
            logging.error(exception)