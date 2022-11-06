import functools
import itertools
import logging
import time
from abc import ABC
from concurrent.futures import Future
from typing import Optional, List, Dict

from google.protobuf.empty_pb2 import Empty as EmptyProto

from server.actor import Actor
from server.comm.connection import IConnection, IConnectionClient, ConnectionState
from server.comm.presentation.messenger import IMessenger, IMessageClient, IOutgoingMessage
from server.comm.presentation.protocol_pb2 import GenericMessage, ErrorMessage


class ISession(IConnection, ABC):

    def request(self, request: GenericMessage) -> Future[GenericMessage]:
        raise NotImplementedError


class ISessionClient(IConnectionClient, ABC):

    def on_request(self, request: GenericMessage) -> Future[GenericMessage]:
        raise NotImplementedError


class Session(ISession, Actor):
    HEARTBEAT_S = 0.5
    TIMEOUT_S = 32 * HEARTBEAT_S

    def __init__(self, messenger_provider, client, executor=None):
        Actor.__init__(self, executor=executor)
        self.session_id: Optional[int] = None
        self._posted_heartbeat: Optional[Future[GenericMessage]] = None
        self._last_transfer = time.monotonic()
        self.waiting_for_response: Dict[int, Session.PendingMessage] = {}
        self._next_request_id = itertools.count()
        self._queue: List[Session.PendingMessage] = []

        client = Session.Client(self, client)
        self._messenger: IMessenger = messenger_provider(client)
        super().__init__()

    @property
    def state(self) -> ConnectionState:
        return self._messenger.state

    def request(self, request: GenericMessage) -> Future[GenericMessage]:
        logging.debug("request():")

        header = GenericMessage()
        if self.session_id is not None:
            header.sessionId = self.session_id
        header.requestId = next(self._next_request_id)

        request.MergeFrom(header)

        pending = Session.PendingMessage(self, True, request)
        self._queue.append(pending)
        self._pump_messages()

        return pending.future

    @Actor.handler()
    def reconnect(self):
        self._messenger.reconnect()

    @Actor.handler()
    def disconnect(self):
        self._messenger.disconnect()

    @Actor.assert_executor()
    def process_control_requests(self, message: GenericMessage) -> Optional[GenericMessage]:
        logging.debug(f"_process_control_requests(): ${message.WhichOneof('payload')}")

        if message.WhichOneof("payload") == "heartbeat":
            logging.debug(f"_process_control_requests(): Heartbeat")
            return GenericMessage(ok=EmptyProto())
        elif message.WhichOneof("payload") == "setSessionId":
            self.session_id = message.setSessionId.sessionId
            logging.debug(f"_process_control_requests(): Setting sessionId=${self.session_id}")
            return GenericMessage(ok=EmptyProto())
        else:
            return None

    @Actor.handler()
    def _pump_messages(self):
        logging.debug("_pump_messages(): ")
        while self._queue:
            pending = self._queue.pop(0)

            if pending.is_request:
                assert pending.id not in self.waiting_for_response
                self.waiting_for_response[pending.id] = pending

            outgoing = self._messenger.send(pending.message)
            pending.set_outgoing_message(outgoing)

    @Actor.handler(force_schedule=True, guarded=True)
    def timeout_session(self):
        if self.state != ConnectionState.CONNECTED:
            return

        duration = time.monotonic() - self._last_transfer
        logging.debug(f"timeout_session(): state={self.state} duration={duration}")

        if duration > Session.TIMEOUT_S:
            logging.error(f"timeout_session(): Session timeout")
            self.reconnect()
            return

        self.timeout_session(timeout=Session.TIMEOUT_S)

        if duration < Session.HEARTBEAT_S or self._posted_heartbeat is None or not self._posted_heartbeat.done():
            return

        self._posted_heartbeat = self.request(GenericMessage(heartbeat=EmptyProto()))

    @Actor.handler()
    def update_last_transfer(self):
        logging.debug(f"update_last_transfer(): state={self.state}")
        self._last_transfer = time.monotonic()
        self.timeout_session(timeout=Session.HEARTBEAT_S)

    @Actor.handler()
    def on_request_done(self, request_id: int, response: Future[GenericMessage]):
        logging.debug(f"on_request_done(): request_id={request_id}")

        message = None
        exception = response.exception()
        if exception is not None:
            message = GenericMessage()
            if self.session_id is not None:
                message.sessionId = self.session_id
            message.responseId = request_id
            message.error = ErrorMessage(description=str(exception))
        else:
            message = GenericMessage()
            message.CopyFrom(response.result())
            if self.session_id is not None:
                message.sessionId = self.session_id
            message.responseId = request_id
            message.ClearField("requestId")

        logging.debug(f"on_request_done(): request_id={request_id} response={message.WhichOneof('payload')}")
        self._queue.append(Session.PendingMessage(self, False, message))
        self._pump_messages()

    class PendingMessage(object):
        def __init__(self, session, is_request, message):
            self._session: Session = session
            self.is_request: bool = is_request
            self.message: GenericMessage = message
            self._outgoing: Optional[IOutgoingMessage] = None
            self.future = Future()

        @property
        def id(self) -> int:
            if self.is_request:
                return self.message.requestId
            else:
                return self.message.responseId

        def set_outgoing_message(self, outgoing):
            self._session.assert_executor()
            logging.debug("set_outgoing_message():")
            assert self._outgoing is None
            self._outgoing = outgoing
            outgoing.future.add_done_callback(self._on_response)

        def _on_response(self, future: Future):
            logging.debug("_on_response():")
            assert self._outgoing.future == future
            if future.exception() is None:
                self._session.update_last_transfer()

    class Client(IMessageClient, Actor):

        def __init__(self, session, client):
            super().__init__(parent=session)
            self._session: Session = session
            self._client: ISessionClient = client

        @Actor.handler()
        def _on_response(self, response: GenericMessage):
            logging.debug(f"_on_response(): id={response.responseId}")

            pending = self._session.waiting_for_response.pop(response.responseId)
            if pending is None:
                logging.warning(
                    f"_on_response(): Received a response for non existing request id={response.responseId}")
                return

            logging.debug(f"_on_response(): Completing request id={response.responseId}")
            pending.future.set_result(response)

        @Actor.handler()
        def _on_request(self, request: GenericMessage):
            logging.debug(f"_on_request(): Received request id={request.requestId}")

            response = self._session.process_control_requests(request)
            if response is not None:
                logging.debug(f"_on_request(): Received request id={request.requestId}")
                future = Future()
                future.set_result(response)
                self._session.on_request_done(request.requestId, future)
                return

            logging.debug(f"_on_request(): Deferring request to client")

            future = self._client.on_request(request)
            future.add_done_callback(functools.partial(self._session.on_request_done, request.requestId))

        @Actor.handler()
        def on_message_received(self, message: GenericMessage):
            logging.debug(f"on_message_received(): message={message.WhichOneof('payload')}")

            if self._session.session_id is not None and message.sessionId != self._session.session_id:
                logging.warning("on_message_received(): Received a message invalid session id")
                return

            self._session.update_last_transfer()
            if message.HasField("requestId") and not message.HasField("responseId"):
                self._on_request(message)
            elif message.HasField("responseId") and not message.HasField("requestId"):
                self._on_request(message)
            else:
                logging.warning("on_message_received(): Received a message that is not a request nor a response")

        @Actor.handler()
        def on_state_changed(self, state: ConnectionState):
            if state == ConnectionState.CONNECTED:
                self._session.update_last_transfer()

            self._client.on_state_changed(state)

        @Actor.handler()
        def on_error(self):
            self._client.on_error()
