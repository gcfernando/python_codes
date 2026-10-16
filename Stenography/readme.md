# Image Steganography in Python — Hide Text in a PNG with LSB (stegano)

A short Python example of **image steganography**: it hides a secret text message inside a PNG image using LSB (Least Significant Bit) encoding with the `stegano` library, then reads the message back. (The folder is named `Stenography`; the technique is steganography.)

## Overview

This script uses the `stegano` library's LSB (Least Significant Bit) method to embed a hidden text string into the pixel data of a PNG image. The modified image looks identical to the original, but contains the concealed message. The script also demonstrates how to extract (reveal) the hidden message from the output image.

## What Is Steganography?

Steganography is the practice of hiding information within another file in a way that is not easily detectable. Unlike encryption, it conceals the *existence* of the message rather than scrambling its content. LSB steganography works by replacing the least significant bit of each pixel's color value with bits from the hidden message — a change imperceptible to the human eye.

## Features

- Hides an arbitrary text message inside a PNG image using LSB steganography
- Saves the resulting image to a new file (original is not modified)
- Extracts and prints the hidden message from the output image

## Requirements

```text
stegano
```

Install the dependency:

```bash
pip install stegano
```

## Usage

Open `HideTextInImage.py` and update the file paths:

```python
original_image = 'path/to/input.png'
output_image   = 'path/to/output_secret.png'
```

Also update `hidden_text` with the message you want to embed.

Then run the script from the `Console_Code` folder:

```bash
python HideTextInImage.py
```

The script will:
1. Hide the text in the image and save the result
2. Immediately read back and print the hidden message to confirm it worked

## File Structure

```text
Stenography/
└── Console_Code/
    └── HideTextInImage.py    # Main script
```

## Notes

- Only **PNG images** are supported. JPEG compression would destroy the hidden data.
- The carrier image must be large enough to hold the message (more pixels = more capacity).
- The output image is visually identical to the input.
- Steganography hides that a message exists but does not encrypt it — anyone who runs `lsb.reveal()` on the image can read the text. Encrypt the message first if it must stay confidential.

## Related Projects

- [QR Code generator](../QR%20Code/readme.md)
- [Password Generator and Strength Checker](../Password%20Utility/readme.md)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
