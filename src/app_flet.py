"""Interface gráfica moderna (Flet) do Open Part."""

from __future__ import annotations

import io
from pathlib import Path

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


def _png_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.convert("RGBA").save(buffer, format="PNG")
    return buffer.getvalue()


def main(page: ft.Page) -> None:
    page.title = "Open Part"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    state: dict[str, Image.Image | None] = {"source": None, "result": None}

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

    snack = ft.SnackBar(ft.Text(""))
    snack.open = False

    def notify(message: str) -> None:
        snack.content = ft.Text(message)
        snack.open = True
        page.update()

    def pick_image(e: ft.FilePickerResultEvent) -> None:
        if not e.files:
            return
        try:
            state["source"] = Image.open(e.files[0].path)
        except Exception as exc:
            notify(f"Erro ao abrir: {exc}")
            return
        update_preview()

    async def save_original(e: ft.ControlEvent) -> None:
        if state["result"] is None:
            return
        path = await save_picker.save_file(
            dialog_title="Exportar imagem original",
            file_name="pixelart.png",
            allowed_extensions=["png"],
        )
        if not path:
            return
        state["result"].save(path)
        notify(f"Salvo em: {path}")

    async def save_enhanced(e: ft.ControlEvent) -> None:
        if state["result"] is None:
            return
        path = await save_picker.save_file(
            dialog_title="Exportar aprimorado",
            file_name="pixelart_enhanced.png",
            allowed_extensions=["png"],
        )
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

    open_picker = ft.FilePicker(on_result=pick_image)
    save_picker = ft.FilePicker()
    page.overlay.append(open_picker)
    page.overlay.append(save_picker)
    page.overlay.append(snack)

    pixel_slider = ft.Slider(min=1, max=64, value=8, divisions=63, label="{value}", on_change=lambda _: update_preview())
    colors_slider = ft.Slider(min=2, max=256, value=16, divisions=254, label="{value}", on_change=lambda _: update_preview())
    dither_switch = ft.Switch(label="Dithering", value=False, on_change=lambda _: update_preview())

    preview_img = ft.Image(src="", width=PREVIEW_WIDTH, height=PREVIEW_HEIGHT, fit=ft.BoxFit.CONTAIN, border_radius=8)

    resolution_dropdown = ft.Dropdown(
        label="Resolução do export aprimorado",
        value="1080p (Full HD)",
        options=[ft.dropdown.Option(label) for label in RESOLUTIONS],
        width=280,
    )

    page.add(
        ft.Text("Open Part", size=28, weight=ft.FontWeight.BOLD),
        ft.Text("Transforme suas imagens em pixel art", size=14, color=ft.Colors.GREY),
        ft.Divider(),
        ft.FilledButton("Abrir imagem", icon=ft.Icons.FOLDER_OPEN, on_click=lambda _: open_picker.pick_files()),
        ft.Row([ft.Text("Tamanho do pixel"), pixel_slider]),
        ft.Row([ft.Text("Cores"), colors_slider]),
        ft.Row([dither_switch]),
        ft.Divider(),
        ft.Text("Preview", size=18, weight=ft.FontWeight.BOLD),
        preview_img,
        ft.Divider(),
        ft.Text("Exportar aprimorado (enhance quality)", size=16, weight=ft.FontWeight.BOLD),
        resolution_dropdown,
        ft.FilledButton("Exportar aprimorado", icon=ft.Icons.TUNE, on_click=save_enhanced),
        ft.Divider(),
        ft.Text("Exportar imagem original", size=16, weight=ft.FontWeight.BOLD),
        ft.FilledButton("Exportar original", icon=ft.Icons.IMAGE, on_click=save_original),
    )


def run() -> None:
    ft.run(main)
