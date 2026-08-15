"""
Lançador desktop do Aspersor ETo (calculadora de evapotranspiração de referência,
FAO-56 Penman-Monteith) - abre index.html numa janela nativa usando pywebview.

Funciona tanto rodando direto (`python aspersor_eto_app.py`) quanto empacotado em .exe
pelo PyInstaller (o HTML é embutido no executável via --add-data).
"""

import os
import sys

import webview


def caminho_recurso(nome_arquivo):
    """Resolve o caminho do arquivo tanto em desenvolvimento quanto dentro do .exe."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, nome_arquivo)


def main():
    html_path = caminho_recurso("index.html")
    webview.create_window(
        "Aspersor ETo — Evapotranspiração FAO-56 Penman-Monteith",
        html_path,
        width=1150,
        height=820,
        min_size=(820, 640),
    )
    webview.start()


if __name__ == "__main__":
    main()
