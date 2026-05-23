# Health Monitor

A real-time terminal dashboard for detecting memory leaks in running processes.

## Overview

Health Monitor continuously tracks the memory usage of the top processes on your system and flags any that show consistent upward growth — a common sign of a memory leak. The live dashboard refreshes every second and color-codes each process with a clear status indicator.

## Features

- Live terminal dashboard powered by the `rich` library
- Tracks the top N processes by memory usage
- Detects memory leaks by observing consistent growth over a rolling window of snapshots
- Three status levels per process:
  - **OK** — memory usage is stable
  - **WATCH** — memory is growing faster than usual
  - **LEAK** — memory has grown consistently across 10 or more consecutive snapshots
- Footer shows detected leak PIDs or a "no leaks" confirmation with a timestamp
- Configurable number of processes to track and check interval via command-line arguments

## Leak Detection Logic

| Parameter | Default | Description |
|---|---|---|
| Snapshot interval | 1 second | How often memory is sampled |
| Leak threshold | 50 MB | Growth amount that triggers WATCH status |
| Leak window | 10 snapshots | Consecutive growth snapshots required to trigger LEAK |

## Requirements

```
psutil
rich
```

Install dependencies:

```bash
pip install psutil rich
```

## Usage

```bash
# Run with defaults (top 15 processes, 1-second interval)
python health_monitor.py

# Monitor top 20 processes
python health_monitor.py --top 20

# Check every 5 seconds
python health_monitor.py --interval 5

# Combine options
python health_monitor.py -n 20 -i 5
```

### Arguments

| Argument | Short | Default | Description |
|---|---|---|---|
| `--top` | `-n` | 15 | Number of processes to display and track |
| `--interval` | `-i` | 1 | Seconds between each memory snapshot |

## Dashboard Columns

| Column | Description |
|---|---|
| PID | Process ID |
| Process Name | Name of the process |
| Current (MB) | Current resident memory usage in megabytes |
| Growth (MB) | Memory change since first snapshot in this session |
| Status | OK / WATCH / LEAK |

## File Structure

```
Health Monitor/
└── Console_Code/
    └── health_monitor.py    # Main script
```

## Notes

- Press `Ctrl+C` to stop monitoring. The dashboard is cleared on exit.
- Processes that exit mid-session are automatically removed from tracking.
- Processes that cannot be read (e.g., protected system processes) are silently skipped.
