# Developed by Gehan Fernando

# Builds the standalone dist\Audio8D folder and its zip (usage: see README part 26)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $root "build\venv"
$python = Join-Path $venv "Scripts\python.exe"
$app = Join-Path $root "dist\Audio8D"
$tools = Join-Path $root "bin\executable"

# The exe needs the bundled tools, so stop early if they are missing
foreach ($tool in "ffmpeg.exe", "ffprobe.exe") {
    if (-not (Test-Path (Join-Path $tools $tool))) {
        throw "Missing $tools\$tool. Put the FFmpeg 'essentials' build there first."
    }
}

# A private build environment keeps the exe small and the build repeatable
if (-not (Test-Path $python)) {
    Write-Host "Creating the build environment in $venv"
    python -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw "Could not create $venv (is Python 3.10+ installed?)" }
}
& $python -m pip install --quiet --upgrade pip
& $python -m pip install --quiet "$root[gui]" "pyinstaller>=6.0"
# PyInstaller can't follow an editable install, so always copy in the current code
& $python -m pip install --quiet --no-deps --force-reinstall "$root"
if ($LASTEXITCODE -ne 0) { throw "Could not install the build tools." }

Write-Host "Building Audio8D.exe and audio8d-cli.exe"
& $python -m PyInstaller --noconfirm --clean `
    --distpath (Join-Path $root "dist") `
    --workpath (Join-Path $root "build\work") `
    (Join-Path $root "packaging\audio8d.spec")
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed; see the messages above." }

# Everything the app finds next to itself: tools and licences (the guide stays online, in the one 8D\README.md)
New-Item -ItemType Directory -Force (Join-Path $app "bin\executable") | Out-Null
Copy-Item (Join-Path $tools "*.exe") (Join-Path $app "bin\executable") -Force
# FFmpeg is GPL: its licence and the other notices must travel with every copy
Copy-Item (Join-Path $root "THIRD-PARTY-NOTICES.md") $app -Force
New-Item -ItemType Directory -Force (Join-Path $app "licenses") | Out-Null
Copy-Item (Join-Path $root "licenses\*.txt") (Join-Path $app "licenses") -Force

# A quick self-test of the finished build before it is zipped
$version = & (Join-Path $app "audio8d-cli.exe") --version
if ($LASTEXITCODE -ne 0) { throw "The built audio8d-cli.exe did not start." }
Write-Host "Built: $version"

$zip = Join-Path $root "dist\Audio8D-2.0.0-windows.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path $app -DestinationPath $zip
Write-Host "Done: $app"
Write-Host "Zip:  $zip"
