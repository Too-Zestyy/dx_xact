from copy import deepcopy

from typing_extensions import NamedTuple


class CrcAlgorithmArguments(NamedTuple):
    width: int
    poly: int
    remainder: int
    reflect_input_bytes: bool
    reflect_final_output: bool
    xor_final_output: int


CRC_16_B_ARGS = CrcAlgorithmArguments(
    width=16,
    poly=0x1021,
    remainder=0xFFFF,
    reflect_input_bytes=True,
    reflect_final_output=True,
    xor_final_output=0xFFFF
)


def reverse_number_bit_order(initial_value: int, num_bits: int):
    result = 0
    for i in range(num_bits):
        result <<= 1
        result |= initial_value & 1
        initial_value >>= 1
    return result


def calc_crc_per_bit(width: int, input: bytes, poly: int, remainder: int,
                     reflect_input_bytes: bool, reflect_final_output: bool, xor_final_output: int):
    # https://github.com/gchq/CyberChef/blob/master/src/core/operations/CRCChecksum.mjs#L787
    TOP_BIT = 1 << (width - 1)
    MASK = (1 << width) - 1

    for byte in input:
        if reflect_input_bytes:
            byte = reverse_number_bit_order(byte, 8)

        # Right shift can't be used in a for loop, so this is the closest equivalent
        i = 0x80
        while i:
            bit = remainder & TOP_BIT
            remainder = (remainder << 1) & MASK

            if (byte & i) != 0:
                bit ^= TOP_BIT
            if bit != 0:
                remainder ^= poly

            i >>= 1

    if reflect_final_output:
        remainder = reverse_number_bit_order(remainder, width)
    return remainder ^ xor_final_output


def calc_crc16b(input: bytes):
    return calc_crc_per_bit(
        width=CRC_16_B_ARGS.width,
        input=input,
        poly=CRC_16_B_ARGS.poly,
        remainder=CRC_16_B_ARGS.remainder,
        reflect_input_bytes=CRC_16_B_ARGS.reflect_input_bytes,
        reflect_final_output=CRC_16_B_ARGS.reflect_final_output,
        xor_final_output=CRC_16_B_ARGS.xor_final_output
    )


def calc_soundbank_crc(input: bytes) -> bytes:
    crc_16_b = calc_crc16b(input)
    little_endian_crc_bytes = crc_16_b.to_bytes(length=2, byteorder='little')
    return little_endian_crc_bytes
