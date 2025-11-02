from typing import Annotated

from pydantic import NonNegativeInt, StringConstraints, PositiveInt

from xact_types.utils import StrictBaseModel

# TODO: Add more specific validation for wave bank names when documentation is found
#  - this pattern uses symbols and variations manually found to be valid via the XACT GUI, and *is not* exhaustive
WaveBankFriendlyName = Annotated[str, StringConstraints(pattern=r"^[a-zA-Z0-9-_!£$%&^@#()+\[\].,~'`]+$",
                                                        min_length=1, max_length=63)]


class WaveBankData(StrictBaseModel):
    flags: int
    entry_count: NonNegativeInt
    bank_name: WaveBankFriendlyName
    entry_metadata_element_size: NonNegativeInt
    entry_name_element_size: NonNegativeInt
    alignment: PositiveInt
    compact_format: PositiveInt
    build_time: PositiveInt
