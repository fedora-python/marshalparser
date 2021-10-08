from glob import glob
from pathlib import Path
from subprocess import check_call, check_output
import filecmp
import os
import sys

import pytest

from marshalparser.magic import get_pyc_python_version

PYTHON_VERSION = "{}.{}".format(*sys.version_info[:2])
CMD = ["python" + PYTHON_VERSION, "-m", "marshalparser", "-f"]


def fixed_filename(original_filename):
    original_filename = Path(original_filename)
    return original_filename.with_suffix(".fixed" + original_filename.suffix)


@pytest.fixture(autouse=True)
def clean():
    # run test first
    yield
    for fixed_file in glob(
        str(Path("test") / "**" / "*.fixed.*"), recursive=True
    ):
        os.unlink(fixed_file)


def generate_test_data():
    python_stdlib = glob(str(Path("test") / "python_stdlib" / "*" / "*.pyc"))
    pure_marshal = glob(str(Path("test") / "pure_marshal" / "*"))
    renamed_pycs = glob(str(Path("test") / "renamed_pycs" / "*"))
    return pure_marshal + renamed_pycs + python_stdlib


test_data = generate_test_data()


@pytest.mark.parametrize("filename", test_data)
def test_complete(filename):
    # This command uses the Python we are testing with
    # because for example we can run marshalparser with
    # Python 3.9 and fix pyc file for Python 3.6
    output = check_output(CMD + [filename], encoding="utf-8")

    assert os.path.isfile(fixed_filename(filename))

    if filecmp.cmp(filename, fixed_filename(filename), shallow=False):
        pytest.skip("Fixed file is the same as original, nothing to check")

    assert output.endswith(
        f" unused FLAG_REFs from {fixed_filename(filename)}\n"
    )
    assert output[:8] == "Removed "

    # To compare two pyc files, we need to use Python
    # they were compiled by
    python_version = get_pyc_python_version(filename=filename)
    if python_version:
        python_version_str = "{}.{}".format(*python_version)
        # pass this to marshal_content_check.py so we don't have to
        # check the header there again
        check_pyc = True
    else:
        # For non-pyc files, we use the current Python for content check
        python_version_str = PYTHON_VERSION
        check_pyc = False

    CHECK_CMD = [
        "python" + python_version_str,
        "marshal_content_check.py",
        str(int(check_pyc)),
        filename,
        fixed_filename(filename),
    ]

    try:
        check_call(CHECK_CMD)
    except FileNotFoundError:
        pytest.skip(
            f"python{python_version_str} not found! Cannot check the result."
        )

    # Fixing the already fixed file should make no changes
    again_output = check_output(
        CMD + ["-o", fixed_filename(filename)], encoding="utf-8"
    )
    assert (
        again_output == f"No unused FLAG_REFs in {fixed_filename(filename)}\n"
    )


three_doubles = [test_data[i : i + 2] for i in range(0, 6, 2)]


@pytest.mark.parametrize("filenames", three_doubles)
def test_run_with_more_than_one_file(filenames):
    check_call(CMD + [*filenames])
