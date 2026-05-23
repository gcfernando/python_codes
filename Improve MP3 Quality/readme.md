# Improve MP3 Quality

A command-line tool for re-encoding MP3 files with custom bitrate, channel mode, and sample frequency settings.

## Overview

This script uses `pydub` (backed by FFmpeg) to re-encode one or more MP3 files. The original file is replaced in-place with the optimized version. ID3 tags from the original file are preserved in the output. It can process a single MP3 file or an entire folder of MP3s in one run.

## Features

- Process a single MP3 file or a whole folder at once
- 7 bitrate options: `32k`, `64k`, `96k`, `128k`, `192k`, `256k`, `320k`
- 4 channel modes: `mono`, `stereo`, `joint_stereo`, `dual_mono`
- 11 sample rate options: `8000` Hz to `192000` Hz
- ID3 tags are read from the original and written to the re-encoded output
- Original file is replaced in-place after encoding

## Requirements

```
pydub
```

You also need **FFmpeg** installed and available on your system PATH.

Install the Python dependency:

```bash
pip install pydub
```

Install FFmpeg:

- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

## Usage

```bash
python QualityModifier.py
```

The script prompts for:

1. **File or folder path** — path to a single `.mp3` file or a folder containing `.mp3` files
2. **Bitrate** — one of: `32k`, `64k`, `96k`, `128k`, `192k`, `256k`, `320k`
3. **Mode** — one of: `mono`, `stereo`, `joint_stereo`, `dual_mono`
4. **Frequency (Hz)** — one of: `8000`, `11025`, `12000`, `16000`, `22050`, `24000`, `32000`, `44100`, `48000`, `96000`, `192000`

### Example Session

```
Enter the file path or folder path: C:\Music\album

BitRates (Kbps) => 32k, 64k, 96k, 128k, 192k, 256k, 320k
Select BitRate (Kbps): 320k

Modes => mono, stereo, joint_stereo, dual_mono
Select Mode: stereo

Frequencies => 8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000, 96000, 192000
Select Frequency: 44100

song1.mp3 successfully optimized
song2.mp3 successfully optimized
```

## File Structure

```
Improve MP3 Quality/
├── Common/
├── Console_Code/
│   └── QualityModifier.py    # Main script
└── GUI_Code/
```

## Notes

- The original file is overwritten. Back up your files before running if needed.
- Only `.mp3` files are processed when a folder path is given.
- The `libmp3lame` encoder is used for all output files.
