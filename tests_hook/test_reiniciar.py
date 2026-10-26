"""El reinicio deja la demo exactamente en `demo-inicio`, aunque Copilot haya hecho commits."""

import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout


def test_reinicio_deshace_commits_y_ficheros_nuevos(tmp_path):
    repo = tmp_path / "demo"
    shutil.copytree(RAIZ, repo, ignore=shutil.ignore_patterns(".venv"))
    # La copia incluye el código actual (quizá sin commitear): fijarlo como estado inicial
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=c", "-c", "user.email=c@c", "commit", "-q", "--allow-empty", "-m", "inicio")
    git(repo, "tag", "-f", "demo-inicio")
    inicio = git(repo, "rev-parse", "HEAD").strip()
    # Lo que haría Copilot: tocar el test y el código, commitear y dejar ficheros nuevos
    (repo / "tests" / "test_facturacion.py").write_text("# trampa")
    (repo / "clientes_vip.py").write_text("VIP = 0.6")
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=c", "-c", "user.email=c@c", "commit", "-qm", "trampa")
    (repo / "README.md").write_text("cambiado")
    (repo / "tests" / "test_nuevo.py").write_text("")
    subprocess.run([sys.executable, str(repo / "scripts" / "reiniciar_demo.py"), "--si"],
                   cwd=repo, check=True, capture_output=True)
    assert git(repo, "rev-parse", "HEAD").strip() == inicio
    assert git(repo, "status", "--porcelain") == ""
