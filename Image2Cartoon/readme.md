# Cartoonify an Image with Python and OpenCV — Image2Cartoon

A short Python script that shows **how to cartoonify a photo with OpenCV**: median blur, adaptive-threshold edge detection, and a bilateral filter are combined to turn a regular photograph into a cartoon-style image.

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

The result is only displayed, not saved. To keep it, add `cv2.imwrite('cartoon.jpg', cartoon_image)` after the conversion.

## Tips

- Both images are resized to a fixed 500×500, which stretches photos that are not square. Resize by a scale factor instead to keep the aspect ratio.
- `cv2.adaptiveThreshold(..., 9, 9)` controls edge detection (block size and constant); `cv2.bilateralFilter(image, 9, 250, 250)` controls how flat the colour areas become. Adjust them to make lines thicker or colours smoother.

## File Structure

```
Image2Cartoon/
└── Console_Code/
    └── CartoonImage.py    # Main script
```

## Related Projects

- [Photo to graphite pencil sketch CLI](../Graphite_CLI/README.md)
- [Remove Background](../Remove%20Background/readme.md)
- [Image to ASCII](../Image%20to%20ASCII/readme.md)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
