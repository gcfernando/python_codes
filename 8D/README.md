<!-- Developed by ::> Gehan Fernando -->
<div align="center">

# 🎧 Audio8D

### Turn your songs into music that moves around your head.

**Developed by Gehan Fernando**

<p>
<img src="https://img.shields.io/badge/version-1.0.0-1D5FD1?style=for-the-badge" alt="Version 1.0.0"/>
<img src="https://img.shields.io/badge/Windows-standalone%20app-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Standalone app for Windows"/>
<img src="https://img.shields.io/badge/listen%20with-headphones-111827?style=for-the-badge" alt="Listen with headphones"/>
</p>
<p>
<img src="https://img.shields.io/badge/saves-MP3%20%7C%20FLAC%20%7C%20WAV%20%7C%20M4A%20%7C%20Opus-555?style=flat-square" alt="Saves MP3, FLAC, WAV, M4A and Opus"/>
<img src="https://img.shields.io/badge/powered%20by-FFmpeg-007808?style=flat-square&logo=ffmpeg&logoColor=white" alt="Powered by FFmpeg"/>
</p>

</div>

**Audio8D turns normal music into a moving 3D headphone experience.** Add a song,
choose how you want it to sound, listen to a preview, and create the new audio file.
People call this effect **"8D audio"**: the music seems to travel past one ear, behind
you, past the other ear and back.

- **Who is it for?** Anyone with songs on their computer. You don't need to know
  anything about sound, music software or computers beyond opening a file.
- **Your songs are safe.** Audio8D always makes a **new** file. Your original song is
  not changed.
- **It uses FFmpeg**, a free and well-known sound program, to do the work. It is
  included; you don't install it yourself.

> [!IMPORTANT]
> 🎧 **Use headphones or earbuds.** The effect works because each ear hears something
> a little different. On speakers it sounds much weaker (the **Speakers** style,
> on step 2 → **Change style**, helps).

<p align="center">
  <img src="docs/images/choose-sound.png" alt="Audio8D's step 2, Choose how it sounds: the Sound style card shows Studio with a Change style button, and below it the list of songs with Song, Sound, Settings (Default) and Actions (Preview, Customize) columns." width="100%"/>
</p>

---

## Contents

**Using Audio8D**

1. [What can Audio8D do?](#what-can-audio8d-do)
2. [Before you start (install and check)](#before-you-start)
3. [Quick start with the window](#quick-start-with-the-window)
4. [Sound styles](#sound-styles)
5. [Change how one song sounds (Customize)](#change-how-one-song-sounds-customize)
6. [Default and Custom](#default-and-custom)
7. [Preview your music](#preview-your-music)
8. [All songs or one song](#all-songs-or-one-song)
9. [Choosing a file format](#choosing-a-file-format)
10. [Loudness](#loudness)
11. [Create your songs](#create-your-songs)
12. [Optional add-on: keep the singer in the middle](#optional-add-on-keep-the-singer-in-the-middle)
13. [Your own styles](#your-own-styles)
14. [Settings, keyboard and getting help](#settings-keyboard-and-getting-help)

**Command line (terminal)**

15. [Command line usage](#command-line-usage)
16. [The window and the command line do the same job](#the-window-and-the-command-line-do-the-same-job)

**Reference**

17. [Settings reference](#settings-reference)
18. [Troubleshooting](#troubleshooting)
19. [Words used in this guide](#words-used-in-this-guide)
20. [Advanced technical reference](#advanced-technical-reference)
21. [For developers](#for-developers)
22. [Known limitations](#known-limitations)
23. [Credits and licences](#credits-and-licences)

---

## What can Audio8D do?

- Turn normal music into 3D ("8D") audio that moves around your head
- Let you **listen to a short preview** before creating anything
- Offer **13 sound styles** (Studio, Gentle, Front, Smooth, Groove and more)
- Let you **customize one song** (or several) without changing the others
- Make **many songs at once**: a whole folder, even hundreds of songs
- Save as **MP3, FLAC, WAV, M4A or Opus**
- Make every song **as loud as your other music** (or keep its own loudness)
- Do everything **from the window or from a terminal** (command line)
- Keep **the singer in the middle** with an optional add-on, which you can install and
  remove whenever you like

Audio8D reads MP3, FLAC, WAV, M4A/AAC, OGG, Opus, WMA, AIFF, ALAC, APE, WavPack, MKA and
the sound of MP4/WEBM videos.

---

## Before you start

| You need | Why | Do I have to install it? |
|---|---|---|
| A **Windows 10 or 11** computer (64-bit) | To run the ready-made app | — |
| **Headphones** or earbuds | To hear the effect | — |
| **FFmpeg** | Makes the sound | **No**, it is included in the app (`bin\ffmpeg.exe`, `bin\ffprobe.exe`) |
| **Python** (3.10 or newer) | Only for the optional singer add-on, or to run the source code | Only if you want those |

### Install on a new computer

There are two ways to get Audio8D. Pick **A** if someone gave you the app, **B** if you
start from the source code on GitHub.

**A. The ready-made app (no Python needed)**

1. Get **`Audio8D-1.0.0-windows.zip`**. Audio8D has no public download page: it is the
   file a developer makes with `packaging\build.ps1 -Zip` (see B, step 5) and shares.
2. Unzip it (right-click it, then **Extract All…**). You get a folder called `Audio8D`.
3. Open the **`bin`** folder inside it and double-click **`Audio8D.exe`**.

If Windows says *"Windows protected your PC"*, click **More info**, then **Run anyway**.
This appears because the app is not signed with a paid certificate.

The `bin` folder holds everything Audio8D needs: `Audio8D.exe` (the window),
`audio8d-cli.exe` (the command line), `ffmpeg.exe`, `ffprobe.exe` and a folder called
`_internal`. Keep them together.

**B. From the source code (Windows)**

| Tool | Why | Get it | Check it |
|---|---|---|---|
| **Git** with **Git LFS** | Downloads the code; LFS brings the two large FFmpeg files | [git-scm.com](https://git-scm.com/download/win) (Git LFS is included) | `git lfs version` |
| **Python 3.10 or newer** (64-bit) | Runs Audio8D | [python.org](https://www.python.org/downloads/); tick *Add python.exe to PATH* | `python --version` (if it opens the Microsoft Store instead, install Python again with *Add python.exe to PATH* ticked) |

A **terminal** is the text window where you type commands (Start menu → type
*Terminal*). In a terminal:

```powershell
git lfs install                                          # 1. once per computer
git clone https://github.com/gcfernando/python_codes.git # 2. the code (Audio8D is in 8D)
cd python_codes\8D
python -m pip install customtkinter pillow               # 3. the window's parts
python src\__main__.py --check                           # 4. should end: Everything required is ready
```

After step 2, `bin\ffmpeg.exe` must be about 100 MB. If it is only a few hundred bytes,
Git LFS was missing: run `git lfs pull`.

5. Start it: `python src\__main__.py --gui` opens the window (or double-click
   `Audio8D.pyw`), and `python src\__main__.py --help` shows the command line. To make the
   ready-made app of A instead, run
   `powershell -ExecutionPolicy Bypass -File packaging\build.ps1 -Zip`; the zip lands in
   `build\`.

On macOS or Linux, write `python3` and `src/__main__.py`, and install FFmpeg first
(`brew install ffmpeg` on macOS, `sudo apt install ffmpeg` on Ubuntu).

`python -m pip install ".[gui]"` installs Audio8D as the commands `audio8d` and
`audio8d-gui`. Those commands don't look in the `bin` folder, so tell them where FFmpeg
is: choose `bin\ffmpeg.exe` and `bin\ffprobe.exe` in **Settings** (FFmpeg and FFprobe,
**Browse…**), or add `--ffmpeg bin\ffmpeg.exe --ffprobe bin\ffprobe.exe` to a command
run in the `8D` folder.

### Check that it works

1. **Window:** it opens on *1 Add music*. **Settings → System check** shows FFmpeg and
   FFprobe as ready.
2. **Command line:** open a terminal in the `bin` folder (A; in File Explorer open `bin`,
   right-click an empty area → **Open in Terminal**) or the `8D` folder (B):

   ```powershell
   .\audio8d-cli.exe --check                     # A; for B: python src\__main__.py --check
   ```

   It ends with *Everything required is ready* (the singer add-on is optional).
3. **A test song** (use any song you have): listen to a short preview first, then make
   the 8D song. It is saved as `<song> (8D).mp3` next to the original:

   ```powershell
   .\audio8d-cli.exe "C:\Music\My Song.mp3" --preview
   .\audio8d-cli.exe "C:\Music\My Song.mp3"
   ```

   For B, write `python src\__main__.py` instead of `.\audio8d-cli.exe`.

---

## Quick start with the window

This is the easiest way to use Audio8D. It takes about five minutes.

### 1. Open Audio8D

Double-click **`Audio8D.exe`** (in the `bin` folder). The window opens on **step 1**.
The four steps down the left side are the whole journey:
**1 Add music → 2 Choose sound → 3 Output → 4 Create.**

<p align="center">
  <img src="docs/images/main-screen.png" alt="The Audio8D window on first start: step 1 Add music with a large area saying Drop songs or folders here, and Add songs and Add folder buttons." width="100%"/>
</p>

### 2. Add your songs

Do **one** of these:

- **Drag** songs or a whole folder from File Explorer and **drop** them on the window, or
- Click **Add songs** (pick one or more songs), or **Add folder** (every song in a folder;
  switch on *Include songs in sub-folders* to add those too).

Audio8D reads each song's name, artist, album and length. A file that isn't music is
shown in red and skipped; it doesn't stop the others.

<p align="center">
  <img src="docs/images/add-music.png" alt="Step 1 with 13 songs added: a table with Song, Artist, Album, Genre, Length, Type and Status columns; one file, notes-broken, is red with 'Can't be read: not music, or damaged'." width="100%"/>
</p>

Click **Next: choose sound** (or **2 Choose sound** on the left).

### 3. Choose a sound style

Step 2 shows the **sound style** every song will use, and a list of your songs.

**Studio** is already chosen. It is a safe choice for most music. To try another, click
**Change style**, click a style card, and click **Apply Smooth** (the button names the
style you picked; see [Sound styles](#sound-styles)).

<p align="center">
  <img src="docs/images/choose-style.png" alt="The Choose sound style dialog: cards for Studio (Recommended, In use), Gentle, Front (Selected), Classic, Groove, Smooth, Strong and Spacious, each with one sentence, Good for, and Preview and Apply buttons; more cards below; Cancel and Apply Front at the bottom." width="85%"/>
</p>

### 4. Preview

Select a song in the list and click **Preview** (or click **▶ Preview** in its row).
After a few seconds you hear about 30 seconds of the song, taken from its loudest part.

> Preview lets you listen before creating the final file. Audio8D does **not** keep the
> temporary preview file.

Click **Stop** to stop listening. More in [Preview your music](#preview-your-music).
Then click **Next: output**.

### 5. Choose where and how to save

Click **3 Output**. The recommended choices are already selected, so you can simply go
on. **Where the new files go** is chosen once for all songs:

- **Save them**: *next to each original song* (the default) or *in one folder you choose*;
- **File names**: `Song (8D)` beside the original (recommended), or the song's own name
  in another folder;
- **If the 8D file exists**: skip that song (so running again only makes what's missing)
  or replace it;
- **Original songs**: keep them (the default), or replace them with the 8D version (the
  old one goes to the Recycle Bin, so you can get it back).

**How the songs are saved** starts with two buttons, **All songs** and **One song** (see
[All songs or one song](#all-songs-or-one-song)):

- the **Output format**: MP3 works everywhere (see [Choosing a file format](#choosing-a-file-format));
- **Loudness**: *Match music apps* makes your 8D songs as loud as your other music;
- quality, and under **More output options** the bitrate, peak limit, album picture and
  more.

Then click **Next: create**.

### 6. Create

Click **4 Create**. A short summary tells you what will happen. Then click the big
**Create 12 songs** button below it (it says how many songs will be made).

<p align="center">
  <img src="docs/images/create-summary.png" alt="Step 4 Create: a Summary card with Songs 12 songs (1 that can't be read will be skipped), Sound Studio, Output MP3 High quality, Loudness Match music apps, Folder, File names; then notes such as Everything is ready." width="100%"/>
</p>

While songs are being made you see the progress, which song is being made now, and
roughly how long is left. **Stop** stops after the current step; finished songs are kept.
You can keep using the window.

### 7. Find your new music

Each new song is called **`<song name> (8D).mp3`** and is saved **next to the original
song**, or in the folder you chose on step 3. When everything is done, click **Open
folder** to see them, or **Play** to listen.

<p align="center">
  <img src="docs/images/create-done.png" alt="Step 4 after creating: All done: 12 songs made in 0:29, and a results table where every song says Done and 'Saved as … (8D).mp3 · -14.0 LUFS'." width="100%"/>
</p>

That's it. Put on your headphones and press play. 🎧

---

## Sound styles

A **style** is a ready-made way to make the music move. A style only changes **how it
sounds**: every style is saved the same way (see [Choosing a file format](#choosing-a-file-format)
and [Loudness](#loudness)). If you don't know which to pick, **start with Studio**.

**To change the style for all your songs:** on step 2, click **Change style**, click a
card, listen with **Preview** if you like, then click **Apply** (or **Cancel** to leave
it as it was). Clicking a card only selects it; nothing changes until you apply. The
style in use is marked **✓ In use**, the one you picked **● Selected**. You can also
move between cards with the arrow keys and press **Enter** to apply or **Esc** to cancel.

| Style | What it sounds like | Good for |
|---|---|---|
| **Studio** ⭐ | Balanced movement around your head, with a touch of room | Most music, mixed playlists, or when you are unsure |
| **Gentle** | Soft, subtle movement that stays out of the way | Acoustic, folk and singer-songwriter music |
| **Front** | The music never goes behind you: it sways in front, like a pair of speakers | Jazz, classical and live recordings, long listening, or if circling distracts you |
| **Classic** | Audio8D's earlier 3D sound: like Studio, a touch stronger and roomier | Anyone who liked earlier versions of Audio8D |
| **Groove** | Loops around each ear, in time with the beat | Dance, electronic, hip-hop and pop |
| **Smooth** | Slow, relaxed movement | Lo-fi, chill and background music |
| **Strong** | Big, obvious movement with more room | Rock, metal and EDM (can tire your ears on long albums) |
| **Spacious** | Wide and airy, like a large room | Film music, ambient music and slow ballads |
| **Sky** | Drifts up over your head and back down | Ambient, chill-out and meditation music |
| **Voice** | For speech: a slow sweep in front of you with no room sound | Podcasts, audiobooks and spoken word |
| **Whirlwind** | A very fast spin: fun for a moment, but it may feel dizzying | Short clips and ringtones |
| **Speakers** | Gentle left-right movement that works without headphones | Speakers and car stereos |
| **Retro** | The old left-right "ping-pong" sound of the first Audio8D; the bass moves too | Nostalgia and short clips (not for long listening) |

No style is "better" than another; they just suit different music. Every style was
tested to land near -14 LUFS without clipping. Lossy files aim to keep true peaks under
-1 dBTP (measured for MP3 and Opus); FLAC and WAV keep sample peaks under -1 dBFS;
and a preview uses exactly the same processing as the final file (only shorter, and
played from a temporary WAV file). Fast spins (Whirlwind) can make some listeners
feel they are turning; use them for short clips.

Audio8D can also **suggest** a style for each song from its genre: click **Use suggested
styles** on step 2 (it only changes songs where the genre makes the choice clear).

### Where the styles come from

The styles are **Audio8D Sound Styles**: Audio8D's own ready-made settings, not an
industry standard. No international standard defines a list of consumer "sound
styles", and other 8D apps' preset names are not standards either. What the styles are
built on:

| Kind | What Audio8D uses |
|---|---|
| **Formal standards** | Loudness is measured with FFmpeg's meter, which follows ITU-R BS.1770 and EBU R 128; lossy files aim to keep true peaks below -1 dBTP, the headroom AES TD1008 recommends before lossy encoding (measured for MP3 and Opus; FLAC and WAV are not re-encoded, so they keep sample peaks under -1 dBFS). |
| **Established practice** | Bass below 120 Hz stays in the middle (as in loudspeaker bass management); direction comes from the timing and level differences between your ears (established head models); a modest room helps the sound feel outside your head on headphones; Front stays within about the ±30° of a normal pair of stereo speakers (ITU-R BS.775). |
| **Audio8D's own choices** | The speed, depth, path and room of each style, chosen by listening and measurement. |

Standards for full immersive audio, such as ITU-R BS.2051 / BS.2127, MPEG-H 3D Audio
(ISO/IEC 23008-3) and MPEG-I Immersive Audio (ISO/IEC 23090-4), describe complete
speaker, object and head-tracking systems. Audio8D makes ordinary stereo files for
headphones; it does not implement those systems and claims no compliance with them.

---

## Change how one song sounds (Customize)

Every song follows the default style unless you **customize** it. To change one song:

1. On step 2, select the song and click **Customize…** (or double-click the song, or click
   **✎ Customize** in its row).
2. The **Customize "song name"** window opens. Its title always says which song you are
   changing, and the line under it says that only this song changes.
3. Change what you like, then click **Apply**. **Cancel** (or **Esc**) changes nothing.

<p align="center">
  <img src="docs/images/customize-song.png" alt="The Customize 'Rain Study' dialog: a Custom badge, Sound with Style (Studio, default), Movement Gentle/Balanced/Strong, Speed Slow/Normal/Fast, Space Dry/Natural/Spacious, Optional: Keep bass centered and Keep the singer in the middle (add-on), and Preview, Reset to default, Cancel and Apply buttons." width="85%"/>
</p>

What you can choose, in plain words:

| Choice | What you hear |
|---|---|
| **Style** | The ready-made sound the song starts from |
| **Movement** — Gentle, Balanced, Strong | How far the music travels around your head |
| **Speed** — Slow, Normal, Fast | How quickly the music goes once around you |
| **Space** — Dry, Natural, Spacious | How big the room around the music sounds |
| **Keep bass centered** | The drums and bass stay steady in the middle (recommended) |
| **Keep the singer in the middle** | The music moves; the voice moves only a little and stays near the front (needs the [add-on](#optional-add-on-keep-the-singer-in-the-middle)) |

Click **Preview** in the dialog to hear your changes **before** you apply them. If a
style uses a value between two choices (for example Movement between Gentle and
Balanced), no choice is highlighted and the line under it says so.

**Save this song differently** (folded) gives this song its own file format, quality,
loudness, or only part of the song (handy for ringtones). **Advanced** (folded) holds the
exact numbers behind the choices, plus the path, direction, height, easing, beat sync and
more; you never need them.

<p align="center">
  <img src="docs/images/customize-advanced.png" alt="The Customize dialog with Advanced open: sliders for Movement amount 0.65, Seconds per circle 12 s and Room amount 0.25, and choices for Sound engine, Path and Direction." width="85%"/>
</p>

**Several songs at once:** select them (Shift+click or Ctrl+click in the list) and click
**Customize 2 songs…**. The dialog says how many songs it changes. Only what you change is
applied to all of them; everything else each song already had stays.

<p align="center">
  <img src="docs/images/customize-several.png" alt="The Customize 2 songs dialog: 'Editing 2 songs (City Lights, Midnight Arcade). Only what you change here is applied to all of them', with Style set to Groove." width="85%"/>
</p>

**The default sound for every song:** click **Customize default…** under **Change
style**. The dialog then says *Editing defaults for all songs*; songs you customized keep
their own settings.

---

## Default and Custom

> Audio8D starts with **one set of default settings**. Every song uses those settings
> **unless you customize that song**.

In the song list, the **Settings** column shows one of two words:

| Word | Meaning |
|---|---|
| **Default** | This song follows the main settings. |
| **Custom** | This song has its own settings. |

<p align="center">
  <img src="docs/images/song-list.png" alt="The song list: Storm Wall shows Sound Strong and Settings Custom, Rain Study shows Studio and Custom, every other song shows Studio and Default; each row has Preview and Customize." width="85%"/>
</p>

**Example.** You change the default style to **Smooth**. Every *Default* song now sounds
Smooth. A song you had customized to **Strong** stays Strong. Songs you add later follow
the default too.

**Reset to default** removes a song's own settings and makes it follow the main settings
again. Select the song(s) on step 2 and click **Reset to default**, or open **Customize**
and click **Reset to default** there.

---

## Preview your music

**Preview** lets you listen before creating anything.

- Preview does **not** create the final output file.
- Audio8D makes only a **short temporary** piece of audio (30 seconds by default, taken
  from the loudest part of the song; change it in **Settings → Preview length**).
- The temporary data is **cleaned up automatically**. It is never saved next to your
  music or in your output folder.
- The button always tells you what it will do:
  - **▶ Preview**: nothing is playing; click to listen.
  - **◌ Preparing… 40%**: the preview is being made; click again to cancel.
  - **■ Stop**: it is playing; click to stop.
- Starting another preview replaces the current one. Only one preview is made at a time.
- A song you already previewed with the same settings plays again straight away.
- To **save** a permanent file, use **Create** (step 4).

<p align="center">
  <img src="docs/images/preview.png" alt="The song list while a preview plays: the toolbar button says Stop, and Rain Study's row says Stop and Customize; the status bar says Playing a preview of Rain Study." width="85%"/>
</p>

Inside **Change style** and **Customize**, **Preview** plays the selected song with the
style or changes you are looking at, **without applying them**.

---

## All songs or one song

On **step 3 · Output**, *How the songs are saved* starts with **Settings for:
All songs | One song**. Both parts of that card, the main choices and **More output
options**, follow this one choice.

- **All songs** (where it starts): the line says *Changes here apply to every song
  without its own output settings*. That includes songs you add later.
- **One song**: a **Song** list appears, set to the song selected on step 2 (pick another
  in the **Song** list if you like). The line says *Changes here apply to “Glass Clouds” only*, with a
  **Default** or **Custom** badge. Everything you change below (format, quality,
  loudness, bitrate, *Reach the loudness exactly*, peak limit, album picture, the *(8D)*
  title, only part of the song) is kept for that song only. *More output options* says
  *For “Glass Clouds” only*.

<p align="center">
  <img src="docs/images/output-scope-song.png" alt="Step 3 Output, How the songs are saved: Settings for All songs | One song with One song chosen, Song Glass Clouds, a Custom badge, 'Changes here apply to “Glass Clouds” only. It has its own output settings.', a Reset to default button, Output format M4A and Quality High, and More output options 'For “Glass Clouds” only'." width="100%"/>
</p>

What happens when you change things later:

- Changing a **default** changes every song that follows the defaults, but **never** a
  song's own choice. (Change the default to Opus, and a song you set to M4A stays M4A.)
- **Reset to default** (next to the badge, for One song) removes only that song's own
  output settings; it follows All songs again. Its sound (step 2) is not touched.
- **Reset to recommended** (the same place, for All songs) puts the defaults back to MP3,
  High quality, Match music apps. Songs with their own output settings keep them.
- A choice equal to the default is simply the default: it doesn't make the song Custom.

The same per-song output settings are also under **Customize → Save this song
differently** on step 2. On the command line, the run's options are the defaults and a
`--per-song` line is one song's override (`--default` on a line resets it); see
[Give some songs their own settings](#give-some-songs-their-own-settings). For example:

```powershell
audio8d "C:\Music" --format opus --per-song songs.txt
```

with this line in `songs.txt` saves every song as Opus except *Glass Clouds*, which is
saved as M4A:

```text
"Glass Clouds.mp3" --format m4a
```

Audio8D remembers the **output defaults**, the default **style** and the **preview
length** for next time. It never remembers *Replace them* or *Replace it*, and song
overrides last only while those songs are on the list.

---

## Choosing a file format

Choose it on **step 3 · Output** (**Output format**), for all songs or for one song (see
[All songs or one song](#all-songs-or-one-song)).

| Format | Choose it when | Good to know |
|---|---|---|
| **MP3** (default) | You want a file that works almost everywhere | Phones, cars, every music app |
| **FLAC** | You want lossless quality: nothing is thrown away | About 4 times bigger than MP3; most, but not all, players |
| **WAV** | You want an uncompressed audio file | Very big files; no album picture |
| **M4A** | You want good quality with smaller files | Great on iPhone and in iTunes |
| **Opus** | You want efficient modern compression | The smallest files; some older players can't open it |

**Quality** (for MP3, M4A and Opus) is **High** by default. *Medium* and *Small* make
smaller files. **High** means the best each format needs: MP3 320 kbps, M4A 256 kbps,
Opus 192 kbps. FLAC and WAV are lossless, so they have no quality to choose. **More output options**
holds the rest, and shows only what applies to the chosen file type and loudness:

- **Bitrate (kbps)**: the exact rate behind Quality (Auto, 128 to 320); not shown for FLAC
  and WAV;
- **Reach the loudness exactly**: off (recommended) never squeezes the loudest moments, so
  a very dynamic song may end a little quieter; shown only when a loudness is chosen;
- **Peak limit**: in dB, recommended -1.5 dB for MP3, M4A and Opus, -1.0 dB for FLAC and
  WAV;
- **Keep the album picture** and **Add ' (8D)' to the song title**;
- **Use only part: from / to**: times like 90 or 1:30, for example for a ringtone.

<p align="center">
  <img src="docs/images/output-advanced.png" alt="More output options open for “Glass Clouds” only: Bitrate (kbps) Auto to 320 with 256 chosen, Reach the loudness exactly (off), Peak limit -1.5 dB, Keep the album picture, Add (8D) to the song title, Use only part: from / to." width="100%"/>
</p>

<p align="center">
  <img src="docs/images/output-settings.png" alt="Step 3 Output: Where the new files go (all songs): Save them In one folder I choose (C:\Audio8D Demo\Music 8D), File names, If the 8D file exists, Original songs; then How the songs are saved: Settings for All songs | One song, with All songs chosen." width="100%"/>
</p>

---

## Loudness

Songs from different albums are often not equally loud. Audio8D can fix that.

**Match music apps** (default). Makes your new songs play at about the same volume as
music from Spotify, YouTube and other apps, so they don't sound quieter than the rest of
your music. *(Technical target: -14 LUFS.)*

**Keep original loudness.** Each new song is as loud as its original song was. Use it for
albums whose quiet and loud songs should stay that way.

**Advanced…** shows more: *Apple Music* (-16 LUFS), *TV & radio* (-23 LUFS), *No change*
(no loudness adjustment; 8D songs are often a little quieter then), or *Custom…* (type a
level from -30 to -5).

Loudness is **measured**, never guessed, and the loudest peaks are protected so nothing
crackles. **LUFS** is simply the unit used to measure how loud music feels.

---

## Create your songs

Step 4 · **Create** shows a short **Summary** (how many songs, the sound, output format,
loudness, folder and file names), then anything that must be fixed first in red, or
worth knowing in yellow. When everything is fine you see *Everything is ready*.

Click **Create N songs**. During creating:

- the bar and the line under it show *4 of 12 done · now: Nocturne in Blue · about 0:21 left*;
- each song's row says what it is doing, then **Done** with its new file name;
- **Stop** (or **Esc**) stops after the current step. Finished songs are kept; the song
  being made is cleaned up.

<p align="center">
  <img src="docs/images/create-progress.png" alt="Creating: the Create 12 songs button greyed out, a red Stop button, the progress bar at one third, '4 of 12 done · now: Nocturne in Blue (+1 more) · about 0:21 left', and rows saying Done, Saving the file 0% and Waiting." width="100%"/>
</p>

After creating: **Play** plays the selected new song, **Open folder** opens its folder,
**Show only songs with a problem** filters the list, **Copy problem list** copies the
problems (to send to someone helping you), and **Try failed songs again** retries only
the songs that failed.

If a song's 8D file already exists, Audio8D skips that song (so running again only makes
what's missing). To make them again, choose **If the 8D file exists: Replace it** on
step 3.

---

## Optional add-on: keep the singer in the middle

<p align="center">
  <img src="docs/images/addon-manager.png" alt="Settings, the Add-on card: Not installed, four boxes What it does, Benefits, Changes to your computer and Removal, the Python used to install it, and the buttons Install add-on and Check again." width="100%"/>
</p>

### What is it?

An extra part, called **Demucs**, a free AI model that can separate a singer's voice from
the music. It runs with **PyTorch** (about 1 GB). It is not included in Audio8D because of
its size.

### What does it give me?

The option **Keep the singer in the middle**. With it, the band moves around your head
while the voice moves only a little and stays clear near the front. Many people find songs with
vocals more natural this way.

### Do I need it?

**No.** Audio8D works fully without it. Only this one option needs it.

### What changes on my computer?

Audio8D creates its **own add-on folder** and downloads about **1 GB** into it (Demucs and
PyTorch), using a Python that is already on your computer. **Nothing else is changed**:
not your Python, not your other programs. The folder is:

| Windows | macOS | Linux |
|---|---|---|
| `%LOCALAPPDATA%\Audio8D\addon` | `~/Library/Application Support/Audio8D/addon` | `~/.local/share/audio8d/addon` |

It works on Windows, macOS and Linux (64-bit Python 3.10 or newer). Installing needs an
internet connection and takes a few minutes.

### How do I install it?

**Window:** **Settings** → the **Add-on** card → read the four boxes → **Install add-on**
→ confirm. You can keep using Audio8D while it installs; **Stop** cancels it, and nothing
half-installed is kept. If Python isn't found, the card says how to get it
(python.org; tick *Add python.exe to PATH* when installing).

While it works, the card shows the step and, where it can be measured, a real
percentage, for example *Downloading packages — 42% · torch-2.5.1-cp312-cp312-win_amd64.whl (12 of 31)*, counting the files downloaded. Steps that
can't be measured (making the folder, working out what to download, pip's install step)
show a moving bar and no number. The bar never goes backwards. **100%** appears only
when the work really succeeded (*Installed successfully — 100%*); if it fails or you
stop it, the card says where it stopped, for example *(stopped at 42%)*. **Show
details** lists pip's own output.

<p align="center">
  <img src="docs/images/addon-progress.png" alt="The Add-on card while installing: an Installing badge, a Stop button, the progress bar at 42% and 'Downloading packages — 42% · torch (12 of 31)', with Show details under it." width="100%"/>
</p>

**Command line:**

```powershell
audio8d --install-addon
```

### How do I check whether it is installed?

**Window:** Settings → Add-on shows **✓ Installed** or **○ Not installed**
(or **Needs repair** if the folder was damaged).

<p align="center">
  <img src="docs/images/addon-installed.png" alt="The Add-on card when installed: Installed: 'Keep the singer in the middle' can be used; where it is installed; the buttons Uninstall add-on, Repair (reinstall) and Check again." width="100%"/>
</p>

**Command line** (exit code 0 = installed, 1 = not installed):

```powershell
audio8d --addon-status
```

### How do I use it?

Customize a song (step 2) and switch on **Keep the singer in the middle**. From the
command line: `audio8d "My Song.mp3" --vocals center`. Each such song takes a minute or
two longer.

### How do I remove it?

**Window:** Settings → Add-on → **Uninstall add-on** → confirm. The card counts the
files first, then shows the share removed, ending with *Uninstalled successfully — 100%*.

<p align="center">
  <img src="docs/images/addon-uninstall.png" alt="The question Uninstall the add-on?: the add-on folder will be deleted; Audio8D keeps working; Cancel and Uninstall buttons." width="60%"/>
</p>

**Command line:**

```powershell
audio8d --uninstall-addon
```

**Repair (reinstall)** deletes the add-on folder and installs it again, for when it stops
working. Command line: `audio8d --repair-addon`.

### What happens after uninstalling?

Audio8D keeps working exactly as before. Only **Keep the singer in the middle** becomes
unavailable. Songs that were set to use it can't be created until you install the add-on
again or switch that option off for them; Audio8D tells you which songs.

> If you installed Demucs yourself into your own Python, Audio8D uses it too, but it never
> removes it; the card shows the command to remove it yourself.

---

## Your own styles

On **Your styles** (left side) you can make a style by answering a few questions (music
type, movement, speed, space, headphones or speakers). Audio8D checks it, suggests a name
and a description, and **Try it** plays the selected song with it. Saved styles appear in
**Change style** and **Customize** like the built-in ones.

You can also save your current default sound as a style. Each saved style has these
buttons:

- **Use**: makes it the default style (songs you customized keep theirs);
- **Edit**: opens the style in the Customize dialog with a **Name** box. Change the
  sound (Movement, Speed, Space, the Optional and Advanced parts) and the name, listen
  with **Preview**, then click **Save changes**. The same style is updated; no copy is
  made. Songs that use it get the new sound at once, and a new name is used everywhere.
  **Cancel** keeps the style as it was;
- **Rename**, **Duplicate**, **Export** (to share as a small `.json` file) and **Delete**;
  **Import a style…** adds one from a file.

Saving checks the style the same way every time: the name (words starting with a
capital, not taken, not a built-in name, at most 40 characters) and the quality
check (a style with no movement is refused; a doubtful one asks *Save as it is* or
*Improve and save*). Built-in styles can't be edited or renamed; **Duplicate** one of
yours, or save your current sound, to start from it. A style is only a sound: file
format and loudness are never part of it.

<p align="center">
  <img src="docs/images/edit-style.png" alt="The Edit your style “Late Night” dialog: a Name box with Late Night Drive and 'It will be saved as Late Night Drive.', Movement, Speed and Space, Keep bass centered, and Preview, Cancel and Save changes buttons." width="70%"/>
</p>

---

## Settings, keyboard and getting help

**Settings** (left side) holds:

- the **System check**: every program Audio8D depends on, with *Ready*, *Missing*,
  *Invalid*, *Optional* or *Unavailable* and what to do; **Check everything again**
  re-runs it;
- **FFmpeg and FFprobe**: normally found automatically; **Browse…** to choose your own;
- the **Add-on** (see above);
- **Appearance**: **Theme** (Light, Dark or System), **Size** (text and controls), and
  **Preview length**;
- **Logs and saved data**, and **About** with **Open the full guide**, which opens this
  guide in your web browser. If the browser can't start, the address is copied so you can
  paste it into any browser.

**Keyboard**

| Keys | What they do |
|---|---|
| **Tab**, **Shift+Tab** | Move between buttons and choices (a ring shows where you are) |
| **Space**, **Enter** | Press the button or open the list |
| **←** **→** | Change a choice, e.g. Gentle / Balanced / Strong |
| **Ctrl+1** … **Ctrl+6** | Go to a step or page |
| **Ctrl+O**, **Ctrl+Shift+O** | Add songs, add a folder |
| **Ctrl+P** | Preview (or stop) the selected song |
| **Ctrl+Enter** | Create |
| **Ctrl+F** | Search the song list |
| **Enter** (in the song list) | Customize the selected song |
| **Space** (in the song list) | Preview the selected song |
| **Esc** | Close a dialog without changing anything; otherwise stop creating or a preview |
| **Enter** (in a dialog) | Apply |

States are always said in words as well as colour (for example *Default*, *Custom*,
*✓ Installed*, *● Selected*).

**When something goes wrong,** Audio8D says what happened in plain words and what to do.
The technical details are folded under **Show details** (and **Copy details** copies them
for someone helping you).

<p align="center">
  <img src="docs/images/error-message.png" alt="A problem message: Something went wrong. FFmpeg couldn't process this song. What to do: Audio8D isn't allowed to write there; choose another folder. Show details, Copy details and OK." width="60%"/>
</p>
<p align="center">
  <img src="docs/images/error-details.png" alt="The same message with Show details opened: the exact technical error below the plain words." width="60%"/>
</p>

---

## Command line usage

Everything the window does can also be done by **typing commands** in a terminal. This is
handy for many songs, for scripts, or if you prefer typing.

**How to start it:**

| You have | Type |
|---|---|
| The Windows app (in its `bin` folder) | `.\audio8d-cli.exe` |
| The source code (in the `8D` folder) | `python src\__main__.py` |
| Installed with pip | `audio8d` |

The examples below write **`audio8d`**; use whichever of these fits. Put names with spaces
in **"quotes"**. Typing `audio8d` alone starts a **step-by-step helper** that asks you a few
questions.

### Make one song

```powershell
audio8d "My Song.mp3"
```

What happens: it shows the settings, makes the song and checks it. You get
**`My Song (8D).mp3`** next to the original (Studio style, MP3 High quality, as loud as
music apps). The end of the output looks like this:

```text
  Created in 4.5 s  ->  C:\Music\Rain Study (8D).mp3  (3.6 MB)
  Loudness: measured -17.8 LUFS, turned up 3.8 dB  ->  about -14.0 LUFS
  Check: -14.1 LUFS, peaks -2.5 dBTP, range 5.0 LU, mono-safe (correlation +0.56)
  Put on your headphones and press play!
```

### Make several songs (a folder)

```powershell
audio8d "C:\Music" --output-dir "C:\Music 8D"
audio8d "C:\Music" --recursive --output-dir "C:\Music 8D" --jobs 4
```

`--recursive` also takes songs from sub-folders; `--jobs 4` makes 4 songs at once. Each
finished song gets a line such as `[2/12] ✓  Glass Clouds (8D).mp3`, then a total.

### Choose a style

```powershell
audio8d "My Song.mp3" --style smooth
audio8d --list-styles
```

`--list-styles` shows every style with its exact values (your own styles included).

### Change the output format

```powershell
audio8d "My Song.mp3" --format flac
audio8d "My Song.mp3" --format m4a --bitrate 192
```

Formats: `mp3` (default), `flac`, `wav`, `m4a`, `opus`. Quality is High unless you give
`--bitrate` (128, 160, 192, 224, 256, 320 or `auto`).

### Set the loudness

```powershell
audio8d "My Song.mp3" --loudness match
audio8d "My Song.mp3" --loudness -16
```

`-14` is *Match music apps* (default), `match` is *Keep original loudness*, `off` means no
change; any number from -30 to -5 also works.

### Customize the sound

The same friendly words as the window:

```powershell
audio8d "My Song.mp3" --movement gentle --speed slow --space spacious
```

Or exact values (advanced):

```powershell
audio8d "My Song.mp3" --intensity 0.7 --rotation-seconds 10 --path figure8 --elevation 0.3
```

Don't give a word and its exact value together (`--movement` with `--intensity`); Audio8D
stops and tells you to use only one.

### Preview from the command line

```powershell
audio8d "My Song.mp3" --preview
audio8d "My Song.mp3" --preview 15
audio8d "My Song.mp3" --compare
```

`--preview` makes a short sample (30 seconds, or the number you give) in a temporary
folder, **plays it**, and **deletes it** when it ends (press Enter or Ctrl+C to stop
early). Nothing is saved next to your music. `--compare` plays the original, a short
pause, then the 8D version, at the same loudness. To keep a sample on purpose, name the
file: `audio8d "My Song.mp3" "sample.wav" --preview 20`.

### Use the defaults

```powershell
audio8d "My Song.mp3"
```

Giving no style or setting uses the defaults: **Studio**, **MP3 High quality**, **Match
music apps**, saved next to the original as `<song> (8D).mp3`. These are the same defaults
as the window.

### Give some songs their own settings

For a folder, a small text file can give some songs their own settings (**one song per
line**, then the same options you would type):

```text
# song               its own settings
"Rain Study.mp3"     --style smooth --format flac
*.mp3                --loudness match
"Glass Clouds"       --default
```

```powershell
audio8d "C:\Music" --per-song songs.txt
```

- A line names a song by its file name, its name without `.mp3`, a pattern (`*.flac`) or
  a path. Every matching line applies, top to bottom, so later lines win.
- **`--default`** on a line is **Reset to default**: that song follows the command's
  settings again, whatever earlier lines said.
- Settings for the whole run (`--output-dir`, `--jobs`…) can't go on a line; the message
  names the line.

### Add-on: status, install, remove

```powershell
audio8d --addon-status
audio8d --install-addon
audio8d --repair-addon
audio8d --uninstall-addon
audio8d "My Song.mp3" --vocals center
```

`--addon-status` explains the add-on and exits with 0 when installed, 1 when not.
Installing, repairing and uninstalling print the same steps and real percentages as the
window, and 100% only when it worked; a failed or stopped run says where it stopped,
for example *(stopped at 42%)*.
Installing and uninstalling again changes nothing and says so. `--python PATH` chooses the
Python used to install it.

### Check that everything works

```powershell
audio8d --check
```

It runs every program Audio8D needs and says what is ready and what to fix (exit code 0 =
ready, 1 = something required must be fixed). Add `--verbose` for technical details.

### Show help

```powershell
audio8d --help
audio8d --version
```

`--help` lists every option with a short explanation and the defaults.

### Exit codes

**0** = done; **1** = a problem was explained (for example a song failed); **2** = the
command itself was mistyped (the message says what, with an example).

### All options

| How it sounds | |
|---|---|
| `--style NAME` | A style (`--list-styles`) or one of your own. Default `studio` |
| `--movement gentle\|balanced\|strong` | How far it moves (0.65 / 0.80 / 0.95) |
| `--speed slow\|normal\|fast` | How fast it goes around (12 / 8 / 5 seconds) |
| `--space dry\|natural\|spacious` | How big the room sounds (0.10 / 0.25 / 0.45) |
| `--intensity 0..1`, `--rotation-seconds 2..100`, `--ambience 0..1` | The same three, as exact values |
| `--engine 3d\|pan`, `--path circle\|arc\|figure8\|wander`, `--direction clockwise\|counterclockwise` | Engine, route and direction |
| `--bass HZ\|off` | Keep the bass centered below this pitch (default 120) |
| `--elevation 0..1`, `--fade SECONDS` | Height; ease in and out |
| `--beat-sync`, `--bpm TEMPO` | Circle in time with the beat |
| `--speed-curve "0=10, 1:00=6"`, `--intensity-curve "0=0.6, 1:00=0.95"` | Change speed or movement over time |
| `--vocals move\|center`, `--speakers` | Singer in the middle (add-on); safe for speakers |

| Output (how the file is saved) | |
|---|---|
| `--format mp3\|flac\|wav\|m4a\|opus` | The file format |
| `--bitrate KBPS\|auto`, `--quality 0..9` | Exact quality (advanced) |
| `--loudness LEVEL\|match\|off`, `--exact-loudness` | Loudness |
| `--limiter-ceiling 0.0625..1` | Peak limit (advanced; 0.84 ≈ -1.5 dB, 0.89 ≈ -1.0 dB) |
| `--output-dir FOLDER`, `--name 8d\|original` | Where and under which name |
| `--replace`, `--overwrite` | Replace the originals (they go to the Recycle Bin); replace existing 8D files |
| `--start TIME`, `--end TIME` | Only part of the song (e.g. `1:30`) |
| `--no-cover`, `--keep-title`, `--no-check` | No album picture; don't add (8D) to the title; don't check the result |

| More | |
|---|---|
| `--recursive`, `--jobs N` | With a folder: sub-folders too; N songs at once |
| `--per-song FILE` | Settings of their own for some songs |
| `--preview [SECONDS]`, `--compare`, `--play` | Listen first; play the new file |
| `--save-style NAME` | Save these sound settings as your own style |
| `--list-styles`, `--gui`, `--verbose`, `--version`, `--help` | Styles, the window, details, version, help |
| `--check`, `--ffmpeg PATH`, `--ffprobe PATH`, `--python PATH` | Check the setup; choose programs for this run |
| `--addon-status`, `--install-addon`, `--repair-addon`, `--uninstall-addon` | The add-on |

Older option names still work in scripts: `--preset` (= `--style`), `--list-presets`
and `--save-preset`. The older style names `lossless`, `streaming` and `hifi` also still
work; unlike the styles above, they also set how the file is saved (FLAC, exact loudness,
or FLAC with the original loudness), as they always did.

The command line uses the FFmpeg, Python and styles you chose in the window's Settings.

---

## The window and the command line do the same job

Both use the same code for every decision, so the same choices give the same songs.

### Choose the Studio style

**Window:** step 2 → **Change style** → click **Studio** → **Apply**.

```powershell
audio8d "My Song.mp3" --style studio
```

### Make the movement gentle and slow for one song

**Window:** step 2 → select the song → **Customize…** → Movement **Gentle**, Speed
**Slow** → **Apply**.

```powershell
audio8d "My Song.mp3" --movement gentle --speed slow
```

### Save as FLAC with the original loudness

**Window:** step 3 → Output format **FLAC — lossless quality** → Loudness **Keep original
loudness**.

```powershell
audio8d "My Song.mp3" --format flac --loudness match
```

### One song different from the rest, then back to default

**Window:** step 2 → select *Rain Study* → **Customize…** → Style **Smooth** → **Apply**.
Later: select it → **Reset to default**.

```powershell
audio8d "C:\Music" --per-song songs.txt
```

(with a `songs.txt` line `"Rain Study.mp3" --style smooth`; change that line to
`"Rain Study.mp3" --default`, or remove it, to reset.)

### Listen first

**Window:** step 2 → select the song → **Preview**.

```powershell
audio8d "My Song.mp3" --preview
```

### The add-on

**Window:** Settings → Add-on → **Install add-on** / **Uninstall add-on**.

```powershell
audio8d --addon-status
audio8d --install-addon
audio8d --uninstall-addon
```

---

## Settings reference

The recommended values are the defaults; you only need to change them if you want a
different sound.

| Setting | What it changes | Default | Simple recommendation |
|---|---|---|---|
| Style | The whole sound, as a ready-made set | Studio | Studio; Gentle for acoustic and classical |
| Movement | How far the music travels around you | Balanced (0.80) | Balanced; Gentle for calm music |
| Speed | How quickly it goes around | Normal (8 s per circle) | Normal; under 6 s can make some people dizzy |
| Space | How big the room sounds | Natural (0.25) | Natural; Dry for voices |
| Keep bass centered | The bass (below 120 Hz) stays in the middle | On | On |
| Height | Lets the sound float above ear level | 0 (ear level) | 0 for natural listening |
| Ease in and out | The movement grows in at the start and settles at the end | 3 s | 3 s |
| Spin in time with the beat | Each circle lasts whole bars of music | Off (on in Groove) | On for dance and pop |
| Keep the singer in the middle | The music moves; the voice moves only a little, near the front | Off | On for songs with vocals (needs the add-on) |
| Output format | The kind of file | MP3 | MP3; FLAC to keep every detail |
| Quality | How much detail a compressed file keeps | High | High |
| Loudness | How loud the new song is | Match music apps (-14 LUFS) | Match music apps |
| Reach the loudness exactly | Squeezes the loudest moments to reach the level exactly | Off | Off |
| Peak limit | The loudest a peak may get | -1.5 dB (MP3, M4A, Opus), -1.0 dB (FLAC, WAV) | Leave it |
| Preview length | How long a preview plays | 30 s | 15–30 s |

---

## Troubleshooting

### Audio8D cannot find FFmpeg

The app includes FFmpeg, so this means a file is missing or a wrong one was chosen.
Audio8D opens **Settings → System check** by itself and says what is wrong.

1. Click **Find automatically** in *FFmpeg and FFprobe*, then **Check everything again**.
2. Still missing? Put `ffmpeg.exe` and `ffprobe.exe` back into the `bin` folder (they are
   in the download), or click **Browse…** to choose them and **Save and use**.
3. Command line: `audio8d --check`, or `--ffmpeg PATH --ffprobe PATH` for one run.

No restart is needed.

### The song cannot be processed

The message says why. Common causes: the file isn't really music, is damaged, or uses an
unusual format; the file was moved or deleted after you added it. Check that the song
plays in your music app, or use another copy. Other songs are not affected.

### Preview does not play

- Wait for **Preparing…** to finish; long songs take a few seconds.
- If it says the preview failed, the message says why (often the song file).
- Check your volume and that headphones are connected.
- On macOS and Linux the preview opens in your usual music player instead.

### Output folder cannot be written

*"Audio8D isn't allowed to save in …"*: choose a folder you own, such as your **Music**
folder, on step 3 (**In one folder I choose → Browse…**). A drive that isn't plugged in is
also named. Close any program that has the file open.

### The add-on will not install

- It needs **64-bit Python 3.10 or newer**. The Add-on card says if Python is missing or
  too old; install it from python.org (tick *Add python.exe to PATH*) and click **Find
  automatically**.
- It needs an internet connection and about 1 GB of free space.
- **Show details** on the card has pip's own words. Try **Repair (reinstall)**.
- Command line: `audio8d --install-addon` shows every step.

### I accidentally customized a song

Select it on step 2 and click **Reset to default** (or open **Customize** and click
**Reset to default**). It follows the main settings again. Changes in **Customize** are
only kept when you click **Apply**; **Cancel** changes nothing.

### The output is too loud or too quiet

Step 3 → **Loudness**: **Match music apps** makes songs as loud as other music;
**Keep original loudness** keeps each song as it was. *Advanced…* → *No change* makes
no adjustment (often quieter).

### The music movement feels too strong

Choose a gentler style (**Gentle**, **Front** or **Smooth**) with **Change style**, or
**Customize** the song and set **Movement: Gentle** and **Speed: Slow**.

### The window seems stuck while creating

Creating runs in the background; the window keeps working. The progress bar, *now: song
name* and *about 0:21 left* show it is working. **Stop** (or **Esc**) stops after the
current step. *Keep the singer in the middle* takes a minute or two per song.

### A song asks for the singer add-on

*"… keep the singer in the middle, but the singer add-on isn't ready"*: install the add-on
(Settings → Add-on), or Customize those songs and switch the option off.

---

## Words used in this guide

| Word | Meaning |
|---|---|
| **8D audio** | Music that seems to move around your head when you use headphones. |
| **Style** | A ready-made group of sound settings. |
| **Default** | The settings used automatically unless you change a song. |
| **Custom** | Settings that belong to one song only. |
| **Customize** | Change the settings of one song (or the default). |
| **Preview** | A temporary listen that does not create the final file. |
| **Create** | Make and save the new 8D files. |
| **Output** | How the new file is saved: format, quality, loudness, folder. |
| **Bitrate** | A quality/size setting for compressed audio such as MP3. |
| **Lossless** | Audio saved without throwing any sound data away (FLAC, WAV). |
| **LUFS** | The unit for how loud music feels; music apps use -14. |
| **Add-on** | An optional extra part you can install and remove. |
| **FFmpeg** | The sound program Audio8D uses to do the work. |
| **Terminal / command line** | A window where you type commands instead of clicking. |

---

## Advanced technical reference

*This part is for curious users and developers. You don't need it to use Audio8D.*

**How the 3D sound is made.** Audio8D splits the song into bass and the rest (a crossover
at 120 Hz by default, so the bass stays centered). The rest is moved along a path around
your head using the cues ears use: the tiny time difference between the ears, the level
difference, and the shadow of the head (treble is softer on the far ear and behind you).
A little reverb (the *Space* setting) helps the sound feel outside your head. Then
everything is mixed back, loudness is measured and set, peaks are limited, and the file
is encoded.

**Exact ranges**

| Setting | Range | Option |
|---|---|---|
| Movement (intensity) | 0 – 1 | `--intensity` |
| Seconds per circle | 2 – 100 | `--rotation-seconds` |
| Room (ambience) | 0 – 1 | `--ambience` |
| Bass crossover | 40 – 250 Hz, or off | `--bass` |
| Height (elevation) | 0 – 1 | `--elevation` |
| Ease in and out | 0 – 30 s | `--fade` |
| Tempo | 40 – 240 BPM | `--bpm` |
| Loudness target | -30 – -5 LUFS | `--loudness` |
| Peak limit | 0.0625 – 1 (about -24 to 0 dB) | `--limiter-ceiling` |
| MP3 variable quality | 0 (best) – 9 | `--quality` |
| Bitrate | 128, 160, 192, 224, 256, 320 kbps | `--bitrate` |

**Paths:** *circle* (all the way round), *arc* (side to side in front), *figure8* (loops
around each ear), *wander* (drifts, never repeating). **Engine:** *3d* (the cues above)
or *pan* (simple left-right volume, safe for speakers).

**Beat sync** detects the tempo and rounds the circle to 2, 4, 8, 16 or 32 beats.

**Loudness** is measured (EBU R 128) and the song is turned up or down to the target. By
default the peaks are protected: if reaching the target would need more than a light
touch of limiting, the song stays slightly under the target instead (*Always hit the
loudness exactly* changes that). Lossy formats get about 1 dB of extra headroom, because
their encoders can overshoot.

**Output encoders:** MP3 with LAME (constant bitrate, or variable quality with `auto`),
M4A with FFmpeg's AAC encoder, Opus with libopus, FLAC and WAV as 24-bit.

**Previews** are rendered by the same pipeline as the final file, from the loudest part of
the song, with a shorter ease-in, into a private temporary folder
(`%TEMP%\Audio8D previews\run-<process>-<time>`). Only the newest few previews are kept
for instant replays; a song's out-of-date preview is deleted as soon as a new one replaces
it; everything goes when the window closes; folders left by a closed or crashed window are
removed at the next start. The command line uses a temporary folder that is deleted when
the preview ends, whatever happens.

**Where Audio8D keeps things**

| What | Windows | macOS / Linux |
|---|---|---|
| Settings (`settings.json`) and your styles (`presets.toml`) | `%APPDATA%\Audio8D` | `~/Library/Application Support/Audio8D` / `~/.config/audio8d` |
| Log (`audio8d.log`) | `%LOCALAPPDATA%\Audio8D\logs` | the settings folder, `logs` |
| Remembered measurements, separated vocals | `%LOCALAPPDATA%\Audio8D\cache` | `~/Library/Caches/Audio8D` / `~/.cache/audio8d` |
| The add-on | `%LOCALAPPDATA%\Audio8D\addon` | see [the add-on](#what-changes-on-my-computer) |
| Previews | `%TEMP%\Audio8D previews` | the system temporary folder |

Setting the environment variable `AUDIO8D_HOME` to a folder keeps all of these (except
previews) there instead, for a portable copy.

---

## For developers

**Layout of `src` (the `audio8d` package)**

| Part | Holds |
|---|---|
| `pipeline.py`, `batch.py`, `effects/`, `analysis/`, `ffmpeg/`, `files/` | The conversion, shared by the window and the command line |
| `core/presets.py`, `core/sound_levels.py`, `core/style_guide.py` | The styles (sound only), the standard output, the Movement/Speed/Space words |
| `song_settings.py`, `per_song.py` | How a song's own settings combine with the defaults (window and `--per-song`) |
| `gui_model.py` | The window's settings, Customize drafts, Reset to default, checks; no widgets |
| `previews.py`, `player.py` | Temporary previews and playback |
| `addons.py`, `health.py` | Add-on status, install, repair, uninstall; the system check |
| `cli.py`, `options.py`, `display.py`, `display_health.py`, `guided.py` | The command line |
| `gui_app.py` + `app_*.py` | The main window, split by topic |
| `gui_styles.py`, `gui_style_chooser.py`, `gui_customize.py`, `gui_output.py`, `gui_review.py`, `gui_settings.py`, `gui_health.py`, `gui_songs.py`, `gui_mystyles.py`, `gui_style_save.py` | Pages and dialogs (`gui_style_save.py`: the checks every saved style goes through) |
| `gui_modal.py`, `gui_widgets.py`, `gui_fields.py`, `gui_dialogs.py`, `gui_table.py` | Building blocks |

Business rules live outside the window and the command line, so they can't drift apart.
FFmpeg, FFprobe, Python and pip are always run with argument lists (never through a
shell), are tracked while they run, stop when cancelled, and are stopped when the window
closes.

**Tests and checks** (from the `8D` folder, with `python -m pip install pytest ruff pylint pyright`):

```powershell
python -m pytest                        # all tests (window tests need a screen)
python -m ruff check .
python -m ruff format --check .
python -m pylint src tests
python -m pyright src tests
```

The tests include the real window (the style chooser, Customize with Apply and Cancel,
Reset to default, previews, the add-on card, layout at 100 % and 125 % text), the command
line, the add-on install/repair/uninstall (with pip faked), temporary-preview cleanup, and
a check that every `audio8d` command in this guide is valid.

**Build the Windows app** (from the `8D` folder):

```powershell
powershell -ExecutionPolicy Bypass -File packaging\build.ps1
```

It puts `Audio8D.exe`, `audio8d-cli.exe` and `_internal` into `bin`, beside `ffmpeg.exe`
and `ffprobe.exe`, and checks that they start. Add `-Zip` to also make
`build\Audio8D-<version>-windows.zip`.

---

## Known limitations

- **Screen readers:** everything works from the keyboard, but Tk (the toolkit under the
  window) does not give control names to screen readers such as Narrator or NVDA.
- **Dialogs** (Change style, Customize) take about half a second to appear on a typical
  computer; the page behind them is not redrawn.
- **Previews play inside the window on Windows.** On macOS and Linux they open in your usual
  music player.
- **Suggestions come from tags and names**, not from listening to the audio.
- **No "16D" styles.** "16D" has no technical definition; the only describable idea is
  several layers (singer and music) moving on their own paths at once. Audio8D moves a
  song along one path, and with the singer add-on the voice follows the same path more
  gently, so relabelling a style as 16D would be misleading.
- **Previewing a style** (Change style, or Edit on Your styles) uses the Output step's
  settings for all songs; a song's own output settings and *Safe for speakers too* are
  used when the song is created, not in that preview.
- **Styles saved long ago "based on hifi"** load with Gentle's movement and room, not the
  old hifi values; open them with **Edit** and adjust if they sound different.
- **Editing a saved style is done in the window.** The command line can save a new style
  (`--save-style NAME`) but has no option to change or rename one.
- *Keep the singer in the middle* is slow: a minute or two per song (the separated voice is
  remembered, so the same song is quicker the next time).
- The ready-made app is for Windows. macOS and Linux run the source code, which was not
  tested on those systems for this release.

---

## Credits and licences

Audio8D is developed by **Gehan Fernando**. It uses
[FFmpeg](https://ffmpeg.org) (GPL-3.0, included for Windows),
[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter),
[Pillow](https://python-pillow.org), and, optionally,
[Demucs](https://github.com/facebookresearch/demucs) with
[PyTorch](https://pytorch.org); the Windows app is built with
[PyInstaller](https://pyinstaller.org). Their licences are in the `licenses` folder and
listed in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
