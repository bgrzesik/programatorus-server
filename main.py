import logging
import socket
from typing import List
from datetime import datetime
from concurrent.futures import Future

import Adafruit_SSD1306
from gpiozero import Button
from PIL import ImageDraw, Image

from server.target.request_handler import Proxy, RequestHandler
from server.target.demo_store import get_files
from server.target.flash import FlashService
from server.ui.menu import MenuItem, Menu
from server.ui.pair import PairDialog
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


class TimeMenuItem(MenuItem):
    def __init__(self):
        MenuItem.__init__(self, None)

    @property
    def visible_text(self):
        now = datetime.now()
        return now.strftime("%H:%M:%S")


class CounterMenuItem(MenuItem):
    def __init__(self):
        self.counter = 0
        MenuItem.__init__(self, None)

    @property
    def visible_text(self):
        return f"Counter {self.counter}"

    def on_click(self, select=True):
        if select:
            self.counter += 1
        else:
            self.counter -= 1


class IpMenuItem(MenuItem):
    def __init__(self):
        MenuItem.__init__(self, None)

    @property
    def visible_text(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            return str(s.getsockname()[0])
        except Exception:
            return "Get IP error"


class ProgramFlashMenuItem(MenuItem):
    def __init__(self, file_name, proxy):
        self.file_name = file_name
        self.proxy = proxy
        MenuItem.__init__(self, file_name)

    def on_click(self, select=True):
        self.proxy.start_async(
            "flash", {"board": "rp2040.cfg", "target": self.file_name}
        )


class GetBoardsResponder(protocol.OnGetBoards):

    def on_request(self, request) -> Future[protocol.BoardsData]:
        future: Future[protocol.BoardsData] = Future()
        future.set_result(protocol.BoardsData(
            all=[
                protocol.Board("Test Board 1", False),
                protocol.Board("Test Board 2", True),
            ],
            favorites=[
                protocol.Board("Test Board 1", False),
                protocol.Board("Test Board 2", True),
            ]
        ))
        return future


class GetFirmwareResponder(protocol.OnGetFirmware):

    def on_request(self, request) -> Future[protocol.FirmwareData]:
        print("getFirmwareResponder")
        future: Future[protocol.FirmwareData] = Future()
        future.set_result(protocol.FirmwareData(
            all=[
                protocol.Firmware("Test Firmware 1", False),
                protocol.Firmware("Test Firmware 2", True),
            ],
            favorites=[
                protocol.Firmware("Test Firmware 1", False),
                protocol.Firmware("Test Firmware 2", True),
            ]
        ))
        return future

class PutFirmwareResponder(protocol.OnPutFirmware):

    def on_request(self, request) -> Future[bool]:
        print("putFirmwareResponder", request)
        future: Future[bool] = Future()
        future.set_result(True)
        return future

class PutBoardsResponder(protocol.OnPutBoards):

    def on_request(self, request) -> Future[bool]:
        print("putBoardsResponder", request)
        future: Future[bool] = Future()
        future.set_result(True)
        return future

class MobileClient(IConnectionClient):

    def __init__(self, transport: ITransportBuilder, file_store: FileStore):
        self._router = RequestRouter(
            GetBoardsResponder(),
            FileUploadHandler(file_store),
            GetFirmwareResponder(),
            PutFirmwareResponder(),
            PutBoardsResponder(),
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

    def __init__(self):
        self._clients: List[MobileClient] = []
        self._file_store = FileStore()

    def on_connect(self, transport_builder: ITransportBuilder):
        logging.info("on_connect():")
        self._clients.append(MobileClient(transport_builder, self._file_store))


def main():
    fs = FlashService()
    request_handler = RequestHandler.serve(fs)
    proxy = Proxy.serve(request_handler)

    listener = BluetoothListener(ListenerClient())
    listener.listen()

    disp = Adafruit_SSD1306.SSD1306_128_32(rst=24)
    btn_select = Button(26, pull_up=True)
    btn_down = Button(19, pull_up=True)
    btn_up = Button(13, pull_up=True)
    btn_back = Button(6, pull_up=True)

    menu_items = [
        TimeMenuItem(),
        PairDialog(),
        IpMenuItem(),
        CounterMenuItem(),
        MenuItem("1 button"),
    ]

    for file_name in get_files()["binary"]:
        menu_items.append(ProgramFlashMenuItem(file_name, proxy))

    menu = Menu(menu_items)

    btn_up.when_pressed = menu.on_up_btn
    btn_down.when_pressed = menu.on_down_btn
    btn_select.when_pressed = menu.on_select_btn
    btn_back.when_pressed = menu.on_back_btn
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
