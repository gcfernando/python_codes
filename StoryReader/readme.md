# Story Reader

Reads a PDF document aloud using text-to-speech, page by page.

## Overview

This script extracts text from a PDF file using `PyPDF2` and converts it to speech using `pyttsx3`. It reads each page sequentially, with a brief pause between pages for natural pacing. A preferred voice (female by default) is selected automatically if available.

## Features

- Reads all pages of a PDF aloud using the system's text-to-speech engine
- Automatically selects a female voice if one is available (falls back to default otherwise)
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

Place your PDF file in the same directory as the script (or update the path), then run:

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
