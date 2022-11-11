class FrameEncoder(object):

    def __init__(self, consumer):
        self._consumer = consumer
        self._buffer = []

    def write_byte(self, byte):
        if byte != 0:
            self._buffer.append(byte)
        else:
            self._write_slice(False)

    def write_slice_size(self, size):
        assert size <= 0x3fff

        lo = 0x80 | (size & 0x7f)
        size = size >> 7
        hi = 0x80 | (size & 0x7f)

        self._consumer([lo, hi])

    def start_frame(self):
        self._reset()
        self._consumer([0x00])

    def _write_slice(self, eof):
        self.write_slice_size(len(self._buffer) + (1 if eof else 0))
        self._consumer(self._buffer)
        self._reset()

    def finish_frame(self):
        if len(self._buffer) > 0:
            self._write_slice(True)

        self._reset()
        self._consumer([0x00])

    def _reset(self):
        self._buffer = []


class FrameDecoder(object):

    def __init__(self, producer):
        self._producer = producer
        self._eof = False
        self._buffer = []

    def read_frame(self):
        self._buffer = []

        # Skip partial frame
        read = self._producer()
        while read != 0 and read != -1:
            read = self._producer()

        if read == -1:
            self._eof = True
            return None

        # Skip zero(s)
        read = self._producer()
        while read == 0:
            read = self._producer()

        if read == -1:
            self._eof = True
            return None

        while read != 0:
            slice_size = read & 0x7f

            read = self._producer()
            if read == 0 or read == -1:
                # Error while parsing stream
                self._eof = read == -1
                return None

            slice_size = slice_size | ((read & 0x7f) << 7)

            for i in range(slice_size):
                read = self._producer()
                if read == 0 or read == -1:
                    break
                self._buffer.append(read)

            if read == 0:
                break

            self._buffer.append(0x00)

            read = self._producer()
            if read == 0 or read == -1:
                break

        self._eof = read == -1
        frame = self._buffer
        self._buffer = []

        return frame
