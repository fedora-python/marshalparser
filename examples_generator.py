import marshal

data = {
    "integer": 42,
    "longs": (25487958525413698547, 1 << 64),
    "float": 42.88,
    "string": "hello world",
    "list_of_simple_objects": [True, False, None, ...],
    "set": set((9, 8, 7)),
    "tuple": (6, 5, 4),
    "dict": dict(a=1, b=2, c=3),
    "complex": complex(15, 2),
    "frozenset": frozenset((99, 999, 9999)),
    "nested_tuples": (),
}

for i in range(100):
    data['nested_tuples'] = (data['nested_tuples'], data['nested_tuples'])

for key, value in data.items():
    with open(f"test/pure_marshal/{key}.dat", mode="wb") as fh:
        marshal.dump(value, fh)
