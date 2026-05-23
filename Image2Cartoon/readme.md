# Image2Cartoon

Converts a regular photograph into a cartoon-style image using OpenCV image processing techniques.

## Overview

This script applies a series of computer vision operations to transform an input image into a cartoon-like rendering. The original and cartoon images are displayed side by side for comparison.

## How It Works

The cartoon effect is produced in five steps:

1. **Grayscale conversion** — the image is converted from BGR to grayscale
2. **Median blur** — a 5×5 median blur reduces noise
3. **Edge detection** — adaptive mean thresholding identifies edges
4. **Bilateral filter** — the color image is smoothed while sharp edges are preserved
5. **Bitwise AND** — the smoothed color image is combined with the edge mask to produce the cartoon effect

The output is resized to 500×500 pixels.

## Requirements

```
opencv-python
```

Install the dependency:

```bash
pip install opencv-python
```

## Usage

Open `CartoonImage.py` and set the input image path:

```python
input_image_path = 'path/to/your/image.jpg'
```

Then run the script:

```bash
python CartoonImage.py
```

Two windows will open — one showing the original resized image and one showing the cartoon version. Press any key to close them.

## File Structure

```
Image2Cartoon/
└── Console_Code/
    └── CartoonImage.py    # Main script
```
