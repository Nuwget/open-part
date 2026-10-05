# Open Part

Transformador de imagens em pixel art para Linux e Windows.

Versão alfa: interface gráfica moderna com **Flet** + Pillow. Abre uma imagem,
aplica pixel art com blocos e paleta ajustáveis, preview fixo, e permite
exportar na resolução original ou aprimorada (upscaled).

## Requisitos

- Python 3.10+
- Pillow
- Flet

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

```bash
make install   # cria .venv e instala dependências
make run       # abre a aplicação gráfica
```

Ou manualmente:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

1. Clique em **Abrir Imagem** e escolha o arquivo.
2. Ajuste o **tamanho do pixel** no controle deslizante.
3. Clique em **Salvar** para exportar o resultado.

## Arquitetura

```
main.py            # ponto de entrada (Flet)
src/core.py        # lógica de pixelização (pura, testável, sem GUI)
src/app_flet.py    # interface gráfica (Flet)
src/gui.py         # interface antiga (Tkinter), mantida como referência
```

## Status

**Alpha** — funcionalidade mínima: abrir, pixelar, salvar.
Próximos passos: CLI, paleta de cores, dithering, redução de cores.
