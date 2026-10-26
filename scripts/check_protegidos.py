"""Segunda puerta: falla si los cambios tocan ficheros protegidos.

    python scripts/check_protegidos.py --base <rama-o-etiqueta> [--etiquetas a,b]

Corre en CI, fuera de la máquina del agente: quien ejecuta no verifica.
La vía legítima para cambiar tests/ es que una persona ponga al PR la
etiqueta `cambio-de-especificacion`.
"""

import argparse
import os
import subprocess

PROTEGIDOS = ("tests/", ".github/")
ETIQUETA_APROBACION = "cambio-de-especificacion"


def ficheros_protegidos_tocados(ficheros: list[str], prefijos: tuple[str, ...] = PROTEGIDOS) -> list[str]:
    return [f for f in ficheros if f.replace("\\", "/").startswith(prefijos)]


def _git(*args: str) -> list[str]:
    salida = subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout
    return [linea for linea in salida.splitlines() if linea]


def ficheros_cambiados(base: str) -> list[str]:
    """Cambios respecto a `base`, incluidos los que aún no se han commiteado."""
    cambiados = _git("diff", "--name-only", f"{base}...HEAD")
    cambiados += _git("diff", "--name-only", "HEAD")
    cambiados += _git("ls-files", "--others", "--exclude-standard")
    return sorted(set(cambiados))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True)
    parser.add_argument("--etiquetas", default=os.environ.get("ETIQUETAS", ""))
    args = parser.parse_args(argv)

    tocados = ficheros_protegidos_tocados(ficheros_cambiados(args.base))
    if not tocados:
        print("OK: no se ha tocado ningún fichero protegido.")
        return 0
    if ETIQUETA_APROBACION in args.etiquetas.split(","):
        print(f"OK: se tocan ficheros protegidos, pero una persona lo aprobó ({ETIQUETA_APROBACION}).")
        return 0
    print("ERROR: estos cambios tocan ficheros protegidos:")
    for f in tocados:
        print(f"  - {f}")
    print(f"Si el cambio de especificación es intencionado, una persona debe añadir la etiqueta '{ETIQUETA_APROBACION}'.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
