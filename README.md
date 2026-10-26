# Un prompt no es una puerta: demo de guardarraíles para Copilot

Demo en vivo (unos 20 minutos) para enseñar que una regla escrita en las instrucciones de
GitHub Copilot es una **petición**, y que para que algo *no pueda* pasar hace falta una
**puerta**: un hook que bloquea la acción y un check en CI fuera del alcance del agente.

Inspirada en [«Un prompt no es una puerta»](https://newsletter.gemba.es/p/un-prompt-no-es-una-puerta)
de José Ramón Pérez Agüera (Gemba).

- **Guion paso a paso:** [GUION.md](GUION.md)
- **Diapositivas:** _(enlace pendiente)_

## Qué hay en el repo

| Ruta | Para qué |
|---|---|
| `facturacion.py` | Módulo de ejemplo: total de factura con IVA del 21 % y descuento máximo del 50 % |
| `tests/` | Tests de negocio. **Son la especificación** y están protegidos |
| `.github/copilot-instructions.md` | La regla en prosa: «Nunca modifiques ficheros en `tests/`» |
| `.github/hooks/proteger_tests.py` | **La puerta**: hook `preToolUse` que deniega escrituras en `tests/` y en el propio guardia |
| `.github/hooks/proteger-tests.json.off` | Configuración del hook, **desactivada**. `scripts/hook.py on` la copia a `proteger-tests.json` (ignorado por git), que es el que carga Copilot |
| `scripts/hook.py` | Interruptor: `on`, `off`, `estado` |
| `scripts/reiniciar_demo.py` | Deja el repo como al principio entre ensayos |
| `scripts/check_protegidos.py` | **Segunda puerta**: falla si los cambios tocan `tests/` o `.github/` |
| `.github/workflows/ficheros-protegidos.yml` | Ejecuta esa comprobación en cada PR (GitHub Actions) |
| `tests_hook/` | Tests del hook y de los scripts, verificados **por su efecto** |
| `docs/` | Diseño y plan de la demo |

## Requisitos

- **VS Code** con **GitHub Copilot** (chat en modo *Agent*).
- **Hooks de Copilot** (en *Preview*). En el chat, el control **Session Target** tiene que estar en
  **Copilot**. Los hooks del repositorio se cargan desde `.github/hooks/*.json`.
- **Python ≥ 3.10.** En Linux y macOS se usa `python3`; en Windows, `python`.
- **git** (el reinicio de la demo usa la etiqueta `demo-inicio`).

## Instalación

Linux / macOS:

```bash
git clone <este-repo> demo && cd demo
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
git clone <este-repo> demo; cd demo
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

> En un PC de empresa, `Activate.ps1` suele estar bloqueado por la política de ejecución. No hace
> falta activar el entorno: usa siempre `.venv\Scripts\python -m ...`, como en los ejemplos de abajo.

Abre la carpeta en VS Code (`code .`).

## Uso

En los ejemplos, `python` es `python3` en Linux/macOS, y `.venv\Scripts\python` es `.venv/bin/python`.

| Qué | Comando |
|---|---|
| Tests de negocio (los que ve el público) | `.venv\Scripts\python -m pytest -q` |
| Tests del hook y de los scripts | `.venv\Scripts\python -m pytest tests_hook -q` |
| Activar el hook | `python scripts/hook.py on` y comprobar en el chat con `/hooks` |
| Desactivar el hook | `python scripts/hook.py off` |
| ¿Está activo? | `python scripts/hook.py estado` |
| Reiniciar la demo | `python scripts/reiniciar_demo.py` |
| Check de CI en local | `python scripts/check_protegidos.py --base demo-inicio` |

### Probar el hook a mano (también es el plan B del acto 2)

Le pasamos al hook el mismo evento que le enviaría Copilot al intentar editar un test.

Linux / macOS:

```bash
echo '{"toolName":"edit","toolArgs":{"path":"tests/test_facturacion.py"}}' | python3 .github/hooks/proteger_tests.py
```

Windows (PowerShell):

```powershell
'{"toolName":"edit","toolArgs":{"path":"tests/test_facturacion.py"}}' | python .github\hooks\proteger_tests.py
```

Resultado esperado:

```json
{"permissionDecision": "deny", "permissionDecisionReason": "tests/ y .github/hooks/ están protegidos: ..."}
```

Y uno que debe pasar (ejecutar los tests no es escribir en ellos):

```bash
echo '{"toolName":"bash","toolArgs":{"command":"pytest tests/ -q"}}' | python3 .github/hooks/proteger_tests.py
# {}
```

### Ver qué le llega realmente al hook

Los nombres de las herramientas de Copilot cambian entre versiones. Para ver los eventos reales,
arranca VS Code con la variable `HOOK_LOG=1` y cada evento se añade a `.github/hooks/hook.log`:

```bash
HOOK_LOG=1 code .
```

```powershell
$env:HOOK_LOG = "1"; code .
```

Si aparece una herramienta de lectura o de terminal que no esté en `LECTURA` o `TERMINAL`
(en `proteger_tests.py`), añádela allí.

## Checklist antes de la charla (en el PC donde la vas a dar)

Hazla **días antes**, no el mismo día:

1. [ ] `python --version` funciona en PowerShell (si solo funciona `py`, cambia `"powershell"`
       en `.github/hooks/proteger-tests.json.off` a `py .github/hooks/proteger_tests.py`).
2. [ ] Instalación y `.venv\Scripts\python -m pytest -q` → `6 passed`.
3. [ ] La prueba a mano del hook devuelve `deny`.
4. [ ] `python scripts/hook.py on` → en el chat, `/hooks` lista el hook. Si no aparece, recarga la
       ventana (*Developer: Reload Window*). Si sigue sin aparecer, puede que la **política de la
       organización** desactive los hooks: usa el plan B del acto 2 y avisa a quien administre Copilot.
5. [ ] Con el hook activo, pídele al agente «añade una línea en blanco al final de
       tests/test_facturacion.py» → tiene que quedar **denegado**.
6. [ ] **Ensayo completo** con el modelo que vayas a usar en la charla (selector de modelo del chat),
       siguiendo [GUION.md](GUION.md). Ajusta los prompts si hace falta.
7. [ ] **Graba** un ensayo del acto 1 en el que Copilot edite el test (respaldo por si ese día obedece).
8. [ ] `python scripts/reiniciar_demo.py` y `python scripts/hook.py estado` → `Hook DESACTIVADO`.

## Resolución de problemas

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `/hooks` no muestra el hook | Session Target no es Copilot, la ventana no se ha recargado o la política de la organización lo bloquea | Cambiar el Session Target, recargar la ventana o usar el plan B |
| El hook no bloquea nada | La herramienta que usa Copilot tiene un nombre nuevo o sus argumentos no nombran la ruta | Revisar `hook.log` con `HOOK_LOG=1` |
| Todo queda bloqueado | El hook falla al arrancar (por ejemplo, `python` no encontrado). Si el hook da error, Copilot **deniega** | Probar el hook a mano desde la terminal |
| A veces deja pasar | Si el hook tarda más que `timeoutSec`, Copilot **deja pasar** la acción (fail-open) | Ver si el antivirus ralentiza el arranque de Python; subir `timeoutSec` |
| `pytest` no encuentra `facturacion` | Se ejecuta desde otra carpeta | Ejecutar desde la raíz del repo |
| `reiniciar_demo.py` falla | No existe la etiqueta `demo-inicio` | `git tag demo-inicio <commit-inicial-de-la-demo>` |

## Límites conocidos

El hook documenta sus huecos en su cabecera: comandos ofuscados, scripts intermedios y
herramientas que no nombran la ruta. Por eso existe la segunda puerta en CI. Y es parte del
mensaje: un control honesto dice qué no cubre.
