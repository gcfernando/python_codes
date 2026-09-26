# Developed by Gehan Fernando
"""Checks the audio8d command: options, styles, messages and the guided mode."""

from pathlib import Path

import pytest

from audio8d import PRESETS, ConversionError, EffectConfig, InputValidationError, cli
from audio8d.files import resolve_input

_REAL_RESOLVE_INPUT = resolve_input


@pytest.fixture(autouse=True)
def _pretend_songs_exist(monkeypatch: pytest.MonkeyPatch) -> None:
    """Let tests use made-up song names without real files on disk."""
    # Most tests use made-up song names, so skip the file-exists check by default
    monkeypatch.setattr(cli, "resolve_input", lambda path: path)


def test_no_knobs_means_the_classic_defaults() -> None:
    args = cli.create_parser().parse_args(["in.mp3", "out.mp3"])

    assert cli.resolve_config(args) == EffectConfig()
    assert args.overwrite is False


def test_quality_outside_range_is_a_usage_error() -> None:
    with pytest.raises(SystemExit):
        cli.create_parser().parse_args(["in.mp3", "out.mp3", "--quality", "10"])


def test_main_passes_options_through(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    def fake_convert(**kwargs: object) -> None:
        """Remember what the command asked for instead of converting."""
        seen.update(kwargs)

    monkeypatch.setattr(cli, "convert", fake_convert)
    code = cli.main(
        ["a.wav", "b.mp3", "--intensity", "0.5", "--quality", "0", "--overwrite"]
    )

    assert code == 0
    assert seen["input_path"] == Path("a.wav")
    assert seen["overwrite"] is True
    assert seen["config"] == EffectConfig(intensity=0.5, mp3_quality=0)


def test_main_returns_1_on_known_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def failing_convert(**_: object) -> None:
        """Fail the way a broken encode would."""
        raise ConversionError("boom")

    monkeypatch.setattr(cli, "convert", failing_convert)

    assert cli.main(["a.wav", "b.mp3"]) == 1


def test_default_output_sits_next_to_the_input() -> None:
    assert cli.default_output_for(Path("music/song.flac")) == Path(
        "music/song (8D).mp3"
    )


def test_output_name_is_optional(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}
    monkeypatch.setattr(cli, "convert", lambda **kwargs: seen.update(kwargs))

    assert cli.main(["song.wav"]) == 0
    assert seen["output_path"] == Path("song (8D).mp3")


@pytest.mark.parametrize(
    "typed",
    [
        r"C:\Music\My Song.mp3",
        r'"C:\Music\My Song.mp3"',
        r"'C:\Music\My Song.mp3'",
        r'  "C:\Music\My Song.mp3"  ',
        r"& 'C:\Music\My Song.mp3'",
    ],
)
def test_dragged_or_pasted_paths_are_cleaned(typed: str) -> None:
    # pylint: disable-next=protected-access
    assert cli._clean_typed_path(typed) == r"C:\Music\My Song.mp3"


def _pretend_double_click(monkeypatch: pytest.MonkeyPatch, answers: list[str]) -> None:
    """Act like a real person in a terminal who types these answers in order."""
    monkeypatch.setattr(cli.sys, "argv", ["audio8d"])
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True, raising=False)
    monkeypatch.setattr(cli.sys.stdout, "isatty", lambda: True, raising=False)
    replies = iter(answers)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(replies))


def _song(tmp_path: Path) -> Path:
    """A tiny real file to stand in for a song."""
    song = tmp_path / "song.mp3"
    song.write_bytes(b"audio")
    return song


def test_double_click_asks_for_a_song_and_converts_it(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    seen: dict[str, object] = {}
    monkeypatch.setattr(cli, "convert", lambda **kwargs: seen.update(kwargs))
    song = _song(tmp_path)
    # Dragged-in path, Enter for the best style, Enter to close
    _pretend_double_click(monkeypatch, [f'"{song}"', "", ""])

    assert cli.main() == 0
    assert seen["input_path"] == song
    assert seen["output_path"] == tmp_path / "song (8D).mp3"
    assert seen["config"] == PRESETS["studio"].config


def test_guided_mode_asks_again_for_a_missing_song(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    seen: dict[str, object] = {}
    monkeypatch.setattr(cli, "convert", lambda **kwargs: seen.update(kwargs))
    song = _song(tmp_path)
    _pretend_double_click(
        monkeypatch, [str(tmp_path / "nope.mp3"), str(tmp_path), str(song), "", ""]
    )

    assert cli.main() == 0
    shown = capsys.readouterr().out
    assert "I can't find that file" in shown
    assert "That is a folder" in shown
    assert seen["input_path"] == song


@pytest.mark.parametrize(
    ("answer", "style"), [("", "studio"), ("4", "smooth"), ("voice", "voice")]
)
def test_guided_mode_style_menu(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, answer: str, style: str
) -> None:
    seen: dict[str, object] = {}
    monkeypatch.setattr(cli, "convert", lambda **kwargs: seen.update(kwargs))
    _pretend_double_click(monkeypatch, [str(_song(tmp_path)), answer, ""])

    assert cli.main() == 0
    assert seen["config"] == PRESETS[style].config


def test_guided_mode_explains_a_bad_style_answer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "convert", lambda **_: None)
    _pretend_double_click(monkeypatch, [str(_song(tmp_path)), "99", "", ""])

    assert cli.main() == 0
    assert "Please type a number from 1 to 8" in capsys.readouterr().out


def test_double_click_with_no_answer_does_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli, "convert", lambda **_: pytest.fail("should not convert"))
    _pretend_double_click(monkeypatch, ["", ""])

    assert cli.main() == 2


def test_scripts_without_arguments_still_get_a_usage_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cli.sys, "argv", ["audio8d"])
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: False, raising=False)

    with pytest.raises(SystemExit) as exit_info:
        cli.main()
    assert exit_info.value.code == 2


def test_preset_supplies_every_value() -> None:
    args = cli.create_parser().parse_args(["in.mp3", "--preset", "studio"])

    assert cli.resolve_config(args) == PRESETS["studio"].config


def test_typed_knobs_override_the_preset() -> None:
    args = cli.create_parser().parse_args(
        ["in.mp3", "--preset", "studio", "--intensity", "0.6", "--loudness", "off"]
    )
    config = cli.resolve_config(args)

    assert config.intensity == 0.6
    assert config.loudness_target is None
    assert config.mp3_quality == PRESETS["studio"].config.mp3_quality


def test_loudness_accepts_numbers_and_rejects_words() -> None:
    parser = cli.create_parser()
    args = parser.parse_args(["a.mp3", "--loudness", "-16"])

    assert cli.resolve_config(args).loudness_target == -16
    with pytest.raises(SystemExit):
        parser.parse_args(["a.mp3", "--loudness", "loud"])


def test_unknown_preset_is_a_usage_error() -> None:
    with pytest.raises(SystemExit):
        cli.create_parser().parse_args(["a.mp3", "--preset", "banana"])


def test_list_presets_prints_every_style_without_a_song(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["--list-presets"])

    assert exit_info.value.code == 0
    shown = capsys.readouterr().out
    for name in PRESETS:
        assert name in shown
    assert "Gehan Fernando" in shown


def test_version_names_the_author(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        cli.main(["--version"])

    assert "Gehan Fernando" in capsys.readouterr().out


def test_settings_panel_and_tip_are_shown(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "convert", lambda **_: None)

    assert cli.main(["song.wav"]) == 0
    shown = capsys.readouterr().err
    assert "8 s per full circle" in shown
    assert "classic" in shown
    assert "Conversion completed" in shown
    assert "--preset studio" in shown


def test_tip_is_hidden_once_a_preset_is_chosen(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "convert", lambda **_: None)

    cli.main(["song.wav", "--preset", "smooth"])
    assert "Tip:" not in capsys.readouterr().err


def test_typing_mistakes_get_a_plain_fix_and_an_example(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["song.mp3", "--quality", "11"])

    assert exit_info.value.code == 2
    shown = capsys.readouterr().err
    assert "invalid choice" in shown
    assert "What to do:" in shown
    assert "Example:" in shown


def test_errors_during_conversion_get_a_plain_fix(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def refuse(**_: object) -> None:
        """Fail the way an already-existing output would."""
        raise InputValidationError(
            "Output already exists: x.mp3. Use --overwrite to replace it."
        )

    monkeypatch.setattr(cli, "convert", refuse)

    assert cli.main(["song.mp3"]) == 1
    assert "What to do: add --overwrite" in capsys.readouterr().err


def test_help_shows_the_best_values(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        cli.main(["--help"])

    shown = capsys.readouterr().out
    assert "QUICK START" in shown
    assert "BEST VALUES" in shown
    assert "--quality 0" in shown
    assert "Gehan Fernando" in shown


def test_missing_song_is_explained_before_the_settings_panel(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr(cli, "resolve_input", _REAL_RESOLVE_INPUT)
    monkeypatch.setattr(cli, "convert", lambda **_: pytest.fail("should not convert"))

    assert cli.main([str(tmp_path / "My Sonng.mp3")]) == 1
    shown = capsys.readouterr().err
    assert "Input file does not exist" in caplog.text
    assert "What to do:" in shown
    assert "Spin" not in shown


def test_bitrate_and_exact_loudness_can_be_typed() -> None:
    args = cli.create_parser().parse_args(
        ["a.mp3", "--bitrate", "320", "--exact-loudness"]
    )
    config = cli.resolve_config(args)

    assert config.mp3_bitrate == 320
    assert config.exact_loudness is True


def test_unknown_bitrate_is_a_usage_error() -> None:
    with pytest.raises(SystemExit):
        cli.create_parser().parse_args(["a.mp3", "--bitrate", "999"])
