"""Segunda puerta, en local: uv run check

La misma regla que guardia/ficheros-protegidos.yml aplicaría en CI: falla si
los cambios del proyecto respecto a `inicio` tocan ficheros protegidos.
"""

import subprocess

from demo import argumentos

PROTEGIDOS = ("tests/", ".github/")


def main(argv: list[str] | None = None) -> int:
    proyecto = argumentos(argv, "Comprueba si se han tocado ficheros protegidos.").proyecto
    cambiados = subprocess.run(["git", "-C", str(proyecto), "diff", "--name-only", "inicio"],
                               capture_output=True, text=True, check=True).stdout.split()
    tocados = [f for f in cambiados if f.startswith(PROTEGIDOS)]

    for f in tocados:
        print(f"Fichero protegido modificado: {f}")
    print("ERROR: cambios en ficheros protegidos." if tocados else "OK: ningún fichero protegido modificado.")
    return 1 if tocados else 0  # código de salida
