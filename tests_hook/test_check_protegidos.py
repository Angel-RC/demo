"""Tests del check de CI de ficheros protegidos."""

import importlib.util
from pathlib import Path

RUTA = Path(__file__).resolve().parent.parent / "scripts" / "check_protegidos.py"
_spec = importlib.util.spec_from_file_location("check_protegidos", RUTA)
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)


def test_detecta_ficheros_protegidos():
    ficheros = ["facturacion.py", "tests/test_facturacion.py", ".github/hooks/x.py"]
    assert check.ficheros_protegidos_tocados(ficheros) == ["tests/test_facturacion.py", ".github/hooks/x.py"]


def test_ignora_lo_demas():
    assert check.ficheros_protegidos_tocados(["facturacion.py", "tests_hook/a.py"]) == []


def test_falla_sin_etiqueta(monkeypatch):
    monkeypatch.setattr(check, "ficheros_cambiados", lambda base: ["tests/test_facturacion.py"])
    monkeypatch.delenv("ETIQUETAS", raising=False)
    assert check.main(["--base", "main"]) == 1


def test_pasa_con_etiqueta(monkeypatch):
    monkeypatch.setattr(check, "ficheros_cambiados", lambda base: ["tests/test_facturacion.py"])
    assert check.main(["--base", "main", "--etiquetas", "cambio-de-especificacion"]) == 0


def test_etiqueta_desde_variable_de_entorno(monkeypatch):
    monkeypatch.setattr(check, "ficheros_cambiados", lambda base: ["tests/test_facturacion.py"])
    monkeypatch.setenv("ETIQUETAS", "bug,cambio-de-especificacion")
    assert check.main(["--base", "main"]) == 0


def test_pasa_sin_ficheros_protegidos(monkeypatch):
    monkeypatch.setattr(check, "ficheros_cambiados", lambda base: ["facturacion.py"])
    monkeypatch.delenv("ETIQUETAS", raising=False)
    assert check.main(["--base", "main"]) == 0
