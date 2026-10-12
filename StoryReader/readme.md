# Read a PDF Aloud with Python — PyPDF2 and pyttsx3 Offline Text-to-Speech

A short Python script that **reads a PDF aloud**, page by page: it extracts the text with `PyPDF2` and speaks it with `pyttsx3`, which uses your operating system's built-in (offline) text-to-speech voices.

## Overview

This script extracts text from a PDF file using `PyPDF2` and converts it to speech using `pyttsx3`. It reads each page sequentially, with a brief pause between pages for natural pacing. A preferred voice (female by default) is selected automatically if available.

## Features

- Reads all pages of a PDF aloud using the system's text-to-speech engine
- Tries to select a voice whose name or ID contains "female" (see the note on voice selection below)
- Configurable reading speed (words per minute) and volume
- Prints progress to the console as each page is read
- Short pause between pages for a more natural listening experience
- Error handling for missing files and unexpected issues

## Requirements

```
PyPDF2
pyttsx3
```

Install dependencies:

```bash
pip install PyPDF2 pyttsx3
```

## Usage

`Story.pdf` is not included in the repository. Place your own PDF named `Story.pdf` in the folder you run the script from (or update the path), then run:

```bash
python StoryReader.py
```

The default configuration reads `Story.pdf` with a female voice at speed 150 and volume 0.9.

### Changing the PDF File

Update the file path in the `__main__` block:

```python
read_pdf_aloud("path/to/your/file.pdf", voice_id=chosen_voice, rate=150, volume=0.9)
```

### Parameters

| Parameter | Default | Description |
|---|---|---|
| `file_path` | `"Story.pdf"` | Path to the PDF file |
| `voice_id` | Female voice (auto-selected) | System voice ID |
| `rate` | `150` | Speaking speed in words per minute |
| `volume` | `0.9` | Volume level (0.0 to 1.0) |

## File Structure

```
StoryReader/
└── Console_Code/
    └── StoryReader.py    # Main script
```

## Notes

- `pyttsx3` uses the operating system's built-in TTS engine (SAPI5 on Windows, NSSpeechSynthesizer on macOS, eSpeak on Linux).
- Pages with no extractable text are silently skipped.
- Press `Ctrl+C` to interrupt playback.
- `PyPDF2` is no longer developed under that name; its successor is `pypdf`, which provides the same `PdfReader` class.

### Voice selection

`select_voice` looks for the word "female" in each installed voice's name or ID. Standard Windows voice names such as "Microsoft Zira Desktop" do not contain that word, so the function usually falls back to `voices[1]`, the second installed voice. On a default English (US) Windows installation, that is typically Zira. If only one voice is installed, `voices[1]` raises an `IndexError`; change the fallback to `voices[0]` or pass a specific voice ID.

## Related Projects

- [Text2Audio — Google text-to-speech desktop app](../Text2Audio/readme.md)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
