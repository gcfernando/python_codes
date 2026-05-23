# Simple WhatsApp Sender

Sends a scheduled WhatsApp message to a phone number at a specified time using the `pywhatkit` library.

## Overview

This script automates sending a WhatsApp message via WhatsApp Web. It opens the WhatsApp Web interface in a browser at the scheduled time and sends the message automatically.

## Features

- Sends a WhatsApp message to any phone number with a country code
- Schedules the message for a specific hour and minute (24-hour format)
- Automatically closes the browser tab after sending (`tab_close=True`)

## Requirements

```
pywhatkit
```

Install the dependency:

```bash
pip install pywhatkit
```

> WhatsApp Web must be open and logged in in your default browser before running the script. The script will open a new tab when it is time to send.

## Configuration

Open `WhatAppMessage.py` and update the following variables:

| Variable | Description | Example |
|---|---|---|
| `phone_number` | Recipient's phone number with country code, no `+` or leading `0` | `"+46123456789"` |
| `message` | Text of the message to send | `"Hello from Python!"` |
| `hour` | Hour to send the message (24-hour format) | `21` |
| `min` | Minute to send the message | `5` |

## Usage

```bash
python WhatAppMessage.py
```

The script will wait until the specified time, then open WhatsApp Web and send the message automatically.

## File Structure

```
Simple WhatApp Sender/
└── Cosole_Code/
    └── WhatAppMessage.py    # Main script
```

## Notes

- WhatsApp Web must be logged in before the scheduled send time.
- The `pywhatkit` library controls Chrome via keyboard automation, so do not interact with the browser while it is sending.
- Phone number format: include the country code with `+` (e.g., `+46` for Sweden, `+1` for USA).
