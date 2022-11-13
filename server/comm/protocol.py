from enum import IntEnum
from typing import List, Optional
from dataclasses import dataclass, field

from server.comm.app import IRequester, IResponder
from server.comm.presentation.protocol_pb2 import (
    GenericMessage, GetBoardsResponse, DeviceUpdateStatus
)


@dataclass
class Boards(object):
    boards: List[str] = field(default_factory=list)


class OnGetBoards(IResponder[None, Boards]):

    @property
    def request_payload(self) -> str:
        return "getBoardsRequest"

    def unpack_request(self, request: GenericMessage) -> None:
        return None

    def prepare_response(self, response: Boards) -> GenericMessage:
        return GenericMessage(
            getBoardsResponse=GetBoardsResponse(
                name=response.boards
            )
        )


@dataclass
class DeviceStatus(object):

    class Status(IntEnum):
        UNREACHABLE = 0
        READY = 1
        FLASHING = 2
        ERROR = 3

        def to_proto(self) -> DeviceUpdateStatus.Status:
            return getattr(DeviceUpdateStatus.Status, self.name)

    status: Status
    flashing_progress: Optional[float] = None
    image: Optional[str] = None

    def to_message(self) -> GenericMessage:
        return GenericMessage(
            deviceUpdateStatus=DeviceUpdateStatus(
                status=self.status.to_proto(),
                flashingProgress=self.flashing_progress,
                image=self.image
            )
        )


class UpdateDeviceStatus(IRequester[None]):

    def __init__(self, status):
        self._status: DeviceStatus = status

    def prepare(self) -> GenericMessage:
        return self._status.to_message()

    @property
    def response_payload(self) -> str:
        return "ok"

    def handle_response(self, response: GenericMessage) -> None:
        return None
