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

class FileUpload(_message.Message):
    __slots__ = ["finish", "part", "result", "start", "uid"]
    class FileType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class Result(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class Finish(_message.Message):
        __slots__ = ["checksum"]
        CHECKSUM_FIELD_NUMBER: _ClassVar[int]
        checksum: bytes
        def __init__(self, checksum: _Optional[bytes] = ...) -> None: ...
    class Part(_message.Message):
        __slots__ = ["chunk", "partNo"]
        CHUNK_FIELD_NUMBER: _ClassVar[int]
        PARTNO_FIELD_NUMBER: _ClassVar[int]
        chunk: bytes
        partNo: int
        def __init__(self, partNo: _Optional[int] = ..., chunk: _Optional[bytes] = ...) -> None: ...
    class Start(_message.Message):
        __slots__ = ["chunks", "name", "size", "type"]
        CHUNKS_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        SIZE_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        chunks: int
        name: str
        size: int
        type: FileUpload.FileType
        def __init__(self, name: _Optional[str] = ..., size: _Optional[int] = ..., chunks: _Optional[int] = ..., type: _Optional[_Union[FileUpload.FileType, str]] = ...) -> None: ...
    ALREADY_EXISTS: FileUpload.Result
    FINISH_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE: FileUpload.FileType
    INVALID_CHECKSUM: FileUpload.Result
    IO_ERROR: FileUpload.Result
    OK: FileUpload.Result
    PART_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    finish: FileUpload.Finish
    part: FileUpload.Part
    result: FileUpload.Result
    start: FileUpload.Start
    uid: int
    def __init__(self, uid: _Optional[int] = ..., start: _Optional[_Union[FileUpload.Start, _Mapping]] = ..., part: _Optional[_Union[FileUpload.Part, _Mapping]] = ..., finish: _Optional[_Union[FileUpload.Finish, _Mapping]] = ..., result: _Optional[_Union[FileUpload.Result, str]] = ...) -> None: ...

class GenericMessage(_message.Message):
    __slots__ = ["deviceUpdateStatus", "error", "fileUpload", "getBoardsRequest", "getBoardsResponse", "heartbeat", "ok", "request", "response", "sessionId", "setSessionId", "test"]
    DEVICEUPDATESTATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    FILEUPLOAD_FIELD_NUMBER: _ClassVar[int]
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
    fileUpload: FileUpload
    getBoardsRequest: GetBoardsRequest
    getBoardsResponse: GetBoardsResponse
    heartbeat: _empty_pb2.Empty
    ok: _empty_pb2.Empty
    request: int
    response: int
    sessionId: int
    setSessionId: SetSessionId
    test: TestMessage
    def __init__(self, sessionId: _Optional[int] = ..., request: _Optional[int] = ..., response: _Optional[int] = ..., setSessionId: _Optional[_Union[SetSessionId, _Mapping]] = ..., heartbeat: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., ok: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., getBoardsRequest: _Optional[_Union[GetBoardsRequest, _Mapping]] = ..., getBoardsResponse: _Optional[_Union[GetBoardsResponse, _Mapping]] = ..., deviceUpdateStatus: _Optional[_Union[DeviceUpdateStatus, _Mapping]] = ..., fileUpload: _Optional[_Union[FileUpload, _Mapping]] = ..., test: _Optional[_Union[TestMessage, _Mapping]] = ..., error: _Optional[_Union[ErrorMessage, _Mapping]] = ...) -> None: ...

class GetBoardsRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetBoardsResponse(_message.Message):
    __slots__ = ["board"]
    class Board(_message.Message):
        __slots__ = ["favourite", "name"]
        FAVOURITE_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        favourite: bool
        name: str
        def __init__(self, name: _Optional[str] = ..., favourite: bool = ...) -> None: ...
    BOARD_FIELD_NUMBER: _ClassVar[int]
    board: _containers.RepeatedCompositeFieldContainer[GetBoardsResponse.Board]
    def __init__(self, board: _Optional[_Iterable[_Union[GetBoardsResponse.Board, _Mapping]]] = ...) -> None: ...

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
