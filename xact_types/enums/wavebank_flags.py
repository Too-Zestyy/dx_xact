from enum import IntEnum


class WaveBankFlags(IntEnum):
    entry_names_included = 0x00010000
    compact_format = 0x00020000
    disabled_audition_sync = 0x00040000
    includes_sync_tables = 0x00080000
    flag_mask = 0x000F0000
