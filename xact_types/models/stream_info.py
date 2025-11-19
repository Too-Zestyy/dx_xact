from typing import Annotated

from pydantic import NonNegativeInt

from xact_types.enums.mini_format_tag import MiniFormatTag
from xact_types.models.int_values import UInt32Value
from xact_types.models.utils import StrictBaseModel


class StreamInfo(StrictBaseModel):
    flags_and_duration: UInt32Value = 0

    format: UInt32Value = 0
    file_offset: NonNegativeInt = 0
    file_length: NonNegativeInt = 0
    loop_start: int = 0
    loop_length: int = 0
    