# Wifi Scanner

Scans for nearby Wi-Fi networks and prints detailed information about each one using the `pywifi` library.

## Overview

This script initializes the system's first Wi-Fi interface, triggers a scan, and then reads the results to display network details including SSID, BSSID, signal strength, frequency, and security mode for each discovered access point.

## Features

- Scans all visible Wi-Fi networks
- Displays for each network:
  - SSID (network name)
  - BSSID (access point MAC address)
  - Signal strength (dBm)
  - Frequency (MHz)
  - AKM security mode (OPEN, WPA-PSK, WPA2-PSK, WPA-EAP, WPA2-EAP, UNKNOWN)
  - Authentication mode
- Error handling for scan failures

## Requirements

```
pywifi
```

Install the dependency:

```bash
pip install pywifi
```

> On Windows, `pywifi` may also require `comtypes`. Install with:
> ```bash
> pip install pywifi comtypes
> ```

## Usage

```bash
python Wifi_Scanner.py
```

### Example Output

```
SSID: HomeNetwork
BSSID: AA:BB:CC:DD:EE:FF
Signal Strength (dBm): -55
Frequency (MHz): 2412.0
Security Mode: WPA2-PSK
Security Auth: WPA2_PSK


SSID: GuestWifi
BSSID: 11:22:33:44:55:66
Signal Strength (dBm): -72
Frequency (MHz): 5180.0
Security Mode: WPA-PSK
Security Auth: WPA_PSK
```

## File Structure

```
Wifi Scanner/
└── Console_Code/
    └── Wifi_Scanner.py    # Main script
```

## Notes

- The script always uses the first Wi-Fi interface (`interfaces()[0]`). Systems with multiple Wi-Fi adapters will use whichever is first in the list.
- `pywifi` support varies by platform. It works on Windows and Linux; macOS support is limited.
- On Linux, you may need to run the script with `sudo` for full scan access.
