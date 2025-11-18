import struct
import wave
from pathlib import Path
from typing import BinaryIO

from pydantic import NonNegativeInt, PositiveInt

from xact_types.enums.mini_format_tag import MiniFormatTag
from xact_types.enums.wavebank_flags import WaveBankFlags, WaveBankTypes
from xact_types.models.segments import Segment
from xact_types.models.stream_info import StreamInfo
from xact_types.models.wave_bank_data import WaveBankData, WaveBankFriendlyName
from xact_types.models.wave_bank_header import WaveBankHeader
from xact_types.models.wave_format import WaveFormat
from xact_types.sound_effect import SoundEffect
from xact_types.utils import StrictBaseModel


class XwbValidationError(ValueError):
    """Denotes a concrete error with an XWB file's contents. Should *not* be used for heuristics."""
    pass

class XwbHeuristicError(ValueError):
    pass


def read_int_32_from_stream(stream: BinaryIO) -> int:
    return struct.unpack('<i', stream.read(4))[0]


class WaveBank(StrictBaseModel):
    # TODO: Add parsing of sound data (likely just waves for now)
    sounds: list[SoundEffect] | tuple[SoundEffect, ...]
    streams: tuple[StreamInfo, ...]

    # bank_name: WaveBankFriendlyName
    file_name: Path
    streaming: bool
    # offset: NonNegativeInt
    # packet_size: PositiveInt

    # version: PositiveInt
    play_region_offset: NonNegativeInt

    header: WaveBankHeader
    data: WaveBankData

    # TODO: Remove fields if left unused
    # is_in_use: bool
    # is_prepared: bool

    # TODO: Provide `play_region_offset` updates when bank is updated?
    #  Remove in favour of function that reads data when called?

    @classmethod
    def from_xwb(cls, file_path: Path) -> 'WaveBank':
        with (open(file_path, 'rb') as xwb_file):

            if (file_magic_number := xwb_file.read(4)) != b'WBND':
                raise XwbValidationError(f"Wavebank file is missing magic number. "
                                         f"(expected b'WBND', got {file_magic_number})")

            # XWB PARSING
            # Adapted from MonoXNA & MonoGame
            # Originally adapted from Luigi Auriemma's unxwb
            # (I wonder how long this comment chain will get?)

            # entry_name_element_size = 0
            # compact_format = 0
            # alignment = 0
            # build_time = 0

            xwb_header = WaveBankHeader(version=read_int_32_from_stream(xwb_file))
            xwb_data = WaveBankData()

            last_segment = 4

            if xwb_header.version <= 3:
                last_segment = 3
            if xwb_header.version >= 42:
                read_int_32_from_stream(xwb_file)

            for i in range(last_segment):
                xwb_header.segments[i].offset = read_int_32_from_stream(xwb_file)
                xwb_header.segments[i].length = read_int_32_from_stream(xwb_file)

            # print(xwb_header)

            # Move to the first segment
            xwb_file.seek(xwb_header.segments[0].offset)

            # WAVEBANKDATA:

            xwb_data.flags = read_int_32_from_stream(xwb_file)
            xwb_data.entry_count = read_int_32_from_stream(xwb_file)

            if xwb_header.version == 2 or xwb_header.version == 3:
                bank_name_length = 16
            else:
                bank_name_length = 64

            # Remove null bytes from bank name buffer since it's fixed length
            xwb_data.bank_name = xwb_file.read(bank_name_length).decode('utf-8').replace('\0', '')

            if xwb_header.version == 1:
                xwb_data.entry_metadata_element_size = 20
            else:
                xwb_data.entry_metadata_element_size = read_int_32_from_stream(xwb_file)
                xwb_data.entry_name_element_size = read_int_32_from_stream(xwb_file)
                xwb_data.alignment = read_int_32_from_stream(xwb_file)
                wavebank_offset = xwb_header.segments[1].offset  # METADATASEGMENT

            if (xwb_data.flags & WaveBankFlags.compact_format) != 0:
                read_int_32_from_stream(xwb_file)  # Compact format

            play_region_offset = xwb_header.segments[last_segment].offset
            if play_region_offset == 0:
                play_region_offset = wavebank_offset + (xwb_data.entry_count * xwb_data.entry_metadata_element_size)

            segidx_entry_name = 2
            if xwb_header.version >= 42:
                segidx_entry_name = 3

            if xwb_header.segments[segidx_entry_name].offset != 0 and xwb_header.segments[segidx_entry_name].length != 0:
                if xwb_data.entry_name_element_size == -1:
                    xwb_data.entry_name_element_size = 0

                # Bytes initialise to 0, and then has a byte set to 0 again - unsure of reasoning, kept for parity
                entry_name = bytearray(b'\0' * (xwb_data.entry_name_element_size + 1))
                entry_name[xwb_data.entry_name_element_size] = 0

            sounds: list[SoundEffect] = []
            streams = tuple(StreamInfo() for _ in range(xwb_data.entry_count))
            # Go to the first wave audio data
            xwb_file.seek(wavebank_offset)

            # print(wavebank_offset)
            # print(xwb_header.segments)

            is_compact_format = (xwb_data.flags & WaveBankFlags.compact_format) != 0

            if is_compact_format:
                for i in range(xwb_data.entry_count):
                    length = read_int_32_from_stream(xwb_file)
                    streams[i].format = MiniFormatTag(xwb_data.compact_format)
                    streams[i].file_offset = (length & ((1 << 21) - 1)) * xwb_data.alignment

                for i in range(xwb_data.entry_count):
                    next_offset: NonNegativeInt
                    if i == (xwb_data.entry_count - 1):
                        next_offset = xwb_header.segments[last_segment].length
                    else:
                        next_offset = streams[i + 1].file_offset

                    # The length of the current stream is by definition the space between
                    # the current and next stream's offset
                    streams[i].file_length = next_offset - streams[i].file_offset

            else:
                for i in range(xwb_data.entry_count):
                    info = streams[i]

                    if xwb_header.version == 1:
                        info.format = MiniFormatTag(read_int_32_from_stream(xwb_file))
                        info.file_offset = read_int_32_from_stream(xwb_file)
                        info.file_length = read_int_32_from_stream(xwb_file)
                        info.loop_start = read_int_32_from_stream(xwb_file)
                        info.loop_length = read_int_32_from_stream(xwb_file)

                    else:
                        flags_and_duration = read_int_32_from_stream(xwb_file)  # Unused for this

                        # Read data if the buffer includes it
                        if xwb_data.entry_metadata_element_size >= 8:
                            info.format = read_int_32_from_stream(xwb_file)
                            # NOTE: The data stored here makes this a negative number when signed,
                            # so the hex when naively converted won't be what to actually check against
                        if xwb_data.entry_metadata_element_size >= 12:
                            info.file_offset = read_int_32_from_stream(xwb_file)
                        if xwb_data.entry_metadata_element_size >= 16:
                            info.file_length = read_int_32_from_stream(xwb_file)
                        if xwb_data.entry_metadata_element_size >= 20:
                            info.loop_start = read_int_32_from_stream(xwb_file)
                        if xwb_data.entry_metadata_element_size >= 24:
                            info.loop_length = read_int_32_from_stream(xwb_file)

                    # If the metadata element size isn't large enough to include all fields,
                    # overwrite non-zero file lengths with the length of the last known segment (?)
                    if xwb_data.entry_metadata_element_size < 24:
                        if info.file_length != 0:
                            info.file_length = xwb_header.segments[last_segment].length

            # In cases like a game engine, the sounds would only be loaded if necessary
            # (i.e. when the sound is directly requested in the case of streaming banks, and immediately otherwise).
            # Since this library focuses on manipulating the data as easily as possible,
            # the audio data is loaded immediately regardless of if the wavebank calls for it.
            is_streaming_bank = bool(xwb_data.flags & WaveBankTypes.streaming)  # Unused due to above

            # if not is_streaming_bank:
            #     print('Not streaming.')
            # else:
            #     print('Streaming.')

            for i in range(len(streams)):
                info = streams[i]

                xwb_file.seek(info.file_offset + play_region_offset)
                audio_data = xwb_file.read(info.file_length)

                format_info = decode_audio_format(info.format, xwb_header.version)

                assert format_info.codec == MiniFormatTag.Pcm

                sounds.append(
                    SoundEffect(
                        codec=format_info.codec,
                        audio_data=audio_data,
                        channels=format_info.channels,
                        sample_rate=format_info.rate,
                        block_alignment=format_info.alignment,
                        loop_start=info.loop_start,
                        loop_length=info.loop_length
                    )
                )

            assert len(streams) == len(sounds)
            # print(sounds[0].codec.name)

        return WaveBank(
            sounds=sounds,
            streams=streams,
            file_name=file_path,
            streaming=is_streaming_bank,
            play_region_offset=play_region_offset,
            header=xwb_header,
            data=xwb_data,
        )

                # with wave.open('test.wav', 'wb') as wav_file:
                #
                #     wav_file.setnchannels(format_info.channels)
                #     wav_file.setframerate(format_info.rate)
                #     wav_file.setsampwidth(format_info.channels)
                #     wav_file.writeframes(audio_data)


            # TODO: Return filled WaveBank once file is read, Load sound effects (make class)


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
        codec     = MiniFormatTag(format_data                      & ((1 << 1) - 1))
        channels  =              (format_data >>  1)               & ((1 << 3) - 1)
        rate      =              (format_data >> (1 + 3 + 1))      & ((1 << 18) - 1)
        alignment =              (format_data >> (1 + 3 + 1 + 18)) & ((1 << 8) - 1)

    # versions 2, 3, 37, 42, 43, 44 and so on, check WAVEBANKMINIWAVEFORMAT in xact3wb.h
    # 0 00000000 000111110100000000 010 01
    # | |        |                  |   |
    # | |        |                  |   wFormatTag
    # | |        |                  nChannels
    # | |        nSamplesPerSec
    # | wBlockAlign
    # wBitsPerSample
    else:
        codec     = MiniFormatTag(format_data                      & ((1 << 2) - 1))
        channels  =              (format_data >>  2)               & ((1 << 3) - 1)
        rate      =              (format_data >> (2 + 3))          & ((1 << 18) - 1)
        alignment =              (format_data >> (2 + 3 + 18))     & ((1 << 8) - 1)

    return WaveFormat(codec=codec, channels=channels, rate=rate, alignment=alignment)
