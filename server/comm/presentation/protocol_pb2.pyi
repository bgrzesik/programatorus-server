from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Board(_message.Message):
    __slots__ = ["favourite", "name"]
    FAVOURITE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    favourite: bool
    name: str
    def __init__(self, name: _Optional[str] = ..., favourite: bool = ...) -> None: ...

class DebuggerLine(_message.Message):
    __slots__ = ["line", "ordinal"]
    LINE_FIELD_NUMBER: _ClassVar[int]
    ORDINAL_FIELD_NUMBER: _ClassVar[int]
    line: str
    ordinal: int
    def __init__(self, ordinal: _Optional[int] = ..., line: _Optional[str] = ...) -> None: ...

class DebuggerStart(_message.Message):
    __slots__ = ["firmware", "target"]
    FIRMWARE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    firmware: str
    target: str
    def __init__(self, target: _Optional[str] = ..., firmware: _Optional[str] = ...) -> None: ...

class DebuggerStarted(_message.Message):
    __slots__ = ["sessionId"]
    SESSIONID_FIELD_NUMBER: _ClassVar[int]
    sessionId: int
    def __init__(self, sessionId: _Optional[int] = ...) -> None: ...

class DebuggerStop(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

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

class Firmware(_message.Message):
    __slots__ = ["favourite", "name"]
    FAVOURITE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    favourite: bool
    name: str
    def __init__(self, name: _Optional[str] = ..., favourite: bool = ...) -> None: ...

class FlashRequest(_message.Message):
    __slots__ = ["board", "firmware"]
    BOARD_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_FIELD_NUMBER: _ClassVar[int]
    board: Board
    firmware: Firmware
    def __init__(self, firmware: _Optional[_Union[Firmware, _Mapping]] = ..., board: _Optional[_Union[Board, _Mapping]] = ...) -> None: ...

class FlashResponse(_message.Message):
    __slots__ = ["message", "success"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    message: str
    success: bool
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class GenericMessage(_message.Message):
    __slots__ = ["debuggerLine", "debuggerStart", "debuggerStarted", "debuggerStop", "deviceUpdateStatus", "error", "fileUpload", "flashRequest", "flashResponse", "getBoardsRequest", "getBoardsResponse", "getFirmwareRequest", "getFirmwareResponse", "heartbeat", "ok", "putBoardsRequest", "putBoardsResponse", "putFirmwareRequest", "putFirmwareResponse", "request", "response", "sessionId", "setSessionId", "test"]
    DEBUGGERLINE_FIELD_NUMBER: _ClassVar[int]
    DEBUGGERSTARTED_FIELD_NUMBER: _ClassVar[int]
    DEBUGGERSTART_FIELD_NUMBER: _ClassVar[int]
    DEBUGGERSTOP_FIELD_NUMBER: _ClassVar[int]
    DEVICEUPDATESTATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    FILEUPLOAD_FIELD_NUMBER: _ClassVar[int]
    FLASHREQUEST_FIELD_NUMBER: _ClassVar[int]
    FLASHRESPONSE_FIELD_NUMBER: _ClassVar[int]
    GETBOARDSREQUEST_FIELD_NUMBER: _ClassVar[int]
    GETBOARDSRESPONSE_FIELD_NUMBER: _ClassVar[int]
    GETFIRMWAREREQUEST_FIELD_NUMBER: _ClassVar[int]
    GETFIRMWARERESPONSE_FIELD_NUMBER: _ClassVar[int]
    HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    OK_FIELD_NUMBER: _ClassVar[int]
    PUTBOARDSREQUEST_FIELD_NUMBER: _ClassVar[int]
    PUTBOARDSRESPONSE_FIELD_NUMBER: _ClassVar[int]
    PUTFIRMWAREREQUEST_FIELD_NUMBER: _ClassVar[int]
    PUTFIRMWARERESPONSE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SESSIONID_FIELD_NUMBER: _ClassVar[int]
    SETSESSIONID_FIELD_NUMBER: _ClassVar[int]
    TEST_FIELD_NUMBER: _ClassVar[int]
    debuggerLine: DebuggerLine
    debuggerStart: DebuggerStart
    debuggerStarted: DebuggerStarted
    debuggerStop: DebuggerStop
    deviceUpdateStatus: DeviceUpdateStatus
    error: ErrorMessage
    fileUpload: FileUpload
    flashRequest: FlashRequest
    flashResponse: FlashResponse
    getBoardsRequest: GetBoardsRequest
    getBoardsResponse: GetBoardsResponse
    getFirmwareRequest: GetFirmwareRequest
    getFirmwareResponse: GetFirmwareResponse
    heartbeat: _empty_pb2.Empty
    ok: _empty_pb2.Empty
    putBoardsRequest: PutBoardsRequest
    putBoardsResponse: PutBoardsResponse
    putFirmwareRequest: PutFirmwareRequest
    putFirmwareResponse: PutFirmwareResponse
    request: int
    response: int
    sessionId: int
    setSessionId: SetSessionId
    test: TestMessage
    def __init__(self, sessionId: _Optional[int] = ..., request: _Optional[int] = ..., response: _Optional[int] = ..., setSessionId: _Optional[_Union[SetSessionId, _Mapping]] = ..., heartbeat: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., ok: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., getBoardsRequest: _Optional[_Union[GetBoardsRequest, _Mapping]] = ..., getBoardsResponse: _Optional[_Union[GetBoardsResponse, _Mapping]] = ..., putBoardsRequest: _Optional[_Union[PutBoardsRequest, _Mapping]] = ..., putBoardsResponse: _Optional[_Union[PutBoardsResponse, _Mapping]] = ..., getFirmwareRequest: _Optional[_Union[GetFirmwareRequest, _Mapping]] = ..., getFirmwareResponse: _Optional[_Union[GetFirmwareResponse, _Mapping]] = ..., putFirmwareRequest: _Optional[_Union[PutFirmwareRequest, _Mapping]] = ..., putFirmwareResponse: _Optional[_Union[PutFirmwareResponse, _Mapping]] = ..., flashRequest: _Optional[_Union[FlashRequest, _Mapping]] = ..., flashResponse: _Optional[_Union[FlashResponse, _Mapping]] = ..., deviceUpdateStatus: _Optional[_Union[DeviceUpdateStatus, _Mapping]] = ..., fileUpload: _Optional[_Union[FileUpload, _Mapping]] = ..., debuggerStart: _Optional[_Union[DebuggerStart, _Mapping]] = ..., debuggerStarted: _Optional[_Union[DebuggerStarted, _Mapping]] = ..., debuggerStop: _Optional[_Union[DebuggerStop, _Mapping]] = ..., debuggerLine: _Optional[_Union[DebuggerLine, _Mapping]] = ..., test: _Optional[_Union[TestMessage, _Mapping]] = ..., error: _Optional[_Union[ErrorMessage, _Mapping]] = ...) -> None: ...

class GetBoardsRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetBoardsResponse(_message.Message):
    __slots__ = ["all", "favorites"]
    ALL_FIELD_NUMBER: _ClassVar[int]
    FAVORITES_FIELD_NUMBER: _ClassVar[int]
    all: _containers.RepeatedCompositeFieldContainer[Board]
    favorites: _containers.RepeatedCompositeFieldContainer[Board]
    def __init__(self, all: _Optional[_Iterable[_Union[Board, _Mapping]]] = ..., favorites: _Optional[_Iterable[_Union[Board, _Mapping]]] = ...) -> None: ...

class GetFirmwareRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetFirmwareResponse(_message.Message):
    __slots__ = ["all", "favorites"]
    ALL_FIELD_NUMBER: _ClassVar[int]
    FAVORITES_FIELD_NUMBER: _ClassVar[int]
    all: _containers.RepeatedCompositeFieldContainer[Firmware]
    favorites: _containers.RepeatedCompositeFieldContainer[Firmware]
    def __init__(self, all: _Optional[_Iterable[_Union[Firmware, _Mapping]]] = ..., favorites: _Optional[_Iterable[_Union[Firmware, _Mapping]]] = ...) -> None: ...

class PutBoardsRequest(_message.Message):
    __slots__ = ["all", "favorites"]
    ALL_FIELD_NUMBER: _ClassVar[int]
    FAVORITES_FIELD_NUMBER: _ClassVar[int]
    all: _containers.RepeatedCompositeFieldContainer[Board]
    favorites: _containers.RepeatedCompositeFieldContainer[Board]
    def __init__(self, all: _Optional[_Iterable[_Union[Board, _Mapping]]] = ..., favorites: _Optional[_Iterable[_Union[Board, _Mapping]]] = ...) -> None: ...

class PutBoardsResponse(_message.Message):
    __slots__ = ["success"]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class PutFirmwareRequest(_message.Message):
    __slots__ = ["all", "favorites"]
    ALL_FIELD_NUMBER: _ClassVar[int]
    FAVORITES_FIELD_NUMBER: _ClassVar[int]
    all: _containers.RepeatedCompositeFieldContainer[Firmware]
    favorites: _containers.RepeatedCompositeFieldContainer[Firmware]
    def __init__(self, all: _Optional[_Iterable[_Union[Firmware, _Mapping]]] = ..., favorites: _Optional[_Iterable[_Union[Firmware, _Mapping]]] = ...) -> None: ...

class PutFirmwareResponse(_message.Message):
    __slots__ = ["success"]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

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
