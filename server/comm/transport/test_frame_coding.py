import unittest
from typing import List

from random import Random
from server.comm.transport.frame_coding import FrameEncoder, FrameDecoder


class FrameEncoderTest(unittest.TestCase):
    def test_write_slice_size(self):
        def test_number(num, expected):
            arr: List[int] = []
            encoder = FrameEncoder(arr.extend)
            encoder.write_slice_size(num)
            self.assertListEqual(expected, arr)

        test_number(0, [0x80, 0x80])
        test_number(10, [0x8A, 0x80])
        test_number(127, [0xFF, 0x80])
        test_number(128, [0x80, 0x81])
        test_number(129, [0x81, 0x81])
        test_number(256, [0x80, 0x82])
        test_number(512, [0x80, 0x84])
        test_number(1024, [0x80, 0x88])

    def _test_encoding(self, data, expected):
        arr: List[int] = []
        encoder = FrameEncoder(arr.extend)
        for byte in data:
            encoder.write_byte(byte)
        encoder.finish_frame()
        self.assertListEqual(expected, arr)

    def test_write_without_zeros(self):
        self._test_encoding(
            [0x1, 0x2, 0x3, 0x4],
            [0x85, 0x80, 0x1, 0x2, 0x3, 0x4, 0x0],
        )

        self._test_encoding(
            [0x1, 0x2, 0x3, 0x4, 0x5, 0x6],
            [0x87, 0x80, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x0],
        )

        long = [0x1A] * 256
        self._test_encoding(long, [0x81, 0x82, *long, 0x0])

    def test_write_with_zeros(self):
        self._test_encoding([0x0], [0x80, 0x80, 0x0])
        self._test_encoding([0x1, 0x0], [0x81, 0x80, 0x1, 0x0])
        self._test_encoding(
            [0x1, 0x0, 0x1], [0x81, 0x80, 0x1, 0x82, 0x80, 0x1, 0x0])
        self._test_encoding(
            [0x1, 0x0, 0x1, 0x0], [0x81, 0x80, 0x1, 0x81, 0x80, 0x1, 0x0]
        )


class FrameDecoderTest(unittest.TestCase):
    @staticmethod
    def decode_single_frame(bytes: List[int]):
        arr = bytes.copy()

        def produce():
            nonlocal arr
            if arr:
                return arr.pop(0)
            return -1

        decoder = FrameDecoder(produce)
        return decoder.read_frame()

    def _test_single_frame(self, plain, byte_stream):
        decoded = self.decode_single_frame(byte_stream)
        self.assertIsNotNone(decoded)
        self.assertListEqual(plain, decoded)

    def test_rubbish_data(self):
        self.assertIsNone(self.decode_single_frame([0xFF, 0xF1, 0x2F, 0x3F]))

    def test_empty_stream(self):
        self.assertIsNone(self.decode_single_frame([]))

    def test_null_stream(self):
        self.assertIsNone(self.decode_single_frame([0x00, 0x00]))

    def test_stream_without_zeros(self):
        self._test_single_frame([0x1], [0x00, 0x82, 0x80, 0x1, 0x0])
        self._test_single_frame([0x1, 0x2], [0x00, 0x83, 0x80, 0x1, 0x2, 0x0])
        self._test_single_frame(
            [0x1, 0x2, 0x3], [0x00, 0x84, 0x80, 0x1, 0x2, 0x3, 0x0])

    def test_steam_with_zeros(self):
        self._test_single_frame([0x1, 0x0], [0x00, 0x81, 0x80, 0x1, 0x0])
        self._test_single_frame([0x0], [0x0, 0x80, 0x80, 0x0])
        self._test_single_frame([0x1, 0x0], [0x0, 0x81, 0x80, 0x1, 0x0])
        self._test_single_frame(
            [0x1, 0x0, 0x1], [0x0, 0x81, 0x80, 0x1, 0x82, 0x80, 0x1, 0x0]
        )
        self._test_single_frame(
            [0x1, 0x0, 0x1, 0x0], [0x0, 0x81, 0x80, 0x1, 0x81, 0x80, 0x1, 0x0]
        )


class FrameEncoderDecoderTest(unittest.TestCase):
    def _test(self, plain: List[int]):
        arr: List[int] = []
        encoder = FrameEncoder(arr.extend)
        encoder.finish_frame()
        for byte in plain:
            encoder.write_byte(byte)
        encoder.finish_frame()

        def produce():
            nonlocal arr
            if arr:
                return arr.pop(0)
            return -1

        decoder = FrameDecoder(produce)
        decoded = decoder.read_frame()

        self.assertIsNotNone(decoded)
        self.assertListEqual(plain, decoded)

    def test_encode_decode_without_zeros(self):
        self._test([0x1, 0x2, 0x3, 0x4])
        self._test([0x1, 0x2, 0x3, 0x4, 0x5, 0x6])
        self._test([0x1, 0x0])
        self._test([0x1])
        self._test([0x1, 0x2])
        self._test([0x1, 0x2, 0x3])
        self._test([0x01] * 256)

    def test_encode_decode_with_zeros(self):
        self._test([0x1, 0x0])
        self._test([0x1, 0x0, 0x1])
        self._test([0x1, 0x0, 0x1, 0x0])
        self._test([0x0])
        self._test([0x0, 0x0])
        self._test([0x0, 0x1, 0x0])
        self._test([0x00] * 256)

    def test_randomized_messages(self):
        random = Random(2137)
        self._test(list(random.randbytes(20)))
        self._test(list(random.randbytes(100)))
        self._test(list(random.randbytes(512)))
        self._test(list(random.randbytes(512)))
        self._test(list(random.randbytes(1020)))
        self._test(list(random.randbytes(1020)))
        self._test(list(random.randbytes(2048)))
