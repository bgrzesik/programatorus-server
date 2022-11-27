from enum import IntEnum
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

from .app import IRequester, IResponder
from .presentation import protocol_pb2 as pb


@dataclass
class Board(object):
    name: str
    favourite: bool


@dataclass
class Boards(object):
    boards: List[Board] = field(default_factory=list)


class OnGetBoards(IResponder[None, Boards]):

    @property
    def request_payload(self) -> str:
        return "getBoardsRequest"

    def unpack_request(self, request: pb.GenericMessage) -> None:
        return None

    def prepare_response(self, response: Boards) -> pb.GenericMessage:
        return pb.GenericMessage(
            getBoardsResponse=pb.GetBoardsResponse(
                board=[pb.GetBoardsResponse.Board(name=b.name,
                                                  favourite=b.favourite)
                       for b in response.boards]
            )
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
