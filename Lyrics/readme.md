# Get Song Lyrics with Python and the Genius API — lyricsgenius Example

A short Python script that **searches the Genius API for a song** with the `lyricsgenius` library and prints its title, artist, album, and a lyrics preview.

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

From the `Console_Code` folder:

```bash
python Lyrics.py
```

### Output Format

```
🎵 Title: <song title>
🎤 Artist: <artist>
💿 Album: <album full title>

🎶 Lyrics:

<first 1,000 characters of the lyrics>...
```

If no match is found, the script prints `Song not found.`

## File Structure

```
Lyrics/
└── Console_Code/
    └── Lyrics.py    # Main script
```

## Related Projects

- [MP3 Tags — read ID3 metadata](../MP3%20Tags/readme.md)
- [MP3 Player with crossfade](../MP3%20Player/readme.md)
- [Back to all Python projects](../README.md)

## Notes

- Use your own Genius API token. Do not commit a real token to source control — read it from an environment variable instead, for example `lyricsgenius.Genius(os.environ["GENIUS_ACCESS_TOKEN"])`.
- `song.album` can be `None` for songs without an album on Genius, which would make the `song.album.full_title` line fail.
- The Genius free API tier has rate limits. If you hit them, the search may return `None`.
- Only the first 1,000 characters of the lyrics are printed in the current implementation.
