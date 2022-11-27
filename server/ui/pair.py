from concurrent.futures import Future
from .menu import MenuItem, FONT

import os
if os.uname().sysname == "Linux":
    from ..comm.listener.bt import PairingAgent, PairingClient
else:
    # Stub
    class PairingClient(object):
        pass

class PairDialog(MenuItem, PairingClient):
    def __init__(self):
        super().__init__("Enable pairing")
        self.height = 16
        self.width = 96
        self._agent = PairingAgent(self)
        self._pin = None
        self._future: Future[bool] = Future()
        self.text = "Connect now"

    def on_state_changed(self, state):
        if self._pin is not None:
            self.text = f"Pin: {self._pin}"
        else:
            self.text = "Connect now"

    def confirm_pin(self, pin) -> Future[bool]:
        self._future = Future()
        self._pin = pin
        self.text = f"Pin: {self._pin}"
        return self._future

    @property
    def visible_text(self):
        return self.text + "\n" + "YES [OK]    NO [<-]"

    def on_click(self, select=True):
        if self._pin is None:
            pass
        else:
            self._future.set_result(select)
            self._pin = None
            self.text = "Connect now"

    def draw(self, draw, x, y):
        if self.is_selected:
            draw.rectangle((x, y, x + self.width, y +
                           self.height), outline=1, fill=0)

        draw.text((x + 1, y), self.text, font=FONT, fill=1)
        draw.text((x + 1, y + 8), "YES [OK]    NO [<-]", font=FONT, fill=1)
