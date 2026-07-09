import os
import subprocess

YTDLP_EXECUTABLE = "yt-dlp"

MP4_HEIGHT_LIMITS = {
    "Melhor": None,
    "1080p": 1080,
    "720p": 720,
    "480p": 480,
}

ILLEGAL_FILENAME_CHARS = '\\/:*?"<>|'


def sanitize_filename(nome: str) -> str:
    return "".join("_" if c in ILLEGAL_FILENAME_CHARS else c for c in nome)


def build_args(url: str, formato: str, qualidade: str, nome_arquivo: str, pasta: str) -> list[str]:
    output_template = os.path.join(pasta, f"{sanitize_filename(nome_arquivo)}.%(ext)s")
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


def fetch_title(url: str) -> str:
    result = subprocess.run(
        [YTDLP_EXECUTABLE, "--get-title", url],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Falha ao buscar o título do vídeo.")
    return result.stdout.strip()


def run_download(args, on_output, on_done):
    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace",
    )
    for line in process.stdout:
        on_output(line.rstrip("\n"))
    process.wait()
    on_done(process.returncode)
