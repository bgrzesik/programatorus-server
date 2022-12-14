from enum import IntEnum
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

from google.protobuf import empty_pb2

from .app import IRequester, IResponder
from .presentation import protocol_pb2 as pb


@dataclass
class Board(object):
    name: str
    favourite: bool


@dataclass
class BoardsData(object):
    all: List[Board] = field(default_factory=list)
    favorites: List[Board] = field(default_factory=list)


class OnGetBoards(IResponder[None, BoardsData]):

    @property
    def request_payload(self) -> str:
        return "getBoardsRequest"

    def unpack_request(self, request: pb.GenericMessage) -> None:
        return None

    def prepare_response(self, response: BoardsData) -> pb.GenericMessage:
        toDto = lambda b: pb.Board(name=b.name, favourite=b.favourite)
        return pb.GenericMessage(
            getBoardsResponse=pb.GetBoardsResponse(
                all=[toDto(b) for b in response.all],
                favorites=[toDto(b) for b in response.favorites]
            )
        )


@dataclass
class Firmware(object):
    name: str
    favourite: bool


@dataclass
class FirmwareData(object):
    all: List[Firmware] = field(default_factory=list)
    favorites: List[Firmware] = field(default_factory=list)


class OnGetFirmware(IResponder[None, FirmwareData]):

    @property
    def request_payload(self) -> str:
        return "getFirmwareRequest"

    def unpack_request(self, request: pb.GenericMessage) -> None:
        return None

    def prepare_response(self, response: FirmwareData) -> pb.GenericMessage:
        toDto = lambda b: pb.Firmware(name=b.name, favourite=b.favourite)
        return pb.GenericMessage(
            getFirmwareResponse=pb.GetFirmwareResponse(
                all=[toDto(b) for b in response.all],
                favorites=[toDto(b) for b in response.favorites]
            )
        )



class OnPutFirmware(IResponder[FirmwareData, bool]):

    @property
    def request_payload(self) -> str:
        return "putFirmwareRequest"

    def unpack_request(self, request: pb.GenericMessage) -> FirmwareData:
        return FirmwareData(request.putFirmwareRequest.all, request.putFirmwareRequest.favorites)

    def prepare_response(self, response: bool) -> pb.GenericMessage:
        return pb.GenericMessage(
            putFirmwareResponse=pb.PutFirmwareResponse(
                success=response
            )
        )


class OnPutBoards(IResponder[BoardsData, bool]):

    @property
    def request_payload(self) -> str:
        return "putBoardsRequest"

    def unpack_request(self, request: pb.GenericMessage) -> BoardsData:
        return BoardsData(request.putBoardsRequest.all, request.putBoardsRequest.favorites)

    def prepare_response(self, response: bool) -> pb.GenericMessage:
        return pb.GenericMessage(
            putBoardsResponse=pb.PutBoardsResponse(
                success=response
            )
        )

@dataclass
class FlashRequest(object):
    board: Board = field()
    firmware: Firmware = field()

class OnFlashRequest(IResponder[FlashRequest, str]):

    @property
    def request_payload(self) -> str:
        return "flashRequest"

    def unpack_request(self, request: pb.GenericMessage) -> FlashRequest:
        return FlashRequest(request.flashRequest.board, request.flashRequest.firmware)

    def prepare_response(self, response: str) -> pb.GenericMessage:
        return pb.GenericMessage(
            flashResponse=pb.FlashResponse(
                message=response
            )
        )

class OnDeleteFile(IResponder[str, None]):

    @property
    def request_payload(self) -> str:
        return "deleteFile"

    def unpack_request(self, request: pb.GenericMessage) -> str:
        return request.deleteFile.name

    def prepare_response(self, response: str) -> pb.GenericMessage:
        return pb.GenericMessage(
            ok=empty_pb2.Empty()
        )

@dataclass
class DeviceStatus(object):
    class Status(IntEnum):
        UNREACHABLE = 0
        READY = 1
        FLASHING = 2
        ERROR = 3

        def to_proto(self) -> pb.DeviceUpdateStatus.Status:
            return getattr(pb.DeviceUpdateStatus.Status, self.name)

    status: Status
    flashing_progress: Optional[float] = None
    image: Optional[str] = None

    def to_message(self) -> pb.GenericMessage:
        return pb.GenericMessage(
            deviceUpdateStatus=pb.DeviceUpdateStatus(
                status=self.status.to_proto(),
                flashingProgress=self.flashing_progress,
                image=self.image
            )
        )


class UpdateDeviceStatus(IRequester[None]):

    def __init__(self, status):
        self._status: DeviceStatus = status

    def prepare(self) -> pb.GenericMessage:
        return self._status.to_message()

    @property
    def response_payload(self) -> str:
        return "ok"

    def handle_response(self, response: pb.GenericMessage) -> None:
        return None


class FileUpload(object):

    @dataclass
    class Request(object):
        pass

    @dataclass
    class Start(Request):
        name: str
        size: int
        chunks: int
        type_: str

    @dataclass
    class Part(Request):
        uid: int
        part_no: int
        chunk: bytes

    @dataclass
    class Finish(Request):
        uid: int
        checksum: bytes

    class Result(IntEnum):
        OK = 0
        INVALID_CHECKSUM = 1
        IO_ERROR = 2
        ALREADY_EXISTS = 3

        def to_proto(self) -> pb.FileUpload.Result:
            return getattr(pb.FileUpload.Result, self.name)

    Response = Tuple[int, Result]


class OnFileUpload(IResponder[FileUpload.Request, FileUpload.Response]):

    @property
    def request_payload(self) -> str:
        return "fileUpload"

    def unpack_request(self, request: pb.GenericMessage) -> FileUpload.Request:
        fileUpload = request.fileUpload
        event = fileUpload.WhichOneof("event")

        if event == "start":
            if fileUpload.start.type != \
                    getattr(pb.FileUpload.FileType, "FIRMWARE"):
                raise RuntimeError("Unknown file type")

            return FileUpload.Start(
                name=fileUpload.start.name,
                size=fileUpload.start.size,
                chunks=fileUpload.start.chunks,
                type_="FIRMWARE",
            )
        elif event == "part":
            return FileUpload.Part(
                uid=fileUpload.uid,
                part_no=fileUpload.part.partNo,
                chunk=fileUpload.part.chunk
            )
        elif event == "finish":
            return FileUpload.Finish(
                uid=fileUpload.uid,
                checksum=fileUpload.finish.checksum
            )
        else:
            raise RuntimeError("Unknown event type")

    def prepare_response(self,
                         response: FileUpload.Response) -> pb.GenericMessage:

        uid: int = response[0]
        result: FileUpload.Result = response[1]

        return pb.GenericMessage(
            fileUpload=pb.FileUpload(
                uid=uid,
                result=result.to_proto()
            )
        )


@dataclass
class DebuggerStart(object):
    session_id: int
    target: str
    firmware: str


class OnDebuggerStart(IResponder[DebuggerStart, int]):
    "Handler's response is mapped to sessionId"

    @property
    def request_payload(self) -> str:
        return "debuggerStart"

    def unpack_request(self, request: pb.GenericMessage) -> DebuggerStart:
        session_id = request.sessionId
        start = request.debuggerStart
        return DebuggerStart(session_id, start.target, start.firmware)

    def prepare_response(self, response: int) -> pb.GenericMessage:
        return pb.GenericMessage(
            debuggerStarted=pb.DebuggerStarted(
                sessionId=response
            )
        )


class OnDebuggerStop(IResponder[int, None]):
    "Handler's request is mapped to sessionId"

    @property
    def request_payload(self) -> str:
        return "debuggerStop"

    def unpack_request(self, request: pb.GenericMessage) -> int:
        return request.sessionId

    def prepare_response(self, response) -> pb.GenericMessage:
        return pb.GenericMessage(
            ok=empty_pb2.Empty()
        )


@dataclass
class DebuggerLine(object):
    session_id: int
    ordinal: int
    line: str


class OnDebuggerLine(IResponder[DebuggerLine, None]):

    @property
    def request_payload(self) -> str:
        return "debuggerLine"

    def unpack_request(self, request: pb.GenericMessage) -> DebuggerLine:
        session_id = request.sessionId
        line = request.debuggerLine
        return DebuggerLine(session_id, line.ordinal, line.line)

    def prepare_response(self, response) -> pb.GenericMessage:
        return pb.GenericMessage(
            ok=empty_pb2.Empty()
        )


class SendDebuggerLine(IRequester[None]):

    def __init__(self, line):
        self._line: DebuggerLine = line

    def prepare(self) -> pb.GenericMessage:
        return pb.GenericMessage(
            debuggerLine=pb.DebuggerLine(
                ordinal=self._line.ordinal,
                line=self._line.line
            )
        )

    @property
    def response_payload(self) -> str:
        return "ok"

    def handle_response(self, response: pb.GenericMessage) -> None:
        return None
