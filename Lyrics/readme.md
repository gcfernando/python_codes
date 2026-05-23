# Lyrics

Fetches and displays song lyrics from the Genius music database using the `lyricsgenius` library.

## Overview

This script searches for a song by title and artist name using the Genius API, cleans the retrieved lyrics by stripping section headers (e.g., `[Verse 1]`), and prints the song's metadata along with a preview of the lyrics (up to 1,000 characters).

## Features

- Searches the Genius database by song title and artist name
- Removes section headers (e.g., `[Chorus]`, `[Bridge]`) from lyrics using regex
- Displays song title, artist, album, and a 1,000-character lyrics preview
- Skips remixes and live recordings via `excluded_terms`
- Suppresses non-song results using `skip_non_songs`

## Requirements

```
lyricsgenius
```

Install the dependency:

```bash
pip install lyricsgenius
```

## Configuration

Open `Lyrics.py` and update the following variables:

| Variable | Description |
|---|---|
| `genius` API token | Replace the token string with your own Genius API token |
| `song_title` | The title of the song to search for |
| `artist_name` | The artist's name |

To get a Genius API token, register at [genius.com/developers](https://genius.com/developers) and create a new API client.

## Usage

```bash
python Lyrics.py
```

### Example Output

```
🎵 Title: Sapphire
🎤 Artist: Ed Sheeran
💿 Album: Shivers (Single)

🎶 Lyrics:

Life is beautiful, standing on the edge...
```

## File Structure

```
Lyrics/
└── Console_Code/
    └── Lyrics.py    # Main script
```

## Notes

- The API token in the script is a placeholder and should be replaced with your own.
- The Genius free API tier has rate limits. If you hit them, the search may return `None`.
- Only the first 1,000 characters of the lyrics are printed in the current implementation.
