# Python dbm Example — Simple Key-Value Database with the Standard Library

A simple example of **key-value data persistence** using Python's built-in **`dbm` module**: store a small record in a file-based database and read it back, with no database server and no third-party packages.

## Overview

This script demonstrates how to store and retrieve structured data using Python's `dbm` module — a lightweight, file-based key-value store that requires no external database server. It saves a set of user details to a database file, then reads them back and formats a summary.

`dbm` is a good fit for small caches, settings, or lookup tables where a full database such as SQLite would be more than you need. For queryable relational data, see the SQLite-backed [Bookmark](../Bookmark/readme.md) project instead.

## Features

- Stores key-value pairs in a file-based database using `dbm`
- Reads back and decodes stored data from the database
- No external libraries or server setup required

## Requirements

No external dependencies. `dbm` is part of the Python standard library.

## Usage

```bash
cd DatabaseManager/Console_Code
python data_manager.py
```

The intended output is:

```
Hi, I am Gehan Fernando. I live in Sri Lanka, and I am 43 years old.
```

Database files named after `user.db` are created in the working directory. Their exact names depend on the platform's `dbm` backend — for example, the pure-Python `dbm.dumb` fallback creates `user.db.dat`, `user.db.dir`, and `user.db.bak`.

## Known issue

As currently written, the script raises `KeyError: 'first_name'` when it reaches the print step. `dbm` returns **keys** as bytes as well as values, and `load_user_data()` decodes only the values, so the returned dictionary has keys such as `b'first_name'` rather than `'first_name'`. Decoding the keys too — `{key.decode(): db[key].decode() for key in db.keys()}` — produces the intended output.

## How It Works

1. A dictionary of user data (first name, last name, age, country) is defined.
2. `save_user_data()` opens the database file in create/write mode (`'c'`) and stores each key-value pair. Strings are encoded to bytes automatically.
3. `load_user_data()` opens the database in read mode (`'r'`), reads back all keys, decodes the byte values to strings, and returns a dictionary.
4. The loaded data is formatted into a readable sentence and printed.

## File Structure

```
Database/
└── DatabaseManager/
    └── Console_Code/
        └── data_manager.py    # Main script
```

## Notes

- The database file is created in the current working directory when the script runs.
- `dbm` stores all keys and values as bytes. The `load_user_data()` function decodes the values using `.decode()`.

## Related examples

- [Object Clone](../Object%20Clone/readme.md) and [Custom Exception](../Custom%20Exception/readme.md) — other short Python fundamentals examples
- [Back to all Python projects](../README.md)
