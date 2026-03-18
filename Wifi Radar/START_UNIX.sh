#!/bin/bash
# ============================================
#  WiFi Military Radar  --  macOS/Linux Launcher
# ============================================

clear
echo ""
echo "  ============================================"
echo "   WiFi MILITARY RADAR  --  Unix Launcher"
echo "  ============================================"
echo ""

OS_TYPE="$(uname -s)"

# ── Check Python 3 ────────────────────────────────────────────────
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    VER=$(python --version 2>&1 | grep -o 'Python 3')
    if [ "$VER" = "Python 3" ]; then
        PYTHON=python
    else
        echo "  [ERROR] Python 3 is required."
        echo "          macOS:  brew install python3"
        echo "          Linux:  sudo apt install python3 python3-pip"
        exit 1
    fi
else
    echo "  [ERROR] Python 3 not found."
    exit 1
fi

echo "  [OK] Python found: $($PYTHON --version)"
echo ""

# ── Install dependencies ───────────────────────────────────────────
echo "  [SETUP] Installing/checking dependencies..."
$PYTHON -m pip install flask flask-cors --quiet --disable-pip-version-check 2>/dev/null || \
$PYTHON -m pip install flask flask-cors --quiet --break-system-packages 2>/dev/null
echo "  [OK] Dependencies ready"
echo ""

# ── Linux: warn about sudo ─────────────────────────────────────────
if [ "$OS_TYPE" = "Linux" ]; then
    if [ "$EUID" -ne 0 ]; then
        echo "  [WARN] Not running as root. For best scan results:"
        echo "         sudo bash START_UNIX.sh"
        echo ""
    fi
fi

# ── macOS: check airport tool ─────────────────────────────────────
if [ "$OS_TYPE" = "Darwin" ]; then
    AIRPORT="/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
    if [ ! -f "$AIRPORT" ]; then
        echo "  [WARN] airport utility not found (removed in macOS Ventura+)."
        echo "         Falling back to system_profiler scan."
        echo ""
    else
        echo "  [OK] airport utility found"
        echo ""
    fi
fi

echo "  [START] Launching radar server..."
echo ""
echo "  Open your browser:  http://localhost:5000"
echo "  Debug info:         http://localhost:5000/api/debug"
echo ""
echo "  Press Ctrl+C to stop."
echo "  ============================================"
echo ""

# ── Open browser after short delay ────────────────────────────────
(
  sleep 2
  if [ "$OS_TYPE" = "Darwin" ]; then
    open "http://localhost:5000"
  elif command -v xdg-open &>/dev/null; then
    xdg-open "http://localhost:5000" 2>/dev/null
  fi
) &

# ── Run server ────────────────────────────────────────────────────
$PYTHON server.py
