# Phase 6.2 — `log_dataindex` nach `lib/io_ops.py`

## Scope-Entscheidung nach Inspektion

Vor dem Migrieren habe ich projektweit inspiziert:

| Kandidat | Analyse | Entscheidung |
|---|---|---|
| `log_dataindex` | **1** Definition (K_01), 4 Aufrufe — nur in K_01 | **migriert** — damit andere NBs es zukünftig einfach nutzen können |
| `transfer.json`-Helper | **0** NBs nutzen `transfer.json` aktuell | nicht migriert (keine Duplikation, keine aktuellen Nutzer) |
| Config-Loader (`with open('../sync/config.json')`) | 4 Varianten, aber je nur 1-2 Zeilen | nicht migriert (Code zu trivial, NB-spezifische Aliase folgen immer direkt danach) |

**Ergebnis:** Schlank. Nur `log_dataindex` aus K_01 in `lib/io_ops.py`
gezogen — mit leichten Generalisierungen für zukünftige NB-Nutzung.

## Änderungen

### 1. `lib/io_ops.py` (neu)

```python
def log_dataindex(filename, source_url, local_path, data_type,
                  rows=None, size_kb=None, status='active', note='',
                  dataindex_path=None):
    """Schreibt einen Eintrag ins Daten-Provenienz-Protokoll.

    Existiert bereits ein aktiver Eintrag mit demselben `filename`, wird
    dieser als 'superseded' markiert (mit Zeitstempel in 'superseded_at').
    """
```

**Anpassungen gegenüber der K_01-Variante:**

- `dataindex_path`-Parameter: explizit übergebbar. Wenn `None`, wird im
  aufrufenden Scope die globale `DATAINDEX`-Variable gesucht
  (Rückwärtskompatibilität für K_01). Fallback: `"../sync/dataindex.csv"`.
- `DATAINDEX_COLUMNS`-Konstante für saubere Dokumentation der Spalten
- Docstring mit Parameter-Erklärungen
- Import von `pandas` lokal in der Funktion (keine Library-weite pandas-Dep)

### 2. K_01 — Bootstrap erweitert

```python
from lib.plotting import show_source, should_skip, make_gif_chart
from lib.io_ops   import log_dataindex
```

### 3. K_01 — lokale `def log_dataindex(...)` aus Cell 9 entfernt

Die ganze ~18-Zeilen-Definition ist weg. `DATAINDEX`-Variable bleibt
erhalten, wird jetzt einfach implizit von `log_dataindex()` aus dem
Caller-Scope gelesen.

### 4. K_01 — `show_source`-Block vor erster Verwendung (Cell 25)

Analog zum Pattern aus Phase 4d/5c/6.1:

```markdown
**🔎 Quellcode der importierten lib-Funktion**

Die Funktion `log_dataindex` wird aus `lib/io_ops.py` importiert und
schreibt Einträge ins Daten-Provenienz-Protokoll `sync/dataindex.csv`. ...
```

```python
show_source(log_dataindex)
```

## Qualitäts-Checks (alle ✅)

| Check | Status |
|---|---|
| `lib/io_ops.py` syntaktisch valide | ✅ |
| `from lib.io_ops import log_dataindex` funktioniert | ✅ |
| K_01 keine lokale def log_dataindex mehr | ✅ |
| AST-Validierung aller 34 Code-Zellen | ✅ |
| 4 log_dataindex-Aufrufe weiterhin vorhanden | ✅ |
| show_source-Block vor Cell 25 | ✅ |

## Installation

```bash
cp <ZIP>/lib/io_ops.py lib/
cp <ZIP>/patched_notebooks/kuer/K_01_Raeumliche_Analyse.ipynb kuer/
```

## Nutzung in zukünftigen NBs

Für jedes NB, das etwas in `sync/dataindex.csv` schreiben will, reicht ein
Bootstrap-Eintrag:

```python
from lib.io_ops import log_dataindex
```

Und der Aufruf:

```python
log_dataindex(
    filename='my_output.csv',
    source_url='ENTSO-E Transparency',
    local_path='data/intermediate/my_output.csv',
    data_type='intermediate',
    rows=8760,
    size_kb=245.3,
    note='Tagesauflösung',
    dataindex_path='../sync/dataindex.csv',   # optional
)
```

## Nächste Schritte

Phase 6.2 war sehr schlank — nur 1 Funktion migriert. Für Phase 6 bleiben:

| Sub-Phase | Was | Stand |
|---|---|---|
| 6.3 | `lib/data_fetchers.py` — ENTSO-E/BFE-Loader | offen |
| 6.4 | `lib/simulation.py` — Dispatch-Sim aus NB03/K_06 | **hoch Risiko** |
| 6.5 | `lib/columns.py` — DF-Spalten-Helfer | offen |

Phase 6.3 wäre der nächste sinnvolle Schritt. Vorher aber inspizieren ob
die ENTSO-E-Loader in NB01 und K_01 wirklich gleich sind (oder ob sich
Pflicht- und Kür-NB-Varianten unterscheiden).
