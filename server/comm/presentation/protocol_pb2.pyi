from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class ErrorMessage(_message.Message):
    __slots__ = ["description"]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    description: str
    def __init__(self, description: _Optional[str] = ...) -> None: ...

class GenericMessage(_message.Message):
    __slots__ = [
        "error",
        "heartbeat",
        "ok",
        "request",
        "response",
        "sessionId",
        "setSessionId",
        "test",
    ]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    OK_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SESSIONID_FIELD_NUMBER: _ClassVar[int]
    SETSESSIONID_FIELD_NUMBER: _ClassVar[int]
    TEST_FIELD_NUMBER: _ClassVar[int]
    error: ErrorMessage
    heartbeat: _empty_pb2.Empty
    ok: _empty_pb2.Empty
    request: int
    response: int
    sessionId: int
    setSessionId: SetSessionId
    test: TestMessage
    def __init__(
        self,
        sessionId: _Optional[int] = ...,
        request: _Optional[int] = ...,
        response: _Optional[int] = ...,
        setSessionId: _Optional[_Union[SetSessionId, _Mapping]] = ...,
        heartbeat: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...,
        test: _Optional[_Union[TestMessage, _Mapping]] = ...,
        error: _Optional[_Union[ErrorMessage, _Mapping]] = ...,
        ok: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...,
    ) -> None: ...

class SetSessionId(_message.Message):
    __slots__ = ["sessionId"]
    SESSIONID_FIELD_NUMBER: _ClassVar[int]
    sessionId: int
    def __init__(self, sessionId: _Optional[int] = ...) -> None: ...

class TestMessage(_message.Message):
    __slots__ = ["value"]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...
