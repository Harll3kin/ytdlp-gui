#!/usr/bin/env python3
"""End-to-end check: download through the app's own argument builder.

Point this at the binaries that ship with the app so the --ffmpeg-location
handoff is exercised exactly the way it happens for a real user.

Environment:
  SMOKE_YTDLP    path to the yt-dlp executable
  SMOKE_FFMPEG   path to the ffmpeg executable
  SMOKE_FFPROBE  path to the ffprobe executable
  SMOKE_OUT      directory to download into
  SMOKE_URL      optional, defaults to a short public video
"""

import os
import subprocess
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)

import downloader  # noqa: E402

URL = os.environ.get("SMOKE_URL", "https://youtube.com/shorts/_SRORhIQ3uM")


def main() -> int:
    try:
        ytdlp = os.path.abspath(os.environ["SMOKE_YTDLP"])
        ffmpeg = os.path.abspath(os.environ["SMOKE_FFMPEG"])
        ffprobe = os.path.abspath(os.environ["SMOKE_FFPROBE"])
        out = os.path.abspath(os.environ["SMOKE_OUT"])
    except KeyError as exc:
        print(f"missing environment variable: {exc}")
        return 2

    os.makedirs(out, exist_ok=True)

    # Stand in for the frozen app, which resolves these to bundled binaries.
    downloader._ytdlp_executable = ytdlp
    downloader.FFMPEG_LOCATION = ffmpeg

    for formato, qualidade in (("mp4", "Best"), ("mp3", "192")):
        args = downloader.build_args(URL, formato, qualidade, f"smoke_{formato}", out)
        if "--ffmpeg-location" not in args:
            print("yt-dlp was not told where ffmpeg is")
            return 1

        codes: list[int] = []
        downloader.run_download(args, on_output=print, on_done=codes.append)
        if codes[0] != 0:
            print(f"{formato} download failed with exit code {codes[0]}")
            return 1

    mp4 = os.path.join(out, "smoke_mp4.mp4")
    mp3 = os.path.join(out, "smoke_mp3.mp3")
    for caminho in (mp4, mp3):
        if not os.path.exists(caminho):
            print(f"expected output missing: {caminho}")
            return 1

    codec = subprocess.run(
        [ffprobe, "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=codec_name", "-of", "csv=p=0", mp4],
        capture_output=True,
        text=True,
    ).stdout.strip()

    # av01 is precisely what Premiere Pro refuses to import.
    if codec != "h264":
        print(f"expected h264, got {codec!r}")
        return 1

    print("Smoke test passed: h264 video + mp3 audio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
