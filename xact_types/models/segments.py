from xact_types.utils import StrictBaseModel


class Segment(StrictBaseModel):
    offset: int
    length: int


class WaveBankHeader(StrictBaseModel):
    version: int
    segments: list[Segment]
