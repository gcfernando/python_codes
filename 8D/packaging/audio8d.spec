# Developed by Gehan Fernando

# Two programs (window and terminal) sharing one _internal folder; run via build.ps1

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

ROOT = Path(SPECPATH).parent
ICON = str(ROOT / "src" / "assets" / "audio8d.ico")
# CustomTkinter's themes and fonts, and Audio8D's own icon
DATAS = collect_data_files("customtkinter") + [(ICON, "audio8d/assets")]
# Big optional extras that Audio8D never needs in the standalone build
EXCLUDES = ["demucs", "torch", "torchaudio", "numpy", "pytest", "IPython"]


def analysis(script):
    return Analysis(
        [str(ROOT / "packaging" / script)],
        pathex=[str(ROOT)],
        datas=DATAS,
        hiddenimports=["audio8d.gui_app"],
        excludes=EXCLUDES,
        noarchive=False,
    )


window = analysis("window_entry.py")
terminal = analysis("terminal_entry.py")


def program(built, name, console):
    return EXE(
        PYZ(built.pure),
        built.scripts,
        [],
        exclude_binaries=True,
        name=name,
        icon=ICON,
        console=console,
        upx=False,
        version=str(ROOT / "packaging" / "version.txt"),
    )


COLLECT(
    program(window, "Audio8D", console=False),
    window.binaries,
    window.datas,
    program(terminal, "audio8d-cli", console=True),
    terminal.binaries,
    terminal.datas,
    upx=False,
    name="Audio8D",
)
