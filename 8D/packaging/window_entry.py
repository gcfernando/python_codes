# Developed by Gehan Fernando
"""Audio8D.exe: opens the window; songs dropped on the exe arrive as arguments."""

import sys

from audio8d.cli import main

if __name__ == "__main__":
    sys.exit(main(["--gui", *sys.argv[1:]]))
