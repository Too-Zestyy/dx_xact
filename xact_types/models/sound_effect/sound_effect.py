from pydantic import PositiveInt

from xact_types.enums.mini_format_tag import MiniFormatTag
from xact_types.models.int_values import UInt32Value
from xact_types.models.utils import StrictBaseModel


class SoundEffect(StrictBaseModel):
    codec: MiniFormatTag
    audio_data: bytes
    channels: PositiveInt
    sample_rate: PositiveInt
    block_alignment: PositiveInt

    loop_start: UInt32Value
    loop_length: UInt32Value

