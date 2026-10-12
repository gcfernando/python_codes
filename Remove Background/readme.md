# Remove Image Background in Python with rembg — AI Background Removal Example

A short Python script that shows **how to remove the background from an image in Python** using the AI-based `rembg` library, then places the subject on a solid black background with Pillow.

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

By default the script processes the included sample image `Elephant.jpg` and writes `Elephant_Modified.jpg`, so you can try it straight away from the `Console_Code` folder:

```bash
python Remove.py
```

To use your own image, set the input and output paths in `Remove.py`:

```python
orginal_image = 'path/to/input.jpg'
output_image  = 'path/to/output.jpg'
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
    ├── Remove.py      # Main script
    └── Elephant.jpg   # Sample input image
```

## Notes

- The output background color is currently set to black. Change `'black'` to `'white'` or any other color in `Image.new('RGB', result_img.size, 'black')` to use a different background.
- `rembg` works best on images with clear subject-background contrast.
- To keep a transparent background instead, save `result_img` (the RGBA image) as a `.png` file rather than compositing it onto a colour.
- The function's docstring and variable name mention a white background, but the code uses `'black'`.

## Related Projects

- [Image2Cartoon — cartoon effect with OpenCV](../Image2Cartoon/readme.md)
- [Photo to graphite pencil sketch CLI](../Graphite_CLI/README.md)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
