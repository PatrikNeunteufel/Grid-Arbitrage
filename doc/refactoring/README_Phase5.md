# Phase 5 — slide_or_play nach lib/widgets.py + show_animation-Wrapper

## Was Phase 5 liefert

**`lib/widgets.py`** (neu, ~10 KB) mit zwei öffentlichen Funktionen:

- **`slide_or_play(name_or_path, framerate, image_width, charts_dir)`** —
  interaktiver Frame-Viewer mit Play-Button und Slider. Lädt alle
  `frame_*.png`-Dateien aus einem `_frames/`-Ordner.
- **`show_animation(path, mode, framerate, width, caption)`** — Wrapper, der
  entweder das fertige GIF inline zeigt oder `slide_or_play` aufruft. Über
  den Parameter **`mode='gif'` oder `mode='slider'`** pro Animation frei
  wählbar.

Die Funktion ist allgemein, nicht projektspezifisch — keine Abhängigkeit von
`EXP_CHARTS_DIR` oder anderen globalen Variablen mehr.

## Geänderte Notebooks

### `experimental/K_01d_Grid_Topologie.ipynb`

- **Entfernt:** die Cell mit der eingebetteten `slide_or_play`-Definition
  (~6 KB Code, kommt jetzt aus `lib/widgets.py`)
- **Ersetzt:** 5 GIF-Anzeige-Zellen
  - `display(Image(filename=_p))` → `show_animation(_p, mode='gif')`
- **Unverändert:** die 1 PNG-Anzeige-Zelle (statische Karte) — für PNGs macht
  `slide_or_play` keinen Sinn

### `experimental/K_01c_Energiefluss_Animationen.ipynb`

- **Ersetzt:** 10 GIF-Anzeige-Zellen auf `show_animation(_p, mode='gif')`

### `kuer/K_00_Business_Strategy.ipynb`

- Die bestehende `show_anim(filename, caption, width)`-Funktion bleibt als
  **dünner Wrapper** über `lib.widgets.show_animation` erhalten.
- Neue optionale Parameter: `mode='gif'` (Default) oder `mode='slider'`.
- Alle bestehenden Aufrufstellen in K_00 funktionieren ohne Änderung weiter.
  Wer einen Slider will, schreibt einfach:
  ```python
  show_anim('kuer_k04_anim_A_07h.gif', 'Caption', mode='slider')
  ```

## Das Pattern — pro Animation frei wählbar

Jede Anzeige-Zelle sieht jetzt so aus:

```python
# ── Ausgabe anzeigen ────────────────────────────────────────────
from lib.widgets import show_animation
import os
_p = os.path.join(EXP_CHARTS_DIR, 'EXP_kuer_k01c_gif_a_jahr.gif')
# Umschalten zwischen GIF und interaktivem Slider: mode='gif' oder mode='slider'
show_animation(_p, mode='gif')
```

Du änderst genau **ein Wort** um zwischen GIF und Slider zu wechseln — pro
Animation einzeln, lokal in der Anzeige-Zelle. Kein globaler Schalter, keine
Config-Änderung.

## Voraussetzung für `mode='slider'`

1. **`ipywidgets` muss installiert sein.** `O_00_Installer` → Gruppen
   `kuer_anim` oder `exp_widgets` deckt das ab. Ohne ipywidgets fällt die
   Funktion auf eine Warnung zurück; der Notebook-Lauf bricht nicht ab.

2. **Die Einzelframes müssen gespeichert sein.** Das ist der Fall wenn
   `sync/config.json` → `animation.einzelbilder: true` (ist seit Phase 4a
   Default). Frames landen dann beim GIF-Erzeugen automatisch in
   `<gif_basename>_frames/frame_0000.png`, `frame_0001.png`, ...

3. **Alternativ:** `mode='slider'` funktioniert auch ohne GIF-Datei, solange
   der `_frames/`-Ordner existiert.

## API-Details

### `show_animation(path, mode='gif', framerate=10, width=1100, caption=None)`

| Parameter | Default | Erklärung |
|---|---|---|
| `path` | — | Voller Pfad zur `.gif`-Datei |
| `mode` | `'gif'` | `'gif'` (inline-Anzeige) oder `'slider'` (interaktiv) |
| `framerate` | `10` | fps bei `mode='slider'`. Bei GIF ignoriert. |
| `width` | `1100` | Int = Pixel, Str = CSS (`'100%'`, `'900px'`) |
| `caption` | `None` | Optionale Bildunterschrift |

### `slide_or_play(name_or_path, framerate=10, image_width='100%', charts_dir=None)`

Wird von `show_animation(mode='slider')` intern aufgerufen; direkte Nutzung
nur wenn man zum Beispiel andere Frame-Sequenzen (ohne zugehöriges GIF)
abspielen will.

## Installation

```bash
cd /pfad/zum/projekt

# 1. lib/widgets.py — Ersatz des Phase-1-Platzhalters
cp <ZIP>/lib/widgets.py lib/

# 2. Geänderte Notebooks
cp <ZIP>/patched_notebooks/experimental/K_01c_Energiefluss_Animationen.ipynb experimental/
cp <ZIP>/patched_notebooks/experimental/K_01d_Grid_Topologie.ipynb experimental/
cp <ZIP>/patched_notebooks/kuer/K_00_Business_Strategy.ipynb kuer/

# 3. K_01d_Grid_Topologie_slider.ipynb am Projekt-Root ist damit endgültig obsolet:
rm K_01d_Grid_Topologie_slider.ipynb   # falls noch vorhanden
```

## Qualitäts-Checks

| Check | Status |
|---|---|
| `lib/widgets.py` syntaktisch valide (ast.parse) | ✅ |
| Import `from lib.widgets import slide_or_play, show_animation` | ✅ |
| `show_animation` mit ungültigem `mode` → ValueError | ✅ |
| `show_animation` mit fehlender Datei → saubere Warnung | ✅ |
| K_01d: slide_or_play-Def entfernt (Cell 31) | ✅ |
| K_01d: 5 GIF-Zellen auf show_animation | ✅ |
| K_01d: PNG-Zelle unverändert | ✅ |
| K_01c: 10 GIF-Zellen auf show_animation | ✅ |
| K_00: show_anim als lib-Wrapper, Aufrufstellen unverändert | ✅ |

## Was Phase 5 NICHT macht

- **Keine Migration der GIF-Erzeugung** — die `make_gif_chart`-Funktionen
  in K_01, K_04 etc. bleiben wo sie sind; das ist Phase 6.
- **Keine Tests in K_01** — das NB zeigt Animationen aktuell nicht direkt an
  (nur Erzeugung). Falls später Anzeige-Zellen dort hinzukommen, gilt das
  gleiche Pattern.
- **Keine Änderung in `notebooks/00_Business_Case`** — das NB hat aktuell
  keine GIF-Anzeige-Zellen (nur statische Charts).

## Nächste Phasen

- **Phase 6** — Lib-Migration: Funktionen aus Notebooks nach `lib/`-Modulen
  ziehen (`make_gif_chart`, `show_chart`, `draw_base_map`, Dispatch-Simulation
  etc.) — step-by-step je NB
- **Phase 7** — `grid_topo.py` Konsolidierung (K_01d-Topologie-Helper in ein
  separates Modul)
- **Phase 8** — Dokumentation & Regression-Test
