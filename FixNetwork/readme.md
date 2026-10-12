# Windows Network Reset Script in Python — Fix Internet Connection Problems

A Windows network repair utility written in Python that automates the standard **Windows network troubleshooting commands** — DHCP release/renew, DNS flush, Winsock and TCP/IP stack reset, proxy reset, adapter restart, and connectivity tests — with a progress bar and colour-coded results.

> ⚠️ **This script changes system network settings.** Resetting the TCP/IP stack and Winsock catalog can remove static IP addresses, custom DNS servers, and some VPN or network-filter configurations, and restarting adapters disconnects you briefly. Note any custom settings before running it.

## Overview

This script automates a series of common network troubleshooting steps — releasing DHCP leases, flushing caches, resetting the TCP/IP and Winsock stacks, restarting the WLAN service, and running connectivity tests — all with a progress bar and color-coded output. It must be run as Administrator.

## Features

- Administrator privilege check before execution
- Progress bar via `tqdm` showing step name and completion
- Color-coded output (green for success, red for failure) via `colorama`
- Runs 22 ordered network repair steps:

| Category | Steps |
|---|---|
| **Diagnostics (before fix)** | Show IP config, routing table, WinHTTP proxy |
| **DHCP + DNS** | Release lease, flush DNS, register DNS, renew lease |
| **Cache resets** | Clear ARP cache, reset NetBIOS cache and names |
| **Proxy & SSL** | Reset WinHTTP proxy, clear SSL state |
| **Service restart** | Restart WLAN service |
| **Core resets** | Reset TCP/IP stack, repair Winsock catalog |
| **Optional resets** | Reset IPv4 and IPv6 stacks |
| **Adapter restart** | Disable and re-enable active network adapters |
| **Connectivity tests** | Ping localhost, gateway, Google DNS (8.8.8.8), DNS lookup |

## Requirements

```
colorama
tqdm
```

Install dependencies:

```bash
pip install colorama tqdm
```

## Usage

From the `Console_Code` folder, in a terminal or PowerShell window opened as Administrator:

```bash
python network_repair.py
```

If not run as Administrator, the script will print an error and exit immediately.

After the routine completes, a reboot is recommended for maximum stability.

## File Structure

```
FixNetwork/
└── Console_Code/
    └── network_repair.py    # Main script
```

## Notes

- All commands use `subprocess.run()` with `shell=True`. Each step's output is shown only if the step fails.
- This tool is Windows-only. It relies on `netsh`, `ipconfig`, `arp`, `nbtstat`, `ping`, `nslookup`, and PowerShell cmdlets.
- Personal files and installed programs are not touched, but network configuration is: the TCP/IP, IPv4/IPv6, and Winsock resets rewrite network settings (a restart is needed for them to take full effect), DHCP leases are released and renewed, and active adapters are disabled and re-enabled.
- The "Clear SSL state" step runs `RunDll32.exe InetCpl.cpl,ClearMyTracksByProcess 8`, which deletes temporary Internet files in the Windows Internet Options cache.

## Related Projects

- [WiFi Profiles — manage saved Windows Wi-Fi networks](../Wifi%20Profiles/readme.md)
- [Internet Speed Test](../Internet%20Speed%20Test/readme.md)
- [Windows maintenance PowerShell script](https://github.com/gcfernando/other_codes/tree/main/SystemMaintenance)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
