# Phase 6.2 — Nachzug: log_dataindex-Migration in 4 weiteren NBs

## Der übersehene Scope

In Phase 6.2 schrieb ich: *"log_dataindex ist genau 1x definiert (K_01 Cell 9), wird aber nur in K_01 genutzt"*. Das war falsch — ich hatte damals im zu engen Scope gesucht (nur im Phase-4d-Output, das nur 4 NBs enthielt).

**Tatsächlicher Stand der Baseline (verified_3a):** 5 NBs hatten lokale `def log_dataindex`:

| NB | In Phase 6.2 migriert? |
|---|---|
| `kuer/K_01_Raeumliche_Analyse` | ✅ (damals migriert) |
| `notebooks/01_Daten_Laden` | ❌ übersehen |
| `notebooks/02_Daten_Bereinigung` | ❌ übersehen |
| `notebooks/03_Daten_Analyse` | ❌ übersehen |
| `kuer/K_02_Cross_Border` | ❌ übersehen |

Guter Catch — das sollte konsistent sein.

## Was der Nachzug macht

In den 4 betroffenen NBs:

1. **Lokale `def log_dataindex(...)`-Funktion entfernen** (~18 Zeilen je NB)
2. **Bootstrap erweitern** um `log_dataindex`-Import
3. **`show_source`-Block** vor der ersten Verwendung (Konvention aus 4d/5c/6.1)
4. **Aufrufe bleiben unverändert** — die lib-Version ist signatur-kompatibel
   (mit Fallback auf die globale `DATAINDEX`-Variable im Caller-Scope)

Ergebnis:

| NB | Bootstrap | Lokale def | show_source | Aufrufe |
|---|---|---|---:|---:|
| `notebooks/01_Daten_Laden` | erweitert | Cell 12 entfernt | Cell 12 | 3 |
| `notebooks/02_Daten_Bereinigung` | erweitert | Cell 16 entfernt | Cell 16 | 2 |
| `notebooks/03_Daten_Analyse` | erweitert | Cell 16 entfernt | Cell 16 | 4 |
| `kuer/K_02_Cross_Border` | erweitert | Cell 9 entfernt | Cell 13 | 2 |

## Projektweiter Endstand nach Nachzug

```
Keine lokale `def log_dataindex` mehr — alle NBs nutzen lib/io_ops.log_dataindex
```

| NB | Aufrufe | lib-Import |
|---|---:|---|
| `kuer/K_01_Raeumliche_Analyse` | 4 | ✅ |
| `kuer/K_02_Cross_Border` | 2 | ✅ |
| `notebooks/01_Daten_Laden` | 3 | ✅ |
| `notebooks/02_Daten_Bereinigung` | 2 | ✅ |
| `notebooks/03_Daten_Analyse` | 4 | ✅ |

Gesamt **15 Aufrufe** via eine einzige lib-Definition — vorher **5 lokale Duplikate** (in 3 verschiedenen Varianten).

## Ein Muster das sich wiederholt hat

Zur Ehrlichkeit: das ist der zweite Fall wo ein Duplikations-Check im zu engen Scope lief (nach Phase 6.2 transfer.json — wo du es auch gemerkt hast). **Lektion:** Bei jeder projektweiten Inspektion immer gegen die vollständige Baseline (`verified_3a`) suchen, nicht gegen den aktuellen Phase-Output.

Das ist jetzt als Prinzip im Plan festgehalten (ich kann es nachtragen wenn gewünscht).

## Qualitäts-Checks (alle ✅)

| Check | Status |
|---|---|
| AST-Validierung aller Code-Zellen in allen 4 NBs | ✅ |
| 0 lokale `def log_dataindex` projektweit | ✅ |
| Alle NBs haben `from lib.io_ops import log_dataindex` | ✅ |
| show_source-Block pro NB einmal vor erster Verwendung | ✅ |
| 15 Aufrufe insgesamt verteilt über 5 NBs | ✅ |

## Installation

```bash
cp <ZIP>/patched_notebooks/notebooks/*.ipynb notebooks/
cp <ZIP>/patched_notebooks/kuer/K_02_Cross_Border.ipynb kuer/
```

⚠️ Voraussetzung: `lib/io_ops.py` aus Phase 6.2 muss installiert sein.

## Ausserhalb des Scopes

K_01 war bereits in Phase 6.2 migriert — nicht im Nachzug enthalten, keine Regression.

## lib/-Stand unverändert

```
lib/
├── plotting.py          ✅  show_source, should_skip, make_gif_chart
├── widgets.py           ✅  slide_or_play, show_animation
├── io_ops.py            ✅  log_dataindex, load_transfer, save_transfer
├── data_fetchers.py     ✅  fetch_entsoe_yearly
├── simulation.py        ⏳  Phase 6.4
├── columns.py           ⏳  Phase 6.5
└── grid_topo.py         ⏳  Phase 7
```

## Nächster Schritt

Phase 6.4 — `lib/simulation.py` Dispatch-Sim.
