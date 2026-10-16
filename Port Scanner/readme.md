# Python Port Scanner — Multithreaded TCP Scanner with IPv6, Banners and JSON Output

A fast, multithreaded **TCP port scanner written in pure Python** (standard library only). It scans IPv4 and IPv6 hosts, distinguishes open, closed, and filtered ports, can grab service banners, and can emit JSON for automation.

> **Only scan systems you own or have explicit written permission to test.**
> Unauthorized scanning may violate computer-misuse laws in your jurisdiction.

## Features

- **IPv4 and IPv6** — resolves hostnames via `getaddrinfo`, prefers IPv4 with automatic IPv6 fallback
- **Flexible port specification** — single ports, ranges, lists, or any mix: `80`, `1-1024`, `22,80,443`, `1-100,8080`
- **Three port states** — distinguishes `open`, `closed`, and `filtered`
- **Banner grabbing** — optional service-banner read on open ports
- **Streamed output** — open ports are printed as they are discovered
- **JSON mode** — machine-readable output for piping into other tools
- **Graceful Ctrl+C** — pending work is cancelled cleanly; exits with code 130
- **Configurable** — timeout, concurrency, and port range are all tunable from the CLI

## Requirements

- Python **3.10** or newer
- No external packages

## Usage

```bash
python portscan.py <target> [options]
```

### Examples

`example.com` below is a placeholder — replace it with a host you own or are authorized to scan, such as `127.0.0.1` for your own machine.

```bash
# Scan default ports 1-1024
python portscan.py example.com

# Scan all ports
python portscan.py example.com -p 1-65535

# Scan specific ports
python portscan.py example.com -p 22,80,443

# Mixed range and singletons
python portscan.py example.com -p 1-100,443,8000-8100

# Faster scan
python portscan.py example.com -p 1-65535 -c 500 -t 0.5

# IPv6 target
python portscan.py 2606:4700::1111 -p 80,443

# Banner grabbing
python portscan.py example.com -p 22,80,443 --banner

# JSON output
python portscan.py example.com -p 1-1024 --json > results.json

# Verbose/debug logging
python portscan.py example.com -v
```

## CLI Options

| Flag | Default | Description |
|---|---|---|
| `target` | — | Hostname, IPv4, or IPv6 address (required) |
| `-p`, `--ports` | `1-1024` | Port specification |
| `-t`, `--timeout` | `1.0` | Per-port connection timeout (seconds) |
| `-c`, `--concurrency` | `200` | Maximum concurrent connections |
| `--banner` | off | Attempt to read a service banner from open ports |
| `--json` | off | Emit results as a JSON document on stdout |
| `-v`, `--verbose` | off | Enable debug logging on stderr |

## Output Formats

### Human-readable (default)

Illustrative output (addresses and open ports depend on the target):

```text
14:32:01 [INFO] Target: example.com -> 93.184.216.34 (IPv4)
14:32:01 [INFO] Scanning 1024 port(s) with concurrency=200, timeout=1.00s
  22     open   (ssh)
  80     open   (http)
  443    open   (https)
14:32:04 [INFO] Scan complete. 3 open port(s) found.
```

### JSON (`--json`)
```json
{
  "target": "example.com",
  "ip": "93.184.216.34",
  "family": "IPv4",
  "scanned": 1024,
  "open": [
    { "port": 22,  "state": "open", "service": "ssh",   "banner": null },
    { "port": 80,  "state": "open", "service": "http",  "banner": null },
    { "port": 443, "state": "open", "service": "https", "banner": null }
  ]
}
```

## Port States

| State | Meaning |
|---|---|
| `open` | Service accepted the TCP handshake |
| `closed` | Host actively refused the connection |
| `filtered` | Connection timed out (likely a firewall) |

The human-readable format and the JSON structure above were confirmed by scanning `127.0.0.1`. Service names come from the operating system's services database (`socket.getservbyport`), so the same port can be labelled differently on different systems (for example, port 135 appears as `epmap` on Windows).

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Scan completed successfully |
| `1` | Unexpected error during scan |
| `2` | Invalid arguments |
| `130` | Interrupted by user (Ctrl+C) |

## File Structure

```text
Port Scanner/
└── Console_Code/
    └── portscan.py    # Main script
```

## FAQ

**Is this a replacement for Nmap?**
No. It performs TCP connect scans only (no SYN, UDP, OS, or version detection). It is a readable example of a concurrent scanner and a lightweight tool for quick checks.

**Why are some ports shown as `filtered`?**
The connection attempt timed out rather than being refused, which usually means a firewall dropped the packets. Increasing `--timeout` can turn slow `filtered` results into `open` or `closed`.

## Related Projects

- [WiFi Radar — Flask Wi-Fi scanner dashboard](../Wifi%20Radar/readme.md)
- [Linux command reference for cybersecurity](https://github.com/gcfernando/other_codes/tree/main/Linux_Commands)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
