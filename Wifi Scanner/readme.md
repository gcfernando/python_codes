# Python Wi-Fi Scanner — List Nearby Networks with pywifi

A short Python script that **scans for nearby Wi-Fi networks** with the `pywifi` library and prints each network's SSID, BSSID, signal strength, frequency, and security type.

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

From the `Console_Code` folder:

```bash
python Wifi_Scanner.py
```

### Example Output

Illustrative output showing the labels the script prints. Because of the [known issues](#known-issues), on Windows the frequency appears in GHz (for example `2.412`) and WPA2-Personal networks are labelled `WPA2-EAP`.

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
- `scan()` starts an asynchronous scan, and the script reads `scan_results()` immediately afterwards. Waiting a few seconds between the two calls (for example `time.sleep(3)`) can return a more complete list.

## Known issues

- **Security labels are shifted.** `pywifi` numbers its AKM types as 0 = none, 1 = WPA, 2 = WPA-PSK, 3 = WPA2, 4 = WPA2-PSK, 5 = unknown, but the script's `akm_modes` list is ordered `OPEN, WPA-PSK, WPA-EAP, WPA2-PSK, WPA2-EAP, UNKNOWN`. As a result, a typical WPA2-Personal network (type 4) is printed as `WPA2-EAP`. Reordering the list to `['OPEN', 'WPA-EAP', 'WPA-PSK', 'WPA2-EAP', 'WPA2-PSK', 'UNKNOWN']` matches `pywifi`'s constants.
- **Frequency units.** On Windows, `pywifi` returns the channel centre frequency in kHz, so `network.freq / 1000000` prints gigahertz (for example `2.412`) under a "MHz" label. Dividing by `1000` gives MHz. Other platforms may report frequency in different units.

## Related Projects

- [WiFi Radar — live Wi-Fi dashboard](../Wifi%20Radar/readme.md)
- [WiFi Profiles — saved Windows Wi-Fi networks](../Wifi%20Profiles/readme.md)
- [Internet Speed Test](../Internet%20Speed%20Test/readme.md)
- [Back to all Python projects](../README.md)
