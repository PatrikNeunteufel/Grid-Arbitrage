# Phase 7 — `lib/grid_topo.py` mit `load_kantone` (richtig gemacht)

## Was vorher schiefgelaufen war

Meine erste Phase-7-Analyse suchte nur nach `def load_kantone` und fand dadurch nur K_01d (2× definiert). Die Schlussfolgerung *"alle anderen NBs haben keine Topo-Helpers, `grid_topo.py` lohnt sich nicht"* war daher falsch.

**Tatsächlich:** K_01 und K_01c haben die **gleiche Logik inline** (keine eigene Def, aber KANT_CANDIDATES + KANT_NUM_TO_ABK + gpd.read_file + Kürzel-Detektion). Die breitere Suche — gut, dass du nachgefragt hast — brachte sie an den Tag.

**Projektweite Situation:**

| NB | Form | Länge | Nutzt |
|---|---|---:|---|
| K_01 Cell 49 | inline | ~80 Zeilen | `KANT_NAME_TO_ABK`, `KANT_NUM_TO_ABK`, `KANT_CANDIDATES`, Download-Fallback, Strategie-Logik |
| K_01c Cell 13 | inline | ~40 Zeilen | `KANT_CANDIDATES`, `KANT_NUM_TO_ABK`, Kürzel-Detektion mit 3 Strategien |
| K_01d Cell 8/15 | 2× `def` | 27 + 28 Zeilen | eigene Funktion, 3 Aufrufe innerhalb K_01d |

Das **ist** ein klares Duplikat und lohnt eine Migration.

## `lib/grid_topo.py` — neue lib-Funktion

```python
def load_kantone(data_dirs, download_url=None, download_target=None,
                 min_file_size=50_000, verbose=True):
    """Lädt Schweizer Kantonsgrenzen aus GeoPackage-Cache.
    
    Probiert mehrere Pfad-Kandidaten nacheinander. Normalisiert auf
    EPSG:4326, ergänzt 'KAB'-Spalte mit 2-Buchstaben-Kürzeln."""
```

**Deckt alle 3 NB-Use-Cases ab:**
- **K_01:** lokaler Pfad mit Fallback auf swissBOUNDARIES3D-Download (via `download_url` + `download_target` Parameter)
- **K_01c:** mehrere Pfad-Kandidaten probieren
- **K_01d:** aus K_01-Produktiv-Daten laden

**Drei Kürzel-Detektions-Strategien automatisch:**
1. Spalten-Name ist `icc`/`kab`/`abbreviation`
2. Spalte mit Zahlen 1..26 → via `KANT_NUM_TO_ABK`-Dict
3. Spalte mit direkten 2-Buchstaben-Kürzeln (case-insensitiv, ≥20 Matches als Schwelle)

**Konstanten als Modul-Exports:**
- `KANT_NUM_TO_ABK` — Dict mit 26 Einträgen (Kantons-Nummer → Kürzel)
- `KANT_ABK_SET` — Set aller 26 Kürzel

## Migrationen (3 NBs, sehr unterschiedlich)

### K_01 Cell 49 (vorher ~80 Zeilen inline)

```python
# NEU (ca. 15 Zeilen):
_KANT_CANDIDATES = [
    os.path.join(DATA_DIR, 'kantone.gpkg'),
    os.path.join('data', 'kantone.gpkg'),
    os.path.join('data', 'CH_storymap', 'kantone.gpkg'),
]
_ZIP_URL = 'https://data.geo.admin.ch/.../swissboundaries3d_2026-01_2056_5728.gpkg.zip'
_KANT_FILE_TARGET = os.path.join(DATA_DIR, 'kantone.gpkg')

gdf_kant = load_kantone(
    data_dirs=_KANT_CANDIDATES,
    download_url=_ZIP_URL,
    download_target=_KANT_FILE_TARGET,
)
KANTON_ABB_COL = 'KAB' if gdf_kant is not None and 'KAB' in gdf_kant.columns else None
```

**6530 chars → ~1000 chars.**

### K_01c Cell 13 (vorher ~40 Zeilen inline)

```python
# NEU (ca. 8 Zeilen):
_KANT_CANDIDATES = [
    os.path.join(PROD_DATA_DIR, 'kantone.gpkg'),
    os.path.join(PROD_DATA_DIR, 'swissboundaries3d.gpkg'),
    os.path.join(DATA_DIR, 'swissBOUNDARIES3D_1_5_TLM_KANTONSGEBIET.gpkg'),
    os.path.join('..', 'data', 'raw', 'kantone.gpkg'),
]
gdf_kant = load_kantone(data_dirs=_KANT_CANDIDATES)
```

**2084 chars → ~450 chars.** CH_OUTLINE-Fallback bleibt nach dem Block unverändert.

### K_01d (vorher 2× def)

```python
# NEU:
gdf_kant = load_kantone([
    os.path.join(PROD_DATA_DIR, 'kantone.gpkg'),
    os.path.join(PROD_DATA_DIR, 'swissboundaries3d.gpkg'),
])
```

**Alle 3 Aufrufe** (Cell 9 original, Cell 19, Cell 23) auf die neue lib-Signatur umgestellt. Beide lokalen Defs entfernt.

## Qualitäts-Checks (alle ✅)

| Check | Status |
|---|---|
| `lib/grid_topo.py` syntaktisch valide | ✅ |
| Import + API-Signatur korrekt | ✅ |
| `KANT_NUM_TO_ABK` hat 26 Einträge | ✅ |
| K_01: 0 lokale defs, 1 lib-Aufruf, AST valide | ✅ |
| K_01c: 0 lokale defs, 1 lib-Aufruf, AST valide | ✅ |
| K_01d: 0 lokale defs, 3 lib-Aufrufe, AST valide | ✅ |
| Alle 3 NBs haben `from lib.grid_topo import load_kantone` | ✅ |
| Alle bisherigen K_01d-Fixes (quotechar, EXP_RAW_DIR, log_dataindex, TOC) erhalten | ✅ |

## Installation

```bash
cp <ZIP>/lib/grid_topo.py lib/
cp <ZIP>/patched_notebooks/kuer/K_01_Raeumliche_Analyse.ipynb kuer/
cp <ZIP>/patched_notebooks/experimental/K_01c_Energiefluss_Animationen.ipynb experimental/
cp <ZIP>/patched_notebooks/experimental/K_01d_Grid_Topologie.ipynb experimental/
```

## Was NICHT in grid_topo.py ist

Bewusste Entscheidungen:

- **`load_pypsa_zenodo`** (172 Zeilen in K_01d) — bleibt NB-lokal, zu spezifisch für K_01d-Workflow (nutzt viele globale Konstanten wie `BB`, `ZENODO_RECORD`, `CC_CODE`, spezielles Schema)
- **`in_bbox`, `clean_name`** (4-6 Zeilen) — trivial, bleiben NB-lokal
- **`compute_edge_flows`, `get_border_flows`** — spezifisch für K_01d's Zonenfluss-Modell
- **`cluster_plants`** (K_01c) — NB-lokal, nicht dupliziert

## lib/-Stand (final Phase 6 + 7)

```
lib/
├── plotting.py          ✅  show_source, should_skip, make_gif_chart, show_chart
├── widgets.py           ✅  slide_or_play, show_animation
├── io_ops.py            ✅  log_dataindex, load_transfer, save_transfer,
│                              needs_download, needs_rebuild, log_missing
├── data_fetchers.py     ✅  fetch_entsoe_yearly
├── simulation.py        ✅  simulate_battery_dispatch
├── columns.py           ✅  find_col
└── grid_topo.py         ✅  load_kantone, KANT_NUM_TO_ABK, KANT_ABK_SET   ← NEU
```

## Lektion (erneut)

Zweiter Fall in Folge, wo ich zu eng gesucht hab. Erst bei log_dataindex (nur im Phase-4d-Output statt verified_3a), jetzt bei load_kantone (nur nach `def` statt auch nach inline-Code). Das Prinzip *"Inspektion gegen volle Baseline"* muss für mich **auch die Such-Pattern breit genug** machen — nicht nur welche Dateien ich durchsuche, sondern auch **nach welchen Mustern** ich in ihnen suche.

Konkret für künftige Inspektionen: **nicht nur `def fn_name` suchen, sondern auch die konstanten die typischerweise mit der Funktion einhergehen** (hier: `KANT_NUM_TO_ABK`, `KANT_CANDIDATES`). Das hätte K_01 und K_01c sofort als Duplikate entlarvt.

## Nächster Schritt

Phase 7 damit wirklich abgeschlossen. Als nächstes Phase 8 (Doku-Update) oder Phase 9 (Regressionstest).
