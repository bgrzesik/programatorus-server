from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message

DESCRIPTOR: _descriptor.FileDescriptor


class GenericMessage(_message.Message):
    __slots__ = ["requestId", "sessionId", "test"]
    REQUESTID_FIELD_NUMBER: _ClassVar[int]
    SESSIONID_FIELD_NUMBER: _ClassVar[int]
    TEST_FIELD_NUMBER: _ClassVar[int]
    requestId: int
    sessionId: int
    test: TestMessage

    def __init__(self, sessionId: _Optional[int] = ..., requestId: _Optional[int] = ...,
                 test: _Optional[_Union[TestMessage, _Mapping]] = ...) -> None: ...


class TestMessage(_message.Message):
    __slots__ = ["value"]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str

    def __init__(self, value: _Optional[str] = ...) -> None: ...
