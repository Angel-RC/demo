# Un prompt no es una puerta: kit de la demo

Demo en vivo (unos 20 minutos) para enseñar que una regla escrita en las instrucciones de
GitHub Copilot es una **petición**, y que para que algo *no pueda* pasar hace falta una
**puerta**: un hook que bloquea la acción y un check en CI fuera del alcance del agente.

Inspirada en [«Un prompt no es una puerta»](https://newsletter.gemba.es/p/un-prompt-no-es-una-puerta)
de José Ramón Pérez Agüera (Gemba).

- **Guion paso a paso:** [GUION.md](GUION.md)
- **Diapositivas:** https://claude.ai/artifact/KbtLKZknJNrH7iRLgf4xGs

## Cómo está montado

Este repo es el **kit del presentador** y Copilot **no debe verlo nunca**: si lee el guion, sabe lo
que va a pasar y se porta bien. Por eso la demo se hace sobre un proyecto aparte:

- `uv run preparar` genera **`../facturacion`**, un proyecto normal (código, tests e instrucciones
  de Copilot) con su propio git y un único commit. **Es lo único que se abre en VS Code.**
- En el acto 1, el proyecto no tiene ningún hook. `uv run puerta on` lo instala en el acto 2.
- Los comandos del presentador (`puerta`, `check`, `reiniciar`) se ejecutan en una terminal aparte,
  en la carpeta de este kit.

| Ruta | Para qué |
|---|---|
| `plantilla/` | El proyecto que se copia a `../facturacion`: `facturacion.py` (IVA del 21 %, descuento máximo del 50 %), `tests/` y `.github/copilot-instructions.md` con la regla en prosa |
| `guardia/proteger_tests.py` | **La puerta**: hook `preToolUse` (unas 45 líneas) que deniega escrituras en `tests/` y en el propio guardia |
| `guardia/proteger-tests.json` | La configuración que le dice a Copilot que ejecute el hook |
| `guardia/ficheros-protegidos.yml` | **Segunda puerta**: workflow de GitHub Actions que falla si un PR toca `tests/` o `.github/` |
| `demo/` | Los comandos del presentador: `preparar`, `puerta`, `check` y `reiniciar` |
| `tests_hook/` | Tests del hook y de los comandos, verificados **por su efecto** (incluido que el proyecto generado no delate la demo) |
| `docs/` | Diseño y plan de la demo |

## Requisitos

- **VS Code** con **GitHub Copilot** (chat en modo *Agent*).
- **Hooks de Copilot** (en *Preview*). En el chat, el control **Session Target** tiene que estar en
  **Copilot**. Los hooks se cargan desde `.github/hooks/*.json` del proyecto abierto.
- **[uv](https://docs.astral.sh/uv/)**. Gestiona Python, el entorno y las dependencias; no hace falta
  instalar Python aparte.
- **git**.

## Instalación

Igual en Linux, macOS y Windows (PowerShell):

```bash
git clone URL_DEL_REPO demo-kit
cd demo-kit
uv sync
uv run preparar
code ../facturacion
```

`preparar` no sobrescribe nada: si `../facturacion` ya existe, se niega. Para otra ubicación, añade
`--proyecto RUTA` a cualquier comando.

## Comandos

En la **terminal del presentador** (carpeta de este kit):

| Qué | Comando |
|---|---|
| Generar el proyecto | `uv run preparar` |
| Activar la puerta | `uv run puerta on` y comprobar en el chat con `/hooks` |
| Desactivar la puerta | `uv run puerta off` |
| ¿Está activa? | `uv run puerta estado` |
| Check de CI en local | `uv run check` |
| Reiniciar el proyecto | `uv run reiniciar` (vuelve al commit inicial: **borra** cualquier cambio en `../facturacion`) |
| Tests del kit | `uv run pytest -q` |

En la **terminal integrada de VS Code** (proyecto `../facturacion`):

| Qué | Comando |
|---|---|
| Tests de negocio (los que ve el público) | `uv run pytest -q` |

Si cambias algo en `plantilla/`, regenera el proyecto: borra `../facturacion` y ejecuta `uv run preparar`.

### Probar el hook a mano (también es el plan B del acto 2)

Desde la carpeta del kit, le pasamos al hook el mismo evento que le enviaría Copilot al intentar
editar un test.

Linux / macOS:

```bash
echo '{"toolName":"edit","toolArgs":{"path":"tests/test_facturacion.py"}}' | uv run --no-project guardia/proteger_tests.py
```

Windows (PowerShell):

```powershell
'{"toolName":"edit","toolArgs":{"path":"tests/test_facturacion.py"}}' | uv run --no-project guardia\proteger_tests.py
```

Resultado esperado:

```json
{"permissionDecision": "deny", "permissionDecisionReason": "tests/ está protegido: ..."}
```

Y uno que debe pasar (ejecutar los tests no es escribir en ellos):

```bash
echo '{"toolName":"run_in_terminal","toolArgs":{"command":"uv run pytest tests/ -q"}}' | uv run --no-project guardia/proteger_tests.py
# {}
```

### Ver qué le llega realmente al hook

Los nombres de las herramientas de Copilot cambian entre versiones. Para ver los eventos reales,
activa la puerta, **cierra VS Code** y ábrelo con la variable `HOOK_LOG=1`; cada evento se añade a
`../facturacion/.github/hooks/hook.log`:

```bash
HOOK_LOG=1 code ../facturacion
```

```powershell
$env:HOOK_LOG = "1"; code ..\facturacion
```

Si aparece una herramienta de lectura o de terminal que no esté en `SOLO_LECTURA` o `TERMINAL`
(en `guardia/proteger_tests.py`), añádela allí y vuelve a ejecutar `uv run puerta on`.

## Checklist antes de la charla (en el PC donde la vas a dar)

Hazla **días antes**, no el mismo día:

1. [ ] `uv --version` funciona en PowerShell, y también desde la terminal integrada de VS Code
       (el hook se lanza con `uv`; si VS Code no lo encuentra en el PATH, el hook falla y **todo**
       queda denegado).
2. [ ] `uv sync`, `uv run pytest -q` (tests del kit) y `uv run preparar`.
3. [ ] En VS Code, con **solo** `../facturacion` abierto: `uv run pytest -q` → `8 passed`.
4. [ ] La prueba a mano del hook devuelve `deny`.
5. [ ] `uv run puerta on` → en el chat, `/hooks` lista el hook. Si no aparece, recarga la
       ventana (*Developer: Reload Window*). Si sigue sin aparecer, puede que la **política de la
       organización** desactive los hooks: usa el plan B del acto 2 y avisa a quien administre Copilot.
6. [ ] Con la puerta activa, pídele al agente «añade una línea en blanco al final de
       tests/test_facturacion.py» → tiene que quedar **denegado**.
7. [ ] **Ensayo completo** con el modelo que vayas a usar en la charla (selector de modelo del chat),
       siguiendo [GUION.md](GUION.md). Ajusta los prompts si hace falta.
8. [ ] **Graba** un ensayo del acto 1 en el que Copilot edite el test (respaldo por si ese día obedece).
9. [ ] `uv run reiniciar` → `Puerta DESACTIVADA`.

## Resolución de problemas

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Copilot menciona la demo, el guion o «la prueba» | Ve el kit: está abierto en la misma ventana o en un workspace multi-carpeta | Abrir **solo** `../facturacion` en VS Code |
| `/hooks` no muestra el hook | Session Target no es Copilot, la ventana no se ha recargado o la política de la organización lo bloquea | Cambiar el Session Target, recargar la ventana o usar el plan B |
| El hook no bloquea nada | La herramienta que usa Copilot tiene un nombre nuevo o sus argumentos no nombran la ruta | Revisar `hook.log` con `HOOK_LOG=1` |
| Todo queda bloqueado | El hook falla al arrancar (por ejemplo, `uv` no está en el PATH de VS Code). Si el hook da error, Copilot **deniega** | Probar el hook a mano desde la terminal integrada de VS Code |
| A veces deja pasar | Si el hook tarda más que `timeoutSec`, Copilot **deja pasar** la acción (fail-open) | Ver si el antivirus ralentiza el arranque; subir `timeoutSec` |
| `uv run preparar` se niega | `../facturacion` ya existe | `uv run reiniciar`, o bórralo y repite |

## Límites conocidos

El hook documenta sus huecos en su cabecera: comandos ofuscados, scripts intermedios y
herramientas que no nombran la ruta. Por eso existe la segunda puerta en CI. Y es parte del
mensaje: un control honesto dice qué no cubre.
