# Internet Speed Test

Measures your internet connection's download speed, upload speed, and ping using the Speedtest.net infrastructure.

## Overview

This script connects to the best available Speedtest.net server, runs a full speed test, and prints the results to the console. All speeds are reported in Mbps.

## Features

- Automatically selects the best available test server
- Measures download speed (Mbps)
- Measures upload speed (Mbps)
- Reports ping latency (ms)
- Displays the selected server's host, country, and sponsor

## Requirements

```
speedtest-cli
```

Install the dependency:

```bash
pip install speedtest-cli
```

## Usage

```bash
python SpeedTest.py
```

### Example Output

```
Loading servers
Calulating download speed...
Calulating upload speed...
Calulating ping result...

Choose best server example.server.net located at United States Sponsor by Example ISP
Download    : 95.42 Mbps
Upload      : 48.17 Mbps
Ping        : 12.34 ms
```

## File Structure

```
Internet Speed Test/
└── Console_Code/
    └── SpeedTest.py    # Main script
```
