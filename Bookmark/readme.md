# Bookmark

A lightweight command-line link organizer for saving, searching, opening, editing, and deleting bookmarks with notes.

## Overview

Bookmark stores your important URLs in a local SQLite database (`links.db`) alongside a title and a short summary note. All operations are done through a simple interactive prompt. The `rich` library provides colored, readable output in the terminal.

## Features

- **Add** links with a title, URL, and summary note
- **Search** links by keyword matching the title
- **Open** a saved link directly in your default web browser
- **Edit** the title, URL, and note of an existing bookmark
- **Delete** a bookmark by ID
- Data persisted in a local SQLite database (`links.db`)
- Color-coded terminal output via `rich`
- Graceful exit with `Ctrl+C`

## Requirements

```
rich
```

`sqlite3` and `webbrowser` are part of the Python standard library.

Install the dependency:

```bash
pip install rich
```

## Usage

```bash
python book_marks.py
```

At the prompt, type one of the following commands:

| Command | Description |
|---|---|
| `ADD` | Add a new bookmark |
| `SEARCH` | Search bookmarks by title keyword |
| `EDIT` | Search and then edit a bookmark |
| `DELETE` | Search and then delete a bookmark |
| `OPEN` | Search and then open a bookmark in the browser |
| `HELP` | Show the list of available commands |

### Example Session

```
COMMAND >> add
Title: Python Docs
URL: https://docs.python.org
Summary: Official Python documentation

COMMAND >> search
Keyword (Title): python
[1] Python Docs → https://docs.python.org
    Official Python documentation

COMMAND >> open
Keyword (Title): python
[1] Python Docs → https://docs.python.org
Choose ID: 1
Opening...
```

## File Structure

```
Bookmark/
└── Console_Code/
    └── book_marks.py    # Main script (also creates links.db in the working directory)
```

## Notes

- `links.db` is created automatically in the directory where the script is run.
- The database schema adds the `note` column automatically if it's missing (for backwards compatibility with older databases).
