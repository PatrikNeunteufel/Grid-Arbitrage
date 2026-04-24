# Phase 4d — show_source(should_skip) vor erster Verwendung

Nachtrag zu Phase 4c: in Phase 5c hatten wir bereits `show_source(show_animation)`
vor der ersten Nutzung eingefügt — für `should_skip` wurde das bisher
vergessen. Hiermit nachgeholt.

## Was Phase 4d macht

Vor der jeweiligen `make_gif_*`-Helper-Zelle (in der `should_skip` zum ersten
Mal verwendet wird) wird ein 2-Zellen-Block eingefügt:

- **Markdown-Info** mit Hinweis auf Quellcode
- **Code** `show_source(should_skip)`

## Gepatchte NBs

| NB | Helper-Zelle (jetzt) | show_source-Block vor |
|---|---|---|
| `experimental/K_01c_Energiefluss_Animationen.ipynb` | Cell 21 (`make_gif_fast`) | Cells 19–20 |
| `experimental/K_01d_Grid_Topologie.ipynb` | Cell 33 (`make_gif_fast_d`) | Cells 31–32 |
| `kuer/K_01_Raeumliche_Analyse.ipynb` | Cell 12 (`make_gif_chart`) | Cells 10–11 |
| `kuer/K_04_Animationen.ipynb` | Cell 12 (`make_gif_chart`) | Cells 10–11 |

## Konvention für künftige NBs

Pro lib-Funktion einmal, direkt vor der ersten tatsächlichen Verwendung
(bzw. vor der Zelle, die die Funktion im Körper nutzt):

```markdown
**🔎 Quellcode der importierten lib-Funktion**

Die Funktion `<fn>` wird aus `lib/<modul>.py` importiert und ab dieser Stelle
im Notebook verwendet. Aufklappbar darunter ist der Quellcode einsehbar.
```

```python
show_source(<fn>)
```

Festgehalten im `Refactoring_Plan.md` unter "Kanonischer Bootstrap".

## Installation

```bash
cp <ZIP>/patched_notebooks/kuer/*.ipynb kuer/
cp <ZIP>/patched_notebooks/experimental/*.ipynb experimental/
```
