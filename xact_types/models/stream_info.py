from typing import Annotated

from pydantic import NonNegativeInt

from xact_types.enums.mini_format_tag import MiniFormatTag
from xact_types.utils import StrictBaseModel


class StreamInfo(StrictBaseModel):
    format: int = 0
    file_offset: NonNegativeInt = 0
    file_length: NonNegativeInt = 0
    loop_start: int = 0
    loop_length: int = 0
    