"""lib.simulation — Dispatch-Algorithmen und Wirtschaftlichkeitsrechnung.

Dieses Modul bündelt die Batterie-Dispatch- und Business-Case-Funktionen:

* Reaktiver Quantil-Dispatch (Pflicht-Baseline)
* Day-Ahead-optimaler Dispatch (K_06)
* Hybrid-Simulation Arbitrage + Eigenverbrauch (K_99)
* CAPEX-Lernkurven-Projektion (K_07)
* Break-Even-Berechnungen

**Status:** Platzhalter. Die Funktionen werden in Phase 6a/6b
aus den Notebooks hierher verschoben.

Quelle der aktuell noch in Notebooks liegenden Originale:

* ``simulate_battery``             — notebooks/03_Daten_Analyse.ipynb, Cell 16
* ``simulate_battery_reactive``    — kuer/K_06_Dispatch_Optimierung.ipynb, Cell 11
* ``simulate_battery_da_optimal``  — kuer/K_06_Dispatch_Optimierung.ipynb, Cell 11
* ``sim_arbitrage``, ``sim_ev``,
  ``sim_hybrid``, ``fmt_be``       — kuer/K_99_Kombinierte_Simulation.ipynb, Cell 11
* ``be_est``, ``get_trigger``      — kuer/K_99_Kombinierte_Simulation.ipynb, Cell 21
* ``exp_decay``                    — kuer/K_07_Technologievergleich.ipynb, Cell 14

Siehe Refactoring_Plan.md §6a, §6b.
"""

from __future__ import annotations

# Migration erfolgt in Phase 6a/6b — aktuell keine Exports.
