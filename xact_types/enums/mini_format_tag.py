from enum import IntEnum


class MiniFormatTag(IntEnum):
    Pcm = 0x0
    Xma = 0x1
    Adpcm = 0x2
    Wma = 0x3

    PlatformSpecific = Xma
