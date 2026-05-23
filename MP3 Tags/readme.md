# MP3 Tags

Reads and displays ID3 metadata and audio properties from an MP3 file using `eyed3`.

## Overview

This script loads an MP3 file, extracts its ID3 tag information and audio stream properties, and prints them to the console. It covers both tag metadata (title, artist, genre, etc.) and technical audio details (bitrate, sample rate, duration, channels).

## Features

Extracts and displays the following information:

**ID3 Tags:**
- Title
- Artist
- Album
- Album Artist
- Genre
- Track Number
- Year (only if present in metadata)

**Audio Stream Properties:**
- Sample rate (Hz)
- Bitrate (kbps)
- Duration (seconds)
- Channel mode (stereo, mono, etc.)

**File Information:**
- File size (MB)

## Requirements

```
eyed3
```

Install the dependency:

```bash
pip install eyed3
```

## Usage

Open `ReadMP3File.py` and update the file path:

```python
mp3_file_path = "path/to/your/audio.mp3"
```

Then run the script:

```bash
python ReadMP3File.py
```

### Example Output

```
Title: Bohemian Rhapsody
Artist: Queen
Album: A Night at the Opera
Album Artist: Queen
Genre: Rock
Track Number: (11, None)
Year: 1975
Sample Rate: 44100
Bitrate: 320 kbps
Duration: 354.32 seconds
Channels: Joint stereo
File Size: 14.23 MB
```

## File Structure

```
MP3 Tags/
└── Console_Code/
    └── ReadMP3File.py    # Main script
```

## Notes

- The file path is currently hardcoded in the script. Update it before running.
- Year is only printed if `getBestDate()` returns a valid date object.
