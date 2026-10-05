# Open Part

Transformador de imagens em pixel art para Linux e Windows.

Versão alfa: interface gráfica (Tkinter + Pillow) que abre uma imagem,
aplica o efeito pixel art com tamanho de bloco ajustável e permite salvar
o resultado (PNG com transparência preservada).

## Requisitos

- Python 3.10+
- Pillow
- Tkinter (`apt install python3-tk` no Linux; já vem com o Python no Windows)

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
main.py            # ponto de entrada
src/core.py        # lógica de pixelização (pura, testável, sem GUI)
src/gui.py         # interface gráfica (Tkinter)
```

## Status

**Alpha** — funcionalidade mínima: abrir, pixelar, salvar.
Próximos passos: CLI, paleta de cores, dithering, redução de cores.
