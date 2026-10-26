"""Deja el proyecto como al principio: uv run reiniciar

Vuelve a la etiqueta `inicio` (descarta commits, cambios y ficheros nuevos;
lo ignorado por git, como .venv, se conserva) y desactiva la puerta.
"""

import subprocess

from demo import argumentos, puerta


def main(argv: list[str] | None = None) -> None:
    proyecto = argumentos(argv, "Deja el proyecto de la demo como al principio.").proyecto
    subprocess.run(["git", "-C", str(proyecto), "reset", "-q", "--hard", "inicio"], check=True)
    subprocess.run(["git", "-C", str(proyecto), "clean", "-q", "-fd"], check=True)
    puerta.main(["off", "--proyecto", str(proyecto)])
    print(f"Proyecto reiniciado: {proyecto}")
