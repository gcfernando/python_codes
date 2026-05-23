# Remove Background

Removes the background from an image and replaces it with a solid black backdrop using `rembg` and Pillow.

## Overview

This script takes an input image, removes its background using the AI-powered `rembg` library, and composites the foreground onto a solid black canvas. The result is saved as a new image file.

## Features

- Automatic background removal using `rembg` (powered by U²-Net deep learning model)
- Composites the transparent result onto a solid black background
- Accepts any image format supported by Pillow as input
- Output saved as a separate file (original is preserved)

## Requirements

```
rembg
Pillow
```

Install dependencies:

```bash
pip install rembg Pillow
```

> On first run, `rembg` will download the U²-Net model (~170 MB). This only happens once.

## Usage

Open `Remove.py` and set the input and output file paths:

```python
orginal_image = 'path/to/input.jpg'
output_image  = 'path/to/output.jpg'
```

Then run the script:

```bash
python Remove.py
```

The processed image will be saved at the output path.

## How It Works

1. The input image is opened and converted to PNG bytes (required by `rembg`).
2. `rembg.remove()` applies the background removal model.
3. The resulting RGBA image (with transparent background) is pasted onto a new black RGB canvas.
4. The final image is saved to the output path.

## File Structure

```
Remove Background/
└── Console_Code/
    └── Remove.py    # Main script
```

## Notes

- The output background color is currently set to black. Change `'black'` to `'white'` or any other color in `Image.new('RGB', result_img.size, 'black')` to use a different background.
- `rembg` works best on images with clear subject-background contrast.
