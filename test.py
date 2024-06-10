import filecmp
import os
import sys
from pathlib import Path
from subprocess import STDOUT, CalledProcessError, check_call, check_output

import pytest

from marshalparser.magic import get_pyc_python_version

PYTHON_VERSION = "{}.{}".format(*sys.version_info[:2])
CMD = ["python" + PYTHON_VERSION, "-m", "marshalparser", "-f"]


def fixed_filename(original_filename):
    original_filename = Path(original_filename)
    return original_filename.with_suffix(".fixed" + original_filename.suffix)


def param(p, *, skip_reason=None):
    """Return a pytest.param with stringified id, for nicer verbose output

    When skip_reson is set, the pytest.param will be marked as skipped."""
    if skip_reason is None:
        return pytest.param(p, id=str(p))
    return pytest.param(
        p, id=str(p), marks=[pytest.mark.skip(reason=skip_reason)]
    )


def generate_test_data():
    for python_version_dir in (Path("test") / "python_stdlib").glob("*"):
        python_version = python_version_dir.name
        try:
            check_call(("python" + python_version, "-c", "pass"))
        except FileNotFoundError:
            skip_reason = f"python{python_version} not found"
        else:
            skip_reason = None
        yield from (
            param(p, skip_reason=skip_reason)
            for p in python_version_dir.glob("*.pyc")
        )
    yield from (param(p) for p in (Path("test") / "pure_marshal").glob("*"))
    yield from (param(p) for p in (Path("test") / "renamed_pycs").glob("*"))


@pytest.mark.parametrize("original_filename", generate_test_data())
def test_complete(original_filename, tmp_path):
    # To be able to run tests in parallel, we create
    # a symlink for each test file so the fixed file appears
    # next to the symlink in the temp dir instead of the
    # test folder next to the original files.
    filename = tmp_path / original_filename.name
    filename.symlink_to(original_filename.absolute())

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
        # this could still happen with test/renamed_pycs
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


test_files = sorted((Path("test") / "renamed_pycs").glob("*"))
three_doubles = [(test_files[n], test_files[n + 1]) for n in range(0, 6, 2)]


@pytest.mark.parametrize("original_filenames", three_doubles)
def test_run_with_more_than_one_file(original_filenames, tmp_path):
    filenames = []
    for original_filename in original_filenames:
        filename = tmp_path / original_filename.name
        filename.symlink_to(original_filename.absolute())
        filenames.append(filename)
    check_call(CMD + [*filenames])


def test_empty_file(tmp_path):
    filename = tmp_path / "empty_file.pyc"
    filename.touch()
    with pytest.raises(CalledProcessError) as e:
        check_output(CMD + [filename], encoding="utf-8", stderr=STDOUT)
    assert e.value.returncode == 1
    assert f"File {filename} is empty!" in e.value.output
