# Extract CPU Information

Retrieves and displays detailed information about the system's CPU using Python.

## Overview

This script uses the `psutil` and `py-cpuinfo` libraries to gather and print CPU details to the console, including brand name, architecture, clock speed, core counts, and an estimated temperature.

## Features

- CPU brand name and architecture
- cpuinfo version string
- Actual clock frequency (human-readable)
- Number of physical cores
- Number of logical cores (including hyper-threaded)
- Estimated temperature in °C (derived from current frequency)

## Requirements

```
psutil
py-cpuinfo
```

Install dependencies:

```bash
pip install psutil py-cpuinfo
```

## Usage

```bash
python CPU.py
```

### Example Output

```
Processor Info
    Brand            : Intel(R) Core(TM) i7-10750H CPU @ 2.60GHz
    Architecture     : X86_64
    Version          : cpuinfo-9.0.0
    Actucal Hz       : 2.6000 GHz
    Physical Cores   : 6
    Logical Cores    : 12
    Temperature      : 41.0°C
```

## Notes

- Temperature is estimated based on the current CPU frequency (`freq / 100 + 15`). It is not a hardware sensor reading.
- `psutil` and `cpuinfo` support Windows, macOS, and Linux.

## File Structure

```
Extract CPU Information/
└── Console_Code/
    └── CPU.py    # Main script
```
