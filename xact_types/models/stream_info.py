from typing import Annotated

from pydantic import NonNegativeInt

from xact_types.utils import StrictBaseModel


class StreamInfo(StrictBaseModel):
    format: NonNegativeInt
    file_offset: NonNegativeInt
    file_length: NonNegativeInt
    loop_start: int
    loop_length: int
    