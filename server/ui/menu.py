import os

from PIL import ImageFont, Image

# from main import TimeMenuItem, IpMenuItem, CounterMenuItem, ProgramFlashMenuItem
from server.target.config_repository import BoardsService, FirmwareService
from server.ui.menu_item import MenuItem
from server.ui.pair import PairDialog

base_dir = os.path.dirname(os.path.realpath(__file__))
BOTTOM_BAR = Image.open(os.path.join(base_dir, "bar.png"))
FONT = ImageFont.truetype(os.path.join(base_dir, "slkscr.ttf"), 8)


class Menu(object):
    def __init__(self, proxy, boards_service: BoardsService, firmware_service: FirmwareService, y_wrap=64):
        self.y_wrap = y_wrap
        self.selected = 0
        self.up = False
        self.down = False
        self.select = False
        self.back = False

        self.chosen_board = ""
        self.chosen_firmware = ""

        self.proxy = proxy
        self.boards_service = boards_service
        self.firmware_service = firmware_service

        self.items = self.init_items()

    def init_items(self):
        return [
            ProgramFlashMenuItem(self, "Flash Device"),
            ChooseBoardMenuItem(self, f"board: {self.chosen_board}"),
            ChooseFirmwareMenuItem(self, f"board: {self.chosen_board}"),
            PairDialog(),
        ]

    def on_select_btn(self):
        self.items[self.selected].on_select()

    def on_back_btn(self):
        self.items[self.selected].on_prev()

    def on_next_btn(self):
        self.items[self.selected].on_next()

    def on_up_btn(self):
        self.selected -= 1
        self.selected %= len(self.items)
        self.items[self.selected].refresh()

    def on_down_btn(self):
        self.selected += 1
        self.selected %= len(self.items)
        self.items[self.selected].refresh()

    def draw(self, draw):
        x, y = 0, 0
        max_w = 0

        visible_items = self.items[self.selected - 1: self.selected + 2]
        if self.selected == 0:
            visible_items = self.items[:3]

        for item in visible_items:
            item.is_selected = item is self.items[self.selected]
            if y + item.height <= 32:
                item.draw(draw, x, y)

            y += item.height
            max_w = max(max_w, item.width)

            if y >= self.y_wrap:
                y = 0
                x += max_w
                max_w = 0

        # draw.bitmap((0, 32 - 8), BOTTOM_BAR, fill=1)

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

    def on_next(self, select=True):
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
    def __init__(self, parent, header):
        self.parent = parent
        self.state = 'PROMPT'
        MenuItem.__init__(self, [], header)

    def on_select(self):
        if self.state == 'AWAIT':
            return
        if self.state != 'PROMPT':
            self.state = 'PROMPT'
            return

        def show_result_cb(future):
            if "Verified OK" in future.result():
                self.state = 'SUCCESS'
            else:
                self.state = 'FAILED'

        future = self.parent.proxy.start_async(
            "flash", {"board": self.parent.chosen_board, "target": self.parent.chosen_firmware}
        )
        future.add_done_callback(show_result_cb)
        self.state = 'AWAIT'

    @property
    def visible_text(self):
        if not self.is_selected:
            return [self.header]
        elif self.state == 'PROMPT':
            return [
            "Flash device using",
            "files below    submit (x)"
        ]
        elif self.state == 'AWAIT':
            return [
            "awaiting flash results",
            ""
        ]
        elif self.state == 'SUCCESS':
            return [
            "Finished with success",
            "                   OK (x)"
        ]
        else:
            return [
            "Finished with failure",
            "                   OK (x)"
        ]


ALL = 0
FAV = 1
class ChooseBoardMenuItem(MenuItem):
    def __init__(self, parent: Menu, header):
        self.parent = parent

        self.width = 128

        data = parent.boards_service.get()
        self.apply_lists(data)

        self.indices = [0, 0]
        self.state = FAV if len(self.values[FAV]) > 0 else ALL
        self.parent.chosen_board = self.chosen

        MenuItem.__init__(self, [], header)

    @property
    def chosen(self):
        return self.values[self.state][self.indices[self.state]]

    @property
    def visible_text(self):
        return [
            f"< {self.chosen} >",
            f"{'[fav]      all    swap(x)' if self.state == FAV else ' fav      [all]   swap(x)'}"
        ] if self.is_selected else [f"board: {self.chosen}"]
    def on_next(self):
        self.indices[self.state] += 1
        self.indices[self.state] %= len(self.values[self.state])
        self.parent.chosen_board = self.chosen

    def on_prev(self):
        self.indices[self.state] += 1
        self.indices[self.state] %= len(self.values[self.state])
        self.parent.chosen_board = self.chosen

    def on_select(self):
        self.state = FAV if (self.state == ALL and self.values[FAV]) else ALL

    def refresh(self):
        data = self.parent.boards_service.get()
        self.apply_lists(data)

    def apply_lists(self, data):
        self.values = [
            list(map(lambda b: b.name, data.all)),
            list(map(lambda b: b.name, data.favorites))
        ]
        if len(self.values[ALL]) == 0:
            self.values[ALL].append("[None]")
        if len(self.values[FAV]) == 0:
            self.values[FAV].append("[None]")


class ChooseFirmwareMenuItem(MenuItem):
    def __init__(self, parent: Menu, header):
        self.parent = parent

        self.width = 128

        data = parent.firmware_service.get()
        self.apply_lists(data)

        self.indices = [0, 0]
        self.state = FAV if len(self.values[FAV]) > 0 else ALL
        self.parent.chosen_firmware = self.chosen

        MenuItem.__init__(self, [], header)

    @property
    def chosen(self):
        return self.values[self.state][self.indices[self.state]]

    @property
    def visible_text(self):
        return [
            f"< {self.chosen} >",
            f"{'[fav]      all    swap(x)' if self.state == FAV else ' fav      [all]   swap(x)'}"
        ] if self.is_selected else [f"firmware: {self.chosen}"]

    def on_next(self):
        self.indices[self.state] += 1
        self.indices[self.state] %= len(self.values[self.state])
        self.parent.chosen_firmware = self.chosen

    def on_prev(self):
        self.indices[self.state] += 1
        self.indices[self.state] %= len(self.values[self.state])
        self.parent.chosen_firmware = self.chosen

    def on_select(self):
        self.state = FAV if self.state == ALL else ALL

    def refresh(self):
        data = self.parent.firmware_service.get()
        self.apply_lists(data)
        self.parent.chosen_firmware = self.chosen

    def apply_lists(self, data):
        self.values = [
            list(map(lambda b: b.name, data.all)),
            list(map(lambda b: b.name, data.favorites))
        ]
        if len(self.values[ALL]) == 0:
            self.values[ALL].append("[None]")
        if len(self.values[FAV]) == 0:
            self.values[FAV].append("[None]")

