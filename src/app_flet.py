"""Interface gráfica moderna (Flet) do Open Part.

Layout em cartões: controles à esquerda, preview à direita, exportação
embaixo. Diálogos de arquivo nativos de cada SO via src.dialogs.
"""

from __future__ import annotations

import io
from pathlib import Path

import flet as ft
from PIL import Image

from src.core import pixelate
from src.dialogs import pick_open_path, pick_save_path

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


def _card(title: str, *controls: ft.Control) -> ft.Card:
    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                [ft.Text(title, size=16, weight=ft.FontWeight.BOLD), *controls],
                spacing=12,
            ),
            padding=16,
        )
    )


def main(page: ft.Page) -> None:
    page.title = "Open Part"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 24
    page.scroll = ft.ScrollMode.AUTO

    state: dict[str, Image.Image | None] = {"source": None, "result": None}

    status = ft.Text("", color=ft.Colors.GREY, semantics_label="Status")

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
        path = pick_open_path(IMAGES_DIR, "Abrir Imagem", "Imagens")
        if not path:
            return
        try:
            state["source"] = Image.open(path)
        except Exception as exc:
            notify(f"Erro ao abrir: {exc}")
            return
        notify(f"Aberto: {Path(path).name}")
        update_preview()

    def _require_result() -> Image.Image | None:
        if state["result"] is None:
            notify("Abra uma imagem primeiro.")
            return None
        return state["result"]

    def export_original(_: ft.ControlEvent) -> None:
        result = _require_result()
        if result is None:
            return
        path = pick_save_path(IMAGES_DIR, "Exportar imagem original", "pixelart.png")
        if not path:
            return
        result.save(path)
        notify(f"Salvo em: {path}")

    def export_enhanced(_: ft.ControlEvent) -> None:
        result = _require_result()
        if result is None:
            return
        path = pick_save_path(IMAGES_DIR, "Exportar aprimorado", "pixelart_enhanced.png")
        if not path:
            return
        target = RESOLUTIONS[resolution_dropdown.value]
        ratio = target / max(result.size)
        enlarged = result.resize(
            (max(1, int(result.width * ratio)), max(1, int(result.height * ratio))),
            Image.LANCZOS,
        )
        enlarged.save(path)
        notify(f"Salvo aprimorado em: {path}")

    def on_pixel_change(_: ft.ControlEvent) -> None:
        pixel_value.value = str(int(pixel_slider.value))
        update_preview()

    def on_colors_change(_: ft.ControlEvent) -> None:
        colors_value.value = str(int(colors_slider.value))
        update_preview()

    pixel_value = ft.Text("8", width=36, tooltip="Valor atual do tamanho do pixel")
    pixel_slider = ft.Slider(
        min=1, max=64, value=8, divisions=63, label="{value}",
        expand=True, tooltip="Tamanho do bloco do pixel art",
        on_change=on_pixel_change,
    )
    colors_value = ft.Text("16", width=36, tooltip="Valor atual da paleta de cores")
    colors_slider = ft.Slider(
        min=2, max=256, value=16, divisions=254, label="{value}",
        expand=True, tooltip="Quantidade máxima de cores",
        on_change=on_colors_change,
    )
    dither_switch = ft.Switch(
        label="Dithering", value=False,
        tooltip="Suaviza transições com pontilhado (Floyd–Steinberg)",
        on_change=lambda _: update_preview(),
    )

    preview_img = ft.Image(
        src="", width=PREVIEW_WIDTH, height=PREVIEW_HEIGHT,
        fit=ft.BoxFit.CONTAIN, border_radius=8,
        semantics_label="Pré-visualização do pixel art",
    )

    resolution_dropdown = ft.Dropdown(
        label="Resolução do export aprimorado",
        value="1080p (Full HD)",
        options=[ft.dropdown.Option(label) for label in RESOLUTIONS],
        width=280,
        tooltip="Tamanho do lado maior da imagem exportada",
    )

    controls_card = _card(
        "Ajustes",
        ft.FilledButton(
            "Abrir imagem", icon=ft.Icons.FOLDER_OPEN, on_click=open_image,
            tooltip="Escolhe a imagem de entrada",
        ),
        ft.Text("Tamanho do pixel"),
        ft.Row([pixel_slider, pixel_value]),
        ft.Text("Cores"),
        ft.Row([colors_slider, colors_value]),
        dither_switch,
    )
    preview_card = _card("Preview", preview_img, status)

    page.add(
        ft.Text("Open Part", size=28, weight=ft.FontWeight.BOLD),
        ft.Text(
            "Transforme suas imagens em pixel art",
            size=14, color=ft.Colors.GREY,
        ),
        ft.Divider(),
        ft.Row(
            [controls_card, preview_card],
            spacing=16, run_spacing=16, wrap=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        _card(
            "Exportar",
            resolution_dropdown,
            ft.Row(
                [
                    ft.FilledButton(
                        "Exportar aprimorado", icon=ft.Icons.TUNE,
                        on_click=export_enhanced,
                        tooltip="Salva ampliado na resolução escolhida",
                    ),
                    ft.FilledButton(
                        "Exportar original", icon=ft.Icons.IMAGE,
                        on_click=export_original,
                        tooltip="Salva no tamanho original",
                    ),
                ],
                wrap=True, spacing=12, run_spacing=12,
            ),
        ),
    )


def run() -> None:
    ft.run(main)
