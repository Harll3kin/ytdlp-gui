import subprocess

import downloader


def test_build_args_mp3():
    args = downloader.build_args(
        url="https://youtu.be/abc",
        formato="mp3",
        qualidade="192",
        nome_arquivo="minha musica",
        pasta="C:\\Downloads",
    )

    assert args == [
        "yt-dlp",
        "-o", "C:\\Downloads\\minha musica.%(ext)s",
        "-x", "--audio-format", "mp3", "--audio-quality", "192",
        "https://youtu.be/abc",
    ]


def test_build_args_mp4_com_limite_de_altura():
    args = downloader.build_args(
        url="https://youtu.be/abc",
        formato="mp4",
        qualidade="720p",
        nome_arquivo="meu video",
        pasta="C:\\Downloads",
    )

    assert args == [
        "yt-dlp",
        "-o", "C:\\Downloads\\meu video.%(ext)s",
        "-f", "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "--merge-output-format", "mp4",
        "https://youtu.be/abc",
    ]


def test_build_args_mp4_melhor_qualidade():
    args = downloader.build_args(
        url="https://youtu.be/abc",
        formato="mp4",
        qualidade="Best",
        nome_arquivo="meu video",
        pasta="C:\\Downloads",
    )

    assert args == [
        "yt-dlp",
        "-o", "C:\\Downloads\\meu video.%(ext)s",
        "-f", "bestvideo+bestaudio/best",
        "--merge-output-format", "mp4",
        "https://youtu.be/abc",
    ]


def test_build_args_formato_invalido_levanta_erro():
    try:
        downloader.build_args(
            url="https://youtu.be/abc",
            formato="avi",
            qualidade="Best",
            nome_arquivo="x",
            pasta="C:\\Downloads",
        )
        assert False, "esperava ValueError"
    except ValueError:
        pass


def test_build_args_sanitiza_nome_arquivo_com_caracteres_invalidos():
    args = downloader.build_args(
        url="https://youtu.be/abc",
        formato="mp3",
        qualidade="192",
        nome_arquivo='Song Name: "Official" Video?',
        pasta="C:\\Downloads",
    )

    assert args[2] == 'C:\\Downloads\\Song Name_ _Official_ Video_.%(ext)s'


def test_fetch_title_returns_stripped_stdout(monkeypatch):
    class FakeResult:
        returncode = 0
        stdout = "Título do vídeo\n"
        stderr = ""

    def fake_run(cmd, capture_output, text, encoding, errors, creationflags):
        assert cmd == ["yt-dlp", "--get-title", "https://youtu.be/abc"]
        return FakeResult()

    monkeypatch.setattr(subprocess, "run", fake_run)

    titulo = downloader.fetch_title("https://youtu.be/abc")

    assert titulo == "Título do vídeo"


def test_fetch_title_raises_on_failure(monkeypatch):
    class FakeResult:
        returncode = 1
        stdout = ""
        stderr = "erro: vídeo indisponível"

    def fake_run(cmd, capture_output, text, encoding, errors, creationflags):
        return FakeResult()

    monkeypatch.setattr(subprocess, "run", fake_run)

    try:
        downloader.fetch_title("https://youtu.be/abc")
        assert False, "esperava RuntimeError"
    except RuntimeError as exc:
        assert "indisponível" in str(exc)


def test_run_download_streams_output_and_reports_returncode(monkeypatch):
    class FakeProcess:
        stdout = iter(["linha 1\n", "linha 2\n"])
        returncode = 0

        def wait(self):
            return None

    def fake_popen(args, stdout, stderr, text, bufsize, encoding, errors, creationflags):
        return FakeProcess()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    linhas = []
    codigos = []

    downloader.run_download(["yt-dlp"], on_output=linhas.append, on_done=codigos.append)

    assert linhas == ["linha 1", "linha 2"]
    assert codigos == [0]


def test_parse_progress_extracts_percentage_as_fraction():
    linha = "[download]  45.2% of   10.00MiB at    1.21MiB/s ETA 00:04"
    assert downloader.parse_progress(linha) == 0.452


def test_parse_progress_handles_whole_number_percentage():
    linha = "[download] 100% of   10.00MiB in 00:00:08"
    assert downloader.parse_progress(linha) == 1.0


def test_parse_progress_returns_none_for_non_progress_line():
    linha = "[ExtractAudio] Destination: song.mp3"
    assert downloader.parse_progress(linha) is None


def test_parse_progress_returns_none_for_empty_line():
    assert downloader.parse_progress("") is None
