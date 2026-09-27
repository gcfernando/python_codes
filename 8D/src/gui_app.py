# Developed by ::> Gehan Fernando
"""The Audio8D desktop window, built with CustomTkinter.

A guided workflow in four steps - 1 Add songs, 2 Sound, 3 Output,
4 Review & convert - plus Your styles and Settings. Every command-line option
has a control here (see README part 25, "Every option"). All decisions live
in gui_model.GuiSettings; conversions run through the same pipeline and batch
code as the command line, on a helper thread, reporting back through a queue.
"""

# A desktop window is made of many small widgets and callbacks by nature
# pylint: disable=too-many-instance-attributes,too-many-lines,too-many-locals
# pylint: disable=too-many-statements,too-many-public-methods
# CustomTkinter widgets already sit deep in a class tree
# pylint: disable=too-many-ancestors

import dataclasses
import gc
import logging
import queue
import threading
import time
import tkinter as tk
import webbrowser
from collections.abc import Callable, Sequence
from pathlib import Path
from tkinter import filedialog
from types import TracebackType

import customtkinter as ctk

from . import __author__, __version__, hints
from .analysis import demucs_available, demucs_hint
from .batch import BatchOutcome, BatchReport, progress_tracker, run_batch
from .core.errors import Audio8DError
from .core.locations import (
    GUIDE_URL,
    cache_dir,
    guide_file,
    is_packaged,
    log_file,
    presets_file,
    tools_dir,
)
from .core.parsing import format_time, parse_time
from .core.presets import PRESETS, RECOMMENDED_PRESET, Preset
from .core.settings import EffectConfig
from .core.style_files import FILE_SUFFIX as STYLE_FILE_SUFFIX
from .core.style_files import export_style, import_style, read_style_file
from .core.types import AudioStreamInfo
from .core.user_presets import (
    all_presets,
    check_style_name,
    delete_user_preset,
    duplicate_user_preset,
    pascal_case,
    rename_user_preset,
    save_user_preset,
)
from .dropfiles import enable_file_drop
from .ffmpeg import FFmpegToolchain, probe_audio
from .files import (
    AUDIO_EXTENSIONS,
    describe_removal,
    find_songs,
    is_own_output,
    removal_summary,
)
from .gui_model import (
    BITRATE_CHOICES,
    FILE_CHOICES,
    LEVEL_CHOICES,
    LOUDNESS_CHOICES,
    MOVEMENT_CHOICES,
    MUSIC_CHOICES,
    PLACE_CHOICES,
    ROOM_CHOICES,
    SPEED_CHOICES,
    GuiSettings,
    StyleNote,
    config_for,
    describe,
    describe_curve,
    destination_for,
    gui_words,
    guided_config,
    improve_answers,
    improved,
    items_for,
    options_for,
    own_styles_line,
    problems,
    review,
    song_config,
    source_notes,
    style_check,
    style_label,
    style_summary,
    suggested_answers,
    suggested_description,
    suggested_name,
    warnings,
)
from .gui_widgets import (
    ACCENT,
    ACCENT_SOFT,
    BORDER,
    DANGER,
    DANGER_SOFT,
    INK,
    SIDEBAR,
    SUCCESS,
    SURFACE,
    SURFACE_ALT,
    TEXT_DIM,
    WARNING,
    WARNING_SOFT,
    WHITE,
    Card,
    ChoiceField,
    ChoiceMenu,
    Dialog,
    EntryField,
    Icons,
    NameDialog,
    Section,
    SliderField,
    SwitchField,
    Toast,
    Tooltip,
    button,
    fit_width,
    font,
    hint,
    icon_text,
    open_path,
    use_app_icon,
)
from .pipeline import (
    STAGE_CHECK,
    STAGE_RENDER,
    STAGE_SAVE,
    STAGE_STEMS,
    compare,
    compare_output_for,
    preview,
    preview_output_for,
    stages_for,
)

LOG = logging.getLogger(__name__)
# Rows built at a time in long lists; hundreds at once would freeze Tk's layout
SONGS_PER_PAGE = 25
# Tk's grid refuses row numbers from here on
_GRID_ROWS = 10_000
# How often the window frees cyclic garbage itself (see Audio8DApp.__init__)
GC_INTERVAL_MS = 3000
# How to reach the terminal app from here, for the About text
HELP_COMMAND = (
    "audio8d-cli.exe --help"
    if is_packaged()
    else "audio8d --help  (or python src\\__main__.py --help)"
)

_STAGE_WORDS = {
    STAGE_STEMS: "Splitting vocals",
    STAGE_RENDER: "Making the 3D mix",
    STAGE_SAVE: "Saving the file",
    STAGE_CHECK: "Checking the result",
}
# The first choice in every song's style menu
SAME_STYLE = "Same as all songs"
_SPIN_HELP = (
    "Seconds for one full circle. Recommended: 8 (classic 8D). Below 5 can make "
    "people dizzy; above 20 is hard to notice."
)
_HEIGHT_HELP = (
    "Lets the sound float up over your head and back down. 0 stays at ear level. "
    "Try 0.5 for ambient music."
)


def _problem(fn: Callable[[], object]) -> str | None:
    """Run a check; return its error message in window words, or None."""
    try:
        fn()
    except Audio8DError as exc:
        return gui_words(str(exc))
    return None


# ------------------------------------------------------------------ pages


class Page(ctk.CTkScrollableFrame):
    """A scrolling page with a step number, a title and a short explanation."""

    def __init__(self, master: tk.Misc, step: str, title: str, subtitle: str) -> None:
        """Draw the heading; content goes in rows 2 and below."""
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=28, pady=(22, 14))
        if step:
            ctk.CTkLabel(
                head, text=step, font=font(12, "bold"), text_color=ACCENT, anchor="w"
            ).pack(anchor="w")
        ctk.CTkLabel(head, text=title, font=font(24, "bold"), anchor="w").pack(
            anchor="w"
        )
        hint(head, subtitle).pack(anchor="w", fill="x")

    def add(self, widget: tk.Widget, row: int, pady: tuple[int, int] = (0, 16)) -> None:
        """Place a card on the page."""
        widget.grid(row=row, column=0, sticky="ew", padx=28, pady=pady)

    def footer(
        self,
        row: int,
        back: Callable[[], None] | None,
        text: str,
        forward: Callable[[], None],
    ) -> ctk.CTkFrame:
        """The Back / Next buttons at the bottom of a step."""
        strip = ctk.CTkFrame(self, fg_color="transparent")
        strip.grid(row=row, column=0, sticky="ew", padx=28, pady=(4, 28))
        if back is not None:
            button(strip, "back", "Back", back, width=110).pack(side="left")
        button(strip, "next", text, forward, kind="primary", width=240).pack(
            side="right"
        )
        return strip


class SongEntry:
    """One song on the list; its row on screen is only built while it is shown."""

    def __init__(self, song: Path, folder: Path | None) -> None:
        """A song, and the folder it was added from (None for a single file)."""
        self.song = song
        self.folder = folder
        # (codec, seconds, lossless) once the file has been read
        self.details: tuple[str, float | None, bool] | None = None
        # Everything reading the file found, for the heads-ups about its quality
        self.info: AudioStreamInfo | None = None
        self.bad = False
        self.selected = False
        self.view: SongRow | None = None

    @property
    def length_text(self) -> str:
        """What the length column shows: '…' while reading, '!' if unreadable."""
        if self.bad:
            return "!"
        if self.details is None:
            return "…"
        return format_time(self.details[1]) if self.details[1] else "?"

    def show_details(self, codec: str, seconds: float | None, lossless: bool) -> None:
        """Remember what reading the file found, and show it if the row is visible."""
        self.details = (codec, seconds, lossless)
        if self.view is not None:
            self.view.show_details(*self.details)

    def unreadable(self) -> None:
        """This file can't be read as music."""
        self.bad = True
        if self.view is not None:
            self.view.unreadable()

    def select(self, on: bool) -> None:
        """Mark this as the song Preview and A/B use."""
        self.selected = on
        if self.view is not None:
            self.view.select(on)

    def hide(self) -> None:
        """Take the row off the screen; the song stays on the list."""
        if self.view is not None:
            self.view.destroy()
            self.view = None


class SongRow(ctk.CTkFrame):
    """One song in the list: name, where it is, type and length."""

    def __init__(
        self,
        master: tk.Misc,
        entry: SongEntry,
        on_select: Callable[[SongEntry], None],
        on_remove: Callable[[SongEntry], None],
    ) -> None:
        """Draw the row, with whatever is already known about the song."""
        super().__init__(master, fg_color=SURFACE, corner_radius=10)
        song, folder = entry.song, entry.folder
        self.song = song
        self.grid_columnconfigure(1, weight=1)
        icon = ctk.CTkLabel(
            self,
            text=Icons.glyph("music"),
            font=Icons.font(18),
            text_color=ACCENT,
            width=36,
        )
        icon.grid(row=0, column=0, rowspan=2, padx=(12, 6), pady=8)
        name = ctk.CTkLabel(self, text=song.stem, font=font(13, "bold"), anchor="w")
        name.grid(row=0, column=1, sticky="ew", pady=(8, 0))
        where = (
            str(song.parent.relative_to(folder.parent)) if folder else song.parent.name
        )
        self.detail = ctk.CTkLabel(
            self, text=where, font=font(11), text_color=TEXT_DIM, anchor="w"
        )
        self.detail.grid(row=1, column=1, sticky="ew", pady=(0, 8))
        # The file type is in the detail line; fewer widgets keep long lists quick
        self.length = ctk.CTkLabel(
            self, text="…", font=font(12), text_color=TEXT_DIM, width=56
        )
        self.length.grid(row=0, column=2, rowspan=2, padx=4)
        remove = ctk.CTkLabel(
            self,
            text=Icons.glyph("remove"),
            font=Icons.font(12),
            width=30,
            height=30,
            text_color=TEXT_DIM,
            cursor="hand2",
        )
        remove.grid(row=0, column=3, rowspan=2, padx=(4, 12))
        remove.bind("<Button-1>", lambda _e: on_remove(entry))
        remove.bind("<Enter>", lambda _e: remove.configure(text_color=DANGER))
        remove.bind("<Leave>", lambda _e: remove.configure(text_color=TEXT_DIM))
        Tooltip(remove, "Take this song off the list (the file itself is not touched)")
        Tooltip(name, str(song))
        # CustomTkinter types add as True on frames and "+" on labels; both add
        self.bind("<Button-1>", lambda _e: on_select(entry), add=True)
        self.bind("<Double-Button-1>", lambda _e: open_path(self.song), add=True)
        for label in (icon, name, self.detail, self.length):
            label.bind("<Button-1>", lambda _e: on_select(entry), add="+")
            label.bind("<Double-Button-1>", lambda _e: open_path(self.song), add="+")
        if entry.bad:
            self.unreadable()
        elif entry.details is not None:
            self.show_details(*entry.details)
        if entry.selected:
            self.select(True)

    def show_details(self, codec: str, seconds: float | None, lossless: bool) -> None:
        """Fill in what reading the file found."""
        self.length.configure(text=format_time(seconds) if seconds else "?")
        quality = "lossless, the best start" if lossless else "compressed"
        self.detail.configure(
            text=f"{self.detail.cget('text')}  ·  {codec.upper()}, {quality}"
        )

    def unreadable(self) -> None:
        """This file can't be read as music."""
        self.length.configure(text="!", text_color=DANGER)
        self.detail.configure(
            text="Can't be read as music - it will fail", text_color=DANGER
        )

    def select(self, on: bool) -> None:
        """Highlight the row when it is the chosen one."""
        self.configure(
            fg_color=ACCENT_SOFT if on else SURFACE,
            border_width=1 if on else 0,
            border_color=ACCENT,
        )


class SongsPage(Page):
    """Step 1: the drop zone and the list of songs."""

    def __init__(self, master: tk.Misc, app: "Audio8DApp") -> None:
        """Build the page."""
        super().__init__(
            master,
            "STEP 1 OF 4",
            "Add your songs",
            "Drag songs or whole folders onto the window, or use the buttons. "
            "Nothing is changed until you press Start on the last step.",
        )
        self.app = app
        drop = ctk.CTkFrame(
            self,
            fg_color=SURFACE_ALT,
            corner_radius=16,
            border_width=2,
            border_color=ACCENT,
        )
        self.add(drop, 2)
        drop.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            drop, text=Icons.glyph("drop"), font=Icons.font(34), text_color=ACCENT
        ).grid(row=0, column=0, rowspan=2, padx=(24, 16), pady=22)
        ctk.CTkLabel(
            drop, text="Drop songs or folders here", font=font(17, "bold"), anchor="w"
        ).grid(row=0, column=1, sticky="sw", pady=(22, 0))
        hint(
            drop,
            "MP3, FLAC, WAV, M4A, OGG, Opus, WMA, AIFF, APE, WavPack, and the sound of "
            "videos (MP4, MKV, WEBM). Tip: FLAC or WAV gives the very best result.",
            # The icon and the two buttons share the same row
            margin=460,
        ).grid(row=1, column=1, sticky="new", pady=(0, 22))
        buttons = ctk.CTkFrame(drop, fg_color="transparent")
        buttons.grid(row=0, column=2, rowspan=2, padx=20)
        button(
            buttons,
            "add",
            "Add songs",
            app.ask_files,
            kind="primary",
            tooltip="Choose one or more song files (Ctrl+O)",
        ).pack(side="left", padx=4)
        button(
            buttons,
            "folder",
            "Add folder",
            app.ask_folder,
            tooltip="Add every song in a folder (Ctrl+Shift+O)",
        ).pack(side="left", padx=4)

        options = ctk.CTkFrame(self, fg_color="transparent")
        self.add(options, 3, (0, 8))
        options.grid_columnconfigure(0, weight=1)
        self.summary = ctk.CTkLabel(options, text="", font=font(15, "bold"), anchor="w")
        self.summary.grid(row=0, column=0, sticky="w")
        clear = button(
            options,
            "clear",
            "Clear list",
            app.clear_songs,
            width=120,
            height=32,
            tooltip="Take every song off the list (the files are not touched)",
        )
        clear.grid(row=0, column=1, sticky="e")
        self.recursive = SwitchField(
            options,
            "Include songs in sub-folders",
            "Folders you add also bring the songs in their sub-folders; the same "
            "sub-folders are made where the 8D songs are saved.",
            app.set_recursive,
        )
        self.recursive.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        self.recursive.set(app.settings.recursive)

        self.list = ctk.CTkFrame(self, fg_color=SURFACE_ALT, corner_radius=14)
        self.add(self.list, 4, (0, 12))
        self.list.grid_columnconfigure(0, weight=1)
        self.empty = ctk.CTkLabel(
            self.list,
            text="No songs yet.\nDrag them onto this window, or press Add songs.",
            font=font(14),
            text_color=TEXT_DIM,
        )
        self.empty.grid(row=0, column=0, pady=50)
        # Long lists show a page at a time; every song is still converted
        self.more = ctk.CTkFrame(self.list, fg_color="transparent")
        self.more.grid_columnconfigure(0, weight=1)
        self.more_text = ctk.CTkLabel(
            self.more, text="", font=font(13), text_color=TEXT_DIM, anchor="w"
        )
        self.more_text.grid(row=0, column=0, sticky="ew", padx=(12, 8))
        self.more_button = button(
            self.more,
            "add",
            "Show more",
            app.show_more_songs,
            width=190,
            height=32,
            tooltip="Show the next songs (long lists show a page at a time)",
        )
        self.more_button.grid(row=0, column=1, padx=(0, 8), pady=8)
        hint(
            self,
            "Click a song to choose it for Preview and A/B compare. Double-click to "
            "play the original. Files Audio8D made itself ('(8D)' files) are skipped.",
            margin=60,
        ).grid(row=5, column=0, sticky="ew", padx=28, pady=(0, 8))
        self.footer(6, None, "Next: choose the sound", lambda: app.show_page("sound"))


class SoundPage(Page):
    """Step 2: a style, then the essentials, then everything else under Advanced."""

    def __init__(self, master: tk.Misc, app: "Audio8DApp") -> None:
        """Build the page."""
        super().__init__(
            master,
            "STEP 2 OF 4",
            "Choose the sound",
            "Pick a style that suits your music (Studio is the best of best). You can "
            "fine-tune it below; every setting explains itself.",
        )
        self.app = app
        change = app.change_sound

        styles = Card(
            self,
            "1. Pick a style for all songs",
            "Click a card: every song gets this style. You can change any detail "
            "afterwards; 'Back to the style' undoes your changes. To give one song a "
            "different style, use card 4 below.",
        )
        self.add(styles, 2)
        self.cards_frame = styles.body
        self.cards: dict[str, ctk.CTkFrame] = {}
        self.build_cards()

        basics = Card(
            self, "2. The essentials", "The three settings that change the sound most."
        )
        self.add(basics, 3)
        self.style_note = ctk.CTkLabel(
            basics.body, text="", font=font(12, "bold"), text_color=ACCENT, anchor="w"
        )
        self.style_note.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.movement = SliderField(
            basics.body,
            "Movement",
            "How far round your head the music travels. Recommended: 0.80. 0 keeps "
            "it in the middle; above 0.95 can tire your ears.",
            0,
            1,
            20,
            lambda v: f"{v:.2f}",
            lambda v: change(intensity=round(v, 2)),
        )
        self.spin = SliderField(
            basics.body,
            "Spin speed",
            _SPIN_HELP,
            2,
            100,
            196,
            lambda v: f"{v:g} s",
            lambda v: change(rotation_seconds=round(v * 2) / 2),
        )
        self.room = SliderField(
            basics.body,
            "Room",
            "How much natural room sound (reverb) is added. Recommended: 0.25. 0 is "
            "dry (best for speech); above 0.6 can make voices blurry.",
            0,
            1,
            20,
            lambda v: f"{v:.2f}",
            lambda v: change(ambience=round(v, 2)),
        )
        for row, widget in enumerate((self.movement, self.spin, self.room), start=1):
            widget.grid(row=row, column=0, sticky="ew", pady=6)

        adv = Section(
            self,
            "3. Advanced sound",
            "Engine, path, bass, height, the beat, changes over time, the singer, "
            "speakers. The chosen style already set good values.",
        )
        self.add(adv, 4)
        self._advanced(adv.body, change)
        self.own = Section(
            self,
            "4. A different style for some songs",
            "Optional. Every song uses the style above, unless you pick another one "
            "for it here. A song with its own style uses that style exactly as it is, "
            "including its file type and loudness.",
        )
        self.add(self.own, 5)
        self._song_styles(self.own.body)
        self.footer(
            6,
            lambda: app.show_page("songs"),
            "Next: output options",
            lambda: app.show_page("output"),
        )

    def _advanced(self, body: ctk.CTkFrame, change: Callable[..., None]) -> None:
        """Every sound knob beyond the essentials."""
        app = self.app
        self.engine = ChoiceField(
            body,
            "Sound engine",
            "3D (recommended) uses the same clues your ears do - timing, loudness and "
            "tone - so the music goes round and behind you. Panning is the simple "
            "left-right effect of the first Audio8D.",
            {"3D around you": "3d", "Left-right panning": "pan"},
            lambda v: change(engine=v),
        )
        self.path = ChoiceField(
            body,
            "Path",
            "The route: a full circle; a front arc (side to side in front of you); a "
            "figure-8 round each ear; or a free wander that never repeats.",
            {
                "Circle": "circle",
                "Front arc": "arc",
                "Figure-8": "figure8",
                "Wander": "wander",
            },
            lambda v: change(path=v),
        )
        self.direction = ChoiceField(
            body,
            "Direction",
            "Which way it turns round your head.",
            {"Clockwise": "clockwise", "Counter-clockwise": "counterclockwise"},
            lambda v: change(direction=v),
        )
        self.bass_on = SwitchField(
            body,
            "Keep the bass in the middle",
            "Recommended ON. The kick drum and bass stay centred, like every "
            "professional mix, so the beat feels solid.",
            lambda on: change(bass_hz=self.bass_value() if on else 0.0),
        )
        self.bass = SliderField(
            body,
            "Bass below",
            "Everything below this pitch stays in the middle. Recommended: 120 Hz.",
            40,
            250,
            21,
            lambda v: f"{v:.0f} Hz",
            lambda v: change(bass_hz=self.bass_value()),
        )
        self.height = SliderField(
            body,
            "Height",
            _HEIGHT_HELP,
            0,
            1,
            20,
            lambda v: f"{v:.2f}",
            lambda v: change(elevation=round(v, 2)),
        )
        self.fade = SliderField(
            body,
            "Ease in and out",
            "The movement grows in at the start and settles back at the end, so a "
            "song never starts mid-spin. Recommended: 3 s. 0 turns it off.",
            0,
            30,
            60,
            lambda v: f"{v:g} s",
            lambda v: change(fade_seconds=round(v * 2) / 2),
        )
        self.beat = SwitchField(
            body,
            "Spin in time with the beat",
            "Finds the song's tempo and makes one circle last whole bars, as close as "
            "possible to the spin speed. Great for dance and pop.",
            lambda on: change(beat_sync=on),
        )
        self.bpm = EntryField(
            body,
            "Tempo (optional)",
            "Know the song's BPM? Type it to skip the detection (40 to 240). Leave "
            "it empty to let Audio8D find it.",
            "e.g. 128",
            app.set_bpm,
            width=120,
        )
        self.speed_curve = EntryField(
            body,
            "Speed over time",
            "Optional: change the spin during the song with TIME=SECONDS pairs, e.g. "
            "0=10, 1:00=6, 2:30=10 (faster in the chorus). Takes over from Spin speed.",
            "e.g. 0=10, 1:00=6, 2:30=10",
            app.set_speed_curve,
            width=320,
        )
        self.amount_curve = EntryField(
            body,
            "Movement over time",
            "Optional: change how far it moves with TIME=AMOUNT pairs from 0 to 1, "
            "e.g. 0=0.5, 1:00=0.95. Takes over from Movement.",
            "e.g. 0=0.5, 1:00=0.95",
            app.set_intensity_curve,
            width=320,
        )
        stems = demucs_available()
        self.vocals = SwitchField(
            body,
            "Keep the singer in the middle",
            "An AI model (Demucs) separates the voice so it stays clear and close "
            "while the band moves. Takes a minute or two per song."
            if stems
            else f"Needs the free Demucs AI model: {demucs_hint()}.",
            lambda on: change(vocals="center" if on else "move"),
        )
        if not stems:
            self.vocals.enable(False)
        self.speakers = SwitchField(
            body,
            "Safe for speakers too",
            "3D sound is made for headphones. Turn this on if the song will be played "
            "on speakers or in a car: gentler left-right movement that sounds right "
            "there.",
            app.set_speakers,
        )
        widgets = (
            self.engine,
            self.path,
            self.direction,
            self.bass_on,
            self.bass,
            self.height,
            self.fade,
            self.beat,
            self.bpm,
            self.speed_curve,
            self.amount_curve,
            self.vocals,
            self.speakers,
        )
        for row, widget in enumerate(widgets):
            widget.grid(row=row, column=0, sticky="ew", pady=6)
        button(
            body,
            "clear",
            "Back to the style",
            app.reset_style,
            width=200,
            tooltip="Undo every change and use the chosen style's own values",
        ).grid(row=len(widgets), column=0, sticky="w", pady=(14, 0))

    def bass_value(self) -> float:
        """The bass slider's value, rounded to 10 Hz."""
        return float(round(self.bass.slider.get() / 10) * 10)

    def _song_styles(self, body: ctk.CTkFrame) -> None:
        """Card 4: every song with a menu, the style for all songs or one of its own."""
        top = ctk.CTkFrame(body, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)
        self.own_note = hint(top, "", margin=340)
        self.own_note.grid(row=0, column=0, sticky="ew")
        self.own_reset = button(
            top,
            "clear",
            "All songs use the style above",
            self.app.clear_song_styles,
            width=270,
            height=32,
            tooltip="Take away every song's own style",
        )
        self.own_reset.grid(row=0, column=1, padx=(10, 0))
        self.own_rows = ctk.CTkFrame(body, fg_color="transparent")
        self.own_rows.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.own_rows.grid_columnconfigure(0, weight=1)
        self.own_more = button(
            body, "add", "Show more", self.show_more_own, width=190, height=32
        )
        self.own_shown = SONGS_PER_PAGE

    def style_choices(self) -> dict[str, str | None]:
        """The menu's words -> the style each means (None: the style for all songs)."""
        choices: dict[str, str | None] = {SAME_STYLE: None}
        for preset in self.app.presets.values():
            choices[preset.label + ("   (yours)" if preset.custom else "")] = (
                preset.name
            )
        return choices

    def show_songs(self) -> None:
        """Rebuild the song menus (a page of them for a long list)."""
        for child in self.own_rows.winfo_children():
            child.destroy()
        choices = self.style_choices()
        labels = {name: label for label, name in choices.items()}
        own = self.app.settings.song_styles
        for index, entry in enumerate(self.app.rows[: self.own_shown]):
            line = ctk.CTkFrame(self.own_rows, fg_color=SURFACE_ALT, corner_radius=10)
            line.grid(row=index, column=0, sticky="ew", pady=3)
            line.grid_columnconfigure(0, weight=1)
            name = ctk.CTkLabel(line, text=entry.song.stem, font=font(13), anchor="w")
            name.grid(row=0, column=0, sticky="ew", padx=(14, 8), pady=8)
            Tooltip(name, str(entry.song))
            menu = ChoiceMenu(
                line,
                list(choices),
                lambda value, e=entry: self.app.set_song_style(e, choices.get(value)),
            )
            menu.set(labels.get(own.get(entry.song), SAME_STYLE))
            menu.grid(row=0, column=1, padx=(0, 12), pady=8)
        hidden = len(self.app.rows) - min(len(self.app.rows), self.own_shown)
        if hidden:
            self.own_more.configure(
                **icon_text("add", f"Show {min(hidden, SONGS_PER_PAGE)} more")
            )
            self.own_more.grid(row=2, column=0, sticky="w", pady=(6, 0))
        else:
            self.own_more.grid_remove()
        self.show_own_count()

    def show_own_count(self) -> None:
        """The line that says how many songs have a style of their own."""
        songs = [entry.song for entry in self.app.rows]
        count = sum(1 for song in songs if song in self.app.settings.song_styles)
        if not songs:
            text = "Add songs on step 1 first; then any of them can have its own style."
        elif count:
            has = "has its" if count == 1 else "have their"
            text = (
                f"{count} of {len(songs)} songs {has} own style; the others use the "
                "style above."
            )
        elif len(songs) == 1:
            text = "The song uses the style above. Pick another style here if you like."
        else:
            text = f"All {len(songs)} songs use the style above."
        self.own_note.configure(text=text)
        if count:
            self.own_reset.grid()
        else:
            self.own_reset.grid_remove()

    def show_more_own(self) -> None:
        """Show the next page of song menus."""
        self.own_shown += SONGS_PER_PAGE
        self.show_songs()

    def build_cards(self) -> None:
        """One card per style (built-in and saved), three to a row."""
        for child in self.cards_frame.winfo_children():
            child.destroy()
        self.cards.clear()
        for column in range(3):
            self.cards_frame.grid_columnconfigure(column, weight=1, uniform="cards")
        for index, preset in enumerate(self.app.presets.values()):
            card = self._card(preset)
            card.grid(row=index // 3, column=index % 3, sticky="nsew", padx=4, pady=4)
            self.cards[preset.name] = card

    def _card(self, preset: Preset) -> ctk.CTkFrame:
        """A clickable card for one style."""
        card = ctk.CTkFrame(
            self.cards_frame,
            fg_color=SURFACE_ALT,
            corner_radius=12,
            border_width=2,
            border_color=SURFACE_ALT,
            cursor="hand2",
        )
        card.grid_columnconfigure(0, weight=1)
        title = preset.label + (
            "   ★ best" if preset.name == RECOMMENDED_PRESET else ""
        )
        title += "   (yours)" if preset.custom else ""
        name = ctk.CTkLabel(card, text=title, font=font(13, "bold"), anchor="w")
        name.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 0))
        cfg = preset.config
        paths = {
            "circle": "Circle",
            "arc": "Front arc",
            "figure8": "Figure-8",
            "wander": "Wander",
        }
        tags = [
            "3D" if cfg.engine == "3d" else "Panning",
            paths[cfg.path],
            cfg.output_format.upper(),
        ]
        if cfg.beat_sync:
            tags.append("beat")
        if cfg.loudness_target is not None:
            tags.append(f"{cfg.loudness_target:g} LUFS")
        tag = ctk.CTkLabel(
            card, text=" · ".join(tags), font=font(11), text_color=ACCENT, anchor="w"
        )
        tag.grid(row=1, column=0, sticky="ew", padx=12)
        summary = ctk.CTkLabel(
            card,
            text=preset.summary,
            font=font(11),
            text_color=TEXT_DIM,
            anchor="w",
            justify="left",
            wraplength=220,
        )
        summary.grid(row=2, column=0, sticky="ew", padx=12, pady=(2, 10))
        for widget in (card, name, tag, summary):
            widget.bind(
                "<Button-1>", lambda _e, p=preset: self.app.choose_style(p.name)
            )
        return card

    def show(self, settings: GuiSettings) -> None:
        """Make every control match the settings, and show or hide what applies."""
        for name, card in self.cards.items():
            card.configure(
                border_color=ACCENT if name == settings.style else SURFACE_ALT
            )
        preset = self.app.presets.get(settings.style)
        changed = preset is not None and settings.differs_from(preset)
        self.style_note.configure(
            text=f"Style: {style_label(settings.style, self.app.presets)}"
            + ("   (changed by you)" if changed else "")
        )
        cfg = settings.sound
        self.movement.set(cfg.intensity)
        self.spin.set(cfg.rotation_seconds)
        self.room.set(cfg.ambience)
        self.engine.set(cfg.engine)
        self.path.set(cfg.path)
        self.direction.set(cfg.direction)
        self.bass_on.set(bool(cfg.bass_hz))
        self.bass.set(cfg.bass_hz or 120.0)
        self.bass.enable(bool(cfg.bass_hz))
        self.height.set(cfg.elevation)
        self.fade.set(cfg.fade_seconds)
        self.beat.set(cfg.beat_sync)
        self.vocals.set(cfg.vocals == "center")
        self.speakers.set(settings.speakers)
        for field, text in (
            (self.bpm, settings.bpm_text),
            (self.speed_curve, settings.speed_curve_text),
            (self.amount_curve, settings.intensity_curve_text),
        ):
            focused = str(self.focus_get() or "").startswith(str(field.entry))
            if field.entry.get() != text and not focused:
                field.set(text)
        # Show only what applies right now, and say why the rest is off
        if cfg.beat_sync or settings.bpm_text.strip():
            self.bpm.grid()
        else:
            self.bpm.grid_remove()
        speed_curve = bool(settings.speed_curve_text.strip())
        self.spin.enable(not speed_curve)
        self.spin.explain(
            "'Speed over time' (Advanced) is in charge of the spin now."
            if speed_curve
            else _SPIN_HELP
            + ("  Beat sync rounds it to whole bars." if cfg.beat_sync else "")
        )
        amount_curve = bool(settings.intensity_curve_text.strip())
        self.movement.enable(not amount_curve)
        panning = cfg.engine == "pan" or settings.speakers
        self.height.enable(not panning)
        self.height.explain(
            "Height needs the 3D engine (not panning or 'Safe for speakers')."
            if panning
            else _HEIGHT_HELP
        )
        self.engine.enable(not settings.speakers)


class OutputPage(Page):
    """Step 3: file type, loudness, where it goes, the originals, then Advanced."""

    def __init__(self, master: tk.Misc, app: "Audio8DApp") -> None:
        """Build the page."""
        super().__init__(
            master,
            "STEP 3 OF 4",
            "Output options",
            "Choose the file type, how loud it should be, and where the new songs go. "
            "The recommended choices are already selected.",
        )
        self.app = app

        basics = Card(self, "The essentials")
        self.add(basics, 2)
        self.format = ChoiceField(
            basics.body,
            "File type",
            "",
            {"MP3": "mp3", "FLAC": "flac", "WAV": "wav", "M4A": "m4a", "Opus": "opus"},
            lambda v: app.change_sound(output_format=v),
            "MP3 plays everywhere. FLAC and WAV keep every detail. M4A suits Apple. "
            "Opus makes small files.",
        )
        self.loudness = ChoiceField(
            basics.body,
            "Loudness",
            "Music apps play everything at about the same loudness. Recommended: "
            "Spotify / YouTube, so your 8D song fits in with the rest of your music. "
            "'Same as original' keeps your song's own loudness.",
            dict(LOUDNESS_CHOICES),
            self._loudness,
        )
        self.custom_loud = EntryField(
            basics.body,
            "Custom loudness",
            "In LUFS, from -30 (quiet) to -5 (very loud). -14 is the music-app "
            "standard.",
            "-14",
            app.set_custom_loudness,
            width=100,
        )
        self.save_in = ChoiceField(
            basics.body,
            "Save the new songs",
            "Next to each original song, or all in one folder of your choice.",
            {"Next to each original": "next", "In a folder I choose": "folder"},
            self._place,
        )
        self.folder_row = ctk.CTkFrame(basics.body, fg_color="transparent")
        self.folder_row.grid_columnconfigure(0, weight=1)
        self.folder = ctk.CTkEntry(
            self.folder_row, placeholder_text="Choose a folder…", font=font(12)
        )
        self.folder.grid(row=0, column=0, sticky="ew", padx=(160, 10))
        self.folder.bind("<KeyRelease>", lambda _e: self._folder_typed())
        button(
            self.folder_row,
            "folder",
            "Browse",
            self._browse,
            kind="primary",
            width=110,
            height=34,
        ).grid(row=0, column=1)
        self.originals = ChoiceField(
            basics.body,
            "The original songs",
            "Recommended: keep them. 'Replace' puts the 8D song in the original's "
            "place and moves the original to the Recycle Bin, so you can restore it "
            "(drives without one, like USB sticks, keep it as '<song> (original)').",
            {
                "Keep them": "keep",
                "Replace (original name)": "replace",
                "Replace (keep '(8D)')": "replace-8d",
            },
            app.set_originals,
        )
        for row, widget in enumerate(
            (
                self.format,
                self.loudness,
                self.custom_loud,
                self.save_in,
                self.folder_row,
                self.originals,
            )
        ):
            widget.grid(row=row, column=0, sticky="ew", pady=6)

        adv = Section(
            self,
            "Advanced output",
            "Bitrate, peaks, file names, album art, trimming and speed.",
        )
        self.add(adv, 3)
        self._advanced(adv.body)
        self.footer(
            4,
            lambda: app.show_page("sound"),
            "Next: review and convert",
            lambda: app.show_page("review"),
        )

    def _advanced(self, body: ctk.CTkFrame) -> None:
        """Every output option beyond the essentials."""
        app = self.app
        self.bitrate = ChoiceField(
            body,
            "Bitrate",
            "",
            {name: (None if name == "Auto" else int(name)) for name in BITRATE_CHOICES},
            lambda v: app.change_sound(bitrate=v),
        )
        self.quality = SliderField(
            body,
            "MP3 quality",
            "Used when the bitrate is Auto. 0 = best (about 245 kbps), 2 = excellent "
            "(about 190 kbps), 9 = smallest files. Recommended: 0 to 2.",
            0,
            9,
            9,
            lambda v: f"V{v:.0f}",
            lambda v: app.change_sound(quality=int(round(v))),
        )
        self.exact = SwitchField(
            body,
            "Always hit the loudness exactly",
            "Off (recommended) never squeezes the song. On shaves the very loudest "
            "peaks a little so every song lands exactly on the target.",
            lambda on: app.change_sound(exact_loudness=on),
        )
        self.ceiling = SliderField(
            body,
            "Peak roof",
            "The loudest a peak may get, so nothing crackles. Recommended: 0.84 "
            "(-1.5 dB) for MP3, M4A and Opus; 0.89 is fine for FLAC and WAV.",
            0.5,
            1.0,
            50,
            lambda v: f"{v:.2f}",
            lambda v: app.change_sound(limiter_ceiling=round(v, 2)),
        )
        self.naming = ChoiceField(
            body,
            "New file name",
            "",
            {
                "'<song> (8D)'": "8d",
                "Same as the original": "original",
                "Custom…": "custom",
            },
            app.set_name_style,
        )
        self.custom_name = EntryField(
            body,
            "Custom name",
            "Only for a single song. The right ending (.mp3, .flac…) is added for you.",
            "e.g. My Song 8D version",
            app.set_custom_name,
            width=320,
        )
        self.overwrite = SwitchField(
            body,
            "Replace 8D files that already exist",
            "Off (recommended): songs that already have an 8D version are skipped. "
            "On: they are made again and the old 8D file is replaced.",
            lambda on: setattr(app.settings, "overwrite", on),
        )
        self.cover = SwitchField(
            body,
            "Keep the album picture",
            "Copies the cover art into the new file (MP3, FLAC and M4A can hold it).",
            lambda on: setattr(app.settings, "keep_cover", on),
        )
        self.title_tag = SwitchField(
            body,
            "Add ' (8D)' to the song title",
            "So your music app lists the 8D version as its own track.",
            lambda on: setattr(app.settings, "tag_title", on),
        )
        self.checking = SwitchField(
            body,
            "Check each finished song",
            "Measures loudness, peaks and how it sounds on one speaker, and shows the "
            "result. Takes a second; recommended ON.",
            lambda on: setattr(app.settings, "check", on),
        )
        trim = ctk.CTkFrame(body, fg_color="transparent")
        self.start = EntryField(
            trim,
            "Only part: from",
            "Optional. Leave both empty for the whole song.",
            "e.g. 1:00",
            lambda t: self._time(t, "trim_start"),
            width=110,
        )
        self.end = EntryField(
            trim,
            "to",
            "Great for ringtones and short clips.",
            "e.g. 1:30",
            lambda t: self._time(t, "trim_end"),
            width=110,
        )
        self.start.grid(row=0, column=0, sticky="w")
        self.end.grid(row=0, column=1, sticky="w", padx=(20, 0))
        self.end.label.configure(width=30)
        self.jobs = SliderField(
            body,
            "Songs at once",
            "Several songs can be made at the same time. More is faster on computers "
            "with many cores; a good value for this computer is already set.",
            1,
            8,
            7,
            lambda v: f"{v:.0f}",
            lambda v: setattr(app.settings, "jobs", int(round(v))),
        )
        self.play = SwitchField(
            body,
            "Play the first song when finished",
            "Opens the first new song in your music player straight away.",
            lambda on: setattr(app.settings, "play_when_done", on),
        )
        widgets = (
            self.bitrate,
            self.quality,
            self.exact,
            self.ceiling,
            self.naming,
            self.custom_name,
            self.overwrite,
            self.cover,
            self.title_tag,
            self.checking,
            trim,
            self.jobs,
            self.play,
        )
        for row, widget in enumerate(widgets):
            widget.grid(row=row, column=0, sticky="ew", pady=6)

    def _time(self, text: str, key: str) -> str | None:
        """A trim box changed: store it, and complain if it isn't a time."""
        setattr(self.app.settings, key, text)
        self.app.refresh_status()
        if text.strip() and _problem(lambda: parse_time(text)):
            return "Write a time like 90 (seconds) or 1:30 (minutes:seconds)."
        return None

    def _loudness(self, value: object) -> None:
        """A loudness choice was picked."""
        settings = self.app.settings
        if value == "custom":
            settings.loudness_is_custom = True
            settings.change(match_loudness=False)
            self.app.set_custom_loudness(self.custom_loud.entry.get() or "-14")
        elif value == "match":
            settings.loudness_is_custom = False
            settings.change(match_loudness=True, loudness_target=None)
        else:
            settings.loudness_is_custom = False
            settings.change(match_loudness=False, loudness_target=value)
        self.app.sync_controls()

    def _place(self, value: object) -> None:
        """Next to the originals, or in a chosen folder."""
        self.wants_folder = value == "folder"
        if not self.wants_folder:
            self.app.settings.destination = ""
        elif not self.folder.get().strip():
            self._browse()
            return
        else:
            self.app.settings.destination = self.folder.get().strip()
        self.app.sync_controls()

    def _folder_typed(self) -> None:
        """The folder box was edited by hand."""
        self.app.settings.destination = self.folder.get().strip()
        self.app.refresh_status()

    def _browse(self) -> None:
        """Pick the output folder."""
        chosen = filedialog.askdirectory(title="Where should the 8D songs go?")
        if chosen:
            self.folder.delete(0, "end")
            self.folder.insert(0, str(Path(chosen)))
            self.app.settings.destination = str(Path(chosen))
            self.wants_folder = True
        self.app.sync_controls()

    wants_folder = False

    def show(self, settings: GuiSettings) -> None:
        """Make every control match the settings, and show or hide what applies."""
        cfg = settings.sound
        self.format.set(cfg.output_format)
        self.format.explain(
            {
                "mp3": "MP3: plays on everything; 320 kbps is the best MP3 can be.",
                "flac": "FLAC 24-bit: nothing is lost at all; keeps the album art.",
                "wav": "WAV 24-bit: nothing is lost; big files, and no album picture.",
                "m4a": "M4A (AAC): great for iPhone and iTunes; keeps the album art.",
                "opus": "Opus: small files that still sound great; no album picture.",
            }[cfg.output_format]
        )
        if settings.loudness_is_custom:
            self.loudness.set("custom")
            self.custom_loud.grid()
        else:
            self.loudness.set("match" if cfg.match_loudness else cfg.loudness_target)
            self.custom_loud.grid_remove()
        has_target = cfg.wants_loudness or settings.loudness_is_custom
        self.exact.set(cfg.exact_loudness)
        self.exact.enable(has_target)
        self.exact.explain(
            "Off (recommended) never squeezes the song. On shaves the very loudest "
            "peaks a little so every song lands exactly on the target."
            if has_target
            else "Only used when a loudness target is chosen above."
        )
        in_folder = bool(settings.destination) or self.wants_folder
        self.save_in.set("folder" if in_folder else "next")
        if in_folder:
            self.folder_row.grid()
        else:
            self.folder_row.grid_remove()
        self.originals.set(settings.originals)

        lossless = cfg.output_format in {"flac", "wav"}
        self.bitrate.set(cfg.bitrate)
        self.bitrate.enable(not lossless)
        self.bitrate.explain(
            "FLAC and WAV are lossless, so there is no bitrate to choose."
            if lossless
            else "Detail per second for MP3, M4A and Opus. 320 is the most MP3 allows "
            "and the best. Auto: MP3 uses the quality below; M4A 256; Opus 192."
        )
        if cfg.output_format == "mp3" and cfg.bitrate is None:
            self.quality.grid()
        else:
            self.quality.grid_remove()
        self.quality.set(cfg.quality)
        self.ceiling.set(cfg.limiter_ceiling)
        replacing = settings.originals != "keep"
        self.naming.set(settings.name_style)
        self.naming.enable(not replacing)
        one_song = len(self.app.rows) == 1
        self.naming.explain(
            "Set by 'The original songs' above while replacing."
            if replacing
            else "'<song> (8D)' (recommended) sits next to the original without "
            "clashing. "
            "'Same as the original' needs a different folder. "
            + ("Custom: type any name." if one_song else "Custom works with one song.")
        )
        if settings.name_style == "custom" and not replacing:
            self.custom_name.grid()
        else:
            self.custom_name.grid_remove()
        self.overwrite.set(settings.overwrite)
        can_cover = cfg.output_format in {"mp3", "flac", "m4a"}
        self.cover.set(settings.keep_cover)
        self.cover.enable(can_cover)
        self.cover.explain(
            "Copies the cover art into the new file."
            if can_cover
            else f"{cfg.output_format.upper()} files can't hold an album picture."
        )
        self.title_tag.set(settings.tag_title)
        self.checking.set(settings.check)
        self.jobs.set(settings.jobs)
        self.play.set(settings.play_when_done)


class RunRow(ctk.CTkFrame):
    """One song while converting: status, progress, then the result and buttons."""

    def __init__(self, master: tk.Misc, song: Path) -> None:
        """Draw the row in its waiting state."""
        super().__init__(master, fg_color=SURFACE_ALT, corner_radius=10)
        self.song = song
        self.grid_columnconfigure(1, weight=1)
        self.icon = ctk.CTkLabel(
            self,
            text=Icons.glyph("music"),
            font=Icons.font(18),
            text_color=TEXT_DIM,
            width=36,
        )
        self.icon.grid(row=0, column=0, rowspan=2, padx=(12, 6), pady=10)
        ctk.CTkLabel(self, text=song.stem, font=font(13, "bold"), anchor="w").grid(
            row=0, column=1, sticky="ew", pady=(10, 0)
        )
        self.status = ctk.CTkLabel(
            self,
            text="Waiting",
            font=font(12),
            text_color=TEXT_DIM,
            anchor="w",
            justify="left",
            wraplength=520,
        )
        self.status.grid(row=1, column=1, sticky="ew", pady=(0, 10))
        fit_width(self.status, self, 540)
        self.strip = ctk.CTkProgressBar(
            self, width=200, height=8, progress_color=ACCENT
        )
        self.strip.set(0)
        self.strip.grid(row=0, column=2, rowspan=2, padx=12)
        # Button-wide but 1 px tall until the buttons arrive, so every bar lines up
        self.actions = ctk.CTkFrame(self, fg_color="transparent", width=198, height=1)
        self.actions.grid(row=0, column=3, rowspan=2, padx=(0, 12))

    def progress(self, stage: str, share: float, stages: list[str]) -> None:
        """Show which step it is on and how far."""
        step = stages.index(stage) if stage in stages else 0
        shown, percent = stage, int(share * 100)
        # A finished step means the next has begun, so say that rather than "100%"
        if share >= 1.0 and step + 1 < len(stages):
            shown, percent = stages[step + 1], 0
        self.status.configure(
            text=f"{_STAGE_WORDS.get(shown, shown)}… {percent}%",
            text_color=WARNING,
        )
        self.strip.set(min(1.0, (step + share) / max(1, len(stages))))

    def finished(self, outcome: BatchOutcome) -> None:
        """A tick, the measured result and Play/Folder buttons - or why it failed."""
        self.strip.set(1.0)
        result = outcome.result
        if result is None:
            error = outcome.error
            fix = gui_words(hints.fix_for(error) or "") if error else ""
            # One readable line here; FFmpeg's full log goes to Technical details
            LOG.error("%s failed: %s", self.song.name, error)
            words = gui_words(hints.short_message(error)) if error else ""
            text = words + (f"\nWhat to do: {fix}" if fix else "")
            self.status.configure(text=text, text_color=DANGER)
            self.icon.configure(text=Icons.glyph("error"), text_color=DANGER)
            self.strip.configure(progress_color=DANGER)
            return
        parts = [f"Saved as {result.output.name}"]
        if result.quality:
            report = result.quality
            parts.append(
                f"{report.integrated_lufs:.1f} LUFS, "
                f"peaks {report.true_peak_db:.1f} dBTP"
                + (", mono-safe" if report.mono_safe else ", weak on one speaker")
            )
        if result.bpm:
            parts.append(
                f"{result.bpm:g} BPM, one circle = {result.beats_per_turn} beats"
            )
        elif result.config.beat_sync:
            parts.append("no clear beat, so the spin kept its own speed")
        if result.original_removed_to:
            parts.append(f"original {describe_removal(result.original_removed_to)}")
        self.status.configure(text="  ·  ".join(parts), text_color=SUCCESS)
        self.icon.configure(text=Icons.glyph("check"), text_color=SUCCESS)
        self.strip.configure(progress_color=SUCCESS)
        output = result.output
        button(
            self.actions, "play", "Play", lambda: open_path(output), width=90, height=32
        ).pack(side="left", padx=2)
        button(
            self.actions,
            "open",
            "Folder",
            lambda: open_path(output.parent),
            width=100,
            height=32,
        ).pack(side="left", padx=2)


class ReviewPage(Page):
    """Step 4: a plain-word summary, warnings, problems, then the conversion itself."""

    def __init__(self, master: tk.Misc, app: "Audio8DApp") -> None:
        """Build the page."""
        super().__init__(
            master,
            "STEP 4 OF 4",
            "Review and convert",
            "Check your choices, try a preview if you like, then press Start "
            "converting.",
        )
        self.app = app
        # Songs past the first page of progress rows: [made, failed, how many]
        self.rest = [0, 0, 0]
        self.rest_line: ctk.CTkLabel | None = None
        self.summary = Card(self, "Your choices")
        self.add(self.summary, 2)
        self.notes = ctk.CTkFrame(self, fg_color="transparent")
        self.add(self.notes, 3, (0, 8))
        self.notes.grid_columnconfigure(0, weight=1)

        actions = Card(
            self,
            "Try it, then make it",
            "A preview makes a short sample from the loudest part (usually the "
            "chorus). "
            "A/B compare plays the original, a pause, then the 8D version at the same "
            "loudness, so you hear only the effect.",
        )
        self.add(actions, 4)
        strip = actions.body
        self.preview_length = SliderField(
            strip,
            "Preview length",
            "",
            10,
            60,
            10,
            lambda v: f"{v:.0f} s",
            lambda v: setattr(app.settings, "preview_seconds", int(round(v))),
        )
        self.preview_length.help.grid_remove()
        self.preview_length.grid(
            row=0, column=0, columnspan=5, sticky="ew", pady=(0, 6)
        )
        self.for_song = hint(strip, "")
        self.for_song.grid(row=1, column=0, columnspan=5, sticky="ew", pady=(0, 12))
        self.preview = button(
            strip,
            "preview",
            "Preview",
            app.run_preview,
            width=130,
            tooltip="Make and play a short sample of the chosen song (Ctrl+P)",
        )
        self.preview.grid(row=2, column=0, sticky="w")
        self.compare = button(
            strip,
            "compare",
            "A/B compare",
            app.run_compare,
            width=150,
            tooltip="Original, a short pause, then 8D - at the same loudness",
        )
        self.compare.grid(row=2, column=1, sticky="w", padx=8)
        strip.grid_columnconfigure(2, weight=1)
        self.stop = button(
            strip,
            "stop",
            "Stop",
            app.stop,
            kind="danger",
            width=110,
            tooltip="Stop after the current step; finished songs are kept (Esc)",
        )
        self.stop.grid(row=2, column=3, padx=8)
        self._stop_look(busy=False)
        self.start = button(
            strip,
            "play",
            "Start converting",
            app.run_convert,
            kind="primary",
            width=210,
            tooltip="Make the 8D version of every song on the list (Ctrl+Enter)",
        )
        self.start.grid(row=2, column=4)

        self.run_card = Card(
            self,
            "Progress",
            "Each song shows its own progress and, when it's done, its measured "
            "result with Play and Folder buttons.",
        )
        self.add(self.run_card, 5)
        self.run_list = self.run_card.body
        hint(self.run_list, "Nothing has been converted yet.").grid(
            row=0, column=0, sticky="w"
        )

        self.details = Section(
            self,
            "Technical details",
            "What Audio8D is doing behind the scenes (more with 'Show technical "
            "details' in Settings). Useful when asking for help.",
        )
        self.add(self.details, 6, (0, 28))
        self.log = ctk.CTkTextbox(
            self.details.body, height=180, font=("Consolas", 11), wrap="word"
        )
        self.log.grid(row=0, column=0, sticky="ew")
        self.log.configure(state="disabled")

    def write_log(self, text: str) -> None:
        """Add a line to the technical details."""
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def set_busy(self, busy: bool) -> None:
        """Lock the buttons while work runs."""
        for widget in (self.preview, self.compare, self.start):
            widget.configure(state="disabled" if busy else "normal")
        self._stop_look(busy)

    def _stop_look(self, busy: bool) -> None:
        """Red only while there is something to stop; a quiet outline otherwise."""
        ink = WHITE if busy else TEXT_DIM
        self.stop.configure(
            state="normal" if busy else "disabled",
            fg_color=DANGER if busy else "transparent",
            border_width=0 if busy else 1,
            text_color_disabled=TEXT_DIM,
            **icon_text("stop", "Stop", 16, ink),
        )

    def show(self, settings: GuiSettings) -> None:
        """Rebuild the summary, the problems and the warnings."""
        body = self.summary.body
        for child in body.winfo_children():
            child.destroy()
        songs = [(row.song, row.folder) for row in self.app.rows]
        count = len(songs)
        lines = [
            (
                "Songs",
                f"{count} song{'s' if count != 1 else ''}" if count else "none yet",
            )
        ]
        own = own_styles_line(settings, songs, self.app.presets)
        if own:
            lines.append(("Own styles", own))
        try:
            lines += review(settings, self.app.presets)
        except Audio8DError:
            pass
        body.grid_columnconfigure(1, weight=1)
        for row, (label, value) in enumerate(lines):
            ctk.CTkLabel(
                body,
                text=label,
                font=font(13),
                text_color=TEXT_DIM,
                width=120,
                anchor="w",
            ).grid(row=row, column=0, sticky="nw", pady=2)
            value_label = ctk.CTkLabel(
                body,
                text=value,
                font=font(13),
                anchor="w",
                justify="left",
                wraplength=640,
            )
            value_label.grid(row=row, column=1, sticky="ew", pady=2)
            fit_width(value_label, body, 150)

        for child in self.notes.winfo_children():
            child.destroy()
        found = problems(settings, songs, self.app.presets)
        row = 0
        for page, text in found:
            self._note(row, "error", text, (DANGER, DANGER_SOFT), page)
            row += 1
        read = [(e.song.stem, e.info) for e in self.app.rows if e.info is not None]
        for text in warnings(settings) + source_notes(read):
            self._note(row, "warning", text, (WARNING, WARNING_SOFT), None)
            row += 1
        if not found:
            self._note(
                row,
                "check",
                "Everything is ready. Press Start converting when you are.",
                (SUCCESS, ACCENT_SOFT),
                None,
            )
        self.start.configure(state="disabled" if found or self.app.busy else "normal")
        chosen = self.app.chosen_song()
        self.for_song.configure(
            text=f"Preview and A/B use: {chosen.song.name}  (click another song on "
            "step 1 to choose it)."
            if chosen
            else "Add a song on step 1 to try a preview."
        )
        self.preview_length.set(settings.preview_seconds)

    def _note(
        self,
        row: int,
        icon: str,
        text: str,
        colors: tuple[tuple[str, str], tuple[str, str]],
        page: str | None,
    ) -> None:
        """One coloured line: a problem (with 'Fix it'), a warning, or all clear."""
        color, fill = colors
        note = ctk.CTkFrame(self.notes, fg_color=fill, corner_radius=10)
        note.grid(row=row, column=0, sticky="ew", pady=3)
        note.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            note, text=Icons.glyph(icon), font=Icons.font(15), text_color=color
        ).grid(row=0, column=0, padx=(14, 10), pady=10)
        message = ctk.CTkLabel(
            note, text=text, font=font(13), anchor="w", justify="left", wraplength=640
        )
        message.grid(row=0, column=1, sticky="ew", pady=10)
        fit_width(message, note, 150 if page else 60)
        if page:
            ctk.CTkButton(
                note,
                text="Fix it",
                width=80,
                fg_color=color,
                hover_color=color,
                command=lambda: self.app.show_page(page),
            ).grid(row=0, column=2, padx=12)

    def start_run(self, songs: list[Path]) -> list[RunRow]:
        """Fresh progress rows for a new conversion (a page of them, then a total)."""
        for child in self.run_list.winfo_children():
            child.destroy()
        rows = []
        for index, song in enumerate(songs[:SONGS_PER_PAGE]):
            row = RunRow(self.run_list, song)
            row.grid(row=index, column=0, sticky="ew", pady=3)
            rows.append(row)
        # Songs past the first page share one line; any that fail get a row too
        self.rest = [0, 0, len(songs) - len(rows)]
        self.rest_line = None
        if self.rest[2]:
            self.rest_line = ctk.CTkLabel(
                self.run_list, text="", font=font(13), text_color=TEXT_DIM, anchor="w"
            )
            # After every row a failure could add; Tk counts grid rows below 10,000
            last = min(len(songs) + 1, _GRID_ROWS - 1)
            self.rest_line.grid(row=last, column=0, sticky="ew", padx=14, pady=8)
            self._show_rest(len(rows))
        return rows

    def _show_rest(self, first: int) -> None:
        """Update the line that stands for the songs past the first page."""
        made, failed, total = self.rest
        if self.rest_line is not None:
            waiting = total - made - failed
            self.rest_line.configure(
                text=f"Songs {first + 1} to {first + total}: {made} made"
                + (f", {failed} failed (shown above)" if failed else "")
                + (f", {waiting} still to go" if waiting else "")
                + "."
            )

    def rest_finished(self, first: int, outcome: BatchOutcome) -> None:
        """A song past the first page finished: count it, and show it if it failed."""
        if outcome.result is not None:
            self.rest[0] += 1
        else:
            self.rest[1] += 1
            row = RunRow(self.run_list, outcome.item.source)
            place = min(first + self.rest[1], _GRID_ROWS - 2)
            row.grid(row=place, column=0, sticky="ew", pady=3)
            row.finished(outcome)
        self._show_rest(first)


# How a style name should look, shown under every name box
NAME_HELP = (
    "Words that each start with a capital, with or without spaces: Sunset Drive or "
    "SunsetDrive. Type it any way you like: 'sunset drive' becomes Sunset Drive."
)
_LEVEL_COLOURS = {"error": DANGER, "warning": WARNING, "tip": TEXT_DIM}


class StylesPage(Page):  # pylint: disable=too-many-instance-attributes
    """Create, save, rename, share and manage your own styles."""

    def __init__(self, master: tk.Misc, app: "Audio8DApp") -> None:
        """Build the page."""
        super().__init__(
            master,
            "",
            "Your styles",
            "Make a style of your own, then use it on step 2 like the built-in ones: "
            "for all songs, or just some. Your styles stay on this computer, and can "
            "be exported to share and imported back.",
        )
        self.app = app
        self.answers = suggested_answers("mixed")
        # Set once the name or description is typed, so suggestions stop replacing it
        self.name_typed = False
        self.summary_typed = False
        self.suggested = ("", "")
        self.notes: list[StyleNote] = []
        self._build_creator()

        save = Card(
            self,
            "Or save your current settings",
            "Everything from steps 2 and 3 that shapes the sound, the file type and "
            "the loudness is saved (not the songs, folders or file names).",
        )
        self.add(save, 3)
        self.name = EntryField(
            save.body,
            "Name",
            NAME_HELP,
            "e.g. Party Mix",
            lambda text: self._name_typed(self.name, text),
            width=260,
        )
        self.name.grid(row=0, column=0, sticky="ew", pady=4)
        self.summary = EntryField(
            save.body,
            "Description",
            "Optional: a few words to remind you what it's for.",
            "e.g. big figure-8 for parties",
            lambda _t: None,
            width=420,
        )
        self.summary.grid(row=1, column=0, sticky="ew", pady=4)
        button(
            save.body, "save", "Save style", self._save, kind="primary", width=150
        ).grid(row=2, column=0, sticky="w", pady=(10, 0))

        self.saved = Card(self, "Saved styles", f"Stored in {presets_file()}")
        self.add(self.saved, 4, (0, 28))
        self.refresh()

    # ------------------------------------------------------------ the creator

    def _build_creator(self) -> None:
        """The guided 'Create your own style' card."""
        card = Card(
            self,
            "Create your own style",
            "Answer a few questions. Audio8D turns your answers into the right "
            "settings, checks them, and suggests a name. Try it on a song, then save.",
        )
        self.add(card, 2)
        body = card.body
        self.q_music = ChoiceField(
            body,
            "Music",
            "What will you listen to? Strong beat: dance, pop, hip-hop. Calm: chill, "
            "acoustic, lo-fi. Big and loud: rock, EDM, film music. Talking: podcasts, "
            "audiobooks. Picking one fills in good answers below.",
            MUSIC_CHOICES,  # type: ignore[arg-type]
            self._music_picked,
        )
        self.q_movement = ChoiceField(
            body,
            "Movement",
            "How far should it travel round your head? Gentle is relaxing; Clear is "
            "the classic 8D feeling (recommended); Big goes right into each ear.",
            MOVEMENT_CHOICES,  # type: ignore[arg-type]
            lambda value: self._answer(movement=str(value)),
        )
        self.q_speed = ChoiceField(
            body,
            "Speed",
            "How fast should it go round? Slow: one circle every 12 s. Normal: every "
            "8 s (recommended). Fast: every 5 s. With the beat: follows the song.",
            SPEED_CHOICES,  # type: ignore[arg-type]
            lambda value: self._answer(speed=str(value)),
        )
        self.q_room = ChoiceField(
            body,
            "Room",
            "How much room sound? None is dry, best for talking. A little makes "
            "music feel around you (recommended). A big hall can blur voices.",
            ROOM_CHOICES,  # type: ignore[arg-type]
            lambda value: self._answer(room=str(value)),
        )
        self.q_place = ChoiceField(
            body,
            "Listen on",
            "3D sound is made for headphones. 'Speakers or a car too' makes a "
            "gentler version that sounds right everywhere.",
            PLACE_CHOICES,  # type: ignore[arg-type]
            lambda value: self._answer(place=str(value)),
        )
        self.q_file = ChoiceField(
            body,
            "File type",
            "MP3 plays everywhere, at the best MP3 quality. FLAC keeps every detail "
            "(bigger files). M4A suits iPhone and iTunes.",
            FILE_CHOICES,  # type: ignore[arg-type]
            lambda value: self._answer(file_type=str(value)),
        )
        self.q_level = ChoiceField(
            body,
            "Loudness",
            "Like music apps: as loud as Spotify and YouTube (recommended). Same as "
            "the song: keeps each song's own loudness. Natural: can be quieter.",
            LEVEL_CHOICES,  # type: ignore[arg-type]
            lambda value: self._answer(level=str(value)),
        )
        self.new_name = EntryField(
            body,
            "Name",
            NAME_HELP,
            "e.g. Sunset Drive",
            self._new_name_typed,
            width=260,
        )
        self.new_summary = EntryField(
            body,
            "Description",
            "A few words so you remember what it's for. One is written for you; "
            "change it if you like.",
            "e.g. calm songs for late nights",
            self._new_summary_typed,
            width=460,
        )
        fields = (
            self.q_music,
            self.q_movement,
            self.q_speed,
            self.q_room,
            self.q_place,
            self.q_file,
            self.q_level,
            self.new_name,
            self.new_summary,
        )
        for row, widget in enumerate(fields):
            widget.grid(row=row, column=0, sticky="ew", pady=5)
        result = ctk.CTkFrame(body, fg_color=SURFACE_ALT, corner_radius=10)
        result.grid(row=len(fields), column=0, sticky="ew", pady=(10, 4))
        result.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(result, text="Your style", font=font(13, "bold"), anchor="w").grid(
            row=0, column=0, sticky="ew", padx=14, pady=(10, 0)
        )
        self.result = ctk.CTkLabel(
            result, text="", font=font(12), anchor="w", justify="left"
        )
        self.result.grid(row=1, column=0, sticky="ew", padx=14, pady=(2, 10))
        self.checks = ctk.CTkFrame(body, fg_color="transparent")
        self.checks.grid(row=len(fields) + 1, column=0, sticky="ew")
        self.checks.grid_columnconfigure(0, weight=1)
        strip = ctk.CTkFrame(body, fg_color="transparent")
        strip.grid(row=len(fields) + 2, column=0, sticky="ew", pady=(10, 0))
        strip.grid_columnconfigure(1, weight=1)
        self.improve = button(
            strip,
            "check",
            "Improve it for me",
            self._improve,
            width=200,
            tooltip="Change the answers the quality check points out",
        )
        self.improve.grid(row=0, column=0, sticky="w")
        button(
            strip,
            "preview",
            "Try it",
            lambda: self.app.run_preview(guided_config(self.answers)),
            width=130,
            tooltip="Make and play a short preview of the chosen song with this style",
        ).grid(row=0, column=2, padx=8)
        button(
            strip, "save", "Save style", self._create, kind="primary", width=160
        ).grid(row=0, column=3)
        self._show_answers()

    def _music_picked(self, value: object) -> None:
        """A kind of music was picked: fill in good answers for it."""
        self.answers = suggested_answers(str(value))
        self._show_answers()

    def _answer(self, **answer: str) -> None:
        """One answer changed."""
        self.answers = dataclasses.replace(self.answers, **answer)
        self._show_creator()

    def _show_answers(self) -> None:
        """Show every answer, then what they make."""
        answers = self.answers
        for field, value in (
            (self.q_music, answers.music),
            (self.q_movement, answers.movement),
            (self.q_speed, answers.speed),
            (self.q_room, answers.room),
            (self.q_place, answers.place),
            (self.q_file, answers.file_type),
            (self.q_level, answers.level),
        ):
            field.set(value)
        self._show_creator()

    def _show_creator(self) -> None:
        """Refresh the suggested name and description, the summary and the check."""
        config = guided_config(self.answers)
        name = suggested_name(self.answers, self.taken())
        summary = suggested_description(self.answers)
        if not self.name_typed and self.new_name.entry.get() in ("", self.suggested[0]):
            self.new_name.set(name)
            self._name_typed(self.new_name, name)
        if not self.summary_typed:
            self.new_summary.set(summary)
        self.suggested = (name, summary)
        self.result.configure(text=style_summary(config))
        self.notes = style_check(config, self.new_summary.entry.get())
        for child in self.checks.winfo_children():
            child.destroy()
        if not self.notes:
            self.notes_line(
                "check", "Quality check: this style looks good.", SUCCESS, 0
            )
        for row, note in enumerate(self.notes):
            icon = {"error": "error", "warning": "warning"}.get(note.level, "info")
            self.notes_line(icon, note.text, _LEVEL_COLOURS[note.level], row)
        if any(note.fix for note in self.notes):
            self.improve.grid()
        else:
            self.improve.grid_remove()

    def notes_line(
        self, icon: str, text: str, colour: tuple[str, str], row: int
    ) -> None:
        """One line of the quality check."""
        line = ctk.CTkFrame(self.checks, fg_color="transparent")
        line.grid(row=row, column=0, sticky="ew", pady=2)
        line.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            line, text=Icons.glyph(icon), font=Icons.font(14), text_color=colour
        ).grid(row=0, column=0, padx=(0, 8))
        message = ctk.CTkLabel(
            line, text=text, font=font(12), text_color=colour, anchor="w",
            justify="left", wraplength=640,
        )  # fmt: skip
        message.grid(row=0, column=1, sticky="ew")
        fit_width(message, line, 40)

    def _new_name_typed(self, text: str) -> str | None:
        """The creator's name box."""
        self.name_typed = bool(text.strip()) and text != self.suggested[0]
        return self._name_typed(self.new_name, text)

    def _new_summary_typed(self, text: str) -> None:
        """The creator's description box (any text is fine, even none)."""
        self.summary_typed = text != self.suggested[1]
        self._show_creator()

    def _improve(self) -> None:
        """Follow the quality check's advice."""
        self.answers = improve_answers(self.answers, self.notes)
        self._show_answers()
        Toast(self.app, "Improved: the answers now follow the advice", "ok")

    def _create(self) -> None:
        """Save the style the answers make."""
        config = guided_config(self.answers)
        if self._store(self.new_name, config, self.new_summary.entry.get()):
            self.name_typed = self.summary_typed = False
            self.new_name.set("")
            self._show_creator()

    # ------------------------------------------------------------ saving

    def taken(self) -> list[str]:
        """The names of your saved styles."""
        return [preset.name for preset in self.app.presets.values() if preset.custom]

    def check_name(
        self, text: str, keep: str | None = None
    ) -> tuple[str | None, str | None]:
        """(the name it will get, None), or (None, why it can't be used)."""
        try:
            return check_style_name(text, self.taken(), keep=keep), None
        except Audio8DError as exc:
            return None, gui_words(str(exc)) + "."

    def _name_typed(self, field: EntryField, text: str) -> str | None:
        """A name box changed: say what it becomes, or why it can't be used."""
        if not text.strip():
            field.explain(NAME_HELP)
            return None
        name, problem = self.check_name(text)
        if name:
            field.explain(f"It will be saved as {name}.", SUCCESS)
        return problem

    def _save(self) -> None:
        """Save the current settings under the typed name."""
        try:
            config = config_for(self.app.settings)
        except Audio8DError as exc:
            self.name.explain(f"Fix the settings first: {gui_words(str(exc))}.", DANGER)
            return
        if self._store(self.name, config, self.summary.entry.get()):
            self.name.set("")
            self.summary.set("")
            self.name.explain(NAME_HELP)

    def _store(self, field: EntryField, config: EffectConfig, summary: str) -> bool:
        """Check a new style fully, offer to improve it, then save it."""
        name, problem = self.check_name(field.entry.get())
        if name is None:
            field.entry.configure(border_color=DANGER)
            field.explain(problem or "Type a name first.", DANGER)
            return False
        notes = style_check(config, summary)
        errors = [note for note in notes if note.level == "error"]
        if errors:
            field.explain(errors[0].text, DANGER)
            return False
        warnings_ = [note for note in notes if note.level == "warning"]
        if warnings_:
            answer = Dialog(
                self.app,
                "Save it as it is?",
                "The quality check found something that may not sound its best:\n\n"
                + "\n".join(f"•  {note.text}" for note in warnings_)
                + "\n\nImprove and save follows the advice for you.",
                [
                    ("Go back", "no"),
                    ("Save as it is", "as-is"),
                    ("Improve and save", "improve"),
                ],
                icon="warning",
                color=WARNING,
            ).ask()
            if answer not in ("as-is", "improve"):
                return False
            if answer == "improve":
                config = improved(config, warnings_)
        try:
            saved = save_user_preset(
                name, config, based_on=self.app.settings.style, summary=summary
            )
        except Audio8DError as exc:
            field.explain(gui_words(str(exc)) + ".", DANGER)
            return False
        field.explain(
            f"Saved '{saved}'. It's now on step 2 with the other styles.", SUCCESS
        )
        self.app.reload_styles(select=saved)
        Toast(self.app, f"Saved your style '{saved}'", "ok")
        return True

    # ------------------------------------------------------------ saved styles

    def refresh(self) -> None:
        """List the saved styles, each with what can be done with it."""
        body = self.saved.body
        for child in body.winfo_children():
            child.destroy()
        if self.app.styles_problem:
            problem = ctk.CTkLabel(
                body,
                text=f"Your saved styles can't be shown, because the styles file has "
                f"a mistake: {self.app.styles_problem}. Fix that line in "
                f"{presets_file()} (any text editor), or delete the file to start "
                "again. Built-in styles still work.",
                font=font(13),
                text_color=DANGER,
                anchor="w",
                justify="left",
                wraplength=700,
            )
            problem.grid(row=0, column=0, sticky="ew")
            fit_width(problem, body, 10)
            return
        top = ctk.CTkFrame(body, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top.grid_columnconfigure(0, weight=1)
        mine = [p for p in self.app.presets.values() if p.custom]
        hint(
            top,
            f"{len(mine)} saved style{'s' if len(mine) != 1 else ''}."
            if mine
            else "No saved styles yet. Create one above, or import a style file.",
            margin=260,
        ).grid(row=0, column=0, sticky="ew")
        button(
            top,
            "open",
            "Import a style…",
            self._import,
            width=190,
            height=32,
            tooltip="Add a style from a file exported by Audio8D",
        ).grid(row=0, column=1, padx=(10, 0))
        for index, preset in enumerate(mine, start=1):
            self._saved_row(body, index, preset)

    def _saved_row(self, body: ctk.CTkFrame, index: int, preset: Preset) -> None:
        """One saved style: its name and description, then its buttons."""
        row = ctk.CTkFrame(body, fg_color=SURFACE_ALT, corner_radius=10)
        row.grid(row=index, column=0, sticky="ew", pady=3)
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            row, text=Icons.glyph("star"), font=Icons.font(14), text_color=ACCENT
        ).grid(row=0, column=0, padx=12, pady=(10, 0))
        title = ctk.CTkLabel(
            row,
            text=f"{preset.name}  ·  {preset.summary}",
            font=font(13),
            anchor="w",
            justify="left",
            wraplength=640,
        )
        title.grid(row=0, column=1, sticky="ew", pady=(10, 0), padx=(0, 12))
        fit_width(title, row, 60)
        actions = ctk.CTkFrame(row, fg_color="transparent")
        # Under the star as well, so five buttons fit the narrowest window at 125 %
        actions.grid(row=1, column=0, columnspan=2, sticky="w", padx=12, pady=(6, 10))
        name = preset.name
        for key, (icon, text, command, kind) in enumerate(
            (
                (
                    "check",
                    "Use",
                    lambda: self.app.choose_style(name, go=True),
                    "primary",
                ),
                ("save", "Rename", lambda: self._rename(name), "outline"),
                ("add", "Duplicate", lambda: self._duplicate(name), "outline"),
                ("open", "Export", lambda: self._export(name), "outline"),
                ("delete", "Delete", lambda: self._delete(name), "outline"),
            )
        ):
            button(actions, icon, text, command, kind=kind, width=92, height=32).grid(
                row=0, column=key, padx=(0, 6)
            )

    def _failed(self, title: str, error: Audio8DError) -> None:
        """Explain a style operation that couldn't be done; nothing was changed."""
        fix = hints.fix_for(error)
        message = gui_words(str(error)) + "."
        if fix:
            message += f"\n\nWhat to do: {gui_words(fix)}"
        Dialog(
            self.app,
            title,
            message + "\n\nNothing was changed.",
            [("OK", "ok")],
            icon="error",
            color=DANGER,
        ).ask()

    def _free_name(self, stem: str) -> str:
        """stem, or stem2, stem3… whichever is not taken yet."""
        name, number = pascal_case(stem), 2
        while self.check_name(name)[1]:
            name, number = f"{pascal_case(stem)} {number}", number + 1
        return name

    def _rename(self, name: str) -> None:
        """Give a saved style a new name; songs that use it keep it."""
        new = NameDialog(
            self.app,
            "Rename this style",
            f"Choose a new name for '{name}'. Songs that use it keep using it.",
            name,
            lambda text: self.check_name(text, keep=name),
            "Rename",
        ).ask()
        if not new or new == name:
            return
        try:
            renamed = rename_user_preset(name, new)
        except Audio8DError as exc:
            self._failed("Can't rename this style", exc)
            return
        self.app.reload_styles(renamed=(name, renamed))
        Toast(self.app, f"Renamed '{name}' to '{renamed}'", "ok")

    def _duplicate(self, name: str) -> None:
        """Copy a saved style under a new name."""
        new = NameDialog(
            self.app,
            "Duplicate this style",
            f"The copy of '{name}' needs a name of its own.",
            self._free_name(f"{name} Copy"),
            self.check_name,
            "Duplicate",
        ).ask()
        if not new:
            return
        try:
            copy = duplicate_user_preset(name, new)
        except Audio8DError as exc:
            self._failed("Can't duplicate this style", exc)
            return
        self.app.reload_styles()
        Toast(self.app, f"Made '{copy}', a copy of '{name}'", "ok")

    def _export(self, name: str) -> None:
        """Save a style to a file, to keep or share."""
        chosen = filedialog.asksaveasfilename(
            title="Export a style",
            initialfile=f"{name}{STYLE_FILE_SUFFIX}",
            defaultextension=STYLE_FILE_SUFFIX,
            filetypes=[("Audio8D style", f"*{STYLE_FILE_SUFFIX}")],
        )
        if not chosen:
            return
        try:
            target = export_style(self.app.presets[name], Path(chosen))
        except Audio8DError as exc:
            self._failed("Can't export this style", exc)
            return
        Toast(self.app, f"Exported '{name}' to {target.name}", "ok")

    def _import(self) -> None:
        """Add a style from a file, after checking all of it and its new name."""
        chosen = filedialog.askopenfilename(
            title="Import a style",
            filetypes=[
                ("Audio8D style", f"*{STYLE_FILE_SUFFIX}"),
                ("All files", "*.*"),
            ],
        )
        if not chosen:
            return
        path = Path(chosen)
        try:
            style = read_style_file(path)
        except Audio8DError as exc:
            self._failed("Can't import this style", exc)
            return
        description = f" ({style.summary})" if style.summary else ""
        new = NameDialog(
            self.app,
            "Import a style",
            f"'{style.name}'{description} passed every check. Choose its name: it "
            "can't be the name of a style you already have.",
            pascal_case(style.name),
            self.check_name,
            "Import",
        ).ask()
        if not new:
            return
        try:
            imported = import_style(path, new)
        except Audio8DError as exc:
            self._failed("Can't import this style", exc)
            return
        self.app.reload_styles()
        Toast(self.app, f"Imported '{imported}'", "ok")

    def _delete(self, name: str) -> None:
        """Delete a saved style after asking."""
        answer = Dialog(
            self.app,
            "Delete this style?",
            f"'{name}' will be removed from your saved styles. Songs you made with it "
            "are not touched; songs on the list that use it go back to the style for "
            "all songs.",
            [("Cancel", "no"), ("Delete", "yes")],
            icon="delete",
            color=DANGER,
        ).ask()
        if answer == "yes":
            delete_user_preset(name)
            moved = self.app.reload_styles()
            songs = f"{moved} song{'s' if moved != 1 else ''}"
            extra = f"; {songs} now use the style for all songs" if moved else ""
            Toast(self.app, f"Deleted '{name}'{extra}")


class SettingsPage(Page):
    """Appearance, technical details, the tools Audio8D found, and about."""

    def __init__(self, master: tk.Misc, app: "Audio8DApp") -> None:
        """Build the page."""
        super().__init__(
            master, "", "Settings", "How the window looks, and what's installed."
        )
        self.app = app
        look = Card(self, "Appearance and details")
        self.add(look, 2)
        self.mode = ChoiceField(
            look.body,
            "Theme",
            "System follows your Windows light/dark setting.",
            {"System": "System", "Light": "Light", "Dark": "Dark"},
            lambda mode: ctk.set_appearance_mode(str(mode)),
        )
        self.mode.set("System")
        self.mode.grid(row=0, column=0, sticky="ew", pady=4)
        self.scale = ChoiceField(
            look.body,
            "Size",
            "Makes all text and buttons bigger or smaller.",
            {"90%": 0.9, "100%": 1.0, "110%": 1.1, "125%": 1.25},
            lambda v: ctk.set_widget_scaling(float(v)),  # type: ignore[arg-type]
        )
        self.scale.set(1.0)
        self.scale.grid(row=1, column=0, sticky="ew", pady=4)
        self.verbose = SwitchField(
            look.body,
            "Show technical details",
            "Writes everything Audio8D does into 'Technical details' on step 4 (the "
            "command line's --verbose). Handy when asking for help.",
            app.set_verbose,
        )
        self.verbose.grid(row=2, column=0, sticky="ew", pady=4)

        tools = Card(self, "Tools")
        self.add(tools, 3)
        try:
            found = FFmpegToolchain.discover()
            rows = [(f"FFmpeg found: {found.ffmpeg}", True)]
        except Audio8DError:
            rows = [
                (
                    "FFmpeg not found. Put ffmpeg.exe and ffprobe.exe in "
                    f"{tools_dir()}",
                    False,
                )
            ]
        rows.append(
            ("Demucs (singer in the middle): installed", True)
            if demucs_available()
            else (
                f"Demucs (singer in the middle): {demucs_hint()}",
                False,
            )
        )
        for index, (text, ok) in enumerate(rows):
            line = ctk.CTkLabel(
                tools.body,
                text=f"{'✓' if ok else '•'}  {text}",
                font=font(13),
                text_color=SUCCESS if ok else WARNING,
                anchor="w",
                justify="left",
                wraplength=700,
            )
            line.grid(row=index, column=0, sticky="ew", pady=2)
            fit_width(line, tools.body, 10)
        actions = ctk.CTkFrame(tools.body, fg_color="transparent")
        actions.grid(row=len(rows), column=0, sticky="w", pady=(12, 0))
        button(
            actions,
            "clear",
            "Forget remembered measurements",
            self._clear_cache,
            width=300,
            tooltip=f"Deletes the loudness cache in {cache_dir()}. It is rebuilt "
            "automatically; nothing else is touched.",
        ).grid(row=0, column=0, padx=(0, 12))
        button(
            actions,
            "open",
            "Open log folder",
            self._open_logs,
            width=200,
            tooltip=f"The technical log is {log_file()}. Send it along when you "
            "ask for help.",
        ).grid(row=0, column=1)

        about = Card(self, "About")
        self.add(about, 4, (0, 28))
        ctk.CTkLabel(
            about.body, text=f"Audio8D {__version__}", font=font(18, "bold"), anchor="w"
        ).grid(row=0, column=0, sticky="w")
        hint(
            about.body,
            f"Developed by {__author__}. 3D music for headphones, powered by FFmpeg. "
            "Everything here can also be done from a terminal: run  "
            f"{HELP_COMMAND}  to see how.",
        ).grid(row=1, column=0, sticky="w", pady=(2, 10))
        button(
            about.body,
            "guide",
            "Open the full guide",
            self._open_guide,
            kind="primary",
            width=220,
        ).grid(row=2, column=0, sticky="w")

    @staticmethod
    def _open_guide() -> None:
        """Show the README beside the app, or the online copy when there isn't one."""
        guide = guide_file()
        if guide.exists():
            open_path(guide)
        else:
            webbrowser.open(GUIDE_URL)

    def _open_logs(self) -> None:
        """Show the folder with the technical log."""
        folder = log_file().parent
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError:
            Toast(self.app, "The log folder can't be created", "error")
            return
        open_path(folder)

    def _clear_cache(self) -> None:
        """Delete the loudness cache file."""
        try:
            (cache_dir() / "loudness.json").unlink(missing_ok=True)
        except OSError:
            Toast(self.app, "Could not clear the cache", "error")
            return
        Toast(self.app, "Remembered measurements cleared", "ok")


# ------------------------------------------------------------------- the app


class _QueueLog(logging.Handler):
    """Sends log lines to the window's event queue (safe from any thread)."""

    def __init__(self, events: queue.Queue) -> None:
        """Remember the queue."""
        super().__init__()
        self.events = events
        self.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s: %(message)s", "%H:%M:%S"
            )
        )

    def emit(self, record: logging.LogRecord) -> None:
        """Queue one formatted line."""
        self.events.put(("log", self.format(record)))


class Audio8DApp(ctk.CTk):
    """The main window: steps in the sidebar, pages, a status strip, the work thread."""

    def __init__(self, songs: Sequence[Path] = ()) -> None:
        """Build everything and show step 1."""
        ctk.set_appearance_mode("System")
        super().__init__()
        Icons.setup()
        self.title(f"Audio8D {__version__} - 3D music for headphones")
        use_app_icon(self)
        self.geometry("1280x860")
        self.minsize(1100, 720)
        self.configure(fg_color=SURFACE_ALT)

        # Set by _load_styles when the saved-styles file can't be read
        self.styles_problem: str | None = None
        self.presets: dict[str, Preset] = self._load_styles()
        self.settings = GuiSettings()
        self.settings.apply_style(self.presets[RECOMMENDED_PRESET])
        self.rows: list[SongEntry] = []
        # How many songs the list shows; more are one click away
        self.shown = SONGS_PER_PAGE
        self.selected: SongEntry | None = None
        self.events: queue.Queue[tuple] = queue.Queue()
        self.cancel = threading.Event()
        self.busy = False
        self.started = 0.0
        self.run_rows: list[RunRow] = []
        self.stages: list[str] = []
        self.current: str | None = None
        self.log_handler = _QueueLog(self.events)
        logging.getLogger().addHandler(self.log_handler)
        self.set_verbose(False)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
        self.pages: dict[str, Page] = {
            "songs": SongsPage(self.content, self),
            "sound": SoundPage(self.content, self),
            "output": OutputPage(self.content, self),
            "review": ReviewPage(self.content, self),
            "styles": StylesPage(self.content, self),
            "settings": SettingsPage(self.content, self),
        }
        self._build_status()
        self._bind_keys()
        self.show_page("songs")
        self.sync_controls()
        self._layout_rows()
        self.protocol("WM_DELETE_WINDOW", self.close)

        # Hooked now rather than on a timer, so a drop in the first seconds still counts
        enable_file_drop(self, self.add_paths)
        if self.styles_problem:
            self.after(
                600,
                lambda: Toast(
                    self, "Your saved styles couldn't be read: see Your styles", "error"
                ),
            )
        if songs:
            self.after(300, lambda: self.add_paths(list(songs)))
        self.after(80, self._poll)
        # Tk objects freed on a helper thread block it on Tcl, so only collect here
        gc.disable()
        self.after(GC_INTERVAL_MS, self._collect_garbage)

    def _collect_garbage(self) -> None:
        """Free cyclic garbage on the window's own thread, a few times a minute."""
        gc.collect()
        self.after(GC_INTERVAL_MS, self._collect_garbage)

    def destroy(self) -> None:
        """Close the window and hand garbage collection back to Python."""
        gc.enable()
        # Timers still waiting would fire into a closed window and print Tcl errors
        try:
            for job in self.tk.call("after", "info"):
                self.tk.call("after", "cancel", job)
        except tk.TclError:
            pass
        super().destroy()

    # ------------------------------------------------------------ building

    def _load_styles(self) -> dict[str, Preset]:
        """Built-in and saved styles; a broken styles file only loses your own."""
        try:
            styles = all_presets()
        except Audio8DError as exc:
            LOG.warning("Saved styles could not be read: %s", exc)
            self.styles_problem = gui_words(str(exc))
            return dict(PRESETS)
        self.styles_problem = None
        return styles

    def _build_sidebar(self) -> None:
        """Logo, the four steps, the extra pages, and the version at the bottom."""
        strip = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=SIDEBAR)
        strip.grid(row=0, column=0, rowspan=2, sticky="nsw")
        strip.grid_propagate(False)
        strip.grid_columnconfigure(0, weight=1)
        strip.grid_rowconfigure(9, weight=1)
        logo = ctk.CTkFrame(strip, fg_color="transparent")
        logo.grid(row=0, column=0, sticky="ew", padx=20, pady=(26, 24))
        ctk.CTkLabel(
            logo, text=Icons.glyph("preview"), font=Icons.font(28), text_color=ACCENT
        ).pack(side="left")
        words = ctk.CTkFrame(logo, fg_color="transparent")
        words.pack(side="left", padx=10)
        ctk.CTkLabel(words, text="Audio8D", font=font(20, "bold"), anchor="w").pack(
            anchor="w"
        )
        ctk.CTkLabel(
            words, text="3D music for headphones", font=font(11), text_color=TEXT_DIM
        ).pack(anchor="w")

        self.nav: dict[str, ctk.CTkButton] = {}
        self.nav_icons: dict[str, tuple] = {}
        entries = (
            ("songs", "1  Add songs", "Step 1: choose the songs (Ctrl+1)"),
            ("sound", "2  Sound", "Step 2: style and sound settings (Ctrl+2)"),
            (
                "output",
                "3  Output",
                "Step 3: file type, loudness, where to save (Ctrl+3)",
            ),
            ("review", "4  Review & convert", "Step 4: check, preview, start (Ctrl+4)"),
            (None, "", ""),
            ("styles", "Your styles", "Create and share your own styles (Ctrl+5)"),
            ("settings", "Settings", "Theme, technical details, tools, about (Ctrl+6)"),
        )
        for row, (key, text, tip) in enumerate(entries, start=1):
            if key is None:
                ctk.CTkFrame(strip, height=1, fg_color=BORDER).grid(
                    row=row, column=0, sticky="ew", padx=24, pady=10
                )
                continue
            widget = ctk.CTkButton(
                strip,
                **icon_text(key, f"  {text}", 18),
                font=font(14),
                anchor="w",
                height=44,
                corner_radius=10,
                fg_color="transparent",
                hover_color=ACCENT_SOFT,
                text_color=INK,
                command=lambda key=key: self.show_page(key),
            )
            widget.grid(row=row, column=0, sticky="ew", padx=14, pady=3)
            Tooltip(widget, tip)
            self.nav[key] = widget
            self.nav_icons[key] = (
                Icons.image(key, 18, INK),
                Icons.image(key, 18, ACCENT),
            )
        ctk.CTkLabel(
            strip,
            text=f"v{__version__}\nDeveloped by {__author__}",
            font=font(11),
            text_color=TEXT_DIM,
            justify="left",
        ).grid(row=10, column=0, sticky="sw", padx=22, pady=20)

    def _build_status(self) -> None:
        """The bottom strip: overall progress, what's happening, the chosen settings."""
        status = ctk.CTkFrame(self, height=52, corner_radius=0, fg_color=SURFACE)
        status.grid(row=1, column=1, sticky="ew")
        status.grid_columnconfigure(1, weight=1)
        self.overall = ctk.CTkProgressBar(status, width=220, progress_color=ACCENT)
        self.overall.set(0)
        self.overall.grid(row=0, column=0, padx=(28, 14), pady=18)
        self.status_text = ctk.CTkLabel(
            status, text="Ready.", font=font(13), anchor="w"
        )
        self.status_text.grid(row=0, column=1, sticky="ew")
        self.settings_text = ctk.CTkLabel(
            status, text="", font=font(12), text_color=TEXT_DIM, anchor="e"
        )
        self.settings_text.grid(row=0, column=2, sticky="e", padx=28)
        # Short notices take the summary's place for a moment (see Toast)
        self.toast_slot = (status, self.settings_text)
        Tooltip(
            self.settings_text, "What every song will get. Change it on steps 2 and 3."
        )

    def _bind_keys(self) -> None:
        """Keyboard shortcuts for the common actions."""
        self.bind("<Control-o>", lambda _e: self.ask_files())
        self.bind("<Control-O>", lambda _e: self.ask_folder())
        self.bind("<Control-Return>", lambda _e: self.run_convert())
        self.bind("<Control-p>", lambda _e: self.run_preview())
        self.bind("<Escape>", lambda _e: self.stop())
        for number, key in enumerate(
            ("songs", "sound", "output", "review", "styles", "settings"), start=1
        ):
            self.bind(
                f"<Control-Key-{number}>", lambda _e, key=key: self.show_page(key)
            )

    def report_callback_exception(
        self,
        exc: type[BaseException],
        val: BaseException,
        tb: TracebackType | None,
    ) -> None:
        """A surprise inside a button or event: log it and explain, never go silent."""
        LOG.error("Unexpected problem in the window", exc_info=(exc, val, tb))
        self._show_error(val)

    def close(self) -> None:
        """Closing the window mid-conversion: ask first, then stop cleanly."""
        if self.busy:
            answer = Dialog(
                self,
                "Stop and close?",
                "A conversion is still running. Songs that are finished are kept; the "
                "song being made is cleaned up.",
                [("Keep working", "no"), ("Stop and close", "yes")],
                icon="warning",
                color=WARNING,
            ).ask()
            if answer != "yes":
                return
            self.cancel.set()
        logging.getLogger().removeHandler(self.log_handler)
        self.destroy()

    # ------------------------------------------------------------ navigation

    def show_page(self, key: str) -> None:
        """Bring one page to the front and highlight its sidebar button."""
        # Scrolling pages live inside an outer frame, so show/hide beats tkraise
        if self.current is not None and self.current != key:
            self.pages[self.current].grid_forget()
        self.pages[key].grid(row=0, column=0, sticky="nsew")
        self.current = key
        for name, widget in self.nav.items():
            chosen = name == key
            options: dict = {
                "fg_color": ACCENT_SOFT if chosen else "transparent",
                "text_color": ACCENT if chosen else INK,
            }
            normal, active = self.nav_icons.get(name, (None, None))
            if normal is not None:
                options["image"] = active if chosen else normal
            widget.configure(**options)
        if key == "review":
            self.pages["review"].show(self.settings)  # type: ignore[attr-defined]

    def sync_controls(self) -> None:
        """Make every page show the current settings."""
        songs = self.pages["songs"]
        songs.recursive.set(self.settings.recursive)  # type: ignore[attr-defined]
        self.pages["sound"].show(self.settings)  # type: ignore[attr-defined]
        self.pages["output"].show(self.settings)  # type: ignore[attr-defined]
        if self.current == "review":
            self.pages["review"].show(self.settings)  # type: ignore[attr-defined]
        self.refresh_status()

    def refresh_status(self) -> None:
        """Update the settings summary on the right of the status strip."""
        try:
            text = describe(self.settings)
        except Audio8DError:
            text = "some settings need fixing (see step 4)"
        destination = destination_for(self.settings)
        text += f"  →  {destination.name}" if destination else "  →  next to originals"
        self.settings_text.configure(text=text)

    # ------------------------------------------------------------ settings

    def choose_style(self, name: str, go: bool = False) -> None:
        """A style card (or 'Use') was clicked."""
        self.settings.apply_style(self.presets[name])
        self.settings.speakers = False
        self.sync_controls()
        Toast(self, f"Style: {style_label(name, self.presets)}")
        if go:
            self.show_page("sound")

    def change_sound(self, **knobs: object) -> None:
        """A sound or format control changed."""
        self.settings.change(**knobs)
        self.sync_controls()

    def reset_style(self) -> None:
        """Back to the chosen style's own values."""
        self.choose_style(self.settings.style)

    def reload_styles(
        self, select: str | None = None, renamed: tuple[str, str] | None = None
    ) -> int:
        """Saved styles changed: rebuild the cards, lists and menus.

        renamed is (old name, new name) after a rename, so songs keep their style.
        Returns how many songs went back to the style for all songs because their
        own style is gone.
        """
        self.presets = self._load_styles()
        own = self.settings.song_styles
        if renamed:
            old, new = renamed
            for song, name in own.items():
                if name == old:
                    own[song] = new
            if self.settings.style == old:
                self.settings.style = new
        gone = [song for song, name in own.items() if name not in self.presets]
        for song in gone:
            del own[song]
        self.pages["sound"].build_cards()  # type: ignore[attr-defined]
        self.pages["styles"].refresh()  # type: ignore[attr-defined]
        if select:
            self.settings.style = select
        elif self.settings.style not in self.presets:
            self.settings.apply_style(self.presets[RECOMMENDED_PRESET])
        self.pages["sound"].show_songs()  # type: ignore[attr-defined]
        self.sync_controls()
        return len(gone)

    def set_song_style(self, entry: SongEntry, name: str | None) -> None:
        """Give one song a style of its own, or None for the style for all songs."""
        if name is None:
            self.settings.song_styles.pop(entry.song, None)
        else:
            self.settings.song_styles[entry.song] = name
        self.pages["sound"].show_own_count()  # type: ignore[attr-defined]
        self.refresh_status()

    def clear_song_styles(self) -> None:
        """Every song uses the style for all songs again."""
        self.settings.song_styles.clear()
        self.pages["sound"].show_songs()  # type: ignore[attr-defined]
        self.refresh_status()

    def set_speakers(self, on: bool) -> None:
        """'Safe for speakers too'."""
        self.settings.speakers = on
        self.sync_controls()

    def set_recursive(self, on: bool) -> None:
        """'Include songs in sub-folders' (applies to folders added from now on)."""
        self.settings.recursive = on

    def set_originals(self, value: object) -> None:
        """Keep or replace the originals."""
        self.settings.originals = str(value)
        self.sync_controls()

    def set_name_style(self, value: object) -> None:
        """How the new files are named."""
        self.settings.name_style = str(value)
        self.sync_controls()

    def set_custom_name(self, text: str) -> str | None:
        """The custom file name box."""
        self.settings.custom_name = text
        self.refresh_status()
        if any(c in text for c in '<>:"/\\|?*'):
            return "File names can't contain  < > : \" / \\ | ? *"
        return None

    def set_verbose(self, on: bool) -> None:
        """'Show technical details': everything, or just the important lines."""
        self.settings.verbose = on
        self.log_handler.setLevel(logging.DEBUG if on else logging.INFO)
        logging.getLogger().setLevel(logging.DEBUG if on else logging.INFO)

    def _typed(self, key: str, text: str) -> str | None:
        """Store a typed value; return a friendly error if it can't be used yet."""
        setattr(self.settings, key, text)
        problem = _problem(lambda: config_for(self.settings)) if text.strip() else None
        self.refresh_status()
        return problem

    def set_bpm(self, text: str) -> str | None:
        """The tempo box: a number from 40 to 240, or empty."""
        problem = self._typed("bpm_text", text)
        if problem:
            return "Type a tempo from 40 to 240, e.g. 128 (or leave it empty)."
        if text.strip() and not self.settings.sound.beat_sync:
            self.change_sound(beat_sync=True)
        return None

    def set_speed_curve(self, text: str) -> str | None:
        """'Speed over time'."""
        problem = self._typed("speed_curve_text", text)
        page = self.pages["sound"]
        page.show(self.settings)  # type: ignore[attr-defined]
        if problem:
            return f"{problem}.  Example: 0=10, 1:00=6"
        if text.strip():
            page.speed_curve.explain(  # type: ignore[attr-defined]
                "Reads as: " + describe_curve(text, " s per circle"), SUCCESS
            )
        return None

    def set_intensity_curve(self, text: str) -> str | None:
        """'Movement over time'."""
        problem = self._typed("intensity_curve_text", text)
        page = self.pages["sound"]
        page.show(self.settings)  # type: ignore[attr-defined]
        if problem:
            return f"{problem}.  Example: 0=0.5, 1:00=0.95"
        if text.strip():
            page.amount_curve.explain(  # type: ignore[attr-defined]
                "Reads as: " + describe_curve(text, " movement"), SUCCESS
            )
        return None

    def set_custom_loudness(self, text: str) -> str | None:
        """The custom loudness box."""
        problem = self._typed("custom_loudness_text", text)
        return "Type a loudness from -30 to -5, e.g. -14." if problem else None

    # ------------------------------------------------------------ the song list

    def add_paths(self, paths: list[Path]) -> None:
        """Add dropped or chosen files; folders add every song inside them."""
        if self.busy:
            Toast(self, "Please wait until the conversion finishes", "error")
            return
        known = {row.song for row in self.rows}
        added: list[SongEntry] = []
        skipped = 0
        for path in paths:
            if path.is_dir():
                found = [
                    (song, path)
                    for song in find_songs(path, recursive=self.settings.recursive)
                ]
                if not found:
                    Toast(self, f"No songs found in {path.name}", "error")
            elif path.suffix.lower() in AUDIO_EXTENSIONS and not is_own_output(path):
                found = [(path, None)]
            else:
                found = []
                skipped += 1
            for song, folder in found:
                if song in known:
                    continue
                known.add(song)
                row = SongEntry(song, folder)
                self.rows.append(row)
                added.append(row)
        self._layout_rows()
        if added:
            self.pages["sound"].show_songs()  # type: ignore[attr-defined]
            Toast(
                self, f"Added {len(added)} song{'s' if len(added) != 1 else ''}", "ok"
            )
            threading.Thread(target=self._probe, args=(added,), daemon=True).start()
        elif skipped:
            Toast(self, "Those files aren't music (or were made by Audio8D)", "error")
        self.sync_controls()

    def _probe(self, rows: list[SongEntry]) -> None:
        """Read each new song's length and type in the background."""
        try:
            toolchain = FFmpegToolchain.discover()
        except Audio8DError as exc:
            self.events.put(("error", exc))
            return
        for row in rows:
            try:
                info = probe_audio(toolchain, row.song)
            except Audio8DError:
                self.events.put(("unreadable", row))
                continue
            except Exception:  # pylint: disable=broad-exception-caught
                # One strange file must not stop the others from being read
                LOG.exception("Could not read %s", row.song)
                self.events.put(("unreadable", row))
                continue
            self.events.put(("probed", row, info))

    def _layout_rows(self) -> None:
        """Place the shown rows (or the empty message) and update the summary."""
        songs = self.pages["songs"]
        if self.rows:
            songs.empty.grid_remove()  # type: ignore[attr-defined]
        else:
            songs.empty.grid()  # type: ignore[attr-defined]
        # Hundreds of rows would freeze Tk's layout, so only a page is built
        shown = self.rows[: self.shown]
        for entry in self.rows[self.shown :]:
            entry.hide()
        self._build_rows()
        count = len(self.rows)
        hidden = count - len(shown)
        if hidden:
            songs.more_text.configure(  # type: ignore[attr-defined]
                text=f"Showing {len(shown)} of {count} songs. All {count} will be "
                "converted."
            )
            songs.more_button.configure(  # type: ignore[attr-defined]
                **icon_text("add", f"Show {min(hidden, SONGS_PER_PAGE)} more")
            )
            songs.more.grid(  # type: ignore[attr-defined]
                row=len(shown) + 1, column=0, sticky="ew", padx=8, pady=(3, 6)
            )
        else:
            songs.more.grid_remove()  # type: ignore[attr-defined]
        songs.summary.configure(  # type: ignore[attr-defined]
            text=f"{count} song{'s' if count != 1 else ''} ready"
            if count
            else "Your list"
        )

    def _build_rows(self) -> None:
        """Build and place the rows of the songs currently shown."""
        songs = self.pages["songs"]
        for index, entry in enumerate(self.rows[: self.shown]):
            if entry.view is None:
                entry.view = SongRow(
                    songs.list,  # type: ignore[attr-defined]
                    entry,
                    self.select_row,
                    self.remove_row,
                )
            entry.view.grid(row=index + 1, column=0, sticky="ew", padx=8, pady=3)

    def show_more_songs(self) -> None:
        """Show the next page of a long song list."""
        self.shown += SONGS_PER_PAGE
        self._layout_rows()

    def chosen_song(self) -> SongEntry | None:
        """The row Preview and A/B use: the clicked one, or the first."""
        if not self.rows:
            return None
        return self.selected if self.selected in self.rows else self.rows[0]

    def select_row(self, row: SongEntry) -> None:
        """Click on a row: make it the one Preview and A/B use."""
        if self.selected is not None:
            self.selected.select(False)
        self.selected = row
        row.select(True)

    def remove_row(self, row: SongEntry | None) -> None:
        """Take a song off the list (never while converting)."""
        if row is None or self.busy:
            return
        self.rows.remove(row)
        self.settings.song_styles.pop(row.song, None)
        if self.selected is row:
            self.selected = None
        row.hide()
        self._layout_rows()
        self.pages["sound"].show_songs()  # type: ignore[attr-defined]
        self.sync_controls()

    def clear_songs(self) -> None:
        """Empty the list."""
        if self.busy:
            return
        for row in self.rows:
            row.hide()
        self.rows.clear()
        self.settings.song_styles.clear()
        self.shown = SONGS_PER_PAGE
        self.selected = None
        self._layout_rows()
        self.pages["sound"].show_songs()  # type: ignore[attr-defined]
        self.sync_controls()

    def ask_files(self) -> None:
        """Add songs from a file dialog."""
        patterns = " ".join(f"*{ext}" for ext in sorted(AUDIO_EXTENSIONS))
        chosen = filedialog.askopenfilenames(
            title="Choose songs", filetypes=[("Music", patterns), ("All files", "*.*")]
        )
        self.add_paths([Path(name) for name in chosen])

    def ask_folder(self) -> None:
        """Add a folder of songs."""
        chosen = filedialog.askdirectory(title="Choose a folder of songs")
        if chosen:
            self.add_paths([Path(chosen)])

    # ------------------------------------------------------------ running

    def _ready(self) -> bool:
        """Check everything first; if something's wrong, show step 4's list."""
        found = problems(
            self.settings, [(row.song, row.folder) for row in self.rows], self.presets
        )
        if found:
            self.show_page("review")
            Toast(self, "Please fix the red items first", "error")
            return False
        return True

    def _start(self, label: str, work: Callable[[], None]) -> None:
        """Run work on a helper thread; the window keeps responding."""
        self.busy = True
        self.cancel.clear()
        self.started = time.perf_counter()
        self.overall.set(0)
        self.status_text.configure(text=label)
        self.pages["review"].set_busy(True)  # type: ignore[attr-defined]

        def target() -> None:
            try:
                work()
            except Audio8DError as exc:
                # Stopping on purpose isn't a problem; the status bar says "Stopped"
                if not self.cancel.is_set():
                    self.events.put(("error", exc))
            except Exception as exc:  # pylint: disable=broad-exception-caught
                # Never let a surprise take the window down; show it instead
                LOG.exception("Unexpected problem")
                self.events.put(("error", exc))
            finally:
                self.events.put(("finished",))

        threading.Thread(target=target, daemon=True).start()

    def run_preview(self, config: EffectConfig | None = None) -> None:
        """Make and play a short sample of the chosen song.

        With a config (a style being created), that's what it tries; the other
        settings don't matter then, so their problems don't stop it.
        """
        row = self.chosen_song()
        if row is None:
            Toast(self, "Add a song first (step 1)", "error")
            return
        if self.busy or (config is None and not self._ready()):
            return
        if config is None:
            config = song_config(self.settings, row.song, self.presets)
        seconds = float(self.settings.preview_seconds)

        def work() -> None:
            result = preview(
                row.song,
                preview_output_for(row.song, config.extension),
                config,
                seconds=seconds,
                on_progress=lambda stage, share: self.events.put(("one", stage, share)),
                cancel=self.cancel,
            )
            self.events.put(("toast", f"Preview ready: {result.output.name}", "ok"))
            open_path(result.output)

        self._start(f"Making a {seconds:.0f}-second preview of {row.song.stem}…", work)

    def run_compare(self) -> None:
        """Make and play the A/B file of the chosen song."""
        row = self.chosen_song()
        if row is None:
            Toast(self, "Add a song first (step 1)", "error")
            return
        if self.busy or not self._ready():
            return
        config = song_config(self.settings, row.song, self.presets)

        def work() -> None:
            made = compare(
                row.song,
                compare_output_for(row.song),
                config,
                on_progress=lambda stage, share: self.events.put(("one", stage, share)),
                cancel=self.cancel,
            )
            self.events.put(("toast", "A/B file ready: original first, then 8D", "ok"))
            open_path(made)

        self._start(f"Making an A/B compare of {row.song.stem}…", work)

    def run_convert(self) -> None:
        """Convert every song in the list."""
        if self.busy or not self._ready():
            return
        settings = self.settings
        if settings.originals != "keep":
            answer = Dialog(
                self,
                "Replace the original songs?",
                "After each 8D song is safely saved, its original will be moved to the "
                "Recycle Bin (you can restore it from there). On drives with no "
                "Recycle Bin, such as USB sticks, it stays in its folder, renamed "
                "'<song> (original)'. An 8D song can't be turned back into the "
                "normal song.",
                [("Cancel", "no"), ("Replace them", "yes")],
                icon="warning",
                color=WARNING,
            ).ask()
            if answer != "yes":
                return
        items = items_for(
            settings, [(row.song, row.folder) for row in self.rows], self.presets
        )
        # Songs that already have an 8D version are skipped, as on the command line
        todo = [
            item
            for item in items
            if settings.overwrite
            or not item.output.exists()
            or (settings.originals == "replace" and item.output == item.source)
        ]
        skipped = len(items) - len(todo)
        if not todo:
            Dialog(
                self,
                "Nothing new to make",
                "Every song already has an 8D version. Turn on 'Replace 8D files that "
                "already exist' (step 3, Advanced output) to make them again.",
                [("OK", "ok")],
            ).ask()
            return
        config = config_for(settings)
        options = options_for(settings)
        self.stages = stages_for(options)
        update, overall = progress_tracker(len(todo), self.stages)
        self.show_page("review")
        self.run_rows = self.pages["review"].start_run(  # type: ignore[attr-defined]
            [item.source for item in todo]
        )
        if skipped:
            Toast(self, f"Skipped {skipped} song(s) that already have an 8D version")

        def work() -> None:
            def progress(index: int, stage: str, share: float) -> None:
                update(index, stage, share)
                self.events.put(("row", index, stage, share, overall()))

            report = run_batch(
                todo,
                config,
                options=options,
                overwrite=settings.overwrite,
                jobs=settings.jobs,
                on_progress=progress,
                on_done=lambda index, outcome: self.events.put(
                    ("done", index, outcome)
                ),
                cancel=self.cancel,
            )
            self.events.put(("report", report))

        label = f"Converting {len(todo)} song{'s' if len(todo) != 1 else ''}…"
        self._start(label, work)

    def stop(self) -> None:
        """Ask the running work to stop after the current step."""
        if self.busy:
            self.cancel.set()
            self.status_text.configure(text="Stopping after the current step…")

    # ------------------------------------------------------------ events

    def _poll(self) -> None:
        """Apply what the helper thread reported."""
        try:
            while True:
                self._handle(self.events.get_nowait())
        except queue.Empty:
            pass
        except tk.TclError:
            return
        if self.busy:
            elapsed = time.perf_counter() - self.started
            text = self.status_text.cget("text").split("  (")[0]
            self.status_text.configure(text=f"{text}  ({format_time(elapsed)})")
        self.after(80, self._poll)

    def _handle(self, event: tuple) -> None:  # pylint: disable=too-many-branches
        """One event from the helper thread."""
        kind = event[0]
        if kind == "log":
            self.pages["review"].write_log(event[1])  # type: ignore[attr-defined]
        elif kind == "probed":
            _, row, info = event
            row.info = info
            row.show_details(info.codec_name, info.duration_seconds, info.is_lossless)
        elif kind == "unreadable":
            event[1].unreadable()
        elif kind == "row":
            _, index, stage, share, overall = event
            if index < len(self.run_rows):
                self.run_rows[index].progress(stage, share, self.stages)
            self.overall.set(overall)
        elif kind == "done":
            _, index, outcome = event
            if index < len(self.run_rows):
                self.run_rows[index].finished(outcome)
            else:
                self.pages["review"].rest_finished(  # type: ignore[attr-defined]
                    len(self.run_rows), outcome
                )
        elif kind == "one":
            _, stage, share = event
            self.overall.set(share)
            self.status_text.configure(text=f"{_STAGE_WORDS.get(stage, stage)}…")
        elif kind == "toast":
            Toast(self, event[1], event[2])
        elif kind == "error":
            self._show_error(event[1])
        elif kind == "report":
            report = event[1]
            self.after(150, lambda: self._show_report(report))
        elif kind == "finished":
            self.busy = False
            self.overall.set(1.0)
            self.pages["review"].set_busy(False)  # type: ignore[attr-defined]
            if self.cancel.is_set():
                self.status_text.configure(text="Stopped. Finished songs are kept.")
            elif not self.status_text.cget("text").startswith("Done"):
                self.status_text.configure(text="Done.")
            self.pages["review"].show(self.settings)  # type: ignore[attr-defined]

    def _show_error(self, error: BaseException) -> None:
        """A problem the work thread hit, with the plain-word fix."""
        fix = hints.fix_for(error) if isinstance(error, Audio8DError) else None
        LOG.error("%s", error)
        message = gui_words(hints.short_message(error))
        if fix:
            message += f"\n\nWhat to do: {gui_words(fix)}"
        message += (
            "\n\nMore detail is in 'Technical details' on step 4, and in the log "
            "file (Settings, Open log folder)."
        )
        Dialog(self, "Something went wrong", message, [("OK", "ok")], icon="error",
               color=DANGER)  # fmt: skip

    def _show_report(self, report: BatchReport) -> None:
        """The summary dialog after converting a list."""
        converted = report.converted
        results = report.results
        failed = report.failed
        seconds = report.seconds
        self.status_text.configure(
            text=f"Done: {len(converted)} made, {len(failed)} failed, "
            f"in {format_time(seconds)}."
        )
        if converted and self.settings.play_when_done:
            open_path(results[0].output)
        if self.cancel.is_set():
            return
        places = [result.original_removed_to for result in results]
        lines = [
            f"{len(converted)} song{'s' if len(converted) != 1 else ''} made in "
            f"{seconds:.1f} seconds."
        ]
        lines += removal_summary([place for place in places if place])
        if failed:
            lines.append(
                f"{len(failed)} could not be made - the red rows on step 4 say why and "
                "what to do."
            )
        lines.append("Put on your headphones and press play!")
        buttons = [("Close", "close")]
        if converted:
            buttons += [("Open folder", "folder"), ("Play first", "play")]
        answer = Dialog(
            self,
            "All done!" if not failed else "Finished, with some problems",
            "\n".join(lines),
            buttons,
            icon="check" if not failed else "warning",
            color=SUCCESS if not failed else WARNING,
        ).ask()
        if answer == "folder":
            open_path(results[0].output.parent)
        elif answer == "play":
            open_path(results[0].output)


def launch(songs: Sequence[Path] = ()) -> int:
    """Open the window and wait until it is closed."""
    app = Audio8DApp(songs)
    app.mainloop()
    return 0


__all__ = ["Audio8DApp", "launch"]
