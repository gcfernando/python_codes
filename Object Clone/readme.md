# Deep Copy vs Shallow Copy in Python — copy.deepcopy() Example

A minimal example of **cloning a Python object with `copy.deepcopy()`**, showing that changes to the original do not affect the copy.

## Overview

This script illustrates the difference between a reference copy and a true deep copy of an object. It creates an instance of a custom class, clones it with `copy.deepcopy()`, modifies the original, and shows that the clone remains unchanged — confirming that the two objects are fully independent.

## How It Works

```python
import copy

class MyClass:
    def __init__(self, x):
        self.x = x

original_object = MyClass(10)
cloned_object = copy.deepcopy(original_object)

original_object.x = 20

print(original_object.x)   # 20
print(cloned_object.x)     # 10 — unchanged
```

`deepcopy` creates a new object with its own reference and recursively clones all attributes, so modifications to the original do not affect the clone.

## Requirements

No external dependencies. `copy` is part of the Python standard library.

## Usage

From the `Console_Code` folder:

```bash
python CloneObject.py
```

**Output:**
```
20
10
```

## File Structure

```
Object Clone/
└── Console_Code/
    └── CloneObject.py    # Main script
```

## Notes

- Use `copy.copy()` for a **shallow copy**, which only copies the top-level object (nested mutable objects are still shared).
- Use `copy.deepcopy()` for a **deep copy**, which recursively copies all nested objects — suitable when the object contains lists, dicts, or other mutable attributes.
- In this particular example, `x` is an integer (immutable), so `copy.copy()` would give the same result. The difference appears when an attribute is mutable — for example, if `x` were a list and you appended to `original_object.x`, a shallow copy would see the change and a deep copy would not.

## Related Projects

- [Custom Exception](../Custom%20Exception/readme.md)
- [Python dbm database example](../Database/README.md)
- [Python OOP and dunder methods guides](https://github.com/gcfernando/document)
- [Back to all Python projects](../README.md)
