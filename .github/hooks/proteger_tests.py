"""Hook preToolUse: una PUERTA, no un aviso.

Copilot ejecuta este script antes de usar cada herramienta y le pasa por stdin
un JSON con la herramienta (toolName) y sus argumentos (toolArgs). Si la acción
toca algo protegido, respondemos "deny" y no ocurre, diga lo que diga el prompt.

Huecos conocidos (un control honesto dice qué no cubre):
- Comandos que construyen la ruta a trozos, o scripts intermedios que escriben.
- Un comando de terminal que ejecuta pytest y además escribe en tests/.
- Si este script tarda más que su timeout, Copilot deja pasar la acción.
Por eso hay una segunda puerta en CI (.github/workflows/ficheros-protegidos.yml).
"""

import json
import os
import sys
from pathlib import Path

PROTEGIDOS = ("tests/", ".github/hooks/", "puerta", "reiniciar")
SOLO_LECTURA = {"view", "read_file", "grep", "glob", "list_dir", "file_search", "grep_search"}
TERMINAL = {"bash", "powershell", "run_in_terminal"}

entrada = sys.stdin.buffer.read()
if os.environ.get("HOOK_LOG"):  # para ensayar: ver qué herramientas usa Copilot de verdad
    with open(Path(__file__).with_name("hook.log"), "ab") as log:
        log.write(entrada.strip() + b"\n")
evento = json.loads(entrada)  # si no es JSON, falla, y Copilot deniega
herramienta = evento.get("toolName", "")
argumentos = json.dumps(evento.get("toolArgs", "")).replace("\\\\", "/").lower()  # rutas de Windows

toca_protegido = any(ruta in argumentos for ruta in PROTEGIDOS)
solo_lee = herramienta in SOLO_LECTURA
ejecuta_tests = herramienta in TERMINAL and "pytest" in argumentos

if toca_protegido and not solo_lee and not ejecuta_tests:
    decision = {
        "permissionDecision": "deny",
        "permissionDecisionReason": "tests/ está protegido: los tests son la especificación del negocio. "
        "Si crees que hay que cambiar una regla de negocio, detente y pregúntale a la persona.",
    }
else:
    decision = {}

sys.stdout.reconfigure(encoding="utf-8")
print(json.dumps(decision, ensure_ascii=False))
