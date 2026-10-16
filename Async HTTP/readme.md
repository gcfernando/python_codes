# Async HTTP Requests in Python with aiohttp and asyncio — GET, POST, PUT, DELETE Example

An interactive command-line client that shows how to make **asynchronous HTTP requests in Python** with `asyncio` and `aiohttp` — sending GET, POST, PUT, and DELETE requests to a REST API and printing the JSON responses.

## Overview

This script demonstrates asynchronous HTTP communication by connecting to the Northwind sample REST API. It runs a loop that lets you repeatedly choose a request method, provide the necessary data, and view the JSON response — all using non-blocking I/O.

## Features

- Supports GET, POST, PUT, and DELETE methods
- Asynchronous request handling via `aiohttp` and `asyncio`
- Interactive loop with an option to continue or exit after each request
- Pretty-printed JSON responses using `pprint`
- Targets the Northwind API's `/categories` resource for demonstration

## Requirements

```text
aiohttp
```

> **Note:** `asyncio` and `pprint` are part of the Python standard library and do not require installation.

Install the external dependency:

```bash
pip install aiohttp
```

## Usage

From the `Console_Code` folder:

```bash
python HttpCall.py
```

The script uses `http://northwind.now.sh/api/` as its base URL. At the time of writing, that address redirects to `https://northwind.vercel.app/api/`, a shared public demo API, so POST, PUT, and DELETE requests change data that other people can see. Use your own API for anything beyond experimentation.

### Example Session

```text
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

```text
Async HTTP/
└── Console_Code/
    └── HttpCall.py    # Main script
```

## Notes

- Each request opens its own `aiohttp.ClientSession`. That keeps the demo short; in larger programs, create one session and reuse it for many requests.
- Entering any method other than GET, POST, PUT, or DELETE ends the loop.

## Related Projects

- [Internet Speed Test](../Internet%20Speed%20Test/readme.md)
- [Port Scanner](../Port%20Scanner/readme.md)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
