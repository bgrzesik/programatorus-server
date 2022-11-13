import logging
import socket
import subprocess

import bluetooth as bt

from server.actor import Actor
from server.comm.listener.listener import SocketListener


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
