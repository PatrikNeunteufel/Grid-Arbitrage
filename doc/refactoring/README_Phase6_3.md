# Phase 6.3 — ENTSO-E Retry-Logik nach `lib/data_fetchers.py`

## Scope-Entscheidung nach Inspektion

Projektweite Inspektion der Data-Fetcher ergab:

| Kandidat | Status | Entscheidung |
|---|---|---|
| **ENTSO-E Retry-Logik** | 3× identisch: NB01 (2×: Preise, Last) + K_02 (1×: Grenzflüsse) | **migriert** |
| ENTSO-E API-Connectivity-Check | 1× in NB01 | nicht migriert (Single-Use) |
| BFE GPKG-Download | 1× in K_01 (Rest lädt nur Cache) | nicht migriert (Single-Use) |
| swisstopo/swissboundaries | 1× in K_01 (Rest lädt nur Cache) | nicht migriert (Single-Use) |

## Was 6.3 liefert

### `lib/data_fetchers.py` (neu)

```python
def fetch_entsoe_yearly(query_fn, year, max_retries=3, wait_s=20,
                        tz='Europe/Zurich'):
    """Ruft eine ENTSO-E-Query jahresweise mit 503-Retry auf."""
```

**Design-Prinzip:** Die konkrete Query wird als Callable übergeben (typisch
als Lambda), nicht als Method-Name-String. So funktioniert der Wrapper mit
**jeder** ENTSO-E-Query ohne Änderung am Modul — auch mit solchen, die wir
heute noch nicht nutzen (z.B. `query_generation_per_plant`).

### Vorher / Nachher

**Vorher — 3× identisch in NBs** (je ~18 Zeilen Def + Aufruf):

```python
def _fetch_prices_year(client, year, max_retries=3, wait_s=20):
    """Lädt ein Jahr Day-Ahead-Preise mit Retry bei 503."""
    import time
    from requests.exceptions import HTTPError
    start = pd.Timestamp(f'{year}-01-01', tz='Europe/Zurich')
    end   = pd.Timestamp(f'{year}-12-31 23:00', tz='Europe/Zurich')
    for attempt in range(1, max_retries + 1):
        try:
            ts = client.query_day_ahead_prices('CH', start=start, end=end)
            return ts
        except HTTPError as e:
            if '503' in str(e) and attempt < max_retries:
                print(...)
                time.sleep(wait_s)
            else:
                raise

# Aufruf:
ts_year = _fetch_prices_year(client, year)
```

**Nachher — 3 Zeilen statt 18:**

```python
ts_year = fetch_entsoe_yearly(
    lambda s, e: client.query_day_ahead_prices('CH', start=s, end=e),
    year)
```

## Gepatchte NBs

| NB | Vorher | Nachher |
|---|---|---|
| `notebooks/01_Daten_Laden` | 2 Retry-Defs + 2 Aufrufe | 2 Aufrufe via Helper |
| `kuer/K_02_Cross_Border` | 1 Retry-Def + 2 Aufrufe | 2 Aufrufe via Helper |

Spart ca. **36 Zeilen duplizierten Code**.

## Bootstrap-Erweiterung

**NB01** hatte schon Bootstrap aus Phase 6.2c — nur erweitert um:
```python
from lib.data_fetchers  import fetch_entsoe_yearly
```

**K_02** hatte noch keinen Bootstrap (war nicht in Phase 6.2 dabei) — neu eingefügt.

## show_source-Block

In beiden NBs vor der ersten Verwendung von `fetch_entsoe_yearly`:

```markdown
**🔎 Quellcode der importierten lib-Funktion**

Die Funktion `fetch_entsoe_yearly` wird aus `lib/data_fetchers.py`
importiert und kapselt die jahresweise ENTSO-E-Abfrage mit 503-Retry. ...
```

## Qualitäts-Checks (alle ✅)

| Check | Status |
|---|---|
| `lib/data_fetchers.py` syntaktisch valide | ✅ |
| Import `fetch_entsoe_yearly` funktioniert | ✅ |
| NB01: 0 `_fetch_*_year`-Aufrufe mehr, 2 neue Helper-Aufrufe | ✅ |
| K_02: 0 `_fetch_*_year`-Aufrufe mehr, 2 neue Helper-Aufrufe | ✅ |
| AST-Validierung aller Code-Zellen | ✅ |

## Installation

```bash
cp <ZIP>/lib/data_fetchers.py lib/
cp <ZIP>/patched_notebooks/notebooks/01_Daten_Laden.ipynb notebooks/
cp <ZIP>/patched_notebooks/kuer/K_02_Cross_Border.ipynb kuer/
```

## Hinweis — parallel dazu

Die K_01d-Fixes aus den letzten Patches (CSV-Quoting + Raw/Intermediate-Trennung
+ log_dataindex) sind bereits eingepflegt und im aktualisierten
`Refactoring_Plan.md` als abgeschlossen vermerkt. Die neue Daten-Konvention
(Rohdaten → `data/raw/<quelle>/`, Zwischenergebnisse → `data/intermediate/`,
jeder Write mit `log_dataindex()`) steht ab jetzt im Plan — gilt für **alle**
NBs (Pflicht, Kür, experimental).

## lib/-Stand nach 6.3

```
lib/
├── __init__.py          ✅
├── plotting.py          ✅  show_source, should_skip, make_gif_chart
├── widgets.py           ✅  slide_or_play, show_animation
├── io_ops.py            ✅  log_dataindex, load_transfer, save_transfer
├── data_fetchers.py     ✅  fetch_entsoe_yearly
├── simulation.py        ⏳  Phase 6.4 (hoch Risiko)
├── columns.py           ⏳  Phase 6.5
└── grid_topo.py         ⏳  Phase 7
```

## Nächster Schritt

**Phase 6.4** — `lib/simulation.py` für Dispatch-Sim aus NB03 und K_06.
Markiert als **hoch Risiko**, weil diese Funktionen die zentralen Kennzahlen
des Projekts bestimmen (ROI, Payback, Break-Even). Vor dem Mergen muss
verifiziert werden, dass die Resultate identisch bleiben — z.B. über einen
Hash der erzeugten CSV oder einen numerischen Vergleich der Kennzahlen.
