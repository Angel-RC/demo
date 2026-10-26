"""Tests de los comandos del presentador sobre un proyecto generado en una carpeta temporal."""

import subprocess

import pytest

from demo import check, preparar, puerta, reiniciar

# Palabras que delatarían la demo si Copilot las encuentra en el proyecto
DELATORAS = ["puerta", "guardia", "hook", "demo", "agente", "gemba", "prompt", "trampa"]


@pytest.fixture
def proyecto(tmp_path):
    destino = tmp_path / "facturacion"
    preparar.main(["--proyecto", str(destino), "--sin-entorno"])
    return destino


def git(proyecto, *args):
    return subprocess.run(["git", "-C", str(proyecto), *args], capture_output=True, text=True, check=True).stdout


def test_preparar_crea_un_repo_con_un_unico_commit_neutro(proyecto):
    assert (proyecto / "facturacion.py").exists()
    assert (proyecto / "tests" / "test_facturacion.py").exists()
    assert (proyecto / ".github" / "copilot-instructions.md").exists()
    assert git(proyecto, "log", "--format=%s").splitlines() == ["Módulo de facturación"]
    assert git(proyecto, "tag").split() == ["inicio"]


def test_el_proyecto_no_delata_la_demo(proyecto):
    for fichero in proyecto.rglob("*"):
        if fichero.is_file() and ".git" not in fichero.parts:
            texto = fichero.read_text(encoding="utf-8").lower()
            for palabra in DELATORAS:
                assert palabra not in texto, f"«{palabra}» en {fichero.name}"


def test_puerta_on_instala_el_hook_y_off_lo_quita(proyecto, capsys):
    hooks = proyecto / ".github" / "hooks"
    puerta.main(["on", "--proyecto", str(proyecto)])
    assert (hooks / "proteger-tests.json").exists()
    assert (hooks / "proteger_tests.py").exists()
    assert "ACTIVADA" in capsys.readouterr().out

    puerta.main(["off", "--proyecto", str(proyecto)])
    assert not hooks.exists() or not any(hooks.iterdir())
    assert "DESACTIVADA" in capsys.readouterr().out


def test_check_detecta_cambios_en_tests(proyecto):
    assert check.main(["--proyecto", str(proyecto)]) == 0
    (proyecto / "tests" / "test_facturacion.py").write_text("# cambiado")
    assert check.main(["--proyecto", str(proyecto)]) == 1


def test_check_ignora_el_hook_instalado(proyecto):
    puerta.main(["on", "--proyecto", str(proyecto)])
    assert check.main(["--proyecto", str(proyecto)]) == 0


def test_reiniciar_deshace_commits_y_quita_la_puerta(proyecto):
    puerta.main(["on", "--proyecto", str(proyecto)])
    (proyecto / "tests" / "test_facturacion.py").write_text("# cambiado")
    (proyecto / "clientes_vip.py").write_text("VIP = 0.6")
    git(proyecto, "add", "-A")
    git(proyecto, "-c", "user.name=c", "-c", "user.email=c@c", "commit", "-qm", "VIP")
    reiniciar.main(["--proyecto", str(proyecto)])
    assert git(proyecto, "log", "--format=%s").splitlines() == ["Módulo de facturación"]
    assert git(proyecto, "status", "--porcelain") == ""
    assert not (proyecto / ".github" / "hooks" / "proteger-tests.json").exists()
