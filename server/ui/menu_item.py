import os

from PIL import ImageFont, Image

base_dir = os.path.dirname(os.path.realpath(__file__))
FONT = ImageFont.truetype(os.path.join(base_dir, "slkscr.ttf"), 8)

class MenuItem(object):
    def __init__(self, lines: list[str], header: str = "MenuItem"):
        self.header = header
        self.lines = lines
        self.width = 127
        self.is_selected = False

    @property
    def height(self):
        return 16 if self.is_selected else 8
    @property
    def visible_text(self):
        return self.lines if self.is_selected else [self.header]

    def on_prev(self):
        pass

    def on_next(self):
        pass

    def on_select(self):
        pass

    def refresh(self):
        pass

    def draw(self, draw, x, y):
        if self.is_selected:
            draw.rectangle((x, y, x + self.width, y +
                           16), outline=1, fill=0)

            for line in self.visible_text:
                draw.text((x + 1, y), line, font=FONT, fill=1)
                y += 8
        else:
            draw.text((x + 1, y), self.visible_text[0], font=FONT, fill=1)