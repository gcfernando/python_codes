# How to Create a Custom Exception in Python — Minimal Example

A minimal Python example demonstrating **how to define, raise, and catch a custom exception class** by subclassing `Exception`.

## Overview

This script shows the pattern for creating a user-defined exception in Python by subclassing the built-in `Exception` class. It demonstrates how to raise the custom exception under a specific condition and catch it with a `try/except` block.

## How It Works

1. `CustomException` is defined as a subclass of `Exception`, accepting a `message` parameter.
2. `some_function()` raises `CustomException` when a condition is met (`x < y`).
3. The exception is caught in a `try/except` block, and the message is printed.

## Code Example

```python
class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

def some_function():
    x = 5
    y = 6
    if x < y:
        raise CustomException("Something went wrong")

try:
    some_function()
except CustomException as e:
    print(e.message)
```

## Usage

From the `Console_Code` folder:

```bash
python CustomException.py
```

**Output** (confirmed by running the script):
```text
Something went wrong
```

## Notes

- No external dependencies required — uses only Python built-ins.
- The script includes a discussion in the docstring about when it is appropriate to make a custom exception serializable (relevant for distributed systems where exceptions may be passed across process boundaries).

## File Structure

```text
Custom Exception/
└── Console_Code/
    └── CustomException.py    # Main script
```

## FAQ

**Do I need to store `message` on the exception?**
No — `str(e)` already returns the message passed to `super().__init__(message)`. Storing it as `self.message` simply makes it available as a named attribute, which is handy when you add more fields (such as an error code).

**Should custom exceptions inherit from `Exception` or `BaseException`?**
From `Exception` (or one of its subclasses). `BaseException` is reserved for exceptions such as `KeyboardInterrupt` and `SystemExit` that ordinary `except Exception` blocks should not catch.

## Related Projects

- [Object Clone — deep copy example](../Object%20Clone/readme.md)
- [Python dbm database example](../Database/README.md)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
