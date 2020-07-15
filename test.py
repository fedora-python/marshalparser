from glob import glob
from pathlib import Path
from subprocess import check_call
import filecmp
import os
import sys

import pytest

from marshalparser.magic import get_pyc_python_version

PYTHON_VERSION = "{}.{}".format(*sys.version_info[:2])
PATH = Path("test") / "python_stdlib"
CMD = ["python" + PYTHON_VERSION, "-m", "marshalparser", "-f"]


def fixed_filename(original_filename):
    original_filename = Path(original_filename)
    return original_filename.with_suffix(".fixed" + original_filename.suffix)


@pytest.fixture(autouse=True)
def clean():
    # run test first
    yield
    for fixed_file in glob(str(PATH / "*" / "*.fixed.pyc")):
        os.unlink(fixed_file)


def generate_test_data():
    return glob(str(PATH / "*" / "*.pyc"))


test_data = generate_test_data()


@pytest.mark.parametrize("filename", test_data)
def test_complete(filename):
    # This command uses the Python we are testing with
    # because for example we can run marshalparser with
    # Python 3.9 and fix pyc file for Python 3.6
    check_call(CMD + [filename])

    assert os.path.isfile(fixed_filename(filename))

    if filecmp.cmp(filename, fixed_filename(filename), shallow=False):
        pytest.skip("Fixed file is the same as original, nothing to check")

    # To compare two pyc files, we need to use Python
    # they were compiled by
    python_version = get_pyc_python_version(filename)
    python_version_str = "{}.{}".format(*python_version)
    CHECK_CMD = [
        "python" + python_version_str, "marshal_content_check.py", filename,
        fixed_filename(filename)
    ]

    check_call(CHECK_CMD)


three_doubles = [test_data[i:i+2] for i in range(0, 6, 2)]


@pytest.mark.parametrize("filenames", three_doubles)
def test_run_with_more_than_one_file(filenames):
    check_call(CMD + [*filenames])
