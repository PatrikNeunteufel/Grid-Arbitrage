# Phase 4c — `should_skip()` zentral in make_gif_*-Helpers

## Der Trick

Statt in jeder einzelnen GIF-Erzeugungs-Zelle (~19 insgesamt) einen Skip-Check
einzubauen, steht der Check **genau einmal** in der jeweiligen lokalen
Helper-Funktion — von der alle Erzeugungs-Zellen profitieren.

| NB | Helper-Funktion | Erzeugungs-Zellen abgedeckt |
|---|---|---:|
| `kuer/K_01_Raeumliche_Analyse.ipynb` | `make_gif_chart` | 1 |
| `kuer/K_04_Animationen.ipynb` | `make_gif_chart` | 3 |
| `experimental/K_01c_Energiefluss_Animationen.ipynb` | `make_gif_fast` | 10 |
| `experimental/K_01d_Grid_Topologie.ipynb` | `make_gif_fast_d` | 5 |

Insgesamt **19 Erzeugungs-Stellen** durch **4 zentrale Patches** abgedeckt.
Kein Side-Effect-Risiko in den Zellen selbst, weil dort nichts angefasst wurde.

## Der eingebaute Check

Direkt am Anfang jeder Helper-Funktion (nach Docstring falls vorhanden):

```python
def make_gif_fast(draw_fn, n_frames, fps, path, zone_alpha=0.12):
    # Skip-Check: überspringt Erzeugung wenn GIF existiert
    # (gesteuert durch sync/config.json → animation.modus)
    _name = os.path.basename(path).rsplit('.', 1)[0]
    if should_skip(path, 'animation', _name, CFG):
        print(f'⏭️  {_name} übersprungen (existiert)')
        return
    # ... bestehender Body ...
```

Der Check liest `CFG` aus dem NB-Scope (global durch die Init-Zelle gesetzt).
Der `name` wird aus dem `path`-Argument abgeleitet (`kuer_k04_anim_A` etc.) —
passt zum `overrides`-Dict in `config.json`.

## Was das jetzt heisst

Nach dem ersten vollständigen Lauf (z.B. `run_all.sh`) sind alle GIFs
erzeugt. Bei **jedem weiteren Lauf** prüft der Helper automatisch:

- **Datei existiert** → `⏭️  übersprungen` (instant, keine Frame-Renderings)
- **Datei fehlt** → Erzeugung läuft durch

Für den typischen Dev-Flow heisst das: einmal teuer rendern, danach ist ein
Re-run der NBs innerhalb weniger Sekunden durch.

## Overrides-Beispiele

Wenn du für einzelne GIFs `always` (immer neu rendern) willst, im
`config.json`:

```json
"animation": {
  "modus": "skip_if_exists",
  "overrides": {
    "kuer_k04_anim_A_07h": "always",
    "EXP_kuer_k01c_gif_a_tag_winter": "always"
  }
}
```

Oder alle GIFs forcieren für einen frischen Lauf:
```json
"animation": { "modus": "always" }
```

## Bonus: einheitlicher Bootstrap in allen 4 NBs

Der Bootstrap ist jetzt in allen NBs identisch:

```python
from lib.widgets  import show_animation
from lib.plotting import show_source, should_skip
```

In K_01c und K_01d wurde er **erweitert**, in K_01 und K_04 **neu eingefügt**.
Für zukünftige Phasen gilt: wenn eine NB eine weitere `lib.xxx`-Funktion
braucht, in diesen Block aufnehmen.

## Qualitäts-Checks (alle ✅)

| Check | Status |
|---|---|
| AST-Validierung der 4 Helper-Zellen | ✅ |
| AST-Validierung der 4 Bootstrap-Zellen | ✅ |
| Skip-Check greift auf `CFG` und `os` aus NB-Scope zu | ✅ (vor Helpers geladen) |
| Docstrings bleiben erhalten (Introspection-fähig) | ✅ |
| Keine NB-Erzeugungs-Zellen angefasst | ✅ |

## Installation

```bash
cp <ZIP>/patched_notebooks/kuer/*.ipynb kuer/
cp <ZIP>/patched_notebooks/experimental/*.ipynb experimental/
```

## Bewusst ausgelassen

- **Statische PNG-Charts** — rendern meist in <1s, `modus_statisch='always'`
  (Default) passt. Bei Bedarf analog einbauen oder über
  `modus_statisch='skip_if_exists_all'`-Master-Schalter.
- **NB-Erzeugungs-Zellen direkt** — keine Einzelfall-Patches, der Check sitzt
  im Helper. Falls eine Zelle jemals **ohne** Helper ein GIF schreibt (z.B.
  direkt `frames[0].save(...)`), wäre dort ein lokaler Check nötig — aktuell
  macht das keine der NBs.

## Nächste Phase

**Phase 6** — Lib-Migration: Funktionen aus Notebooks nach `lib/`-Modulen
ziehen (`make_gif_chart`, `show_chart`, `draw_base_map`, Dispatch-Simulation
etc.) — step-by-step je NB. Das ist der verbleibende grosse Phase-Block im
Plan.
