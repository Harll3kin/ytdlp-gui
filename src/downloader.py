import os

YTDLP_EXECUTABLE = "yt-dlp"

MP4_HEIGHT_LIMITS = {
    "Melhor": None,
    "1080p": 1080,
    "720p": 720,
    "480p": 480,
}


def build_args(url: str, formato: str, qualidade: str, nome_arquivo: str, pasta: str) -> list[str]:
    output_template = os.path.join(pasta, f"{nome_arquivo}.%(ext)s")
    args = [YTDLP_EXECUTABLE, "-o", output_template]

    if formato == "mp3":
        args += ["-x", "--audio-format", "mp3", "--audio-quality", qualidade]
    elif formato == "mp4":
        height = MP4_HEIGHT_LIMITS.get(qualidade)
        if height is None:
            args += ["-f", "bestvideo+bestaudio/best"]
        else:
            args += ["-f", f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"]
        args += ["--merge-output-format", "mp4"]
    else:
        raise ValueError(f"Formato desconhecido: {formato}")

    args.append(url)
    return args
