from pathlib import Path

from pydantic import NonNegativeInt, PositiveInt

from xact_types.models.wave_bank_data import WaveBankData, WaveBankFriendlyName
from xact_types.utils import StrictBaseModel


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

    # TODO: Remove fields if left unused
    is_in_use: bool
    is_prepared: bool

    @classmethod
    def from_wavebank_file(cls, file_path: Path) -> 'WaveBank':
        ...
