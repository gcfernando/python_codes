# Setup Wizard — Fruit Wiki

A GUI application that displays fruit images and information in a paginated viewer, built with PySimpleGUI and Pillow. The project is packaged for distribution using PyInstaller.

## Overview

Fruit Wiki is a simple desktop encyclopedia for fruits. It reads image files from an `Images/` folder and matching text files from a `Data/` folder, then displays them side by side in a centered window. Users can browse entries using Previous and Next buttons.

## Features

- Paginated image viewer with Previous / Next navigation
- Loads images (`.png`, `.jpg`, `.jpeg`) from an `Images/` folder
- Reads corresponding description text from a `Data/` folder (matched by filename)
- Images are automatically resized to fit a 300×300 display area
- Custom font loaded from a `Fonts/` folder (`Futura.ttf`)
- Dark teal theme (`DarkTeal10`)
- Resource paths resolved correctly for both development and PyInstaller bundles

## Requirements

```
PySimpleGUI
Pillow
pyglet
pyinstaller
```

Install dependencies:

```bash
pip install PySimpleGUI Pillow pyglet pyinstaller
```

## Folder Structure (at Runtime)

The application expects the following structure relative to the executable or script:

```
SetupWizard/
├── GUI_Code/
│   └── fruitWiki.py    # Main application
├── Fonts/
│   └── Futura.ttf      # Custom font
├── Images/
│   ├── apple.png       # Fruit images
│   └── banana.jpg
└── Data/
    ├── apple.txt       # Matching text description for apple.png
    └── banana.txt
```

Each `.txt` file in `Data/` must have the same base name as its matching image file.

## Usage

### Running the script directly

```bash
python GUI_Code/fruitWiki.py
```

### Building a standalone executable with PyInstaller

```bash
pyinstaller --onefile --windowed GUI_Code/fruitWiki.py
```

The generated `.exe` can be distributed as a standalone installer. Bundle the `Fonts/`, `Images/`, and `Data/` folders alongside it.

## Notes

- The `resource_path()` function ensures the app finds its assets whether run from source or as a PyInstaller bundle.
- Sentence formatting is applied to description text: periods followed by a space are replaced with a newline.
- The Delete button is disabled when viewing the first entry; the Next button is disabled on the last.
