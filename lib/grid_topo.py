"""lib.grid_topo — Netz-Topologie, Flussmodell, Animations-Rendering (K_01d).

Dieses Modul bündelt die ~70 Funktionen der K_01d-Topologie-Analyse:

* **Accessoren** (Cell 24): Daten-Zugriff für Stunden/Wochen-Zeitreihen
  (solar_h, hydro_h, cons_h, zone_produktion_h/w, ch_produktion_h/w, ...)
* **Grid-Compute** (Cell 25): Fluss-Modell auf Graph-Kanten
  (compute_edge_flows, get_border_flows, _find_border_hub)
* **Render-Core** (Cell 29): Basis-Rendering und GIF-Pipeline
  (_render_grid_background, make_gif_fast_d, precompute_flow_cache)
* **Overlay-Zeichner** (Cell 29): Einzelne Visualisierungselemente
  (draw_overlay_*, draw_zonen_imbalance_labels, draw_all_static_overlays,
  draw_all_dynamic_overlays)
* **Draw-Misc** (Cell 29): Engpässe, Flow-Dots, Border-Flow, Zeitlabel
* **Factories** (Cell 30/31/32/39/40): dyn-Updater, Smooth/Tagesmittel-Wrapper

**Status:** Platzhalter. Die Migration erfolgt in Phase 6d. Achtung: mehrere
Funktionen referenzieren aktuell globale Variablen (ZONE_PROD_INSTALLED, CF,
CF_SEASONAL, ZONE_BASE_CONS). Beim Umzug werden diese zu expliziten
Parametern oder durch eine GridContext-Klasse gekapselt (siehe
Refactoring_Plan.md §6d).

**Phase 7 (optional):** Konsolidierung der Smooth/Tagesmittel-Wrapper
zu einer Factory — reduziert die Funktionsanzahl von ~70 auf ~40.

Quelle aller zu migrierenden Funktionen:

* experimental/K_01d_Grid_Topologie.ipynb (nach Phase 3d Move; vorher:
  K_01d_Grid_Topologie_slider.ipynb)

Siehe Refactoring_Plan.md §4.1, §6d, §7.
"""

from __future__ import annotations

# Migration erfolgt in Phase 6d — aktuell keine Exports.
