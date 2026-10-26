# Un prompt no es una puerta: demo de guardarraíles para Copilot

Demo en vivo (unos 20 minutos) para enseñar que una regla escrita en las instrucciones de
GitHub Copilot es una **petición**, y que para que algo *no pueda* pasar hace falta una
**puerta**: un hook que bloquea la acción y un check en CI fuera del alcance del agente.

Inspirada en [«Un prompt no es una puerta»](https://newsletter.gemba.es/p/un-prompt-no-es-una-puerta)
de José Ramón Pérez Agüera (Gemba).

- **Guion paso a paso:** [GUION.md](GUION.md)
- **Diapositivas:** https://claude.ai/artifact/KbtLKZknJNrH7iRLgf4xGs

## Qué hay en el repo

| Ruta | Para qué |
|---|---|
| `facturacion.py` | Módulo de ejemplo: total de factura con IVA del 21 % y descuento máximo del 50 % |
| `tests/` | Tests de negocio. **Son la especificación** y están protegidos |
| `.github/copilot-instructions.md` | La regla en prosa: «Nunca modifiques ficheros en `tests/`» |
| `.github/hooks/proteger_tests.py` | **La puerta**: hook `preToolUse` (unas 45 líneas) que deniega escrituras en `tests/` y en el propio guardia |
| `.github/hooks/proteger-tests.json.off` | Configuración del hook, **desactivada**. `uv run puerta on` la copia a `proteger-tests.json` (ignorado por git), que es el que carga Copilot |
| `demo/` | Los comandos de la demo: `puerta`, `check` y `reiniciar` |
| `.github/workflows/ficheros-protegidos.yml` | **Segunda puerta**: en cada PR, falla si se tocan `tests/` o `.github/` |
| `tests_hook/` | Tests del hook y del interruptor, verificados **por su efecto** |
| `pyproject.toml` | Proyecto uv: dependencias y atajos (`[project.scripts]`) |
| `docs/` | Diseño y plan de la demo |

## Requisitos

- **VS Code** con **GitHub Copilot** (chat en modo *Agent*).
- **Hooks de Copilot** (en *Preview*). En el chat, el control **Session Target** tiene que estar en
  **Copilot**. Los hooks del repositorio se cargan desde `.github/hooks/*.json`.
- **[uv](https://docs.astral.sh/uv/)**. Gestiona Python, el entorno y las dependencias; no hace falta
  instalar Python aparte.
- **git** (el reinicio de la demo usa la etiqueta `demo-inicio`).

## Instalación

Igual en Linux, macOS y Windows (PowerShell):

```bash
git clone URL_DEL_REPO demo
cd demo
uv sync
code .
```

## Comandos

Todos se ejecutan desde la raíz del repo y son iguales en todos los sistemas.

| Qué | Comando |
|---|---|
| Tests de negocio (los que ve el público) | `uv run pytest -q` |
| Tests del hook y del interruptor | `uv run pytest tests_hook -q` |
| Activar la puerta | `uv run puerta on` y comprobar en el chat con `/hooks` |
| Desactivar la puerta | `uv run puerta off` |
| ¿Está activa? | `uv run puerta estado` |
| Check de CI en local | `uv run check demo-inicio` |
| Reiniciar la demo | `uv run reiniciar` (**borra** todo lo posterior a `demo-inicio`; si cambias el repo a propósito, `git tag -f demo-inicio`) |

Los atajos `puerta`, `check` y `reiniciar` están definidos en `[project.scripts]` de `pyproject.toml`.

### Probar el hook a mano (también es el plan B del acto 2)

Le pasamos al hook el mismo evento que le enviaría Copilot al intentar editar un test.

Linux / macOS:

```bash
echo '{"toolName":"edit","toolArgs":{"path":"tests/test_facturacion.py"}}' | uv run --no-project .github/hooks/proteger_tests.py
```

Windows (PowerShell):

```powershell
'{"toolName":"edit","toolArgs":{"path":"tests/test_facturacion.py"}}' | uv run --no-project .github\hooks\proteger_tests.py
```

Resultado esperado:

```json
{"permissionDecision": "deny", "permissionDecisionReason": "tests/ está protegido: ..."}
```

Y uno que debe pasar (ejecutar los tests no es escribir en ellos):

```bash
echo '{"toolName":"run_in_terminal","toolArgs":{"command":"uv run pytest tests/ -q"}}' | uv run --no-project .github/hooks/proteger_tests.py
# {}
```

### Ver qué le llega realmente al hook

Los nombres de las herramientas de Copilot cambian entre versiones. Para ver los eventos reales,
**cierra VS Code** y ábrelo con la variable `HOOK_LOG=1`; cada evento se añade a `.github/hooks/hook.log`:

```bash
HOOK_LOG=1 code .
```

```powershell
$env:HOOK_LOG = "1"; code .
```

Si aparece una herramienta de lectura o de terminal que no esté en `SOLO_LECTURA` o `TERMINAL`
(en `proteger_tests.py`), añádela allí.

## Checklist antes de la charla (en el PC donde la vas a dar)

Hazla **días antes**, no el mismo día:

1. [ ] `uv --version` funciona en PowerShell, y también desde la terminal integrada de VS Code
       (el hook se lanza con `uv`; si VS Code no lo encuentra en el PATH, el hook falla y **todo**
       queda denegado).
2. [ ] `uv sync` y `uv run pytest -q` → `6 passed`.
3. [ ] La prueba a mano del hook devuelve `deny`.
4. [ ] `uv run puerta on` → en el chat, `/hooks` lista el hook. Si no aparece, recarga la
       ventana (*Developer: Reload Window*). Si sigue sin aparecer, puede que la **política de la
       organización** desactive los hooks: usa el plan B del acto 2 y avisa a quien administre Copilot.
5. [ ] Con la puerta activa, pídele al agente «añade una línea en blanco al final de
       tests/test_facturacion.py» → tiene que quedar **denegado**.
6. [ ] **Ensayo completo** con el modelo que vayas a usar en la charla (selector de modelo del chat),
       siguiendo [GUION.md](GUION.md). Ajusta los prompts si hace falta.
7. [ ] **Graba** un ensayo del acto 1 en el que Copilot edite el test (respaldo por si ese día obedece).
8. [ ] `uv run reiniciar` → `Puerta DESACTIVADA`.

## Resolución de problemas

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `/hooks` no muestra el hook | Session Target no es Copilot, la ventana no se ha recargado o la política de la organización lo bloquea | Cambiar el Session Target, recargar la ventana o usar el plan B |
| El hook no bloquea nada | La herramienta que usa Copilot tiene un nombre nuevo o sus argumentos no nombran la ruta | Revisar `hook.log` con `HOOK_LOG=1` |
| Todo queda bloqueado | El hook falla al arrancar (por ejemplo, `uv` no está en el PATH de VS Code). Si el hook da error, Copilot **deniega** | Probar el hook a mano desde la terminal integrada de VS Code |
| A veces deja pasar | Si el hook tarda más que `timeoutSec`, Copilot **deja pasar** la acción (fail-open) | Ver si el antivirus ralentiza el arranque; subir `timeoutSec` |
| `uv run reiniciar` falla | No existe la etiqueta `demo-inicio` | `git tag demo-inicio <commit-inicial-de-la-demo>` |

## Límites conocidos

El hook documenta sus huecos en su cabecera: comandos ofuscados, scripts intermedios y
herramientas que no nombran la ruta. Por eso existe la segunda puerta en CI. Y es parte del
mensaje: un control honesto dice qué no cubre.
