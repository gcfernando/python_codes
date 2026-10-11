# Generate a QR Code in Python — Custom Colours with the qrcode Library

A short Python script that shows **how to generate a QR code in Python** with the `qrcode` library, using custom fill and background colours and saving the result as a PNG image.

## Overview

This script uses the `qrcode` library to create a QR code that encodes a short text containing a LinkedIn profile address. The QR code is styled with a dark blue fill on a light gray background and saved to `profile.png`. A sample `profile.png` is included in the `Console_Code` folder.

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

Then run the script from the `Console_Code` folder:

```bash
python qr_code.py
```

To make the QR code open a website when scanned, encode a full URL including `https://`; plain text is shown as text by most scanner apps.

A file named `profile.png` will be created in the working directory.

## Configuration

| Parameter | Value | Description |
|---|---|---|
| `version` | `1` | Starting QR code size (1–40). Because `qr.make(fit=True)` is used, the version grows automatically if the data does not fit |
| `box_size` | `15` | Pixel size of each box in the QR code |
| `border` | `5` | Width of the quiet zone border (in boxes) |
| `fill_color` | `'darkblue'` | Color of the QR code modules |
| `back_color` | `'lightgray'` | Background color |

## File Structure

```
QR Code/
└── Console_Code/
    ├── qr_code.py    # Main script
    └── profile.png   # Sample output
```

## Related Projects

- [Steganography — hide text inside a PNG](../Stenography/readme.md)
- [Image to ASCII](../Image%20to%20ASCII/readme.md)
- [Back to all Python projects](../README.md)
