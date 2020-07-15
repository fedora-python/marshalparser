# Helper script for tests which compares content of two pyc files

import marshal
import sys

from marshalparser.magic import get_pyc_header_lenght

original_filename = sys.argv[1]
fixed_filename = sys.argv[2]

PYC = original_filename.endswith(".pyc")

if PYC:
    pyc_header_len = get_pyc_header_lenght(sys.version_info[:2])

with open(sys.argv[1], mode="rb") as fh:
    if PYC:
        fh.seek(pyc_header_len)
    original = marshal.load(fh)

with open(sys.argv[2], mode="rb") as fh:
    if PYC:
        fh.seek(pyc_header_len)
    fixed = marshal.load(fh)

assert original == fixed
