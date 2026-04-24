# Phase 6.4 — Dispatch-Simulation nach `lib/simulation.py` (hoch Risiko)

## Inspektions-Befund

Projektweite Suche nach Dispatch-/Simulations-Funktionen ergab 4 Kandidaten,
aber **nur 3 sind echte Duplikate — eine Funktion ist ein eigener Algorithmus.**

| Funktion | NB | Status |
|---|---|---|
| `simulate_battery` | NB03 Cell 17 | Haupt-Modell, Referenz-Implementierung (liefert DataFrame) |
| `simulate_battery_reactive` | K_06 Cell 12 | **Byte-gleiche Schleifen-Logik** wie NB03, liefert nur `cashflows.sum()` |
| `simulate_battery_da_optimal` | K_06 Cell 12 | Trivialer Pass-Through zu `_reactive` (bewusst, zeigt geringen Modell-Bias) |
| **`sim_arbitrage`** | **K_99 Cell 12** | **Eigener Algorithmus** — NICHT migriert |
| `roi`, `roi2` | K_99 Cells 12, 24 | inline-nested 1-Zeiler, nicht migrierbar |

**Warum `sim_arbitrage` (K_99) nicht migriert wird:**

- Nutzt globale Module-Level-Constants (`CHARGE_Q`, `SOC_MIN`, `EFFICIENCY`)
  statt Funktions-Arguments
- `np.percentile(..., CHARGE_Q*100)` statt `pd.quantile(charge_q)` —
  subtile Unterschiede bei Interpolation möglich
- Andere SoC-Bounds-Logik: `mxC = min(pow_kw, (SOC_MAX-soc)*cap_kwh/EFFICIENCY)`
  statt `min(power_kw, (soc_max-soc)/sqrt_eff)`
- Zweck: schlankes Hybrid-Modell für K_99 — nicht 1:1 äquivalent

Eine Konsolidierung würde entweder die K_99-Logik ändern (numerisch) oder
die lib-Funktion so aufblähen, dass sie beide Varianten abdeckt. Kein
sinnvoller Trade-off jetzt.

## Die neue lib-Funktion

```python
def simulate_battery_dispatch(prices_df, capacity_kwh, power_kw,
                              efficiency, charge_q, discharge_q,
                              soc_min_pct, soc_max_pct):
    """Schwellenwert-Dispatch auf Basis tagesbasierter Preisquantile."""
```

Kern-Logik 1:1 aus NB03 `simulate_battery` übernommen (die war schon die
Referenz-Implementierung). Return ist der DataFrame mit
`timestamp, action, cashflow_eur, grid_delta_kw`.

## Numerische Verifikation — VOR dem Commit

Ein synthetisches 8760h-Preisprofil (realistisch: Basis + Duck-Curve + Noise
+ 200 negative Preise) wurde durch **beide alte Versionen** UND die neue
lib-Version geschickt. Ergebnis:

```
Row count: 8760 ✅
Spalten: ['timestamp', 'action', 'cashflow_eur', 'grid_delta_kw'] ✅
actions: 100% bit-identisch ✅
cashflow_eur: 100% bit-identisch (max diff = 0.0) ✅
grid_delta_kw: 100% bit-identisch ✅

Cashflow-Summe (= Jahreserlös EUR):
    alt NB03 (DataFrame.sum): 27110.24
    alt K_06 (Skalar):        27110.24
    neu lib (DataFrame.sum):  27110.24
Alle drei identisch: ✅
```

**Bit-identisch, nicht nur `isclose`.** Bei einem hoch-Risiko-Patch ist das
der richtige Standard: gleiche Inputs → gleiche Outputs auf jedem Bit.

## Änderungen je NB

### `notebooks/03_Daten_Analyse.ipynb`

- Lokale `def simulate_battery(...)` (73 Zeilen) entfernt
- Bootstrap erweitert: `from lib.simulation import simulate_battery_dispatch`
- Aufruf umbenannt: `simulate_battery(...)` → `simulate_battery_dispatch(...)`
- show_source-Block vor erster Verwendung

### `kuer/K_06_Dispatch_Optimierung.ipynb`

Die beiden lokalen Defs (`_reactive` und `_da_optimal`) werden durch
**dünne Wrapper** ersetzt — die Kern-Logik steckt in lib, aber die lokalen
Namen bleiben erhalten (damit die bestehenden Call-Sites unverändert sind):

```python
def simulate_battery_reactive(prices_df, capacity_kwh, ...):
    '''Reaktives Modell — Jahreserlös [EUR].'''
    df_disp = simulate_battery_dispatch(prices_df, capacity_kwh, ...)
    return df_disp['cashflow_eur'].sum()

def simulate_battery_da_optimal(prices_df, capacity_kwh, ...):
    '''DA-optimales Modell — identisch zum reaktiven.'''
    return simulate_battery_reactive(prices_df, capacity_kwh, ...)
```

Das hält die Semantik "liefert Skalar, nicht DataFrame" für die K_06-Aufrufer
und dokumentiert gleichzeitig das Pass-Through-Verhältnis.

Bootstrap erweitert, show_source-Block eingefügt.

## Qualitäts-Checks (alle ✅)

| Check | Status |
|---|---|
| `lib/simulation.py` syntaktisch valide | ✅ |
| Import `simulate_battery_dispatch` funktioniert | ✅ |
| **Numerische Verifikation: bit-identisch mit 3 Test-Szenarien** | ✅ |
| NB03: keine lokale `def simulate_battery` mehr | ✅ |
| K_06: keine lokalen Kern-Logik-Defs mehr (nur Wrapper) | ✅ |
| AST-Validierung aller Code-Zellen | ✅ |
| K_99 `sim_arbitrage` unverändert (bewusst, kein Regression-Risiko) | ✅ |

## Installation

```bash
cp <ZIP>/lib/simulation.py lib/
cp <ZIP>/patched_notebooks/notebooks/03_Daten_Analyse.ipynb notebooks/
cp <ZIP>/patched_notebooks/kuer/K_06_Dispatch_Optimierung.ipynb kuer/
```

⚠️ Voraussetzung: die bisherigen lib/-Module aus Phase 6.1–6.3 sind installiert.

## Regressions-Test beim nächsten Lauf

Beim nächsten vollständigen `run_all.sh` sollten **bit-identische** Ergebnisse
in folgenden Outputs entstehen (verglichen mit Vor-Refactoring-Lauf):

- `data/intermediate/<szenario>/wirtschaftlichkeit.csv` (aus NB03)
- `data/intermediate/<szenario>/dispatch_*.csv` (aus K_06)

Falls ein Hash-Vergleich gewünscht ist, kann Phase 9 dies systematisch
abdecken.

## lib/-Status nach 6.4

```
lib/
├── plotting.py          ✅  show_source, should_skip, make_gif_chart, show_chart
├── widgets.py           ✅  slide_or_play, show_animation
├── io_ops.py            ✅  log_dataindex, load_transfer, save_transfer
├── data_fetchers.py     ✅  fetch_entsoe_yearly
├── simulation.py        ✅  simulate_battery_dispatch                ← NEU
├── columns.py           ⏳  Phase 6.5
└── grid_topo.py         ⏳  Phase 7
```

## Nächster Schritt

**Phase 6.5** — `lib/columns.py` für DF-Spalten-Helfer (Normalisierung der
ENTSO-E-Rückgaben, Tages/Wochen/Monats-Resampling). Wie gewohnt: zuerst
projektweit inspizieren gegen `verified_3a`, dann migrieren wo echte
Duplikate sind.

Oder direkt zu **Phase 7** (`lib/grid_topo.py`) — das ist auch klar
umrissen, betrifft aber nur K_01d.
