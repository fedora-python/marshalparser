# Marshal parser

[`marshal`](https://docs.python.org/3/library/marshal.html)
is an internal Python object serialization which is internally used
for serialization of [code objects](https://docs.python.org/3/c-api/code.html) into `*.pyc` files.

In the foreseeable future, this kinda useless brain exercise should
help me to solve issues with non-reproducible `.pyc` files.

## Parser in action

The current version of parser creates a human-readable list of parsed objects
with info about bytes where objects start and about their content:

```
$ python3.8 marshalparser.py test/data/list_of_simple_objects.dat
n=0 byte=(b'5b', b'[', 0b1011011) TYPE_LIST REF[0]
  tuple/list/set size: 4
  n=5 byte=(b'54', b'T', 0b1010100) TYPE_TRUE
  result=True, type=<class 'bool'>
  n=6 byte=(b'46', b'F', 0b1000110) TYPE_FALSE
  result=False, type=<class 'bool'>
  n=7 byte=(b'4e', b'N', 0b1001110) TYPE_NONE
  result=None, type=<class 'NoneType'>
  n=8 byte=(b'2e', b'.', 0b101110) TYPE_ELLIPSIS
  result=Ellipsis, type=<class 'ellipsis'>
result=[True, False, None, Ellipsis], type=<class 'list'>
```

The same for `.pyc` files but they are more complex as they contain code objects which are reported as dictionaries:

```
$ cd test/python && python3.8 -c "import test_module" && cd ../..
$ python3.8 marshalparser.py test/python/__pycache__/test_module.cpython-38.pyc
n=16 byte=(b'63', b'c', 0b1100011) TYPE_CODE REF[0]
  n=41 byte=(b'73', b's', 0b1110011) TYPE_STRING
  result=b'd\x00d\x01\x84\x00Z\x00e\x01e\x00\x83\x00\x83\x01\x01\x00e\x00\x83\x00\\\x02Z\x02Z\x03e\x02e\x03f\x02\x01\x00e\x02e\x03g\x02\x01\x00e\x02e\x03i\x01\x01\x00d\x02S\x00', type=<class 'bytes'>
  n=102 byte=(b'29', b')', 0b101001) TYPE_SMALL_TUPLE
    Small tuple size: 3
    n=104 byte=(b'63', b'c', 0b1100011) TYPE_CODE
      n=129 byte=(b'73', b's', 0b1110011) TYPE_STRING
      result=b'd\x01}\x00d\x02}\x01|\x00|\x01f\x02S\x00', type=<class 'bytes'>
      n=150 byte=(b'29', b')', 0b101001) TYPE_SMALL_TUPLE
        Small tuple size: 3
        n=152 byte=(b'4e', b'N', 0b1001110) TYPE_NONE
        result=None, type=<class 'NoneType'>
        n=153 byte=(b'69', b'i', 0b1101001) TYPE_INT REF[1]
        result=42, type=<class 'int'>
        n=158 byte=(b'67', b'g', 0b1100111) TYPE_BINARY_FLOAT
        result=42.8, type=<class 'float'>
      result=(None, 42, 42.8), type=<class 'tuple'>
      n=167 byte=(b'29', b')', 0b101001) TYPE_SMALL_TUPLE REF[2]
        Small tuple size: 0
      result=(), type=<class 'tuple'>
      … etc …
```

### Unused `FLAG_REF`s

New version of the parser produces also a list of unused `FLAG_REF`s — objects with
enabled possibility to refference to them but with zero usage of that possibility.

```
Unused FLAG_REFs:
0 - Flag_ref(byte=16, type='TYPE_CODE', content={'argcount': 0, 'posonlyargcount': 0, 'kwonlyargcount': 0, 'nlocals': 0, 'stacksize': 2, 'flags': 64, 'code': b'd\x00d\x01\x84\x00Z\x00e\x01e\x00\x83\x00\x83\x01\x01\x00e\x00\x83\x00\\\x02Z\x02Z\x03e\x02e\x03f\x02\x01\x00e\x02e\x03g\x02\x01\x00e\x02e\x03i\x01\x01\x00d\x02S\x00', 'consts': ({'argcount': 0, 'posonlyargcount': 0, 'kwonlyargcount': 0, 'nlocals': 2, 'stacksize': 2, 'flags': 67, 'code': b'd\x01}\x00d\x02}\x01|\x00|\x01f\x02S\x00', 'consts': (None, 42, 42.8), 'names': (), 'varnames': (b'a', b'b'), 'freevars': "REF to 2: Flag_ref(byte=167, type='TYPE_SMALL_TUPLE', content=(), usages=1)", 'cellvars': "REF to 2: Flag_ref(byte=167, type='TYPE_SMALL_TUPLE', content=(), usages=2)", 'filename': b'/home/lbalhar/Dropbox/Projekty/marshal_parser/test/python/test_module.py', 'name': b'funkce', 'firstlineno': 1, 'lnotab': b'\x00\x01\x04\x01\x04\x01'}, "REF to 6: Flag_ref(byte=261, type='TYPE_SHORT_ASCII_INTERNED', content=b'funkce', usages=1)", None), 'names': ("REF to 6: Flag_ref(byte=261, type='TYPE_SHORT_ASCII_INTERNED', content=b'funkce', usages=2)", b'print', "REF to 3: Flag_ref(byte=171, type='TYPE_SHORT_ASCII_INTERNED', content=b'a', usages=1)", "REF to 4: Flag_ref(byte=174, type='TYPE_SHORT_ASCII_INTERNED', content=b'b', usages=1)"), 'varnames': "REF to 2: Flag_ref(byte=167, type='TYPE_SMALL_TUPLE', content=(), usages=3)", 'freevars': "REF to 2: Flag_ref(byte=167, type='TYPE_SMALL_TUPLE', content=(), usages=4)", 'cellvars': "REF to 2: Flag_ref(byte=167, type='TYPE_SMALL_TUPLE', content=(), usages=5)", 'filename': "REF to 5: Flag_ref(byte=187, type='TYPE_SHORT_ASCII', content=b'/home/lbalhar/Dropbox/Projekty/marshal_parser/test/python/test_module.py', usages=1)", 'name': b'<module>', 'firstlineno': 1, 'lnotab': b'\x08\x06\n\x02\n\x02\x08\x01\x08\x01'}, usages=0)
1 - Flag_ref(byte=153, type='TYPE_INT', content=42, usages=0)
7 - Flag_ref(byte=297, type='TYPE_SHORT_ASCII_INTERNED', content=b'print', usages=0)
8 - Flag_ref(byte=334, type='TYPE_SHORT_ASCII_INTERNED', content=b'<module>', usages=0)
```

### Fixed `.pyc` file

If there is at least one unused `FLAG_REF` a new `.pyc` file is produces where this is disabled and all references
are recalculated.

```
$ cd test/python && python3.8 -c "import test_module" && cd ../..
$ python3.8 marshalparser.py test/python/__pycache__/test_module.cpython-38.pyc
$ python3.8 marshalparser.py test/python/__pycache__/test_module.cpython-38.fixed.pyc
…
Content is the same, nothing to fix…
```

## Python support

The code works with Python 3.8 but it should be easy to adjust it for Python 3.7. The only difference are
position-only arguments in code objects since Python 3.8.

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
* ✓ TYPE_LONG
* ✓ TYPE_STRING
* ? TYPE_INTERNED (no idea where it is and how to test it)
* ✓ TYPE_REF
* ✓ TYPE_TUPLE
* ✓ TYPE_LIST
* ✓ TYPE_DICT
* ✓ TYPE_CODE
* ? TYPE_UNICODE (only in marshal version < 3)
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
