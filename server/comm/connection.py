import enum
import logging
from abc import ABC


class ConnectionState(enum.Enum):
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"

    DISCONNECTING = "DISCONNECTING"
    DISCONNECTED = "DISCONNECTED"

    ERROR = "ERROR"


class IConnection(object):

    @property
    def state(self) -> ConnectionState:
        raise NotImplemented

    def reconnect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError


class IConnectionClient(object):

    def on_state_changed(self, state: ConnectionState):
        raise NotImplementedError

    def on_error(self):
        pass


class AbstractConnection(IConnection, ABC):

    def __init__(self, client: IConnectionClient):
        self._state: ConnectionState = ConnectionState.DISCONNECTED
        self.client = client

    @property
    def state(self) -> ConnectionState:
        return self._state

    @state.setter
    def state(self, value):
        if self._state != value:
            self._state = value
            self.client.on_state_changed(value)
            logging.debug("")
