import unittest
from copy import deepcopy
from multiprocessing.spawn import old_main_modules

from xact_types.utils.wavebank_audio_format import decode_audio_format, encode_v2plus_audio_format, \
    encode_v2plus_audio_format_from_wave_format


class TestV2plusAudioFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._audio_format_value = 2182449288
        cls._audio_format_bytes = cls._audio_format_value.to_bytes(4, signed=False)
        cls._wavebank_version = 45

    def test_audio_format_round_trip(self):
        """
        Tests that audio format data is encoded identically to the original data after a round trip.
        """
        decoded_format = decode_audio_format(self._audio_format_value, self._wavebank_version)

        re_encoded_format = encode_v2plus_audio_format_from_wave_format(decoded_format)
        re_encoded_bytes = re_encoded_format.to_bytes(4)

        self.assertEqual(
            first=self._audio_format_bytes, second=re_encoded_bytes,
            msg=f'{self._audio_format_value.to_bytes(4, signed=False)} '
            f'!= {re_encoded_format.to_bytes(4, signed=False)}'
        )

        # self.assertEqual()
        #
        # print(f'{self._audio_format_value.to_bytes(4, signed=False)} '
        #     f'== {re_encoded_format.to_bytes(4, signed=False)}')

    def test_audio_format_encoding_stability(self):
        """
        Tests that audio format data does not mutate over multiple passes of encoding and decoding.
        """
        old_round_trip_format = encode_v2plus_audio_format_from_wave_format(
            decode_audio_format(self._audio_format_value, self._wavebank_version)
        )

        for i in range(10):
            with self.subTest(i=i):
                new_round_trip_format = encode_v2plus_audio_format_from_wave_format(decode_audio_format(old_round_trip_format, self._wavebank_version))
                self.assertEqual(old_round_trip_format, new_round_trip_format)
                old_round_trip_format = deepcopy(new_round_trip_format)

