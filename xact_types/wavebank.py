import struct
from pathlib import Path
from typing import BinaryIO

from pydantic import NonNegativeInt, PositiveInt

from xact_types.enums.wavebank_flags import WaveBankFlags
from xact_types.models.segments import Segment
from xact_types.models.wave_bank_data import WaveBankData, WaveBankFriendlyName
from xact_types.models.wave_bank_header import WaveBankHeader
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
    sounds: list
    streams: list

    bank_name: WaveBankFriendlyName
    file_name: str
    streaming: bool
    offset: NonNegativeInt
    packet_size: PositiveInt

    version: PositiveInt
    play_region_offset: NonNegativeInt

    header: WaveBankHeader
    data: WaveBankData

    # TODO: Remove fields if left unused
    is_in_use: bool
    is_prepared: bool

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
                wavebank_offset = xwb_header.segments[1].offset

            if xwb_data.flags & WaveBankFlags.compact_format == 0:
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

            # TODO: At line 188, continue translation and add classes as necessary (SoundEffect)

            # TODO: Return filled WaveBank once file is read
