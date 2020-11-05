import struct
from typing import Optional, Tuple

# Copied from CPython source code
# Lib/importlib/_bootstrap_external.py
MAGIC_NUMBERS = {
    3360: (3, 6),
    3361: (3, 6),
    3370: (3, 6),
    3371: (3, 6),
    3372: (3, 6),
    3373: (3, 6),
    3375: (3, 6),
    3376: (3, 6),
    3377: (3, 6),
    3378: (3, 6),
    3379: (3, 6),
    3390: (3, 7),
    3391: (3, 7),
    3392: (3, 7),
    3393: (3, 7),
    3394: (3, 7),
    3400: (3, 8),
    3401: (3, 8),
    3410: (3, 8),
    3411: (3, 8),
    3412: (3, 8),
    3413: (3, 8),
    3420: (3, 9),
    3421: (3, 9),
    3422: (3, 9),
    3423: (3, 9),
    3424: (3, 9),
    3425: (3, 9),
    3430: (3, 10),
}


def get_pyc_python_version(
    *, filename: str = None, bytes: bytes = None
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
    python_version = MAGIC_NUMBERS.get(magic_data[0], None)

    return python_version


def get_pyc_header_lenght(python_version: Tuple[int, int]) -> int:
    """Returns pyc header lenght (number of bytes) for Python version"""
    if python_version >= (3, 7):
        return 16
    elif python_version >= (3, 3):
        return 12
    else:
        return 8
