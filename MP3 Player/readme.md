# MP3 Player

A console-based MP3 player with seamless crossfade transitions, background preloading, and shuffle playback.

## Overview

This script plays all `.mp3` files from a folder you specify, in shuffled order, with smooth crossfade transitions between tracks. It uses `pygame`'s dual-channel mixer to overlap the end of one track with the start of the next, preventing any silence between songs. The next track is preloaded in a background thread so the transition is seamless.

## Features

- Shuffle playback of all `.mp3` files in a given folder
- Crossfade between tracks (configurable duration and trigger time)
- Background preloading of the next track via a daemon thread
- Animated "Playing..." indicator in the console
- Displays previous, current, and next track names with durations
- Console window title updated to show the currently playing track
- Windows sleep prevention (keeps the screen on while music plays)
- Graceful shutdown on playlist end or interrupt

## Configuration

Two constants in the script control the crossfade behavior:

| Constant | Default | Description |
|---|---|---|
| `CROSSFADE_MS` | `5000` | Duration of the fade effect in milliseconds (5 seconds) |
| `CROSSFADE_START_TIME_S` | `15` | How many seconds before a song ends to begin the crossfade |

## Requirements

```
pygame
mutagen
colorama
```

Install dependencies:

```bash
pip install pygame mutagen colorama
```

## Usage

```bash
python MP3Player.py
```

When prompted, enter the full path to your music folder:

```
Enter music folder path: C:\Music\Playlist
```

The player will shuffle the playlist, preload the first track, and begin playback automatically.

## How It Works

1. All `.mp3` files in the folder are discovered and shuffled.
2. The pygame mixer is initialized with two channels.
3. Before the main loop starts, the first track is preloaded in a background thread.
4. When a track is playing, a second background thread preloads the next one.
5. When `CROSSFADE_START_TIME_S` seconds remain, the inactive channel fades in the next track while the active channel fades out.
6. Channels swap roles after each transition.

## File Structure

```
MP3 Player/
├── Console_Code/
│   └── MP3Player.py    # Main script
└── GUI_Code/
```

## Notes

- Only `.mp3` files are supported.
- If a track fails to load, it is skipped and the next track loads.
- On non-Windows systems, sleep prevention and console title updates use ANSI escape codes.
