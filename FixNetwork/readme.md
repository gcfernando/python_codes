# FixNetwork

A Windows network repair utility that runs a sequence of safe diagnostic and reset operations to stabilize an unstable or slow internet connection.

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

Run as Administrator in a terminal or PowerShell:

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
- No system files, programs, or personal data are modified.
