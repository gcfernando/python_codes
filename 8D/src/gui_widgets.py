# Developed by ::> Gehan Fernando
"""The building blocks of the Audio8D window: colours, icons and friendly controls.

Every control here carries its own explanation: a short line under it that is
always visible, and a longer tooltip on hover. That is what lets a beginner
use every option without knowing any audio terms.
"""

# Widgets are small classes with many options by nature
# pylint: disable=too-many-arguments,too-many-positional-arguments
# pylint: disable=too-many-instance-attributes,too-many-ancestors

__all__ = ["open_path"]

import os
import tkinter as tk
import tkinter.font as tkfont
from collections.abc import Callable
from pathlib import Path
from typing import Literal

import customtkinter as ctk

from .opener import open_path

# CustomTkinter's own scrollbar drawing, kept so the quicker version can call it
_SCROLLBAR_DRAW = ctk.CTkScrollbar._draw  # pylint: disable=protected-access


def _draw_scrollbar_without_flush(
    self: ctk.CTkScrollbar, no_color_updates: bool = False
) -> None:
    """Draw a scrollbar without forcing the whole window to lay itself out first."""
    # CustomTkinter 5.2 forces a full layout pass on every redraw; Tk redraws anyway
    # pylint: disable-next=protected-access
    self._canvas.update_idletasks = _no_flush
    _SCROLLBAR_DRAW(self, no_color_updates)


def _no_flush() -> None:
    """Stands in for update_idletasks on a scrollbar's canvas."""


# pylint: disable-next=protected-access
ctk.CTkScrollbar._draw = _draw_scrollbar_without_flush  # type: ignore[method-assign]


# ------------------------------------------------------------------ look & feel

# (light mode, dark mode) pairs, the way CustomTkinter takes colours
ACCENT = ("#6D28D9", "#8B5CF6")
ACCENT_HOVER = ("#5B21B6", "#7C3AED")
ACCENT_SOFT = ("#EDE9FE", "#2E1F4F")
SURFACE = ("#FFFFFF", "#1E1E2E")
SURFACE_ALT = ("#F4F4F8", "#181825")
SIDEBAR = ("#EDEDF4", "#11111B")
BORDER = ("#DCDCE6", "#313244")
TEXT_DIM = ("#5B5B6E", "#A6ADC8")
INK = ("#1F2937", "#E5E7EB")
WHITE = ("#FFFFFF", "#FFFFFF")
SUCCESS = ("#15803D", "#4ADE80")
DANGER = ("#B91C1C", "#F87171")
DANGER_HOVER = ("#991B1B", "#EF4444")
WARNING = ("#B45309", "#FBBF24")
WARNING_SOFT = ("#FEF3C7", "#3A2E12")
DANGER_SOFT = ("#FEE2E2", "#3B1A1F")

# Windows 11/10 icon-font glyphs, with plain characters for everyone else
_GLYPHS = {
    "songs": ("\ue8d6", "♪"),
    "sound": ("\ue9e9", "≋"),
    "output": ("\ue74e", "⤓"),
    "review": ("\ue9d5", "✓"),
    "styles": ("\ue771", "✎"),
    "settings": ("\ue713", "⚙"),
    "add": ("\ue710", "+"),
    "folder": ("\ue8b7", "▤"),
    "open": ("\ued25", "↗"),
    "play": ("\ue768", "▶"),
    "stop": ("\ue71a", "■"),
    "preview": ("\ue7f6", "♫"),
    "compare": ("\ue8ab", "⇄"),
    "remove": ("\ue711", "✕"),
    "delete": ("\ue74d", "✕"),
    "check": ("\ue73e", "✓"),
    "error": ("\uea39", "!"),
    "warning": ("\ue7ba", "!"),
    "info": ("\ue946", "i"),
    "drop": ("\ue898", "⇧"),
    "save": ("\ue74e", "⤓"),
    "clear": ("\ue894", "⌫"),
    "music": ("\ue8d6", "♪"),
    "star": ("\ue734", "★"),
    "guide": ("\ue82d", "?"),
    "next": ("\ue72a", "→"),
    "back": ("\ue72b", "←"),
    "down": ("\ue70d", "▾"),
    "up": ("\ue70e", "▴"),
}


def font(size: int = 13, weight: Literal["normal", "bold"] = "normal") -> ctk.CTkFont:
    """The window's text font."""
    return ctk.CTkFont(family="Segoe UI", size=size, weight=weight)


class Icons:
    """Finds the icon font once and hands out glyphs, fonts and images."""

    family: str | None = None
    font_file: Path | None = None
    _cache: dict[tuple, "ctk.CTkImage | None"] = {}

    @classmethod
    def setup(cls) -> None:
        """Look for the icon font (call after the Tk root exists)."""
        # Images belong to one window; a new window needs fresh ones
        cls._cache = {}
        try:
            families = set(tkfont.families())
        except tk.TclError:
            families = set()
        cls.family = next(
            (f for f in ("Segoe Fluent Icons", "Segoe MDL2 Assets") if f in families),
            None,
        )
        fonts = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
        for name in ("SegoeIcons.ttf", "segmdl2.ttf"):
            if (fonts / name).is_file():
                cls.font_file = fonts / name
                break

    @classmethod
    def glyph(cls, name: str) -> str:
        """The character for an icon."""
        fluent, plain = _GLYPHS[name]
        return fluent if cls.family else plain

    @classmethod
    def font(cls, size: int = 16) -> ctk.CTkFont:
        """The font the glyphs are drawn with."""
        return ctk.CTkFont(family=cls.family or "Segoe UI Symbol", size=size)

    @classmethod
    def image(
        cls, name: str, size: int = 16, color: tuple[str, str] = INK
    ) -> "ctk.CTkImage | None":
        """The icon as a crisp image for buttons (None where it can't be drawn)."""
        key = (name, size, color)
        if key not in cls._cache:
            cls._cache[key] = cls._draw(name, size, color)
        return cls._cache[key]

    @classmethod
    def _draw(
        cls, name: str, size: int, color: tuple[str, str]
    ) -> "ctk.CTkImage | None":
        """Render one glyph four times larger, then let CTk scale it down."""
        if cls.font_file is None:
            return None
        try:
            from PIL import (  # pylint: disable=import-outside-toplevel
                Image,
                ImageDraw,
                ImageFont,
            )
        except ImportError:
            return None
        scale = 4
        glyph_font = ImageFont.truetype(str(cls.font_file), size * scale)

        def draw(fill: str) -> "Image.Image":
            canvas = Image.new("RGBA", (size * scale, size * scale), (0, 0, 0, 0))
            ImageDraw.Draw(canvas).text(
                (size * scale / 2, size * scale / 2),
                _GLYPHS[name][0],
                font=glyph_font,
                fill=fill,
                anchor="mm",
            )
            return canvas

        return ctk.CTkImage(
            light_image=draw(color[0]), dark_image=draw(color[1]), size=(size, size)
        )


def icon_text(
    name: str, text: str, size: int = 16, color: tuple[str, str] = INK
) -> dict:
    """Button options for an icon followed by text (an image when possible)."""
    image = Icons.image(name, size, color)
    if image is None:
        return {"text": f"{_GLYPHS[name][1]}  {text}"}
    return {"text": f"  {text}", "image": image, "compound": "left"}


def button(
    master: tk.Misc,
    icon: str,
    text: str,
    command: Callable[[], None],
    *,
    kind: str = "outline",
    width: int = 140,
    height: int = 40,
    tooltip: str = "",
) -> ctk.CTkButton:
    """A button in one of three looks: 'primary', 'outline' or 'danger'."""
    looks = {
        "primary": (ACCENT, ACCENT_HOVER, WHITE, 0),
        "outline": ("transparent", ACCENT_SOFT, INK, 1),
        "danger": (DANGER, DANGER_HOVER, WHITE, 0),
    }
    fill, hover, ink, border = looks[kind]
    widget = ctk.CTkButton(
        master,
        **icon_text(icon, text, 16, ink),
        font=font(13, "bold" if kind != "outline" else "normal"),
        width=width,
        height=height,
        corner_radius=10,
        fg_color=fill,
        hover_color=hover,
        border_width=border,
        border_color=BORDER,
        text_color=ink,
        command=command,
    )
    if tooltip:
        Tooltip(widget, tooltip)
    return widget


# ------------------------------------------------------------------ helpers


class Tooltip:  # pylint: disable=too-few-public-methods
    """A short explanation that appears when the mouse rests on a widget."""

    def __init__(self, widget: tk.Misc, text: str | Callable[[], str]) -> None:
        """Attach to widget; text may be a function for hints that change."""
        self.widget = widget
        self.text = text
        self.window: tk.Toplevel | None = None
        self.pending: str | None = None
        try:
            widget.bind("<Enter>", self._schedule, add="+")
            widget.bind("<Leave>", self._hide, add="+")
            widget.bind("<ButtonPress>", self._hide, add="+")
        except NotImplementedError:
            # Segmented buttons refuse bindings; their row's label has the tooltip
            pass

    def _schedule(self, _event: object = None) -> None:
        """Show after a short pause, so moving across doesn't flash hints."""
        self._cancel()
        self.pending = self.widget.after(450, self._show)

    def _cancel(self) -> None:
        """Forget a hint that was about to appear."""
        if self.pending is not None:
            self.widget.after_cancel(self.pending)
            self.pending = None

    def _show(self) -> None:
        """Draw the hint just below the widget."""
        text = self.text() if callable(self.text) else self.text
        if not text or not self.widget.winfo_exists():
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.window = tk.Toplevel(self.widget)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f"+{x}+{y}")
        self.window.attributes("-topmost", True)
        dark = ctk.get_appearance_mode() == "Dark"
        tk.Label(
            self.window,
            text=text,
            justify="left",
            wraplength=380,
            background="#313244" if dark else "#1F2937",
            foreground="#F8FAFC",
            padx=10,
            pady=7,
            font=("Segoe UI", 9),
        ).pack()

    def _hide(self, _event: object = None) -> None:
        """Remove the hint."""
        self._cancel()
        if self.window is not None:
            self.window.destroy()
            self.window = None


def hint(
    master: tk.Misc,
    text: str,
    color: tuple[str, str] = TEXT_DIM,
    margin: int = 0,
) -> ctk.CTkLabel:
    """A small grey explanation line that wraps to the width it is given."""
    label = ctk.CTkLabel(
        master,
        text=text,
        font=font(12),
        text_color=color,
        anchor="w",
        justify="left",
        wraplength=600,
    )
    fit_width(label, master, margin)
    return label


# Labels that wrap to their parent's width, per parent (by its Tk path name)
_FITTED: dict[str, list[tuple[ctk.CTkLabel, int]]] = {}


def fit_width(label: ctk.CTkLabel, master: tk.Misc, margin: int) -> None:
    """Keep a label's text wrapped inside master, whatever the window size or scale."""
    # One resize handler per parent, which forgets labels that have been destroyed
    fitted = _FITTED.get(str(master))
    if fitted is None:
        fitted = _FITTED[str(master)] = []

        def resize(event: tk.Event) -> None:
            fitted[:] = [(lbl, gap) for lbl, gap in fitted if lbl.winfo_exists()]
            for lbl, gap in fitted:
                # Events report real pixels, while wraplength is in unscaled units
                scale = lbl._get_widget_scaling()  # pylint: disable=protected-access
                lbl.configure(wraplength=max(160, int(event.width / scale) - gap))

        master.bind("<Configure>", resize, add="+")
    fitted.append((label, margin))


class Card(ctk.CTkFrame):
    """A rounded panel with an optional title and subtitle; content goes in .body."""

    def __init__(self, master: tk.Misc, title: str = "", subtitle: str = "") -> None:
        """Draw the panel."""
        super().__init__(
            master,
            fg_color=SURFACE,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        self.grid_columnconfigure(0, weight=1)
        row = 0
        if title:
            ctk.CTkLabel(self, text=title, font=font(15, "bold"), anchor="w").grid(
                row=row, column=0, sticky="ew", padx=20, pady=(16, 0)
            )
            row += 1
        if subtitle:
            hint(self, subtitle).grid(
                row=row, column=0, sticky="ew", padx=20, pady=(2, 0)
            )
            row += 1
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=row, column=0, sticky="nsew", padx=20, pady=(12, 18))
        self.body.grid_columnconfigure(0, weight=1)


class Section(Card):
    """A card whose body folds away: used for the 'Advanced' settings."""

    def __init__(self, master: tk.Misc, title: str, subtitle: str, open_: bool = False):
        """Draw the header with a show/hide button."""
        super().__init__(master, "", "")
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 0))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text=title, font=font(15, "bold"), anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        hint(header, subtitle, margin=140).grid(row=1, column=0, sticky="ew")
        self.toggle_button = ctk.CTkButton(
            header,
            width=120,
            height=32,
            corner_radius=8,
            fg_color="transparent",
            hover_color=ACCENT_SOFT,
            border_width=1,
            border_color=BORDER,
            text_color=INK,
            font=font(12),
            command=self.toggle,
        )
        self.toggle_button.grid(row=0, column=1, rowspan=2, padx=(10, 0))
        self.body.grid_configure(row=1)
        self.opened = open_
        self._apply()

    def toggle(self) -> None:
        """Show or hide the content."""
        self.opened = not self.opened
        self._apply()

    def _apply(self) -> None:
        """Match the body and the button to the state."""
        if self.opened:
            self.body.grid()
            self.toggle_button.configure(**icon_text("up", "Hide", 12))
        else:
            self.body.grid_remove()
            self.toggle_button.configure(**icon_text("down", "Show", 12))
        if not self.opened:
            self.grid_rowconfigure(1, minsize=14)


class Field(ctk.CTkFrame):
    """One setting: name on the left, control in the middle, explanation below."""

    def __init__(self, master: tk.Misc, label: str, help_text: str, tooltip: str = ""):
        """Lay out the name and the explanation; subclasses add the control."""
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)
        self.label = ctk.CTkLabel(
            self, text=label, font=font(13), width=150, anchor="w"
        )
        self.label.grid(row=0, column=0, sticky="w")
        # The explanation sits under the control, right of the 150-wide name column
        self.help_text = help_text
        self.help = hint(self, help_text, margin=170)
        self.help.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(1, 0))
        if tooltip:
            Tooltip(self.label, tooltip)

    def explain(self, text: str, color: tuple[str, str] = TEXT_DIM) -> None:
        """Change the explanation line (e.g. to a warning)."""
        self.help.configure(text=text, text_color=color)


class SliderField(Field):
    """A slider with its value shown on the right and a note under it."""

    def __init__(
        self,
        master: tk.Misc,
        label: str,
        help_text: str,
        low: float,
        high: float,
        steps: int,
        fmt: Callable[[float], str],
        on_change: Callable[[float], None],
        tooltip: str = "",
    ) -> None:
        """Build the row; call set() to show a value."""
        super().__init__(master, label, help_text, tooltip)
        self.fmt = fmt
        self.on_change = on_change
        self.quiet = False
        self.slider = ctk.CTkSlider(
            self,
            # CTkSlider takes floats (0.5 to 1.0 here), though its type hints say int
            from_=low,  # pyright: ignore[reportArgumentType]
            to=high,  # pyright: ignore[reportArgumentType]
            number_of_steps=steps,
            command=self._moved,
            button_color=ACCENT,
            button_hover_color=ACCENT_HOVER,
            progress_color=ACCENT,
        )
        self.slider.grid(row=0, column=1, sticky="ew", padx=10)
        self.value = ctk.CTkLabel(
            self, text="", font=font(12, "bold"), width=80, anchor="e"
        )
        self.value.grid(row=0, column=2, sticky="e")
        if tooltip:
            Tooltip(self.slider, tooltip)

    def _moved(self, value: float) -> None:
        """Show the new value and pass it on (unless we set it ourselves)."""
        self.value.configure(text=self.fmt(value))
        if not self.quiet:
            self.on_change(value)

    def set(self, value: float) -> None:
        """Show a value without treating it as the user's change."""
        self.quiet = True
        self.slider.set(value)
        self.value.configure(text=self.fmt(value))
        self.quiet = False

    def enable(self, on: bool) -> None:
        """Grey the slider out, or bring it back."""
        self.slider.configure(state="normal" if on else "disabled")
        self.value.configure(text_color=INK if on else TEXT_DIM)


class ChoiceField(Field):
    """A segmented button of named options, e.g. Path: Circle | Arc | Figure-8."""

    def __init__(
        self,
        master: tk.Misc,
        label: str,
        help_text: str,
        options: dict[str, object],
        on_change: Callable[[object], None],
        tooltip: str = "",
    ) -> None:
        """options maps shown text -> value."""
        super().__init__(master, label, help_text, tooltip)
        self.options = options
        self.on_change = on_change
        self.buttons = ctk.CTkSegmentedButton(
            self,
            values=list(options),
            command=lambda shown: self.on_change(self.options[shown]),
            selected_color=ACCENT,
            selected_hover_color=ACCENT_HOVER,
            font=font(12),
        )
        self.buttons.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(10, 0))

    def set(self, value: object) -> None:
        """Select the option whose value is `value`."""
        for shown, option in self.options.items():
            if option == value:
                self.buttons.set(shown)
                return

    def enable(self, on: bool) -> None:
        """Grey the whole choice out, or bring it back."""
        self.buttons.configure(state="normal" if on else "disabled")


class SwitchField(ctk.CTkFrame):
    """An on/off switch with its explanation under it."""

    def __init__(
        self,
        master: tk.Misc,
        text: str,
        help_text: str,
        on_change: Callable[[bool], None],
        tooltip: str = "",
    ) -> None:
        """Build the switch."""
        super().__init__(master, fg_color="transparent")
        self.on_change = on_change
        self.quiet = False
        self.switch = ctk.CTkSwitch(
            self, text=text, command=self._flipped, progress_color=ACCENT, font=font(13)
        )
        self.switch.grid(row=0, column=0, sticky="w")
        self.grid_columnconfigure(0, weight=1)
        # Indented under the switch's label, so it lines up with the text
        self.help = hint(self, help_text, margin=60)
        self.help.grid(row=1, column=0, sticky="ew", padx=(50, 0))
        if tooltip:
            Tooltip(self.switch, tooltip)

    def _flipped(self) -> None:
        """Pass the new state on (unless we set it ourselves)."""
        if not self.quiet:
            self.on_change(bool(self.switch.get()))

    def set(self, on: bool) -> None:
        """Show a state without treating it as the user's change."""
        if bool(self.switch.get()) != on:
            self.quiet = True
            self.switch.toggle()
            self.quiet = False

    def get(self) -> bool:
        """The current state."""
        return bool(self.switch.get())

    def enable(self, on: bool, why: str = "") -> None:
        """Grey the switch out (with the reason under it), or bring it back."""
        self.switch.configure(state="normal" if on else "disabled")
        if why:
            self.help.configure(text=why)

    def explain(self, text: str, color: tuple[str, str] = TEXT_DIM) -> None:
        """Change the explanation line."""
        self.help.configure(text=text, text_color=color)


class ChoiceMenu(ctk.CTkOptionMenu):
    """A drop-down list of choices in the window's colours."""

    def __init__(
        self,
        master: tk.Misc,
        values: list[str],
        on_change: Callable[[str], None],
        width: int = 280,
    ) -> None:
        """values are the words shown; on_change gets the one picked."""
        super().__init__(
            master,
            values=values,
            width=width,
            font=font(12),
            dropdown_font=font(12),
            dynamic_resizing=False,
            fg_color=SURFACE,
            button_color=ACCENT,
            button_hover_color=ACCENT,
            text_color=INK,
            dropdown_hover_color=ACCENT_SOFT,
            command=on_change,
        )

    def destroy(self) -> None:
        """Let go of the drop-down list completely."""
        dropdown = self._dropdown_menu
        super().destroy()
        # CustomTkinter 5.2 forgets this, so a later Size change would hit a closed list
        # pylint: disable-next=protected-access
        ctk.ScalingTracker.remove_widget(dropdown._set_scaling, dropdown)


class EntryField(Field):
    """A text box checked as you type: red border and a reason when it's wrong."""

    def __init__(
        self,
        master: tk.Misc,
        label: str,
        help_text: str,
        placeholder: str,
        on_change: Callable[[str], str | None],
        width: int = 260,
        tooltip: str = "",
    ) -> None:
        """on_change stores the text and returns an error message, or None."""
        super().__init__(master, label, help_text, tooltip)
        self.on_change = on_change
        self.entry = ctk.CTkEntry(
            self, placeholder_text=placeholder, width=width, font=font(12)
        )
        self.entry.grid(row=0, column=1, sticky="w", padx=10)
        self.entry.bind("<KeyRelease>", lambda _e: self.check())
        self.entry.bind("<FocusOut>", lambda _e: self.check())
        if tooltip:
            Tooltip(self.entry, tooltip)

    def check(self) -> bool:
        """Store the text; show the reason in red if it can't be used."""
        # A mistake that has been put right must not leave its red line behind
        self.explain(self.help_text)
        problem = self.on_change(self.entry.get())
        if problem:
            self.entry.configure(border_color=DANGER)
            self.explain(problem, DANGER)
            return False
        self.entry.configure(border_color=BORDER)
        return True

    def set(self, text: str) -> None:
        """Put text in the box (without checking)."""
        self.entry.delete(0, "end")
        if text:
            self.entry.insert(0, text)

    def enable(self, on: bool) -> None:
        """Grey the box out, or bring it back."""
        self.entry.configure(state="normal" if on else "disabled")


# The title bar and taskbar icon of every Audio8D window (also the exe's icon)
APP_ICON = Path(__file__).resolve().parent / "assets" / "audio8d.ico"


def use_app_icon(window: tk.Wm) -> None:
    """Show Audio8D's own icon in a window's title bar, where Windows allows it."""
    if os.name == "nt" and APP_ICON.is_file():
        try:
            window.iconbitmap(str(APP_ICON))
        except tk.TclError:
            pass


class Dialog(ctk.CTkToplevel):
    """A small modal window with a message and some buttons."""

    def __init__(
        self,
        master: ctk.CTk,
        title: str,
        message: str,
        buttons: list[tuple[str, str]],
        icon: str = "info",
        color: tuple[str, str] = ACCENT,
    ) -> None:
        """buttons: (text, key) pairs; the pressed key ends up in self.result."""
        super().__init__(master)
        self.title(title)
        use_app_icon(self)
        # CustomTkinter puts its own icon on new windows after 200 ms; ours goes back on
        self.after(250, lambda: use_app_icon(self))
        self.result: str | None = None
        self.resizable(False, False)
        self.transient(master)
        self.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            self, text=Icons.glyph(icon), font=Icons.font(30), text_color=color
        ).grid(row=0, column=0, rowspan=2, padx=(24, 12), pady=24, sticky="n")
        ctk.CTkLabel(self, text=title, font=font(16, "bold"), anchor="w").grid(
            row=0, column=1, sticky="w", padx=(0, 24), pady=(24, 4)
        )
        ctk.CTkLabel(
            self,
            text=message,
            font=font(13),
            justify="left",
            anchor="w",
            wraplength=460,
        ).grid(row=1, column=1, sticky="w", padx=(0, 24))
        self.actions = ctk.CTkFrame(self, fg_color="transparent")
        self.actions.grid(row=2, column=0, columnspan=2, sticky="e", padx=24, pady=20)
        # Each button by its key, so a subclass can switch one off
        self.buttons: dict[str, ctk.CTkButton] = {}
        for index, (text, key) in enumerate(buttons):
            primary = index == len(buttons) - 1
            self.buttons[key] = ctk.CTkButton(
                self.actions,
                text=text,
                width=120,
                fg_color=ACCENT if primary else "transparent",
                hover_color=ACCENT_HOVER if primary else ACCENT_SOFT,
                border_width=0 if primary else 1,
                border_color=BORDER,
                text_color=WHITE if primary else INK,
                command=lambda key=key: self.close(key),
            )
            self.buttons[key].pack(side="left", padx=(8, 0))
        self.bind("<Escape>", lambda _e: self.close(None))
        self.protocol("WM_DELETE_WINDOW", lambda: self.close(None))
        self.after(50, self._center)

    def _center(self) -> None:
        """Sit in the middle of the main window, and take the focus."""
        self.update_idletasks()
        master = self.master
        x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        try:
            self.grab_set()
        except tk.TclError:
            pass
        self.focus_force()

    def close(self, key: str | None) -> None:
        """Remember the answer and close."""
        self.result = key
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()

    def ask(self) -> str | None:
        """Wait until a button is pressed and return its key."""
        self.master.wait_window(self)
        return self.result


class NameDialog(Dialog):
    """Asks for a style name, checking it as you type; OK only works when it's valid."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        master: ctk.CTk,
        title: str,
        message: str,
        initial: str,
        check: Callable[[str], tuple[str | None, str | None]],
        ok_text: str = "OK",
    ) -> None:
        """check(text) returns (the name it will get, None) or (None, why not)."""
        super().__init__(master, title, message, [("Cancel", "no"), (ok_text, "ok")])
        self.check_name = check
        self.value: str | None = None
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.grid(row=2, column=1, sticky="ew", padx=(0, 24), pady=(14, 0))
        self.entry = ctk.CTkEntry(box, width=320, font=font(13))
        self.entry.grid(row=0, column=0, sticky="w")
        self.entry.insert(0, initial)
        self.note = ctk.CTkLabel(
            box, text="", font=font(12), anchor="w", justify="left", wraplength=440
        )
        self.note.grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.actions.grid(row=3, column=0, columnspan=2, sticky="e", padx=24, pady=20)
        self.entry.bind("<KeyRelease>", lambda _e: self.check())
        self.entry.bind("<Return>", lambda _e: self._accept())
        self.check()
        self.after(120, self.entry.focus_set)

    def check(self) -> bool:
        """Show what the name will be, or why it can't be used."""
        name, problem = self.check_name(self.entry.get())
        ok = self.buttons["ok"]
        if problem or not name:
            self.value = None
            self.entry.configure(border_color=DANGER)
            self.note.configure(text=problem or "", text_color=DANGER)
            ok.configure(state="disabled")
            return False
        self.value = name
        self.entry.configure(border_color=BORDER)
        self.note.configure(text=f"It will be saved as {name}", text_color=SUCCESS)
        ok.configure(state="normal")
        return True

    def _accept(self) -> None:
        """Enter works like OK, but only for a valid name."""
        if self.check():
            self.close("ok")

    def ask(self) -> str | None:
        """The valid name that was accepted, or None for Cancel."""
        return self.value if super().ask() == "ok" else None


class Toast(ctk.CTkFrame):
    """A short message in the status bar that goes away by itself."""

    def __init__(self, master: ctk.CTk, text: str, kind: str = "info") -> None:
        """Show text for a few seconds without covering any control."""
        color = {"info": ACCENT, "ok": SUCCESS, "error": DANGER}[kind]
        icon = {"info": "info", "ok": "check", "error": "error"}[kind]
        # The app lends its status-bar summary cell; floating would cover buttons
        slot = getattr(master, "toast_slot", None)
        super().__init__(
            slot[0] if slot else master,
            fg_color=SURFACE_ALT,
            corner_radius=10,
            border_width=1,
            border_color=color,
        )
        ctk.CTkLabel(
            self, text=Icons.glyph(icon), font=Icons.font(15), text_color=color
        ).pack(side="left", padx=(12, 8), pady=4)
        ctk.CTkLabel(self, text=text, font=font(13)).pack(
            side="left", padx=(0, 14), pady=4
        )
        self.slot = slot
        if slot:
            area, hidden = slot
            for other in area.winfo_children():
                if isinstance(other, Toast) and other is not self:
                    other.destroy()
            hidden.grid_remove()
            self.grid(row=0, column=2, sticky="e", padx=28)
        else:
            self.place(relx=1.0, rely=1.0, x=-24, y=-24, anchor="se")
        self.after(4000, self.destroy)

    def destroy(self) -> None:
        """Hand the status-bar cell back to what it normally shows."""
        try:
            if self.slot and self.winfo_exists():
                area, hidden = self.slot
                others = [
                    w
                    for w in area.winfo_children()
                    if isinstance(w, Toast) and w is not self
                ]
                if not others:
                    hidden.grid()
        except tk.TclError:  # the window itself is closing
            pass
        super().destroy()
