# Send SMS and WhatsApp Messages and Make Calls with Python and Twilio

A command-line Python client that shows **how to send an SMS, send a WhatsApp message, and place a voice call with the Twilio API**, using the official `twilio` package.

## Overview

This script wraps the Twilio REST API into a `TwilioService` class with three communication methods. It runs an interactive loop that lets you choose the communication type, enter a recipient's phone number, and type a message.

## Features

- Send SMS messages to any phone number
- Send WhatsApp messages via Twilio's WhatsApp Business API
- Make voice calls using a TwiML URL
- Interactive console loop for repeated use

## Requirements

```
twilio
```

Install the dependency:

```bash
pip install twilio
```

## Configuration

Open `SendSMS.py` and replace the placeholder credentials with your actual Twilio account details (the committed file contains masked placeholder values):

```python
twilio_service = TwilioService(
    account_sid='YOUR_ACCOUNT_SID',
    auth_token='YOUR_AUTH_TOKEN',
    twilio_phone_number='+1XXXXXXXXXX',
    twilio_whatsapp_number='+1XXXXXXXXXX'
)
```

You can find these values in your [Twilio Console](https://console.twilio.com/). Do not commit real credentials; in your own copy, read them from environment variables such as `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`.

## Usage

From the `Console_Code` folder:

```bash
python SendSMS.py
```

### Interactive Prompt

```
Enter option (0, 1, 2) : 0       → Send SMS
Enter option (0, 1, 2) : 1       → Send WhatsApp message
Enter option (0, 1, 2) : 2       → Make a voice call

Enter recipient phone number : +46123456789
Enter message : Hello from Python!
```

| Option | Action |
|---|---|
| `0` | Send an SMS |
| `1` | Send a WhatsApp message |
| `2` | Make a voice call (uses a Twilio demo TwiML URL) |

## How It Works

- **SMS:** Sends via `client.messages.create(from_=twilio_phone_number, to=recipient, body=message)`
- **WhatsApp:** Sends via `client.messages.create(from_='whatsapp:...', to='whatsapp:...', body=message)`
- **Voice call:** Creates a call via `client.calls.create(url=twiml_url, from_=..., to=...)`

## File Structure

```
Use Twilio/
└── Console_Code/
    └── SendSMS.py    # Main script
```

## Notes

- The voice call option uses `http://demo.twilio.com/docs/voice.xml` as the TwiML URL, which plays a Twilio demo message.
- WhatsApp messaging requires a Twilio WhatsApp sender number approved through the Twilio console.
- Phone numbers must include the country code (e.g., `+1` for USA, `+44` for UK).
- The script asks for a message even for option `2`; the text is not used for voice calls. Any option other than `0` or `1` places a call.
- The loop runs until you press `Ctrl+C`, and it clears the screen with `cls` (Windows) at the start of each round.
- The option prompt is read with `eval(input(...))`, which executes whatever is typed as Python code. Run it only on your own machine, or change it to `int(input(...))`.
- Twilio trial accounts can only send to verified numbers, and messages and calls are billed to your Twilio account.

## Related Projects

- [Simple WhatsApp Sender — WhatsApp Web automation](../Simple%20WhatApp%20Sender/readme.md)
- [Back to all Python projects](../README.md)
