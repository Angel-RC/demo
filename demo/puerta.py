"""Interruptor de la puerta: uv run puerta on | off | estado

on copia el hook de guardia/ a .github/hooks/ del proyecto (Copilot lo carga
desde ahí); off lo borra. En el acto 1 el proyecto no tiene ni rastro del hook.
"""

import shutil

from demo import GUARDIA, argumentos

FICHEROS = ("proteger-tests.json", "proteger_tests.py")


def main(argv: list[str] | None = None) -> None:
    args = argumentos(argv, "Activa o desactiva la puerta que protege tests/.", "on", "off", "estado")
    hooks = args.proyecto / ".github" / "hooks"

    if args.orden == "on":
        hooks.mkdir(parents=True, exist_ok=True)
        for nombre in FICHEROS:
            shutil.copyfile(GUARDIA / nombre, hooks / nombre)
    elif args.orden == "off":
        for nombre in (*FICHEROS, "hook.log"):
            (hooks / nombre).unlink(missing_ok=True)

    if (hooks / "proteger-tests.json").exists():
        print("Puerta ACTIVADA")
        if args.orden == "on":
            print("Compruébalo en el chat de VS Code con /hooks.")
    else:
        print("Puerta DESACTIVADA")
