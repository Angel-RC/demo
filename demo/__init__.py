"""Comandos del presentador: uv run preparar | puerta | check | reiniciar.

Actúan sobre el proyecto que se abre en VS Code (por defecto ../facturacion),
que se genera desde plantilla/ para que Copilot no vea nada de la demo.
"""

import argparse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantilla"
GUARDIA = RAIZ / "guardia"
PROYECTO = RAIZ.parent / "facturacion"


def argumentos(argv: list[str] | None, descripcion: str, *ordenes: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=descripcion)
    if ordenes:
        parser.add_argument("orden", choices=ordenes)
    parser.add_argument("--proyecto", type=Path, default=PROYECTO)
    return parser.parse_known_args(argv)[0]
