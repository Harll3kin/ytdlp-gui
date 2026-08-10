import gzip
import os
import subprocess

import downloader

PASTA = os.path.join("C:" + os.sep, "Downloads")


def _saida(nome: str) -> str:
    return os.path.join(PASTA, f"{nome}.%(ext)s")


def test_build_args_mp3():
    args = downloader.build_args(
        url="https://youtu.be/abc",
        formato="mp3",
        qualidade="192",
        nome_arquivo="minha musica",
        pasta=PASTA,
    )

    assert args == [
        "yt-dlp",
        "-o", _saida("minha musica"),
        "-x", "--audio-format", "mp3", "--audio-quality", "192",
        "https://youtu.be/abc",
    ]


def test_build_args_mp4_com_limite_de_altura():
    args = downloader.build_args(
        url="https://youtu.be/abc",
        formato="mp4",
        qualidade="720p",
        nome_arquivo="meu video",
        pasta=PASTA,
    )

    assert args == [
        "yt-dlp",
        "-o", _saida("meu video"),
        "-f", downloader.mp4_format_selector("720p"),
        "--merge-output-format", "mp4",
        "https://youtu.be/abc",
    ]


def test_build_args_mp4_melhor_qualidade():
    args = downloader.build_args(
        url="https://youtu.be/abc",
        formato="mp4",
        qualidade="Best",
        nome_arquivo="meu video",
        pasta=PASTA,
    )

    assert args == [
        "yt-dlp",
        "-o", _saida("meu video"),
        "-f", downloader.mp4_format_selector("Best"),
        "--merge-output-format", "mp4",
        "https://youtu.be/abc",
    ]


def test_build_args_nao_pede_atualizacao_durante_o_download():
    # Updating is done once at startup, not coupled to every download.
    args = downloader.build_args(
        url="https://youtu.be/abc",
        formato="mp3",
        qualidade="192",
        nome_arquivo="x",
        pasta=PASTA,
    )

    assert "-U" not in args


def test_build_args_formato_invalido_levanta_erro():
    try:
        downloader.build_args(
            url="https://youtu.be/abc",
            formato="avi",
            qualidade="Best",
            nome_arquivo="x",
            pasta=PASTA,
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
        pasta=PASTA,
    )

    assert args[2] == _saida('Song Name_ _Official_ Video_')


def test_mp4_selector_prefere_h264_antes_de_qualquer_fallback():
    # Premiere Pro cannot decode av01/vp9, so avc1 must be tried first.
    selector = downloader.mp4_format_selector("Best")

    assert selector.startswith("bestvideo[vcodec^=avc1]")
    assert "av01" not in selector


def test_mp4_selector_aplica_limite_de_altura_em_todas_as_alternativas():
    selector = downloader.mp4_format_selector("720p")

    assert selector.count("[height<=720]") == len(selector.split("/"))


def test_no_window_kwargs_vazio_fora_do_windows(monkeypatch):
    # subprocess.CREATE_NO_WINDOW does not exist on macOS/Linux.
    monkeypatch.setattr(downloader, "IS_WINDOWS", False)

    assert downloader._no_window_kwargs() == {}


def test_no_window_kwargs_esconde_console_no_windows(monkeypatch):
    monkeypatch.setattr(downloader, "IS_WINDOWS", True)
    monkeypatch.setattr(subprocess, "CREATE_NO_WINDOW", 0x08000000, raising=False)

    assert downloader._no_window_kwargs() == {"creationflags": 0x08000000}


def test_bundled_path_ignora_execucao_fora_do_app(monkeypatch):
    monkeypatch.setattr(downloader.sys, "frozen", False, raising=False)

    assert downloader._bundled_path("ffmpeg.exe", "ffmpeg") is None


def test_bundled_path_encontra_binario_ao_lado_do_executavel(monkeypatch, tmp_path):
    # Layout produced by the Windows installer: the binaries sit next to
    # ytdlp-gui.exe in the install directory.
    exe = tmp_path / "ytdlp-gui.exe"
    exe.write_bytes(b"")
    vizinho = tmp_path / "ffmpeg.exe"
    vizinho.write_bytes(b"")

    monkeypatch.setattr(downloader.sys, "frozen", True, raising=False)
    monkeypatch.setattr(downloader.sys, "executable", str(exe))
    monkeypatch.delattr(downloader.sys, "_MEIPASS", raising=False)

    assert downloader._bundled_path("ffmpeg.exe", "ffmpeg") == str(vizinho)


def test_bundled_path_prefere_meipass(monkeypatch, tmp_path):
    # Layout produced by PyInstaller inside the macOS .app, where the payload
    # directory is not the one holding the executable.
    meipass = tmp_path / "Frameworks"
    meipass.mkdir()
    (meipass / "ffmpeg").write_bytes(b"")
    exe_dir = tmp_path / "MacOS"
    exe_dir.mkdir()
    (exe_dir / "ffmpeg").write_bytes(b"")

    monkeypatch.setattr(downloader.sys, "frozen", True, raising=False)
    monkeypatch.setattr(downloader.sys, "_MEIPASS", str(meipass), raising=False)
    monkeypatch.setattr(downloader.sys, "executable", str(exe_dir / "ytdlp-gui"))

    assert downloader._bundled_path("ffmpeg.exe", "ffmpeg") == str(meipass / "ffmpeg")


def test_resolve_ytdlp_usa_o_path_quando_nada_esta_embutido(monkeypatch):
    monkeypatch.setattr(downloader, "BUNDLED_YTDLP_GZ", None)
    monkeypatch.setattr(downloader, "BUNDLED_YTDLP", None)

    assert downloader._resolve_ytdlp() == "yt-dlp"


def test_resolve_ytdlp_extrai_gz_preservando_os_bytes(monkeypatch, tmp_path):
    # The extracted file must be byte-identical: yt-dlp carries its own code
    # signature, and any change makes macOS refuse to run it on arm64.
    conteudo = b"\xcf\xfa\xed\xfe payload with trailing archive\x00\x01\x02"
    origem = tmp_path / "yt-dlp.gz"
    with gzip.open(origem, "wb") as f:
        f.write(conteudo)

    destino = tmp_path / "bin"
    destino.mkdir()

    monkeypatch.setattr(downloader, "BUNDLED_YTDLP_GZ", str(origem))
    monkeypatch.setattr(downloader, "BUNDLED_YTDLP", None)
    monkeypatch.setattr(downloader.paths, "bin_dir", lambda: str(destino))

    caminho = downloader._resolve_ytdlp()

    with open(caminho, "rb") as f:
        assert f.read() == conteudo
    assert not os.path.exists(caminho + ".part")


def test_resolve_ytdlp_nao_reextrai_por_cima_de_uma_atualizacao(monkeypatch, tmp_path):
    # 'yt-dlp -U' rewrites this copy; re-extracting would undo every update.
    origem = tmp_path / "yt-dlp.gz"
    with gzip.open(origem, "wb") as f:
        f.write(b"versao embutida")

    destino = tmp_path / "bin"
    destino.mkdir()
    ja_atualizado = destino / ("yt-dlp.exe" if downloader.IS_WINDOWS else "yt-dlp")
    ja_atualizado.write_bytes(b"versao mais nova")

    monkeypatch.setattr(downloader, "BUNDLED_YTDLP_GZ", str(origem))
    monkeypatch.setattr(downloader, "BUNDLED_YTDLP", None)
    monkeypatch.setattr(downloader.paths, "bin_dir", lambda: str(destino))

    downloader._resolve_ytdlp()

    assert ja_atualizado.read_bytes() == b"versao mais nova"


def test_fetch_title_returns_stripped_stdout(monkeypatch):
    class FakeResult:
        returncode = 0
        stdout = "Título do vídeo\n"
        stderr = ""

    def fake_run(cmd, **kwargs):
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

    def fake_run(cmd, **kwargs):
        return FakeResult()

    monkeypatch.setattr(subprocess, "run", fake_run)

    try:
        downloader.fetch_title("https://youtu.be/abc")
        assert False, "esperava RuntimeError"
    except RuntimeError as exc:
        assert "indisponível" in str(exc)


def test_update_ytdlp_reporta_falha_sem_levantar(monkeypatch):
    def fake_run(cmd, **kwargs):
        raise FileNotFoundError()

    monkeypatch.setattr(subprocess, "run", fake_run)

    ok, mensagem = downloader.update_ytdlp()

    assert ok is False
    assert "not found" in mensagem


def test_update_ytdlp_sobrevive_a_timeout(monkeypatch):
    def fake_run(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd="yt-dlp", timeout=180)

    monkeypatch.setattr(subprocess, "run", fake_run)

    ok, mensagem = downloader.update_ytdlp()

    assert ok is False
    assert "timed out" in mensagem


def test_run_download_streams_output_and_reports_returncode(monkeypatch):
    class FakeProcess:
        stdout = iter(["linha 1\n", "linha 2\n"])
        returncode = 0

        def wait(self):
            return None

    def fake_popen(args, **kwargs):
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
