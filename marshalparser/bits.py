from sys import byteorder
import struct


def testBit(int_type, offset):
    """
    testBit() returns a nonzero result, 2**offset, if the bit at
    'offset' is one.
    """
    mask = 1 << offset
    return int_type & mask


def setBit(int_type, offset):
    """setBit() returns an integer with the bit at 'offset' set to 1."""
    mask = 1 << offset
    return int_type | mask


def clearBit(int_type, offset):
    """clearBit() returns an integer with the bit at 'offset' cleared."""
    mask = ~(1 << offset)
    return int_type & mask


def toggleBit(int_type, offset):
    """
    toggleBit() returns an integer with the bit at
    'offset' inverted, 0 -> 1 and 1 -> 0.
    """
    mask = 1 << offset
    return int_type ^ mask


def bytes_to_int(bytes, signed=False):
    return int.from_bytes(bytes, byteorder, signed=signed)


def bytes_to_float(bytes):
    return struct.unpack("d", bytes)[0]
