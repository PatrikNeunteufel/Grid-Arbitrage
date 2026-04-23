# Phase 5b — Import-Cleanup + framerate sichtbar

## Zwei Dinge korrigiert

### 1. Keine redundanten Imports mehr in Anzeige-Zellen

**Vorher (schlechter Style):**
```python
# ── Ausgabe anzeigen ────────────────────────────────────────────
from lib.widgets import show_animation      ← unnötig in jeder Zelle
import os                                    ← bereits in Init importiert
_p = os.path.join(EXP_CHARTS_DIR, '...gif')
show_animation(_p, mode='gif')
```

**Nachher:**
```python
# ── Ausgabe anzeigen ────────────────────────────────────────────
_p = os.path.join(EXP_CHARTS_DIR, '...gif')
# Umschalten: mode='gif' (Standbild) oder mode='slider' (interaktiv).
# framerate nur für Slider relevant (bei GIF steckt fps im GIF selbst).
show_animation(_p, mode='gif', framerate=10)
```

Der `show_animation`-Import ist jetzt **einmal zentral** im Bootstrap:

```python
# Bootstrap-Zelle (einmal pro NB, direkt nach ## Initialisierung)
import sys, os
_PROJECT_ROOT = os.path.abspath('..')
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
try:
    get_ipython().run_line_magic('load_ext', 'autoreload')
    get_ipython().run_line_magic('autoreload', '2')
except Exception:
    pass

# lib-Imports (einmal zentral — in allen folgenden Zellen verfügbar)
from lib.widgets import show_animation

print(f'lib-Pfad aktiv: {_PROJECT_ROOT}/lib')
```

Zukünftige `from lib.xxx import ...` gehören ebenfalls in diese Bootstrap-
Zelle — das ist die richtige Stelle für zentrale Projekt-Imports.

### 2. `framerate` explizit in jedem Call sichtbar

Bisher war der Slider-Default hart auf 10 fps gesetzt; um ihn zu ändern
hätte man in `lib/widgets.py` schauen müssen. Jetzt steht `framerate=10`
direkt in jeder Anzeige-Zelle und kann pro Animation überschrieben werden:

```python
show_animation(_p, mode='slider', framerate=15)   # schneller
show_animation(_p, mode='slider', framerate=6)    # langsamer
```

Bei `mode='gif'` wird der Parameter ignoriert (die fps stecken ja schon im
GIF selbst). Zur Klarheit steht der Hinweis als Kommentar über jedem Call.

## Geänderte NBs

| NB | Änderungen |
|---|---|
| `kuer/K_00_Business_Strategy.ipynb` | Bootstrap erweitert + `show_anim`-Wrapper bekommt `framerate`-Parameter |
| `experimental/K_01c_Energiefluss_Animationen.ipynb` | Bootstrap erweitert + 10 Anzeige-Zellen bereinigt |
| `experimental/K_01d_Grid_Topologie.ipynb` | Bootstrap erweitert + 5 Anzeige-Zellen bereinigt |

## K_00 Wrapper

Der `show_anim`-Wrapper in K_00 nimmt jetzt auch `framerate`:

```python
def show_anim(filename, caption='', width=1100, mode='gif', framerate=10):
    path = os.path.join(CHARTS_DIR, filename)
    ...
    show_animation(path, mode=mode, width=width, caption=caption, framerate=framerate)
```

Damit kannst du in K_00 so nutzen:

```python
show_anim('kuer_k04_anim_A_07h.gif', 'Morgenspitze', mode='slider', framerate=20)
```

## Installation

```bash
cp <ZIP>/patched_notebooks/kuer/K_00_Business_Strategy.ipynb kuer/
cp <ZIP>/patched_notebooks/experimental/*.ipynb experimental/
```

## Qualitäts-Checks

| Check | K_00 | K_01c | K_01d |
|---|---|---|---|
| Bootstrap erweitert um `show_animation`-Import | ✅ | ✅ | ✅ |
| 0 redundante Imports in Anzeige-Zellen | n/a | ✅ (10) | ✅ (5) |
| Alle Calls haben `framerate=...` | via Wrapper | ✅ (10/10) | ✅ (5/5) |
| JSON-Validität, Cell-IDs erhalten | ✅ | ✅ | ✅ |

## Nächste Phase

**Phase 4c** — `should_skip()` in die Chart/GIF-**Erzeugungs-Zellen** einbauen.
Scope wie besprochen: K_01c, K_01d, K_04, K_01 — in dieser Priorität.
