import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, ttk

import config
import downloader

MP3_QUALIDADES = ["320", "192", "128"]
MP4_QUALIDADES = ["Melhor", "1080p", "720p", "480p"]


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("yt-dlp GUI")

        self.cfg = config.load_config()
        self.pasta_atual = self.cfg["last_folder"]
        self.last_auto_title = ""
        self.log_queue = queue.Queue()

        self._montar_ui()
        self.root.after(100, self._drenar_log)

    def _montar_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="Link do vídeo:").grid(row=0, column=0, sticky="w")
        self.link_var = tk.StringVar()
        link_entry = ttk.Entry(frame, textvariable=self.link_var, width=60)
        link_entry.grid(row=1, column=0, columnspan=3, sticky="ew")
        link_entry.bind("<FocusOut>", self._on_link_focus_out)

        self.formato_var = tk.StringVar(value="mp3")
        ttk.Radiobutton(
            frame, text="MP3 (áudio)", variable=self.formato_var, value="mp3",
            command=self._atualizar_qualidades,
        ).grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(
            frame, text="MP4 (vídeo)", variable=self.formato_var, value="mp4",
            command=self._atualizar_qualidades,
        ).grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="Qualidade:").grid(row=3, column=0, sticky="w")
        self.qualidade_var = tk.StringVar()
        self.qualidade_combo = ttk.Combobox(
            frame, textvariable=self.qualidade_var, state="readonly",
        )
        self.qualidade_combo.grid(row=3, column=1, columnspan=2, sticky="ew")
        self._atualizar_qualidades()

        ttk.Label(frame, text="Nome do arquivo:").grid(row=4, column=0, sticky="w")
        self.nome_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.nome_var, width=60).grid(
            row=5, column=0, columnspan=3, sticky="ew"
        )

        ttk.Label(frame, text="Pasta de destino:").grid(row=6, column=0, sticky="w")
        self.pasta_label = ttk.Label(frame, text=self.pasta_atual)
        self.pasta_label.grid(row=7, column=0, columnspan=2, sticky="w")
        ttk.Button(frame, text="Trocar pasta", command=self._trocar_pasta).grid(
            row=7, column=2, sticky="e"
        )

        self.baixar_button = ttk.Button(frame, text="Baixar", command=self._on_baixar)
        self.baixar_button.grid(row=8, column=0, pady=10, sticky="w")

        self.log_text = tk.Text(frame, height=12, width=70, state="disabled")
        self.log_text.grid(row=9, column=0, columnspan=3, sticky="nsew")

    def _atualizar_qualidades(self):
        valores = MP3_QUALIDADES if self.formato_var.get() == "mp3" else MP4_QUALIDADES
        self.qualidade_combo["values"] = valores
        self.qualidade_var.set(valores[0])

    def _on_link_focus_out(self, event):
        url = self.link_var.get().strip()
        if not url:
            return
        threading.Thread(target=self._buscar_titulo, args=(url,), daemon=True).start()

    def _buscar_titulo(self, url):
        try:
            titulo = downloader.fetch_title(url)
        except FileNotFoundError:
            self.log_queue.put(
                "Erro: yt-dlp não encontrado no PATH. Instale com 'pip install yt-dlp'."
            )
            return
        except Exception as exc:
            self.log_queue.put(f"Erro ao buscar título: {exc}")
            return
        self.log_queue.put(f"Título encontrado: {titulo}")
        self.root.after(0, self._preencher_nome, titulo)

    def _preencher_nome(self, titulo):
        nome_atual = self.nome_var.get()
        if nome_atual == "" or nome_atual == self.last_auto_title:
            self.nome_var.set(titulo)
            self.last_auto_title = titulo

    def _trocar_pasta(self):
        pasta = filedialog.askdirectory(initialdir=self.pasta_atual)
        if pasta:
            self.pasta_atual = pasta
            self.pasta_label.config(text=pasta)

    def _on_baixar(self):
        url = self.link_var.get().strip()
        if not url:
            self.log_queue.put("Erro: cole um link antes de baixar.")
            return

        nome_arquivo = self.nome_var.get().strip() or "video"
        formato = self.formato_var.get()
        qualidade = self.qualidade_var.get()
        pasta = self.pasta_atual

        os.makedirs(pasta, exist_ok=True)
        config.save_config({"last_folder": pasta})

        self.baixar_button.config(state="disabled")
        args = downloader.build_args(url, formato, qualidade, nome_arquivo, pasta)
        threading.Thread(target=self._rodar_download, args=(args,), daemon=True).start()

    def _rodar_download(self, args):
        try:
            downloader.run_download(
                args,
                on_output=lambda linha: self.log_queue.put(linha),
                on_done=lambda codigo: self.log_queue.put(
                    "Concluído." if codigo == 0 else f"Erro: yt-dlp saiu com código {codigo}."
                ),
            )
        except FileNotFoundError:
            self.log_queue.put(
                "Erro: yt-dlp não encontrado no PATH. Instale com 'pip install yt-dlp'."
            )
        except Exception as exc:
            self.log_queue.put(f"Erro inesperado: {exc}")
        finally:
            self.root.after(0, lambda: self.baixar_button.config(state="normal"))

    def _drenar_log(self):
        while not self.log_queue.empty():
            linha = self.log_queue.get_nowait()
            self.log_text.config(state="normal")
            self.log_text.insert("end", linha + "\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.root.after(100, self._drenar_log)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
