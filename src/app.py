import os
import queue
import threading
from tkinter import StringVar, filedialog

import customtkinter as ctk

import config
import downloader
import paths
import theme

MP3_QUALIDADES = ["320", "192", "128"]
MP4_QUALIDADES = ["Best", "1080p", "720p", "480p"]

ctk.set_appearance_mode("Dark")


class App:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("yt-dlp GUI")
        self.root.configure(fg_color=theme.WINDOW_BACKGROUND)

        self.cfg = config.load_config()
        self.pasta_atual = self.cfg["last_folder"]
        # Folder the user picked, restored when switching back from MP4.
        self.pasta_usuario = self.cfg["last_folder"]
        self.last_auto_title = ""
        self.log_queue = queue.Queue()

        self._montar_ui()
        self.root.after(100, self._drenar_log)
        self.root.after(500, self._atualizar_ytdlp_em_background)

    def _label(self, parent, texto):
        ctk.CTkLabel(
            parent,
            text=texto.upper(),
            font=("Segoe UI", 11, "bold"),
            text_color=theme.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(0, 6))

    def _montar_ui(self):
        panel = ctk.CTkFrame(self.root, fg_color=theme.BACKGROUND, corner_radius=20)
        panel.pack(padx=24, pady=24, fill="both", expand=True)

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(padx=26, pady=26, fill="both", expand=True)

        ctk.CTkLabel(
            inner, text="▶ yt-dlp GUI", font=("Segoe UI", 16, "bold"), text_color=theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 16))

        self._label(inner, "Video link")
        self.link_var = StringVar()
        link_entry = ctk.CTkEntry(
            inner,
            textvariable=self.link_var,
            placeholder_text="Paste the YouTube link...",
            width=380,
            height=40,
            corner_radius=20,
            fg_color=theme.INPUT_BACKGROUND,
            border_color=theme.INPUT_BORDER,
            border_width=1,
            text_color=theme.TEXT_PRIMARY,
            placeholder_text_color=theme.TEXT_PLACEHOLDER,
        )
        link_entry.pack(fill="x", pady=(0, 14))
        link_entry.bind("<FocusOut>", self._on_link_focus_out)

        self._label(inner, "Format")
        formato_row = ctk.CTkFrame(inner, fg_color="transparent")
        formato_row.pack(fill="x", pady=(0, 14))
        formato_row.columnconfigure((0, 1), weight=1)

        self.formato_var = StringVar(value="mp3")
        self.mp3_button = theme.GradientButton(
            formato_row, text="MP3", width=180, height=36, command=lambda: self._selecionar_formato("mp3")
        )
        self.mp3_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        self.mp4_button = theme.GradientButton(
            formato_row, text="MP4", width=180, height=36, command=lambda: self._selecionar_formato("mp4")
        )
        self.mp4_button.grid(row=0, column=1, padx=(6, 0), sticky="ew")
        self.mp3_button.set_active(True)
        self.mp4_button.set_active(False)

        self.qualidade_var = StringVar()
        self.qualidade_menu = ctk.CTkOptionMenu(
            inner,
            variable=self.qualidade_var,
            values=MP3_QUALIDADES,
            width=380,
            height=36,
            corner_radius=18,
            fg_color=theme.INPUT_BACKGROUND,
            button_color=theme.INPUT_BACKGROUND,
            button_hover_color=theme.SURFACE,
            text_color=theme.TEXT_PRIMARY,
            dropdown_fg_color=theme.INPUT_BACKGROUND,
            dropdown_text_color=theme.TEXT_PRIMARY,
        )
        self.qualidade_menu.pack(fill="x", pady=(0, 14))
        self._atualizar_qualidades()

        self._label(inner, "File name")
        self.nome_var = StringVar()
        ctk.CTkEntry(
            inner,
            textvariable=self.nome_var,
            width=380,
            height=40,
            corner_radius=20,
            fg_color=theme.INPUT_BACKGROUND,
            border_color=theme.INPUT_BORDER,
            border_width=1,
            text_color=theme.TEXT_PRIMARY,
        ).pack(fill="x", pady=(0, 14))

        self._label(inner, "Destination folder")
        folder_row = ctk.CTkFrame(inner, fg_color=theme.SURFACE, corner_radius=14)
        folder_row.pack(fill="x", pady=(0, 20))
        self.pasta_label = ctk.CTkLabel(
            folder_row, text=self.pasta_atual, text_color=theme.TEXT_SECONDARY, font=("Segoe UI", 12)
        )
        self.pasta_label.pack(side="left", padx=14, pady=10)
        ctk.CTkButton(
            folder_row,
            text="Change",
            fg_color="transparent",
            hover_color=theme.SURFACE,
            text_color=theme.GRADIENT_END,
            width=60,
            command=self._trocar_pasta,
        ).pack(side="right", padx=10)

        self.baixar_button = theme.GradientButton(
            inner, text="Download", width=380, height=44, command=self._on_baixar
        )
        self.baixar_button.pack(fill="x", pady=(0, 18))

        status_row = ctk.CTkFrame(inner, fg_color="transparent")
        status_row.pack(fill="x")
        self.status_label = ctk.CTkLabel(
            status_row, text="", text_color=theme.TEXT_SECONDARY, font=("Segoe UI", 12)
        )
        self.status_label.pack(side="left")
        self.percent_label = ctk.CTkLabel(
            status_row, text="", text_color=theme.GRADIENT_END, font=("Segoe UI", 12, "bold")
        )
        self.percent_label.pack(side="right")

        self.progress_bar = theme.GradientProgressBar(inner, width=380, height=7)
        self.progress_bar.pack(fill="x", pady=(8, 0))

    def _selecionar_formato(self, formato):
        formato_anterior = self.formato_var.get()
        self.formato_var.set(formato)
        self.mp3_button.set_active(formato == "mp3")
        self.mp4_button.set_active(formato == "mp4")

        # Clicking the format that is already selected must not discard the
        # quality or the folder the user chose afterwards.
        if formato == formato_anterior:
            return

        self._atualizar_qualidades()

        # MP4 lands in the editing assets folder; MP3 goes back to the user's choice.
        destino = paths.assets_dir() if formato == "mp4" else self.pasta_usuario
        self.pasta_atual = destino
        self.pasta_label.configure(text=destino)

    def _atualizar_qualidades(self):
        valores = MP3_QUALIDADES if self.formato_var.get() == "mp3" else MP4_QUALIDADES
        self.qualidade_menu.configure(values=valores)
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
                ("status", "Error: yt-dlp not found in PATH. Install it with 'pip install yt-dlp'.")
            )
            return
        except Exception as exc:
            self.log_queue.put(("status", f"Error fetching title: {exc}"))
            return
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
            self.pasta_usuario = pasta
            self.pasta_label.configure(text=pasta)

    def _on_baixar(self):
        url = self.link_var.get().strip()
        if not url:
            self.log_queue.put(("status", "Error: paste a link before downloading."))
            return

        nome_arquivo = self.nome_var.get().strip() or "video"
        formato = self.formato_var.get()
        qualidade = self.qualidade_var.get()
        pasta = self.pasta_atual

        try:
            os.makedirs(pasta, exist_ok=True)
            config.save_config({"last_folder": pasta})

            self.baixar_button.set_enabled(False)
            args = downloader.build_args(url, formato, qualidade, nome_arquivo, pasta)
        except Exception as exc:
            self.log_queue.put(("status", f"Error preparing the download: {exc}"))
            self.baixar_button.set_enabled(True)
            return

        self.log_queue.put(("progress", 0.0))
        self.log_queue.put(("status", "Downloading..."))
        threading.Thread(target=self._rodar_download, args=(args,), daemon=True).start()

    def _rodar_download(self, args):
        def on_output(linha):
            fracao = downloader.parse_progress(linha)
            if fracao is not None:
                self.log_queue.put(("progress", fracao))

        def on_done(codigo):
            if codigo == 0:
                self.log_queue.put(("progress", 1.0))
                self.log_queue.put(("status", "Done."))
            else:
                self.log_queue.put(("status", f"Error: yt-dlp exited with code {codigo}."))

        try:
            downloader.run_download(args, on_output=on_output, on_done=on_done)
        except FileNotFoundError:
            self.log_queue.put(
                ("status", "Error: yt-dlp not found in PATH. Install it with 'pip install yt-dlp'.")
            )
        except Exception as exc:
            self.log_queue.put(("status", f"Unexpected error: {exc}"))
        finally:
            self.root.after(0, lambda: self.baixar_button.set_enabled(True))

    def _atualizar_ytdlp_em_background(self):
        threading.Thread(target=self._rodar_atualizacao, daemon=True).start()

    def _rodar_atualizacao(self):
        self.log_queue.put(("status", "Checking for yt-dlp updates..."))
        ok, mensagem = downloader.update_ytdlp()
        # A failed update is not fatal: the bundled version still works.
        self.log_queue.put(("status", mensagem if ok else f"Warning: {mensagem}"))

    def _drenar_log(self):
        try:
            while not self.log_queue.empty():
                kind, valor = self.log_queue.get_nowait()
                if kind == "progress":
                    self.progress_bar.set_progress(valor)
                    self.percent_label.configure(text=f"{round(valor * 100)}%")
                elif kind == "status":
                    self.status_label.configure(text=valor)
        finally:
            self.root.after(100, self._drenar_log)


def main():
    root = ctk.CTk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
