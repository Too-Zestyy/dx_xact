def calc_crc_per_bit(width: int, input: bytes, poly: int, remainder: int, reflectIn: bool, reflectOut: bool, xorOut: int):
    # https://github.com/gchq/CyberChef/blob/master/src/core/operations/CRCChecksum.mjs#L787
    TOP_BIT = 1 << (width - 1)
    MASK = (1 << width) - 1

    for byte in input:
        if reflectIn:
            ...


def calc_crc16b(input: bytes):
    return calc_crc_per_bit(16, input, 0x1021, 0xFFFF, True,  True,  0xFFFF)
