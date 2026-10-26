"""Deja la demo como al principio: uv run reiniciar

Vuelve a la etiqueta git `demo-inicio` (descarta commits, cambios y ficheros
nuevos; lo ignorado por git, como .venv, se conserva) y desactiva la puerta.
Si cambias el repo a propósito, mueve la etiqueta: git tag -f demo-inicio
"""

import subprocess

from demo import puerta


def main() -> None:
    subprocess.run(["git", "reset", "--hard", "demo-inicio"], check=True)
    subprocess.run(["git", "clean", "-fd"], check=True)
    puerta.main(["off"])
