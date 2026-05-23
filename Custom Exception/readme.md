# Custom Exception

A minimal Python example demonstrating how to define and raise a custom exception class.

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

```bash
python CustomException.py
```

**Output:**
```
Something went wrong
```

## Notes

- No external dependencies required — uses only Python built-ins.
- The script includes a discussion in the docstring about when it is appropriate to make a custom exception serializable (relevant for distributed systems where exceptions may be passed across process boundaries).

## File Structure

```
Custom Exception/
└── Console_Code/
    └── CustomException.py    # Main script
```
