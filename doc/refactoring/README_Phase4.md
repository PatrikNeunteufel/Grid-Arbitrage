# Phase 4 — Animations- und Chart-Schalter

## Was Phase 4 liefert

**Phase 4a: Config-Infrastruktur**

- `sync/config.json` `animation`-Block wird um drei neue Felder erweitert:
  - `modus` — Rebuild-Verhalten für **GIFs/Animationen** (Default: `'skip_if_exists'`)
  - `modus_statisch` — Rebuild-Verhalten für **statische Charts** (Default: `'always'`)
  - `overrides` — Dict mit pro-Chart-Übersteuerungen

Die bestehenden Felder (`dpi`, `frames_per_hour`, `fps_chart` etc.) bleiben
unverändert. `lib.plotting.should_skip()` ist aus Phase 1 bereits einsatzbereit
und liest diese Schalter.

**Phase 4b: Integrations-Patterns**

Dokumentation und Code-Snippets, wie `should_skip()` in Chart-/GIF-Zellen
eingebaut wird — minimal-invasiv, ohne bestehenden Render-Code zu verändern.

## Installation

```bash
cd /pfad/zum/projekt
cp <ZIP>/sync/config.json sync/
```

Es wird **nur** `sync/config.json` ersetzt — der `animation`-Block ist erweitert,
alle anderen Sektionen (`pflicht`, `kuer`, `visualisierung`, …) bleiben exakt
wie sie sind. Ein Diff zeigt nur drei Ergänzungen im `animation`-Block.

## Wie die drei Schalter zusammenspielen

Entscheidungsreihenfolge in `should_skip()`:

1. **`overrides[chart_name]`** — wenn explizit gesetzt, gewinnt immer (höchste Priorität)
2. **`asset_type == 'animation'`** → `modus` (Default `'skip_if_exists'`)
3. **`asset_type == 'statisch'`** → `modus_statisch` (Default `'always'`)
   - Spezialwert `'skip_if_exists_all'` für `modus_statisch` = **Master-Schalter**:
     alle statischen Charts werden behandelt wie `'skip_if_exists'`

### Typische Profile

| Ziel | modus | modus_statisch | overrides |
|---|---|---|---|
| **Default (Entwicklung)** | `skip_if_exists` | `always` | `{}` |
| **Schnelles run_all** nach kleinen Anpassungen | `skip_if_exists` | `skip_if_exists_all` | `{}` |
| **Frischer Lauf für Abgabe** | `always` | `always` | `{}` |
| **Einzelnes GIF erzwingen** | `skip_if_exists` | `always` | `{"kuer_k04_anim_A": "always"}` |

## Pattern A — GIF/Animation-Zelle

**Vorher (bestehender Code):**
```python
# ── GIF A: Tagesfluss ─────────────────────────────────────────────
from PIL import Image
frames = build_frames(...)
out = os.path.join(CHARTS_DIR, 'kuer_k04_anim_A.gif')
frames[0].save(out, save_all=True, append_images=frames[1:], ...)
log_dataindex(out, 'K_04 GIF A')
```

**Nachher (mit Schalter):**
```python
# ── GIF A: Tagesfluss ─────────────────────────────────────────────
from lib.plotting import should_skip

chart_name = 'kuer_k04_anim_A'
out        = os.path.join(CHARTS_DIR, f'{chart_name}.gif')

if should_skip(out, 'animation', chart_name, CFG):
    print(f'⏭️  {chart_name} übersprungen (existiert)')
else:
    from PIL import Image
    frames = build_frames(...)
    frames[0].save(out, save_all=True, append_images=frames[1:], ...)
    log_dataindex(out, 'K_04 GIF A')
    print(f'✓  {chart_name} erzeugt')
```

## Pattern B — Statische Chart-Zelle

**Vorher:**
```python
# ── Chart 1: Summary-Diagramm ─────────────────────────────────────
fig, ax = plt.subplots(...)
# ... plot code ...
out = os.path.join(CHARTS_DIR, 'nb04_summary.png')
plt.savefig(out, dpi=150)
log_dataindex(out, 'NB04 Chart 1')
```

**Nachher:**
```python
# ── Chart 1: Summary-Diagramm ─────────────────────────────────────
from lib.plotting import should_skip

chart_name = 'nb04_summary'
out        = os.path.join(CHARTS_DIR, f'{chart_name}.png')

if should_skip(out, 'statisch', chart_name, CFG):
    print(f'⏭️  {chart_name} übersprungen (existiert)')
else:
    fig, ax = plt.subplots(...)
    # ... plot code ...
    plt.savefig(out, dpi=150)
    log_dataindex(out, 'NB04 Chart 1')
    print(f'✓  {chart_name} erzeugt')
```

## Scope: Wo der Schalter sinnvoll ist

Gezählte Chart-/GIF-Zellen pro NB (Orientierung für Integration):

| NB | GIF-Zellen | PNG-Zellen | Priorität |
|---|---:|---:|---|
| `experimental/K_01c_Energiefluss_Animationen` | 21 | 1 | **hoch** (viele GIFs, aufwändig) |
| `experimental/K_01d_Grid_Topologie` | 9 | 4 | **hoch** (OSM+GIF rechenintensiv) |
| `kuer/K_01_Raeumliche_Analyse` | 2 | 15 | mittel (viele statische Karten) |
| `notebooks/04_Visualisierungen` | 0 | 12 | niedrig (schnell) |
| `kuer/K_04_Animationen` | 4 | 1 | **hoch** (reine Animationen) |
| `kuer/K_00_Business_Strategy` | 5 | 0 | mittel (zeigt fertige GIFs) |
| `kuer/K_99_Kombinierte_Simulation` | 0 | 6 | mittel |
| `kuer/K_03 / K_05-K_10` | 0 | 1-3 je | niedrig |
| `experimental/K_01b` | 0 | 3 | niedrig |
| `organisation/O_99` | 0 | 4 | niedrig |

**Empfehlung:** Mit den "hohen" Prioritäten beginnen. Bei statischen Charts
(PNG) lohnt sich der Einbau nur, wenn die Erzeugung >2s dauert (sonst bringt
`skip_if_exists` keinen spürbaren Zeitgewinn).

## Empfohlene `overrides`-Einträge (exemplarisch)

Einige Charts sind besonders aufwendig. Für die kann man einen Override
setzen, der sie standardmässig überspringt — unabhängig vom globalen
`modus_statisch`:

```json
"overrides": {
  "kuer_k01_karte_generator_mix": "skip_if_exists",
  "kuer_k01_karte_verbraucher_zone": "skip_if_exists",
  "exp_k01d_netzwerk_schweiz": "skip_if_exists"
}
```

Das kann man in späteren Runden basierend auf tatsächlichen Rendering-Zeiten
befüllen (hier nur als Beispiel; der User entscheidet selbst).

## Was Phase 4 NICHT macht

- **Keine NB-Änderungen** — die `should_skip()`-Integration pro Zelle ist
  Aufgabe einer späteren Runde, wenn gewünscht
- **Keine automatische Chart-Namen-Erkennung** — der `chart_name`-Parameter
  muss manuell in jede Zelle eingefügt werden (konsistent zur `CHARTS_DIR`-
  Dateiname-Konvention `kuer_kXX_*` / `nb04_*`)
- **Keine Invalidierung** bei Code-Änderungen — `skip_if_exists` prüft nur
  auf Datei-Existenz, nicht auf Code-Hash. Wer bewusst neu rendern will, muss
  entweder die Datei löschen oder `modus` temporär auf `always` setzen.

## Verifikation

Nach Installation von `sync/config.json`:

```python
# In irgendeiner NB-Zelle testen:
from lib.plotting import should_skip
print(should_skip('nonexistent.gif', 'animation', 'foo', CFG))  # → False
# Eine existierende Datei:
print(should_skip('output/charts/nb04_summary.png', 'animation', 'foo', CFG))  # → True (bei Default)
```

## Nächste Schritte

- **Phase 5** — `slide_or_play` nach `lib/widgets.py` + GIF-Fallback (wichtig
  für K_01d, das den Slider stark nutzt)
- **Phase 6** — Lib-Migration: Funktionen aus Notebooks nach `lib/`-Modulen
  (`make_gif_chart`, `show_chart`, `draw_base_map`, Dispatch-Sim etc.)
- **Phase 6 als Option: `should_skip()` in NBs nachziehen** — in Pattern A/B
  wie oben beschrieben
