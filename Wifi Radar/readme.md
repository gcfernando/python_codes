# WiFi Radar

A real-time, cross-platform Wi-Fi scanner with a military-style radar web interface. Displays nearby access points as live radar blips with signal strength, security info, vendor lookup, and CSV export.

## Overview

WiFi Radar runs a local Flask web server that continuously scans nearby Wi-Fi networks using native OS tools. The results are displayed in a browser-based radar UI that refreshes automatically. Vendor lookup is done via the macvendors.com API and cached locally.

## Features

| Feature | Description |
|---|---|
| Live radar sweep | Refreshes every 4 seconds with real scan data |
| Real scan data | Uses native OS tools — `netsh`, `airport`, `nmcli`, `iwlist` |
| Vendor identification | Manufacturer resolved via macvendors.com API, cached in `vendor_cache.json` |
| Color-coded security | Visual security level (WPA3, WPA2, WPA, WEP, OPEN) |
| Signal strength | dBm and percentage, with noise floor and SNR on supported platforms |
| Radio generation | WiFi 4/5/6/7 detection (802.11n/ac/ax/be) |
| Cipher detection | CCMP vs TKIP per access point |
| Network type | Infrastructure vs Ad-Hoc |
| New AP alerts | Alert when a new unknown network appears |
| CSV export | Download a full metadata snapshot |
| Cross-platform | Windows, macOS, Linux — one codebase |
| ETag caching | 304 Not Modified support to avoid wasted bandwidth |
| Auto-install | Flask and Flask-CORS are installed automatically if missing |

## Quick Start

### Windows
```bat
START_WINDOWS.bat
```

### macOS
```bash
bash START_UNIX.sh
```

### Linux
```bash
sudo bash START_UNIX.sh
```

### Manual (any platform)
```bash
pip install flask flask-cors
python server.py         # Windows / macOS
sudo python3 server.py   # Linux
```

Then open your browser at: **http://localhost:5000**

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Radar UI (index.html) |
| `GET /api/scan` | Live scan data as JSON (ETag supported) |
| `GET /api/export/csv` | Download current networks as a CSV file |
| `GET /api/debug` | Raw scan output and diagnostics |
| `GET /api/vendor_cache` | Vendor cache stats and contents |

## Platform Details

| OS | Primary Tool | Fallback |
|---|---|---|
| Windows | `netsh wlan show networks mode=Bssid` | State machine parser |
| macOS | `airport -s` | `system_profiler SPAirPortDataType` |
| Linux | `nmcli dev wifi list --rescan yes` | `iwlist scan` |

Linux requires `sudo` for scanning.

## Data Fields Per Network

| Field | Description |
|---|---|
| SSID | Network name |
| BSSID | MAC address |
| Vendor | Manufacturer (from macvendors.com, cached) |
| Signal (dBm / %) | Signal strength |
| Noise floor / SNR | Available on macOS and Linux |
| Channel / Band | 2.4 GHz / 5 GHz / 6 GHz |
| Security | OPEN / WEP / WPA / WPA2 / WPA3 / WPA2/WPA3 |
| Cipher | CCMP (strong) or TKIP (weak) |
| Radio type | WiFi 4/5/6/7 |
| Network type | Infrastructure or Ad-Hoc |

## Requirements

- Python 3.8+
- Flask and Flask-CORS (auto-installed by launcher scripts)
- Wi-Fi adapter enabled in OS settings
- Any modern web browser
- Internet access for vendor lookups (works offline after cache is built)

## File Structure

```
Wifi Radar/
├── server.py              # Python backend — Wi-Fi scanner + Flask API
├── index.html             # Radar UI — pure HTML/CSS/JS
├── requirements.txt       # Python dependencies (flask, flask-cors)
├── vendor_cache.json      # Auto-generated vendor lookup cache
├── START_WINDOWS.bat      # Windows one-click launcher
└── START_UNIX.sh          # macOS / Linux launcher
```

## Disclaimer

This tool is intended for educational and network diagnostic purposes only. Only scan networks you own or have explicit permission to scan.
