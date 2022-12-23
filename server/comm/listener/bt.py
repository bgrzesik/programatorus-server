import logging
import socket
import functools
import threading
import subprocess
from concurrent.futures import Future
from abc import ABC, abstractmethod

import bluetooth as bt

from ...tasker import Tasker
from .listener import SocketListener

import dbus
import dbus.service
import dbus.mainloop.glib


class _Agent(dbus.service.Object):
    BUS_NAME = 'org.bluez'
    AGENT_INTERFACE = 'org.bluez.Agent1'
    AGENT_PATH = "/test/programatorus"

    def __init__(self, mainloop, on_pair):
        dbus.service.Object.__init__(self, dbus.SystemBus(),
                                     _Agent.AGENT_PATH)
        self._mainloop = mainloop
        self._on_pair = on_pair

    def set_trusted(self, path):
        props = dbus.Interface(self.bus.get_object("org.bluez", path),
                               "org.freedesktop.DBus.Properties")
        logging.debug(f"set_trusted(): Trusing {path}")
        props.Set("org.bluez.Device1", "Trusted", True)

    @dbus.service.method(AGENT_INTERFACE,
                         in_signature="", out_signature="")
    def Release(self):
        print("Release")
        self._mainloop.quit()

    @dbus.service.method(AGENT_INTERFACE,
                         in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print("RequestPinCode (%s)" % (device))
        self.set_trusted(device)
        return "000000"

    @dbus.service.method(AGENT_INTERFACE,
                         in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        class Rejected(dbus.DBusException):
            _dbus_error_name = "org.bluez.Error.Rejected"

        logging.debug(f"RequestConfirmation(): device={device} path={passkey}")
        self._on_pair(device, passkey)

    @dbus.service.method(AGENT_INTERFACE,
                         in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")


class PairingClient(ABC):

    @abstractmethod
    def confirm_pin(self, pin: str) -> Future[bool]:
        raise NotImplementedError


class PairingAgent(Tasker):

    def __init__(self, client: PairingClient):
        super().__init__()

        from gi.repository import GLib
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        dbus.mainloop.glib.threads_init()
        bus = dbus.SystemBus()

        self.mainloop = GLib.MainLoop()
        self._agent = _Agent(self.mainloop, self._on_pair)

        obj = bus.get_object(_Agent.BUS_NAME, "/org/bluez")
        inf = dbus.Interface(obj, "org.bluez.AgentManager1")
        inf.RegisterAgent(_Agent.AGENT_PATH, "DisplayYesNo")

        inf.RequestDefaultAgent(_Agent.AGENT_PATH)

        self._client = client
        self._thread = threading.Thread(target=self.mainloop.run)
        self._thread.start()

    def pair(self):
        pass

    @Tasker.handler()
    def _on_pair(self, device, pin):
        logging.debug("_on_pair()")
        self._client.confirm_pin(pin) \
            .add_done_callback(functools.partial(self._trust, device))

    @Tasker.handler()
    def _trust(self, device, fut):
        logging.debug("_trust()")
        if fut.result():
            self._agent.set_trusted(device)


class BluetoothListener(SocketListener, Tasker):
    UUID = "0446eb5c-d775-11ec-9d64-0242ac120002"

    def __init__(self, client, wrap_transport=True):
        SocketListener.__init__(self, client, wrap_transport=wrap_transport)

    @Tasker.assert_executor()
    def _set_discoverable(self, discoverable=True):
        setting = "on" if discoverable else "off"
        logging.info(f"set_discoverable(): discoverable={discoverable}")
        subprocess.call(["bluetoothctl", "discoverable", setting])

    @Tasker.assert_executor()
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
