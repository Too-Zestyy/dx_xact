from typing import Annotated

from pydantic import NonNegativeInt

from xact_types.enums.mini_format_tag import MiniFormatTag
from xact_types.models.int_values import UInt32Value
from xact_types.models.utils import StrictBaseModel


class StreamInfo(StrictBaseModel):
    flags_and_duration: UInt32Value = 0

    format: UInt32Value = 0
    file_offset: UInt32Value = 0
    file_length: UInt32Value = 0
    loop_start: UInt32Value = 0
    loop_length: UInt32Value = 0
    