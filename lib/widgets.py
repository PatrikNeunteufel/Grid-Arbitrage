"""lib.widgets — Interaktive ipywidgets-Komponenten für Notebooks.

**Status:** Platzhalter. In Phase 5 wird hier ``slide_or_play`` angelegt —
ein robuster Frame-Viewer mit Slider + Play-Button für Animations-Output.

Die neue Version wird gegenüber der bestehenden (experimental/K_01d
Cell 30) zwei Verbesserungen enthalten:

1. **GIF-Fallback** wenn ipywidgets nicht rendert (Problem aktuell real:
   Frames werden geladen, aber VBox-Repr erscheint als Plain-Text).
2. **base_dir-Parameter** statt globalem EXP_CHARTS_DIR.

Diagnose-Hinweise bei Widget-Rendering-Problemen siehe Docstring von
``slide_or_play`` (wird in Phase 5 geschrieben).

Siehe Refactoring_Plan.md §5.

Quelle der zu migrierenden Funktionen:

* ``slide_or_play``       — experimental/K_01d_Grid_Topologie.ipynb, Cell 30
                            (nach Phase 3d Move, vorher
                            K_01d_Grid_Topologie_slider.ipynb, Cell 30)
* ``_find_frame_dir``     — ebenda
"""

from __future__ import annotations

# Migration erfolgt in Phase 5 — aktuell keine Exports.
