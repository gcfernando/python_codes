# 📡 WIFI-RADAR by Gehan Fernando
### *Tactical Network Scanner — See Every Signal. Know Your Airspace.*

```
 ██╗    ██╗██╗███████╗██╗      ██████╗  █████╗ ██████╗  █████╗ ██████╗
 ██║    ██║██║██╔════╝██║      ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗
 ██║ █╗ ██║██║█████╗  ██║█████╗██████╔╝███████║██║  ██║███████║██████╔╝
 ██║███╗██║██║██╔══╝  ██║╚════╝██╔══██╗██╔══██║██║  ██║██╔══██║██╔══██╗
 ╚███╔███╔╝██║██║     ██║      ██║  ██║██║  ██║██████╔╝██║  ██║██║  ██║
  ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝      ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
```

> *"In the age of invisible signals, the one who sees everything wins."*

---

## 🎯 What Is This?

WiFi-Radar is a **real-time, military-style radar interface** that scans every wireless access point near you and displays them as live blips on a rotating radar — just like the ones you've seen in war movies, but for your Wi-Fi neighborhood.

Built for **network engineers, security researchers, curious geeks**, and anyone who's ever wondered *"whose router is that?"*

No cloud. No tracking. No nonsense. **100% local.**

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔄 **Live Radar Sweep** | Rotating sweep refreshes every 4 seconds with real scan data |
| 📡 **Real Scan Data** | Uses native OS tools — `netsh`, `airport`, `nmcli` — actual radio hardware |
| 🏭 **Vendor Identification** | Identifies 200+ router manufacturers from MAC OUI (TP-Link, ASUS, Netgear…) |
| 📈 **Signal History Graph** | Live multi-line chart tracking signal strength over time — pin any AP |
| 🎨 **Color-Coded Threats** | Security level visible at a glance — teal=WPA3, red=OPEN, orange=WEP |
| 📋 **Multi-Band Grouping** | WiFi 6/7 routers with multiple radios shown as one entry with sub-bands |
| ⚠️ **New AP Alerts** | Audio beep + popup when a new unknown network appears |
| ⬇️ **CSV Export** | One-click snapshot of all visible networks with full metadata |
| 🖥️ **CRT Aesthetic** | Scanlines, phosphor glow, flicker — because style matters |
| 🌐 **Cross-Platform** | Windows, macOS, Linux — one codebase, native scan on each |

---

## 🚀 Quick Start

### Windows
```bat
double-click  START_WINDOWS.bat
```
Browser opens automatically at **http://localhost:5000**

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
python server.py        # Windows / macOS
sudo python3 server.py  # Linux
```
Then open → **http://localhost:5000**

---

## 🎨 The Color Code

The radar speaks in colors. Learn to read it.

| Color | Security | Meaning |
|---|---|---|
| 🩵 **Teal** | WPA3 | Fort Knox. Best in class. |
| 🟢 **Lime** | WPA2/WPA3 | Transition mode. Almost there. |
| 🟢 **Green** | WPA2 · 2.4GHz | Standard protection. Fine. |
| 🔵 **Cyan** | WPA2 · 5GHz | Fast and protected. |
| 🟡 **Amber** | WPA | Old. Should upgrade. |
| 🟠 **Orange** | WEP | Broken. Hackable in minutes. |
| 🔴 **Red** | OPEN | No password. Walk right in. |

---

## 🖥️ Platform Details

| OS | Scan Tool | Fallback | Needs Root? |
|---|---|---|---|
| **Windows** | `netsh wlan show networks mode=Bssid` | state machine parser | No |
| **macOS** | `airport -s` | `system_profiler SPAirPortDataType` | No |
| **Linux** | `nmcli dev wifi list --rescan yes` | `iwlist scan` | Yes (sudo) |

---

## 📁 File Structure

```
wifi-radar/
├── server.py            ← Python backend · WiFi scanner + Flask API
├── index.html           ← Military radar UI · pure HTML/CSS/JS
├── requirements.txt     ← Python deps (flask, flask-cors)
├── START_WINDOWS.bat    ← Windows one-click launcher
├── START_UNIX.sh        ← macOS / Linux launcher
└── README.md            ← You are here
```

---

## 🔌 API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Radar UI |
| `GET /api/scan` | Live scan data as JSON |
| `GET /api/export/csv` | Download snapshot as CSV |
| `GET /api/debug` | Raw scan output + diagnostics |

---

## 🩺 Troubleshooting

<details>
<summary><b>📵 APs showing 0 on Windows</b></summary>

1. Make sure Wi-Fi is **ON** in Windows Settings
2. Verify WLAN AutoConfig service is running:
   `Win+R` → `services.msc` → find **WLAN AutoConfig** → Start
3. Test manually in CMD:
   ```
   netsh wlan show networks mode=Bssid
   ```
4. Try running `START_WINDOWS.bat` **as Administrator**
5. Visit `http://localhost:5000/api/debug` to see raw output
</details>

<details>
<summary><b>🍎 macOS Ventura/Sonoma issues</b></summary>

The `airport` utility was removed in newer macOS versions.
The app automatically falls back to `system_profiler`.

If still failing:
- Go to **System Preferences → Privacy & Security → Full Disk Access**
- Add your Terminal app
</details>

<details>
<summary><b>🐧 Linux — permission denied</b></summary>

```bash
sudo python3 server.py
# or
sudo nmcli dev wifi list --rescan yes
```

Make sure NetworkManager is running:
```bash
sudo systemctl start NetworkManager
```
</details>

<details>
<summary><b>🔍 Why does my router show multiple blips?</b></summary>

Modern **WiFi 6/6E/7 routers** with MLO (Multi-Link Operation) broadcast the **same SSID from multiple physical radios** (2.4 GHz, 5 GHz, 6 GHz) — each with its own MAC address.

WiFi-Radar detects this and **groups them** under one entry in the list, showing each band as a sub-row. On the radar, one label is shown at the strongest radio with a `3× 2.4+5+6G` badge.
</details>

---

## 🛠️ Requirements

- **Python 3.8+** — [python.org/downloads](https://python.org/downloads)
- **Flask** + **Flask-CORS** — auto-installed by launcher scripts
- **Wi-Fi adapter** — must be enabled in OS settings
- **Browser** — any modern browser (Chrome, Firefox, Edge, Safari)

---

## ⚠️ Disclaimer

This tool is intended for **educational and network diagnostic purposes only**.

Only scan networks **you own or have explicit permission to scan**.
Use responsibly. Know your local laws regarding wireless scanning.

---

## 📜 Built With

- **Python 3** · Flask · threading
- **Vanilla JS** · Canvas API · Web Audio API
- **HTML5 / CSS3** · no frameworks, no dependencies
- **netsh / airport / nmcli** · native OS WiFi tools
- **Orbitron + Share Tech Mono** · because it has to look right

---

<div align="center">

```
SCAN COUNT: ████████  //  NETWORKS: ████  //  STATUS: ACTIVE
```

*Made with 🟢 phosphor glow and too much coffee.*

</div>
