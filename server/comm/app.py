import logging
from abc import ABC, abstractmethod
from concurrent.futures import Future
from typing import Generic, TypeVar, Optional, Dict

from .connection import IConnectionClient
from .presentation.protocol_pb2 import GenericMessage
from .session.session import ISession, ISessionClient


Request = TypeVar("Request")
Response = TypeVar("Response")


class IRequester(ABC, Generic[Response]):

    @abstractmethod
    def prepare(self) -> GenericMessage:
        raise NotImplementedError

    @property
    @abstractmethod
    def response_payload(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def handle_response(self, response: GenericMessage) -> Response:
        raise NotImplementedError

    def on_response(self, response: GenericMessage):
        received_payload = response.WhichOneof("payload")
        if self.response_payload != received_payload:
            raise RuntimeError("invalid response "
                               f"expected: {self.response_payload} "
                               f"got {received_payload}")

        return self.handle_response(response)

    def request(self, session: ISession) -> Future[Response]:
        future: Future[Response] = Future()
        message = self.prepare()

        def on_response_wrapper(res: Future[GenericMessage]):
            nonlocal self, future

            if res.cancelled():
                future.cancel()
            elif res.exception():
                future.set_exception(res.exception())
            else:
                future.set_result(self.handle_response(res.result()))

        assert message.WhichOneof("payload")
        req: Future[GenericMessage] = session.request(message)
        req.add_done_callback(on_response_wrapper)

        return future


class IResponder(ABC, Generic[Request, Response]):

    @property
    @abstractmethod
    def request_payload(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def unpack_request(self, request: GenericMessage) -> Request:
        raise NotImplementedError

    @abstractmethod
    def on_request(self, request: Request) -> Future[Response]:
        raise NotImplementedError

    @abstractmethod
    def prepare_response(self, response: Response) -> GenericMessage:
        raise NotImplementedError

    def handle(self, request: GenericMessage) -> Future[GenericMessage]:
        assert request.WhichOneof("payload") == self.request_payload
        future: Future[GenericMessage] = Future()
        req: Request = self.unpack_request(request)

        def prepare_response_wrapper(res: Future[Response]):
            nonlocal self, future

            if res.cancelled():
                future.cancel()
                print("cancelled")
            elif res.exception():
                future.set_exception(res.exception())
                print("exception")
            else:
                future.set_result(self.prepare_response(res.result()))
                print("good")

        self.on_request(req).add_done_callback(prepare_response_wrapper)

        return future


class RequestRouter(ISessionClient):

    def __init__(self, *responders: IResponder,
                 client: Optional[IConnectionClient] = None):
        self._responders: Dict[str, IResponder] = {}
        self._client = client

        for responder in responders:
            self._responders[responder.request_payload] = responder

    def on_request(self, request: GenericMessage) -> Future[GenericMessage]:
        payload = request.WhichOneof("payload")
        if payload not in self._responders:
            logging.error(f"on_request(): Missing Responder for {payload}")
            future: Future[GenericMessage] = Future()
            future.set_exception(RuntimeError("Missing responder"))
            return future

        responder = self._responders[payload]
        print(responder)

        return responder.handle(request)

    def on_state_changed(self, state):
        if self._client is not None:
            self._client.on_state_changed(state)

    def on_error(self):
        if self._client is not None:
            self._client.on_error()
