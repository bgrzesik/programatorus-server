from server.comm.transport.bt_deprecated import PairThread, INACTIVE, AGENT_SETUP, AWAITING_CONNECTION
from server.ui.menu import *


class PairDialog(MenuItem):
    def __init__(self):
        super().__init__("Enable pairing")
        self.height = 16
        self.width = 96
        self.pairThread = PairThread()

    @property
    def visible_text(self):
        return self.pairThread.display_text + "\n" + "YES [OK]    NO [<-]"

    def on_click(self, select=True):
        print("clicked", select)
        if self.pairThread.state == INACTIVE:
            self.pairThread = PairThread()
            self.pairThread.start()
        elif self.pairThread.state == AGENT_SETUP:
            pass
        elif self.pairThread.state == AWAITING_CONNECTION:
            pass
        else:
            self.pairThread.notify(select)

    def draw(self, draw, x, y):
        if self.is_selected:
            draw.rectangle((x, y, x + self.width, y + self.height),
                           outline=1, fill=0)

        draw.text((x + 1, y), self.pairThread.display_text, font=FONT, fill=1)
        draw.text((x + 1, y + 8), "YES [OK]    NO [<-]", font=FONT, fill=1)
