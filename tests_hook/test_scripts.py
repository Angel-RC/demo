"""Tests del interruptor del hook."""

import subprocess
import sys
from pathlib import Path

INTERRUPTOR = Path(__file__).resolve().parent.parent / "scripts" / "hook.py"


def interruptor(raiz, orden):
    r = subprocess.run([sys.executable, str(INTERRUPTOR), orden, "--raiz", str(raiz)],
                       capture_output=True, text=True, encoding="utf-8", check=True)
    return r.stdout


def test_on_y_off(tmp_path):
    hooks = tmp_path / ".github" / "hooks"
    hooks.mkdir(parents=True)
    (hooks / "proteger-tests.json.off").write_text("{}")

    assert "ACTIVADO" in interruptor(tmp_path, "on")
    assert (hooks / "proteger-tests.json").exists()

    assert "DESACTIVADO" in interruptor(tmp_path, "off")
    assert not (hooks / "proteger-tests.json").exists()
