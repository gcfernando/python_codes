# Async HTTP

An interactive command-line client for making asynchronous HTTP requests using Python's `asyncio` and `aiohttp` libraries.

## Overview

This script demonstrates asynchronous HTTP communication by connecting to the Northwind sample REST API. It runs a loop that lets you repeatedly choose a request method, provide the necessary data, and view the JSON response — all using non-blocking I/O.

## Features

- Supports GET, POST, PUT, and DELETE methods
- Asynchronous request handling via `aiohttp` and `asyncio`
- Interactive loop with an option to continue or exit after each request
- Pretty-printed JSON responses using `pprint`
- Targets the Northwind API's `/categories` resource for demonstration

## Requirements

```
aiohttp
```

> **Note:** `asyncio` and `pprint` are part of the Python standard library and do not require installation.

Install the external dependency:

```bash
pip install aiohttp
```

## Usage

```bash
python HttpCall.py
```

### Example Session

```
Enter Method (GET, POST, PUT, DELETE): GET
# → prints list of categories

More! (Y|N): Y

Enter Method (GET, POST, PUT, DELETE): POST
Enter Category Id: 10
Enter Category Name: Beverages
Enter Category Description: Soft drinks and teas
# → prints created category

More! (Y|N): N
```

### Supported Methods

| Method | Action | Input Required |
|---|---|---|
| GET | Retrieve all categories | None |
| POST | Create a new category | ID, Name, Description |
| PUT | Update an existing category | ID, Name, Description |
| DELETE | Delete a category | ID |

## File Structure

```
Async HTTP/
└── Console_Code/
    └── HttpCall.py    # Main script
```
