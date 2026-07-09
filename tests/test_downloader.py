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
        qualidade="Melhor",
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
            qualidade="Melhor",
            nome_arquivo="x",
            pasta="C:\\Downloads",
        )
        assert False, "esperava ValueError"
    except ValueError:
        pass
