from concurrent.futures import Future

from server.comm.listener.bt import PairingAgent, PairingClient, PairingState
from server.ui.menu import MenuItem, FONT


class PairDialog(MenuItem, PairingClient):
    def __init__(self):
        super().__init__("Enable pairing")
        self.height = 16
        self.width = 96
        self._agent = PairingAgent(self)
        self._pin = "000000"
        self._future: Future[bool] = Future()

    def on_state_changed(self, state):
        if state == PairingState.INACTIVE:
            self.text = "Enabling pairing"
        elif state == PairingState.AGENT_SETUP:
            self.text = "Please wait..."
        elif state == PairingState.AWAITING_CONNECTION:
            self.text = "Connect now"
        elif state == PairingState.AWAITING_INPUT:
            self.text = f"Pin: {self._pin}"

    def confirm_pin(self, pin) -> Future[bool]:
        self._future = Future()
        self._pin = pin
        self.on_state_changed(PairingState.AWAITING_INPUT)
        return self._future

    @property
    def visible_text(self):
        return self.text + "\n" + "YES [OK]    NO [<-]"

    def on_click(self, select=True):
        if self._agent.state == PairingState.INACTIVE:
            self._agent.pair()
        elif self._agent.state == PairingState.AWAITING_CONNECTION:
            self._agent.cancel()
        elif self._agent.state == PairingState.AWAITING_INPUT:
            self._future.set_result(select)

    def draw(self, draw, x, y):
        if self.is_selected:
            draw.rectangle((x, y, x + self.width, y +
                           self.height), outline=1, fill=0)

        draw.text((x + 1, y), self.text, font=FONT, fill=1)
        draw.text((x + 1, y + 8), "YES [OK]    NO [<-]", font=FONT, fill=1)
