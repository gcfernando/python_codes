# Send a Scheduled WhatsApp Message with Python — pywhatkit Example

A short Python script that shows **how to schedule and send a WhatsApp message from Python** with the `pywhatkit` library, which automates WhatsApp Web in your browser.

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
| `phone_number` | Recipient's phone number in international format, starting with `+` and the country code | `"+46123456789"` |
| `message` | Text of the message to send | `"Hello from Python!"` |
| `hour` | Hour to send the message (24-hour format) | `21` |
| `min` | Minute to send the message | `5` |

## Usage

From the `Cosole_Code` folder:

```bash
python WhatAppMessage.py
```

The script will wait until the specified time, then open WhatsApp Web and send the message automatically.

## How It Works

In `pywhatkit` 5.4, `sendwhatmsg`:

1. Checks that the number contains a `+` country code (otherwise it raises `CountryCodeException`).
2. Calculates the time until the scheduled minute and sleeps until 15 seconds before it (`wait_time=15`).
3. Opens a WhatsApp Web chat link in your **default browser**, waits for it to load, clicks the centre of the screen, and presses **Enter** with `pyautogui`.
4. With `tab_close=True`, closes the tab a few seconds after sending.

Because it simulates mouse and keyboard input, keep the computer unlocked, the browser window visible, and avoid typing while it sends. The scheduled time must be at least 15 seconds in the future; a time that has already passed today is treated as that time tomorrow.

## File Structure

```
Simple WhatApp Sender/
└── Cosole_Code/
    └── WhatAppMessage.py    # Main script
```

## Notes

- WhatsApp Web must be logged in before the scheduled send time.
- Phone number format: include the country code with `+` (e.g., `+46` for Sweden, `+1` for USA).
- Only send messages to people who expect them; automated bulk messaging can breach WhatsApp's terms of service.

## Related Projects

- [Use Twilio — send SMS and WhatsApp messages through an API](../Use%20Twilio/readme.md)
- [Simple Selenium Scraper — browser automation](../Simple%20Selenium%20Scraper/readme.md)
- [Back to all Python projects](../README.md)
