"""Tests del hook por su efecto: le pasamos eventos y miramos qué decide."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

RUTA_HOOK = Path(__file__).resolve().parent.parent / ".github" / "hooks" / "proteger_tests.py"
_spec = importlib.util.spec_from_file_location("proteger_tests", RUTA_HOOK)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

MOTIVO = (
    "tests/ y .github/hooks/ están protegidos: los tests son la especificación del negocio. "
    "Si crees que hay que cambiar una regla de negocio, detente y pregúntale a la persona."
)


def evento(herramienta, argumentos):
    return {"toolName": herramienta, "toolArgs": argumentos}


DENEGAR = [
    evento("edit", {"path": "tests/test_facturacion.py"}),
    evento("edit", json.dumps({"path": "tests/test_facturacion.py"})),
    evento("create", {"path": "/home/x/demo/tests/nuevo.py"}),
    evento("replace_string_in_file", {"filePath": "C:\\demo\\tests\\test_facturacion.py"}),
    evento("apply_patch", {"input": "*** Update File: tests/test_facturacion.py\n@@\n-0.5\n+0.6"}),
    {"tool_name": "Edit", "tool_input": {"file_path": "tests/x.py"}},
    evento("edit", {"path": ".github/hooks/proteger_tests.py"}),
    evento("bash", {"command": "sed -i 's/0.5/0.6/' tests/test_facturacion.py"}),
    evento("bash", {"command": "echo x > tests/test_facturacion.py"}),
    evento("powershell", {"command": "Set-Content tests\\test_facturacion.py 'x'"}),
    evento("run_in_terminal", {"command": "python scripts/hook.py off"}),
]

PERMITIR = [
    evento("edit", {"path": "facturacion.py"}),
    evento("view", {"path": "tests/test_facturacion.py"}),
    evento("read_file", {"filePath": "tests/test_facturacion.py"}),
    evento("bash", {"command": "pytest tests/ -q"}),
    evento("bash", {"command": "pytest tests/ -q 2>&1"}),
    evento("run_in_terminal", {"command": "python -m pytest tests -q"}),
    evento("edit", {"path": "tests_hook/x.py"}),
    evento("edit", {"path": "mytests/x.py"}),
]


@pytest.mark.parametrize("ev", DENEGAR)
def test_deniega_escrituras_en_rutas_protegidas(ev):
    assert hook.decidir(ev) == {"permissionDecision": "deny", "permissionDecisionReason": MOTIVO}


@pytest.mark.parametrize("ev", PERMITIR)
def test_permite_lo_demas(ev):
    assert hook.decidir(ev) == {}


def ejecutar(entrada):
    r = subprocess.run([sys.executable, str(RUTA_HOOK)], input=entrada,
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, json.loads(r.stdout)


def test_entrada_corrupta_se_deniega():
    codigo, salida = ejecutar("no es json")
    assert codigo == 0
    assert salida["permissionDecision"] == "deny"


def test_extremo_a_extremo_deniega():
    codigo, salida = ejecutar(json.dumps(DENEGAR[0]))
    assert codigo == 0
    assert salida["permissionDecision"] == "deny"


def test_extremo_a_extremo_permite():
    codigo, salida = ejecutar(json.dumps(PERMITIR[0]))
    assert codigo == 0
    assert salida == {}
