import logging
import socket
from typing import List
from datetime import datetime
from concurrent.futures import Future

import Adafruit_SSD1306
from gpiozero import Button
from PIL import ImageDraw, Image

from server.comm.protocol import BoardsData, FirmwareData
from server.target.config_repository import ConfigFilesRepository, BoardsService, FirmwareService
from server.target.request_handler import Proxy, RequestHandler
from server.target.flash import FlashService
from server.ui.menu import Menu
from server.comm import protocol
from server.comm.app import RequestRouter
from server.comm.connection import IConnectionClient
from server.comm.listener.listener import IListenerClient
from server.comm.listener.bt import BluetoothListener
from server.comm.presentation.messenger import Messenger
from server.comm.presentation.protocol_messenger import ProtocolMessenger
from server.comm.transport.transport import ITransportBuilder
from server.comm.session.session import Session
from server.files.handler import FileStore, FileUploadHandler


class GetBoardsResponder(protocol.OnGetBoards):

    def __init__(self, boards_service: BoardsService):
        self.board_service = boards_service

    def on_request(self, request) -> Future[protocol.BoardsData]:
        future: Future[protocol.BoardsData] = Future()
        future.set_result(
            self.board_service.get()
        )
        return future


class GetFirmwareResponder(protocol.OnGetFirmware):

    def __init__(self, firmware_service: FirmwareService):
        self.firmware_service = firmware_service

    def on_request(self, request) -> Future[protocol.FirmwareData]:
        future: Future[protocol.FirmwareData] = Future()
        future.set_result(
            self.firmware_service.get()
        )
        return future

class PutFirmwareResponder(protocol.OnPutFirmware):

    def __init__(self, firmware_service: FirmwareService):
        self.firmware_service = firmware_service
    def on_request(self, request: FirmwareData) -> Future[bool]:
        future: Future[bool] = Future()
        self.firmware_service.put(request)
        future.set_result(True)
        return future

class PutBoardsResponder(protocol.OnPutBoards):

    def __init__(self, boards_service: BoardsService):
        self.board_service = boards_service

    def on_request(self, request: BoardsData) -> Future[bool]:
        future: Future[bool] = Future()
        self.board_service.put(request)
        future.set_result(True)
        return future

class FlashRequestResponder(protocol.OnFlashRequest):

    def __init__(self, proxy):

        self.proxy = proxy
    def on_request(self, request) -> Future[str]:
        args = {"board": request.board.name, "target": request.firmware.name}
        future: Future[str] = self.proxy.start_async("flash", args)
        return future

class MobileClient(IConnectionClient):

    def __init__(self, transport: ITransportBuilder, file_store: FileStore, boards_service: BoardsService, firmware_service: FirmwareService, proxy: Proxy):

        self._router = RequestRouter(
            GetBoardsResponder(boards_service),
            FileUploadHandler(file_store),
            GetFirmwareResponder(firmware_service),
            PutFirmwareResponder(firmware_service),
            PutBoardsResponder(boards_service),
            FlashRequestResponder(proxy),
            client=self
        )

        self._session = Session.Builder(
            messenger=Messenger.Builder(
                messenger=ProtocolMessenger.Builder(
                    transport=transport)
            )
        ).build(self._router)

        self._session.reconnect()

    def on_error(self):
        pass

    def on_state_changed(self, state):
        logging.info(f"on_state_changed(): {state}")


class ListenerClient(IListenerClient):

    def __init__(self, proxy: Proxy, boards_service: BoardsService, firmware_service: FirmwareService):
        self._clients: List[MobileClient] = []
        self._file_store = FileStore()
        self.boards_service = boards_service
        self.firmware_service = firmware_service
        self.proxy = proxy

    def on_connect(self, transport_builder: ITransportBuilder):
        logging.info("on_connect():")
        self._clients.append(MobileClient(
            transport_builder,
            self._file_store,
            self.boards_service,
            self.firmware_service,
            self.proxy
        ))


def main():
    fs = FlashService()
    request_handler = RequestHandler.serve(fs)
    proxy = Proxy.serve(request_handler)

    file_repository = ConfigFilesRepository()
    boards_service = BoardsService(file_repository)
    firmware_service = FirmwareService(file_repository)

    listener = BluetoothListener(ListenerClient(proxy, boards_service, firmware_service))
    listener.listen()

    menu = Menu(proxy, boards_service, firmware_service)

    disp = Adafruit_SSD1306.SSD1306_128_32(rst=24)
    btn_select = Button(26, pull_up=True)
    btn_down = Button(19, pull_up=True)
    btn_up = Button(13, pull_up=True)
    btn_back = Button(6, pull_up=True)
    btn_next = Button(0, pull_up=True)


    btn_up.when_pressed = menu.on_up_btn
    btn_down.when_pressed = menu.on_down_btn
    btn_select.when_pressed = menu.on_select_btn
    btn_back.when_pressed = menu.on_back_btn
    btn_next.when_pressed = menu.on_next_btn
    disp.begin()
    disp.clear()
    disp.display()

    image = Image.new("1", (128, 32))
    draw = ImageDraw.Draw(image)

    while True:
        draw.rectangle((0, 0, 128, 32), outline=0, fill=0)
        menu.draw(draw)

        disp.image(image)
        disp.display()


if __name__ == "__main__":
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.ERROR,
                        format="%(asctime)s,%(msecs)d %(levelname)-8s "
                        "[%(filename)s:%(lineno)d] %(message)s")
    main()
