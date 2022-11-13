from server.comm.presentation.message_utils import *


class StreamParser:
    def __init__(self):
        self.buffer = b""

    def parse(self, bytes):
        self.buffer += bytes.rstrip()
        if HEADER_LEN[self.buffer[0]] > len(self.buffer):
            return None

        msg_len = int.from_bytes(self.buffer[1:5], byteorder="big")
        if msg_len <= len(self.buffer):
            result = self.buffer[:msg_len]
            self.buffer = b""
            return result

        return None
