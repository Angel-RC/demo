"""Tests del hook por su efecto: le pasamos eventos como los de Copilot y miramos qué decide."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent.parent / ".github" / "hooks" / "proteger_tests.py"


def decidir(herramienta, argumentos):
    entrada = json.dumps({"toolName": herramienta, "toolArgs": argumentos})
    r = subprocess.run([sys.executable, str(HOOK)], input=entrada.encode(), capture_output=True)
    return json.loads(r.stdout).get("permissionDecision")


@pytest.mark.parametrize("herramienta, argumentos", [
    ("edit", {"path": "tests/test_facturacion.py"}),
    ("create_file", {"filePath": "C:\\demo\\tests\\test_nuevo.py"}),
    ("replace_string_in_file", {"filePath": "tests/test_facturacion.py", "newString": "import pytest"}),
    ("run_in_terminal", {"command": "sed -i 's/0.5/0.6/' tests/test_facturacion.py"}),
    ("edit", {"path": ".github/hooks/proteger_tests.py"}),
    ("run_in_terminal", {"command": "uv run puerta off"}),
    ("run_in_terminal", {"command": "uv run reiniciar"}),
])
def test_deniega(herramienta, argumentos):
    assert decidir(herramienta, argumentos) == "deny"


@pytest.mark.parametrize("herramienta, argumentos", [
    ("edit", {"path": "facturacion.py"}),
    ("read_file", {"filePath": "tests/test_facturacion.py"}),
    ("run_in_terminal", {"command": "python -m pytest tests/ -q"}),
])
def test_permite(herramienta, argumentos):
    assert decidir(herramienta, argumentos) is None


def test_entrada_corrupta_falla():
    """Si el hook falla, Copilot deniega la acción (fail-closed)."""
    r = subprocess.run([sys.executable, str(HOOK)], input=b"no es json", capture_output=True)
    assert r.returncode != 0


def test_hook_log_registra_los_eventos():
    log = HOOK.with_name("hook.log")
    log.unlink(missing_ok=True)
    entrada = json.dumps({"toolName": "view", "toolArgs": {}}).encode()
    subprocess.run([sys.executable, str(HOOK)], input=entrada, capture_output=True,
                   env={**os.environ, "HOOK_LOG": "1"})
    assert '"view"' in log.read_text()
    log.unlink()
