# Phase 5c — show_source bei erster Verwendung

## Was Phase 5c macht

1. **Bootstrap erweitert** um den Import von `show_source`:
   ```python
   from lib.widgets  import show_animation
   from lib.plotting import show_source
   ```

2. **Vor der ersten Verwendung** einer importierten lib-Funktion wird ein
   2-Zellen-Block eingefügt:
   - Eine **Markdown-Info-Zelle** mit dem Hinweis, dass der Quellcode
     aufklappbar darunter sichtbar ist.
   - Eine **Code-Zelle** mit `show_source(show_animation)` — rendert den
     Quellcode inline mit JupyterLab-Syntax-Highlighting in einem
     aufklappbaren `<details>`-Block.

## Konvention für zukünftige NBs

Wenn eine weitere lib-Funktion zum ersten Mal in einem NB genutzt wird,
denselben Block einfügen — pro Funktion einmal, direkt vor der ersten
Verwendung. Beispiel für eine spätere Phase mit `make_gif_chart`:

```markdown
**🔎 Quellcode der importierten lib-Funktion**

Die Funktion `make_gif_chart` wird aus `lib/plotting.py` importiert und ab
dieser Stelle im Notebook verwendet. ...
```

```python
show_source(make_gif_chart)
```

## Platzierung je NB

| NB | Block-Position | Warum |
|---|---|---|
| `kuer/K_00` | **nach** der Wrapper-Zelle `def show_anim(...)` | Wrapper gehört mit seiner MD-Beschreibung zusammen; der Block dazwischen würde den Flow trennen. Die erste **tatsächliche** Verwendung (erster `show_anim(...)`-Call) kommt erst in §1. |
| `experimental/K_01c` | **vor** der ersten Anzeige-Zelle (Cell 22) | Natürlicher Flow: "hier ist der Quellcode", dann gleich die erste Nutzung. |
| `experimental/K_01d` | **vor** der ersten Anzeige-Zelle (Cell 34) | Wie K_01c. |

## Was der Reviewer sieht

Durch den aufklappbaren `<details>`-Block ist der Quellcode standardmässig
eingeklappt — der NB-Lesefluss bleibt kompakt. Ein Klick auf das 🔎-Symbol
zeigt den kompletten Python-Code der Funktion inline, mit dem Syntax-
Highlighting des aktuellen JupyterLab-Themes.

## Geänderte Notebooks

| NB | Änderung |
|---|---|
| `kuer/K_00_Business_Strategy.ipynb` | Bootstrap + show_source-Block nach Wrapper |
| `experimental/K_01c_Energiefluss_Animationen.ipynb` | Bootstrap + show_source-Block vor Cell 22 |
| `experimental/K_01d_Grid_Topologie.ipynb` | Bootstrap + show_source-Block vor Cell 34 |

## Installation

```bash
cp <ZIP>/patched_notebooks/kuer/K_00_Business_Strategy.ipynb kuer/
cp <ZIP>/patched_notebooks/experimental/*.ipynb experimental/
```

## Nächster Schritt

**Phase 4c** — `should_skip()` in die GIF-Erzeugungs-Zellen. Scope wie
besprochen: K_01c, K_01d, K_04, K_01.
