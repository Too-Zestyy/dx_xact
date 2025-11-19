from typing import Annotated

from pydantic import NonNegativeInt, StringConstraints, PositiveInt

from xact_types.models.utils import StrictBaseModel

# TODO: Add more specific validation for wave bank names when documentation is found
#  - this pattern uses symbols and variations manually found to be valid via the XACT GUI, and *is not* exhaustive
WaveBankFriendlyName = Annotated[str, StringConstraints(pattern=r"^[a-zA-Z0-9-_!£$%&^@#()+\[\].,~'` ]+$",
                                                        min_length=1, max_length=63)]


class WaveBankData(StrictBaseModel):
    flags: int = 0
    entry_count: NonNegativeInt = 0
    bank_name: WaveBankFriendlyName = ''
    entry_metadata_element_size: NonNegativeInt = 0
    entry_name_element_size: NonNegativeInt = 0
    alignment: NonNegativeInt = 0
    compact_format: NonNegativeInt = 0
    build_time: NonNegativeInt = 0
