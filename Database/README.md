# Database

A simple example of key-value data persistence using Python's built-in `dbm` module.

## Overview

This script demonstrates how to store and retrieve structured data using Python's `dbm` module — a lightweight, file-based key-value store that requires no external database server. It saves a set of user details to a database file, then reads them back and prints a formatted summary.

## Features

- Stores key-value pairs in a file-based database using `dbm`
- Reads back and decodes stored data from the database
- No external libraries or server setup required

## Requirements

No external dependencies. `dbm` is part of the Python standard library.

## Usage

```bash
python data_manager.py
```

**Example output:**
```
Hi, I am Gehan Fernando. I live in Sri Lanka, and I am 43 years old.
```

A file named `user.db` (or similar, depending on the platform's `dbm` backend) will be created in the working directory.

## How It Works

1. A dictionary of user data (first name, last name, age, country) is defined.
2. `save_user_data()` opens the database file in create/write mode and stores each key-value pair.
3. `load_user_data()` opens the database in read mode, reads back all keys, decodes the byte values to strings, and returns a plain dictionary.
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
- `dbm` stores all values as bytes. The `load_user_data()` function decodes them using `.decode()`.
