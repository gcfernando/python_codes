@echo off
title WiFi Military Radar
color 0A
cls
echo.
echo  ============================================
echo   WiFi MILITARY RADAR  --  Windows Launcher
echo  ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found!
    echo  Download from: https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo  [OK] Python found
echo.

:: Install dependencies silently
echo  [SETUP] Installing/checking dependencies...
python -m pip install flask flask-cors --quiet --disable-pip-version-check
echo  [OK] Dependencies ready
echo.

:: Check Wi-Fi adapter
echo  [INFO] Checking Wi-Fi adapter...
netsh wlan show interfaces | find "State" >nul 2>&1
if errorlevel 1 (
    echo  [WARN] Wi-Fi adapter may be off or unavailable.
    echo         Make sure Wi-Fi is enabled in Windows Settings.
    echo.
)

echo  [START] Launching radar server...
echo.
echo  Open your browser at:  http://localhost:5000
echo  Debug info at:         http://localhost:5000/api/debug
echo.
echo  Press Ctrl+C to stop.
echo  ============================================
echo.

:: Try to open browser after 2 seconds
start "" /min cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5000"

:: Run server
python server.py
if errorlevel 1 (
    echo.
    echo  [ERROR] Server failed. Try running as Administrator:
    echo  Right-click this file -> Run as administrator
    echo.
    pause
)
