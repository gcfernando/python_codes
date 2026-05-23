# Use Twilio

A command-line client for sending SMS messages, WhatsApp messages, and making voice calls via the Twilio REST API.

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

Open `SendSMS.py` and replace the placeholder credentials with your actual Twilio account details:

```python
twilio_service = TwilioService(
    account_sid='YOUR_ACCOUNT_SID',
    auth_token='YOUR_AUTH_TOKEN',
    twilio_phone_number='+1XXXXXXXXXX',
    twilio_whatsapp_number='+1XXXXXXXXXX'
)
```

You can find these values in your [Twilio Console](https://console.twilio.com/).

## Usage

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
