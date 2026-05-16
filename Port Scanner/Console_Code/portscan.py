#!/usr/bin/env python3
"""
Developer ::> Gehan Fernando

Multithreaded TCP port scanner.

Features:
    - IPv4 and IPv6 support
    - Flexible port specification: "80", "1-1024", "22,80,443", "1-100,8080"
    - Optional banner grabbing
    - Streamed results (printed as discovered)
    - Structured logging, optional JSON output
    - Graceful Ctrl+C handling
    - Configurable concurrency and timeout

Usage:
    portscan.py example.com
    portscan.py example.com -p 1-65535 -t 0.5 -c 500
    portscan.py 2606:4700::1111 -p 80,443 --banner
    portscan.py example.com -p 1-1024 --json > results.json

Disclaimer:
    Only scan hosts you own or have explicit written permission to test.
    Unauthorized scanning may violate computer-misuse laws in your jurisdiction.
"""

from __future__ import annotations

import argparse
import json
import logging
import signal
import socket
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from typing import Iterable, Iterator

# ---------------------------------------------------------------------------
# Configuration defaults
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT = 1.0
DEFAULT_CONCURRENCY = 200
DEFAULT_PORTS = "1-1024"
MAX_PORT = 65535
BANNER_BYTES = 1024

log = logging.getLogger("portscan")

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScanResult:
    """Result of scanning a single TCP port."""

    port: int
    state: str  # "open" | "closed" | "filtered"
    service: str | None = None
    banner: str | None = None


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ScannerError(Exception):
    """Base class for scanner errors users see on the CLI."""


class ResolutionError(ScannerError):
    """Raised when a target hostname cannot be resolved."""


class PortSpecError(ScannerError):
    """Raised when the --ports specification cannot be parsed."""


# ---------------------------------------------------------------------------
# Resolution & parsing
# ---------------------------------------------------------------------------


def resolve_target(target: str) -> tuple[str, int]:
    """Resolve a hostname to (ip, address_family). Prefers IPv4, falls back to IPv6."""
    try:
        infos = socket.getaddrinfo(target, None, type=socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise ResolutionError(f"Failed to resolve {target!r}: {e}") from e

    # Prefer IPv4 for compatibility; users can pass an IPv6 literal to force v6.
    for preferred in (socket.AF_INET, socket.AF_INET6):
        for family, _type, _proto, _canon, sockaddr in infos:
            if family == preferred:
                ip = sockaddr[0]  # first element is the host string for both v4 and v6
                assert isinstance(ip, str)
                return ip, int(family)

    raise ResolutionError(f"No usable address for {target!r}")


def parse_ports(spec: str) -> list[int]:
    """
    Parse a port spec into a sorted, deduplicated list.

    Accepts:
        "80"               -> [80]
        "1-1024"           -> [1, 2, ..., 1024]
        "22,80,443"        -> [22, 80, 443]
        "1-100,443,8000-8100"
    """
    ports: set[int] = set()

    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            if "-" in part:
                start_s, end_s = part.split("-", 1)
                start, end = int(start_s), int(end_s)
                if not 1 <= start <= end <= MAX_PORT:
                    raise ValueError(f"out of range: {part}")
                ports.update(range(start, end + 1))
            else:
                port = int(part)
                if not 1 <= port <= MAX_PORT:
                    raise ValueError(f"out of range: {part}")
                ports.add(port)
        except ValueError as e:
            raise PortSpecError(
                f"Invalid port spec {part!r}: {e}. "
                "Use formats like '80', '1-1024', or '22,80,443'."
            ) from e

    if not ports:
        raise PortSpecError("Empty port specification.")

    return sorted(ports)


# ---------------------------------------------------------------------------
# Scanning core
# ---------------------------------------------------------------------------


def _grab_banner(sock: socket.socket) -> str | None:
    """Best-effort banner grab. Returns None if nothing readable."""
    try:
        sock.settimeout(0.5)
        data = sock.recv(BANNER_BYTES)
        if not data:
            return None
        return data.decode("utf-8", errors="replace").strip() or None
    except (socket.timeout, OSError):
        return None


def scan_port(
    ip: str,
    family: int,
    port: int,
    timeout: float,
    grab_banner: bool,
) -> ScanResult:
    """Scan a single TCP port. Always returns a ScanResult (open/closed/filtered)."""
    sock = socket.socket(family, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        err = sock.connect_ex((ip, port))
        if err == 0:
            service = _service_name(port)
            banner = _grab_banner(sock) if grab_banner else None
            return ScanResult(port=port, state="open", service=service, banner=banner)
        if err in (111,):  # ECONNREFUSED on Linux; differs by OS, but good enough
            return ScanResult(port=port, state="closed")
        return ScanResult(port=port, state="filtered")
    except socket.timeout:
        return ScanResult(port=port, state="filtered")
    except OSError as e:
        log.debug("port %d errored: %s", port, e)
        return ScanResult(port=port, state="filtered")
    finally:
        sock.close()


def _service_name(port: int) -> str | None:
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return None


def scan_ports(
    ip: str,
    family: int,
    ports: Iterable[int],
    timeout: float,
    concurrency: int,
    grab_banner: bool,
    cancel_event: threading.Event,
) -> Iterator[ScanResult]:
    """
    Yield only OPEN ports as they're discovered.

    Cancellation: if `cancel_event` is set, in-flight tasks finish but no new
    results are yielded; the executor is shut down with cancel_futures=True.
    """
    with ThreadPoolExecutor(max_workers=concurrency, thread_name_prefix="scan") as ex:
        futures = {
            ex.submit(scan_port, ip, family, p, timeout, grab_banner): p for p in ports
        }
        try:
            for fut in as_completed(futures):
                if cancel_event.is_set():
                    break
                result = fut.result()
                if result.state == "open":
                    yield result
        finally:
            if cancel_event.is_set():
                # Python 3.9+: cancel pending futures so we exit promptly
                ex.shutdown(wait=False, cancel_futures=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Multithreaded TCP port scanner.",
        epilog="Only scan systems you are authorized to test.",
    )
    p.add_argument("target", help="Target hostname, IPv4, or IPv6 address.")
    p.add_argument(
        "-p",
        "--ports",
        default=DEFAULT_PORTS,
        help="Port spec (default: %(default)s). "
        "Examples: '80', '1-1024', '22,80,443', '1-100,8080'.",
    )
    p.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Per-port connection timeout in seconds (default: {DEFAULT_TIMEOUT}).",
    )
    p.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Max concurrent connections (default: {DEFAULT_CONCURRENCY}).",
    )
    p.add_argument(
        "--banner",
        action="store_true",
        help="Attempt to read a service banner from open ports.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit results as a single JSON document on stdout.",
    )
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging on stderr.",
    )
    return p


def _configure_logging(verbose: bool, json_mode: bool) -> None:
    # In JSON mode, send all human output to stderr so stdout stays clean.
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )
    if json_mode:
        # Suppress the human-readable INFO chatter in JSON mode unless -v.
        if not verbose:
            logging.getLogger().setLevel(logging.WARNING)


def main(argv: list[str] | None = None) -> int:
    """Run the scanner from the command line. Returns a process exit code."""
    args = _build_parser().parse_args(argv)
    _configure_logging(args.verbose, args.json)

    if args.concurrency < 1:
        log.error("--concurrency must be >= 1")
        return 2

    try:
        ports = parse_ports(args.ports)
        ip, family = resolve_target(args.target)
    except ScannerError as e:
        log.error("%s", e)
        return 2

    family_name = "IPv6" if family == socket.AF_INET6 else "IPv4"
    log.info("Target: %s -> %s (%s)", args.target, ip, family_name)
    log.info(
        "Scanning %d port(s) with concurrency=%d, timeout=%.2fs",
        len(ports),
        args.concurrency,
        args.timeout,
    )

    cancel = threading.Event()

    def _handle_sigint(_signum, _frame):
        """Set the cancel event so the scan loop can exit promptly."""
        log.warning("Interrupt received, shutting down...")
        cancel.set()

    signal.signal(signal.SIGINT, _handle_sigint)

    results: list[ScanResult] = []
    try:
        for r in scan_ports(
            ip=ip,
            family=family,
            ports=ports,
            timeout=args.timeout,
            concurrency=args.concurrency,
            grab_banner=args.banner,
            cancel_event=cancel,
        ):
            results.append(r)
            if not args.json:
                _print_result(r)
    except Exception as e:  # pylint: disable=broad-except
        # Last-resort safety net: any uncaught error from worker threads surfaces
        # here. We log with traceback and exit non-zero rather than crash.
        log.exception("Unexpected error during scan: %s", e)
        return 1

    if args.json:
        json.dump(
            {
                "target": args.target,
                "ip": ip,
                "family": family_name,
                "scanned": len(ports),
                "open": [asdict(r) for r in sorted(results, key=lambda x: x.port)],
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        log.info("Scan complete. %d open port(s) found.", len(results))

    return 0 if not cancel.is_set() else 130  # 130 = conventional SIGINT exit


def _print_result(r: ScanResult) -> None:
    svc = r.service or "unknown"
    line = f"  {r.port:<6} open   ({svc})"
    if r.banner:
        # Truncate noisy banners so the output stays readable.
        snippet = r.banner.replace("\n", " ")[:80]
        line += f"  banner={snippet!r}"
    print(line, flush=True)


if __name__ == "__main__":
    sys.exit(main())
