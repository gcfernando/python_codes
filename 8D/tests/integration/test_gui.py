# Developed by ::> Gehan Fernando
"""Drives the real Audio8D window: start-up, adding songs, validation, converting."""

# pytest hands fixtures to tests by name, which pylint sees as shadowing
# pylint: disable=redefined-outer-name,protected-access

import gc
import importlib.util
import json
import os
import time
from pathlib import Path

import pytest

from src import EffectConfig
from src.core.locations import presets_file
from src.core.user_presets import (
    delete_user_preset,
    rename_user_preset,
    save_user_preset,
)
from src.ffmpeg.toolchain import FFmpegToolchain

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("customtkinter") is None,
    reason="the window needs CustomTkinter (pip install customtkinter)",
)


@pytest.fixture(scope="module")
def window():
    """One real window for the whole module (Tk dislikes many in one process)."""
    tk = pytest.importorskip("tkinter")
    from src.gui_app import Audio8DApp  # pylint: disable=import-outside-toplevel

    try:
        made = Audio8DApp()
    except tk.TclError as exc:  # no screen, e.g. on a server
        pytest.skip(f"no display: {exc}")
    made.update()
    yield made
    made.cancel.set()
    made.destroy()


@pytest.fixture
def app(window):
    """The shared window, back to a fresh start: no songs, the best style."""
    from src.gui_model import GuiSettings  # pylint: disable=import-outside-toplevel

    window.clear_songs()
    window.settings = GuiSettings()
    window.settings.apply_style(window.presets["studio"])
    window.sync_controls()
    window.show_page("songs")
    window.__dict__.pop("report", None)
    window.update()
    return window


def _pump(window, until, seconds: float = 90.0) -> None:
    """Let the window run until a condition is true (or give up)."""
    end = time.time() + seconds
    while not until() and time.time() < end:
        window.update()
        time.sleep(0.02)
    window.update()


def test_window_starts_on_step_one_with_the_best_style(app) -> None:
    assert app.current == "songs"
    assert app.settings.style == "studio"
    for key in ("songs", "sound", "output", "review", "styles", "settings"):
        app.show_page(key)
        app.update()
        assert app.current == key


def test_adding_songs_and_reading_their_details(app, stereo_tone: Path) -> None:
    app.add_paths([stereo_tone, stereo_tone.with_name("notes.txt")])
    _pump(app, lambda: app.rows and app.rows[0].length_text != "…", 20)

    assert [row.song for row in app.rows] == [stereo_tone]
    assert app.rows[0].length_text == "0:03"
    assert app.rows[0].view.length.cget("text") == "0:03"
    app.add_paths([stereo_tone])
    assert len(app.rows) == 1


def test_start_is_blocked_until_the_setup_is_valid(app, stereo_tone: Path) -> None:
    app.show_page("review")
    app.update()
    assert str(app.pages["review"].start.cget("state")) == "disabled"

    app.add_paths([stereo_tone])
    app.set_speed_curve("nonsense")
    app.run_convert()
    assert not app.busy
    app.set_speed_curve("")
    app.show_page("review")
    app.update()
    assert str(app.pages["review"].start.cget("state")) == "normal"


def test_a_real_conversion_from_the_window(
    app,
    stereo_tone: Path,
    tmp_path: Path,
) -> None:
    if FFmpegToolchain.discover is None:  # pragma: no cover
        pytest.skip("no FFmpeg")
    out = tmp_path / "8D"
    app.add_paths([stereo_tone])
    app.settings.destination = str(out)
    app.change_sound(output_format="flac")
    app._show_report = lambda report: setattr(app, "report", report)
    app.run_convert()
    app.update()
    # A waiting row is one compact line pair, not stretched by empty button space
    assert app.run_rows[0].winfo_reqheight() < 160
    _pump(app, lambda: not app.busy and hasattr(app, "report"))

    made = out / "tone (8D).flac"
    assert made.is_file(), app.run_rows[0].status.cget("text")
    assert len(app.report.converted) == 1
    status = app.run_rows[0].status.cget("text")
    assert "Saved as tone (8D).flac" in status and "LUFS" in status


def test_a_failing_song_shows_the_reason_and_the_fix(
    app,
    tmp_path: Path,
) -> None:
    broken = tmp_path / "broken.mp3"
    broken.write_bytes(b"this is not music")
    app.add_paths([broken])
    app._show_report = lambda report: setattr(app, "report", report)
    app.run_convert()
    _pump(app, lambda: not app.busy and hasattr(app, "report"), 30)

    assert len(app.report.failed) == 1
    assert "What to do" in app.run_rows[0].status.cget("text")


def _open_everything(app) -> None:
    """Every 'Advanced' section open and every optional box showing."""
    for page in app.pages.values():
        for child in page.winfo_children():
            if child.__class__.__name__ == "Section" and not child.opened:
                child.toggle()
    app.change_sound(beat_sync=True)
    app.pages["output"]._loudness("custom")
    app.set_name_style("custom")
    app.pages["output"].wants_folder = True
    # A song with its own style, a saved style's buttons, and the creator's advice
    save_user_preset("LayoutCheck", EffectConfig(), summary="x" * 110)
    app.reload_styles()
    if app.rows:
        app.set_song_style(app.rows[0], "LayoutCheck")
    app.pages["styles"]._answer(level="natural")
    app.sync_controls()


@pytest.mark.parametrize("scale", [1.0, 1.25])
def test_no_control_ever_overlaps_or_spills_out(
    app, stereo_tone: Path, scale: float
) -> None:
    ctk = pytest.importorskip("customtkinter")
    # pylint: disable-next=import-outside-toplevel
    from src.gui_layout import layout_problems

    app.add_paths([stereo_tone])
    _open_everything(app)
    ctk.set_widget_scaling(scale)
    try:
        for size in ("1100x720", "1600x1000"):
            app.geometry(size)
            for key in app.pages:
                app.show_page(key)
                app.update()
                assert layout_problems(app, app.pages[key]) == [], (scale, size, key)
    finally:
        ctk.set_widget_scaling(1.0)
        app.geometry("1280x860")
        delete_user_preset("LayoutCheck")
        app.pages["styles"]._music_picked("mixed")
        app.reload_styles()


def test_controls_show_only_what_applies(app) -> None:
    output = app.pages["output"]
    app.change_sound(output_format="flac")
    app.update()
    assert output.bitrate.buttons._state == "disabled"
    assert not output.quality.winfo_ismapped()
    app.change_sound(output_format="mp3", bitrate=None)
    app.show_page("output")
    for child in output.winfo_children():
        if child.__class__.__name__ == "Section" and not child.opened:
            child.toggle()
    app.update()
    assert output.quality.winfo_ismapped()
    output._loudness(None)
    assert str(output.exact.switch.cget("state")) == "disabled"
    output._loudness("custom")
    app.update()
    assert output.custom_loud.winfo_ismapped()
    assert app.set_custom_loudness("-50") is not None
    assert app.set_custom_loudness("-16") is None
    assert (
        app.settings.sound.loudness_target is not None
        or app.settings.loudness_is_custom
    )
    output._loudness("match")
    assert app.settings.sound.match_loudness is True


def test_preview_and_compare_from_the_window(
    app, dynamic_song: Path, monkeypatch
) -> None:
    opened: list[Path] = []
    monkeypatch.setattr("src.gui_app.open_path", opened.append)
    app.add_paths([dynamic_song])
    app.settings.preview_seconds = 10
    app.run_preview()
    _pump(app, lambda: not app.busy)
    app.run_compare()
    _pump(app, lambda: not app.busy)

    names = [path.name for path in opened]
    assert "dynamic (8D preview).mp3" in names
    assert "dynamic (A-B compare).mp3" in names


def test_saving_and_deleting_a_style(app, monkeypatch) -> None:
    styles = app.pages["styles"]
    styles.name.set("qa style")
    styles.summary.set("made by the tests")
    styles._save()
    # Saved in PascalCase, and straight away a card on step 2
    assert "Qa Style" in app.presets and app.presets["Qa Style"].custom
    assert "Qa Style" in app.pages["sound"].cards

    # The same name again, in any form, is refused and nothing is replaced
    before = presets_file().read_text(encoding="utf-8")
    styles.name.set("QA-style")
    styles._save()
    assert "already have a style" in styles.name.help.cget("text")
    assert presets_file().read_text(encoding="utf-8") == before

    monkeypatch.setattr("src.gui_app.Dialog.ask", lambda self: "yes")
    styles._delete("Qa Style")
    assert "Qa Style" not in app.presets


def test_stop_keeps_the_window_usable(app, dynamic_song: Path, tmp_path: Path) -> None:
    app.add_paths([dynamic_song])
    app.settings.destination = str(tmp_path / "out")
    app._show_report = lambda report: setattr(app, "report", report)
    app.run_convert()
    app.stop()
    _pump(app, lambda: not app.busy, 60)

    assert not app.busy
    assert "Stopped" in app.status_text.cget("text")
    assert str(app.pages["review"].start.cget("state")) == "normal"


def test_replacing_the_originals_from_the_window(
    app, stereo_tone: Path, monkeypatch
) -> None:
    removed: list[Path] = []

    def fake_remove(path: Path) -> str:
        removed.append(path)
        path.unlink()
        return "Recycle Bin"

    monkeypatch.setattr("src.pipeline.remove_original", fake_remove)
    monkeypatch.setattr("src.gui_app.Dialog.ask", lambda self: "yes")
    app.add_paths([stereo_tone])
    app.set_originals("replace")
    app._show_report = lambda report: setattr(app, "report", report)
    app.run_convert()
    _pump(app, lambda: not app.busy and hasattr(app, "report"))

    assert removed == [stereo_tone]
    assert stereo_tone.is_file()  # now the 8D version, under the original name
    assert "original moved to the Recycle Bin" in app.run_rows[0].status.cget("text")


def test_notices_sit_in_the_status_bar_not_over_buttons(app) -> None:
    from src.gui_widgets import Toast  # pylint: disable=import-outside-toplevel

    area, summary = app.toast_slot
    Toast(app, "first")
    latest = Toast(app, "second", "ok")
    app.update()
    shown = [w for w in area.winfo_children() if isinstance(w, Toast)]
    assert shown == [latest] and latest.winfo_ismapped()
    assert not summary.winfo_ismapped()
    latest.destroy()
    app.update()
    assert summary.winfo_ismapped()


def test_garbage_is_only_collected_on_the_window_thread(app) -> None:
    # A Tk font freed on the conversion thread once stalled a whole conversion
    assert not gc.isenabled()
    app._collect_garbage()
    assert not gc.isenabled()


def test_stopping_a_preview_is_not_reported_as_an_error(
    app, dynamic_song: Path, monkeypatch
) -> None:
    shown: list[str] = []
    monkeypatch.setattr("src.gui_app.Dialog.ask", lambda self: shown.append("dialog"))
    monkeypatch.setattr("src.gui_app.open_path", lambda _path: None)
    app.add_paths([dynamic_song])
    app.run_preview()
    app.stop()
    _pump(app, lambda: not app.busy, 60)

    assert not shown
    assert "Stopped" in app.status_text.cget("text")


def test_a_broken_styles_file_is_explained_not_hidden(app) -> None:

    presets_file().parent.mkdir(parents=True, exist_ok=True)
    presets_file().write_text("[mine]\nintensity = lots\n", encoding="utf-8")
    try:
        app.presets = app._load_styles()
        app.pages["styles"].refresh()
        texts = [
            w.cget("text") for w in app.pages["styles"].saved.body.winfo_children()
        ]

        assert "studio" in app.presets
        assert any("line 2" in text and "Fix that line" in text for text in texts)
    finally:
        presets_file().unlink()
        app.presets = app._load_styles()
        app.pages["styles"].refresh()
    assert app.styles_problem is None


@pytest.mark.skipif(os.name != "nt", reason="drag-and-drop from File Explorer")
def test_songs_dropped_from_file_explorer_are_added(app, stereo_tone: Path) -> None:
    import ctypes  # pylint: disable=import-outside-toplevel
    from ctypes import wintypes  # pylint: disable=import-outside-toplevel

    kernel32, user32 = ctypes.windll.kernel32, ctypes.windll.user32
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    user32.GetParent.restype = wintypes.HWND
    user32.PostMessageW.argtypes = [
        wintypes.HWND,
        wintypes.UINT,
        ctypes.c_void_p,
        wintypes.LPARAM,
    ]
    # The same DROPFILES block File Explorer sends: a header, then wide file names
    names = (str(stereo_tone) + "\0\0").encode("utf-16-le")
    header = ctypes.sizeof(wintypes.DWORD) * 5
    block = kernel32.GlobalAlloc(0x0042, header + len(names))
    memory = kernel32.GlobalLock(block)
    ctypes.memmove(memory, (wintypes.DWORD * 5)(header, 0, 0, 0, 1), header)
    ctypes.memmove(memory + header, names, len(names))
    kernel32.GlobalUnlock(block)

    user32.PostMessageW(user32.GetParent(app.winfo_id()), 0x0233, block, 0)
    _pump(app, lambda: bool(app.rows), 10)

    assert [row.song for row in app.rows] == [stereo_tone]


def test_long_lists_show_a_page_at_a_time_but_convert_everything(
    app, tmp_path: Path
) -> None:
    from src.gui_app import SONGS_PER_PAGE  # pylint: disable=import-outside-toplevel

    # Files that fail at once keep this quick; each still needs its row or count
    songs = []
    for number in range(60):
        song = tmp_path / f"broken {number:02}.mp3"
        song.write_bytes(b"not music")
        songs.append(song)
    app.add_paths(songs)
    app.update()
    songs_page = app.pages["songs"]

    assert len(app.rows) == 60
    assert sum(1 for row in app.rows if row.view) == SONGS_PER_PAGE
    assert "Showing 25 of 60 songs. All 60 will be converted." in (
        songs_page.more_text.cget("text")
    )
    app.show_more_songs()
    app.update()
    assert sum(1 for row in app.rows if row.view) == 2 * SONGS_PER_PAGE

    for row in app.rows[30:]:
        app.remove_row(row)
    app._show_report = lambda report: setattr(app, "report", report)
    app.settings.destination = str(tmp_path / "out")
    app.run_convert()
    _pump(app, lambda: not app.busy and hasattr(app, "report"), 60)

    review = app.pages["review"]
    assert len(app.run_rows) == SONGS_PER_PAGE
    assert len(app.report.failed) == 30
    # The five songs past the first page failed too, so each got its own row
    assert review.rest == [0, 5, 5]
    assert len(review.run_list.winfo_children()) == SONGS_PER_PAGE + 5 + 1
    assert "0 made, 5 failed" in review.rest_line.cget("text")


def test_message_windows_keep_the_audio8d_icon(app, monkeypatch) -> None:
    from src.gui_widgets import Dialog  # pylint: disable=import-outside-toplevel

    opened = time.perf_counter()
    applied: list[float] = []
    monkeypatch.setattr(
        "src.gui_widgets.use_app_icon",
        lambda _window: applied.append(time.perf_counter() - opened),
    )
    dialog = Dialog(app, "Test", "A message", [("OK", "ok")])
    # CustomTkinter puts its own icon on new windows after 200 ms
    _pump(app, lambda: False, 0.5)

    assert any(when >= 0.2 for when in applied)
    dialog.close("ok")


def test_the_guide_opens_online_when_no_readme_is_beside_the_app(
    monkeypatch, tmp_path: Path
) -> None:
    from src import gui_app  # pylint: disable=import-outside-toplevel

    opened: list[str] = []
    monkeypatch.setattr(gui_app, "guide_file", lambda: tmp_path / "README.md")
    monkeypatch.setattr(gui_app.webbrowser, "open", opened.append)

    gui_app.SettingsPage._open_guide()  # pylint: disable=protected-access

    assert opened == [gui_app.GUIDE_URL]


def _texts(widget) -> list[str]:
    """Every label's text inside a widget, however deep."""
    found = []
    for child in widget.winfo_children():
        try:
            found.append(str(child.cget("text")))
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        found += _texts(child)
    return found


def test_built_in_style_names_are_shown_capitalised(app) -> None:
    sound = app.pages["sound"]
    cards = {name: _texts(card) for name, card in sound.cards.items()}

    assert any(text.startswith("Studio") and "best" in text for text in cards["studio"])
    assert "Streaming" in cards["streaming"]
    assert sound.style_note.cget("text") == "Style: Studio"
    choices = sound.style_choices()
    assert choices["Same as all songs"] is None
    assert choices["Studio"] == "studio" and choices["Streaming"] == "streaming"
    app.show_page("review")
    assert "Studio" in _texts(app.pages["review"].summary)
    # The names people type stay the same everywhere else
    assert "studio" in app.presets and app.settings.style == "studio"


def test_one_style_for_all_songs_or_one_per_song(
    app, stereo_tone: Path, tmp_path: Path
) -> None:
    from src.gui_model import items_for  # pylint: disable=import-outside-toplevel

    second = tmp_path / "second.mp3"
    second.write_bytes(stereo_tone.read_bytes())
    app.add_paths([stereo_tone, second])
    app.update()
    sound = app.pages["sound"]
    songs = [(row.song, row.folder) for row in app.rows]

    # Nothing chosen: every song simply uses the style for all songs, as before
    assert "All 2 songs use the style above." in sound.own_note.cget("text")
    assert all(item.config is None for item in items_for(app.settings, songs))

    app.set_song_style(app.rows[1], "voice")
    app.set_song_style(app.rows[1], "lossless")  # changed again later
    assert "1 of 2 songs has its own style" in sound.own_note.cget("text")
    assert "1 song with own style" in app.settings_text.cget("text")
    app.show_page("review")
    assert any("second: Lossless" in text for text in _texts(app.pages["review"]))

    app.settings.destination = str(tmp_path / "out")
    app._show_report = lambda report: setattr(app, "report", report)
    app.run_convert()
    _pump(app, lambda: not app.busy and hasattr(app, "report"), 90)

    assert len(app.report.converted) == 2
    assert (tmp_path / "out" / "tone (8D).mp3").is_file()
    assert (tmp_path / "out" / "second (8D).flac").is_file()

    app.set_song_style(app.rows[1], None)
    assert not app.settings.song_styles
    app.set_song_style(app.rows[1], "voice")
    app.remove_row(app.rows[1])
    assert not app.settings.song_styles


def test_your_styles_join_the_song_menus_and_follow_renames(
    app, stereo_tone: Path
) -> None:
    styles = app.pages["styles"]
    styles._music_picked("calm")
    styles.new_name.set("night drive")
    styles._new_name_typed("night drive")
    styles._create()
    try:
        assert app.presets["Night Drive"].custom
        assert app.settings.style == "Night Drive"
        assert app.pages["sound"].style_choices()["Night Drive   (yours)"] == (
            "Night Drive"
        )

        app.add_paths([stereo_tone])
        app.update()
        app.set_song_style(app.rows[0], "Night Drive")
        new = rename_user_preset("Night Drive", "drive at night")
        app.reload_styles(renamed=("Night Drive", new))
        assert app.settings.song_styles[app.rows[0].song] == "Drive At Night"
        assert app.settings.style == "Drive At Night"

        delete_user_preset("Drive At Night")
        assert app.reload_styles() == 1
        assert not app.settings.song_styles
    finally:
        delete_user_preset("Night Drive")
        delete_user_preset("Drive At Night")
        app.reload_styles()


def test_the_style_creator_guides_checks_and_improves(app, monkeypatch) -> None:
    styles = app.pages["styles"]
    styles._music_picked("talk")
    assert styles.answers.room == "none" and styles.answers.movement == "gentle"
    assert styles.new_name.entry.get() == "Voice Mix"
    assert "Talking" in styles.new_summary.entry.get()
    assert "front" in styles.result.cget("text")
    assert "looks good" in " ".join(_texts(styles.checks))

    styles._answer(level="natural")
    assert any("quieter" in text for text in _texts(styles.checks))
    assert styles.improve.winfo_manager()
    styles._improve()
    assert styles.answers.level == "apps"

    # A built-in name is explained and nothing is saved
    styles.new_name.set("studio")
    styles._create()
    assert "built-in" in styles.new_name.help.cget("text")
    assert not any(preset.custom for preset in app.presets.values())

    # A weak style is offered an improvement before it is saved
    styles._answer(level="natural")
    styles.new_name.set("Quiet Talk")
    monkeypatch.setattr("src.gui_app.Dialog.ask", lambda self: "improve")
    styles._create()
    try:
        assert app.presets["Quiet Talk"].config.loudness_target == -14.0
    finally:
        delete_user_preset("Quiet Talk")
        app.reload_styles()
        styles._music_picked("mixed")


def test_the_name_dialog_only_accepts_a_free_valid_name(app) -> None:
    from src.gui_widgets import NameDialog  # pylint: disable=import-outside-toplevel

    save_user_preset("PartyMix", EffectConfig())
    app.reload_styles()
    try:
        styles = app.pages["styles"]
        dialog = NameDialog(app, "Name", "Pick one", "party mix", styles.check_name)
        app.update()
        assert str(dialog.buttons["ok"].cget("state")) == "disabled"
        assert "already have a style" in dialog.note.cget("text")

        dialog.entry.delete(0, "end")
        dialog.entry.insert(0, "new one")
        assert dialog.check()
        assert str(dialog.buttons["ok"].cget("state")) == "normal"
        assert dialog.value == "New One"
        assert "saved as New One" in dialog.note.cget("text")
        dialog.close("no")
    finally:
        delete_user_preset("PartyMix")
        app.reload_styles()


def test_rename_duplicate_export_and_import_in_the_window(
    app, monkeypatch, tmp_path: Path
) -> None:
    save_user_preset("PartyMix", EffectConfig(intensity=0.95), summary="loud")
    app.reload_styles()
    styles = app.pages["styles"]
    shared = tmp_path / "PartyMix.json"
    shown: list[str] = []
    monkeypatch.setattr(
        "src.gui_app.filedialog.asksaveasfilename", lambda **_: str(shared)
    )
    monkeypatch.setattr(
        "src.gui_app.filedialog.askopenfilename", lambda **_: str(shared)
    )
    monkeypatch.setattr(
        "src.gui_app.Dialog.ask", lambda self: shown.append(self.title())
    )
    try:
        styles._export("PartyMix")
        assert json.loads(shared.read_text(encoding="utf-8"))["name"] == "PartyMix"

        # The file's own name is taken, so the name the user chose is used
        monkeypatch.setattr("src.gui_app.NameDialog.ask", lambda self: "PartyCopy")
        styles._import()
        assert app.presets["PartyCopy"].config == app.presets["PartyMix"].config

        monkeypatch.setattr("src.gui_app.NameDialog.ask", lambda self: "PartyTwo")
        styles._duplicate("PartyMix")
        monkeypatch.setattr("src.gui_app.NameDialog.ask", lambda self: "PartyThree")
        styles._rename("PartyTwo")
        assert "PartyThree" in app.presets and "PartyTwo" not in app.presets

        # A broken file is explained and changes nothing
        before = presets_file().read_text(encoding="utf-8")
        shared.write_text('{"format": "audio8d-style"}', encoding="utf-8")
        styles._import()
        assert shown == ["Can't import this style"]
        assert presets_file().read_text(encoding="utf-8") == before
    finally:
        for name in ("PartyMix", "PartyCopy", "PartyThree"):
            delete_user_preset(name)
        app.reload_styles()


def test_a_corrected_box_loses_its_red_message(app) -> None:
    sound = app.pages["sound"]
    field = sound.amount_curve
    field.set("0=0.5, 1:00=1.5")
    field.check()
    assert "between 0 and 1" in field.help.cget("text")

    field.set("")
    field.check()
    assert field.help.cget("text") == field.help_text
    app.set_intensity_curve("")


def test_step_four_warns_about_low_quality_song_files(app, stereo_tone: Path) -> None:
    # pylint: disable-next=import-outside-toplevel
    from src.core.types import AudioStreamInfo

    app.add_paths([stereo_tone])
    app.update()
    app.rows[0].info = AudioStreamInfo("mp3", 2, 44100, 3.0, 96_000)
    app.show_page("review")

    notes = " ".join(_texts(app.pages["review"].notes))
    assert "1 song is a low-quality file (tone)" in notes
    assert "Everything is ready" in notes


def test_scrollbars_no_longer_force_a_layout_pass(app) -> None:
    import customtkinter as ctk  # pylint: disable=import-outside-toplevel

    from src import gui_widgets  # pylint: disable=import-outside-toplevel

    # Every scrolling page draws with the quicker version, and still scrolls
    assert ctk.CTkScrollbar._draw is gui_widgets._draw_scrollbar_without_flush
    page = app.pages["sound"]
    app.show_page("sound")
    page._parent_canvas.yview_moveto(0.5)
    app.update()
    assert page._scrollbar._canvas.update_idletasks is gui_widgets._no_flush
    assert page._parent_canvas.yview()[0] > 0
