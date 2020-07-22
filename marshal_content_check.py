# Helper script for tests which compares content of two pyc files

import marshal
import sys

from marshalparser.magic import get_pyc_header_lenght

PYC = bool(int(sys.argv[1]))
original_filename = sys.argv[2]
fixed_filename = sys.argv[3]

if PYC:
    pyc_header_len = get_pyc_header_lenght(sys.version_info[:2])

with open(original_filename, mode="rb") as fh:
    if PYC:
        fh.seek(pyc_header_len)
    original = marshal.load(fh)

with open(fixed_filename, mode="rb") as fh:
    if PYC:
        fh.seek(pyc_header_len)
    fixed = marshal.load(fh)

assert original == fixed
