import logging
import subprocess
from concurrent import futures

log = logging.getLogger(__name__)

class FlashService(object):

    def __init__(self):
        super().__init__()
        self.executor = futures.ThreadPoolExecutor(max_workers=1)

    def start_async(self, args):
        return self.executor.submit(self.resend, args)

    def flash(self, args):
        cmd = ["openocd"]
        for arg in args:
            cmd.append(arg)

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             shell=False)
        return p.communicate()
