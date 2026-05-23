# Use Windows Login

Authenticates a user against the local Windows account using their Windows password.

## Overview

This script uses `getpass` to securely collect the current user's Windows password (without echoing it to the terminal) and then verifies it via the Win32 `LogonUser` API. This pattern can be used to add a Windows credential gate to any Python application.

## Features

- Automatically detects the currently logged-in Windows username
- Prompts for the password securely (input is not displayed)
- Verifies credentials against the local Windows account using `win32security.LogonUser`
- Prints a success or failure message

## Requirements

```
getpass4
pywin32
```

Install dependencies:

```bash
pip install getpass4 pywin32
```

> `getpass4` is a drop-in replacement for the standard `getpass` module with improved compatibility. `pywin32` provides the `win32security` module required for Windows authentication.

## Usage

```bash
python Use_Win_Login.py
```

### Example Session

```
Enter your Windows password:
Login successful!
```

Or, if the password is incorrect:

```
Enter your Windows password:
Login failed. Exiting application.
```

## How It Works

1. `getpass.getuser()` retrieves the current Windows username from the environment.
2. `getpass.getpass()` securely prompts for a password without displaying it.
3. `win32security.LogonUser()` attempts a network logon with the provided credentials.
   - If successful: prints `Login successful!`
   - If it raises `win32security.error`: prints `Login failed. Exiting application.`

## File Structure

```
Use Windows Login/
└── Console_Code/
    └── Use_Win_Login.py    # Main script
```

## Notes

- This script is Windows-only. `win32security` is not available on macOS or Linux.
- The `LOGON32_LOGON_NETWORK` logon type is used, which validates credentials without creating a full user session.
