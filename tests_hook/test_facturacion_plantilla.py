"""Los tests de negocio de la plantilla pasan (el estado del que parte el acto 1)."""

import subprocess
import sys
from pathlib import Path

PLANTILLA = Path(__file__).resolve().parent.parent / "plantilla"


def test_tests_de_negocio_en_verde():
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                       cwd=PLANTILLA, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout
    assert "6 passed" in r.stdout
