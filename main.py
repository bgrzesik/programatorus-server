import socket
from datetime import datetime

import Adafruit_SSD1306
from PIL import ImageDraw
from gpiozero import Button

from server.comm.transport.bt import BTServer
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
        self.proxy.start_async("flash", {'board': 'rp2040.cfg', 'target': self.file_name})


def main():
    fs = FlashService()
    request_handler = RequestHandler.serve(fs)
    proxy = Proxy.serve(request_handler)
    server = BTServer(proxy)
    server.start()

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
    main()
