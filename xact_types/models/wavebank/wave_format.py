from xact_types.enums.mini_format_tag import MiniFormatTag
from xact_types.models.utils import StrictBaseModel


class WaveFormat(StrictBaseModel):
    codec: MiniFormatTag
    channels: int
    rate: int
    alignment: int
    bits_per_sample: int
