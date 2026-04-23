"""lib.columns — Column-Mapping und Utility-Funktionen für DataFrames/GeoDataFrames.

Dieses Modul bündelt kleine Helper rund um Spalten-Erkennung in heterogenen
Quelldaten (ENTSO-E, BFE, BFS unterscheiden sich in der Spaltenbenennung):

* ``find_col``    — findet die tatsächliche Spaltenbezeichnung zu einer Liste
                    möglicher Aliases (case-insensitive, substring-basiert)
* ``map_et``      — Mapping BFE-SubCategory-Codes → Energieträger-Gruppen
* ``clean_name``  — Säubert Knoten-/Kantennamen (OSM-Tags)
* ``in_bbox``     — Bounding-Box-Test für Koordinaten

**Status:** Platzhalter. Die Funktionen werden in Phase 6b/6d
aus den Notebooks hierher verschoben.

Quelle der aktuell noch in Notebooks liegenden Originale:

* ``find_col``    — kuer/K_01_Raeumliche_Analyse.ipynb, Cell 15
                    (identisches Duplikat in K_01b, Cell 12)
* ``map_et``      — kuer/K_01_Raeumliche_Analyse.ipynb, Cell 15
* ``clean_name``  — experimental/K_01d_Grid_Topologie.ipynb, Cell 17
* ``in_bbox``     — experimental/K_01d_Grid_Topologie.ipynb, Cell 17

Siehe Refactoring_Plan.md §6b, §6d.
"""

from __future__ import annotations

# Migration erfolgt in Phase 6b/6d — aktuell keine Exports.
