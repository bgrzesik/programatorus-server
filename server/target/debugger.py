import os
import select
import typing
import threading
import subprocess
import io
import logging

from concurrent.futures import Future
from abc import ABC, abstractmethod
from enum import Enum

from ..actor import Actor
from ..comm.protocol import DebuggerLine, SendDebuggerLine, DebuggerStart, \
                            OnDebuggerStart, OnDebuggerLine, OnDebuggerStop
from ..comm.session.session import Session


class DebuggerClient(ABC):

    @abstractmethod
    def on_line(self, line):
        pass


class Debugger(Actor):

    def __init__(self, client, firmware, board):
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

        self._client: DebuggerClient = client

    @Actor.handler(guarded=True)
    def start(self):
        assert self._poller is None and self._gdb is None

        openocd_cmd = "openocd " \
            "-c 'gdb_port pipe'" \
            "-f interface/raspberrypi-swd.cfg" \
            f"-f target/{self._board}"

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
        if self._gdb.poll() is not None:
            self.stop()
            return

        try:
            while True:
                line = stream.readline()
                if line:
                    self._client.on_line(line)
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


class DebuggerService(Actor):

    def __init__(self, session_cb):
        self._session_cb: typing.Callable[[int], Session] = session_cb
        self._debuggers: typing.Dict[int, Debugger] = {}
        self._next_session_id = 1

    def start(self, start: DebuggerStart) -> Future[int]:
        logging.debug(f"start(): start={start}")
        session_id = self._next_session_id

        self._next_session_id += 1

        debugger = Debugger(DebuggerService.Client(self, session_id),
                            start.firmware, start.target)

        self._debuggers[session_id] = debugger

        fut: Future[int] = Future()

        def on_started(future: Future[None]):
            nonlocal fut, session_id

            if future.cancelled():
                fut.cancel()
            elif future.exception() is not None:
                fut.set_exception(future.exception())
            else:
                fut.set_result(session_id)

        debugger.start().add_done_callback(on_started)

        return fut

    def stop(self, session_id: int) -> Future[None]:
        logging.debug(f"stop(): session_id={session_id}")

        if session_id in self._debuggers:
            return self._debuggers[session_id].stop()

        fut: Future[None] = Future()
        fut.set_exception(IndexError())
        return fut

    def send_line(self, line: DebuggerLine) -> Future[None]:
        logging.debug(f"send_line(): line={line}")

        if line.session_id in self._debuggers:
            return self._debuggers[line.session_id].send_command(line.line)

        fut: Future[None] = Future()
        fut.set_exception(IndexError())
        return fut

    @Actor.handler()
    def _on_line(self, session_id: int, ordinal, line):
        session = self._session_cb(session_id)

        SendDebuggerLine(DebuggerLine(session_id, ordinal, line)) \
            .request(session)

    class Client(DebuggerClient):

        def __init__(self, service, session_id):
            self._service: DebuggerService = service
            self._session_id: int = session_id
            self._ordinal = 0

        def on_line(self, line):
            self._ordinal += 1
            self._service._on_line(self._session_id, self._ordinal, line)
