# Phase 6.1 — `make_gif_chart` nach `lib/plotting.py`

Erster Lib-Migration-Schritt aus Phase 6. `make_gif_chart` war **identisch
dupliziert** in K_01 und K_04 (~95 % Übereinstimmung, nur Docstring und
Formatting-Details unterschiedlich). Jetzt zentral in `lib/plotting.py`.

## Änderungen

### 1. `lib/plotting.py` erweitert

Neue Funktion:

```python
def make_gif_chart(fig, update_fn, frames, fps, path,
                   dpi=None, save_frames=None, cfg=None):
    """PIL-basierter GIF-Builder für animierte Charts."""
```

**Neue CFG-Integration:** Wenn `cfg` übergeben wird, zieht die Funktion
`dpi`- und `einzelbilder`-Defaults aus `cfg['animation']` und macht den
Skip-Check via `should_skip()` automatisch.

Ohne `cfg` (Rückwärtskompatibilität): Standard-Defaults (dpi=110,
save_frames=False), kein Skip-Check.

### 2. Helper-Zellen in K_01 und K_04 geschrumpft

Die lokalen `def make_gif_chart(...)`-Duplikate (~35 Zeilen) sind raus. Was
bleibt, ist **echter NB-spezifischer Code** — 4 Zeilen pro NB:

**K_01 Cell 12:**
```python
import numpy as _np_k1
from scipy.interpolate import CubicSpline as _CS_k1

HOUR_TIMES = _np_k1.linspace(0, 24, N_FRAMES_HOUR, endpoint=False)

def make_spline_h24(values_24):
    '''Cubic-Spline für 24h-Daten (periodisch).'''
    h = _np_k1.arange(25)
    v = _np_k1.array(list(values_24) + [values_24[0]])
    return _CS_k1(h, v, bc_type='periodic')
```

**K_04 Cell 12:**
```python
import numpy as _np
from scipy.interpolate import CubicSpline as _CS

WEEK_TIMES = _np.linspace(1.0, 52.0, N_FRAMES_WEEK, endpoint=True)

def make_spline_w4(weeks_arr, values_arr, extrapolate=False):
    '''Cubic-Spline über wöchentliche Datenpunkte.'''
    return _CS(weeks_arr, values_arr, extrapolate=extrapolate)
```

Überflüssige `_io` und `_PILImage`-Imports wurden entfernt (wurden nur für
`make_gif_chart` gebraucht, das nun in lib ist).

### 3. Bootstrap erweitert

In beiden NBs:

```python
from lib.plotting import show_source, should_skip, make_gif_chart
```

### 4. `show_source`-Block kombiniert

Statt zwei getrennter Blöcke (einer für `should_skip`, einer für `make_gif_chart`)
jetzt ein **zusammenhängender Block** vor der Helper-Zelle:

```markdown
**🔎 Quellcode der importierten lib-Funktionen**

Die Funktionen `should_skip` und `make_gif_chart` werden aus
`lib/plotting.py` importiert und in den folgenden Zellen verwendet.
...
```

```python
show_source(should_skip)
show_source(make_gif_chart)
```

### 5. Aufrufstellen: `cfg=CFG` ergänzt

| NB | Aufrufe |
|---|---:|
| K_01 | 1 (Cell 77) |
| K_04 | 3 (Cells 20, 22, 24) |

Minimal-invasiv: nur `, cfg=CFG` am Ende jedes Calls ergänzt. Dadurch funktioniert
der Skip-Check in der neuen lib-Variante identisch zur bisherigen lokalen
Version.

## Migration von NBs mit eigenem `make_gif_*`

**Explizit nicht migriert:** `make_gif_fast` (K_01c) und `make_gif_fast_d` (K_01d)
bleiben lokal, weil sie NB-spezifische Sachen machen (eigenen
Hintergrund-Renderer für Zonenfüllung bzw. Netzwerkgraph). Die Skip-Logik
dort läuft über Phase-4c-Einbau direkt im lokalen Helper.

Wenn sich später herauskristallisiert, dass `make_gif_fast` und `make_gif_fast_d`
ein gemeinsames Interface haben, können sie ebenfalls zusammengezogen werden —
aktuell kein Zwang.

## Qualitäts-Checks (alle ✅)

| Check | Status |
|---|---|
| `lib/plotting.py` syntaktisch valide (ast.parse) | ✅ |
| `from lib.plotting import make_gif_chart` funktioniert | ✅ |
| K_01 Helper-Zelle frei von `def make_gif_chart` | ✅ |
| K_04 Helper-Zelle frei von `def make_gif_chart` | ✅ |
| K_01 Call hat `cfg=CFG` | ✅ |
| K_04: alle 3 Calls haben `cfg=CFG` | ✅ |
| AST-Validierung aller Code-Zellen | ✅ |

## Installation

```bash
cp <ZIP>/lib/plotting.py lib/
cp <ZIP>/patched_notebooks/kuer/K_01_Raeumliche_Analyse.ipynb kuer/
cp <ZIP>/patched_notebooks/kuer/K_04_Animationen.ipynb kuer/
```

## Nächste Schritte im Plan

| Sub-Phase | Was |
|---|---|
| 6.2 | `lib/io_ops.py` — `log_dataindex`, transfer-Helper |
| 6.3 | `lib/data_fetchers.py` — ENTSO-E/BFE-Loader |
| 6.4 | `lib/simulation.py` — Dispatch-Sim aus NB03/K_06 (**hoch Risiko**) |
| 6.5 | `lib/columns.py` — DF-Spalten-Helfer |

6.1 ist niedrig-Risiko abgeschlossen. 6.4 ist die grösste Aufgabe und sollte
sorgfältig gemacht werden, weil NB03- und K_06-Dispatch subtile Unterschiede
haben können.
