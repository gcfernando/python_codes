# portscan

A fast, multithreaded TCP port scanner written in pure Python. No dependencies outside the standard library.

> ⚠️ **Only scan systems you own or have explicit written permission to test.**
> Unauthorized scanning may violate computer-misuse laws in your jurisdiction (CFAA in the US, Computer Misuse Act in the UK, and similar statutes elsewhere).

---

## Features

- **IPv4 and IPv6** — resolves hostnames via `getaddrinfo`, prefers IPv4 with v6 fallback
- **Flexible port specs** — single ports, ranges, lists, or any mix: `80`, `1-1024`, `22,80,443`, `1-100,8080`
- **Three-state results** — distinguishes `open`, `closed`, and `filtered` ports
- **Banner grabbing** — optional service-banner read on open ports
- **Streamed output** — open ports print as they're discovered, not at the end
- **JSON mode** — machine-readable output for piping into other tools
- **Graceful Ctrl+C** — pending work is cancelled cleanly; exits with code 130
- **Configurable** — timeout, concurrency, and port range all tunable from the CLI

---

## Requirements

- Python **3.10** or newer (uses PEP 604 union syntax: `str | None`)
- No external packages

---

## Installation

Clone the repo and run the script directly:

```bash
git clone https://github.com/<your-username>/portscan.git
cd portscan
chmod +x portscan.py
```

Or drop `portscan.py` anywhere on your `$PATH`.

---

## Usage

### Basic scan

```bash
python3 portscan.py example.com
```

Scans ports `1-1024` (the default) with 200 concurrent connections.

### Custom port range

```bash
python3 portscan.py example.com -p 1-65535
```

### Specific ports

```bash
python3 portscan.py example.com -p 22,80,443,8080
```

### Mixed ranges and singletons

```bash
python3 portscan.py example.com -p 1-100,443,8000-8100
```

### Faster scan (higher concurrency, shorter timeout)

```bash
python3 portscan.py example.com -p 1-65535 -c 500 -t 0.5
```

### IPv6 target

```bash
python3 portscan.py 2606:4700::1111 -p 80,443
```

### Banner grabbing

```bash
python3 portscan.py example.com -p 22,80,443 --banner
```

### JSON output

```bash
python3 portscan.py example.com -p 1-1024 --json > results.json
```

In `--json` mode, human-readable logs go to stderr so stdout stays clean and pipeable.

### Verbose / debug logging

```bash
python3 portscan.py example.com -v
```

---

## CLI options

| Flag                  | Default   | Description                                            |
| --------------------- | --------- | ------------------------------------------------------ |
| `target`              | —         | Hostname, IPv4 address, or IPv6 address (required)     |
| `-p`, `--ports`       | `1-1024`  | Port spec — single, range, list, or mix                |
| `-t`, `--timeout`     | `1.0`     | Per-port connection timeout in seconds                 |
| `-c`, `--concurrency` | `200`     | Maximum concurrent connections                         |
| `--banner`            | off       | Attempt to read a service banner from open ports       |
| `--json`              | off       | Emit results as a single JSON document on stdout       |
| `-v`, `--verbose`     | off       | Enable debug logging on stderr                         |

---

## Output formats

### Human-readable (default)

```
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

---

## Port states

| State      | Meaning                                                              |
| ---------- | -------------------------------------------------------------------- |
| `open`     | Service accepted the TCP handshake                                   |
| `closed`   | Host actively refused the connection (RST) — host is up, port isn't  |
| `filtered` | Connection timed out — likely a firewall dropping packets silently   |

Only `open` ports are shown by default; the distinction between `closed` and `filtered` is preserved internally and surfaced in `--json` if you extend the output.

---

## Performance notes

- Default concurrency (200) is safe for most networks. For full 65535-port sweeps, `-c 500` to `-c 1000` is reasonable on a healthy connection.
- On Linux you may hit the open-file-descriptor limit (`ulimit -n`) at high concurrency. Raise it with `ulimit -n 4096` before scanning.
- Don't set `--timeout` below `0.3` over the internet — you'll start misclassifying slow-but-open ports as `filtered`.

---

## Exit codes

| Code | Meaning                                  |
| ---- | ---------------------------------------- |
| `0`  | Scan completed successfully              |
| `1`  | Unexpected error during scan             |
| `2`  | Invalid arguments (bad port spec, etc.)  |
| `130`| Interrupted by user (Ctrl+C)             |

---

## Legal & ethical use

This tool is intended for:

- Auditing systems you own
- Authorized penetration tests with written scope
- CTF challenges and lab environments (HackTheBox, TryHackMe, etc.)
- Educational use against intentionally vulnerable targets (`scanme.nmap.org`)

It is **not** intended for unauthorized scanning of third-party infrastructure. The author accepts no responsibility for misuse.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Author

**Gehan Fernando**
