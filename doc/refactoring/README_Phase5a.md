# Phase 5a — lib-Import-Fix (Bootstrap)

## Was war das Problem

`from lib.widgets import show_animation` funktionierte in K_00, K_01c, K_01d
nicht. In `Test_Phase1.ipynb` **funktionierte** es, weil dort eine
Bootstrap-Zelle den Projekt-Root in `sys.path` einträgt:

```python
import sys
from pathlib import Path
_lib_root = Path('..').resolve()
if str(_lib_root) not in sys.path:
    sys.path.insert(0, str(_lib_root))
```

In den anderen NBs fehlte dieser Bootstrap. Ohne ihn sucht Python in
`kuer/` bzw. `experimental/` nach `lib/` — wo keins liegt.

## Der Fix

Eine **Bootstrap-Zelle** direkt nach `## Initialisierung` eingefügt, in
jedem NB das `lib/...` importiert:

```python
# ── lib/ aus Projekt-Root erreichbar machen ──────────────────────────────────
# Notebook liegt in einem Unterordner (kuer/, experimental/, notebooks/,
# organisation/). Damit 'from lib.xxx import ...' funktioniert, muss der
# Projekt-Root vorne in sys.path stehen. autoreload sorgt dafür, dass
# Änderungen in lib/*.py ohne Kernel-Restart übernommen werden.
import sys, os
_PROJECT_ROOT = os.path.abspath('..')
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
try:
    get_ipython().run_line_magic('load_ext', 'autoreload')
    get_ipython().run_line_magic('autoreload', '2')
except Exception:
    pass
print(f'lib-Pfad aktiv: {_PROJECT_ROOT}/lib')
```

Plus: `autoreload 2` aktiviert — wenn du später `lib/widgets.py` änderst,
musst du nicht den Kernel neu starten.

## Gepatchte NBs

| NB | Bootstrap-Position | Erster lib-Import |
|---|---|---|
| `kuer/K_00_Business_Strategy.ipynb` | Cell 7 | Cell 10 |
| `experimental/K_01c_Energiefluss_Animationen.ipynb` | Cell 5 | Cell 22 |
| `experimental/K_01d_Grid_Topologie.ipynb` | Cell 5 | Cell 34 |

## Installation

```bash
cd /pfad/zum/projekt
cp <ZIP>/patched_notebooks/kuer/K_00_Business_Strategy.ipynb kuer/
cp <ZIP>/patched_notebooks/experimental/*.ipynb experimental/
```

## Für zukünftige NBs

Pattern zum Kopieren — als erste Zelle nach `## Initialisierung`:

```python
import sys, os
_PROJECT_ROOT = os.path.abspath('..')
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
try:
    get_ipython().run_line_magic('load_ext', 'autoreload')
    get_ipython().run_line_magic('autoreload', '2')
except Exception:
    pass
```

Der `'..'`-Weg gilt für jede NB in einem Unterordner. Bei NBs, die eine
tiefere Schachtelung hätten (`experimental/subfolder/`), wäre es `'../..'`
— aktuell nicht der Fall.

## Zum zweiten Punkt: `skip_if_exists` bei Erstellung

Richtig gesehen — Phase 4 hat nur **Infrastruktur** geliefert:
`config.json` + `lib.plotting.should_skip()` + Pattern-Doku. Die Erzeugungs-
Zellen in K_01, K_01c, K_01d, K_04 wurden **nicht** angefasst.

### Warum nicht direkt mit Phase 5 erledigt

Die Erzeugungs-Zellen haben unterschiedliche Strukturen:

**Variante A — einzelner Save (einfach einzubauen):**
```python
# Vorher:
plt.savefig(out_path)

# Nachher:
chart_name = os.path.basename(out_path).replace('.png','')
if should_skip(out_path, 'statisch', chart_name, CFG):
    print(f'⏭️  {chart_name} übersprungen')
else:
    # ... render ...
    plt.savefig(out_path)
```

**Variante B — Schleife über mehrere Saves (häufig in K_01c!):**
```python
for saison in SAISONS:
    path = os.path.join(EXP_CHARTS_DIR, f"EXP_kuer_k01c_gif_a_tag_{saison}.gif")
    # Hier muss der Check im Loop sein, nicht davor:
    chart_name = os.path.basename(path).replace('.gif','')
    if should_skip(path, 'animation', chart_name, CFG):
        print(f'⏭️  {chart_name} übersprungen')
        continue
    make_gif_fast(...)
```

**Variante C — Zelle mit Vorberechnung, die auch anderswo genutzt wird:**
Hier darf die Berechnung nicht geskippt werden — nur der Save-Teil.

Deshalb braucht jede Zelle eine **individuelle Analyse** — welche Teile der
Zelle dürfen übersprungen werden, welche nicht? Das ist fehleranfällig wenn
blind patched.

### Vorschlag für Phase 4c

Ich mache das in einem separaten Patch, wenn du gibst:
- **K_01c** (10 GIF-Erzeugungs-Zellen, grösster Hebel → `skip_if_exists`-Default
  spart beim Rebuild die meiste Zeit)
- **K_01d** (9 GIF-Erzeugungs-Zellen)
- **K_04** (4 GIF-Erzeugungs-Zellen)
- **K_01** (2 GIF-Erzeugungs-Zellen)

Statische Charts (PNG) hätte ich zunächst weggelassen — die rendern schnell
und die Default-Einstellung `modus_statisch='always'` passt. Bei Bedarf
nachziehen.

Sag Bescheid ob ich Phase 4c jetzt angehen soll und ob der vorgeschlagene
Scope passt.
