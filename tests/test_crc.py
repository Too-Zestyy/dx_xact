import unittest

from checksums.crc import reverse_number_bit_order, calc_crc16b, calc_soundbank_crc


class TestV2plusAudioFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._example_file_data = (b'\x01\x01\x00\x00\x00\x00\x00\x10\x00\x01\x01\x00\x0b\x00\x00\x00\xd6\x00\x00\x00'
                                  b'\xff\xff\xff\xff\x01\x01\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
                                  b'\x8a\x00\x00\x00\xdb\x00\x00\x00\xfb\x00\x00\x00\xca\x00\x00\x00911\x00\x00\x00'
                                  b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                                  b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                                  b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00911\x00'
                                  b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                                  b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                                  b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                                  b'\x00\x01\x00\xb4\x00\x00\x00\x0c\x00\x00\x00\x00\x04\xca\x00\x00\x00\xff\xff\xff'
                                  b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
                                  b'\xff\xff\xff\xff\xff\x00\x00\xff\xff\x01\x01\x00\x00\xff\xffGM_BGM_911\x00')
        cls._example_file_checksum = 0x9D88

    def test_crc_16_b(self):
        crc_16_b = calc_crc16b(self._example_file_data)
        self.assertEqual(
            crc_16_b, self._example_file_checksum,
            f'\n\nExpected: {hex(self._example_file_checksum)}\n'
            f'Got:      {hex(crc_16_b)}'
        )

    def test_soundbank_crc(self):
        expected_value = b'\x88\x9D'
        soundbank_crc = calc_soundbank_crc(self._example_file_data)

        self.assertEqual(
            soundbank_crc, expected_value,
            f'\n\nExpected: {expected_value}\n'
            f'Got:      {soundbank_crc}'
        )


def get_int_bit_count(value: int) -> int:
    count = 0
    while value:
        count += 1
        value >>= 1

    return count


class TestNumberBitOrderReversal(unittest.TestCase):
    def test_known_bit_reversal_answers(self):
        known_bit_reversal_answers = (
            (0b11111111, 0b11111111),
            (0b11110000, 0b00001111),
            (0b11110001, 0b10001111),
            (0b11000000, 0b00000011),
            (0b10000000, 0b00000001),
            (0b10, 0b01),
            (0b1001, 0b1001),
            (0b1101, 0b1011),
            (0b11000000000000000000001, 0b10000000000000000000011),
        )

        for input, expected_output in known_bit_reversal_answers:
            with self.subTest(input=input, expected_output=expected_output):
                self.assertEqual(reverse_number_bit_order(input, get_int_bit_count(input)), expected_output)
