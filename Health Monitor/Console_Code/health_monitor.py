#!/usr/bin/env python3
"""
Developer ::> Gehan Fernando
"""

import psutil
import time
import argparse
from collections import defaultdict
from datetime import datetime

from rich.console import Console, Group
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

console = Console(emoji=False)

SNAPSHOT_INTERVAL = 1
LEAK_THRESHOLD_MB = 50
LEAK_WINDOW = 10


def get_process_memory(pid: int) -> float | None:
    try:
        return psutil.Process(pid).memory_info().rss / (1024 * 1024)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def build_table(snapshots: dict[int, list[float]], streaks: dict[int, int]) -> Table:
    table = Table(
        title="Memory Leak Detector — Live Monitor",
        border_style="bright_blue",
        header_style="bold cyan",
        show_lines=True,
        expand=True,
        pad_edge=False,
    )

    # Fixed widths for numeric columns prevent header truncation ("Current..." / "Growth ...")
    table.add_column("PID", style="dim", justify="right", width=6, no_wrap=True)
    table.add_column("Process Name", ratio=1, overflow="ellipsis")
    table.add_column("Current (MB)", justify="right", width=13, no_wrap=True)
    table.add_column("Growth (MB)", justify="right", width=12, no_wrap=True)
    table.add_column("Status", justify="center", width=10, no_wrap=True, overflow="crop")

    for pid, history in sorted(snapshots.items(), key=lambda x: -x[1][-1]):
        try:
            name = psutil.Process(pid).name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            name = "unknown"

        current = history[-1]
        growth = current - history[0] if len(history) > 1 else 0.0
        consec = streaks.get(pid, 0)

        if consec >= LEAK_WINDOW:
            status = Text("🚨 LEAK", style="bold red")
            growth_style = "bold red"
        elif growth > LEAK_THRESHOLD_MB / 2:
            status = Text("👀 WATCH", style="yellow")
            growth_style = "yellow"
        else:
            status = Text("✅ OK", style="green")
            growth_style = "green"

        growth_text = f"+{growth:.1f}" if growth >= 0 else f"{growth:.1f}"

        table.add_row(
            str(pid),
            name,
            f"{current:.1f}",
            Text(growth_text, style=growth_style),
            status,
        )

    return table


def build_header(top_n: int, interval: int) -> Panel:
    return Panel(
        Text.assemble(
            ("Smart Memory Leak Detector\n", "bold cyan"),
            (
                f"Tracking top {top_n} processes every {interval}s · "
                f"Leak = +{LEAK_THRESHOLD_MB}MB over {LEAK_WINDOW} snapshots",
                "dim",
            ),
        ),
        border_style="bright_blue",
        padding=(0, 1),
    )


def build_screen(header: Panel, table: Table, footer: Text) -> Panel:
    # Panel.fit prevents the full-screen blank area you’re seeing.
    return Panel.fit(
        Group(
            header,
            Panel(
                table,
                border_style="bright_blue",
                subtitle=footer,
                subtitle_align="left",
                padding=(0, 1),
            ),
        ),
        border_style="bright_blue",
        padding=0,
    )


def monitor(top_n: int = 15, interval: int = SNAPSHOT_INTERVAL):
    snapshots: dict[int, list[float]] = defaultdict(list)
    growth_streak: dict[int, int] = defaultdict(int)

    header = build_header(top_n, interval)

    # screen=False => no alternate buffer, no “full screen frame”, no giant empty bottom area.
    # transient=True => clears the last rendered frame when you quit.
    with Live(console=console, refresh_per_second=4, screen=False, transient=True) as live:
        while True:
            procs = sorted(
                psutil.process_iter(["pid", "memory_info", "name"]),
                key=lambda p: p.info["memory_info"].rss if p.info.get("memory_info") else 0,
                reverse=True,
            )[:top_n]

            active_pids: set[int] = set()

            for proc in procs:
                pid = proc.pid
                mem = get_process_memory(pid)
                if mem is None:
                    continue

                active_pids.add(pid)
                history = snapshots[pid]

                if history and mem > history[-1]:
                    growth_streak[pid] += 1
                else:
                    growth_streak[pid] = 0

                history.append(mem)
                if len(history) > 20:
                    history.pop(0)

            for pid in list(snapshots.keys()):
                if pid not in active_pids:
                    snapshots.pop(pid, None)
                    growth_streak.pop(pid, None)

            leaks = [pid for pid, s in growth_streak.items() if s >= LEAK_WINDOW]
            table = build_table(snapshots, growth_streak)

            footer = (
                Text(f"LEAK DETECTED: PIDs {leaks}", style="bold red")
                if leaks
                else Text(
                    f"Last check: {datetime.now().strftime('%H:%M:%S')} — No leaks detected",
                    style="dim",
                )
            )

            live.update(build_screen(header, table, footer))
            time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Smart Process Memory Leak Detector")
    parser.add_argument("-n", "--top", type=int, default=15, help="Number of processes to monitor")
    parser.add_argument("-i", "--interval", type=int, default=SNAPSHOT_INTERVAL, help="Check interval seconds")
    args = parser.parse_args()

    try:
        monitor(top_n=args.top, interval=args.interval)
    except KeyboardInterrupt:
        console.print("[bold yellow]Monitoring stopped.[/bold yellow]")


if __name__ == "__main__":
    main()
