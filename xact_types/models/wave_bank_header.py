from pydantic import NonNegativeInt

from xact_types.models.segments import Segment
from xact_types.utils import StrictBaseModel


class WaveBankHeader(StrictBaseModel):
    version: NonNegativeInt = 0
    segments: tuple[Segment, Segment, Segment, Segment, Segment] = tuple(Segment(offset=0, length=0) for i in range(5))
