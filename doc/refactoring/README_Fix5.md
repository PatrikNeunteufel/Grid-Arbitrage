# Fix — `show_animation` Konsistenz in K_00, K_01, K_04, K_01c

## Ausgangslage

Du hast festgestellt (nach meinem falschen Scan gegen `verified_3a`):

**K_01d ist der Lead-Standard** — nutzt `show_animation` aus `lib.widgets` in
5 Zellen korrekt. Die anderen 4 NBs haben unterschiedliche Muster:

| NB | Vorher | Migriert zu |
|---|---|---|
| **K_00** | `show_chart('*.gif', ...)` für Animationen | `show_animation(os.path.join(CHARTS_DIR, '*.gif'), mode='gif', ...)` |
| **K_01** | `make_gif_chart(...)` ohne Anzeige | `make_gif_chart(...)` + neue Zelle mit `show_animation(...)` |
| **K_04** | `make_gif_chart(...)` ohne Anzeige | `make_gif_chart(...)` + neue Zelle mit `show_animation(...)` |
| **K_01c** | `display(Image(filename=_p))` | `show_animation(_p, mode='gif', framerate=10)` |

**K_01d:** nicht angefasst — ist Referenz. Deine `OV_BILANZ_POS = (0.04, 0.75)`
und alle anderen Overlay-Settings bleiben erhalten.

## Was gemacht wurde

### K_00_Business_Strategy

- Bootstrap erweitert: `from lib.widgets import show_animation`
- 5 `show_chart('*.gif', ...)`-Aufrufe umgeschrieben zu `show_animation(...)`:
  - `width` und `caption` werden korrekt übernommen
  - Pfad wird via `os.path.join(CHARTS_DIR, 'filename.gif')` gebildet
  - `mode='gif'`, `framerate=10` als Standard
- **`show_chart`-Aufrufe für PNG/JPG bleiben unverändert** — das ist weiterhin
  die richtige Funktion für statische Bilder

Beispiel:
```python
# Vorher:
show_chart('kuer_k04_anim_C_spread.gif',
           'Animation C: Arbitrage-Spread ...',
           width=900)

# Nachher:
show_animation(os.path.join(CHARTS_DIR, 'kuer_k04_anim_C_spread.gif'),
               mode='gif', framerate=10, width=900,
               caption='Animation C: Arbitrage-Spread ...')
```

### K_01_Raeumliche_Analyse

- Bootstrap erweitert: `from lib.widgets import show_animation`
- Cell 79 (hat `make_gif_chart(fig_a, update_k01, HOUR_TIMES, ANIM_FPS, gif_path)`)
  bleibt unverändert
- **Neue Zelle direkt danach eingefügt:**
  ```python
  # ── Animation anzeigen ──────────────────────────────────────────────────
  show_animation(gif_path, mode='gif', framerate=10)
  ```
- `show_source(show_animation)`-Block vor erster Verwendung

**Nicht Teil dieses Fixes:** K_01 hat noch eine lokale `def make_gif_chart` in
Cell 10 — das wäre Phase-6.1-Nacharbeit (separater Schritt). Habe ich bewusst
nicht gemacht, um den Scope klein zu halten.

### K_04_Animationen

- Bootstrap hatte bereits `from lib.widgets import show_animation` (seit Phase 5)
- Nach jeder der 3 `make_gif_chart`-Aufrufe (Cells 20, 22, 24) eine neue Zelle:
  ```python
  show_animation(fname, mode='gif', framerate=10)   # bzw. fname_b, fname_c
  ```
- `show_source(show_animation)`-Block vor erster Verwendung

### K_01c_Energiefluss_Animationen

- Bootstrap erweitert: `from lib.widgets import show_animation`
- 10 `display(Image(filename=_p))`-Aufrufe durch
  `show_animation(_p, mode='gif', framerate=10)` ersetzt
- `show_source(show_animation)`-Block vor erster Verwendung

## Qualitäts-Checks (alle ✅)

```
  ✅ K_01d       : lib-import=yes  show_animation-calls= 5  (UNVERÄNDERT)
  ✅ K_01c       : lib-import=yes  show_animation-calls=10  display(Image)=0
  ✅ K_04        : lib-import=yes  show_animation-calls= 3
  ✅ K_01        : lib-import=yes  show_animation-calls= 1
  ✅ K_00        : lib-import=yes  show_animation-calls= 5
```

- Alle neuen Imports syntaktisch valide
- AST aller Code-Zellen in allen 4 NBs: **0 Fehler**
- K_01d unverändert: `OV_BILANZ_POS = (0.04, 0.75)` bestätigt, 5 show_animation-Calls unverändert

## Installation

```bash
cp <ZIP>/patched_notebooks/kuer/K_00_Business_Strategy.ipynb kuer/
cp <ZIP>/patched_notebooks/kuer/K_01_Raeumliche_Analyse.ipynb kuer/
cp <ZIP>/patched_notebooks/kuer/K_04_Animationen.ipynb kuer/
cp <ZIP>/patched_notebooks/experimental/K_01c_Energiefluss_Animationen.ipynb experimental/
```

K_01d: **nicht im Paket** — bleibt wie er ist.

## Nach dem Einspielen: `run_all.bat` empfohlen

Weil dies eine inhaltliche Änderung der Anzeige-Logik ist, lohnt ein
Regressionslauf, um sicherzugehen dass keine der neuen `show_animation`-Zellen
unerwartete Fehler wirft. Die Funktion wird in K_01d seit Phase 5 produktiv
genutzt, sollte also stabil sein.

## Nicht gemacht (bewusst)

- **K_01 `def make_gif_chart`**: Cell 10 hat noch die alte lokale Def — das
  ist Phase-6.1-Nacharbeit, wäre ein separater Schritt. Risiko klein halten.
- **K_01c `make_gif_fast`**: lokale Anim-Erzeugungs-Fn, nicht Teil der lib.
  Wäre eine Konsolidierungs-Frage für Phase 6.x falls gewünscht.
- **K_01d selbst**: nicht angefasst.

## Nächster Schritt

Nach Install + run_all — weiter mit Phase 8 (Doku-Update) oder bei erkannten
Regressions zurück zum Fix.
