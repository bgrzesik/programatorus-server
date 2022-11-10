import functools
import logging
from abc import ABC
from concurrent.futures import Future
from typing import Optional

from server.actor import Actor
from server.comm.connection import IConnection, IConnectionClient, ConnectionState
from server.comm.presentation.protocol_pb2 import GenericMessage


class IOutgoingMessage(ABC):

    @property
    def message(self) -> GenericMessage:
        raise NotImplementedError

    @property
    def future(self) -> Future:
        raise NotImplementedError


class AbstractOutgoingMessage(IOutgoingMessage, ABC):

    def __init__(self, message, future):
        self._message = message
        self._future = future

    @property
    def message(self) -> GenericMessage:
        return self._message

    @property
    def future(self) -> Future:
        return self._future


class IMessenger(IConnection, ABC):

    def send(self, message: GenericMessage) -> IOutgoingMessage:
        raise NotImplementedError


class IMessageClient(IConnectionClient, ABC):

    def on_message_received(self, message: GenericMessage):
        raise NotImplementedError


class ProxyMessageClient(IMessageClient, Actor):

    def __init__(self, impl, parent=None, executor=None):
        super(ProxyMessageClient, self).__init__(parent=parent, executor=executor)
        self._impl: IMessageClient = impl

    @Actor.handler()
    def on_message_received(self, message: GenericMessage):
        self._impl.on_message_received(message)

    @Actor.handler()
    def on_state_changed(self, state: ConnectionState):
        self._impl.on_state_changed(state)

    @Actor.handler()
    def on_error(self):
        self._impl.on_error()


class Messenger(IMessenger, Actor):

    def __init__(self, messenger_provider, client):
        Actor.__init__(self)
        client = Messenger.Client(self, client)
        self._impl: IMessenger = messenger_provider(client)

    @property
    def state(self):
        return self._impl.state

    @Actor.handler()
    def _send(self, outgoing: "Messenger.OutgoingMessage"):
        impl = self._impl.send(outgoing.message)
        outgoing.set_outgoing_message(impl)

    def send(self, message: GenericMessage) -> IOutgoingMessage:
        outgoing = Messenger.OutgoingMessage(self, message)
        self._send(outgoing)
        return outgoing

    @Actor.handler(guarded=True)
    def reconnect(self):
        self._impl.reconnect()

    @Actor.handler(guarded=True)
    def disconnect(self):
        self._impl.disconnect()

    class OutgoingMessage(AbstractOutgoingMessage):

        def __init__(self, messenger, message):
            super().__init__(message, Future())
            self.messenger: Messenger = messenger
            self.messenger.assert_executor()
            self.impl: Optional[IOutgoingMessage] = None
            self.last_marker: Optional[object] = None

        def set_outgoing_message(self, outgoing: IOutgoingMessage):
            self.messenger.assert_executor()
            logging.debug("set_outgoing_message()")

            self.last_marker = object()
            self.impl = outgoing
            done_cb = functools.partial(self.on_impl_future_done, self.last_marker)
            self.impl.future.add_done_callback(done_cb)

        def on_impl_future_done(self, marker: object, future: Future):
            self.messenger.assert_executor()
            if self.last_marker is not marker:
                # Skip this done notification to avoid zombie execution
                logging.debug("on_impl_future_done(): Stale marker")
                return

            exception = self.impl.future.exception()
            if not exception:
                self.future.set_result(self.impl.future.result())
            else:
                self.future.set_exception(exception)

    class Client(IMessageClient, Actor):
        def __init__(self, messenger, client):
            super().__init__(parent=messenger)
            self.client: IMessageClient = client
            self.last_state: Optional[ConnectionState] = None

        @Actor.handler()
        def on_message_received(self, message: GenericMessage):
            self.client.on_message_received(message)

        @Actor.handler()
        def on_state_changed(self, state: ConnectionState):
            if self.last_state == state:
                logging.debug(f"on_state_changed(): Discarding on_state_changed {state}")
                return

            self.last_state = state
            self.client.on_state_changed(state)

        @Actor.handler()
        def on_error(self):
            self.client.on_error()
