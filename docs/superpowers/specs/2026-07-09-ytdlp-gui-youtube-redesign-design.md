# yt-dlp GUI — Redesign visual estilo YouTube (dark mode) — Design

## Objetivo

Substituir a interface tkinter simples atual por um visual inspirado no dark
mode / nova identidade do YouTube (aprovado pelo usuário num mockup: painel
único centralizado, fundo escuro sólido, pílulas com gradiente
vermelho→rosa), e trocar a caixa de log por uma barra de progresso em
formato de pílula com a porcentagem do download.

## Referências visuais (aprovadas pelo usuário)

- Dashboard conceitual do YouTube (Dribbble): painel escuro flutuante,
  cantos bem arredondados, botões em pílula vermelha, cards.
- Reel do Instagram sobre o rebrand do YouTube: barra de progresso fina em
  pílula, trilho cinza claro, preenchimento em gradiente vermelho→rosa.
- Mockup final aprovado nesta sessão (`layout-final.html`): painel único
  sem sidebar, fundo `#0F0F0F`, campos estilo barra de busca, botão
  "Baixar" e pílula de formato ativo em gradiente, barra de progresso em
  pílula com linha de status curta acima (ex.: "Baixando... 58%").

## Decisões já tomadas

- **Biblioteca:** trocar `tkinter`/`ttk` puro por **CustomTkinter**
  (wrapper sobre tkinter, mesma arquitetura, sem trocar linguagem).
  CustomTkinter já depende de Pillow — não é preciso adicionar Pillow
  manualmente.
- **Gradiente:** CustomTkinter só aceita cor sólida em botões/barra de
  progresso nativos. O usuário escolheu o gradiente de verdade
  (vermelho→rosa) em vez de cor sólida — isso exige um componente
  customizado desenhado com Pillow (ver "Componentes customizados"
  abaixo), não os widgets nativos do CustomTkinter para esses elementos
  específicos.
- **Sem sidebar:** painel único centralizado, sem barra lateral (o app só
  tem uma tela/função, então uma sidebar seria só decorativa).
- **Fundo sólido**, sem imagem de fundo com gradiente colorido desfocado
  (mais simples, evita gerenciar assets de imagem de fundo).
- **Sem caixa de log rolável.** Vira uma barra de progresso em pílula +
  uma linha de status curta (uma frase: "Baixando... 58%", "Concluído.",
  ou uma mensagem de erro). Erros que hoje aparecem no log (yt-dlp não
  encontrado no PATH, link inválido, falha ao preparar o download, etc.)
  passam a aparecer nessa linha de status.

## Sistema de design

**Cores:**

| Token | Hex | Uso |
|---|---|---|
| Background | `#0F0F0F` | Fundo da janela/painel |
| Surface | `#181818` | Chip da pasta de destino |
| Input background | `#121212` | Campos de texto/dropdown |
| Input border | `#303030` | Borda dos campos |
| Pill inativa | `#212121` | Pílula de formato não selecionado |
| Track da barra de progresso | `#272727` | Trilho (parte não preenchida) |
| Texto primário | `#F1F1F1` | Títulos, valores |
| Texto secundário | `#AAAAAA` | Labels, status |
| Placeholder | `#717171` | Texto de exemplo nos campos |
| Gradiente (início) | `#FF0000` | Vermelho YouTube |
| Gradiente (fim) | `#FF4D6D` | Rosa |

O gradiente (`#FF0000` → `#FF4D6D`, horizontal) é usado em: botão
"Baixar", pílula de formato ativa (MP3/MP4 selecionado), preenchimento da
barra de progresso.

**Tipografia:** fonte do sistema (`Segoe UI`, já disponível no Windows,
sem precisar empacotar arquivos de fonte). Título do app ~16px semi-bold;
labels ~11px uppercase; corpo/campos ~13px.

**Componentes nativos do CustomTkinter** (suportam `corner_radius`, cor,
borda diretamente — sem trabalho extra):
- Campos de texto (link, nome do arquivo) → `CTkEntry`, cantos bem
  arredondados, estilo barra de busca.
- Dropdown de qualidade → `CTkOptionMenu` (não `CTkComboBox`: precisa
  continuar *somente seleção*, sem permitir digitar um valor arbitrário —
  o resto do sistema depende de `qualidade` ser sempre uma das chaves
  exatas de `MP4_HEIGHT_LIMITS`/`MP3_QUALIDADES`).
- Chip da pasta + botão "Trocar" (texto vermelho, sem fundo em pílula) →
  `CTkLabel` + `CTkButton` com `fg_color="transparent"`.

**Componentes customizados** (exigem desenho manual com Pillow, pois
precisam do gradiente):
- `GradientButton`: botão em pílula com fundo em gradiente (estado
  "ativo") ou cor sólida `#212121` (estado "inativo"), texto centralizado
  desenhado na própria imagem. Usado no botão "Baixar" (sempre ativo) e
  nas duas pílulas de formato MP3/MP4 (cada uma alterna entre ativa e
  inativa conforme a seleção — por isso as duas usam o mesmo componente,
  em vez de uma ser `GradientButton` e a outra um `CTkButton` nativo).
  Tem variantes de hover (mais clara) e "disabled" (acinzentada, para
  quando o botão "Baixar" fica desabilitado durante o download).
- `GradientProgressBar`: barra de progresso em pílula. Trilho cinza
  (`#272727`) sempre visível; por cima, um recorte da imagem de gradiente
  pré-renderizada, com largura proporcional ao progresso atual (0.0–1.0).
  Método público `set_progress(fraction: float)`.

Ambos ficam num novo módulo `src/theme.py`, junto com os tokens de cor
acima e uma função pura `render_gradient_pill(width, height, start_hex,
end_hex) -> PIL.Image.Image` que desenha um retângulo arredondado (raio =
`height / 2`) preenchido com gradiente horizontal — usada tanto pelo
`GradientButton` quanto pelo `GradientProgressBar`.

## Progresso do download

Hoje `downloader.run_download` só repassa linhas cruas de saída do
yt-dlp para um callback `on_output`. Para alimentar a barra de progresso,
`src/downloader.py` ganha uma nova função pura:

```
parse_progress(line: str) -> float | None
```

Interpreta linhas do tipo `[download]  58.3% of ...` (formato padrão do
yt-dlp) via regex e devolve a fração (`0.583`), ou `None` se a linha não
for uma linha de progresso (outras linhas são ignoradas pela UI — não
existe mais log para mostrá-las).

Em `app.py`, o `on_output` de `run_download` passa cada linha por
`downloader.parse_progress`; quando não é `None`, atualiza a barra de
progresso e a linha de status ("Baixando... N%"). `on_done` continua
funcionando como hoje (mensagem de "Concluído."/erro na linha de status,
reabilita o botão "Baixar").

## Comportamento preservado

Tudo que já funciona continua igual, só muda a forma de exibir
feedback (barra+status em vez de log):
- Auto-preenchimento do nome do arquivo ao perder foco do campo de link
  (sem sobrescrever edição manual).
- Escolha de formato/qualidade, pasta com "Trocar" e persistência em
  `config.json` só no clique de "Baixar".
- Criação automática da pasta se não existir.
- Tratamento de erros (`FileNotFoundError` do yt-dlp não estar no PATH,
  link vazio, falha ao preparar o download) — agora aparecem na linha de
  status em vez do log.
- Download em thread separada, atualização de UI thread-safe via
  `queue.Queue` + polling com `root.after`.
- Supressão das janelas de console do yt-dlp (`CREATE_NO_WINDOW`, já
  corrigido antes deste redesign).

## Empacotamento (PyInstaller)

CustomTkinter empacota arquivos de tema (`.json`) e fontes que o
PyInstaller não detecta automaticamente por análise estática. `build.ps1`
precisa incluir `--collect-all customtkinter` na chamada do PyInstaller
para evitar um `.exe` que abre e imediatamente falha por não achar esses
arquivos. Isso é uma correção conhecida e documentada do próprio
CustomTkinter para uso com PyInstaller.

## Arquivos afetados

```
src/
  app.py            # reescrito: janela CTk, novo layout, novo feedback de progresso
  downloader.py      # + parse_progress(line) -> float | None
  theme.py            # NOVO: tokens de cor, render_gradient_pill, GradientButton, GradientProgressBar
requirements.txt      # + customtkinter
build.ps1              # + --collect-all customtkinter
tests/
  test_downloader.py  # + testes de parse_progress
  test_theme.py         # NOVO: testes de render_gradient_pill (interpolação de cor pura)
```

`config.py` não muda.

## Fora de escopo

- Barra de progresso indeterminada/animada antes do primeiro dado real de
  progresso (a barra começa em 0% e salta para os valores reais conforme
  chegam).
- Hover animado com transição suave nos componentes customizados (troca
  de imagem no hover é instantânea, sem fade).
- Ícones SVG customizados — o app continua sem ícones além do "logo"
  textual simples (▶ ou similar) no cabeçalho do painel.
- Título de janela customizado (sem moldura própria) — mantém a barra de
  título nativa do Windows.

## Testes

- `parse_progress`: automatizado (`pytest`), casos com linha de progresso
  válida, linha sem progresso (retorna `None`), progresso em 100%.
- `render_gradient_pill`: automatizado (`pytest`), verifica dimensões da
  imagem e que o pixel mais à esquerda se aproxima de `start_hex` e o
  mais à direita de `end_hex`.
- `GradientButton`, `GradientProgressBar`, `app.py`: verificação manual
  (mesma convenção já usada no projeto para a UI) — checklist ao rodar
  `python src/app.py` e o `.exe` compilado.
