# Refactoring-Plan — ZHAW CAS Scripting-Projekt SC26_Gruppe_2

**Stand:** 24. April 2026
**Projektabgabe:** 11. Mai 2026 · Review-Checkpoint: 30. April 2026

Dieser Plan dokumentiert den systematischen Umbau der Projekt-Notebooks zu
einem einheitlichen, modularen Stand. Während der Umsetzung haben sich
einige Phasen in Sub-Phasen aufgeteilt — dokumentiert im folgenden Überblick.

## Status-Übersicht

| Phase | Inhalt | Status |
|---|---|---|
| 0 | Baseline Git-Tag vor Refactoring | ✅ |
| 1 | `lib/`-Skeleton + `show_source` + `should_skip` | ✅ |
| 2 | Anker-Hygiene (projektweit) | ✅ |
| 3a | Struktur-Harmonisierung Pflicht-NBs | ✅ |
| 3b | Struktur-Harmonisierung Kür-NBs (K_00–K_99) | ✅ |
| 3b-Fix | Abschluss-Code-Zellen nachgereicht (K_07–K_10) | ✅ |
| 3c | O_04 TOC-Reposition + Einleitung | ✅ |
| 3d | Struktur-Harmonisierung experimental/ + K_01d-Slider-Übernahme | ✅ |
| 3e | TOC-Retrofit für 6 verbliebene NBs (00, O_00–O_03, O_99) | ✅ |
| 4a | `animation`-Schalter in `config.json` (modus/modus_statisch/overrides) | ✅ |
| 4b | Patterns-Dokumentation (ohne NB-Einbau) | ✅ |
| 4c | Skip-Check zentral in `make_gif_*`-Helper-Funktionen | ✅ |
| 4d | `show_source(should_skip)` vor erster Verwendung | ✅ |
| 5 | `slide_or_play` nach `lib/widgets.py` + `show_animation`-Wrapper | ✅ |
| 5a | sys.path-Bootstrap für lib-Import | ✅ |
| 5b | Import-Cleanup + `framerate` explizit pro Anzeige | ✅ |
| 5c | `show_source(show_animation)` vor erster Verwendung | ✅ |
| 6.1 | `make_gif_chart` nach `lib/plotting.py` | ✅ |
| 6.2 | `log_dataindex` nach `lib/io_ops.py` | ✅ |
| 6.2b | `load_transfer` / `save_transfer` nach `lib/io_ops.py` | ✅ |
| 6.2c | Transfer-Migration in 10 NBs (14 Aufrufe) | ✅ |
| 6.2d | Init-Zellen auftrennen + Shadow-Bug (`_sim`) gefixt | ✅ |
| 6.3 | `fetch_entsoe_yearly` nach `lib/data_fetchers.py` | ✅ |
| K_01d Fix | CSV-Quoting (einfache Quotes bei Zenodo v0.6) | ✅ |
| K_01d Fix | Raw/Intermediate-Trennung + log_dataindex integriert | ✅ |
| **6.4** | **`lib/simulation.py` — Dispatch-Sim (hoch Risiko)** | **← aktueller Punkt** |
| 6.5 | `lib/columns.py` — DF-Spalten-Helfer | offen |
| 7 | `grid_topo.py` Konsolidierung (K_01d-Topologie-Helpers) | offen |
| 8 | Dokumentation-Update (O_01, Review-Protokoll, `Notebook_Dokumentation.md`) | offen |
| 9 | Regressionstest (run_all) | offen |

## Kanonisches Notebook-Schema (Ergebnis Phase 3 + 6.2d)

Jedes NB folgt der Struktur. **Wichtige Konvention: eine Zelle = eine Sache.**
Separate Zellen für unterschiedliche Concerns, keine Misch-Zellen.

```
Titel (H1)
[Nav-Row]                      ← bei NBs mit Nav (Pflicht / Kür / experimental)
## Inhaltsverzeichnis
## Einleitung
## Initialisierung
  ├── Bootstrap-Zelle          (sys.path + lib-Imports)
  ├── Imports-Zelle            (pandas, numpy, json, os, …)
  ├── show_source-Block(s)     (MD-Info + show_source(fn) je lib-Funktion)
  ├── Config-Zelle             (CFG-Load + Parameter-Aliases)
  ├── Directories-Zelle        (DIR_*, CHARTS_DIR, os.makedirs)
  ├── Visualisierung-Zelle     (Farben, Stil — OPTIONAL wenn NB plottet)
  └── Transfer-Zelle           (TF-Load mit load_transfer — OPTIONAL)
[## Warn-/Hinweis-Abschnitt ohne Nr]   ← nur wenn thematisch nötig (K_01b, K_01c)
## 1. Hauptteil-Abschnitt
...
## N. Hauptteil-Abschnitt
## Fazit                ← bei NBs mit Schlussfolgerung
## Abschluss            ← Datei-Check / Übersicht
[Nav-Row]
```

**TOC-Konvention:**
- Strukturelle Einträge (Einleitung, Init, Fazit, Abschluss) **ohne Nummer**
- Hauptteil mit `N [Titel]` (Zahl + Space, **kein Punkt**)
- Jede Zeile endet mit 2 Leerzeichen (MD-Hardbreak)

**Variablen-Konvention für Config vs. Transfer:**
- `_sim = CFG['pflicht']['simulation']` → Simulations-**Parameter** (config)
- `_sim_tf = TF.get('simulation', {})` → Simulations-**Ergebnisse** (transfer)
- Niemals denselben Variablennamen für beide verwenden (Shadow-Bug-Risiko)

## Kanonischer Bootstrap (Ergebnis Phase 5 + 6.1 + 6.2 + 6.3)

In jedem NB, das `lib/`-Funktionen nutzt, direkt nach `## Initialisierung`:

```python
# ── lib/ aus Projekt-Root erreichbar machen + lib-Imports ───────────────────
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
from lib.plotting       import show_source, should_skip, make_gif_chart
from lib.widgets        import show_animation
from lib.io_ops         import log_dataindex, load_transfer, save_transfer
from lib.data_fetchers  import fetch_entsoe_yearly

print(f'lib-Pfad aktiv: {_PROJECT_ROOT}/lib')
```

Je nach NB werden nur die benötigten Funktionen importiert (z.B. keine
`fetch_entsoe_yearly`-Zeile in NBs ohne ENTSO-E-Download).

**Konvention:** Wenn eine weitere `lib.xxx.fn` in einem NB zum ersten Mal
genutzt wird, direkt davor ein 2-Zellen-Block einfügen:

```markdown
**🔎 Quellcode der importierten lib-Funktion**

Die Funktion `<fn>` wird aus `lib/<modul>.py` importiert und ab dieser Stelle
im Notebook verwendet. Aufklappbar darunter ist der Quellcode einsehbar.
```

```python
show_source(<fn>)
```

Bei mehreren lib-Funktionen können Blocks konsolidiert werden (siehe Phase 6.1
für `should_skip` + `make_gif_chart` zusammen).

## Daten-Konventionen (Ergebnis K_01d-Fix)

**Gilt projektweit — Pflicht, Kür UND experimental:**

- **Rohdaten von externen Quellen** (ENTSO-E, BFE, Zenodo, OSM, …)
  → `<scope>/data/raw/<quelle>/`
  - Beispiele: `data/raw/ch_spot_prices_raw.csv`,
    `experimental/data/raw/zenodo/buses.csv`

- **Abgeleitete Zwischenergebnisse** (gefiltert, normalisiert, angereichert)
  → `<scope>/data/intermediate/`
  - Beispiele: `data/intermediate/spread_zeitreihe.csv`,
    `experimental/data/intermediate/grid_zenodo/CH_pypsa_buses.csv`

- **Finale Outputs** (fertig für weitere Analyse/Visualisierung)
  → `<scope>/data/processed/`

- **Jeder Datei-Write** wird via `log_dataindex()` im projektweiten
  `sync/dataindex.csv` protokolliert:
  ```python
  log_dataindex(filename, source_url, local_path, data_type='raw|intermediate|processed',
                rows=..., size_kb=..., note=..., dataindex_path=DATAINDEX)
  ```
  `data_type='raw'` referenziert die externe URL als `source_url`;
  `data_type='intermediate'` referenziert den Raw-Pfad — so entsteht eine
  nachvollziehbare Provenienz-Kette bis zur Original-Quelle.

- **Charts (PNG, GIF)** werden NICHT in `dataindex.csv` geloggt — das
  Protokoll ist für Daten, nicht für Visualisierungen.

## lib/-Struktur (Stand 6.3)

```
lib/
├── __init__.py          ✅  ensure_installed()                  (Phase 1)
├── plotting.py          ✅  show_source, should_skip, make_gif_chart  (Phase 1/4/6.1)
├── widgets.py           ✅  slide_or_play, show_animation       (Phase 5)
├── io_ops.py            ✅  log_dataindex, load_transfer, save_transfer  (Phase 6.2)
├── data_fetchers.py     ✅  fetch_entsoe_yearly                 (Phase 6.3)
├── simulation.py        ⏳  Dispatch-Sim aus NB03/K_06          (Phase 6.4)
├── columns.py           ⏳  DF-Spalten-Helfer                   (Phase 6.5)
└── grid_topo.py         ⏳  K_01d OSM-/Topologie-Helpers        (Phase 7)
```

## Transfer-Pipeline (Ergebnis 6.2b/c)

`sync/transfer.json` ist SSOT für berechnete Ergebnisse zwischen NBs:

```
Schreiber:
  NB01 → datenzeitraum
  NB03 → simulation
  K_06 → dispatch_optimierung   (liest auch: simulation.wirtschaftlichkeit, datenzeitraum.n_years)
  K_09 → eigenverbrauch
  K_10 → produkt                (liest auch: simulation, hybrid_simulation)
  K_99 → hybrid_simulation

Leser:
  NB00, NB02, NB03, K_00, K_05, K_06, K_10, K_99
```

**Benutzung via lib-Helper:**

```python
# Lesen
TF = load_transfer()                      # komplettes Dict
dt = load_transfer(key='datenzeitraum')   # ein Teilbaum

# Schreiben (mit automatischem Merge — andere Keys bleiben erhalten)
save_transfer({'n_years': 3.3, ...}, key='datenzeitraum')
```

## Phase 6.4 — `lib/simulation.py` (nächster Schritt, **hoch Risiko**)

- Dispatch-Simulation aus NB03 und K_06 (**subtile Unterschiede**!)
- Wirtschaftlichkeits-Rechner aus NB04 und K_99

Hier besonders vorsichtig — diese Funktionen bestimmen die zentralen
Kennzahlen des Projekts. Vor dem Mergen muss verifiziert werden, dass die
Resultate identisch bleiben (z.B. über einen Hash der erzeugten CSV).

## Phase 6.5 — `lib/columns.py`

- Spalten-Normalisierung für ENTSO-E-Rückgaben
- Resampler-Wrapper für Tages/Wochen/Monatsprofile

## Phase 7 — `lib/grid_topo.py` (nach Phase 6)

Dedicated Modul für die OSM-/Netzwerk-Topologie-Logik aus K_01d:
- Multi-Format-Koordinaten-Parser (`parse_lonlat`)
- Snap-Distance-Logik (5000m CH-Default)
- Multi-Voltage-Filter (`filter_voltage_levels`)
- Graph-Konstruktion (NetworkX-Wrapper)

## Phase 8 — Dokumentation

- **`organisation/O_01_Project_Overview.ipynb`**: §5 Notebook-Map auf den
  aktuellen Stand bringen (lib/ erwähnen, neue experimental/-Struktur)
- **`organisation/O_04_Review_Protokoll.ipynb`**: §2 Korrektur-Iterationen
  um die während des Refactorings entstandenen Einträge ergänzen
  — speziell auch den Shadow-Bug-Fix aus Phase 6.2d dokumentieren
- **`Notebook_Dokumentation.md`** am Projekt-Root: komplette Überarbeitung,
  entspricht jetzt nicht mehr der Realität

## Phase 9 — Regressionstest

Nach Abschluss Phase 6-8 einmal `run_all.sh` durchlaufen lassen:
- Alle GIFs neu rendern (`modus: "always"`)
- Alle statischen Charts neu rendern
- Dataindex-Zählung: muss mit dem Stand vor Refactoring übereinstimmen
  (oder dokumentierte Differenzen vorweisen)
- Alle NBs laufen ohne Fehler durch (Cell-Execution-Reihenfolge)
- transfer.json-Inhalt nach run_all vergleichen mit Vor-Refactoring-Stand

## Kür-Freeze

Seit **30. März 2026** werden keine neuen Kür-Notebooks mehr angelegt.
Neue Ideen werden nur noch in `O_01_Project_Overview.ipynb` §13
("Potenzielle Erweiterungen") dokumentiert, nicht implementiert.

## Abgabe-Checkliste (grob)

Vor der Moodle-Abgabe am 11. Mai 2026:

- [ ] Phase 6 abgeschlossen (Lib-Migration) — 6.1, 6.2a-d, 6.3 fertig; 6.4, 6.5 offen
- [ ] Phase 7 abgeschlossen (grid_topo)
- [ ] Phase 8 abgeschlossen (Doku-Update)
- [ ] Phase 9 abgeschlossen (frischer Regressionslauf)
- [ ] `sync/config.json` `modus: "skip_if_exists"` (Default für Reviewer)
- [ ] `run_all.bat/.sh/.ps1` funktionieren von leerem Checkout aus
- [ ] Alle NB-Outputs in Ausgangszustand (Output-Cells gestripped via
      `nbstripout` in Git-Attributes)
- [ ] `K_01d_Grid_Topologie_slider.ipynb` am Projekt-Root **gelöscht**
      (obsolet seit Phase 3d)
- [ ] CS/SE-Review im `O_04_Review_Protokoll` eingetragen
- [ ] Shadow-Bug-Fix (Phase 6.2d) im Review-Protokoll als A-09 o.ä. dokumentiert
- [ ] K_01d-Fixes (CSV-Quoting + Raw/Intermediate) im Review-Protokoll dokumentiert
- [ ] Abgabe-ZIP enthält: notebooks/, kuer/, experimental/, organisation/,
      sync/, lib/, data/, output/, run_all.*, README.md, .gitattributes
