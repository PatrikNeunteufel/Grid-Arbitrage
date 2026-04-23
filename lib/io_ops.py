"""lib.io_ops — Datei-I/O, Provenienz und Download-Gating.

Dieses Modul bündelt Utilities rund um:

* Auffinden der Projekt-Wurzel (``_find_project_root``)
* Dataindex-Logging für Provenienz (``log_dataindex``, ``log_missing``)
* Entscheidung, ob ein Download/Rebuild nötig ist (``needs_download``, ``needs_rebuild``)

**Status:** Platzhalter. Die Funktionen werden in Phase 6a (NB01, NB02, NB03)
aus den Notebooks hierher verschoben. Bis dahin bleibt dieses Modul leer.

Quelle der aktuell noch in Notebooks liegenden Originale:

* ``_find_project_root``   — experimental/K_01d_Grid_Topologie.ipynb, Cell 4
* ``log_dataindex``        — notebooks/01_Daten_Laden.ipynb, Cell 10
                             (identische Duplikate in 02, 03, K_01, K_02)
* ``log_missing``          — notebooks/01_Daten_Laden.ipynb, Cell 10
                             (identische Duplikate in 02, 03)
* ``needs_download``       — notebooks/01_Daten_Laden.ipynb, Cell 8
* ``needs_rebuild``        — notebooks/02_Daten_Bereinigung.ipynb, Cell 10

Siehe Refactoring_Plan.md §6a.
"""

from __future__ import annotations

# Migration erfolgt in Phase 6a — aktuell keine Exports.
