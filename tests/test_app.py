import app
import paths


class _Var:
    def __init__(self, valor=""):
        self._valor = valor

    def get(self):
        return self._valor

    def set(self, valor):
        self._valor = valor


class _Botao:
    def __init__(self):
        self.ativo = None

    def set_active(self, ativo):
        self.ativo = ativo


class _Label:
    def __init__(self):
        self.texto = None

    def configure(self, text):
        self.texto = text


class _Menu:
    def __init__(self):
        self.valores = None

    def configure(self, values):
        self.valores = values


def _tela(formato="mp3", pasta_usuario=None):
    """Stand-in for App without a Tk root: _selecionar_formato only uses these."""
    tela = app.App.__new__(app.App)
    tela.formato_var = _Var(formato)
    tela.qualidade_var = _Var()
    tela.qualidade_menu = _Menu()
    tela.mp3_button = _Botao()
    tela.mp4_button = _Botao()
    tela.pasta_label = _Label()
    tela.pasta_usuario = pasta_usuario or "/tmp/downloads"
    tela.pasta_atual = tela.pasta_usuario
    return tela


def test_mp4_preenche_a_pasta_de_assets():
    tela = _tela(formato="mp3")

    app.App._selecionar_formato(tela, "mp4")

    assert tela.pasta_atual == paths.assets_dir()
    assert tela.pasta_label.texto == paths.assets_dir()


def test_voltar_para_mp3_restaura_a_pasta_do_usuario():
    tela = _tela(formato="mp4", pasta_usuario="/tmp/musica")

    app.App._selecionar_formato(tela, "mp3")

    assert tela.pasta_atual == "/tmp/musica"
    assert tela.pasta_label.texto == "/tmp/musica"


def test_reclicar_o_mesmo_formato_preserva_a_pasta_escolhida():
    tela = _tela(formato="mp4")
    # The user picked a folder after already switching to MP4.
    tela.pasta_atual = "/tmp/desktop"
    tela.pasta_label.texto = "/tmp/desktop"

    app.App._selecionar_formato(tela, "mp4")

    assert tela.pasta_atual == "/tmp/desktop"
    assert tela.pasta_label.texto == "/tmp/desktop"


def test_reclicar_o_mesmo_formato_preserva_a_qualidade_escolhida():
    tela = _tela(formato="mp4")
    tela.qualidade_var.set("720p")

    app.App._selecionar_formato(tela, "mp4")

    assert tela.qualidade_var.get() == "720p"


def test_trocar_de_formato_reseta_a_lista_de_qualidades():
    tela = _tela(formato="mp3")

    app.App._selecionar_formato(tela, "mp4")

    assert tela.qualidade_menu.valores == app.MP4_QUALIDADES
    assert tela.qualidade_var.get() == app.MP4_QUALIDADES[0]


def test_botoes_refletem_o_formato_ativo():
    tela = _tela(formato="mp3")

    app.App._selecionar_formato(tela, "mp4")

    assert tela.mp4_button.ativo is True
    assert tela.mp3_button.ativo is False
