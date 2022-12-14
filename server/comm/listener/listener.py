import logging
import socket
from abc import ABC, abstractmethod
from typing import Optional

from ...tasker import Tasker
from ..transport.transport import (
    Transport,
    SocketTransport,
    ITransportBuilder,
)


class IListener(ABC):
    @abstractmethod
    def listen(self):
        raise NotImplementedError


class IListenerClient(ABC):
    @abstractmethod
    def on_connect(self, transport_builder: ITransportBuilder):
        raise NotImplementedError


class ProxyListenerClient(IListenerClient, Tasker):
    def __init__(self, impl, parent=None, runner=None):
        super().__init__(parent=parent, runner=runner)
        self.impl: IListenerClient = impl

    @Tasker.handler()
    def on_connect(self, transport_getter):
        self.impl.on_connect(transport_getter)


class SocketListener(IListener, Tasker, ABC):
    def __init__(self, client, wrap_transport=True):
        super().__init__()
        self._client: IListenerClient = client
        self._server: Optional[socket.socket] = None
        self._listening = True
        self._wrap_transport = wrap_transport

    @abstractmethod
    def create_socket(self) -> socket.socket:
        raise NotImplementedError

    def _construct(self, sock, addr) -> ITransportBuilder:
        socket_builder = SocketTransport.Builder(socket=sock, addr=addr)

        if self._wrap_transport:
            return Transport.Builder(transport=socket_builder)
        else:
            return socket_builder

    @Tasker.handler()
    def listen(self):
        try:
            logging.info("listen():")
            self._server = self.create_socket()

            while self._listening:
                logging.info("listen(): Waiting for connection")

                try:
                    client, addr = self._server.accept()
                    logging.info(f"listen(): Pending connection with {addr}")
                    self._client.on_connect(self._construct(client, addr))

                except IOError as error:
                    logging.error("listen(): IO Error ", exc_info=error)

            logging.info("listen(): Server closing")
            self._server.close()

        except Exception as exception:
            logging.error("listen(): ", exc_info=exception)
