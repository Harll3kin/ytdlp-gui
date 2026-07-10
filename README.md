# yt-dlp GUI

A simple Windows app for downloading YouTube videos as MP3 or MP4 — just
paste a link, no command line required.

## Download

Grab the latest installer from the [Releases](../../releases) page. It
bundles `yt-dlp` and `ffmpeg`, so there's nothing else to install.

> **Note:** the installer isn't code-signed, so Windows SmartScreen may show
> a warning on first run. Click **More info → Run anyway** to continue.

## Development

### Requirements

- Python 3.10+

### Setup

```
pip install -r requirements.txt
python src/app.py
```

### Running tests

```
pytest
```

### Building the .exe

```
./build.ps1
```

Produces `dist/ytdlp-gui.exe`. Use `./build.ps1 -Clean` to wipe previous
build artifacts first.

### Building the installer

The installer script (`installer/ytdlp-gui.iss`) is built with
[Inno Setup](https://jrsoftware.org/isinfo.php) and expects:

- `dist/ytdlp-gui.exe` (from `build.ps1`)
- `bin/yt-dlp.exe` and `bin/ffmpeg.exe` (place your own copies here — not
  tracked in git)

Open `installer/ytdlp-gui.iss` in Inno Setup and compile, or run:

```
iscc installer/ytdlp-gui.iss
```

## Credits

Built on top of [yt-dlp](https://github.com/yt-dlp/yt-dlp) and
[FFmpeg](https://ffmpeg.org/).

## License

MIT — see [LICENSE](LICENSE).

Use responsibly and respect the copyright/terms of service of the platforms
you download from.
