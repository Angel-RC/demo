"""Interruptor del hook de la demo: python scripts/hook.py on|off|estado

Copilot carga los ficheros .github/hooks/*.json. Para desactivar el hook
lo renombramos a .json.off; para activarlo, al revés.
"""

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Activa o desactiva el hook que protege tests/.")
    parser.add_argument("orden", choices=["on", "off", "estado"])
    parser.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    hooks = args.raiz / ".github" / "hooks"
    activo = hooks / "proteger-tests.json"
    inactivo = hooks / "proteger-tests.json.off"

    if args.orden == "on" and inactivo.exists():
        inactivo.rename(activo)
    elif args.orden == "off" and activo.exists():
        activo.rename(inactivo)

    if activo.exists():
        print("Hook ACTIVADO")
        if args.orden == "on":
            print("Compruébalo en el chat de VS Code con /hooks.")
    else:
        print("Hook DESACTIVADO")


if __name__ == "__main__":
    main()
