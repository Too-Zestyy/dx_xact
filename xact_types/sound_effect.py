from pydantic import PositiveInt, NonNegativeInt

from xact_types.enums.mini_format_tag import MiniFormatTag
from xact_types.models.utils import StrictBaseModel
from xact_types.models.wave_bank_data import WaveBankFriendlyName


class SoundEffect(StrictBaseModel):
    codec: MiniFormatTag
    audio_data: bytes
    channels: PositiveInt
    sample_rate: PositiveInt
    block_alignment: PositiveInt

    loop_start: NonNegativeInt
    loop_length: NonNegativeInt

