# Convert an Image to ASCII Art in Python — pywhatkit Example

A short Python script that **converts an image into ASCII art** and saves it as a text file, using `pywhatkit.image_to_ascii_art`.

## Overview

This script uses the `pywhatkit` library to transform any image into a text-based ASCII art representation. The output is saved as a `.txt` file at a path you specify in the script.

## Requirements

```
pywhatkit
```

Install the dependency:

```bash
pip install pywhatkit
```

## Usage

Open `ImageToText.py` and update the input and output paths:

```python
image_path = 'path/to/your/image.jpeg'
text_path  = 'path/to/output'
```

`pywhatkit` adds the `.txt` extension itself, so give `text_path` **without** an extension. (The script currently uses a value ending in `.txt`, which produces a file ending in `.txt.txt`.)

Then run the script:

```bash
python ImageToText.py
```

The ASCII art will be written to the specified text file.

## How It Works

In `pywhatkit` 5.4, `image_to_ascii_art` converts the image to grayscale with Pillow, resizes it to 80 characters wide (with the height scaled for character proportions), maps each pixel's brightness to one of 11 characters, and writes the result to `<output_file>.txt`.

> Importing `pywhatkit` also loads its WhatsApp, browser-automation (`pyautogui`), and other helpers, so it installs several extra dependencies. For ASCII art alone, a few lines of Pillow code would do the same job.

## File Structure

```
Image to ASCII/
└── Console_Code/
    └── ImageToText.py    # Main script
```

## Related Projects

- [Photo to graphite pencil sketch CLI](../Graphite_CLI/README.md)
- [Image2Cartoon — cartoon effect with OpenCV](../Image2Cartoon/readme.md)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
