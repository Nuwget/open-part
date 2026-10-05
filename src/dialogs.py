"""Seletores de arquivo nativos de cada sistema operacional.

- Linux: usa o zenity (diálogo do GNOME) quando disponível.
- Windows/macOS: o filedialog do Tkinter já usa os diálogos nativos do SO.
- Fallback geral: filedialog do Tkinter.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

IMAGE_FILTERS = "*.png *.jpg *.jpeg *.webp *.bmp *.gif"


def _zenity(args: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            ["zenity", *args], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        return None
    if completed.returncode != 0:
        return ""  # usuário cancelou
    return completed.stdout.strip()


def _tk_save(dialog: str, **kwargs: object) -> str:
    root = tk.Tk()
    root.withdraw()
    try:
        func = getattr(filedialog, dialog)
        return func(parent=root, **kwargs)  # type: ignore[no-any-return]
    finally:
        root.destroy()


def pick_open_path(initial_dir: Path, title: str, label: str) -> str:
    """Diálogo nativo para escolher uma imagem existente."""
    if sys.platform.startswith("linux") and shutil.which("zenity"):
        picked = _zenity(
            [
                "--file-selection",
                f"--filename={initial_dir}/",
                f"--title={title}",
                f"--file-filter={label} | {IMAGE_FILTERS}",
            ]
        )
        if picked is not None:
            return picked
    return _tk_save(
        "askopenfilename", initialdir=initial_dir, filetypes=[(label, IMAGE_FILTERS)]
    )


def pick_save_path(initial_dir: Path, title: str, initialfile: str) -> str:
    """Diálogo nativo para escolher onde salvar um PNG."""
    if sys.platform.startswith("linux") and shutil.which("zenity"):
        picked = _zenity(
            [
                "--file-selection",
                "--save",
                f"--filename={initial_dir}/{initialfile}",
                f"--title={title}",
                "--file-filter=PNG | *.png",
            ]
        )
        if picked is not None:
            return picked
    return _tk_save(
        "asksaveasfilename",
        initialdir=initial_dir,
        initialfile=initialfile,
        defaultextension=".png",
        filetypes=[("PNG", "*.png")],
    )
