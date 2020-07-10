from glob import glob
from pathlib import Path
from subprocess import check_call
import filecmp
import marshal
import os
import sys

import pytest

from marshalparser import PYC_HEADER_LEN

PYTHON_VERSION = "{}.{}".format(*sys.version_info[:2])
PATH = Path("test") / "python_stdlib" / PYTHON_VERSION
CMD = ["python" + PYTHON_VERSION, "marshalparser.py", "-f"]


def fixed_filename(original_filename):
    original_filename = Path(original_filename)
    return original_filename.with_suffix(".fixed" + original_filename.suffix)


@pytest.fixture(autouse=True)
def clean():
    # run test first
    yield
    for fixed_file in glob(str(PATH / "*.fixed.pyc")):
        print(f"Removing {fixed_file}")
        os.unlink(fixed_file)


def generate_test_data():
    return glob(str(PATH / "*.pyc"))


test_data = generate_test_data()


@pytest.mark.parametrize("filename", test_data)
def test_complete(filename):
    result = check_call(
        CMD + [filename]
    )

    assert result == 0
    assert os.path.isfile(fixed_filename(filename))

    if filecmp.cmp(filename, fixed_filename(filename), shallow=False):
        pytest.skip("Fixed file is the same as original, nothing to check")

    with open(filename, mode="rb") as fh:
        fh.seek(PYC_HEADER_LEN)
        original = marshal.load(fh)

    with open(fixed_filename(filename), mode="rb") as fh:
        fh.seek(PYC_HEADER_LEN)
        fixed = marshal.load(fh)

    assert original == fixed


three_doubles = [test_data[i:i+2] for i in range(0, 6, 2)]


@pytest.mark.parametrize("filenames", three_doubles)
def test_run_with_more_than_one_file(filenames):
    check_call(CMD + [*filenames])
