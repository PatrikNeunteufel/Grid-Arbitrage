# Refactoring-Plan — ZHAW CAS Scripting-Projekt SC26_Gruppe_2

**Stand:** 23. April 2026
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
| **6** | **Lib-Migration** (Funktionen aus NBs nach `lib/`) | **← aktueller Punkt** |
| 7 | `grid_topo.py` Konsolidierung (K_01d-Topologie-Helpers) | offen |
| 8 | Dokumentation-Update (O_01, Review-Protokoll, `Notebook_Dokumentation.md`) | offen |
| 9 | Regressionstest (run_all) | offen |

## Kanonisches Notebook-Schema (Ergebnis Phase 3)

Jedes NB folgt der Struktur:

```
Titel (H1)
[Nav-Row]           ← bei NBs mit Nav, d.h. Pflicht/Kür/experimental
## Inhaltsverzeichnis
## Einleitung
## Initialisierung
  └─ Bootstrap-Zelle (sys.path + lib-Imports)
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

## Kanonischer Bootstrap (Ergebnis Phase 5a/b/c + 4c)

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
from lib.widgets  import show_animation
from lib.plotting import show_source, should_skip

print(f'lib-Pfad aktiv: {_PROJECT_ROOT}/lib')
```

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

## lib/-Struktur (aktuell)

```
lib/
├── __init__.py          ✅  ensure_installed()
├── plotting.py          ✅  show_source, should_skip        (Phase 1/4)
├── widgets.py           ✅  slide_or_play, show_animation    (Phase 5)
├── io_ops.py            ⏳  log_dataindex, transfer-Helper   (Phase 6)
├── data_fetchers.py     ⏳  ENTSO-E/BFE-Loader               (Phase 6)
├── simulation.py        ⏳  Dispatch-Sim aus NB03/K_06       (Phase 6)
├── columns.py           ⏳  DF-Spalten-Helfer                (Phase 6)
└── grid_topo.py         ⏳  K_01d OSM-/Topologie-Helpers     (Phase 7)
```

## Phase 6 — Lib-Migration (nächster Schritt)

Funktionen, die aktuell in NB-Zellen definiert sind und nach `lib/` gezogen
werden sollen. Priorität nach Mehrfachnutzung und Risiko:

### 6.1 `lib/plotting.py` ausbauen (hoch prio, niedrig Risiko)

**Ausgangslage:** `make_gif_chart` ist **identisch dupliziert** in:
- `kuer/K_01_Raeumliche_Analyse.ipynb` Cell 10
- `kuer/K_04_Animationen.ipynb` Cell 10

Eine gemeinsame Definition in `lib/plotting.py`, beide NBs importieren.
Die K_01c/K_01d-Varianten (`make_gif_fast` / `make_gif_fast_d`) sind NB-
spezifisch (enthalten eigenen Hintergrund-Renderer) und bleiben lokal — aber
könnten optional später auch migriert werden, wenn sich ein gemeinsames
Interface herauskristallisiert.

Weitere Migrations-Kandidaten für `lib/plotting.py`:
- `show` / `show_chart` aus K_00 und NB00 (Anzeige statischer Charts)
- `draw_base_map` aus K_01 (auch lokal in K_01c dupliziert)
- `highlight` aus O_01

### 6.2 `lib/io_ops.py` (mittel prio)
- `log_dataindex(path, description)` — aktuell NB-lokal dupliziert
- Transfer-Helper: `load_transfer()`, `save_transfer()`, `update_transfer()`

### 6.3 `lib/data_fetchers.py` (niedrig prio)
- ENTSO-E-Loader aus NB01
- BFE-GeoPackage-Loader aus K_01/K_01c

### 6.4 `lib/simulation.py` (hoch prio, hohes Risiko)
- Dispatch-Simulation aus NB03 und K_06 (mit subtilen Unterschieden!)
- Wirtschaftlichkeits-Rechner aus NB04 und K_99

### 6.5 `lib/columns.py` (niedrig prio)
- Spalten-Normalisierung für ENTSO-E-Rückgaben
- Resampler-Wrapper für Tages/Wochen/Monatsprofile

## Phase 7 — `lib/grid_topo.py` (nach Phase 6)

Dedicated Modul für die OSM-/Netzwerk-Topologie-Logik aus K_01d:
- Multi-Format-Koordinaten-Parser (`parse_lonlat`)
- Snap-Distance-Logik (5000m CH-Default)
- Multi-Voltage-Filter (`filter_voltage_levels`)
- Graph-Konstruktion (NetworkX-Wrapper)

Die Komplexität und die frühe Duplikation zwischen K_01c und K_01d
rechtfertigen ein eigenes Modul.

## Phase 8 — Dokumentation

- **`organisation/O_01_Project_Overview.ipynb`**: §5 Notebook-Map auf den
  aktuellen Stand bringen (lib/ erwähnen, neue experimental/-Struktur)
- **`organisation/O_04_Review_Protokoll.ipynb`**: §2 Korrektur-Iterationen
  um die während des Refactorings entstandenen Einträge ergänzen
- **`Notebook_Dokumentation.md`** am Projekt-Root: komplette Überarbeitung,
  entspricht jetzt nicht mehr der Realität

## Phase 9 — Regressionstest

Nach Abschluss Phase 6-8 einmal `run_all.sh` durchlaufen lassen:
- Alle GIFs neu rendern (`modus: "always"`)
- Alle statischen Charts neu rendern
- Dataindex-Zählung: muss mit dem Stand vor Refactoring übereinstimmen
  (oder dokumentierte Differenzen vorweisen)
- Alle NBs laufen ohne Fehler durch (Cell-Execution-Reihenfolge)

## Kür-Freeze

Seit **30. März 2026** werden keine neuen Kür-Notebooks mehr angelegt.
Neue Ideen werden nur noch in `O_01_Project_Overview.ipynb` §13
("Potenzielle Erweiterungen") dokumentiert, nicht implementiert.

## Abgabe-Checkliste (grob)

Vor der Moodle-Abgabe am 11. Mai 2026:

- [ ] Phase 6 abgeschlossen (Lib-Migration)
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
- [ ] Abgabe-ZIP enthält: notebooks/, kuer/, experimental/, organisation/,
      sync/, lib/, data/, output/, run_all.*, README.md, .gitattributes
