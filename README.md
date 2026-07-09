# yt-dlp GUI

Programa Windows para baixar vídeos do YouTube em MP3 ou MP4 colando um link,
sem precisar abrir o PowerShell.

## Pré-requisitos

- `yt-dlp` e `ffmpeg` disponíveis no PATH do sistema.

## Rodando em desenvolvimento

```
pip install -r requirements.txt
python src/app.py
```

## Rodando os testes

```
pytest
```

## Gerando o .exe

```
./build.ps1
```

Gera `dist/ytdlp-gui.exe`. Use `./build.ps1 -Clean` para limpar builds
anteriores antes de gerar um novo.
