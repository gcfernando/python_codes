# Developed by Gehan Fernando
"""Your own styles, saved in a small TOML file and used like the built-in ones."""

import dataclasses
import os
import re
from pathlib import Path
from typing import Any

from .errors import InputValidationError
from .locations import presets_file
from .parsing import format_keyframes, parse_keyframes
from .presets import PRESETS, Preset
from .settings import EffectConfig

_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{0,23}$")
_FIELDS = {field.name: field for field in dataclasses.fields(EffectConfig)}
# Settings that may be switched off with the word "off" instead of a number
_OPTIONAL = {"loudness_target", "bitrate", "bpm"}
_CURVES = {"speed_curve", "intensity_curve"}
_HEADER = (
    "# Audio8D custom styles. Save new ones with --save-preset NAME.\n"
    "# Any setting left out comes from the style named in based_on.\n"
)

Table = dict[str, dict[str, Any]]


def _parse_value(text: str, line_number: int) -> Any:
    """One TOML value: a "string", true/false, or a number."""
    if text.startswith('"'):
        if len(text) < 2 or not text.endswith('"'):
            raise InputValidationError(f"presets.toml line {line_number}: missing '\"'")
        return text[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if text in {"true", "false"}:
        return text == "true"
    try:
        return int(text) if re.fullmatch(r"[+-]?\d+", text) else float(text)
    except ValueError:
        raise InputValidationError(
            f"presets.toml line {line_number}: '{text}' is not a value"
        ) from None


def _strip_comment(line: str) -> str:
    """Drop a trailing # comment, leaving any # inside a "string" alone."""
    in_string = False
    for index, char in enumerate(line):
        if char == '"' and (index == 0 or line[index - 1] != "\\"):
            in_string = not in_string
        elif char == "#" and not in_string:
            return line[:index]
    return line


def parse_toml(text: str) -> Table:
    """The small part of TOML this file needs: [tables] of key = value lines."""
    tables: Table = {}
    current: dict[str, Any] | None = None
    for number, raw in enumerate(text.splitlines(), start=1):
        line = _strip_comment(raw).strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            name = line[1:-1].strip().strip('"')
            current = tables.setdefault(name, {})
            continue
        key, equals, value = line.partition("=")
        if not equals or current is None:
            raise InputValidationError(
                f"presets.toml line {number}: expected [name] or key = value"
            )
        current[key.strip()] = _parse_value(value.strip(), number)
    return tables


def _format_value(value: Any) -> str:
    """The reverse of _parse_value."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return f"{value:g}" if isinstance(value, float) else str(value)
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def dump_toml(tables: Table) -> str:
    """Write tables back out, one [name] block per style."""
    blocks = []
    for name, values in tables.items():
        lines = [f"[{name}]"]
        lines += [f"{key} = {_format_value(value)}" for key, value in values.items()]
        blocks.append("\n".join(lines))
    return _HEADER + "\n" + "\n\n".join(blocks) + "\n"


def _config_from(name: str, values: dict[str, Any]) -> EffectConfig:
    """Build a style's settings on top of the style it is based on."""
    base_name = str(values.get("based_on", "classic"))
    if base_name not in PRESETS:
        raise InputValidationError(
            f"style '{name}' is based on '{base_name}', which does not exist"
        )
    overrides: dict[str, Any] = {}
    for key, value in values.items():
        if key in {"based_on", "summary"}:
            continue
        if key not in _FIELDS:
            raise InputValidationError(f"style '{name}' has an unknown setting '{key}'")
        if key in _OPTIONAL and value == "off":
            overrides[key] = None
        elif key in _CURVES:
            overrides[key] = parse_keyframes(str(value)) if value else ()
        else:
            overrides[key] = value
    try:
        config = dataclasses.replace(PRESETS[base_name].config, **overrides)
    except TypeError as exc:
        raise InputValidationError(f"style '{name}': {exc}") from exc
    config.validate()
    return config


def load_user_presets(path: Path | None = None) -> dict[str, Preset]:
    """Every saved style, or none if the file does not exist yet."""
    file = path or presets_file()
    try:
        text = file.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    except OSError as exc:
        raise InputValidationError(f"Cannot read your styles file {file}") from exc
    presets = {}
    for name, values in parse_toml(text).items():
        if name in PRESETS:
            continue
        presets[name] = Preset(
            name=name,
            summary=str(values.get("summary", "your own style")),
            config=_config_from(name, values),
            custom=True,
        )
    return presets


def all_presets(path: Path | None = None) -> dict[str, Preset]:
    """Built-in styles first, then your own."""
    return {**PRESETS, **load_user_presets(path)}


def _differences(config: EffectConfig, base: EffectConfig) -> dict[str, Any]:
    """Only the settings that differ from the base style, ready for TOML."""
    changed: dict[str, Any] = {}
    for key in _FIELDS:
        value = getattr(config, key)
        if value == getattr(base, key):
            continue
        if value is None:
            changed[key] = "off"
        elif key in _CURVES:
            changed[key] = format_keyframes(value)
        else:
            changed[key] = value
    return changed


def _read_styles(file: Path) -> dict[str, dict[str, Any]]:
    """The styles file's tables, or none yet; a read problem is explained."""
    try:
        return parse_toml(file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except OSError as exc:
        raise InputValidationError(f"Cannot read your styles file {file}") from exc


def _write_styles(file: Path, tables: dict[str, dict[str, Any]]) -> None:
    """Save the styles file whole: written aside, then swapped in one step."""
    # A crash half-way must never cost every saved style
    partial = file.with_name(f"{file.name}.tmp")
    try:
        file.parent.mkdir(parents=True, exist_ok=True)
        partial.write_text(dump_toml(tables), encoding="utf-8")
        os.replace(partial, file)
    except OSError as exc:
        partial.unlink(missing_ok=True)
        raise InputValidationError(f"Cannot save your styles file {file}") from exc


def save_user_preset(
    name: str,
    config: EffectConfig,
    *,
    based_on: str = "classic",
    summary: str = "",
    path: Path | None = None,
) -> Path:
    """Add or update one style in the styles file and return where it was saved."""
    if not _NAME.match(name):
        raise InputValidationError(
            "style names use a-z, 0-9, - and _ only (up to 24 characters)"
        )
    if name in PRESETS:
        raise InputValidationError(f"'{name}' is a built-in style; pick another name")
    base = based_on if based_on in PRESETS else "classic"
    config.validate()

    file = path or presets_file()
    tables = _read_styles(file)
    values: dict[str, Any] = {"based_on": base}
    if summary:
        values["summary"] = summary
    values.update(_differences(config, PRESETS[base].config))
    tables[name] = values
    _write_styles(file, tables)
    return file


def delete_user_preset(name: str, *, path: Path | None = None) -> bool:
    """Remove one saved style; True if it was there."""
    file = path or presets_file()
    tables = _read_styles(file)
    if name not in tables:
        return False
    del tables[name]
    _write_styles(file, tables)
    return True
