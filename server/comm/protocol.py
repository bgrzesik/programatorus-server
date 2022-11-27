from enum import IntEnum
from typing import List, Optional
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
