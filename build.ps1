param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

if ($Clean) {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build, dist, ytdlp-gui.spec
}

pyinstaller --onefile --windowed --name ytdlp-gui src/app.py
