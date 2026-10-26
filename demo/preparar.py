"""Genera el proyecto de la demo: uv run preparar

Copia plantilla/ a ../facturacion con un repo git propio (un único commit y la
etiqueta `inicio`), sin rastro de la demo: es lo único que Copilot debe ver.
"""

import shutil
import subprocess
import sys

from demo import PLANTILLA, argumentos


def main(argv: list[str] | None = None) -> None:
    destino = argumentos(argv, "Genera el proyecto de la demo.").proyecto
    if destino.exists():
        sys.exit(f"{destino} ya existe. Para empezar de cero: uv run reiniciar (o bórralo y repite).")

    shutil.copytree(PLANTILLA, destino, ignore=shutil.ignore_patterns(".venv", "__pycache__", ".pytest_cache"))
    git = ["git", "-C", str(destino), "-c", "user.name=Equipo de facturación", "-c", "user.email=facturacion@example.com"]
    subprocess.run([*git, "init", "-q", "-b", "main"], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "Módulo de facturación"], check=True)
    subprocess.run([*git, "tag", "inicio"], check=True)
    if "--sin-entorno" not in (argv or sys.argv):
        subprocess.run(["uv", "sync", "-q"], cwd=destino, check=True)
    print(f"Proyecto listo en {destino}\nÁbrelo en VS Code: code {destino}")
