from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import argparse
import binascii
import sys

from .bits import testBit, clearBit, bytes_to_float, bytes_to_int
from .magic import get_pyc_python_version, get_pyc_header_lenght
from .object_types import types

PyLong_MARSHAL_SHIFT = 15

DEBUG = False

# Flag_ref = namedtuple("Flag_ref", ["byte", "type", "content", "usages"])
Reference = namedtuple("Reference", ["byte", "index"])


@dataclass
class Flag_ref:
    byte: int
    type: str
    content: object
    usages: int = 0


class MarshalParser:
    def __init__(self, filename: Path):
        self.filename = filename

        with open(filename, "rb") as fh:
            self.bytes = bytes(fh.read())
            iterator = enumerate(self.bytes)
        # if pyc magic number is detected, skip entire
        # pyc header (first n bytes)
        self.python_version = get_pyc_python_version(bytes=self.bytes[:4])
        if self.python_version:
            pyc_header_len = get_pyc_header_lenght(self.python_version)
            for x in range(pyc_header_len):
                next(iterator)
        else:
            # Not a pyc file, parse it as a marshal dump without header
            if DEBUG:
                print(
                    "File has no or unknown pyc header, "
                    "assuming a marshal dump…"
                )

        self.iterator = iterator

    def parse(self) -> None:
        self.references: List[
            Reference
        ] = []  # references to existing objects with FLAG_REF
        self.flag_refs: List[Flag_ref] = []  # objects with FLAG_REF on
        self.output = ""
        self.indent = 0
        self.read_object()

    def record_object_start(
        self, i: int, b: int, ref_id: Optional[int]
    ) -> None:
        """
        Records human readable output of parsing process
        """
        byte = binascii.hexlify(b.to_bytes(1, "little"))
        bytestring = b.to_bytes(1, "little")
        type = types[bytestring]
        ref = ""
        if ref_id is not None:
            ref = f"REF[{ref_id}]"
        line = (
            f"n={i}/{hex(i)} byte=({byte!r}, {bytestring!r}, "
            f"{bin(b)}) {type} {ref}\n"
        )
        if DEBUG:
            print(line)
        self.output += " " * self.indent + line

    def record_object_result(self, result: Any) -> None:
        """
        Records the result of object parsing with its type
        """
        line = f"result={result}, type={type(result)}\n"
        self.output += " " * self.indent + line

    def record_object_info(self, info: str) -> None:
        """
        Records some info about parsed object
        """
        line = f"{info}\n"
        self.output += " " * self.indent + line

    def read_object(self) -> Any:
        """
        Main method for reading/parsing objects and recording references.
        Simple objects are parsed directly, complex uses other read_* methods
        """
        i, b = next(self.iterator)
        ref_id = None
        if testBit(b, 7):
            b = clearBit(b, 7)
            # Save a slot in global references
            ref_id = len(self.flag_refs)
            self.flag_refs.append(None)  # type: ignore

        bytestring = b.to_bytes(1, "little")
        try:
            type = types[bytestring]
        except KeyError:
            print(
                f"Cannot read/parse byte {b!r} {bytestring!r} on possition {i}"
            )
            print("Might be error or unsupported TYPE")
            print(self.output)
            sys.exit(1)
        self.record_object_start(i, b, ref_id)

        # Increase indentation
        self.indent += 2

        result: Any

        if type == "TYPE_CODE":
            result = self.read_codeobject()

        elif type == "TYPE_LONG":
            result = self.read_py_long()

        elif type in ("TYPE_INT"):
            result = self.read_long()

        elif type in (
            "TYPE_STRING",
            "TYPE_UNICODE",
            "TYPE_ASCII",
            "TYPE_INTERNED",
            "TYPE_ASCII_INTERNED",
        ):
            result = self.read_string()

        elif type == "TYPE_SMALL_TUPLE":
            # small tuple — size is only one byte
            size = bytes_to_int(self.read_bytes())
            self.record_object_info(f"Small tuple size: {size}")
            result = []
            for x in range(size):
                result.append(self.read_object())
            result = tuple(result)

        elif type in ("TYPE_TUPLE", "TYPE_LIST", "TYPE_SET", "TYPE_FROZENSET"):
            # regular tuple, list, set, frozenset
            size = self.read_long()
            self.record_object_info(f"tuple/list/set size: {size}")
            result = []
            for x in range(size):
                result.append(self.read_object())
            if type == "TYPE_TUPLE":
                result = tuple(result)
            elif type == "TYPE_SET":
                result = set(result)
            elif type == "TYPE_FROZENSET":
                result = frozenset(result)

        elif type == "TYPE_NULL":
            result = "null"

        elif type == "TYPE_NONE":
            result = None

        elif type == "TYPE_TRUE":
            result = True

        elif type == "TYPE_FALSE":
            result = False

        elif type == "TYPE_STOPITER":
            result = StopIteration

        elif type == "TYPE_ELLIPSIS":
            result = ...

        elif type in ("TYPE_SHORT_ASCII_INTERNED", "TYPE_SHORT_ASCII"):
            result = self.read_string(short=True)

        elif type == "TYPE_REF":
            index = self.read_long()
            self.references.append(Reference(byte=i, index=index))
            self.flag_refs[index].usages += 1
            result = f"REF to {index}: " + str(self.flag_refs[index])

        elif type == "TYPE_BINARY_FLOAT":
            result = bytes_to_float(self.read_bytes(count=8))

        elif type == "TYPE_BINARY_COMPLEX":
            real = bytes_to_float(self.read_bytes(count=8))
            imag = bytes_to_float(self.read_bytes(count=8))
            result = complex(real, imag)

        elif type == "TYPE_DICT":
            result = {}
            while True:
                key = self.read_object()
                if key == "null":
                    break
                value = self.read_object()
                result[key] = value

        # decrease indentation
        self.indent -= 2
        try:
            self.record_object_result(result)
        except UnboundLocalError:
            message = f"type [{type}] is recognized but result is not present."
            if not self.python_version:
                message += (
                    "\nThe error is probably caused by an unknown "
                    "Python version (magic number) if it's a pyc file."
                )
            raise RuntimeError(message) from None

        # Save the result to the self.references
        if ref_id is not None:
            self.flag_refs[ref_id] = Flag_ref(
                byte=i, type=type, content=result
            )

        return result

    def read_bytes(self, count: int = 1) -> bytes:
        bytes = b""
        for x in range(count):
            index, int_byte = next(self.iterator)
            byte = int_byte.to_bytes(1, "little")
            bytes += byte
        return bytes

    def read_string(self, size: int = None, short: bool = False) -> bytes:
        if size is None:
            if short:
                # short == size is stored as one byte
                size = bytes_to_int(self.read_bytes())
            else:
                # non-short == size is stored as long (4 bytes)
                size = self.read_long()
        bytes = self.read_bytes(size)
        return bytes

    def read_long(self, signed: bool = False) -> int:
        bytes = self.read_bytes(count=4)
        return bytes_to_int(bytes, signed=signed)

    def read_short(self) -> int:
        b = self.read_bytes(count=2)
        x = b[0]
        x |= b[1] << 8
        # Sign-extension, in case short greater than 16 bits
        x |= -(x & 0x8000)
        return x

    def read_py_long(self) -> int:
        n = self.read_long(signed=True)
        result, shift = 0, 0
        for i in range(abs(n)):
            result += self.read_short() << shift
            shift += PyLong_MARSHAL_SHIFT

        return result if n > 0 else -result

    def read_codeobject(self) -> Dict[str, Any]:
        argcount = self.read_long()
        if self.python_version is not None and self.python_version >= (3, 8):
            posonlyargcount = self.read_long()
        kwonlyargcount = self.read_long()
        nlocals = self.read_long()
        stacksize = self.read_long()
        flags = self.read_long()
        code = self.read_object()
        consts = self.read_object()
        names = self.read_object()
        varnames = self.read_object()
        freevars = self.read_object()
        cellvars = self.read_object()
        filename = self.read_object()
        name = self.read_object()
        firstlineno = self.read_long()
        lnotab = self.read_object()

        co = dict(locals())
        del co["self"]  # removed Marshalparser instance from co

        return co

    def unused_ref_flags(self) -> List[Tuple[int, Flag_ref]]:
        unused = []
        for index, flag_ref in enumerate(self.flag_refs):
            if flag_ref.usages == 0:
                unused.append((index, flag_ref))
        return unused

    def clear_unused_ref_flags(self, overwrite: bool = False) -> None:
        # List of flag_refs and references ordered by number of byte in a file
        final_list = self.flag_refs + self.references  # type: ignore
        final_list.sort(key=lambda x: x.byte)
        # a map where at a beginning, index in list == number of flag_ref
        # but when unused flag is removed:
        # - numbers in the list are original numbers of flag_refs
        # - indexes of the list are new numbers
        flag_ref_map = list(range(len(self.flag_refs)))
        # new mutable content
        content = bytearray(self.bytes)

        for r in final_list:
            if isinstance(r, Flag_ref) and r.usages == 0:
                # Clear FLAG_REF bit and remove it from map
                # all subsequent refs will have lower index in the map
                flag_ref_map.remove(self.flag_refs.index(r))
                content[r.byte] = clearBit(content[r.byte], 7)
            elif isinstance(r, Reference):
                # Find a new index of flag_ref after some was removed
                new_index = flag_ref_map.index(r.index)
                # write new number as 4-byte integer
                content[r.byte + 1 : r.byte + 5] = new_index.to_bytes(
                    4, "little"
                )

        # Skip writing if there is no difference
        if bytes(content) != self.bytes:
            if overwrite:
                suffix = ""
            else:
                suffix = ".fixed"

            new_name = self.filename.with_suffix(suffix + self.filename.suffix)

            with open(new_name, mode="wb") as fh:
                fh.write(content)
        else:
            print("Content is the same, nothing to fix…")


def main() -> None:
    arg_parser = argparse.ArgumentParser(
        description="Marshalparser and fixer for .pyc files"
    )
    arg_parser.add_argument(
        "-p",
        "--print",
        action="store_true",
        dest="print",
        default=False,
        help="Print human-readable parser output",
    )
    arg_parser.add_argument(
        "-u",
        "--unused",
        action="store_true",
        dest="unused",
        default=False,
        help="Print unused references",
    )
    arg_parser.add_argument(
        "-f",
        "--fix",
        action="store_true",
        dest="fix",
        default=False,
        help="Fix references",
    )
    arg_parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        dest="overwrite",
        default=False,
        help="Overwrite existing pyc file (works with --fix)",
    )
    arg_parser.add_argument(metavar="files", dest="files", nargs="*")

    args = arg_parser.parse_args()

    for file in args.files:
        parser = MarshalParser(Path(file))
        parser.parse()
        if args.print:
            print(parser.output)
        if args.unused:
            unused = parser.unused_ref_flags()
            if unused:
                print("Unused FLAG_REFs:")
                print("\n".join([f"{i} - {f}" for i, f in unused]))

        if args.fix:
            parser.clear_unused_ref_flags(overwrite=args.overwrite)


if __name__ == "__main__":
    main()
