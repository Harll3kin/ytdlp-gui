param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$YtDlpVersion = "2026.07.04"
$YtDlpUrl = "https://github.com/yt-dlp/yt-dlp/releases/download/$YtDlpVersion/yt-dlp.exe"
# Maintained by the yt-dlp project for exactly this purpose.
$FfmpegUrl = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

if ($Clean) {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build, dist, ytdlp-gui.spec, bin
}

New-Item -ItemType Directory -Force -Path bin | Out-Null

if (-not (Test-Path bin\yt-dlp.exe)) {
    Write-Host "Downloading yt-dlp.exe..."
    Invoke-WebRequest -Uri $YtDlpUrl -OutFile bin\yt-dlp.exe
}

if (-not ((Test-Path bin\ffmpeg.exe) -and (Test-Path bin\ffprobe.exe))) {
    Write-Host "Downloading ffmpeg..."
    $zip = Join-Path $env:TEMP "ffmpeg-win64.zip"
    $extracted = Join-Path $env:TEMP "ffmpeg-win64"
    Invoke-WebRequest -Uri $FfmpegUrl -OutFile $zip
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $extracted
    Expand-Archive -Path $zip -DestinationPath $extracted
    Get-ChildItem -Path $extracted -Recurse -Include ffmpeg.exe, ffprobe.exe |
        ForEach-Object { Copy-Item $_.FullName -Destination bin\ -Force }
}

pyinstaller --noconfirm --onefile --windowed --name ytdlp-gui --collect-all customtkinter src/app.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

Write-Host ""
Write-Host "Build complete."
Write-Host "  dist\ytdlp-gui.exe  (needs the binaries in bin\ beside it)"
Write-Host "  bin\yt-dlp.exe, bin\ffmpeg.exe, bin\ffprobe.exe"
Write-Host ""
Write-Host "To produce the installer: ISCC installer\ytdlp-gui.iss"
