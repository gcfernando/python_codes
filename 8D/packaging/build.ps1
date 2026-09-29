# Developed by ::> Gehan Fernando

# Builds Audio8D.exe and audio8d-cli.exe into bin, beside ffmpeg (-Zip also makes a release zip)
param([switch]$Zip)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$bin = Join-Path $root "bin"
$work = Join-Path $root "build"
$venv = Join-Path $work "venv"
$python = Join-Path $venv "Scripts\python.exe"

# The programs need the bundled tools beside them, so stop early if they are missing
foreach ($tool in "ffmpeg.exe", "ffprobe.exe") {
    if (-not (Test-Path (Join-Path $bin $tool))) {
        throw "Missing $bin\$tool. Put the FFmpeg 'essentials' build there first."
    }
}

# A private build environment keeps the programs small and the build repeatable
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
$made = Join-Path $work "made"
& $python -m PyInstaller --noconfirm --clean `
    --distpath $made `
    --workpath (Join-Path $work "work") `
    (Join-Path $root "packaging\audio8d.spec")
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed; see the messages above." }

# The new programs replace the old ones in bin; ffmpeg and ffprobe stay where they are
foreach ($old in "Audio8D.exe", "audio8d-cli.exe", "_internal") {
    $path = Join-Path $bin $old
    if (Test-Path $path) { Remove-Item $path -Recurse -Force }
}
Copy-Item (Join-Path $made "Audio8D\*") $bin -Recurse -Force

# A quick self-test of the finished programs
$built = & (Join-Path $bin "audio8d-cli.exe") --version
if ($LASTEXITCODE -ne 0) { throw "The built audio8d-cli.exe did not start." }
Write-Host "Built: $built"
Write-Host "Done:  $bin"

if ($Zip) {
    # The release has the project's own layout: bin, the guide, and the licences
    $version = (Select-String -Path (Join-Path $root "pyproject.toml") -Pattern '^version = "(.+)"').Matches[0].Groups[1].Value
    $stage = Join-Path $work "release\Audio8D"
    if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
    New-Item -ItemType Directory -Force $stage | Out-Null
    Copy-Item $bin (Join-Path $stage "bin") -Recurse
    Copy-Item (Join-Path $root "licenses") (Join-Path $stage "licenses") -Recurse
    # FFmpeg is GPL: its licence and the other notices must travel with every copy
    Copy-Item (Join-Path $root "THIRD-PARTY-NOTICES.md"), (Join-Path $root "README.md") $stage
    $archive = Join-Path $work "Audio8D-$version-windows.zip"
    if (Test-Path $archive) { Remove-Item $archive }
    Compress-Archive -Path $stage -DestinationPath $archive
    Write-Host "Zip:   $archive"
}
