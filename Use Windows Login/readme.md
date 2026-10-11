# Verify Windows Credentials in Python — pywin32 LogonUser Example

A short Python script that shows **how to check a Windows username and password from Python** with `win32security.LogonUser` (pywin32), as a simple Windows credential gate for a script or tool.

## Overview

This script uses `getpass` to securely collect the current user's Windows password (without echoing it to the terminal) and then verifies it via the Win32 `LogonUser` API. This pattern can be used to add a Windows credential gate to any Python application.

## Features

- Automatically detects the currently logged-in Windows username
- Prompts for the password securely (input is not displayed)
- Verifies credentials against the local Windows account using `win32security.LogonUser`
- Prints a success or failure message

## Requirements

```
pywin32
```

Install the dependency:

```bash
pip install pywin32
```

> The script imports Python's built-in `getpass` module, so no extra package is needed for the password prompt. `pywin32` provides the `win32security` module required for Windows authentication.

## Usage

From the `Console_Code` folder:

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
- The domain argument is `None`. Microsoft's `LogonUser` documentation recommends the UPN format (`user@domain`) for the username in that case, so domain accounts may need the username adjusted.
- Accounts that sign in with a Microsoft account, PIN, or Windows Hello may need the Microsoft account password rather than the PIN. Repeated failed attempts count towards account lockout policies.

## Related Projects

- [Password Generator and Strength Checker](../Password%20Utility/readme.md)
- [WiFi Profiles — Windows Wi-Fi utility](../Wifi%20Profiles/readme.md)
- [Back to all Python projects](../README.md)
