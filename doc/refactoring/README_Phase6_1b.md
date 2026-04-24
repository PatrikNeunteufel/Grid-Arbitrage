# Phase 6.1b — `show_chart` nach `lib/plotting.py`

## Selbstkorrektur + saubere Inspektion

Gut dass du nachgefragt hast. Beim ersten Grep-Lauf hatte ich **13 NBs mit "show()-Aufrufen"** im Report — alle falsch positiv: das waren `plt.show()` und `ax.imshow(...)` die durch eine ungenaue Heuristik als Aufrufe von `show` gezählt wurden.

**Tatsächlich existierten nur 3 lokale Defs mit ähnlicher Semantik:**

| NB | Name | Signatur |
|---|---|---|
| K_00 | `show` | `(filename, caption='', width=1100)` |
| K_00 | `show_anim` | `(filename, caption='', width=1100)` |
| NB00 | `show_chart` | `(filename, caption='', width=950)` |

Alle drei machen dasselbe: PNG/GIF aus `CHARTS_DIR` laden, mit `display(Image(...))` bzw. `HTML(<img>)` anzeigen, optional Caption.

## Neue lib-Funktion

```python
def show_chart(filename, caption='', width=950, charts_dir=None, as_html=None):
    """Zeigt einen erzeugten Chart (PNG, JPG, GIF) aus einem Charts-Verzeichnis."""
```

**Verbesserungen gegenüber den drei lokalen Varianten:**

- **Automatische GIF-Erkennung:** `as_html=None` (Default) → `.gif`-Endung → HTML-Renderer, sonst `Image`. Damit entfällt die Notwendigkeit eines separaten `show_anim`.
- **Expliziter charts_dir-Parameter:** Wenn `None`, wird die globale `CHARTS_DIR` im Caller-Scope gesucht (Rückwärtskompatibilität).
- **Default-Width 950:** häufigster Wert in bestehenden Aufrufen.

## Gepatchte NBs

### K_00 (`kuer/K_00_Business_Strategy.ipynb`)

- **2 lokale Defs entfernt:** `show` + `show_anim`
- **30 Aufrufe umgestellt:**
  - 25× `show(...)` → `show_chart(...)`
  - 5× `show_anim(...)` → `show_chart(...)` (GIF wird via Dateiendung automatisch als HTML gerendert)
- Bootstrap erweitert: `from lib.plotting import show_source, show_chart`
- show_source-Block vor erster Verwendung

### NB00 (`notebooks/00_Business_Case.ipynb`)

- **1 lokale Def entfernt:** `show_chart`
- **12 Aufrufe bleiben unverändert** — heissen schon `show_chart(...)`, Signatur kompatibel
- Bootstrap erweitert
- show_source-Block vor erster Verwendung

## Qualitäts-Checks (alle ✅)

| Check | Status |
|---|---|
| `lib/plotting.py` syntaktisch valide | ✅ |
| Import `show_chart` funktioniert | ✅ |
| K_00: 0 lokale show/show_anim defs mehr | ✅ |
| K_00: 30 show_chart-Aufrufe, 0 show_anim-Reste | ✅ |
| NB00: 0 lokale show_chart def mehr | ✅ |
| AST-Validierung aller Code-Zellen | ✅ |
| Keine Regex-Kollisionen (kein `show_chart_chart`, `plt.show_chart` etc.) | ✅ |
| `plt.show()` und `ax.imshow(...)` bleiben unangetastet | ✅ |

## Width-Default-Hinweis

Der neue Default `width=950` entspricht dem vorigen NB00-Default. In K_00
war der Default vorher `1100`, aber **95% der K_00-Aufrufe haben explizite
width** (häufigster Wert: 900). Die wenigen K_00-Aufrufe ohne width sind
jetzt bei 950 statt 1100 — ein ca. 14% schmaleres Bild. Falls das auffällt,
kann im Call explizit `width=1100` gesetzt werden.

Verteilung in beiden NBs: `[(900, 22), (950, 5), (1050, 5), (1100, 4), (800, 4), (850, 3), (1000, 2)]`

## Installation

```bash
cp <ZIP>/lib/plotting.py lib/
cp <ZIP>/patched_notebooks/kuer/K_00_Business_Strategy.ipynb kuer/
cp <ZIP>/patched_notebooks/notebooks/00_Business_Case.ipynb notebooks/
```

## lib/-Status nach 6.1b

```
lib/
├── plotting.py          ✅  show_source, should_skip, make_gif_chart, show_chart  ← NEU
├── widgets.py           ✅  slide_or_play, show_animation
├── io_ops.py            ✅  log_dataindex, load_transfer, save_transfer
├── data_fetchers.py     ✅  fetch_entsoe_yearly
├── simulation.py        ⏳  Phase 6.4
├── columns.py           ⏳  Phase 6.5
└── grid_topo.py         ⏳  Phase 7
```

## Anmerkung zu `show_animation` (aus lib/widgets.py)

Das ist eine **andere Funktion**: `show_animation` (aus Phase 5) erzeugt die
slide-or-play-Widget-Anzeige (interaktiver Frame-Slider) für frisch
erzeugte GIFs direkt in den Animations-NBs (K_01, K_04, K_01c, K_01d).

`show_chart` (neu) zeigt **bereits gespeicherte** Dateien an — typisch in
Business-Case-/Strategy-NBs, die Outputs von Analysen anderer NBs einbinden.

Beide Funktionen koexistieren ohne Konflikt — unterschiedliche Use Cases.

## Prinzip für die nächsten Phasen

Nach dem zweiten Fall von zu-enger-Scope-Inspektion (log_dataindex-Nachzug,
und jetzt die falsch-positiven "show"-Aufrufe): **Inspektions-Regex-Patterns
projektweit immer mit negativen Beispielen testen.** Bei Verdacht auf
falsche Matches die Aufruf-Zeilen im Kontext zeigen lassen, nicht nur die
Anzahl zählen.
