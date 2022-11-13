import os
import select
import logging
import socket
import subprocess
from enum import Enum
from typing import Optional
from concurrent.futures import Future
from abc import ABC, abstractmethod

import bluetooth as bt

from server.actor import Actor
from server.comm.listener.listener import SocketListener


class PairingState(Enum):
    INACTIVE = 0
    AGENT_SETUP = 1
    AWAITING_CONNECTION = 2
    AWAITING_INPUT = 3


class PairingClient(ABC):

    @abstractmethod
    def on_state_changed(self, state: PairingState):
        raise NotImplementedError

    @abstractmethod
    def confirm_pin(self, pin: str) -> Future[bool]:
        raise NotImplementedError


class PairingAgent(Actor):

    def __init__(self, client: PairingClient):
        super().__init__()
        self._client = client
        self._state = PairingState.INACTIVE
        self._client.on_state_changed(PairingState.INACTIVE)
        self._proc: Optional[subprocess.Popen] = None

        self._event, self._notify = os.pipe()
        os.set_blocking(self._event, False)

    @property
    def state(self) -> PairingState:
        return self._state

    def _set_state(self, state):
        self._state = state
        self._client.on_state_changed(state)

    def cancel(self):
        logging.debug("cancel():")
        os.write(self._notify, b"\0")

    def drain_event(self):
        try:
            while os.read(self._event, 1):
                pass
        except BlockingIOError:
            pass

    @Actor.handler(guarded=True)
    def pair(self):
        try:
            self._set_state(PairingState.AGENT_SETUP)
            logging.debug("pair(): Setting up agent")

            subprocess.run(["bluetoothctl", "discoverable", "on"])
            self.drain_event()

            with subprocess.Popen("bluetoothctl",
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE) as proc:
                self._proc = proc
                self._canceled = False

                assert proc.stdin and proc.stdout
                lines = [
                    b"discoverable on\n",
                    b"agent off\n",
                    b"agent DisplayYesNo\n",
                    b"default-agent\n",
                ]
                for line in lines:
                    proc.stdin.write(line)

                self._set_state(PairingState.AWAITING_CONNECTION)
                logging.debug("pair(): Awaiting connection")

                pin = None
                buf = []
                while pin is None:
                    read, [], [] = select.select([self._event, proc.stdout],
                                                 [], [])

                    if self._event in read:
                        self.drain_event()
                        return
                    elif proc.stdout not in read:
                        continue

                    buf.append(chr(proc.stdout.read(1)[0]))
                    if len(buf) > len("passkey 000000 (yes/no):"):
                        buf.pop(0)

                    if "".join(buf).endswith("(yes/no):"):
                        pin = "".join(buf[len("passkey "):-len(" (yes/no):")])
                        break

                    if self._canceled:
                        return

                self._set_state(PairingState.AWAITING_INPUT)
                logging.info(f"pair(): pin={pin}")

                if pin and self._client.confirm_pin(pin).result():
                    proc.stdin.write(b"yes\ntrust\n")
                else:
                    proc.stdin.write(b"no\n")

                self._set_state(PairingState.INACTIVE)

        except Exception as exc:
            logging.error("", exc_info=exc)
            raise
        finally:
            self._proc = proc
            self._canceled = False
            try:
                subprocess.run(["bluetoothctl", "pairable", "off"])
                subprocess.run(["bluetoothctl", "discoverable", "off"])
                logging.debug("pair(): Disabled discoverability")
            except Exception as exc:
                logging.error("", exc_info=exc)
                raise
            finally:
                if self._state != PairingState.INACTIVE:
                    self._set_state(PairingState.INACTIVE)


class BluetoothListener(SocketListener, Actor):
    UUID = "0446eb5c-d775-11ec-9d64-0242ac120002"

    def __init__(self, client, wrap_transport=True):
        SocketListener.__init__(self, client, wrap_transport=wrap_transport)

    @Actor.assert_executor()
    def _set_discoverable(self, discoverable=True):
        setting = "on" if discoverable else "off"
        logging.info(f"set_discoverable(): discoverable={discoverable}")
        subprocess.call(["bluetoothctl", "discoverable", setting])

    @Actor.assert_executor()
    def create_socket(self) -> socket.socket:
        logging.info("listen():")
        server = bt.BluetoothSocket(bt.RFCOMM)

        self._set_discoverable()

        logging.info("create_socket(): Socket created")
        server.bind(("", bt.PORT_ANY))

        # Start listening. One connection
        server.listen(1)

        logging.debug("create_socket(): Advertising service")

        bt.advertise_service(
            server,
            "Programatorus",
            service_id=BluetoothListener.UUID,
            service_classes=[BluetoothListener.UUID, bt.SERIAL_PORT_CLASS],
            profiles=[bt.SERIAL_PORT_PROFILE],
        )

        port = server.getsockname()[1]
        logging.info(f"create_socket(): Listening on {port}")

        return server
