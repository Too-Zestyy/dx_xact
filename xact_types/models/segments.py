from pydantic import NonNegativeInt

from xact_types.utils import StrictBaseModel


class Segment(StrictBaseModel):
    offset: NonNegativeInt
    length: NonNegativeInt
