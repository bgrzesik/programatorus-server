from PIL import ImageFont, Image

FONT = ImageFont.truetype('/home/pi/slkscr.ttf', 8)
BOTTOM_BAR = Image.open('/home/pi/bootloader/bar.png')


class Menu(object):
    def __init__(self, items, y_wrap=64):
        self.items = items
        self.y_wrap = y_wrap
        self.selected = 0
        self.up = False
        self.down = False
        self.select = False
        self.back = False

    def on_select_btn(self):
        self.items[self.selected].on_click()

    def on_back_btn(self):
        self.items[self.selected].on_click(False)

    def on_up_btn(self):
        self.selected -= 1
        self.selected %= len(self.items)

    def on_down_btn(self):
        self.selected += 1
        self.selected %= len(self.items)

    def draw(self, draw):
        x, y = 0, 0
        max_w = 0

        visible_items = self.items[self.selected - 1: self.selected + 2]
        if self.selected == 0:
            visible_items = self.items[:3]

        for item in visible_items:
            item.is_selected = item is self.items[self.selected]
            if y + item.height <= 24:
                item.draw(draw, x, y)

            y += item.height
            max_w = max(max_w, item.width)

            if y >= self.y_wrap:
                y = 0
                x += max_w
                max_w = 0

        draw.bitmap((0, 32 - 8), BOTTOM_BAR, fill=1)


class MenuItem(object):
    def __init__(self, text):
        self.text = text
        self.width = 127
        self.height = 8
        self.is_selected = False

    @property
    def visible_text(self):
        return self.text

    def on_click(self, select=True):
        pass

    def draw(self, draw, x, y):
        if self.is_selected:
            draw.rectangle((x, y, x + self.width, y + self.height),
                           outline=1, fill=0)
        draw.text((x + 1, y), self.visible_text, font=FONT, fill=1)
