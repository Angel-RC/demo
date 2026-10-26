"""Interruptor del hook de la demo: uv run puerta on | off | estado

Copilot carga los ficheros .github/hooks/*.json. La configuración versionada
es proteger-tests.json.off (inactiva); activar = copiarla a proteger-tests.json
(ignorado por git, para que no aparezca como cambio); desactivar = borrar la copia.
"""

import argparse
import shutil
from pathlib import Path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Activa o desactiva la puerta que protege tests/.")
    parser.add_argument("orden", choices=["on", "off", "estado"])
    parser.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)

    hooks = args.raiz / ".github" / "hooks"
    activo = hooks / "proteger-tests.json"
    inactivo = hooks / "proteger-tests.json.off"

    if args.orden == "on" and inactivo.exists():
        shutil.copyfile(inactivo, activo)
    elif args.orden == "off":
        activo.unlink(missing_ok=True)

    if activo.exists():
        print("Puerta ACTIVADA")
        if args.orden == "on":
            print("Compruébalo en el chat de VS Code con /hooks.")
    else:
        print("Puerta DESACTIVADA")
