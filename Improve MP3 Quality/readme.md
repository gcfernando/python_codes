# Re-encode MP3 Files in Python — Change Bitrate, Channels and Sample Rate with pydub

A command-line tool written in Python that **re-encodes MP3 files** with a chosen bitrate, channel option, and sample rate using `pydub` and FFmpeg (`libmp3lame`), for a single file or a whole folder.

> Re-encoding cannot add detail that a lower-quality MP3 has already lost; a higher bitrate mainly makes the file larger. Use it to standardize settings or reduce file size.

## Overview

This script uses `pydub` (backed by FFmpeg) to re-encode one or more MP3 files. The original file is replaced in-place with the optimized version. ID3 tags from the original file are preserved in the output. It can process a single MP3 file or an entire folder of MP3s in one run.

## Features

- Process a single MP3 file or a whole folder at once
- 7 bitrate options: `32k`, `64k`, `96k`, `128k`, `192k`, `256k`, `320k`
- 4 channel options: `mono`, `stereo`, `joint_stereo`, `dual_mono` (see [Channel options](#channel-options))
- 11 sample rate options: `8000` Hz to `192000` Hz
- ID3 tags are read from the original and written to the re-encoded output
- Original file is replaced in-place after encoding

## Requirements

```
pydub
```

You also need **FFmpeg** installed and available on your system PATH. Windows builds of `ffmpeg.exe`, `ffplay.exe`, and `ffprobe.exe` are included in the `Common/` folder, but the script does not point `pydub` at them automatically — add that folder to your PATH or install FFmpeg separately.

Install the Python dependency:

```bash
pip install pydub
```

Install FFmpeg:

- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

## Usage

From the `Console_Code` folder:

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

## Channel options

The channel options are applied by `pydub` before encoding; they are not LAME's joint-stereo or dual-channel encoder modes:

| Option | What the script does |
|---|---|
| `mono` | Converts stereo input to one channel |
| `stereo` | Keeps the existing channels |
| `joint_stereo` | Mono input becomes two channels; stereo input is remixed by overlaying the left and right channels with panning onto a silent base track |
| `dual_mono` | Mono input becomes two channels; stereo input keeps **one randomly chosen channel**, so the output is mono |

## File Structure

```
Improve MP3 Quality/
├── Common/
│   ├── ffmpeg.exe            # Bundled Windows FFmpeg binaries
│   ├── ffplay.exe
│   └── ffprobe.exe
└── Console_Code/
    └── QualityModifier.py    # Main script
```

## Notes

- The original file is overwritten. Back up your files before running if needed.
- Only `.mp3` files are processed when a folder path is given.
- The `libmp3lame` encoder is used for all output files.
- Each file is first written to `<name>_temp.mp3` and then moved over the original with `os.replace`.

## Related Projects

- [MP3 Tags — read ID3 metadata](../MP3%20Tags/readme.md)
- [MP3 Player with crossfade](../MP3%20Player/readme.md)
- [Audio8D — FFmpeg 8D audio converter](https://github.com/gcfernando/audio-8d)
- [Back to all Python projects](../README.md)
