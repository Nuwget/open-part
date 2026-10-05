"""Lógica pura de transformação de imagem em pixel art."""

from __future__ import annotations

from PIL import Image


def pixelate(
    image: Image.Image,
    block_size: int,
    colors: int = 16,
    dither: bool = False,
) -> Image.Image:
    """Transforma a imagem em pixel art com estética de "jogo retrô".

    Pipeline:
        1. Reduz a resolução por média de blocos (filtro BOX).
        2. Quantiza para uma paleta limitada (mediana de cores).
        3. Amplia com NEAREST, gerando pixels nítidos.

    Args:
        image: Imagem de origem (qualquer modo; será convertida para RGBA).
        block_size: Tamanho do bloco em pixels (1 = sem pixelização).
        colors: Quantidade máxima de cores na paleta (2..256).
        dither: Se True, aplica Floyd–Steinberg na quantização.

    Returns:
        Nova imagem em modo RGBA com o efeito pixel art.
    """
    if block_size < 1:
        raise ValueError("block_size deve ser >= 1")
    if not 2 <= colors <= 256:
        raise ValueError("colors deve estar entre 2 e 256")

    rgba = image.convert("RGBA")
    if block_size > 1:
        small_width = max(1, rgba.width // block_size)
        small_height = max(1, rgba.height // block_size)
        rgba = rgba.resize((small_width, small_height), Image.BOX)

    if colors < 256:
        rgba = _quantize(rgba, colors, dither)

    return rgba.resize(image.size, Image.NEAREST)


def _quantize(image: Image.Image, colors: int, dither: bool) -> Image.Image:
    """Reduz a paleta preservando o canal alpha."""
    alpha = image.getchannel("A")
    rgb = image.convert("RGB")
    quantized = rgb.quantize(colors=colors, method=Image.MEDIANCUT)
    mode = Image.FLOYDSTEINBERG if dither else Image.NONE
    reduced = rgb.quantize(palette=quantized, dither=mode).convert("RGBA")
    reduced.putalpha(alpha)
    return reduced
