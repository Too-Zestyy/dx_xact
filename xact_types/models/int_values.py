from typing import Annotated

from pydantic import NonNegativeInt, conint, Field


def get_values_in_bits(bits):
    return 1 << bits


def get_unsigned_limit_values_for_bits(bits: int) -> tuple[int, int]:
    return 0, (1 << bits) - 1


def get_unsigned_limit_values_for_bytes(bytes: int) -> tuple[int, int]:
    return get_unsigned_limit_values_for_bits(bytes * 8)


def get_signed_limit_values_for_bits(bits: int) -> tuple[int, int]:
    if bits & 1 == 1:
        raise ValueError('Calculations only valid for even number of bits.')

    unsigned_limit_values = get_unsigned_limit_values_for_bits(bits)

    value_count = get_values_in_bits(bits)

    mid_value = value_count >> 1

    return unsigned_limit_values[0] - mid_value, unsigned_limit_values[1] - mid_value


def get_signed_limit_values_for_bytes(bytes: int):
    return get_signed_limit_values_for_bits(bytes * 8)


def get_signed_annotation(bits: int) -> type[Annotated[int, ...]]:
    limits = get_signed_limit_values_for_bits(bits)
    return Annotated[int, Field(ge=limits[0], le=limits[1])]


def get_unsigned_annotation(bits: int) -> type[Annotated[int, ...]]:
    return Annotated[int, Field(ge=0, le=get_unsigned_limit_values_for_bits(bits)[1])]


Int32Value = get_signed_annotation(32)
UInt32Value = get_unsigned_annotation(32)

