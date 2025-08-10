import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pygame import mixer
import os
import time


class TocadorMusica:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Player de Música")
        self.janela.geometry("600x450")
        self.janela.resizable(False, False)
        self.janela.configure(bg='#121212')

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configurar_estilos()

        mixer.init()

        self.musica_atual = None
        self.pausado = False
        self.playlist = []
        self.indice_atual = 0
        self.volume = 0.7

        self.criar_interface()
        self.atualizar_progresso()

    def configurar_estilos(self):
        self.style.configure('TProgressbar',
                             background='#1DB954',
                             troughcolor='#333333',
                             bordercolor='#121212',
                             lightcolor='#1DB954',
                             darkcolor='#1DB954')

        self.style.configure('TScale',
                             background='#121212',
                             troughcolor='#333333',
                             bordercolor='#121212')

        self.style.map('TButton',
                       foreground=[('active', '#ffffff'), ('!disabled', '#ffffff')],
                       background=[('active', '#535353'), ('!disabled', '#333333')],
                       bordercolor=[('active', '#535353'), ('!disabled', '#333333')])

        self.style.configure('TButton',
                             font=('Segoe UI', 10),
                             padding=6,
                             relief='flat',
                             anchor='center')

    def criar_interface(self):
        frame_principal = tk.Frame(self.janela, bg='#121212')
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        frame_lista = tk.Frame(frame_principal, bg='#121212')
        frame_lista.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.lista_musicas = tk.Listbox(
            frame_lista,
            bg='#212121',
            fg='#ffffff',
            selectbackground='#1DB954',
            selectforeground='#ffffff',
            highlightthickness=0,
            borderwidth=0,
            font=('Segoe UI', 10),
            height=12,
            width=60,
            yscrollcommand=scrollbar.set
        )
        self.lista_musicas.pack(fill=tk.BOTH, expand=True)
        self.lista_musicas.bind('<Double-1>', self.tocar_musica_selecionada)
        scrollbar.config(command=self.lista_musicas.yview)

        frame_progresso = tk.Frame(frame_principal, bg='#121212')
        frame_progresso.pack(fill=tk.X, pady=(10, 5))

        self.barra_progresso = ttk.Progressbar(
            frame_progresso,
            orient='horizontal',
            mode='determinate',
            length=400,
            style='TProgressbar'
        )
        self.barra_progresso.pack(side=tk.LEFT, padx=5)

        self.rotulo_tempo = tk.Label(
            frame_progresso,
            text='00:00 / 00:00',
            bg='#121212',
            fg='#b3b3b3',
            font=('Segoe UI', 9)
        )
        self.rotulo_tempo.pack(side=tk.LEFT, padx=5)

        frame_botoes = tk.Frame(frame_principal, bg='#121212')
        frame_botoes.pack(pady=(10, 15))

        btn_anterior = ttk.Button(
            frame_botoes,
            text="⏮",
            command=self.musica_anterior,
            width=3,
            style='TButton'
        )
        btn_anterior.grid(row=0, column=0, padx=5)

        btn_play = ttk.Button(
            frame_botoes,
            text="▶",
            command=self.tocar_musica,
            width=3,
            style='TButton'
        )
        btn_play.grid(row=0, column=1, padx=5)

        btn_pause = ttk.Button(
            frame_botoes,
            text="⏸",
            command=self.pausar_musica,
            width=3,
            style='TButton'
        )
        btn_pause.grid(row=0, column=2, padx=5)

        btn_stop = ttk.Button(
            frame_botoes,
            text="⏹",
            command=self.parar_musica,
            width=3,
            style='TButton'
        )
        btn_stop.grid(row=0, column=3, padx=5)

        btn_proxima = ttk.Button(
            frame_botoes,
            text="⏭",
            command=self.proxima_musica,
            width=3,
            style='TButton'
        )
        btn_proxima.grid(row=0, column=4, padx=5)

        frame_volume = tk.Frame(frame_principal, bg='#121212')
        frame_volume.pack(fill=tk.X, pady=(5, 10))

        tk.Label(
            frame_volume,
            text="Volume:",
            bg='#121212',
            fg='#b3b3b3',
            font=('Segoe UI', 9)
        ).pack(side=tk.LEFT)

        self.controle_volume = ttk.Scale(
            frame_volume,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.ajustar_volume,
            style='TScale'
        )
        self.controle_volume.set(self.volume * 100)
        self.controle_volume.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        btn_adicionar = ttk.Button(
            frame_principal,
            text="➕ Adicionar Músicas",
            command=self.adicionar_musicas,
            style='TButton'
        )
        btn_adicionar.pack(pady=(5, 10), fill=tk.X)

        self.barra_status = tk.Label(
            frame_principal,
            relief=tk.FLAT,
            anchor=tk.W,
            bg='#333333',
            fg='#ffffff',
            font=('Segoe UI', 9),
            padx=10
        )
        self.barra_status.pack(fill=tk.X, pady=(5, 0))

    def adicionar_musicas(self):
        arquivos = filedialog.askopenfilenames(
            initialdir=os.getcwd(),
            title="Selecione as músicas",
            filetypes=(("Arquivos MP3", "*.mp3"), ("Todos os arquivos", "*.*"))
        )

        if arquivos:
            for arquivo in arquivos:
                self.playlist.append(arquivo)
                self.lista_musicas.insert(tk.END, os.path.basename(arquivo))

            self.barra_status['text'] = f"{len(arquivos)} música(s) adicionada(s)"

    def tocar_musica(self):
        if not self.playlist:
            messagebox.showwarning("Aviso", "Nenhuma música na playlist!")
            return

        if self.musica_atual is None:
            self.musica_atual = self.playlist[0]
            self.indice_atual = 0

        if not self.pausado:
            mixer.music.load(self.musica_atual)
            mixer.music.play()
            self.barra_status['text'] = f"Tocando: {os.path.basename(self.musica_atual)}"
            mixer.music.set_volume(self.volume)
        else:
            mixer.music.unpause()
            self.pausado = False
            self.barra_status['text'] = f"Tocando: {os.path.basename(self.musica_atual)}"

        self.lista_musicas.selection_clear(0, tk.END)
        self.lista_musicas.selection_set(self.indice_atual)
        self.lista_musicas.activate(self.indice_atual)

    def pausar_musica(self):
        if mixer.music.get_busy() and not self.pausado:
            mixer.music.pause()
            self.pausado = True
            self.barra_status['text'] = f"Pausado: {os.path.basename(self.musica_atual)}"

    def parar_musica(self):
        mixer.music.stop()
        self.pausado = False
        self.barra_status['text'] = "Música parada"
        self.barra_progresso['value'] = 0
        self.rotulo_tempo['text'] = '00:00 / 00:00'

    def proxima_musica(self):
        if not self.playlist:
            return

        self.parar_musica()
        self.indice_atual = (self.indice_atual + 1) % len(self.playlist)
        self.musica_atual = self.playlist[self.indice_atual]
        self.tocar_musica()

    def musica_anterior(self):
        if not self.playlist:
            return

        self.parar_musica()
        self.indice_atual = (self.indice_atual - 1) % len(self.playlist)
        self.musica_atual = self.playlist[self.indice_atual]
        self.tocar_musica()

    def tocar_musica_selecionada(self, event):
        if not self.playlist:
            return

        indice_selecionado = self.lista_musicas.curselection()
        if indice_selecionado:
            self.parar_musica()
            self.indice_atual = indice_selecionado[0]
            self.musica_atual = self.playlist[self.indice_atual]
            self.tocar_musica()

    def ajustar_volume(self, valor):
        self.volume = float(valor) / 100
        mixer.music.set_volume(self.volume)

    def atualizar_progresso(self):
        if mixer.music.get_busy() and not self.pausado:
            tempo_atual = mixer.music.get_pos() / 1000
            duracao = self.obter_duracao(self.musica_atual)

            if duracao > 0:
                progresso = (tempo_atual / duracao) * 100
                self.barra_progresso['value'] = progresso

                tempo_str = time.strftime('%M:%S', time.gmtime(tempo_atual))
                duracao_str = time.strftime('%M:%S', time.gmtime(duracao))
                self.rotulo_tempo['text'] = f"{tempo_str} / {duracao_str}"

        self.janela.after(1000, self.atualizar_progresso)

    def obter_duracao(self, caminho_musica):
        try:
            som = mixer.Sound(caminho_musica)
            return som.get_length()
        except:
            return 0


if __name__ == "__main__":
    root = tk.Tk()
    app = TocadorMusica(root)
    root.mainloop()