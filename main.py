import logging
import socket
from concurrent.futures import Future
from datetime import datetime

import Adafruit_SSD1306
from PIL import ImageDraw
from gpiozero import Button

from google.protobuf.empty_pb2 import Empty as EmptyProto

from server.comm.listener.listener import IListenerClient
from server.comm.listener.bt import BluetoothListener
from server.comm.presentation.protocol_messenger import ProtocolMessenger
from server.comm.presentation.protocol_pb2 import GenericMessage
from server.comm.presentation.messenger import Messenger
from server.comm.session.session import Session, ISessionClient
from server.target.demo_store import get_files
from server.ui.menu import *
from server.ui.pair import PairDialog
from server.target.request_handler import *


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
        except:
            return "Get IP error"


class ProgramFlashMenuItem(MenuItem):
    def __init__(self, file_name, proxy):
        self.file_name = file_name
        self.proxy = proxy
        MenuItem.__init__(self, file_name)

    def on_click(self, select=True):
        self.proxy.start_async(
            "flash", {'board': 'rp2040.cfg', 'target': self.file_name})


class SessionClient(ISessionClient):

    def on_request(self, request):
        logging.info(f"on_request(): {request}")
        future = Future()
        future.set_result(GenericMessage(ok=EmptyProto()))
        return future

    def on_state_changed(self, state):
        logging.info(f"on_state_changed(): {state}")


class ListenerClient(IListenerClient):

    def __init__(self):
        self._sessions = []

    def on_connect(self, transport_builder):
        logging.info(f"on_connect():")
        session = Session.Builder(
            messenger=Messenger.Builder(
                messenger=ProtocolMessenger.Builder(
                    transport=transport_builder)))\
            .build(SessionClient())

        session.reconnect()

        self._sessions.append(session)

def main():
    fs = FlashService()
    request_handler = RequestHandler.serve(fs)
    proxy = Proxy.serve(request_handler)

    listener = BluetoothListener(ListenerClient())
    listener.listen()
    # server = BTServer(proxy)
    # server.start()

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

    for file_name in get_files()['binary']:
        menu_items.append(ProgramFlashMenuItem(file_name, proxy))

    menu = Menu(menu_items)

    btn_up.when_pressed = menu.on_up_btn
    btn_down.when_pressed = menu.on_down_btn
    btn_select.when_pressed = menu.on_select_btn
    btn_back.when_pressed = menu.on_back_btn
    disp.begin()
    disp.clear()
    disp.display()

    image = Image.new('1', (128, 32))
    draw = ImageDraw.Draw(image)

    while True:
        draw.rectangle((0, 0, 128, 32), outline=0, fill=0)
        menu.draw(draw)

        disp.image(image)
        disp.display()


if __name__ == '__main__':
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')

    main()
