"""Deja la demo como al principio: python scripts/reiniciar_demo.py

Restaura facturacion.py y tests/ desde la etiqueta git `demo-inicio`,
borra ficheros nuevos en tests/ y desactiva el hook.
"""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def git(*args: str) -> None:
    print("$ git " + " ".join(args))
    subprocess.run(["git", *args], cwd=RAIZ, check=True)


def main() -> None:
    git("restore", "--source", "demo-inicio", "--staged", "--worktree", "--", "facturacion.py", "tests/")
    git("clean", "-fd", "--", "tests/")
    subprocess.run([sys.executable, str(RAIZ / "scripts" / "hook.py"), "off"], check=True)
    print("Demo reiniciada.")


if __name__ == "__main__":
    main()
