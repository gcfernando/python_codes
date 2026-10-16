# Show Saved Wi-Fi Passwords and Delete Wi-Fi Profiles on Windows with Python (netsh)

A Windows utility written in Python that uses `netsh wlan` to **list saved Wi-Fi networks with their stored passwords** and **bulk-delete Wi-Fi profiles** while keeping one network.

> ⚠️ **Running the script as it is deletes your saved Wi-Fi profiles.** Both parts run one after the other: after listing the passwords, the script deletes every saved profile except the one named in `ignore_ssid`, which is set to the placeholder `"WIFI_NAME"`. Unless you change `ignore_ssid` to your network's name, or comment out the delete section, **all** saved Wi-Fi profiles are deleted.

## Overview

This script uses `netsh wlan` commands via `subprocess` to:
1. Display all saved Wi-Fi SSIDs and their stored passwords
2. Delete all saved Wi-Fi profiles except for one specified network

Both operations are in the same script and both run every time. To only list passwords, comment out the delete section (everything from the `ignore_ssid` line onwards).

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

Runs first and prints output like:

```text
SSID: HomeNetwork
Password: mypassword123
------------------------------
SSID: OfficeWifi
Password: No password
------------------------------
```

### Part 2 — Delete All Profiles Except One

Runs immediately after Part 1. Before running the script, open `profile.py` and set the SSID you want to keep (the default value is the placeholder `"WIFI_NAME"`):

```python
ignore_ssid = "YourNetworkName"
```

The script then deletes all other saved profiles, printing `Skipping profile: ...` for the kept network and `Deleted profile: ...` for each deleted one.

## How It Works

**Listing passwords:**
- Runs `netsh wlan show profiles` to get all saved SSIDs
- For each SSID, runs `netsh wlan show profile <name> key=clear` to retrieve the stored password
- Extracts the password using a regex on `Key Content`

**Deleting profiles:**
- Retrieves the same profile list
- Runs `netsh wlan delete profile name=<name>` for each profile not matching `ignore_ssid`

## File Structure

```text
Wifi Profiles/
└── Console_Code/
    └── profile.py    # Main script
```

## Notes

- You may need to run this script as Administrator to read stored passwords on some Windows configurations.
- This tool is intended for personal use to manage your own saved Wi-Fi connections. Always use responsibly and with respect for privacy.
- Deleted profiles cannot be recovered — the connection details must be re-entered manually. To keep a backup first, run `netsh wlan export profile key=clear folder=<path>` (the exported files contain passwords in plain text, so store them securely).
- The profile list is parsed with the English label `All User Profile`, so on Windows installations in other display languages the script may find no profiles.

## Related Projects

- [WiFi Scanner — list nearby networks](../Wifi%20Scanner/readme.md)
- [WiFi Radar — live Wi-Fi dashboard](../Wifi%20Radar/readme.md)
- [FixNetwork — Windows network reset script](../FixNetwork/readme.md)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
