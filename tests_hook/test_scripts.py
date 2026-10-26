"""Tests del interruptor del hook."""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INTERRUPTOR = RAIZ / "scripts" / "hook.py"


def interruptor(raiz, orden):
    r = subprocess.run([sys.executable, str(INTERRUPTOR), orden, "--raiz", str(raiz)],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    return r.stdout


def preparar(tmp_path):
    hooks = tmp_path / ".github" / "hooks"
    hooks.mkdir(parents=True)
    (hooks / "proteger-tests.json.off").write_text("{}")
    return hooks


def test_on_activa_el_hook(tmp_path):
    hooks = preparar(tmp_path)
    assert "Hook ACTIVADO" in interruptor(tmp_path, "on")
    assert (hooks / "proteger-tests.json").exists()
    assert not (hooks / "proteger-tests.json.off").exists()


def test_on_dos_veces_no_falla(tmp_path):
    preparar(tmp_path)
    interruptor(tmp_path, "on")
    assert "Hook ACTIVADO" in interruptor(tmp_path, "on")


def test_estado(tmp_path):
    preparar(tmp_path)
    assert "Hook DESACTIVADO" in interruptor(tmp_path, "estado")
    interruptor(tmp_path, "on")
    assert "Hook ACTIVADO" in interruptor(tmp_path, "estado")


def test_off_desactiva_el_hook(tmp_path):
    hooks = preparar(tmp_path)
    interruptor(tmp_path, "on")
    assert "Hook DESACTIVADO" in interruptor(tmp_path, "off")
    assert (hooks / "proteger-tests.json.off").exists()
    assert not (hooks / "proteger-tests.json").exists()
