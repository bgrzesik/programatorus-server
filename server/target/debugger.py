import os
import select
import typing
import threading
import subprocess
import io

from ..actor import Actor


class Debugger(Actor):

    def __init__(self, firmware, board):
        super().__init__()

        self._firmware = firmware
        self._board = board

        self._event, self._notify = os.pipe()
        os.set_blocking(self._event, False)

        self._is_running = False
        self._poll = select.poll()
        self._poll.register(self._event, select.POLLIN)
        self._poller: typing.Optional[threading.Thread] = None
        self._gdb: typing.Optional[subprocess.Popen] = None

    @Actor.handler(guarded=True)
    def start(self):
        assert self._poller is None and self._gdb is None

        openocd_cmd = "openocd " \
            "-c 'gdb_port pipe'" \
            "-f interface/raspberrypi-swd.cfg" \
            f"-f {self._board}"

        self._gdb = subprocess.Popen(
            args=[
                "gdb-multiarch",
                "-ex",
                f"target extended-remote | {openocd_cmd}",
                self._firmware
            ],
            shell=True,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        os.set_blocking(self._gdb.stdout.fileno(), False)
        self._poll.register(self._gdb.stdout.fileno(), select.POLLIN)

        os.set_blocking(self._gdb.stderr.fileno(), False)
        self._poll.register(self._gdb.stderr.fileno(), select.POLLIN)

        self._is_running = True
        self._poller = threading.Thread(target=self._poller_thread)
        self._poller.start()

    @Actor.handler(guarded=True)
    def send_command(self, command: str):
        assert self._gdb is not None
        self._gdb.stdin.writelines([command.encode("utf-8")])
        self._gdb.stdin.flush()

    @Actor.handler(guarded=True)
    def stop(self):
        assert self._poller is not None and self._gdb is not None
        self._is_running = False
        self._notify_poller()

        self._poller.join()
        self._poller = None

        self._poll.unregister(self._gdb.stdout.fileno())
        self._poll.unregister(self._gdb.stderr.fileno())

        self.send_command("set confirm off\nexit\n")

        self._gdb.kill()
        self._gdb = None

    @Actor.handler()
    def _read_line(self, stream: io.BytesIO):
        try:
            while True:
                line = stream.readline()
                if line:
                    print(line)
                else:
                    break
        except BlockingIOError:
            return

    def _notify_poller(self):
        os.write(self._notify, b"\0")

    def _poller_thread(self):
        while self._is_running and self._gdb is not None:
            for fd, why in self._poll.poll():
                if fd == self._gdb.stdout.fileno():
                    self._read_line(self._gdb.stdout)
                elif fd == self._gdb.stderr.fileno():
                    self._read_line(self._gdb.stderr)
