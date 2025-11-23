from xact_types.enums.mini_format_tag import MiniFormatTag
from xact_types.models.wavebank.wave_format import WaveFormat


def decode_audio_format(format_data: int, version: int) -> WaveFormat:
    # Data descriptions from `unxwb`

    # version 1:
    # 1 00000000 000101011000100010 0 001 0
    # | |         |                 | |   |
    # | |         |                 | |   wFormatTag
    # | |         |                 | nChannels
    # | |         |                 ???
    # | |         nSamplesPerSec
    # | wBlockAlign
    # wBitsPerSample
    if version == 1:
        codec           = MiniFormatTag(format_data                          & ((1 << 1) - 1))
        channels        =              (format_data >>  1)                   & ((1 << 3) - 1)
        rate            =              (format_data >> (1 + 3 + 1))          & ((1 << 18) - 1)
        alignment       =              (format_data >> (1 + 3 + 1 + 18))     & ((1 << 8) - 1)
        bits_per_sample =              (format_data >> (1 + 3 + 1 + 18 + 8)) & ((1 << 1) - 1)

    # versions 2, 3, 37, 42, 43, 44 and so on, check WAVEBANKMINIWAVEFORMAT in xact3wb.h
    # 0 00000000 000111110100000000 010 01
    # | |        |                  |   |
    # | |        |                  |   wFormatTag
    # | |        |                  nChannels
    # | |        nSamplesPerSec
    # | wBlockAlign
    # wBitsPerSample
    else:
        codec           = MiniFormatTag(format_data                          & ((1 << 2) - 1))
        channels        =              (format_data >>  2)                   & ((1 << 3) - 1)
        rate            =              (format_data >> (2 + 3))              & ((1 << 18) - 1)
        alignment       =              (format_data >> (2 + 3 + 18))         & ((1 << 8) - 1)
        bits_per_sample =              (format_data >> (1 + 3 + 1 + 18 + 8)) & ((1 << 1) - 1)

    return WaveFormat(codec=codec, channels=channels, rate=rate, alignment=alignment, bits_per_sample=bits_per_sample)

def decode_v2plus_bits_per_sample_flag(bits_per_sample: int):
    # https://github.com/NeoAxis/SDK/blob/master/Engine/Src/Core/External/DirectX/Include/xact3wb.h#L81
    if bits_per_sample == 0:
        return 8
    elif bits_per_sample == 1:
        return 16
    else:
        raise ValueError('Unknown bits_per_sample value')

# TODO: Treat audio format data as bytes instead of an unsigned int?
def encode_v2plus_audio_format(codec: MiniFormatTag, channels: int, rate: int, alignment: int, bits_per_sample: int):
    codecValue         = codec.value
    channelValue       = channels        << (2)
    rateValue          = rate            << (2 + 3)
    alignmentValue     = alignment       << (2 + 3 + 18)
    bitsPerSampleValue = bits_per_sample << (1 + 3 + 1 + 18 + 8)

    # Subtra
    return codecValue | channelValue | rateValue | alignmentValue | bitsPerSampleValue


def encode_v2plus_audio_format_from_wave_format(format_fields: WaveFormat):
    return encode_v2plus_audio_format(
        codec=format_fields.codec,
        channels=format_fields.channels,
        rate=format_fields.rate,
        alignment=format_fields.alignment,
        bits_per_sample=format_fields.bits_per_sample
    )
