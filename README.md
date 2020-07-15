# Marshal parser

[`marshal`](https://docs.python.org/3/library/marshal.html)
is an internal Python object serialization which is internally used
for serialization of [code objects](https://docs.python.org/3/c-api/code.html) into `*.pyc` files.

In the foreseeable future, this kinda useless brain exercise should
help me to solve issues with non-reproducible `.pyc` files.

## Installation

Marshal parser is available on PyPI:

```
pip install marshalparser
```

and as a Fedora RPM package:

```
sudo dnf install python3-marshalparser
```

## Parser in action

### Printing parsed content in a human-readable way

The current version of parser creates a human-readable list of parsed objects
with info about bytes where objects start and about their content:

```
$ python3 -m marshalparser -p test/pure_marshal/list_of_simple_objects.dat
n=0/0x0 byte=(b'5b', b'[', 0b1011011) TYPE_LIST REF[0]
  tuple/list/set size: 4
  n=5/0x5 byte=(b'54', b'T', 0b1010100) TYPE_TRUE
  result=True, type=<class 'bool'>
  n=6/0x6 byte=(b'46', b'F', 0b1000110) TYPE_FALSE
  result=False, type=<class 'bool'>
  n=7/0x7 byte=(b'4e', b'N', 0b1001110) TYPE_NONE
  result=None, type=<class 'NoneType'>
  n=8/0x8 byte=(b'2e', b'.', 0b101110) TYPE_ELLIPSIS
  result=Ellipsis, type=<class 'ellipsis'>
result=[True, False, None, Ellipsis], type=<class 'list'>
```

The same for `.pyc` files but they are more complex as they contain code objects which are reported as dictionaries:

```
$ python3 -m marshalparser -p test/python_stdlib/3.9/doctest.cpython-39.opt-1.pyc | head -n 30
n=16/0x10 byte=(b'63', b'c', 0b1100011) TYPE_CODE REF[0]
  n=41/0x29 byte=(b'73', b's', 0b1110011) TYPE_STRING
  result=b'd\x00Z\x00d\x01Z\x01g\x00d\x02\xa2\x01Z\x02d\x03d\x04l\x03Z\x03d\x03d\x04l\x04Z\x04d\x03d\x04l\x05Z\x05d\x03d\x04l\x06Z\x06d\x03d\x04l\x07Z\x07d\x03d\x04l\x08Z\x08d\x03d\x04l\tZ\td\x03d\x04l\nZ\nd\x03d\x04l\x0bZ\x0bd\x03d\x04l\x0cZ\x0cd\x03d\x05l\rm\x0eZ\x0e\x01\x00d\x03d\x06l\x0fm\x10Z\x10\x01\x00e\x10d\x07d\x08\x83\x02Z\x11i\x00Z\x12d\td\n\x84\x00Z\x13e\x13d\x0b\x83\x01Z\x14e\x13d\x0c\x83\x01Z\x15e\x13d\r\x83\x01Z\x16e\x13d\x0e\x83\x01Z\x17e\x13d\x0f\x83\x01Z\x18e\x13d\x10\x83\x01Z\x19e\x14e\x15B\x00e\x16B\x00e\x17B\x00e\x18B\x00e\x19B\x00Z\x1ae\x13d\x11\x83\x01Z\x1be\x13d\x12\x83\x01Z\x1ce\x13d\x13\x83\x01Z\x1de\x13d\x14\x83\x01Z\x1ee\x13d\x15\x83\x01Z\x1fe\x1be\x1cB\x00e\x1dB\x00e\x1eB\x00e\x1fB\x00Z d\x16Z!d\x17Z"d\x18d\x19\x84\x00Z#drd\x1bd\x1c\x84\x01Z$d\x1dd\x1e\x84\x00Z%d\x1fd \x84\x00Z&dsd"d#\x84\x01Z\'d$d%\x84\x00Z(G\x00d&d\'\x84\x00d\'e\x0e\x83\x03Z)d(d)\x84\x00Z*d*d+\x84\x00Z+d,d-\x84\x00Z,G\x00d.d/\x84\x00d/e\x08j-\x83\x03Z.d0d1\x84\x00Z/G\x00d2d3\x84\x00d3\x83\x02Z0G\x00d4d5\x84\x00d5\x83\x02Z1G\x00d6d7\x84\x00d7\x83\x02Z2G\x00d8d9\x84\x00d9\x83\x02Z3G\x00d:d;\x84\x00d;\x83\x02Z4G\x00d<d=\x84\x00d=\x83\x02Z5G\x00d>d?\x84\x00d?e6\x83\x03Z7G\x00d@dA\x84\x00dAe6\x83\x03Z8G\x00dBdC\x84\x00dCe4\x83\x03Z9d\x04a:dtdFdG\x84\x01Z;dDd\x04d\x04d\x04d\x04dDd\x03d\x04dEe2\x83\x00d\x04f\x0bdHdI\x84\x01Z<dudKdL\x84\x01Z=d\x03a>dMdN\x84\x00Z?G\x00dOdP\x84\x00dPe\x0cj@\x83\x03ZAG\x00dQdR\x84\x00dReA\x83\x03ZBG\x00dSdT\x84\x00dTe\x0cjC\x83\x03ZDdvdUdV\x84\x01ZEG\x00dWdX\x84\x00dXeA\x83\x03ZFdDd\x04d\x04e2\x83\x00d\x04f\x05dYdZ\x84\x01ZGd[d\\\x84\x00ZHd]d^\x84\x00ZId_d`\x84\x00ZJdwdadb\x84\x01ZKdxdcdd\x84\x01ZLdydedf\x84\x01ZMG\x00dgdh\x84\x00dh\x83\x02ZNeNdidjdkdldmdn\x9c\x06ZOdodp\x84\x00ZPeQdqk\x02\x90\x03r2e\n\xa0ReP\x83\x00\xa1\x01\x01\x00d\x04S\x00', type=<class 'bytes'>
  n=868/0x364 byte=(b'29', b')', 0b101001) TYPE_SMALL_TUPLE
    Small tuple size: 122
    n=870/0x366 byte=(b'61', b'a', 0b1100001) TYPE_ASCII
    result=b'Module doctest -- a framework for running examples in docstrings.\n\nIn simplest use, end each module M to be tested with:\n\ndef _test():\n    import doctest\n    doctest.testmod()\n\nif __name__ == "__main__":\n    _test()\n\nThen running the module as a script will cause the examples in the\ndocstrings to get executed and verified:\n\npython M.py\n\nThis won\'t display anything unless an example fails, in which case the\nfailing example(s) and the cause(s) of the failure(s) are printed to stdout\n(why not stderr? because stderr is a lame hack <0.2 wink>), and the final\nline of output is "Test failed.".\n\nRun it with the -v switch instead:\n\npython M.py -v\n\nand a detailed report of all examples tried is printed to stdout, along\nwith assorted summaries at the end.\n\nYou can force verbose mode by passing "verbose=True" to testmod, or prohibit\nit by passing "verbose=False".  In either of those cases, sys.argv is not\nexamined by testmod.\n\nThere are a variety of other ways to run doctests, including integration\nwith the unittest framework, and support for running non-Python text\nfiles containing doctests.  There are also many ways to override parts\nof doctest\'s default behaviors.  See the Library Reference Manual for\ndetails.\n', type=<class 'bytes'>
    n=2096/0x830 byte=(b'7a', b'z', 0b1111010) TYPE_SHORT_ASCII
    result=b'reStructuredText en', type=<class 'bytes'>
    n=2117/0x845 byte=(b'29', b')', 0b101001) TYPE_SMALL_TUPLE
      … etc …
```

### Unused `FLAG_REF`s

New version of the parser can produce also a list of unused `FLAG_REF`s — objects with
enabled possibility to refference to them but with zero usage of that possibility.

We use the same example as before here so you can try to find the unused `FLAG_REF`
manually on the top of this page.

```
python3 -m marshalparser -u test/pure_marshal/list_of_simple_objects.dat
Unused FLAG_REFs:
0 - Flag_ref(byte=0, type='TYPE_LIST', content=[True, False, None, Ellipsis], usages=0)
```

If we can detect it, we can also fix it. With option `-f`, Marshal parser produces a new
file where all unused `FLAG_REF` are removed and all useful references recalculated.

```
# Fix it
$ python3 -m marshalparser -f test/pure_marshal/list_of_simple_objects.dat
# Check the fixed file
$ python3 -m marshalparser -u test/pure_marshal/list_of_simple_objects.fixed.dat
# Print it
$ python3 -m marshalparser -p test/pure_marshal/list_of_simple_objects.fixed.dat
n=0/0x0 byte=(b'5b', b'[', 0b1011011) TYPE_LIST
  tuple/list/set size: 4
  n=5/0x5 byte=(b'54', b'T', 0b1010100) TYPE_TRUE
  result=True, type=<class 'bool'>
  n=6/0x6 byte=(b'46', b'F', 0b1000110) TYPE_FALSE
  result=False, type=<class 'bool'>
  n=7/0x7 byte=(b'4e', b'N', 0b1001110) TYPE_NONE
  result=None, type=<class 'NoneType'>
  n=8/0x8 byte=(b'2e', b'.', 0b101110) TYPE_ELLIPSIS
  result=Ellipsis, type=<class 'ellipsis'>
result=[True, False, None, Ellipsis], type=<class 'list'>
```

It's also possible to overwrite the existing file with `-fo`.

## Tests

Tests use pytest and `/test/python_stdlib/3.X` cotains around hundred of random `pyc` files from Python standard library
(python3-libs or python36 etc.) RPM package in Fedora for each supported Python version.

Tests check that the parser is able to parse/fix a `pyc` file and then that the unmarshaled code object is the same
in both files (original and fixed).

Tests ensures that MarshalParser running (for example) with Python 3.9 is able to parse and fix pyc files for other supported
Python versions. But to check whether the original and fixed pyc files are the same, we need to run `marshal_content_check.py`
with the Python version the files were compiled by.

## Python support

The code is tested with Python 3.6+ and it's also able to fix pyc files produced by Python 3.6+.
Python 3.6 itself requires [`dataclasses`](https://pypi.org/project/dataclasses/).

## Supported object types

* ✓ TYPE_NULL (as a null operator for TYPE_DICT)
* ✓ TYPE_NONE
* ✓ TYPE_FALSE
* ✓ TYPE_TRUE
* ✓ TYPE_STOPITER
* ✓ TYPE_ELLIPSIS
* ✓ TYPE_INT
* ✘ TYPE_INT64 (is not generated anymore)
* ✘ TYPE_FLOAT (only in marshal version 1)
* ✓ TYPE_BINARY_FLOAT
* ✘ TYPE_COMPLEX (only in marshal version 1)
* ✓ TYPE_BINARY_COMPLEX
* ✓ TYPE_LONG (Parsed to digits but not reconstructed to PyLong)
* ✓ TYPE_STRING
* ✓ TYPE_INTERNED
* ✓ TYPE_REF
* ✓ TYPE_TUPLE
* ✓ TYPE_LIST
* ✓ TYPE_DICT
* ✓ TYPE_CODE
* ✓ TYPE_UNICODE
* ? TYPE_UNKNOWN (no idea how to test unknown bytes-like objects as a bytes object)
* ✓ TYPE_SET
* ✓ TYPE_FROZENSET
* ✓ FLAG_REF (recognized as a flag for all complex types)
* ✓ TYPE_ASCII
* ✓ TYPE_ASCII_INTERNED
* ✓ TYPE_SMALL_TUPLE
* ✓ TYPE_SHORT_ASCII
* ✓ TYPE_SHORT_ASCII_INTERNED

## References

* [distutils is not reproducible](https://bugs.python.org/issue34033)
* [python-3.6 packages do not build reproducibly](https://bugzilla.opensuse.org/show_bug.cgi?id=1049186)
* [PEP 552](https://www.python.org/dev/peps/pep-0552/)
