import time
from concurrent import futures

from .flash import FlashService


class RequestHandler(object):
    def __init__(self, executor: futures.Executor, flash_service: FlashService):
        super().__init__()
        self.executor = executor
        # self.session_controller = session_controller
        self.flash_service = flash_service

        self.request_handlers = {
            "flash": lambda args: self.executor.submit(self.flash, args)
        }

    def flash(self, args):
        cmd = [
            "-f",
            "/home/pi/bootloader/my_rpi.cfg",
            "-c",
            "transport select swd",
            "-f",
            f"/home/pi/openocd/tcl/target/{args['board']}",
            "-c",
            "targets",
            "-c",
            f"program /home/pi/bin_files/{args['target']} verify reset exit",
        ]
        return str(self.flash_service.flash(cmd)[1])

    def start_async(self, request, args):
        return self.request_handlers[request](args)

    @staticmethod
    def serve(session_controller) -> "RequestHandler":
        executor = futures.ThreadPoolExecutor(max_workers=1)
        service = RequestHandler(executor, session_controller)
        return service


class Proxy(object):
    def __init__(self, executor: futures.Executor, service: RequestHandler):
        super().__init__()
        self.executor = executor
        self.service = service

    def start_async(self, request, args):
        return self.executor.submit(self.resend, request, args)

    def resend(self, request, args):
        print("[Proxy]", request, args)

        res = self.service.start_async(request, args).result()

        print(res)

        return res

    @staticmethod
    def serve(service: RequestHandler) -> "Proxy":
        executor = futures.ThreadPoolExecutor(max_workers=1)
        proxy = Proxy(executor, service)
        return proxy


if __name__ == "__main__":
    fs = FlashService()
    requestHandler = RequestHandler.serve(fs)
    proxy = Proxy.serve(requestHandler)

    request = "flash"
    args = {"board": "stm32f0x.cfg", "target": "f07_boot.elf"}

    futs = [proxy.start_async(request, args) for _ in range(1)]

    print(futs)
    time.sleep(1)
    print(futs)

    for a in [fut.result() for fut in futs]:
        print(a)
