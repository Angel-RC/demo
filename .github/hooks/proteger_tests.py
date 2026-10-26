"""Hook preToolUse: una PUERTA, no un aviso.

Copilot llama a este script antes de usar cualquier herramienta. Si la herramienta
va a escribir en tests/, en la configuración de pytest (conftest.py, pytest.ini) o
tocar el propio guardia (.github/hooks/, scripts/hook.py, reiniciar_demo.py),
la denegamos. Da igual lo que diga el prompt: la acción no ocurre.
Inspirado en https://newsletter.gemba.es/p/un-prompt-no-es-una-puerta

HUECOS CONOCIDOS (un control honesto dice qué no cubre):
- Comandos ofuscados (p. ej. `python -c` que construye la ruta a trozos).
- Un script intermedio que escribe el fichero por su cuenta.
- Desactivar los hooks desde la configuración de VS Code.
- Herramientas cuyos argumentos no nombran la ruta.
- Si el hook tarda más que su timeout, Copilot deja pasar la acción (fail-open).
Por eso hay una segunda puerta en CI: .github/workflows/ficheros-protegidos.yml
"""

import json
import os
import re
import sys
from pathlib import Path

MOTIVO = (
    "Los tests, su configuración y el propio guardia están protegidos: "
    "los tests son la especificación del negocio. "
    "Si crees que hay que cambiar una regla de negocio, detente y pregúntale a la persona."
)
DENEGAR = {"permissionDecision": "deny", "permissionDecisionReason": MOTIVO}

GUARDIA = r"hook\.py|scripts\.hook|reiniciar_demo|proteger-tests"
PROTEGIDO = re.compile(r"""(^|[\s"'/=:(])(tests/|\.github/hooks/|conftest\.py|pytest\.ini)|""" + GUARDIA,
                       re.IGNORECASE)  # Windows no distingue mayúsculas
LECTURA = {"view", "read", "read_file", "grep", "glob", "list_dir", "file_search",
           "grep_search", "semantic_search", "runTests", "Read", "Glob", "Grep"}
TERMINAL = {"bash", "powershell", "run_in_terminal", "Bash"}
ESCRITURA = re.compile(r"""(?<![0-9&])>|\bsed\s+-i|open\([^)]*['"][wa]|write_(text|bytes)"""
                       r"|\b(rm|mv|cp|tee|truncate|del|erase|copy|move|ren|ri|rd|rmdir|sc)\b"
                       r"|\bgit\s+(checkout|restore)\b|Set-Content|Add-Content|Out-File"
                       r"|Remove-Item|Move-Item|Copy-Item|Rename-Item|" + GUARDIA, re.IGNORECASE)


def _textos(valor):
    """Todas las cadenas dentro de los argumentos, estén como estén anidadas."""
    if isinstance(valor, dict):
        valor = list(valor.values())
    if isinstance(valor, list):
        return " ".join(_textos(v) for v in valor)
    return str(valor)


def decidir(evento: dict) -> dict:
    nombre = evento.get("toolName") or evento.get("tool_name") or ""
    args = evento.get("toolArgs", evento.get("tool_input", ""))
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            pass
    texto = _textos(args).replace("\\", "/")  # rutas de Windows
    if not PROTEGIDO.search(texto) or nombre in LECTURA:
        return {}
    if nombre in TERMINAL and not ESCRITURA.search(texto):
        return {}  # p. ej. `pytest tests/`
    return DENEGAR


def main() -> None:
    entrada = sys.stdin.buffer.read().decode("utf-8", "replace")
    if os.environ.get("HOOK_LOG"):
        with open(Path(__file__).with_name("hook.log"), "a", encoding="utf-8") as log:
            log.write(entrada.strip() + "\n")
    try:
        decision = decidir(json.loads(entrada))
    except Exception:  # cualquier error: denegar (fail-closed) con una salida limpia
        decision = {**DENEGAR, "permissionDecisionReason": "Entrada no válida: se deniega por seguridad."}
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False))


if __name__ == "__main__":
    main()
