# Phase 6.5 — Column-Helper + I/O-Helper konsolidiert

## Revision gegenüber dem ursprünglichen Plan

Der Plan nannte: *"lib/columns.py — DF-Spalten-Helfer + Resampler-Wrapper"*.

Projektweite Inspektion gegen `verified_3a` ergab ein anderes Bild:

| Funktion | Kategorie | Duplikate | Migrations-Kandidat? |
|---|---|---|---|
| `find_col` | DF-Column-Helper | 2 identische (K_01, K_01b) | ✅ → `lib/columns.py` |
| `needs_download` | I/O-Gate | 3 Varianten (NB01, K_01, K_02) | ✅ → `lib/io_ops.py` |
| `needs_rebuild` | I/O-Gate | 3 NBs (NB02, NB03, K_02) | ✅ → `lib/io_ops.py` |
| `log_missing` | I/O-Logging | 3 NBs (NB01, NB02, NB03) | ✅ → `lib/io_ops.py` |
| Resampler-Wrapper | — | **existieren nicht im Projekt** | — |

**Pragmatischer Split:** `find_col` kommt in ein neues `lib/columns.py`, die drei I/O-Helper gehen ins bestehende `lib/io_ops.py`. Keine zwei Module nur wegen Namens-Konventionen.

## Neue lib-Module

### `lib/columns.py` (NEU)

```python
def find_col(df, *kws):
    """Sucht die erste Spalte, deren Name (case-insensitiv) ein Keyword enthält."""
```

Nützlich für heterogene Spalten-Namen in externen Datenquellen (BFE vs. BFS vs. swisstopo).

### `lib/io_ops.py` (ERWEITERT)

Drei neue Funktionen ergänzen die vorhandenen (`log_dataindex`, `load_transfer`, `save_transfer`):

```python
def needs_download(path, min_kb, key, force_reload=None):
    """True wenn Datei fehlt, zu klein ist, oder force_reload[key] gesetzt."""

def needs_rebuild(filepath, min_rows, ds_key, force_reload=None):
    """True wenn Datei fehlt, zu wenige Zeilen, oder force_reload gesetzt."""

def log_missing(source, reason, data_folder='../data', dataindex_path=None):
    """Protokolliert fehlende/fehlerhafte externe Datenquelle (missing.txt + dataindex)."""
```

**`force_reload=None` Default:** wenn nicht übergeben, sucht die Funktion die globale Variable `FORCE_RELOAD` im Caller-Scope. Dieselbe Logik wie bei `log_dataindex`/`DATAINDEX` — Rückwärtskompatibel zu den bestehenden Aufruf-Patterns, die `force_reload` nicht explizit übergeben.

## Gepatchte NBs (6 NBs, 16 lokale defs entfernt)

| NB | Entfernte lokale defs |
|---|---|
| `notebooks/01_Daten_Laden` | `needs_download` + `log_missing` |
| `notebooks/02_Daten_Bereinigung` | `needs_rebuild` + `log_missing` |
| `notebooks/03_Daten_Analyse` | `needs_rebuild` + `log_missing` |
| `kuer/K_01_Raeumliche_Analyse` | `needs_download` + `find_col` |
| `kuer/K_02_Cross_Border` | `needs_download` + `needs_rebuild` |
| `experimental/K_01b_Zonenmodell_Erweitert` | `find_col` |

**Bootstrap** in K_01 und K_01b neu angelegt (hatten bisher keinen). Alle 6 NBs haben jetzt den kanonischen Bootstrap.

**show_source-Blöcke** vor erster Verwendung eingefügt.

## Projektweiter Stand nach 6.5

```
  needs_download: 4 Aufrufe in 3 NBs   (NB01, K_01, K_02)
  needs_rebuild:  3 Aufrufe in 3 NBs   (NB02, NB03, K_02)
  log_missing:    3 Aufrufe in 1 NB    (NB01)
  find_col:       9 Aufrufe in 2 NBs   (K_01, K_01b)
  ─────────────────────────────────────────
  Total:         19 Aufrufe über 2 lib-Module (columns.py + io_ops.py)
  Vorher:        11 lokale def-Duplikate
```

## Qualitäts-Checks (alle ✅)

| Check | Status |
|---|---|
| `lib/columns.py` syntaktisch valide | ✅ |
| `lib/io_ops.py` erweitert syntaktisch valide | ✅ |
| Alle 4 Funktionen importierbar | ✅ |
| 0 lokale defs projektweit für die 4 Funktionen | ✅ |
| AST-Validierung aller Code-Zellen (alle NBs) | ✅ |
| Aufrufe bleiben unverändert (Signatur-kompatibel) | ✅ |

## Aufruf-Kompatibilität

Die alten Aufrufe funktionieren unverändert weiter — die lib-Versionen haben **rückwärts-kompatible** Signaturen mit optionalen Zusatzparametern:

```python
# Alt (und neu): alle Aufrufe funktionieren unverändert
if needs_download(LOAD_FILE, 10, 'netzlast'):
    ...

# Mit explizitem force_reload (neu möglich):
if needs_download(LOAD_FILE, 10, 'netzlast', force_reload=CFG['force_reload']):
    ...
```

## lib/-Status nach 6.5

```
lib/
├── plotting.py          ✅  show_source, should_skip, make_gif_chart, show_chart
├── widgets.py           ✅  slide_or_play, show_animation
├── io_ops.py            ✅  log_dataindex, load_transfer, save_transfer,
│                              needs_download, needs_rebuild, log_missing   ← NEU
├── data_fetchers.py     ✅  fetch_entsoe_yearly
├── simulation.py        ✅  simulate_battery_dispatch
├── columns.py           ✅  find_col                                       ← NEU
└── grid_topo.py         ⏳  Phase 7 (K_01d OSM-/Topologie-Helpers)
```

## Installation

```bash
cp <ZIP>/lib/columns.py lib/
cp <ZIP>/lib/io_ops.py lib/
cp <ZIP>/patched_notebooks/notebooks/*.ipynb notebooks/
cp <ZIP>/patched_notebooks/kuer/*.ipynb kuer/
cp <ZIP>/patched_notebooks/experimental/K_01b_Zonenmodell_Erweitert.ipynb experimental/
```

## Nächster Schritt

**Phase 6 abgeschlossen.** Nächster Punkt ist Phase 7 — `lib/grid_topo.py` für
die OSM-/Topologie-Helpers aus K_01d (clean_name, in_bbox, compute_edge_flows,
etc.). Oder Phase 8/9 (Doku-Update + Regressionstest) falls Phase 7 nicht
kritisch ist für die Abgabe.
