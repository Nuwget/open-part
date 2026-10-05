"""Interface gráfica moderna (Flet) do Open Part.

Usa diálogos de arquivo nativos do sistema (Tkinter/zenity) em vez do
FilePicker do Flet, por compatibilidade entre versões do cliente Flet.
"""

from __future__ import annotations

import io
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import flet as ft
from PIL import Image

from src.core import pixelate

IMAGES_DIR = Path(__file__).resolve().parent.parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

PREVIEW_WIDTH = 640
PREVIEW_HEIGHT = 480

RESOLUTIONS = {
    "480p (consulta)": 480,
    "720p (HD)": 720,
    "1080p (Full HD)": 1080,
    "1440p (QHD)": 1440,
    "4K (UHD)": 2160,
    "8K (UHD)": 4320,
}

IMAGE_TYPES = [("Imagens", "*.png *.jpg *.jpeg *.webp *.bmp *.gif")]


def _png_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.convert("RGBA").save(buffer, format="PNG")
    return buffer.getvalue()


def _tk_root() -> tk.Tk:
    root = tk.Tk()
    root.withdraw()
    return root


def main(page: ft.Page) -> None:
    page.title = "Open Part"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    state: dict[str, Image.Image | None] = {"source": None, "result": None}

    status = ft.Text("", color=ft.Colors.GREY)

    def notify(message: str) -> None:
        status.value = message
        page.update()

    def update_preview() -> None:
        if state["source"] is None:
            return
        result = pixelate(
            state["source"],
            int(pixel_slider.value),
            colors=int(colors_slider.value),
            dither=dither_switch.value,
        )
        state["result"] = result
        preview = result.copy()
        preview.thumbnail((PREVIEW_WIDTH, PREVIEW_HEIGHT), Image.LANCZOS)
        preview_img.data = _png_bytes(preview)
        page.update()

    def open_image(_: ft.ControlEvent) -> None:
        root = _tk_root()
        try:
            path = filedialog.askopenfilename(
                parent=root, initialdir=IMAGES_DIR, filetypes=IMAGE_TYPES
            )
        finally:
            root.destroy()
        if not path:
            return
        try:
            state["source"] = Image.open(path)
        except Exception as exc:
            notify(f"Erro ao abrir: {exc}")
            return
        notify(f"Aberto: {Path(path).name}")
        update_preview()

    def export_original(_: ft.ControlEvent) -> None:
        if state["result"] is None:
            notify("Abra uma imagem primeiro.")
            return
        root = _tk_root()
        try:
            path = filedialog.asksaveasfilename(
                parent=root,
                initialdir=IMAGES_DIR,
                initialfile="pixelart.png",
                defaultextension=".png",
                filetypes=[("PNG", "*.png")],
            )
        finally:
            root.destroy()
        if not path:
            return
        state["result"].save(path)
        notify(f"Salvo em: {path}")

    def export_enhanced(_: ft.ControlEvent) -> None:
        if state["result"] is None:
            notify("Abra uma imagem primeiro.")
            return
        root = _tk_root()
        try:
            path = filedialog.asksaveasfilename(
                parent=root,
                initialdir=IMAGES_DIR,
                initialfile="pixelart_enhanced.png",
                defaultextension=".png",
                filetypes=[("PNG", "*.png")],
            )
        finally:
            root.destroy()
        if not path:
            return
        target = RESOLUTIONS[resolution_dropdown.value]
        result = state["result"]
        ratio = target / max(result.size)
        enlarged = result.resize(
            (max(1, int(result.width * ratio)), max(1, int(result.height * ratio))),
            Image.LANCZOS,
        )
        enlarged.save(path)
        notify(f"Salvo aprimorado em: {path}")

    pixel_slider = ft.Slider(
        min=1, max=64, value=8, divisions=63, label="{value}",
        on_change=lambda _: update_preview(),
    )
    colors_slider = ft.Slider(
        min=2, max=256, value=16, divisions=254, label="{value}",
        on_change=lambda _: update_preview(),
    )
    dither_switch = ft.Switch(
        label="Dithering", value=False, on_change=lambda _: update_preview()
    )

    preview_img = ft.Image(
        src="", width=PREVIEW_WIDTH, height=PREVIEW_HEIGHT,
        fit=ft.BoxFit.CONTAIN, border_radius=8,
    )

    resolution_dropdown = ft.Dropdown(
        label="Resolução do export aprimorado",
        value="1080p (Full HD)",
        options=[ft.dropdown.Option(label) for label in RESOLUTIONS],
        width=280,
    )

    page.add(
        ft.Text("Open Part", size=28, weight=ft.FontWeight.BOLD),
        ft.Text("Transforme suas imagens em pixel art", size=14, color=ft.Colors.GREY),
        status,
        ft.Divider(),
        ft.FilledButton("Abrir imagem", icon=ft.Icons.FOLDER_OPEN, on_click=open_image),
        ft.Row([ft.Text("Tamanho do pixel"), pixel_slider]),
        ft.Row([ft.Text("Cores"), colors_slider]),
        ft.Row([dither_switch]),
        ft.Divider(),
        ft.Text("Preview", size=18, weight=ft.FontWeight.BOLD),
        preview_img,
        ft.Divider(),
        ft.Text("Exportar aprimorado (enhance quality)", size=16, weight=ft.FontWeight.BOLD),
        resolution_dropdown,
        ft.FilledButton("Exportar aprimorado", icon=ft.Icons.TUNE, on_click=export_enhanced),
        ft.Divider(),
        ft.Text("Exportar imagem original", size=16, weight=ft.FontWeight.BOLD),
        ft.FilledButton("Exportar original", icon=ft.Icons.IMAGE, on_click=export_original),
    )


def run() -> None:
    ft.run(main)
