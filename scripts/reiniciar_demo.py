"""Deja la demo como al principio: python scripts/reiniciar_demo.py [--si]

Vuelve exactamente a la etiqueta git `demo-inicio`: deshace commits, cambios y
ficheros nuevos (los ignorados por git, como .venv, se conservan) y desactiva el hook.
Antes de borrar nada enseña qué se pierde y pide confirmación (--si la omite).

Si cambias el repo a propósito, mueve la etiqueta: git tag -f demo-inicio
"""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, check=True).stdout


def main() -> None:
    commits = git("log", "--oneline", "demo-inicio..HEAD")
    cambios = git("status", "--porcelain")
    if commits or cambios:
        print("Se va a descartar:", flush=True)
        print(commits + cambios, flush=True)
        if "--si" not in sys.argv and input("¿Continuar? [s/N] ").strip().lower() != "s":
            print("Cancelado.")
            return
    git("reset", "--hard", "demo-inicio")
    git("clean", "-fd")
    subprocess.run([sys.executable, str(RAIZ / "scripts" / "hook.py"), "off"], check=True)
    print("Demo reiniciada en demo-inicio.")


if __name__ == "__main__":
    main()
