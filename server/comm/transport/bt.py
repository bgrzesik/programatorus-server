import ast
import subprocess
import threading

import bluetooth as bt
import pexpect

from server.comm.presentation.StreamParser import StreamParser
from server.comm.presentation.message_utils import *
from server.target.demo_store import get_files

INACTIVE = 0
AGENT_SETUP = 1
AWAITING_CONNECTION = 2
AWAITING_INPUT = 3


def pair_trust():
    child = pexpect.spawn("bluetoothctl", encoding="utf-8")
    child.sendline("discoverable on")
    child.sendline("agent off")
    child.sendline("agent DisplayYesNo")
    child.sendline("default-agent")
    try:
        child.expect("(yes/no)", timeout=20)
        print(child.before)
        res = input("[y]es/[n]o: ")
        if res[0] == "y":
            child.send("yes\ntrust\n")
    except:
        print("Failed to pair.")


class BTServer(threading.Thread):
    def __init__(self, openocd_proxy):
        threading.Thread.__init__(self)

        self.proxy = openocd_proxy

        self.uuid = "0446eb5c-d775-11ec-9d64-0242ac120002"
        self.client = None
        self.stream_parser = StreamParser()

        self.handlers = {
            CLEAR: lambda msg: None,
            GET_FILES_REQUEST: lambda msg: self.send(
                str(get_files()).encode(), JSON_DATA
            ),
            FLASH_REQUEST: lambda msg: self.flash_request(msg[5:].decode("utf-8")),
        }

    def flash_request(self, data):
        print(data)
        print(ast.literal_eval(data))
        res = self.proxy.start_async("flash", ast.literal_eval(data))
        self.send(str(res.result()).encode("utf-8"), LOG_TEXT)

    def run(self):
        # must be discoverable to advertise
        subprocess.call(["bluetoothctl", "discoverable", "on"])

        server = bt.BluetoothSocket(bt.RFCOMM)
        print("socket created")
        server.bind(("", bt.PORT_ANY))

        # Start listening. One connection
        server.listen(1)
        port = server.getsockname()[1]

        bt.advertise_service(
            server,
            "BTSrv",
            service_id=self.uuid,
            service_classes=[self.uuid, bt.SERIAL_PORT_CLASS],
            profiles=[bt.SERIAL_PORT_PROFILE],
        )

        while True:
            print(f"Waiting for connection on RFCOMM channel {port}")

            try:
                self.client, addr = server.accept()
                print("Connected with: " + str(addr))

                while True:
                    data = self.client.recv(1024)
                    print(data)
                    msg = self.stream_parser.parse(data)
                    if msg:
                        self.receive_message(msg)

            except IOError as e:
                print(e)
            except KeyboardInterrupt:
                if self.client is not None:
                    self.client.close()

                server.close()

                print("Server closing")
                break

    def send(self, message, msg_type):
        message = prep_message(message, msg_type)  # adding header
        # print(message[5:].decode('utf-8'))
        self.client.send(message)

    def receive_message(self, message):
        self.handlers[int(message[0])](message)


def main():
    server = BTServer()
    server.run()


if __name__ == "__main__":
    pair_trust()
    main()


class PairThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.state = INACTIVE
        self.display_text = "Enable pairing"
        self.event = threading.Event()
        self.decision = None

    def run(self):
        self.state = AGENT_SETUP
        # print("agent setup")
        self.display_text = "setup ..."
        child = pexpect.spawn("bluetoothctl", encoding="utf-8")
        child.sendline("discoverable on")
        child.sendline("agent off")
        child.sendline("agent DisplayYesNo")
        child.sendline("default-agent")

        # print("waiting for connection")
        fail = None
        try:
            self.state = AWAITING_CONNECTION
            self.display_text = "connect now"
            child.expect("(yes/no)", timeout=30)
            print(child.before)
            self.state = AWAITING_INPUT
            self.display_text = child.before[-17:-2]
            self.event.wait()
            if self.decision:
                child.send("yes\ntrust\n")
            else:
                child.send("no\n")
        except:
            fail = True
        if fail:
            self.display_text = "not paired. pair again?"
        else:
            self.display_text = "paired. pair again?"
        self.state = INACTIVE

    def notify(self, decision):
        print("decision", decision)
        self.decision = decision
        self.event.set()
