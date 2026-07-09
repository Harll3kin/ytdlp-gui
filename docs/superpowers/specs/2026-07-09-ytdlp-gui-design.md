# yt-dlp GUI — Design

## Objetivo

Programa Windows (.exe) para baixar vídeos do YouTube em MP3 ou MP4 colando um
link, sem precisar abrir o PowerShell nem digitar comandos do yt-dlp.

## Requisitos funcionais

- Campo para colar o link do vídeo.
- Ao sair do campo de link (perder foco), o app busca o título do vídeo em
  segundo plano e preenche automaticamente o campo "Nome do arquivo". O
  usuário pode apagar e digitar outro nome antes de baixar.
- Escolha de formato: MP3 (áudio) ou MP4 (vídeo).
- Dropdown de qualidade, dependente do formato escolhido:
  - MP3: 320 / 192 / 128 kbps.
  - MP4: Melhor disponível / 1080p / 720p / 480p.
- Pasta de destino exibida na tela, com botão "Trocar pasta" (abre um
  seletor de pasta do Windows). O app lembra a última pasta usada entre
  execuções (persistida em `config.json` ao lado do `.exe`). Na primeira
  execução, a pasta padrão é `%USERPROFILE%\Videos\EDIT\ASSETS\SFX`.
- Botão "Baixar" que dispara o download numa thread separada (a janela não
  pode travar durante o download).
- Caixa de log/texto mostrando o progresso do yt-dlp em tempo real
  (percentual de download, extração de áudio quando aplicável).
- Se a pasta de destino não existir, o app cria automaticamente.
- Se o link for inválido ou o download falhar, o erro aparece no log e o
  programa continua aberto (não trava, não fecha).

## Fora de escopo (não implementar nesta versão)

- Download de playlists ou múltiplos links de uma vez.
- Legendas, thumbnails, metadados extras.
- Atualização automática do yt-dlp.
- Instalador (o entregável é um `.exe` portátil único).

## Arquitetura

**Stack:** Python 3 + `tkinter` (já vem com o Python instalado na máquina) +
`yt-dlp` (já instalado via pip) + `PyInstaller` para empacotar em `.exe`
único (`--onefile --windowed`). `ffmpeg` já está disponível no PATH da
máquina (confirmado: extração de áudio já funcionou antes), então não
precisa ser empacotado junto.

**Estrutura de arquivos do projeto:**

```
YT-DLP DOWNLOADER/
  docs/superpowers/specs/2026-07-09-ytdlp-gui-design.md
  src/
    app.py            # janela tkinter, monta a UI, liga eventos
    downloader.py      # constrói args do yt-dlp e roda subprocess numa thread
    config.py          # lê/escreve config.json (última pasta usada)
  build.ps1            # roda PyInstaller e gera o .exe em dist/
  README.md            # como rodar em dev e como gerar o .exe
```

**Componentes:**

- `config.py`: funções `load_config()` / `save_config(dict)`. Guarda
  `{"last_folder": "..."}` em `config.json` ao lado do executável (usa
  `sys.executable`/`sys.argv[0]` para resolver o diretório tanto rodando
  como script quanto como `.exe` compilado).
- `downloader.py`:
  - `fetch_title(url) -> str`: chama `yt-dlp --get-title <url>` (subprocess,
    captura stdout) e retorna o título. Rodado em thread separada, chamada
    a partir do evento de perda de foco do campo de link.
  - `build_args(url, formato, qualidade, nome_arquivo, pasta) -> list[str]`:
    monta a lista de argumentos do yt-dlp equivalente a
    `-x --audio-format mp3 --audio-quality <kbps>` (MP3) ou
    `-f "bestvideo[height<=N]+bestaudio/best[height<=N]"` (MP4 com limite de
    altura, ou `-f best` para "Melhor disponível"), sempre com
    `-o "<pasta>/<nome_arquivo>.%(ext)s"`.
  - `run_download(args, on_output: callable, on_done: callable)`: abre
    `subprocess.Popen` com os args, lê stdout linha a linha e chama
    `on_output(linha)` pra cada linha (usado pra atualizar o log na UI via
    `root.after`), chama `on_done(returncode)` ao final.
- `app.py`: monta a janela (link, rádio MP3/MP4, dropdown de qualidade,
  campo de nome, linha de pasta + botão trocar, botão baixar, caixa de log),
  liga os eventos aos componentes de `downloader.py` e `config.py`. Todo
  trabalho de rede/subprocess roda em `threading.Thread`, e as atualizações
  de UI voltam pra thread principal via `root.after(0, ...)`.

## Fluxo de dados

1. Usuário cola o link → sai do campo (FocusOut) → thread busca o título →
   preenche "Nome do arquivo" (se o usuário já tiver digitado algo manualmente
   antes disso, não sobrescreve — só preenche se o campo ainda estiver vazio
   ou igual ao último título auto-preenchido).
2. Usuário escolhe formato → dropdown de qualidade atualiza as opções
   correspondentes.
3. Usuário confere/edita nome do arquivo e pasta de destino.
4. Clica "Baixar" → valida que o link não está vazio → desabilita o botão →
   cria a pasta se não existir → salva a pasta em `config.json` → dispara
   thread com `run_download` → log recebe as linhas de progresso.
5. Ao terminar: reabilita o botão, mostra "Concluído" ou a mensagem de erro
   no log.

## Tratamento de erros

- yt-dlp não encontrado no PATH: mensagem clara no log orientando a
  reinstalar (`pip install yt-dlp`).
- Link vazio ao clicar "Baixar": mensagem no log, não tenta rodar.
- Falha de rede / vídeo indisponível: stderr do yt-dlp é capturado e
  mostrado no log, botão reabilita pra nova tentativa.

## Build e distribuição

- `build.ps1` roda `pyinstaller --onefile --windowed --name ytdlp-gui
  src/app.py`, gerando `dist/ytdlp-gui.exe`.
- `README.md` documenta: como rodar em dev (`python src/app.py`), como
  gerar o `.exe` (`./build.ps1`), e o pré-requisito de `yt-dlp` e `ffmpeg`
  no PATH.

## Testes

Sem framework de testes automatizado (app pequeno, UI manual). Verificação
manual cobrindo:
- Rodar `python src/app.py` direto, baixar um vídeo em MP3 e outro em MP4.
- Testar auto-preenchimento do nome ao colar um link e sair do campo.
- Testar edição manual do nome (não deve ser sobrescrito).
- Testar troca de pasta e persistência entre reaberturas do app.
- Testar pasta inexistente (deve criar sozinha).
- Testar link inválido (deve mostrar erro sem travar).
- Gerar o `.exe` com `build.ps1` e repetir os testes acima rodando o `.exe`
  diretamente (fora do ambiente de desenvolvimento).
