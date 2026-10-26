"""Segunda puerta: falla si los cambios respecto a <base> tocan ficheros protegidos.

    uv run check <base>

Corre en CI, fuera de la máquina del agente: quien ejecuta no verifica.
"""

import subprocess
import sys

PROTEGIDOS = ("tests/", ".github/")


def main() -> None:
    cambiados = subprocess.run(["git", "diff", "--name-only", sys.argv[1]],
                               capture_output=True, text=True, check=True).stdout.split()
    tocados = [f for f in cambiados if f.startswith(PROTEGIDOS)]

    for f in tocados:
        print(f"Fichero protegido modificado: {f}")
    print("ERROR: cambios en ficheros protegidos." if tocados else "OK: ningún fichero protegido modificado.")
    sys.exit(1 if tocados else 0)
