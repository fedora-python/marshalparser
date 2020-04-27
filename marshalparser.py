from bits import testBit, clearBit, bytes_to_float, bytes_to_int
from collections import namedtuple
from dataclasses import dataclass
from sys import byteorder
from pathlib import Path
from object_types import types
import binascii
import sys

if sys.version_info >= (3, 7):
    PYC_HEADER_LEN = 16
elif sys.version_info >= (3, 3):
    PYC_HEADER_LEN = 12
else:
    PYC_HEADER_LEN = 8

# Flag_ref = namedtuple("Flag_ref", ["byte", "type", "content", "usages"])
Reference = namedtuple("Reference", ["byte", "index"])


@dataclass
class Flag_ref:
    byte: int
    type: str
    content: object
    usages: int = 0


class MarshalParser:
    def __init__(self, filename):
        self.filename = filename

        with open(filename, "rb") as fh:
            self.bytes = bytes(fh.read())
            iterator = enumerate(self.bytes)
            # skip pyc header (first n bytes)
            if filename.suffix == ".pyc":
                for x in range(PYC_HEADER_LEN):
                    next(iterator)

        self.iterator = iterator

    def parse(self):
        self.references = []  # references to existing objects with FLAG_REF
        self.flag_refs = []  # objects with FLAG_REF on
        self.output = ""
        self.indent = 0
        self.read_object()

    def record_object_start(self, i, b, ref_id):
        """
        Records human readable output of parsing process
        """
        byte = binascii.hexlify(b.to_bytes(1, byteorder))
        bytestring = b.to_bytes(1, byteorder)
        type = types[bytestring]
        ref = ""
        if ref_id is not None:
            ref = f"REF[{ref_id}]"
        line = f"n={i} byte=({byte}, {bytestring}, {bin(b)}) {type} {ref}\n"
        self.output += " " * self.indent + line

    def record_object_result(self, result):
        """
        Records the result of object parsing with its type
        """
        line = f"result={result}, type={type(result)}\n"
        self.output += " " * self.indent + line

    def record_object_info(self, info):
        """
        Records some info about parsed object
        """
        line = f"{info}\n"
        self.output += " " * self.indent + line

    def read_object(self):
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
            self.flag_refs.append(None)

        bytestring = b.to_bytes(1, byteorder)
        try:
            type = types[bytestring]
        except KeyError:
            print(f"Cannot read/parse byte {bytestring} on possition {i}")
            print("Might be error or unsupported TYPE")
            print(self.output)
            sys.exit(1)
        self.record_object_start(i, b, ref_id)

        # Increase indentation
        self.indent += 2

        if type == "TYPE_CODE":
            result = self.read_codeobject()

        elif type in ("TYPE_LONG", "TYPE_INT"):
            result = self.read_long()

        elif type == "TYPE_STRING":
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
        self.record_object_result(result)

        # Save the result to the self.references
        if ref_id is not None:
            self.flag_refs[ref_id] = Flag_ref(byte=i, type=type,
                                              content=result)

        return result

    def read_bytes(self, count=1):
        bytes = b""
        for x in range(count):
            index, byte = next(self.iterator)
            byte = byte.to_bytes(1, byteorder)
            bytes += byte
        return bytes

    def read_string(self, size=None, short=False):
        if size is None:
            if short:
                # short == size is stored as one byte
                size = bytes_to_int(self.read_bytes())
            else:
                # non-short == size is stored as long (4 bytes)
                size = self.read_long()
        bytes = self.read_bytes(size)
        return bytes

    def read_long(self):
        bytes = self.read_bytes(count=4)
        return bytes_to_int(bytes)

    def read_codeobject(self):
        argcount = self.read_long()
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

    def unused_ref_flags(self):
        unused = []
        for index, flag_ref in enumerate(self.flag_refs):
            if flag_ref.usages == 0:
                unused.append((index, flag_ref))
        return unused

    def clear_unused_ref_flags(self, overwrite=False):
        # List of flag_refs and references ordered by number of byte in a file
        final_list = self.flag_refs + self.references
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
                content[r.byte+1:r.byte+5] = new_index.to_bytes(4, byteorder)

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


def main():
    file = Path(sys.argv[1])

    parser = MarshalParser(file)
    parser.parse()
    print(parser.output)
    unused = parser.unused_ref_flags()
    if unused:
        print("Unused FLAG_REFs:")
        print("\n".join([f"{i} - {f}" for i, f in unused]))

    parser.clear_unused_ref_flags()


if __name__ == "__main__":
    main()
