# PySimpleGUI Image Viewer with PyInstaller Packaging — Fruit Wiki (Python)

A Python desktop GUI that displays fruit images and descriptions in a paginated viewer, built with **PySimpleGUI** and **Pillow**, with a `resource_path()` helper that makes bundled assets work when the app is packaged into a Windows executable with **PyInstaller**.

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

```text
PySimpleGUI
Pillow
pyglet
pyinstaller
```

Install dependencies:

```bash
pip install PySimpleGUI Pillow pyglet pyinstaller
```

## Folder Structure

```text
SetupWizard/
└── GUI_Code/
    ├── fruitWiki.py    # Main application
    ├── icon.ico        # Application icon
    ├── Fonts/
    │   └── Futura.ttf  # Custom font
    ├── Images/         # Apple, Banana, Cherry, Grapes, Mango, Papaya (.png)
    └── Data/           # Matching descriptions (Apple.txt, Banana.txt, ...)
```

Each `.txt` file in `Data/` must have the same base name as its matching image file. Six fruits are included.

## Usage

### Running the script directly

When not packaged, `resource_path()` resolves `Fonts`, `Images`, and `Data` relative to the **current working directory**, so run the script from the `GUI_Code` folder:

```bash
cd GUI_Code
python fruitWiki.py
```

### Building a standalone executable with PyInstaller

In a one-file build, `resource_path()` looks for assets in PyInstaller's temporary extraction folder (`sys._MEIPASS`), so the asset folders must be bundled into the executable with `--add-data` (on Windows the separator is `;`). From the `GUI_Code` folder:

```bash
pyinstaller --onefile --windowed --icon icon.ico --add-data "Fonts;Fonts" --add-data "Images;Images" --add-data "Data;Data" fruitWiki.py
```

The executable is created in `dist/`.

## Notes

- The `resource_path()` function ensures the app finds its assets whether run from source or as a PyInstaller bundle.
- Sentence formatting is applied to description text: periods followed by a space are replaced with a newline.
- The Previous button is disabled when viewing the first entry; the Next button is disabled on the last.
- The custom font is registered with `pyglet.font.add_file`, which is why `pyglet` is a dependency.
- PySimpleGUI's licensing changed with version 5. Check the current PySimpleGUI terms before installing, or use FreeSimpleGUI, a community fork of the version 4 API.

## Related Projects

- [Text2Audio — customtkinter text-to-speech app](../Text2Audio/readme.md)
- [Contact Book — ttkbootstrap and SQL Server](../GUI_Apps/README.md)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
