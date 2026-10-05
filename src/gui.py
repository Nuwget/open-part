"""Interface gráfica (Tkinter) do Open Part."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

from src.core import pixelate
from src.dialogs import IMAGE_FILTERS, pick_open_path, pick_save_path

PREVIEW_WIDTH = 640
PREVIEW_HEIGHT = 480
IMAGES_DIR = Path(__file__).resolve().parent.parent / "images"

IMAGE_FILTERS = IMAGE_FILTERS  # re-exportado de src.dialogs

STRINGS = {
    "pt": {
        "open": "Abrir Imagem",
        "save": "Salvar",
        "pixel_size": "Tamanho do pixel:",
        "colors": "Cores:",
        "dither": "Dithering",
        "language": "Idioma:",
        "error": "Erro",
        "open_fail": "Não foi possível abrir: {exc}",
        "save_fail": "Não foi possível salvar: {exc}",
        "warn": "Aviso",
        "open_first": "Abra uma imagem primeiro.",
        "images": "Imagens",
    },
    "en": {
        "open": "Open Image",
        "save": "Save",
        "pixel_size": "Pixel size:",
        "colors": "Colors:",
        "dither": "Dithering",
        "language": "Language:",
        "error": "Error",
        "open_fail": "Could not open: {exc}",
        "save_fail": "Could not save: {exc}",
        "warn": "Warning",
        "open_first": "Open an image first.",
        "images": "Images",
    },
}



class PixelArtApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Open Part — alpha")

        self.source: Image.Image | None = None
        self.result: Image.Image | None = None
        self._preview_ref: ImageTk.PhotoImage | None = None

        self.block_size = tk.IntVar(value=8)
        self.colors = tk.IntVar(value=16)
        self.dither = tk.BooleanVar(value=False)
        self.lang = tk.StringVar(value="pt")

        IMAGES_DIR.mkdir(exist_ok=True)
        self._build_widgets()

    def _build_widgets(self) -> None:
        controls = ttk.Frame(self.root, padding=8)
        controls.pack(fill=tk.X)

        self.btn_open = ttk.Button(controls, command=self.open_image)
        self.btn_open.pack(side=tk.LEFT, padx=4)
        self.btn_save = ttk.Button(controls, command=self.save_image)
        self.btn_save.pack(side=tk.LEFT, padx=4)
        self.lbl_pixel = ttk.Label(controls)
        self.lbl_pixel.pack(side=tk.LEFT, padx=(16, 4))
        ttk.Scale(
            controls,
            from_=1,
            to=64,
            variable=self.block_size,
            command=lambda _=None: self.render(),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        self.lbl_colors = ttk.Label(controls)
        self.lbl_colors.pack(side=tk.LEFT, padx=(16, 4))
        ttk.Scale(
            controls,
            from_=2,
            to=64,
            variable=self.colors,
            command=lambda _=None: self.render(),
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        self.chk_dither = ttk.Checkbutton(
            controls, variable=self.dither, command=self.render
        )
        self.chk_dither.pack(side=tk.LEFT, padx=4)

        self.lbl_language = ttk.Label(controls)
        self.lbl_language.pack(side=tk.LEFT, padx=(16, 4))
        self.cmb_language = ttk.Combobox(
            controls,
            values=["pt", "en"],
            width=4,
            state="readonly",
            textvariable=self.lang,
        )
        self.cmb_language.pack(side=tk.LEFT, padx=4)
        self.lang.trace_add("write", lambda *_: self.apply_language())

        self.apply_language()

        # Preview com tamanho fixo (canvas centralizado, fundo cinza).
        self.preview = tk.Canvas(
            self.root, width=PREVIEW_WIDTH, height=PREVIEW_HEIGHT, bg="#2b2b2b",
            highlightthickness=0,
        )
        self.preview.pack(padx=8, pady=8)

    def _t(self, key: str) -> str:
        return STRINGS[self.lang.get()][key]

    def apply_language(self) -> None:
        t = STRINGS[self.lang.get()]
        self.btn_open.configure(text=t["open"])
        self.btn_save.configure(text=t["save"])
        self.lbl_pixel.configure(text=t["pixel_size"])
        self.lbl_colors.configure(text=t["colors"])
        self.chk_dither.configure(text=t["dither"])
        self.lbl_language.configure(text=t["language"])

    def open_image(self) -> None:
        path = pick_open_path(IMAGES_DIR, self._t("open"), self._t("images"))
        if not path:
            return
        try:
            self.source = Image.open(path)
        except Exception as exc:  # arquivo inválido/corrompido
            messagebox.showerror(self._t("error"), self._t("open_fail").format(exc=exc))
            return
        self.render()

    def render(self) -> None:
        if self.source is None:
            return
        self.result = pixelate(
            self.source,
            int(self.block_size.get()),
            colors=int(self.colors.get()),
            dither=bool(self.dither.get()),
        )

        preview = self.result.copy()
        preview.thumbnail((PREVIEW_WIDTH, PREVIEW_HEIGHT), Image.LANCZOS)
        self._preview_ref = ImageTk.PhotoImage(preview)

        self.preview.delete("all")
        x = (PREVIEW_WIDTH - preview.width) // 2
        y = (PREVIEW_HEIGHT - preview.height) // 2
        self.preview.create_image(x, y, anchor=tk.NW, image=self._preview_ref)

    def save_image(self) -> None:
        if self.result is None:
            messagebox.showinfo(self._t("warn"), self._t("open_first"))
            return
        path = pick_save_path(IMAGES_DIR, self._t("save"), "pixelart.png")
        if not path:
            return
        try:
            self.result.save(Path(path))
        except Exception as exc:
            messagebox.showerror(self._t("error"), self._t("save_fail").format(exc=exc))


def run() -> None:
    root = tk.Tk()
    PixelArtApp(root)
    root.mainloop()
