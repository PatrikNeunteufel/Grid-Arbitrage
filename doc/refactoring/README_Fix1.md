# Fix — TOC-Links einheitlich + Anleitung Einzel-GIF neu erstellen

## 1. TOC-Links einheitlich

In K_01d wurden 9 Links von `[↑ TOC]` auf `[↑ Inhaltsverzeichnis]` umgestellt,
damit's konsistent zu K_01, K_01c, K_04 etc. ist.

Gepatchte Zellen (Markdown): 4, 13, 18, 20, 25, 30, 43, 48, 51

Installation:
```bash
cp <ZIP>/patched_notebooks/experimental/K_01d_Grid_Topologie.ipynb experimental/
```

## 2. Wie stelle ich ein, dass nur Winter-Tagesverlauf neu erstellt wird

Der Chart-Name des Winter-Tagesverlaufs (bei CH-Default `CC_CODE='CH'`) ist:

```
EXP_kuer_k01d_ch_tag_winter
```

Du hast zwei Wege:

### Weg A — Saubere Config-Variante (empfohlen für reproduzierbare Sessions)

In `sync/config.json`:

```json
"animation": {
  "modus": "skip_if_exists",
  "overrides": {
    "EXP_kuer_k01d_ch_tag_winter": "always"
  }
}
```

Effekt beim nächsten Lauf: Alle anderen GIFs werden geskippt (existieren ja
bereits), nur dieses eine wird neu erzeugt. Bleibt in der Config — wenn du
es beim übernächsten Lauf auch wieder wollen würdest, passiert dasselbe.

Nach dem Rebuild den Override wieder entfernen (oder auf `"skip_if_exists"`
setzen), damit nicht bei jedem Lauf neu gerendert wird.

### Weg B — Quick & Dirty (einmalig, dann vergessen)

Die GIF-Datei + den zugehörigen Frames-Ordner löschen:

```bash
rm experimental/output/charts/EXP_kuer_k01d_ch_tag_winter.gif
rm -rf experimental/output/charts/EXP_kuer_k01d_ch_tag_winter_frames/
```

Beim nächsten Lauf greift `should_skip` nicht (Datei existiert nicht mehr),
das GIF wird neu erstellt. Danach wird es wieder geskippt.

**Wichtig:** Auch den `_frames/`-Ordner löschen, sonst bleiben alte Frames,
die evtl. nicht zum neuen Code passen.

### Mehrere Saisonen gleichzeitig

Alle 4 Saisonen (Tagesverläufe) neu:

```json
"overrides": {
  "EXP_kuer_k01d_ch_tag_winter":   "always",
  "EXP_kuer_k01d_ch_tag_frühling": "always",
  "EXP_kuer_k01d_ch_tag_sommer":   "always",
  "EXP_kuer_k01d_ch_tag_herbst":   "always"
}
```

### Alle K_01d-GIFs auf einmal neu

Das wäre eher die "Helper-nuke"-Variante: `modus: "always"` in config.json,
dann läuft einmal alles durch, danach wieder auf `"skip_if_exists"`.

### Nachschauen welche GIFs erzeugt werden

Grundsätzlich: jede `make_gif_*`-Aufrufstelle definiert einen `path`, und
der Basename (ohne `.gif`) ist der chart_name. Für K_01d:

| Quellzelle | chart_name (bei CC_CODE='CH') |
|---|---|
| Cell 35 (LOOP 4 Saisonen) | `EXP_kuer_k01d_ch_tag_winter`, `_frühling`, `_sommer`, `_herbst` |
| Cell 44 (SINGLE) | `EXP_kuer_k01d_ch_jahr_19h`, `_jahr_12h` |
| Cell 45 (SINGLE) | `EXP_kuer_k01d_ch_jahr_tagesmittel` |

Bei Multi-Country-Erweiterung (Cell 52) entstehen zusätzlich GIFs mit anderen
Ländercodes, z.B. `EXP_kuer_k01d_de_tag_winter` etc.

## Hinweis zur Override-Mechanik

Die `overrides` sind nicht symmetrisch:
- `"always"` erzwingt Rebuild (auch wenn Datei existiert)
- `"skip_if_exists"` verhält sich wie der globale Default (wenn `modus` schon
  `"skip_if_exists"` ist, bringt der Override nichts)
- `"force_rebuild"` ist ein Alias für `"always"`

Verfügbare Schalter insgesamt (aus `lib/plotting.should_skip` docstring):
- `modus`: Default für GIFs — `"skip_if_exists"` | `"always"`
- `modus_statisch`: Default für PNGs — `"always"` | `"skip_if_exists_all"`
- `overrides`: Pro-Chart-Übersteuerung (höchste Priorität)
