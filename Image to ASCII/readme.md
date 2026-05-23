# Image to ASCII

Converts an image file into ASCII art and saves the result to a text file.

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
text_path  = 'path/to/output.txt'
```

Then run the script:

```bash
python ImageToText.py
```

The ASCII art will be written to the specified text file.

## File Structure

```
Image to ASCII/
└── Console_Code/
    └── ImageToText.py    # Main script
```
