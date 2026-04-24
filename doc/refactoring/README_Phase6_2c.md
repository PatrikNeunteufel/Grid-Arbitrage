# Phase 6.2c — Transfer-Migration in 10 NBs

Die 14 Transfer-Zellen (10 LOAD + 6 SAVE — teils in denselben NBs) auf die
Helper aus Phase 6.2b umgestellt.

## Übersicht — was passiert in welchem NB

| NB | Rolle | Schreibt key | Liest keys | load/save in NB |
|---|---|---|---|---|
| `notebooks/01_Daten_Laden` | Schreiber | `datenzeitraum` | — | 0 / 1 |
| `notebooks/03_Daten_Analyse` | Schreiber+Leser | `simulation` | datenzeitraum | 3 / 1 |
| `kuer/K_06_Dispatch_Optimierung` | Schreiber+Leser | `dispatch_optimierung` | simulation.wirtschaftlichkeit, datenzeitraum.n_years | 2 / 1 |
| `kuer/K_09_Eigenverbrauch` | Schreiber | `eigenverbrauch` | — | 1 / 1 |
| `kuer/K_10_Produkt_Steckbrief` | Schreiber+Leser | `produkt` | simulation, hybrid_simulation | 2 / 1 |
| `kuer/K_99_Kombinierte_Simulation` | Schreiber+Leser | `hybrid_simulation` | alle zuvor | 2 / 1 |
| `notebooks/00_Business_Case` | Leser | — | alle | 1 / 0 |
| `notebooks/02_Daten_Bereinigung` | Leser | — | datenzeitraum, simulation | 2 / 0 |
| `kuer/K_00_Business_Strategy` | Leser | — | alle | 1 / 0 |
| `kuer/K_05_Revenue_Stacking` | Leser | — | datenzeitraum, simulation | 1 / 0 |

**Total:** 14 `load_transfer`-Aufrufe + 6 `save_transfer`-Aufrufe quer über
10 NBs.

## Typische Transformation

**Vorher — Schreiber:**
```python
_tf_path = '../sync/transfer.json'
_tf = json.loads(open(_tf_path).read() or '{}') if os.path.exists(_tf_path) ... else {}
_tf['datenzeitraum'] = {
    'start_date': str(START_YEAR),
    ...
}
with open(_tf_path, 'w') as _f: json.dump(_tf, _f, indent=2, ensure_ascii=False)
```

**Nachher — Schreiber:**
```python
_datenzeitraum = {
    'start_date': str(START_YEAR),
    ...
}
save_transfer(_datenzeitraum, key='datenzeitraum')
```

**Vorher — Leser:**
```python
_tf_path = '../sync/transfer.json'
if os.path.exists(_tf_path) and os.path.getsize(_tf_path) > 0:
    TF = json.load(open(_tf_path))
    _dt = TF.get('datenzeitraum', {})
    # ... aliases ...
    print(f"..: {TF_START} ...")
else:
    TF = {}; TF_N_YEARS = None; ...
    print('⚠️  ... NB01/NB02 zuerst ausführen')
```

**Nachher — Leser:**
```python
TF        = load_transfer()
_dt       = TF.get('datenzeitraum', {})
# ... aliases ...
if TF:
    print(f"..: {TF_START} ...")
```

Die Warnung bei fehlender/leerer Datei übernimmt `load_transfer` intern.
NBs werden ~6-10 Zeilen leichter pro Transfer-Zelle.

## Bootstrap einheitlich in allen 10 NBs

Neu in jedem NB — direkt nach `## Initialisierung`:

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

from lib.plotting import show_source
from lib.io_ops   import load_transfer, save_transfer

print(f'lib-Pfad aktiv: {_PROJECT_ROOT}/lib')
```

## `show_source`-Block pro NB

Vor der ersten Transfer-Nutzung in jedem NB (Konvention aus Phase 4d/5c/6.1):

```markdown
**🔎 Quellcode der importierten lib-Funktion**

Die Funktion `load_transfer` (bzw. `save_transfer` für Schreiber) wird aus
`lib/io_ops.py` importiert und ...
```

```python
show_source(load_transfer)
```

## Qualitäts-Checks (alle ✅)

| Check | Status |
|---|---|
| AST-Validierung aller Code-Zellen in allen 10 NBs | ✅ |
| 0 Boilerplate-Reste (`with open(_tf_path, 'w')`) | ✅ |
| 0 Boilerplate-Reste (`json.load(open(_tf_path))`) | ✅ |
| 14 `load_transfer` + 6 `save_transfer`-Aufrufe korrekt verteilt | ✅ |

## Installation

```bash
cp <ZIP>/patched_notebooks/notebooks/*.ipynb notebooks/
cp <ZIP>/patched_notebooks/kuer/*.ipynb kuer/
```

⚠️ Voraussetzung: `lib/io_ops.py` aus Phase 6.2b muss installiert sein —
ohne die Helper funktionieren die NBs nicht.

## Was Phase 6.2c NICHT macht

- Die Aliases (`TF_N_YEARS = _dt.get('n_years', None)` etc.) bleiben
  **NB-lokal** unverändert. Sie sind nicht duplikativ — jedes NB nimmt die
  Aliase, die es braucht.
- Die `CFG.get('kuer_aktiv', {})`-Zeile in einigen NBs wurde belassen
  (kommt aus `config.json`, nicht `transfer.json`).

## Status nach Phase 6.2c

**lib/-Füllstand:**

```
lib/
├── __init__.py          ✅  ensure_installed()
├── plotting.py          ✅  show_source, should_skip, make_gif_chart
├── widgets.py           ✅  slide_or_play, show_animation
├── io_ops.py            ✅  log_dataindex, load_transfer, save_transfer
├── data_fetchers.py     ⏳  ENTSO-E/BFE-Loader              (Phase 6.3)
├── simulation.py        ⏳  Dispatch-Sim                    (Phase 6.4)
├── columns.py           ⏳  DF-Spalten-Helfer               (Phase 6.5)
└── grid_topo.py         ⏳  K_01d OSM-Helpers               (Phase 7)
```

## Nächster Schritt

**Phase 6.3** — ENTSO-E und BFE-Loader nach `lib/data_fetchers.py`. Vor dem
Migrieren wieder sorgfältig inspizieren: ist der ENTSO-E-Loader in NB01 und
K_01 identisch, oder gibt's Varianten (Pflicht vs. Kür)?
