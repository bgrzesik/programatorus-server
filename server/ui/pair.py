from concurrent.futures import Future
from .menu_item import MenuItem, FONT

import os
if os.uname().sysname == "Linux":
    from ..comm.listener.bt import PairingAgent, PairingClient
else:
    # Stub
    class PairingClient(object):
        pass

class PairDialog(MenuItem, PairingClient):
    def __init__(self):
        super().__init__(["Enable pairing"])
        self.header = "Pair device"
        self._agent = PairingAgent(self)
        self._pin = None
        self._future: Future[bool] = Future()
        self.text = "ready for pairing"

    def on_state_changed(self, state):
        if self._pin is not None:
            self.text = f"Pin: {self._pin}"
        else:
            self.text = "ready for pairing"

    def confirm_pin(self, pin) -> Future[bool]:
        self._future = Future()
        self._pin = pin
        self.text = f"Pin: {self._pin}"
        return self._future

    @property
    def visible_text(self):
        return self.text + "\n" + "YES (X)            NO (<)"

    def on_select(self):
        if self._pin is None:
            pass
        else:
            self._future.set_result(True)
            self._pin = None
            self.text = "ready for pairing"

    def on_prev(self):
        if self._pin is None:
            pass
        else:
            self._future.set_result(False)
            self._pin = None
            self.text = "ready for pairing"

    def draw(self, draw, x, y):
        if self.is_selected:
            draw.rectangle((x, y, x + self.width, y +
                           self.height), outline=1, fill=0)

            draw.text((x + 1, y), self.text, font=FONT, fill=1)
            if "Pin" in self.text:
                draw.text((x + 1, y + 8), "YES (X)            NO (<)", font=FONT, fill=1)
            else:
                draw.text((x + 1, y + 8), "initiate with mobile", font=FONT, fill=1)
        else:
            draw.text((x + 1, y), self.header, font=FONT, fill=1)