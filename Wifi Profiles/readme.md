# Wifi Profiles

A Windows utility for listing saved Wi-Fi network names and passwords, and bulk-deleting profiles while preserving a specified network.

## Overview

This script uses `netsh wlan` commands via `subprocess` to:
1. Display all saved Wi-Fi SSIDs and their stored passwords
2. Delete all saved Wi-Fi profiles except for one specified network

Both operations are handled in the same script. Run it selectively by commenting out the section you don't need.

## Features

- Lists all saved Wi-Fi profiles with their SSIDs and passwords
- Bulk-deletes all Wi-Fi profiles except a designated "safe" SSID
- Uses only Python standard library modules (`subprocess`, `re`)
- No external dependencies

## Requirements

No external dependencies. Uses only Python standard library.

> **Windows only.** Requires a Windows system with the WLAN AutoConfig service running.

## Usage

```bash
python profile.py
```

### Part 1 — List All SSIDs and Passwords

Runs immediately and prints output like:

```
SSID: HomeNetwork
Password: mypassword123
------------------------------
SSID: OfficeWifi
Password: No password
------------------------------
```

### Part 2 — Delete All Profiles Except One

Before running the delete section, open `profile.py` and set the SSID you want to keep:

```python
ignore_ssid = "YourNetworkName"
```

The script will then delete all other saved profiles and print each deleted profile name.

## How It Works

**Listing passwords:**
- Runs `netsh wlan show profiles` to get all saved SSIDs
- For each SSID, runs `netsh wlan show profile <name> key=clear` to retrieve the stored password
- Extracts the password using a regex on `Key Content`

**Deleting profiles:**
- Retrieves the same profile list
- Runs `netsh wlan delete profile name=<name>` for each profile not matching `ignore_ssid`

## File Structure

```
Wifi Profiles/
└── Console_Code/
    └── profile.py    # Main script
```

## Notes

- You may need to run this script as Administrator to read stored passwords on some Windows configurations.
- This tool is intended for personal use to manage your own saved Wi-Fi connections. Always use responsibly and with respect for privacy.
- Deleted profiles cannot be recovered — the connection details must be re-entered manually.
