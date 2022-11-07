import struct
from functools import lru_cache
from typing import Optional, Tuple


def inclusive_range(f: int, t: int) -> range:
    """Returns range including both ends"""
    return range(f, t + 1)


# Based on CPython source code
# Lib/importlib/_bootstrap_external.py
MAGIC_NUMBERS_RANGES = (
    (inclusive_range(3360, 3361), (3, 6)),
    (inclusive_range(3370, 3379), (3, 6)),
    (inclusive_range(3390, 3394), (3, 7)),
    (inclusive_range(3400, 3401), (3, 8)),
    (inclusive_range(3410, 3413), (3, 8)),
    (inclusive_range(3420, 3425), (3, 9)),
    (inclusive_range(3430, 3439), (3, 10)),
    (inclusive_range(3450, 3495), (3, 11)),
    # This range has to be adjusted when the final release is out
    (inclusive_range(3500, 3549), (3, 12)),
)


@lru_cache()
def python_version_from_magic_number(number: int) -> Optional[Tuple[int, int]]:
    for numbers_range, version in MAGIC_NUMBERS_RANGES:
        if number in numbers_range:
            return version
    return None


def get_pyc_python_version(
    *, filename: Optional[str] = None, bytes: Optional[bytes] = None
) -> Optional[Tuple[int, int]]:
    """Get the version of Python from pyc header (magic number)
    or None if it cannot be detected. Takes a filename to read
    or first 4 bytes from it."""
    magic = None
    if filename:
        with open(filename, "rb") as file:
            magic = file.read(4)
    elif bytes:
        magic = bytes

    if not magic:
        raise RuntimeError("Either filename or bytes has to be specified!")

    magic_data = struct.unpack("<H2B", magic)
    python_version = python_version_from_magic_number(magic_data[0])

    return python_version


def get_pyc_header_lenght(python_version: Tuple[int, int]) -> int:
    """Returns pyc header lenght (number of bytes) for Python version"""
    if python_version >= (3, 7):
        return 16
    elif python_version >= (3, 3):
        return 12
    else:
        return 8
