from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeviceUpdateStatus(_message.Message):
    __slots__ = ["flashingProgress", "image", "status"]
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    ERROR: DeviceUpdateStatus.Status
    FLASHING: DeviceUpdateStatus.Status
    FLASHINGPROGRESS_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    READY: DeviceUpdateStatus.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    UNREACHABLE: DeviceUpdateStatus.Status
    flashingProgress: float
    image: str
    status: DeviceUpdateStatus.Status
    def __init__(self, status: _Optional[_Union[DeviceUpdateStatus.Status, str]] = ..., flashingProgress: _Optional[float] = ..., image: _Optional[str] = ...) -> None: ...

class ErrorMessage(_message.Message):
    __slots__ = ["description"]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    description: str
    def __init__(self, description: _Optional[str] = ...) -> None: ...

class GenericMessage(_message.Message):
    __slots__ = ["deviceUpdateStatus", "error", "getBoardsRequest", "getBoardsResponse", "heartbeat", "ok", "request", "response", "sessionId", "setSessionId", "test"]
    DEVICEUPDATESTATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    GETBOARDSREQUEST_FIELD_NUMBER: _ClassVar[int]
    GETBOARDSRESPONSE_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    OK_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SESSIONID_FIELD_NUMBER: _ClassVar[int]
    SETSESSIONID_FIELD_NUMBER: _ClassVar[int]
    TEST_FIELD_NUMBER: _ClassVar[int]
    deviceUpdateStatus: DeviceUpdateStatus
    error: ErrorMessage
    getBoardsRequest: GetBoardsRequest
    getBoardsResponse: GetBoardsResponse
    heartbeat: _empty_pb2.Empty
    ok: _empty_pb2.Empty
    request: int
    response: int
    sessionId: int
    setSessionId: SetSessionId
    test: TestMessage
    def __init__(self, sessionId: _Optional[int] = ..., request: _Optional[int] = ..., response: _Optional[int] = ..., setSessionId: _Optional[_Union[SetSessionId, _Mapping]] = ..., heartbeat: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., ok: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., getBoardsRequest: _Optional[_Union[GetBoardsRequest, _Mapping]] = ..., getBoardsResponse: _Optional[_Union[GetBoardsResponse, _Mapping]] = ..., deviceUpdateStatus: _Optional[_Union[DeviceUpdateStatus, _Mapping]] = ..., test: _Optional[_Union[TestMessage, _Mapping]] = ..., error: _Optional[_Union[ErrorMessage, _Mapping]] = ...) -> None: ...

class GetBoardsRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetBoardsResponse(_message.Message):
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[_Iterable[str]] = ...) -> None: ...

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
