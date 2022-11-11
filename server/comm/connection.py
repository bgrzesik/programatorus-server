import enum
import logging
from abc import ABC
from typing import Optional

from server.actor import Runner


class ConnectionState(enum.Enum):
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"

    DISCONNECTING = "DISCONNECTING"
    DISCONNECTED = "DISCONNECTED"

    ERROR = "ERROR"


class IConnection(object):

    @property
    def state(self) -> ConnectionState:
        raise NotImplementedError

    def reconnect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    @property
    def supports_reconnecting(self):
        return False


class IConnectionBuilder(ABC):

    def __init__(self, runner=None):
        self.runner: Runner = runner

    def set_runner(self, runner):
        self.runner = runner


class IConnectionClient(object):

    def on_state_changed(self, state: ConnectionState):
        raise NotImplementedError

    def on_error(self):
        pass


class AbstractConnection(IConnection, ABC):

    def __init__(self, client):
        self._state: ConnectionState = ConnectionState.DISCONNECTED
        self._client: IConnectionClient = client

    @property
    def state(self) -> ConnectionState:
        return self._state

    @state.setter
    def state(self, value):
        if self._state != value:
            logging.debug(f"state(): {self._state} -> {value}")
            self._state = value
            self._client.on_state_changed(value)
