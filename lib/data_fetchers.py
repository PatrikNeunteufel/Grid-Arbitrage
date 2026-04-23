"""lib.data_fetchers — API-Downloads für externe Datenquellen.

Dieses Modul bündelt die Download-Funktionen für:

* ENTSO-E Transparency Platform (Day-Ahead-Preise, Netzlast, Grenzflüsse)
* BFS PXWeb (kantonale Bevölkerungsdaten)
* PyPSA-Eur Zenodo-Archiv (Netz-Topologie)
* Kantonsgrenzen (swissBOUNDARIES3D)

**Status:** Platzhalter. Die Funktionen werden in Phase 6a/6b/6d
aus den Notebooks hierher verschoben.

Quelle der aktuell noch in Notebooks liegenden Originale:

* ``_fetch_prices_year``      — notebooks/01_Daten_Laden.ipynb, Cell 12
* ``_fetch_load_year``        — notebooks/01_Daten_Laden.ipynb, Cell 16
* ``_fetch_crossborder_year`` — kuer/K_02_Cross_Border.ipynb, Cell 9
* ``fetch_bfs_pxweb``         — kuer/K_01_Raeumliche_Analyse.ipynb, Cell 21
* ``load_pypsa_zenodo``       — experimental/K_01d_Grid_Topologie.ipynb, Cell 14
* ``load_kantone``            — experimental/K_01d_Grid_Topologie.ipynb, Cell 7

Siehe Refactoring_Plan.md §6a, §6b, §6d.
"""

from __future__ import annotations

# Migration erfolgt in Phase 6a/6b/6d — aktuell keine Exports.
