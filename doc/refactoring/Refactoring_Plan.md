# Refactoring-Plan SC26_Gruppe_2 — v2

Stand: 23.04.2026 · Basis: aktuelle ZIPs vom 22./23.04.
**Änderungen v1 → v2:** Reihenfolge umgekehrt (Struktur zuerst, Lib-Migration am Schluss); Lib-Migration step-by-step je Notebook in Reihenfolge `notebooks/ → kuer/ → organisation/ → experimental/`; Antworten auf v1-§9 eingearbeitet.

---

## 1. Ausgangslage (Ist-Analyse)

**26 Notebooks analysiert:**

| Ordner | Anzahl | Status |
|---|---|---|
| `organisation/` | 5 | O_01–O_04, O_99 |
| `notebooks/` (Pflicht) | 5 | NB00–NB04 |
| `kuer/` | 12 | K_00, K_01, K_02–K_10, K_99 |
| `experimental/` | 3 | K_01b, K_01c, K_01d |
| Root (neu, ungetestet) | 1 | K_01d_Grid_Topologie_slider |

**Hauptbefunde:**
- 70 Funktionen in K_01d (slider-Version), davon ~34 konsolidierbar (Smooth-/Tagesmittel-Wrapper); Gesamtprojekt: >90 Funktions-Definitionen, viele dupliziert
- Keine Skip-if-exists-Logik bei Animationen — jeder Re-Run überschreibt
- Strukturelle Abweichungen von der in `O_03` dokumentierten Reihenfolge in **16 von 22 Pflicht-/Kür-Notebooks**
- Residuale führende Ziffern in Ankern in 7 Notebooks
- Zwei Notebooks mit Doppel-Ankern (K_03, K_09)
- `slide_or_play()` steht aktuell nur in einem Notebook und hat kein GIF-Fallback

---

## 2. Kanonische Notebook-Struktur (Soll, gemäss O_03 §17)

```
1. Titel-Zelle                 # {ID} – {Titel} | Gruppe · Datum · Badge
2. Navigations-Links           | ← Vorheriges | ↑ Übersicht | Nächstes → |
3. Inhaltsverzeichnis          ## Inhaltsverzeichnis <a id='toc_{ID}'>
4. Einleitung                  ## Einleitung  (Motivation + Forschungsfrage / NB-Ziel)
5. Initialisierung             ## Initialisierung  (Imports, Config, Pfade, Daten-Check)
6. Hauptteil                   ## 1. … / ## 2. … / …  (numerierte Abschnitte)
7. Fazit                       ## Fazit  (inhaltliche Zusammenfassung, Erkenntnisse)
8. Abschluss                   ## Abschluss  (technische Kontrolle: Datei-Checks, transfer.json)
9. Navigations-Links           (Wiederholung von 2)
```

**Unterscheidung Fazit vs. Abschluss** (wird aktuell oft vermischt):
- **Fazit** = inhaltlich: Was haben wir gelernt? Beantwortung der Forschungsfragen.
- **Abschluss** = technisch: `EXPECTED_FILES`-Check, `transfer.json` schreiben, Verweis auf nächstes NB.

**Ausnahmen (dokumentiert in O_03 §17.3):**
- Organisation-Notebooks (O_01–O_04, O_99) brauchen keine Einleitung/Fazit — lockerere Struktur.
- NB00 und K_00 sind Report-Notebooks — statt Einleitung/Fazit "Business Case" bzw. "Strategisches Fazit".

---

## 3. Strukturabgleich pro Notebook (Ist → Soll)

Legende: ✅ vorhanden · ❌ fehlt · ⚠ vorhanden, falsche Position · ⇒ Aktion

### 3.1 Pflicht-Notebooks (`notebooks/`)

| NB | Titel | Nav | TOC | Einltg | Init | Haupt | Fazit | Abschl | Aktion |
|---|---|---|---|---|---|---|---|---|---|
| NB00 | ✅ | ✅ | ✅ | ⚠ (nach Init) | ⚠ (vor Einltg) | ✅ | ✅ | ✅ (§6 "Kür-NBs") | Einltg↔Init tauschen; §6 "Kür-NBs" als Anhang vor Abschluss |
| NB01 | ✅ | ? | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ | Einltg einfügen; Fazit einfügen |
| NB02 | ✅ | ? | ✅ | ❌ | ✅ | ✅ (nur "2.") | ❌ | ✅ | Einltg + Fazit; "1."-Nummerierung |
| NB03 | ✅ | ? | ✅ | ❌ | ✅ | ✅ (2.–6., "1." fehlt) | ❌ | ✅ | Einltg + Fazit |
| NB04 | ✅ | ? | ✅ | ❌ | ✅ | ⚠ inkonsistent | ❌ | ✅ | Einltg; Charts durchnumerieren |

### 3.2 Kür-Notebooks (`kuer/`)

| NB | Einltg | Init | Haupt | Fazit | Abschl | Aktion |
|---|---|---|---|---|---|---|
| K_00 | ⚠ (§1 nach Init) | ⚠ | ✅ | ✅ (§13) | ✅ | Einltg↔Init tauschen |
| K_01 | ❌ | ✅ | ✅ | ✅ (§8) | ❌ | Einltg + Abschluss |
| K_02 | ❌ | ⚠ (mit Datenladen verschmolzen) | ✅ | ✅ | ⚠ (vor Fazit) | Einltg; Abschluss ↔ Fazit tauschen |
| K_03 | ❌ | ✅ (Doppelanker!) | ✅ | ❌ | ✅ | Einltg; Doppelanker; Fazit |
| K_04 | ❌ | ✅ | ✅ | ❌ | ⚠ (nach "Erweiterungen") | Einltg; "Erweiterungen" vor Abschluss; Fazit |
| K_05 | ❌ | ✅ | ✅ | ✅ | ✅ | Einltg |
| K_06 | ❌ | ✅ | ✅ | ✅ | ✅ | Einltg; H1→H4 ML-Zwischenheader |
| K_07 | ❌ | ✅ | ✅ | ✅ | ❌ | Einltg + Abschluss |
| K_08 | ⚠ (§2 "Motivation") | ✅ | ✅ | ✅ | ❌ | §2 Motivation→Einltg + Abschluss |
| K_09 | ❌ | ✅ (Doppelanker!) | ✅ | ✅ | ❌ | Einltg; Doppelanker; Abschluss |
| K_10 | ❌ | ✅ | ✅ | ✅ | ❌ | Einltg + Abschluss |
| K_99 | ❌ | ✅ | ✅ | ❌ | ✅ | Einltg + inhaltliches Fazit (§5 ist nur Abschlusskontrolle) |

### 3.3 Experimental (`experimental/`)

| NB | Einltg | Abschl | Aktion |
|---|---|---|---|
| K_01b | ❌ | ✅ | Einltg |
| K_01c | ⚠ (§2 "Warnung" ist halb-Einltg) | ✅ (§11) | Einltg; Warnung bleibt als §2 |
| K_01d | ❌ | ✅ (§9) | Wird ersetzt durch Slider-Version (siehe §6) |
| **K_01d_slider** (Root) | ❌ | ✅ (§9) | Nach `experimental/` verschieben + Einltg |

### 3.4 Organisation (`organisation/`)

| NB | Problem | Aktion |
|---|---|---|
| O_01 | 11 Anker mit führenden Ziffern | Alle Anker von Nummern befreien |
| O_02 | OK | — |
| O_03 | 2 Anker mit Ziffern | Bereinigen |
| O_04 | "§1 Zweck" vor TOC | TOC vor §1 ziehen; Anker bereinigen |
| O_99 | OK | — |

### 3.5 Anker-Hygiene (Gesamtsicht)

| Notebook | Betroffene Anker (Auszug) |
|---|---|
| experimental/K_01b | `3-daten-laden_K_01b`, `4-zonenzuweisung_K_01b`, `5-bilanzen-bvi_K_01b`, `6-vergleich_K_01b`, `7-config-doku_K_01b` |
| kuer/K_01 | `61-heatmap-tages-lastprofil-pro-zone_K_01` |
| kuer/K_02 | `11-entso-e-grenzflüsse-ch-download_K_02`, `12-importexport-analyse-berechnen_K_02`, `21-kernthese_K_02`, `22-ergebnisse_K_02` |
| kuer/K_03 | Doppelanker in Init-Zelle |
| kuer/K_09 | Doppelanker + `0-setup_K_09` |
| organisation/O_01 | 11 Anker mit führenden Ziffern |
| organisation/O_03 | `1-hauptabschnitt-nummeriert-mit-fuehrendem-_O_03`, `2-3-markdown-werte_O_03` |
| organisation/O_04 | `1-zweck-dieses-dokuments_O_04` |

Regel: Anker müssen **vollständig ziffernfrei** sein.

---

## 4. Funktionsbibliothek `lib/` (Soll-Architektur)

Neues Verzeichnis `lib/` **parallel** zu `notebooks/`, `kuer/`, `organisation/`, `experimental/`, `sync/`. **Wird Teil der Git-Abgabe.**

```
lib/
├── __init__.py                # leer
├── io_ops.py                  # Datei-I/O, Provenienz, Download-Gating
├── data_fetchers.py           # API-Downloads (ENTSO-E, BFS, Zenodo, OSM)
├── simulation.py              # Dispatch-Algorithmen & Wirtschaftlichkeit
├── plotting.py                # Plot-Helper, GIF-Builder, Display-Helper
├── widgets.py                 # slide_or_play, weitere ipywidgets-Tools
├── columns.py                 # Column-Mapping, Utility
└── grid_topo.py               # K_01d-Funktionsbibliothek (~70 → ~40 nach Konsolidierung)
```

### 4.1 Modul-Belegung

| Modul | Funktionen (Quelle in Klammer) |
|---|---|
| **`io_ops.py`** | `_find_project_root` (K_01d), `log_dataindex` (NB01/02/03, K_01, K_02), `log_missing` (NB01/02/03), `needs_download` (NB01, K_01, K_02), `needs_rebuild` (NB02, NB03, K_02) |
| **`data_fetchers.py`** | `_fetch_prices_year`, `_fetch_load_year` (NB01), `_fetch_crossborder_year` (K_02), `fetch_bfs_pxweb` (K_01), `load_pypsa_zenodo`, `load_kantone` (K_01d) |
| **`simulation.py`** | `simulate_battery` (NB03), `simulate_battery_reactive`, `simulate_battery_da_optimal` (K_06), `sim_arbitrage`, `sim_ev`, `sim_hybrid` (K_99), `fmt_be`, `be_est`, `get_trigger` (K_99), `exp_decay` (K_07) |
| **`plotting.py`** | `make_gif_chart` (K_01, K_04), `make_spline_h24`, `make_spline_w4` (K_01, K_04), `draw_base_map` (K_01, K_01c), `show_chart` (NB00), `show`, `show_anim`, `nb_aktiv`, `check_aktiv` (K_00), `highlight` (O_01), `fmt_size`, `_nd` (O_99), **`show_source()`** (neu, §4.3), **`should_skip()`** (neu, §5) |
| **`widgets.py`** | `slide_or_play` (robuster, mit GIF-Fallback), `_find_frame_dir` (K_01d_slider) |
| **`columns.py`** | `find_col` (K_01, K_01b), `map_et` (K_01), `clean_name`, `in_bbox` (K_01d) |
| **`grid_topo.py`** | Cell 24 (~21 Accessoren), Cell 25 (Grid-Compute), Cell 29 (Render + Overlays), Cell 30/31/32/39/40 (Factories, Smooth/Tagesmittel), Cell 8 (`draw_engpaesse`). **Phase 7 konsolidiert Smooth-/Tagesmittel-Wrapper zu Factories.** |

### 4.2 Nutzungsmuster im Notebook

```python
# ── lib-Import (eine Zelle, nach Standard-Imports) ────────────────────────
import sys
from pathlib import Path
_lib_root = Path('..').resolve()
if str(_lib_root) not in sys.path:
    sys.path.insert(0, str(_lib_root))

from lib.io_ops import log_dataindex, needs_download
from lib.simulation import simulate_battery

%load_ext autoreload
%autoreload 2
```

### 4.3 Transparenz-Zelle: `show_source()` Helper

**`<details>`-aufklappbare Quellcode-Anzeige** mit Syntax-Highlighting via pygments. Bleibt automatisch synchron mit `lib/` weil `inspect.getsource` die aktuelle Version liest.

```python
# lib/plotting.py
def show_source(func, title=None):
    """Zeigt den Quellcode einer lib-Funktion aufklappbar und syntax-highlighted."""
    import inspect, html as _html
    from IPython.display import HTML, display
    try:
        from pygments import highlight
        from pygments.lexers import PythonLexer
        from pygments.formatters import HtmlFormatter
        src = inspect.getsource(func)
        formatter = HtmlFormatter(noclasses=True, style='github-dark')
        code_html = highlight(src, PythonLexer(), formatter)
    except ImportError:
        src = _html.escape(inspect.getsource(func))
        code_html = f'<pre style="background:#0d1117;color:#e6edf3;padding:10px;border-radius:4px;"><code>{src}</code></pre>'
    mod = func.__module__.replace('.', '/')
    caption = title or f"Quellcode: <code>{func.__name__}</code> (aus <code>{mod}.py</code>)"
    display(HTML(f'''
    <details style="margin:8px 0;">
      <summary style="cursor:pointer;padding:6px 10px;background:#161b22;
                      color:#e6edf3;border-radius:4px;user-select:none;">
        🔎 {caption}
      </summary>
      <div style="margin-top:4px;">{code_html}</div>
    </details>
    '''))
```

**Verwendung (eine Zelle pro Funktion im Erst-Notebook):**

```python
from lib.plotting import show_source
from lib.simulation import simulate_battery
show_source(simulate_battery)
```

**Zuordnung "wo wird welche Funktion erstmals gezeigt" — folgt der Migrations-Reihenfolge:**

| Modul | Erstes Notebook das zeigt | Begründung |
|---|---|---|
| `io_ops.py` | `notebooks/01_Daten_Laden.ipynb` | Erstes Notebook in der Pipeline |
| `data_fetchers.py` | `notebooks/01_Daten_Laden.ipynb` | Dort werden ENTSO-E Fetches erstmals aufgerufen |
| `simulation.py` | `notebooks/03_Daten_Analyse.ipynb` | Erste Dispatch-Simulation |
| `plotting.py` Core-Helper | `notebooks/04_Visualisierungen.ipynb` | Erste Charts mit Helpern |
| `plotting.show_source` | `notebooks/01_Daten_Laden.ipynb` | Muss als erstes gezeigt werden — ist der Helper für alle weiteren |
| `plotting.should_skip` | `kuer/K_01_Raeumliche_Analyse.ipynb` | Erste Animation/aufwendige Karten |
| `columns.py` | `kuer/K_01_Raeumliche_Analyse.ipynb` | Erste Verwendung |
| `widgets.py` (`slide_or_play`) | `kuer/K_01_Raeumliche_Analyse.ipynb` | Erste Animation |
| `grid_topo.py` | `experimental/K_01d_Grid_Topologie.ipynb` | Funktionen sind dort zuhause |

---

## 5. Animations-/Bild-Schalter (Skip-if-exists)

**Entschieden:** Default `skip_if_exists` für Animationen. Statische Bilder 2-stufig: Default `always`, aber mit Override-Liste für aufwendige Einzelcharts und Master-Schalter `modus_statisch: 'skip_if_exists_all'` zum Durchschalten aller.

### 5.1 Config-Erweiterung (`sync/config.json`)

```json
"animation": {
  "_existing": "dpi, frames_per_hour, ... (bleibt)",
  "modus":            "skip_if_exists",
  "_hint_modus":      "'always' = immer neu | 'skip_if_exists' = nur wenn fehlt | 'force_rebuild' = alias zu always",
  "modus_statisch":   "always",
  "_hint_modus_statisch": "Default für savefig-Charts. 'skip_if_exists_all' erweitert Skip-Logik auf ALLE statischen Charts.",
  "overrides": {
    "_hint": "Pro-Chart-Override: {name: 'skip_if_exists' | 'always' | 'force_rebuild'}. Name = Basename ohne Extension.",
    "kuer_k01_karte_verbraucher": "skip_if_exists",
    "kuer_k01_karte_erzeuger_typ": "skip_if_exists",
    "kuer_k01_karte_kombiniert":   "skip_if_exists",
    "EXP_kuer_k01d_netzwerk":      "skip_if_exists"
  }
}
```

### 5.2 `should_skip()` Helper in `lib/plotting.py`

```python
def should_skip(out_path, asset_type, name, cfg):
    """
    Ermittelt, ob die Erzeugung eines Charts/GIFs übersprungen werden soll.
    
    Parameter
    ---------
    out_path : str         Zielpfad des Charts/GIFs
    asset_type : str       'animation' oder 'statisch'
    name : str             Basename des Charts (für overrides-Lookup)
    cfg : dict             Geladenes CFG-Dict
    
    Reihenfolge: 1. overrides[name] | 2. global modus | 3. asset_type-Default
    """
    import os
    anim_cfg  = cfg.get('animation', {})
    overrides = anim_cfg.get('overrides', {})
    
    if name in overrides and not name.startswith('_'):
        mode = overrides[name]
    elif asset_type == 'animation':
        mode = anim_cfg.get('modus', 'skip_if_exists')
    else:  # statisch
        global_static = anim_cfg.get('modus_statisch', 'always')
        mode = 'skip_if_exists' if global_static == 'skip_if_exists_all' else global_static
    
    if mode == 'skip_if_exists':
        return os.path.exists(out_path) and os.path.getsize(out_path) > 0
    return False  # 'always' / 'force_rebuild' → nie skippen
```

### 5.3 Standard-Zellen-Header (Konvention)

Jede Anim-/Chart-Zelle mit potenziell hohem Rechenaufwand beginnt mit **verpflichtendem Kommentar-Header**:

```python
# ── ANIM: kuer_k04_anim_A_18h ────────────────────────────────────────────────
# ⚙ Schalter: CFG['animation']['modus']        → 'skip_if_exists' (default)
# ⚙ Override: CFG['animation']['overrides']['kuer_k04_anim_A_18h']  (optional)
# ─────────────────────────────────────────────────────────────────────────────

from lib.plotting import should_skip

_anim_name = 'kuer_k04_anim_A_18h'
_out_path  = os.path.join(CHARTS_DIR, f'{_anim_name}.gif')

if should_skip(_out_path, 'animation', _anim_name, CFG):
    print(f"✓ Überspringe {_anim_name} (existiert, modus=skip_if_exists)")
else:
    # ... make_gif_chart(...) aufrufen
    pass
```

### 5.4 Abzählung — wo der Schalter eingefügt wird

| Notebook | Anim-Zellen | Statisch-Zellen mit Override-Empfehlung |
|---|---|---|
| K_01 | 1 (Cell 73) | 7 (Karten: 41, 43, 48, 51, 53, 56, 59) |
| K_04 | 3 (Cells 16, 18, 20) | 0 |
| K_01d (slider, neu in experimental/) | 4 (Cells 29, 32, 39, 40) | 1 (Cell 20 Netzwerkkarte mit OSM) |
| K_01c | 5 (Cells mit `_dyn_*`) | 0 |
| **Total** | **~13 Anim-Zellen** | **~8 Statisch-Zellen** |

---

## 6. K_01d Slider-Integration

### 6.1 Status quo

`K_01d_Grid_Topologie_slider.ipynb` ist ein Fork von `experimental/K_01d_Grid_Topologie.ipynb` mit zusätzlicher Zelle 30 (`slide_or_play` + `_find_frame_dir`). Funktioniert, **aber:**
- **Kein GIF-Fallback** wenn `ipywidgets` nicht rendert — konkret beobachtet: VBox-Repr als Plain-Text, keine Anzeige trotz erfolgreichem Frame-Load (621 MB geladen, aber unsichtbar)
- Hängt an globalem `EXP_CHARTS_DIR`

### 6.2 Ziel

1. `slide_or_play` nach `lib/widgets.py` — mit `base_dir`-Parameter statt globalem `EXP_CHARTS_DIR` + automatischem GIF-Fallback
2. `K_01d_Grid_Topologie_slider.ipynb` **ersetzt** `experimental/K_01d_Grid_Topologie.ipynb`
3. In allen Notebooks mit Anim-Output (K_04, K_01c, K_01d): `display(Image(filename=_p))`-Zellen durch `slide_or_play(...)` ersetzen

### 6.3 Robustheits-Anforderungen an `slide_or_play`

```python
def slide_or_play(name, framerate=10, image_width='100%', base_dir=None, cfg=None):
    """
    Interaktiver Frame-Viewer mit automatischem GIF-Fallback.
    
    Fallback-Kaskade (in Reihenfolge):
      1. ipywidgets + Widget-Rendering OK → Slider+Play-UI
      2. ipywidgets nicht installiert / Rendering-Check negativ → statisches GIF anzeigen
      3. Kein GIF vorhanden → erstes Frame als statisches PNG + Hinweis
      4. Auch keine Frames → print-Warnung
    
    Widget-Rendering-Check: Heuristik, z.B. Versuch, ein HBox zu erzeugen und
    dessen `_view_name` abzufragen. Wenn das scheitert → Fallback.
    
    Diagnose-Hilfe im Docstring:
      • pip install ipywidgets jupyterlab_widgets
      • Kernel → Restart nach pip install (KRITISCH)
      • JupyterLab komplett schliessen (Server stoppen), neu starten
      • Notebook als "Trusted" markieren
      • Browser Hard-Reload (Ctrl+Shift+R)
    """
```

### 6.4 Frame-Ordner-Konvention

Das angehängte Sample (`EXP_kuer_k01d_ch_tag_frühling.gif` + `_frames/frame_XXXX.png`) bestätigt: Frames liegen in `{gif_basename}_frames/`, numeriert `frame_XXXX.png`. Bereits korrekt in `make_gif_chart` / `make_gif_fast_d` implementiert — keine Änderung nötig.

---

## 7. Reihenfolge der Umsetzung (Phasenplan v2)

**Prinzip:** Zuerst strukturelle und anker-mässige Bereinigungen (niedrig-Risiko, mechanisch). Dann Animations-Schalter + Slider. **Lib-Migration als letzter grosser Block, step-by-step je Notebook** in Reihenfolge `notebooks/ → kuer/ → organisation/ → experimental/`. Nach jeder Phase läuft `run_all` ohne Fehler.

### Phase 0: Baseline sichern · **~15 min**
- [ ] Aktueller Stand als `baseline_pre_refactor/` (Kopie aller ZIPs)
- [ ] `run_all.sh` einmal durchlaufen, Outputs in `data/` hashen → Regression-Referenz
- [ ] Git-Commit als `baseline-v2-start`

### Phase 1: lib/ Skeleton + zwei Core-Helper · **~30 min**
Die Infrastruktur wird jetzt angelegt — aber noch **keine** Funktionsmigration. Nur zwei neue Helper, die später von allen anderen Phasen gebraucht werden.

- [ ] `lib/__init__.py` + alle sieben Modul-Platzhalter (Docstring, `from __future__ import annotations`)
- [ ] **`lib/plotting.py`:** `show_source()` (für Transparenz-Zellen in Phase 6) + `should_skip()` (für Animations-Schalter in Phase 4)
- [ ] O_03 §5 um Abschnitt "lib/-Nutzung" ergänzen (Import-Pattern, `autoreload`, `show_source`)

### Phase 2: Anker-Hygiene · **~1 h**
Mechanisch, niedrig-Risiko.

- [ ] Vor Beginn: grep über alle `[text](#anchor)` Link-Targets → Mapping-Tabelle alt→neu bauen
- [ ] Anker ohne Ziffern umschreiben in 8 betroffenen Notebooks (siehe §3.5)
- [ ] Doppelanker in K_03 und K_09 auflösen (nur `initialisierung_K_0x` behalten)
- [ ] Parallel dazu alle Link-Targets mitziehen
- [ ] Test: jedes TOC-Link klickbar (visuell in JupyterLab)

### Phase 3: Struktur-Harmonisierung · **~2–3 h**

Reihenfolge nach Aufwand, pro Notebook isoliert:

#### 3a) `notebooks/` (Pflicht)
- [ ] **NB00**: Einltg↔Init tauschen; §6 "Kür-NBs" als Anhang vor Abschluss
- [ ] **NB01**: Einltg + Fazit einfügen
- [ ] **NB02**: Einltg + Fazit; "1."-Nummerierung ergänzen
- [ ] **NB03**: Einltg + Fazit
- [ ] **NB04**: Einltg; Charts durchnumerieren (Chart 1 → §1 Chart, Chart 2 → §2 Chart, …)

#### 3b) `kuer/`
- [ ] **K_00**: Einltg↔Init tauschen
- [ ] **K_01**: Einltg + Abschluss
- [ ] **K_02**: Einltg; Abschluss↔Fazit tauschen (Abschluss als letztes)
- [ ] **K_03**: Einltg + Fazit
- [ ] **K_04**: Einltg + Fazit; "Potenzielle Erweiterungen" vor Abschluss
- [ ] **K_05**: Einltg
- [ ] **K_06**: Einltg; H1-Zwischenzeilen (ML-Code-Header) → H4
- [ ] **K_07**: Einltg + Abschluss
- [ ] **K_08**: §2 Motivation → Einltg umbenennen & vor Init; Abschluss einfügen
- [ ] **K_09**: Einltg + Abschluss
- [ ] **K_10**: Einltg + Abschluss
- [ ] **K_99**: Einltg + inhaltliches Fazit (vor bestehender Abschlusskontrolle)

#### 3c) `organisation/`
- [ ] **O_01**: Nichts ausser Anker (in Phase 2 schon erledigt)
- [ ] **O_03**: Nichts ausser Anker
- [ ] **O_04**: TOC vor §1 ziehen

#### 3d) `experimental/`
- [ ] **K_01d_slider.ipynb** → nach `experimental/K_01d_Grid_Topologie.ipynb` verschieben (alte Version ersetzen)
- [ ] **K_01b**: Einltg einfügen
- [ ] **K_01c**: Einltg einfügen (vor der bestehenden Warnung)
- [ ] **K_01d** (neue Version nach Move): Einltg einfügen

**Ende Phase 3:** Alle Notebooks strukturell konsistent, alle Anker bereinigt. `run_all` läuft.

### Phase 4: Animations-Schalter einführen · **~1 h**
- [ ] `config.json` erweitern (Schema §5.1)
- [ ] `should_skip()` ist bereits in Phase 1 da
- [ ] Alle 13 Animations-Zellen mit Header + `should_skip`-Guard versehen
- [ ] Die 8 aufwendigen statischen Charts (Karten K_01, K_01d) mit Override in `config.json`
- [ ] O_03 §11 (Visualisierungskonventionen) um Schalter-Abschnitt erweitern
- [ ] Test: `run_all` auf unverändertem Stand → sollte Animationen überspringen

### Phase 5: `slide_or_play` Robustheit + Integration · **~1 h**
Dies ist der **einzige frühzeitige lib-Eingriff** (nötig, weil das Widget-Problem aktuell real ist):

- [ ] `lib/widgets.py`: `slide_or_play` mit GIF-Fallback + `base_dir`-Parameter + Diagnose-Docstring
- [ ] `lib/widgets.py`: `_find_frame_dir` mit `base_dir`-Unterstützung
- [ ] In `experimental/K_01d_Grid_Topologie.ipynb` (nach Move in Phase 3d): Cell 30 ersetzen durch Import + Transparenz-Zelle
- [ ] In K_04, K_01c: `display(Image(...))` → `slide_or_play(...)` ersetzen (optional, nice-to-have)
- [ ] User testet lokal: funktioniert `slide_or_play` ODER sauberer GIF-Fallback

**Checkpoint:** Struktur + Schalter + Slider fertig. Ab hier nur noch lib-Migration.

### Phase 6: Lib-Migration step-by-step je Notebook · **~4–5 h**

**Prinzip pro Notebook:**
1. Identifiziere alle `def`-Zellen
2. Funktion nach `lib/<modul>.py` **kopieren** (nicht verschieben — altes noch testen)
3. In Notebook: `from lib.<modul> import ...`-Zeile hinzufügen
4. Alte `def`-Zelle testweise auskommentieren, Zelle ausführen, prüfen dass Funktion erreichbar
5. Wenn grün: alte `def`-Zelle **löschen**
6. Im **Erst-Notebook** einer Funktion: Transparenz-Zelle `show_source(fn)` einfügen
7. Zwischen-Commit pro Notebook

#### 6a) `notebooks/`

| NB | Migrationen | Transparenz-Zellen (neu) |
|---|---|---|
| **NB01** `01_Daten_Laden.ipynb` | `needs_download`, `log_dataindex`, `log_missing`, `_fetch_prices_year`, `_fetch_load_year` → `lib/io_ops.py` + `lib/data_fetchers.py` | `show_source` für alle 5 Funktionen — **erstes Notebook das lib nutzt**, Einführung des Patterns |
| **NB02** `02_Daten_Bereinigung.ipynb` | `log_dataindex`, `log_missing`, `needs_rebuild` — nur noch Import | `show_source(needs_rebuild)` (erste Verwendung) |
| **NB03** `03_Daten_Analyse.ipynb` | `log_dataindex`, `log_missing`, `needs_rebuild`, `simulate_battery` → `lib/simulation.py` | `show_source(simulate_battery)` |
| **NB04** `04_Visualisierungen.ipynb` | Keine def-Zellen aktuell — nur `should_skip`-Integration (falls schon nicht in Phase 4 abgedeckt) | — |
| **NB00** `00_Business_Case.ipynb` | `show_chart` → `lib/plotting.py` | `show_source(show_chart)` |

#### 6b) `kuer/`

| NB | Migrationen | Transparenz-Zellen |
|---|---|---|
| **K_00** | `show`, `show_anim`, `nb_aktiv`, `check_aktiv` → `lib/plotting.py` | Alle 4 |
| **K_01** | `log_dataindex`, `needs_download` (import), `make_spline_h24`, `make_gif_chart`, `find_col`, `map_et`, `fetch_bfs_pxweb`, `draw_base_map`, `update_k01` | `show_source(make_gif_chart)`, `show_source(find_col)`, `show_source(draw_base_map)`, `show_source(fetch_bfs_pxweb)`, `show_source(map_et)` |
| **K_02** | `log_dataindex`, `needs_rebuild`, `_fetch_crossborder_year`, `needs_download` (import) | `show_source(_fetch_crossborder_year)` |
| **K_03** | — (keine def-Zellen) | — |
| **K_04** | `make_spline_w4`, `make_gif_chart` (import) | `show_source(make_spline_w4)` |
| **K_05** | — | — |
| **K_06** | `simulate_battery_reactive`, `simulate_battery_da_optimal` → `lib/simulation.py` | Beide |
| **K_07** | `exp_decay` → `lib/simulation.py` | `show_source(exp_decay)` |
| **K_08** | — | — |
| **K_09** | — | — |
| **K_10** | — | — |
| **K_99** | `sim_arbitrage`, `sim_ev`, `sim_hybrid`, `fmt_be`, `be_est`, `get_trigger` → `lib/simulation.py` | `show_source(sim_hybrid)` (als stellvertretend für die drei Sims), `show_source(be_est)` |

#### 6c) `organisation/`

| NB | Migrationen | Transparenz-Zellen |
|---|---|---|
| **O_01** | `highlight` → `lib/plotting.py` | `show_source(highlight)` (als Illustration im Übersichts-NB) |
| **O_99** | `_nd`, `fmt_size` → `lib/plotting.py` | `show_source(fmt_size)` |
| O_02, O_03, O_04 | — | — |

#### 6d) `experimental/`

| NB | Migrationen | Transparenz-Zellen |
|---|---|---|
| **K_01b** | `find_col` (import) | — (bereits in K_01 gezeigt) |
| **K_01c** | `draw_base_map` (import); `make_gif_fast`, `hydro_h`/`solar_h` lokal belassen (eigene Varianten); `_dyn_*` intern belassen | — |
| **K_01d** (ehem. slider) | **Grosse Migration:** alle 70 Funktionen nach `lib/grid_topo.py` — 1:1 Umzug | `show_source(compute_edge_flows)`, `show_source(make_gif_fast_d)`, `show_source(draw_all_static_overlays)`, `show_source(precompute_flow_cache)` — je eine als Stellvertreter pro Kategorie (4 statt 70) |

**K_01d Besonderheit:** Die Factories (`_make_zone_fn_factory*`) greifen auf globale Variablen zu (`ZONE_PROD_INSTALLED`, `CF`, `CF_SEASONAL`, `ZONE_BASE_CONS`). Beim Umzug nach `lib/grid_topo.py` müssen diese als **explizite Parameter** auftreten:

```python
# vorher (im Notebook):
def zone_produktion_h(zone, h, sais):
    return sum(inst * CF[et] * ... for et, inst in ZONE_PROD_INSTALLED.get(zone,{}).items())

# nachher (in lib/grid_topo.py):
def zone_produktion_h(zone, h, sais, *, zone_installed, cf, cf_seasonal):
    return sum(inst * cf[et] * ... for et, inst in zone_installed.get(zone,{}).items())

# im Notebook Partial/Closure aufbauen:
from functools import partial
from lib.grid_topo import zone_produktion_h as _zone_prod_h_raw
zone_produktion_h = partial(_zone_prod_h_raw, 
                            zone_installed=ZONE_PROD_INSTALLED, 
                            cf=CF, cf_seasonal=CF_SEASONAL)
```

Alternative: `GridContext`-Klasse die die Parameter hält, Accessoren als Methoden. Sauberer, aber grösserer Umbau. **Entscheidung in Phase 6d vor Ort.**

### Phase 7: `grid_topo.py` Konsolidierung (optional) · **~1–2 h**
Nur angehen wenn Phase 6d erfolgreich durchläuft und Zeit bleibt.

- [ ] Smooth-Factory: 5 Wrapper → 1 `make_smooth(raw_fn, kind='spline')`
- [ ] Tagesmittel-Factory: 8 Wrapper → 1 `make_smooth(raw_fn, kind='daily_mean')`
- [ ] Kurven-Helper: `solar_h`, `hydro_h`, `cons_h`, `solar_w`, `hydro_w`, `cons_w` teilweise als `curve(name, t, unit='h', sais=None)` konsolidieren
- [ ] Zielzustand: ~40 statt 70 Funktionen in `grid_topo.py`

Falls übersprungen: `grid_topo.py` hat 70 Funktionen, lesbar aber repetitiv. Nicht kritisch für die Abgabe.

### Phase 8: Dokumentation aktualisieren · **~1 h**
- [ ] `Notebook_Dokumentation.md` überarbeiten: lib-Sektion, neue Struktur-Tabelle
- [ ] `O_01_Project_Overview.ipynb` §6 "Ordner- und Dateistruktur" um `lib/` erweitern
- [ ] `O_03_Konventionen.ipynb` §17: explizite Einleitung/Fazit/Abschluss-Trennung
- [ ] `O_04_Review_Protokoll.ipynb`: Einträge für diese Refactoring-Runde
- [ ] README.md auf Projektebene (falls vorhanden) — lib-Import-Pattern erwähnen

### Phase 9: Regressionstest · **~30 min**
- [ ] `run_all.sh` komplett durchlaufen
- [ ] Output-Files mit Baseline vergleichen (Hashes für CSV/JSON, visuelle Prüfung für PNGs/GIFs)
- [ ] `dataindex.csv` prüfen: alle Einträge vorhanden, keine Duplikate
- [ ] Alle TOC-Links + Inter-Notebook-Nav klickbar
- [ ] Git-Commit als `refactor-v2-complete`

**Gesamtaufwand:** ~10–12 h reine Arbeitszeit, realistisch über 2–3 Tage verteilt.

---

## 8. Abhängigkeitsgraph zwischen Phasen

```
Phase 0 (Baseline)
  ↓
Phase 1 (lib/ Skeleton + show_source + should_skip)
  ↓
Phase 2 (Anker-Hygiene)  ─┐
  ↓                       │  parallel möglich
Phase 3 (Strukturen)  ────┤
  ↓                       │
Phase 4 (Anim-Schalter) ──┘  — braucht should_skip aus Phase 1
  ↓
Phase 5 (slide_or_play) — braucht neue K_01d-Location aus Phase 3d
  ↓
Phase 6 (Lib-Migration step-by-step) — 6a → 6b → 6c → 6d; innerhalb 6x sequenziell je NB
  ↓
Phase 7 (grid_topo Konsolidierung, optional)
  ↓
Phase 8 (Docs) + Phase 9 (Regression)
```

Einzige harte Abhängigkeit: **Phase 1 vor allem anderen** (weil `show_source` schon in Phase 6 massiv benutzt wird, und `should_skip` in Phase 4).

Phase 2 und 3 können in beliebiger Reihenfolge laufen. Wenn das Projekt nach Phase 4 oder 5 pausiert werden muss, ist ein sinnvoller Zwischenstand erreicht: alle Strukturen konsistent, Animationen idempotent, Slider funktioniert. Die lib-Auslagerung ist reine Code-Qualität, nicht funktional nötig für die Abgabe.

---

## 9. Risiken & Gegenmassnahmen

| Risiko | Eintrittswahrscheinlichkeit | Gegenmassnahme |
|---|---|---|
| Broken Imports wegen Pfad-Edge-Cases | Mittel | `_find_project_root()` als erste Funktion in `lib/io_ops.py`; alle lib-Module nutzen sie intern |
| `grid_topo.py` zu gross (~2000 Zeilen) | Hoch | Phase 7 (Konsolidierung) planmässig; sonst ggf. Split in `grid_topo_base.py` + `grid_topo_render.py` |
| Factories mit globalen Variablen bleiben hängen | Hoch | **Phase 6d kritisch:** explizite Parameter oder `GridContext`-Klasse; Modultest mit Minimal-Fixtures |
| Anker-Bereinigung bricht Links | Mittel | Vor Edit: grep über alle `[text](#anchor)` Patterns, Mapping-Tabelle alt→neu (Phase 2 erste Task) |
| `autoreload` verursacht Speicher-Leaks bei langer Session | Niedrig | Kernel-Restart vor finalem Durchlauf |
| ipywidgets nicht in allen Umgebungen (Moodle-Preview / nbviewer) | Mittel | `slide_or_play` hat GIF-Fallback (Phase 5); statisches GIF wird immer parallel gespeichert |
| Halluzinierte Funktionsnamen beim Auslagern | Hoch | `ast.parse()`-Check nach jedem Edit; `assert hasattr(lib.simulation, 'simulate_battery')` in Transparenz-Zellen |
| Transparenz-Zelle zeigt veraltete lib-Version wegen Jupyter-Caching | Niedrig | `%autoreload 2` aktiv in allen Notebooks; `show_source` ruft `inspect.getsource` zur Render-Zeit |
| K_04 / K_01c-Animationen brechen nach Phase 5 (neuer `slide_or_play`) | Mittel | Schrittweise Migration: zuerst neuen Helper importieren, dann alte Display-Zellen ersetzen, pro Zelle testen |
| Kernel-Restart nach pip install vergessen | Hoch (menschlicher Faktor) | README/Checkliste am Anfang jedes Notebook-Runs; `slide_or_play`-Docstring mit Diagnose-Schritten |

---

## 10. Checkliste vor Start

- [ ] v2-Plan durchgelesen
- [ ] Aktuelle Abgabe-Kopie gesichert (ZIP + Git-Commit)
- [ ] Kernel-Versionen fixiert (`jupyterlab`, `ipywidgets`, `jupyterlab_widgets`, `matplotlib`, `pygments`)
- [ ] `autoreload` im Jupyter-Setup getestet
- [ ] Klar: Kür-Freeze bleibt, das Refactoring ist reine Umstrukturierung ohne Funktionsänderung
- [ ] Zeitfenster: 10–12 h verteilbar, Abgabe-Deadline 11.05. genug Puffer
- [ ] **Phase 6 ist optional teilbar** — falls Zeit knapp wird, stoppen nach Phase 5 ist akzeptabel; alle Notebooks funktionieren, lib/-Migration kann in späterer Runde abgeschlossen werden
