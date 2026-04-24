# Phase 6.4b — `sim_arbitrage` aus K_99 entfernt (toter Code)

## Überraschung beim Nachprüfen

Auf deine Frage hin — *"müssen die unterschiedlich berechnet werden?"* — habe
ich K_99 nochmal gründlich angeschaut und einen wichtigen Befund gemacht:

**`sim_arbitrage()` wird in K_99 DEFINIERT, aber NIEMALS aufgerufen.**

Die Arbitrage-Kennzahlen in K_99 kommen **stattdessen direkt aus NB03** via
Transfer-Mechanismus:

```python
# K_99 Cell 10 — Arbitrage-Basiswerte aus NB02
ARB_ROI = dict(zip(df_econ["segment"], df_econ["roi_pct"]))
ARB_NET = dict(zip(df_econ["segment"], df_econ["net_annual"]))
```

Und im Haupt-Sim-Loop (Cell 12):
```python
# Arbitrage-Only: direkt aus NB02-wirtschaftlichkeit.csv (SSOT)
# So bleiben Chart 1b (NB02) und der Arb-Balken hier konsistent.
# ...
arb_net = ARB_NET.get(seg, 0)   # netto EUR/Jahr aus wirtschaftlichkeit.csv
arb_roi = ARB_ROI.get(seg, 0)   # ROI % aus wirtschaftlichkeit.csv
```

## Konsequenz

Die ganze vorherige Diskussion um Dispatch-Modell-Divergenz (symmetrische vs.
charge-only η-Verbuchung) war **numerisch irrelevant** — weil `sim_arbitrage`
nie benutzt wurde, hat sein interner Modell-Unterschied auf **keine einzige
Abgabe-Kennzahl** Auswirkung.

**Die Kohärenz war also schon da** — nur nicht durch gemeinsame Funktion,
sondern durch **Ergebnis-Transfer**. Das Projekt nutzt bereits eine einzige
Arbitrage-Sim (NB03), K_99 liest nur die Ergebnisse.

## Was Phase 6.4b macht

Die tote `def sim_arbitrage(...)` wird ersatzlos gelöscht (694 chars) und
durch einen Kommentar ersetzt, der die Situation dokumentiert:

```python
# -- Simulationsfunktionen -------------------------------------------------
# Hinweis: Arbitrage-Only-Kennzahlen kommen direkt aus NB03 via Transfer
# (ARB_NET/ARB_ROI dicts in Cell 10). Eine lokale Arbitrage-Sim hier wäre
# redundant und würde Datenperioden-Abweichungen riskieren (siehe Kommentar
# unten in der Simulations-Schleife). Deshalb nur sim_ev und sim_hybrid.
# Für die Arbitrage-Sim siehe lib/simulation.simulate_battery_dispatch.
EV_FRAC_STATIC  = 0.70
VERBRAUCH_TAG   = 10.0

def sim_ev(cap_kwh, pow_kw, verbrauch_j, n_years):
    ...

def sim_hybrid(prices, cap_kwh, pow_kw, verbrauch_j, n_years, optimized=False):
    ...
```

`sim_ev` und `sim_hybrid` **bleiben unverändert** — sie werden tatsächlich
aufgerufen (Cell 12 Zeilen 117-119).

## Keine numerische Verifikation nötig

Anders als bei Phase 6.4 braucht es hier **keinen Before/After-Vergleich** —
weil die gelöschte Funktion nie aufgerufen wurde, kann kein Ergebnis sich
ändern. Transfer-File-Inhalte, ROI-Werte, Business-Case-Zahlen: alle identisch.

## Qualitäts-Checks (alle ✅)

| Check | Status |
|---|---|
| AST-Validierung aller Code-Zellen | ✅ |
| 0 `def sim_arbitrage` mehr | ✅ |
| 0 `sim_arbitrage`-Referenzen projektweit | ✅ |
| `sim_ev` + `sim_hybrid` bleiben erhalten | ✅ |

## Projektweiter Dispatch-Sim-Stand nach 6.4b

```
lib.simulation.simulate_battery_dispatch()   ← die eine, zentrale Dispatch-Sim

  ├── NB03: nutzt direkt (Cell 24 via simulate_battery_dispatch)
  └── K_06: nutzt via Wrapper (simulate_battery_reactive → .cashflow_eur.sum())

K_99 nutzt nicht lokal — nimmt die Ergebnisse per Transfer aus NB03
K_99 hat nur noch sim_ev (Haushaltstarife) und sim_hybrid (Partition-Modell)
```

## Installation

```bash
cp <ZIP>/patched_notebooks/kuer/K_99_Kombinierte_Simulation.ipynb kuer/
```

## Lektion

Der dritte Fall wo gründliche Inspektion neue Erkenntnisse bringt — diesmal
aber positiv: **das Projekt war schon kohärenter als beim ersten Blick
erkennbar**. Der Autor von K_99 hat das Muster "sim-Funktion schreiben, aber
Ergebnisse aus Transfer lesen" genutzt um genau die Kohärenz sicherzustellen,
die wir jetzt diskutieren — die lokale `sim_arbitrage`-Funktion war
vermutlich ein Überbleibsel von einer früheren Iteration, in der sie noch
aufgerufen wurde, und wurde beim Umbau auf Transfer-basierte Arbitrage-Werte
nicht aufgeräumt.

## Refactoring_Plan.md — Nachtrag

Phase 6.4 ist mit 6.4b wirklich abgeschlossen. Im Plan unter 6.4 noch
nachtragen: *"sim_arbitrage in K_99 als toter Code entfernt; einzige
Dispatch-Sim projektweit ist jetzt lib.simulation.simulate_battery_dispatch."*
