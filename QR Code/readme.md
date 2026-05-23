# QR Code

Generates a custom QR code image using Python and saves it as a PNG file.

## Overview

This script uses the `qrcode` library to create a QR code that encodes a LinkedIn profile URL. The QR code is styled with a dark blue fill on a light gray background and saved to `profile.png`.

## Features

- Encodes any text or URL into a QR code
- Configurable box size and border width
- Custom fill and background colors
- Output saved as a PNG image

## Requirements

```
qrcode[pil]
```

Install the dependency:

```bash
pip install "qrcode[pil]"
```

> The `[pil]` extra installs Pillow, which is required for image generation.

## Usage

Open `qr_code.py` and update the `data` variable with your desired content:

```python
data = 'Your text or URL here'
```

Then run the script:

```bash
python qr_code.py
```

A file named `profile.png` will be created in the working directory.

## Configuration

| Parameter | Value | Description |
|---|---|---|
| `version` | `1` | QR code complexity (1–40; 1 is smallest) |
| `box_size` | `15` | Pixel size of each box in the QR code |
| `border` | `5` | Width of the quiet zone border (in boxes) |
| `fill_color` | `'darkblue'` | Color of the QR code modules |
| `back_color` | `'lightgray'` | Background color |

## File Structure

```
QR Code/
└── Console_Code/
    └── qr_code.py    # Main script
```
