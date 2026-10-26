"""Tests del interruptor de la puerta (uv run puerta on|off|estado)."""

from demo import puerta


def test_on_y_off(tmp_path, capsys):
    hooks = tmp_path / ".github" / "hooks"
    hooks.mkdir(parents=True)
    (hooks / "proteger-tests.json.off").write_text("{}")

    puerta.main(["on", "--raiz", str(tmp_path)])
    assert "ACTIVADA" in capsys.readouterr().out
    assert (hooks / "proteger-tests.json").exists()

    puerta.main(["off", "--raiz", str(tmp_path)])
    assert "DESACTIVADA" in capsys.readouterr().out
    assert not (hooks / "proteger-tests.json").exists()
