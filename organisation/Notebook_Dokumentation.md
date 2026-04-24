# Notebook-Dokumentation — Grid-Arbitrage mit Batteriespeichern
**SC26_Gruppe_2 · ZHAW CAS Information Engineering Scripting**

> **Zielgruppe:** Grundlegendes Python vorhanden, Data-Science-Einsteiger.
> Jede Code-Zelle wird erklärt: was sie tut, warum, welche Library-Funktionen dabei eine Rolle spielen.
> Jede Library-Funktion wird nur beim **ersten Auftreten** in einem eigenen Tabellenabschnitt beschrieben.
>
> **Projektidee:** Kaufe Strom günstig (Preis-Tief), speichere ihn in einer Batterie, speise teuer ein (Preis-Hoch). Lohnt sich das in der Schweiz?

---

## Projektstruktur

```
SC26_Gruppe_2/
├── sync/config.json          ← SSOT: alle Parameter (User pflegt, Notebooks lesen)
├── sync/transfer.json        ← berechnete Ergebnisse zwischen Notebooks
├── sync/dataindex.csv        ← Datenquellen-Register (append-only)
├── organisation/             ← O_01–O_04, O_99 (Querschnittsdokumente)
├── notebooks/                ← NB00–NB04 (Pflicht, Datenpipeline)
├── kuer/                     ← K_00–K_10, K_99 (Kür, erweiterbar)
├── data/raw/ processed/ intermediate/
└── output/charts/<SZ_AKTIV>/
```

**Pfad-Auflösung:** Alle Notebooks liegen eine Ebene unter dem Projektstamm. Pfade werden immer relativ aufgelöst: `BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), '..'))`.

---

---

# Library-Module (`lib/`) <a id="library-module"></a>

Die `lib/`-Struktur bündelt projektweit wiederverwendete Funktionen. Dieses Kapitel beschreibt alle 9 Module mit ihrer öffentlichen API — Signatur, Zweck, Refactoring-Motivation und die interne Bibliotheksnutzung. Die Notebook-Kapitel weiter unten verweisen auf die entsprechenden Anker hier.

**Modul-Übersicht:**

| Modul | Funktionen / Symbole | Hauptzweck |
|-------|---------------------|------------|
| [`lib`](#lib-init) (`__init__.py`) | `ensure_installed` | Meta-Installer für pip-Pakete |
| [`lib.plotting`](#lib-plotting) | `show_source`, `should_skip`, `make_gif_chart`, `show_chart` | Quellcode-Anzeige, Chart-Skip-Logik, GIF-Erzeugung, Chart-Anzeige |
| [`lib.widgets`](#lib-widgets) | `slide_or_play`, `show_animation` | Interaktive Anzeige von Animationen (GIF oder Frame-Slider) |
| [`lib.io_ops`](#lib-io-ops) | `log_dataindex`, `load_transfer`, `save_transfer`, `needs_download`, `needs_rebuild`, `log_missing` | Datenregister, Transfer-JSON, Reload-Checks |
| [`lib.data_fetchers`](#lib-data-fetchers) | `fetch_entsoe_yearly` | ENTSO-E-API-Loader mit 503-Retry |
| [`lib.simulation`](#lib-simulation) | `simulate_battery_dispatch` | Batterie-Dispatch-Kernalgorithmus |
| [`lib.columns`](#lib-columns) | `find_col` | Spaltennamen-Detektion über Synonyme |
| [`lib.grid_topo`](#lib-grid-topo) | `load_kantone`, `KANT_NUM_TO_ABK`, `KANT_ABK_SET` | Schweizer Kantons-Geodaten |
| [`lib.map_animation`](#lib-map-animation) | `make_gif_fast_map`, `clear_background_cache` | Performance-optimierter Karten-GIF-Renderer |

**Importmuster** in jedem NB-Bootstrap:

```python
import sys, os
_PROJECT_ROOT = os.path.abspath('..')
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lib.plotting import show_source, show_chart
from lib.io_ops   import log_dataindex
# ... weitere Module nach Bedarf
```

**Konvention `show_source(fn)`:** Unmittelbar nach einem neuen lib-Import in einem NB steht ein 2-Zellen-Block (Markdown-Erklärung + `show_source(fn)`-Call). Damit sieht der Reviewer den Quellcode inline, ohne die `.py`-Datei öffnen zu müssen.

---

## `lib` (`__init__.py`) <a id="lib-init"></a>

Top-Level-Package-Modul. Exportiert den Meta-Installer `ensure_installed`.

### `ensure_installed(packages, verbose=True, quiet_install=True)` <a id="lib-init-ensure-installed"></a>

```python
ensure_installed(packages: list, verbose: bool = True, quiet_install: bool = True) -> dict
```

**Was sie tut:** Prüft für jeden Eintrag in `packages` ob das Paket importiert werden kann. Fehlende Pakete werden via `pip install` nachinstalliert. Akzeptiert zwei Eintrags-Formen: einfacher String (`'numpy'`) oder Tupel `(pip_name, import_name)` für Pakete mit abweichendem Import-Namen (`('Pillow', 'PIL')`, `('entsoe-py', 'entsoe')`). Rückgabe: Dict mit `installed`, `already`, `failed`-Listen.

**Warum extrahiert:** Das `try: __import__(...) except ImportError: subprocess.check_call(...)`-Muster war in fast jedem NB als erste Code-Zelle dupliziert. Mit `ensure_installed` wird es ein Einzeiler.

**Aufgerufen von:** `O_00_Installer` (als zentraler Setup-Runner), `NB01` (bei Erst-Setup).

**Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `importlib.import_module(name)` | `importlib` | Dynamischer Import zur Laufzeit — wird verwendet weil Paket-Name erst zur Laufzeit bekannt ist. Wirft `ImportError` bei Fehlen. |
| `subprocess.check_call(cmd)` | `subprocess` | Führt einen externen Befehl aus (hier `pip install`) und blockiert bis zum Abschluss. Wirft Exception bei non-zero exit-code. |
| `sys.executable` | `sys` | Pfad zum aktuellen Python-Interpreter — stellt sicher dass pip im selben Environment läuft. |

---

## `lib.plotting` <a id="lib-plotting"></a>

Plot-Helfer: Quellcode-Anzeige für Notebook-Transparenz, Skip-Logik für teure Chart-Erzeugung, GIF-Builder, Chart-Inline-Anzeige.

### `show_source(func, title=None, collapsed=True, mode='markdown', style='default')` <a id="lib-plotting-show-source"></a>

```python
show_source(func: Callable, title: str | None = None,
            collapsed: bool = True, mode: str = 'markdown',
            style: str = 'default') -> None
```

**Was sie tut:** Zeigt den Quellcode einer Funktion aufklappbar inline im Notebook. Zwei Modi: `'markdown'` (nutzt JupyterLab-eigenes Syntax-Highlighting, passt zum aktiven Theme), `'html'` (pygments mit fixem Style, für nbviewer/HTML-Export). Quellcode wird bei jedem Zellen-Run neu via `inspect.getsource` geholt — zeigt immer den aktuellen lib-Stand.

**Warum extrahiert:** Konvention des Projekts — bei jedem ersten Import einer lib-Funktion ins NB soll der Quellcode inline sichtbar sein, damit Review-Dozenten nicht die `.py`-Datei separat öffnen müssen.

**Aufgerufen von:** Alle NBs die lib-Funktionen importieren — typisch 2-5 Aufrufe pro NB, direkt nach dem Bootstrap-Import. Siehe `O_03_Konventionen` §13 für das exakte Muster.

**Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `inspect.getsource(func)` | `inspect` | Liest den Quellcode einer Funktion/Klasse aus der zugehörigen `.py`-Datei. Wirft `TypeError`/`OSError` bei nicht-introspizierbaren Objekten (Built-ins, interaktiv definiert). |
| `IPython.display.Markdown` | `IPython.display` | Rendert einen String als Markdown im Notebook-Output. `<details>`-Tag wird von JupyterLab 4+ unterstützt → aufklappbare Blöcke. |
| `IPython.display.HTML` | `IPython.display` | Rendert HTML direkt. Für pygments-Mode mit fixem Style. |
| `pygments.highlight(src, lexer, formatter)` | `pygments` | Syntax-Highlighting für Code-Strings. Nur bei `mode='html'` genutzt. Fallback auf `<pre>` wenn nicht installiert. |

---

### `should_skip(out_path, asset_type, name, cfg)` <a id="lib-plotting-should-skip"></a>

```python
should_skip(out_path: str, asset_type: str, name: str, cfg: dict) -> bool
```

**Was sie tut:** Entscheidet basierend auf `config.json → animation`-Section ob eine Chart-/GIF-Erzeugung übersprungen werden kann. Liest drei Konfigurations-Ebenen: globaler `animation.modus` (für `asset_type='animation'`), globaler `animation.modus_statisch` (für `asset_type='statisch'`), und pro-Name-Overrides `animation.overrides.<name>`. Gültige Modi: `'skip_if_exists'`, `'always'`, `'force_rebuild'`. `skip_if_exists` + existierende Datei → True (skip); sonst False.

**Warum extrahiert:** Jede teure Chart-Erzeugungs-Logik in NBs hatte eigene Skip-Checks. Zentrale Funktion ermöglicht einheitliche Config-Steuerung über alle NBs.

**Aufgerufen von:** Intern von `make_gif_chart` (wenn `cfg=` übergeben) und `make_gif_fast_map` (über `skip_check`-Callback). Direkt aufgerufen von NBs in allen Chart-Erzeugungs-Zellen als Gate.

**Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `os.path.exists(path)` | `os` | Prüft ob ein Pfad existiert. Basis für `skip_if_exists`-Logik. |
| `os.path.getsize(path)` | `os` | Dateigrösse in Bytes. Wird zusätzlich geprüft (`> 0`) — verhindert dass leere Platzhalter-Dateien als gültig gelten. |
| `warnings.warn(msg, category)` | `warnings` | Gibt eine Warnung aus ohne den Prozess zu stoppen. Für ungültige Modus-Werte im Config — Tippfehler sollen sichtbar sein aber den Lauf nicht brechen. |

---

### `make_gif_chart(fig, update_fn, frames, fps, path, dpi=None, save_frames=None, cfg=None)` <a id="lib-plotting-make-gif-chart"></a>

```python
make_gif_chart(fig, update_fn, frames, fps, path,
               dpi: int | None = None,
               save_frames: bool | None = None,
               cfg: dict | None = None) -> None
```

**Was sie tut:** PIL-basierter GIF-Builder für animierte Charts (nicht Karten — dafür siehe `make_gif_fast_map`). Für jeden Frame ruft sie `update_fn(frame_val)` auf, rendert die `fig` zu PNG in einen BytesIO-Buffer, sammelt die PIL-Images und speichert sie am Ende als animiertes GIF (`loop=0`). Wenn `save_frames=True`, werden zusätzlich die Einzelbilder in `<path>_frames/frame_NNNN.png` abgelegt — für den Slider-Modus von `show_animation`. Wenn `cfg` übergeben wird, konsultiert die Funktion `should_skip` und kehrt früh zurück wenn das GIF schon existiert.

**Warum extrahiert:** Identische Implementierung war in `K_04` (3 Animationen) und `K_01` (1 Animation) dupliziert. Die PIL-Compositing-Logik (BytesIO → `PIL.Image.open` → `.save(save_all=True)`) ist komplex genug um zentral gewartet zu werden.

**Aufgerufen von:** `NB04` (Pflicht-Animationen), `K_01` (BVI-Animation), `K_04` (saisonale Animationen). Für **Karten-GIFs mit statischem Hintergrund** (K_01c, K_01d) wird stattdessen `make_gif_fast_map` verwendet — siehe [lib.map_animation](#lib-map-animation).

**Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `io.BytesIO()` | `io` | In-Memory-Bytes-Buffer. Ermöglicht `fig.savefig(buf, format='png')` ohne Disk-I/O pro Frame → deutlich schneller. |
| `PIL.Image.open(buf)` | `Pillow (PIL)` | Lädt ein Bild aus einem Pfad oder Bytes-Buffer. `.convert('RGB')` reduziert RGBA auf RGB (GIF hat keine Alpha-Unterstützung im Standardprofil). |
| `PIL.Image.save(path, save_all=True, append_images=[...], duration, loop=0)` | `Pillow (PIL)` | Speichert als animiertes GIF — `save_all=True` + `append_images=[frame2, frame3, ...]` koppelt N Frames zu einer Animation. `loop=0` = Endlosschleife. `duration=int(1000/fps)` = ms pro Frame. |
| `fig.savefig(buf, format='png', dpi, bbox_inches='tight')` | `matplotlib.figure` | Rendert die Figure in den Buffer. `bbox_inches='tight'` schneidet leere Ränder weg. |

---

### `show_chart(filename, caption='', width=950, charts_dir=None, as_html=None)` <a id="lib-plotting-show-chart"></a>

```python
show_chart(filename: str, caption: str = '', width: int = 950,
           charts_dir: str | None = None,
           as_html: bool | None = None) -> None
```

**Was sie tut:** Zeigt ein erzeugtes Chart (PNG/JPG/GIF) aus dem `CHARTS_DIR` (oder einem anderen Verzeichnis via `charts_dir`-Parameter) inline im Notebook. Renderer wird automatisch aus der Dateiendung abgeleitet: `.gif` → HTML-`<img>`-Tag (damit die Animation abgespielt wird), sonst → `IPython.display.Image`. `width` steuert die Anzeige-Breite. Fehlt die Datei, wird eine Fehlermeldung auf stdout geschrieben (keine Exception).

**Warum extrahiert:** Jedes Anzeige-NB (`NB00`, `K_00`) hatte eine eigene lokale Hilfsfunktion für dasselbe Ziel. Zentralisierung ermöglicht einheitliche Fehlerbehandlung und GIF/PNG-Auto-Dispatch.

**Aufgerufen von:** `NB00` (Pflicht-Bericht, zeigt alle NB04-Charts), `K_00` (Business-Strategy, 70+ Chart-Einbindungen), `K_01b` (Display-Zellen für EXP-Charts), `K_01d` (Netz-Statik-PNG und Preview-PNG).

**Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `IPython.display.Image(filename=..., width=...)` | `IPython.display` | Lädt und zeigt ein Bild inline. Für statische PNG/JPG. |
| `inspect.stack()[1].frame.f_globals` | `inspect` | Greift auf das globale Namespace des Aufrufers zu — ermöglicht Rückwärtskompatibilität: wenn `charts_dir=None` übergeben wird, wird die globale Variable `CHARTS_DIR` im Aufrufer-NB gelesen. |

---

## `lib.widgets` <a id="lib-widgets"></a>

Interaktive Widgets für Notebook-Anzeige. Zwei Funktionen: `slide_or_play` (Play-Button + Slider für Einzelbild-Ordner) und `show_animation` (High-Level-Wrapper der wahlweise GIF oder Slider zeigt).

### `slide_or_play(name_or_path, framerate=10, image_width='100%', charts_dir=None)` <a id="lib-widgets-slide-or-play"></a>

```python
slide_or_play(name_or_path: str, framerate: int = 10,
              image_width: str = '100%',
              charts_dir: str | None = None) -> None
```

**Was sie tut:** Interaktiver Frame-Viewer mit Play-Button und Slider. Erwartet einen Ordner mit `frame_0000.png`, `frame_0001.png`, ... (typisch erzeugt durch `make_gif_chart` oder `make_gif_fast_map` mit `save_frames=True`). Frames werden einmal in Memory geladen (als Base64 Data-URIs) und dann via `ipywidgets` zwischen ihnen umgeschaltet. Play-Button startet/stoppt die Auto-Wiedergabe; Slider-Drag stoppt Play und wechselt zum Manuell-Modus.

**Warum extrahiert:** Gleiche Logik wäre in mehreren Kür-NBs mit Animationen nötig. Zentrale Implementierung mit robustem `_find_frame_dir`-Helper der verschiedene Input-Konventionen akzeptiert (direkter Ordner, GIF-Pfad, Basename).

**Aufgerufen von:** `K_01d` via `show_animation(..., mode='slider', ...)`. Indirekt durch `show_animation` als Slider-Modus-Implementation.

**Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `ipywidgets.IntSlider(...)` | `ipywidgets` | Schieberegler für ganzzahlige Werte. `continuous_update=True` → Events bei jeder Bewegung. |
| `ipywidgets.ToggleButton(...)` | `ipywidgets` | Ein/Aus-Knopf mit eigenem Zustand. `value=True/False` steuert Play-Modus. |
| `ipywidgets.HTML(value='...')` | `ipywidgets` | Rendert HTML direkt — hier für `<img src=...>` mit Base64-Data-URI (vermeidet Pfad-Auflösungsprobleme). |
| `ipywidgets.HBox/VBox` | `ipywidgets` | Layout-Container (horizontal/vertikal). |
| `.observe(callback, names='value')` | `ipywidgets` | Registriert Callback bei Wert-Änderung. Callback bekommt `change`-Dict mit `new`/`old`. |
| `threading.Thread(target=fn, daemon=True)` | `threading` | Hintergrund-Thread für die Play-Schleife — Notebook-Zelle blockiert nicht. `daemon=True` → Thread endet mit dem Haupt-Prozess. |
| `threading.Event` | `threading` | Signal-Mechanismus für sauberes Stoppen des Play-Threads. |
| `base64.b64encode(bytes)` | `base64` | Frame-PNG-Bytes in ASCII-String kodieren für Data-URI. |
| `glob.glob(pattern)` | `glob` | Findet Dateien per Wildcard (`frame_*.png`). |

---

### `show_animation(path, mode='gif', framerate=10, width=1100, caption=None)` <a id="lib-widgets-show-animation"></a>

```python
show_animation(path: str, mode: str = 'gif', framerate: int = 10,
               width: int | str = 1100,
               caption: str | None = None) -> None
```

**Was sie tut:** High-Level-Anzeige für Animationen. `mode='gif'` zeigt das fertige GIF inline (via `Image`- oder `HTML`-Tag je nach `width`-Typ); `mode='slider'` ruft `slide_or_play` auf dem zugehörigen `<path>_frames/`-Ordner auf. Die Funktion ist die **kanonische** Anzeige-Methode für Animationen projektweit — vereinheitlicht `K_00`, `K_01`, `K_04`, `K_01c`, `K_01d`.

**Warum extrahiert:** Vor Phase 5 hatten die NBs drei verschiedene Muster: `display(Image(filename=_p))` (K_01c, K_01d statisch), `show_chart('xyz.gif', ...)` (K_00), gar keine Anzeige (K_04, K_01). Konvention war nicht durchgehalten. `show_animation` + `mode`-Parameter macht die Wahl zwischen GIF und interaktivem Slider zur Laufzeit-Entscheidung.

**Aufgerufen von:** `K_00` (5×), `K_01` (1×), `K_04` (3×), `K_01c` (10×), `K_01d` (5×). Total 24 Aufrufe projektweit.

**Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `IPython.display.display(obj)` | `IPython.display` | Gibt ein Objekt im Notebook-Output aus (wenn nicht das Zellen-Endergebnis ist). |

---

## `lib.io_ops` <a id="lib-io-ops"></a>

I/O- und Daten-Provenienz-Helfer: Protokoll aller geladenen Datensätze, Transfer-JSON zwischen NBs, Reload-Prüfungen für API-Caches.

### `log_dataindex(filename, source_url, local_path, data_type, rows=None, size_kb=None, status='active', note='', dataindex_path=None)` <a id="lib-io-ops-log-dataindex"></a>

```python
log_dataindex(filename: str, source_url: str, local_path: str,
              data_type: str,
              rows: int | None = None, size_kb: float | None = None,
              status: str = 'active', note: str = '',
              dataindex_path: str | None = None) -> None
```

**Was sie tut:** Schreibt einen Eintrag ins Provenienz-Register `sync/dataindex.csv` (append-only). Wenn bereits ein aktiver Eintrag für denselben `filename` existiert, wird dieser als `status='superseded'` markiert mit Zeitstempel in `superseded_at`. So ergibt sich eine Versions-Historie pro Datei: man sieht welche Rohdaten wann geladen und welche durch neue ersetzt wurden.

**Warum extrahiert:** Identische Funktionsdefinition war in allen Pflicht-NBs und mehreren Kür-NBs dupliziert (R-07 im Review-Protokoll). 13 Write-Operationen ins `dataindex.csv` projektweit — alle müssen dasselbe Schema haben.

**Aufgerufen von:** `NB01` (bei jedem API-Download), `NB02` (bei bereinigten Daten-CSVs), `NB03` (bei Intermediate-CSVs), `K_01` (BFE-Anlagen, Kantone), `K_02` (Grenzflüsse), `K_99` (kombinierte Ergebnisse).

**Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.DataFrame(data, columns=...)` | `pandas` | Erstellt einen tabellarischen Datensatz aus Dict/List. Grundbaustein aller dataindex-Operationen. |
| `pd.read_csv(path)` | `pandas` | Lädt CSV-Datei als DataFrame. |
| `pd.concat([df1, df2], ignore_index=True)` | `pandas` | Fügt mehrere DataFrames vertikal zusammen. Ersetzt das veraltete `df.append()`. `ignore_index=True` = Index wird neu gesetzt. |
| `df.to_csv(path, index=False)` | `pandas` | Speichert DataFrame als CSV. `index=False` verhindert, dass der automatische Index als erste Spalte gespeichert wird. |
| `datetime.utcnow().isoformat(timespec='seconds')` | `datetime` | Aktueller UTC-Zeitstempel als ISO-8601-String (`2024-01-15T10:30:00`). Maschinenlesbar und sortierbar. |

---

### `load_transfer(path='../sync/transfer.json', key=None, default=None)` <a id="lib-io-ops-load-transfer"></a>

```python
load_transfer(path: str = '../sync/transfer.json',
              key: str | None = None,
              default: any = None) -> dict | any
```

**Was sie tut:** Lädt `sync/transfer.json` und gibt entweder das komplette Dict oder einen Teilbaum zurück. Fehlt die Datei oder ist sie leer → Fallback auf `default` (bei `key=None`: `{}`). Mit `key` wird nur dieser Top-Level-Key zurückgegeben (z.B. `'datenzeitraum'`, `'simulation'`). Das erlaubt kompakten Code in den NBs: `n_years = load_transfer(key='datenzeitraum').get('n_years', 1)`.

**Warum extrahiert:** Jedes Konsumenten-NB hatte eine eigene Crash-Guard-Logik für leere/fehlende `transfer.json`. Zentrale Funktion reduziert diesen Boilerplate auf einen Funktionsaufruf.

**Aufgerufen von:** `NB02`, `NB03`, `NB04`, `K_00`, `K_05`, `K_06`, `K_09`, `K_10`, `K_99` — alle Konsumenten der Pipeline.

**Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `json.load(f)` | `json` | Liest eine JSON-Datei und gibt ein Python-Dict/-List zurück. |

---

### `save_transfer(data, path='../sync/transfer.json', key=None)` <a id="lib-io-ops-save-transfer"></a>

```python
save_transfer(data: dict | any,
              path: str = '../sync/transfer.json',
              key: str | None = None) -> dict
```

**Was sie tut:** Schreibt Daten nach `transfer.json` **mit Merge-Logik**: Lädt die existierende Datei (falls vorhanden), mergt `data` hinein, schreibt zurück. Bei `key=None` muss `data` ein Dict sein → wird auf oberster Ebene gemerged (`existing.update(data)`). Bei gegebenem `key` wird `data` unter diesem Top-Level-Key abgelegt. Rückgabe: das komplette Dict nach dem Write (für Verifikation).

**Warum extrahiert:** Kritischer Punkt — ohne Merge-Logik würden NBs die Werte anderer NBs überschreiben (z.B. K_06 würde `datenzeitraum` von NB01 löschen wenn es `dispatch_optimierung` schreibt). Frühere NB-lokale Implementierungen machten den Merge inkonsistent (manche ohne Merge → Bug).

**Aufgerufen von:** `NB01` (schreibt `datenzeitraum`), `NB03` (`simulation`), `K_06` (`dispatch_optimierung`), `K_09` (`eigenverbrauch`), `K_10` (`produkt`), `K_99` (`hybrid_simulation`).

**Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `json.dump(obj, f, indent=2, ensure_ascii=False)` | `json` | Schreibt Python-Objekt als JSON-Datei. `indent=2` für lesbare Formatierung, `ensure_ascii=False` für Umlaute ohne Escape. |

---

### `needs_download(path, min_kb, key, force_reload=None)` <a id="lib-io-ops-needs-download"></a>

```python
needs_download(path: str, min_kb: float, key: str,
               force_reload: dict | None = None) -> bool
```

**Was sie tut:** Entscheidet ob ein externer Download nötig ist. True wenn: (1) `force_reload[key]` gesetzt, (2) Datei fehlt, (3) Datei existiert aber kleiner als `min_kb * 1024` Bytes (abgebrochener Download). Wenn `force_reload=None`, wird im Caller-Scope die globale Variable `FORCE_RELOAD` aus `config.json` gelesen (Rückwärtskompatibilität).

**Warum extrahiert:** Vor Phase 6.5 hatten 5 NBs eigene Duplikate dieser Logik. Die Byte-Schwelle-Check ist kritisch: ohne ihn werden abgebrochene Downloads (0 Bytes) für gültig gehalten und nicht neu geladen.

**Aufgerufen von:** `NB01` (vor ENTSO-E-Downloads), `K_01` (vor BFE-GeoPackage-Download), `K_02` (vor Grenzfluss-Downloads).

**Verwendete Bibliotheksobjekte**

Nur Standardbibliothek (`os.path.exists`, `os.path.getsize`, `inspect.stack()` — alle bereits bei `show_source` / `should_skip` beschrieben).

---

### `needs_rebuild(filepath, min_rows, ds_key, force_reload=None)` <a id="lib-io-ops-needs-rebuild"></a>

```python
needs_rebuild(filepath: str, min_rows: int, ds_key: str,
              force_reload: dict | None = None) -> bool
```

**Was sie tut:** Pendant zu `needs_download`, aber zeilen-basiert statt byte-basiert. Für Intermediate-CSVs wo die Byte-Grösse nichts aussagt (4 Zeilen = ~280 Bytes, sind aber valide). True wenn: force_reload gesetzt, Datei fehlt, oder weniger als `min_rows` Datenzeilen (Header zählt nicht).

**Warum extrahiert:** Löst den alten A-09-Bug (Dateigrössen-Schwellwert `>1000 bytes` filterte valide kleine CSVs als "kaputt" aus).

**Aufgerufen von:** `NB02`, `NB03`, `K_01` (vor Zwischendatei-Erzeugungen).

**Verwendete Bibliotheksobjekte**

Nur Standardbibliothek (`sum(1 for _ in open(...))` als pythonisches Line-Count ohne die komplette Datei in Memory zu laden).

---

### `log_missing(source, reason, data_folder='../data', dataindex_path=None)` <a id="lib-io-ops-log-missing"></a>

```python
log_missing(source: str, reason: str,
            data_folder: str = '../data',
            dataindex_path: str | None = None) -> None
```

**Was sie tut:** Protokolliert fehlende/fehlerhafte externe Datenquellen. Schreibt zwei Einträge: (1) Klartext-Log in `<data_folder>/missing.txt` (append), (2) `dataindex.csv`-Eintrag mit `status='error'` via `log_dataindex`.

**Warum extrahiert:** Gleiches Log-Format in mehreren NBs nötig — Fehler bei einem API-Download darf die Pipeline nicht silent ignorieren lassen. `missing.txt` ermöglicht nachträgliches Nachvollziehen welche Quellen ausgefallen sind.

**Aufgerufen von:** `NB01` (bei HTTP-Fehlern während ENTSO-E-Downloads), `K_02` (bei Grenzflüssen die nicht verfügbar sind).

**Verwendete Bibliotheksobjekte**

Nutzt intern `log_dataindex` und Standard-I/O (`open(..., 'a')` für append).

---

## `lib.data_fetchers` <a id="lib-data-fetchers"></a>

HTTP-/API-Loader mit Retry-Logik für externe Datenquellen.

### `fetch_entsoe_yearly(query_fn, year, max_retries=3, wait_s=20, tz='Europe/Zurich')` <a id="lib-data-fetchers-fetch-entsoe-yearly"></a>

```python
fetch_entsoe_yearly(query_fn: Callable, year: int,
                    max_retries: int = 3, wait_s: int = 20,
                    tz: str = 'Europe/Zurich') -> any
```

**Was sie tut:** Wrapper um beliebige ENTSO-E-Queries mit jahresweisem Download und HTTP-503-Retry-Logik. Die konkrete Query wird als Callable `query_fn(start, end)` übergeben (typisch als Lambda). Bei HTTP 503 (Server überlastet) wird `wait_s` Sekunden gewartet und bis zu `max_retries`-mal neu versucht. Andere HTTP-Fehler werden direkt weitergereicht (z.B. 401 bei ungültigem API-Key).

**Warum extrahiert:** ENTSO-E gibt bei Serverüberlastung regelmässig 503 zurück. Jahresweiser Abruf mit Pause ist zuverlässiger als ein grosser Mehrjahresrequest. Gleiche Retry-Logik war früher in NB01 (Preise, Last) und K_02 (Grenzflüsse) dupliziert.

**Aufgerufen von:** `NB01` (Day-Ahead-Preise, Netzlast — je 3 Jahre à 1 Call), `K_02` (Grenzflüsse CH-DE, CH-AT, CH-FR, CH-IT — je 3 Jahre à 4 Grenzen).

**Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.Timestamp(str, tz=...)` | `pandas` | Erzeugt einen zeitzonenbehafteten Zeitpunkt. `tz='Europe/Zurich'` ist wichtig für korrekte Winterzeit/Sommerzeit-Behandlung — ENTSO-E verlangt lokal-bezogene Requests. |
| `time.sleep(s)` | `time` | Blockiert den Thread für `s` Sekunden. Zwischen Retry-Versuchen. |
| `requests.exceptions.HTTPError` | `requests` | Exception-Klasse für HTTP 4xx/5xx-Fehler. Wird via `'503' in str(e)` nach Status geprüft (keine strukturierte Exception bei `entsoe-py`). |

---

## `lib.simulation` <a id="lib-simulation"></a>

Batterie-Dispatch-Simulation (Kern-Algorithmus des Projekts).

### `simulate_battery_dispatch(prices_df, capacity_kwh, power_kw, efficiency, charge_q, discharge_q, soc_min_pct, soc_max_pct)` <a id="lib-simulation-simulate-battery-dispatch"></a>

```python
simulate_battery_dispatch(prices_df: pd.DataFrame,
                          capacity_kwh: float, power_kw: float,
                          efficiency: float,
                          charge_q: float, discharge_q: float,
                          soc_min_pct: float,
                          soc_max_pct: float) -> pd.DataFrame
```

**Was sie tut:** Schwellenwert-Dispatch-Modell auf Basis tagesbasierter Preisquantile. Regel pro Stunde:

- **LADEN** wenn Preis ≤ p(`charge_q`) des Tages UND SoC < `soc_max`
- **ENTLADEN** wenn Preis ≥ p(`discharge_q`) des Tages UND SoC > `soc_min`
- sonst **idle**

Break-even-Bedingung dokumentiert im Docstring: `p(discharge_q) × η > p(charge_q)`. Die Funktion berechnet Tages-Quantile einmal vorab (O(n) statt O(n²)), konvertiert zu NumPy-Arrays (`.to_numpy()`) und führt die sequenzielle Simulation (SoC-Update frame-by-frame) in reinem Python-Loop durch (SoC kann nicht vektorisiert werden — jede Stunde hängt vom Vorzustand ab). Rückgabe: DataFrame mit `timestamp`, `action` (`'charge'`/`'discharge'`/`'idle'`), `cashflow_eur`, `grid_delta_kw`.

**Warum extrahiert:** Zentrale Berechnung des Projekts — jede Änderung muss an einer Stelle passieren. Vor Phase 6.4 war die Funktion in NB03 (`simulate_battery`) und K_06 (`simulate_battery_reactive`) als byte-gleiche Duplikate. Bit-identische numerische Verifikation vor/nach Migration bestätigt: Jahres-Erlöse unverändert auf 0.01 EUR (R-09 im Review-Protokoll).

**Aufgerufen von:** `NB03` (4 Segmente: Privat/Gewerbe/Industrie/Utility), `K_06` (Vergleich reaktiv vs. day-ahead-optimal).

**Nicht hier:** `K_99.sim_arbitrage` — eigenständiges schlankeres Modell mit anderer Parametrierung und SoC-Bounds. Siehe NB-Kapitel K_99.

**Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `df.dt.date` | `pandas (.dt)` | Extrahiert das Kalenderdatum (ohne Zeit) aus Datetime-Spalte. Für die Tages-Gruppierung. |
| `df.groupby(col).agg(p_lo=lambda x: x.quantile(q), ...)` | `pandas` | Gruppiert nach Datum und berechnet mehrere Aggregate pro Gruppe — hier beide Quantile in einem Durchgang. |
| `df.join(agg_df, on=col)` | `pandas` | Verbindet DataFrame mit gruppierten Aggregaten — jede Zeile erhält die p_lo/p_hi ihres Tages. |
| `df.to_numpy()` | `pandas` | Konvertiert Series/DataFrame zu NumPy-Array. Notwendig für die Dispatch-Simulation ohne Python-Overhead bei Zellen-Zugriff. |
| `np.empty(n, dtype='U10')` | `numpy` | Erstellt uninitialisiertes Array. `dtype='U10'` = Unicode-Strings max. 10 Zeichen — für die `actions`-Spalte. |
| `np.zeros(n)` | `numpy` | Array mit Nullen. Für `cashflows` und `grid_delta`. |

---

## `lib.columns` <a id="lib-columns"></a>

DataFrame-Spalten-Helfer.

### `find_col(df, *kws)` <a id="lib-columns-find-col"></a>

```python
find_col(df: pd.DataFrame, *kws: str) -> str | None
```

**Was sie tut:** Sucht die erste Spalte in `df`, deren Name (case-insensitiv) eines der Keywords als Substring enthält. Reihenfolge in `kws` bestimmt Priorität: erstes Keyword, das einen Match liefert, gewinnt. Rückgabe: Spaltenname oder `None`.

**Warum extrahiert:** Externe Datenquellen (BFE, BFS, swisstopo) ändern gelegentlich ihre Spaltennamen. Statt im Code hart zu hardcoden wird eine Liste von Synonymen durchsucht (`find_col(gdf, 'canton', 'kanton', 'kt')`). Vor Phase 6.5 waren zwei lokale Duplikate dieser Funktion in K_01 und K_01b.

**Aufgerufen von:** `K_01` (BFE-Spalten-Detektion bei Subkategorien, Kantonen), `K_01b` (dito).

**Verwendete Bibliotheksobjekte**

Nur reiner Python (kein pandas-Call — iteriert über `df.columns`).

---

## `lib.grid_topo` <a id="lib-grid-topo"></a>

Schweizer Kantons-Geodaten: Download, Laden, Kürzel-Mapping.

### `load_kantone(data_dirs, download_url=None, download_target=None, min_file_size=50_000, verbose=True)` <a id="lib-grid-topo-load-kantone"></a>

```python
load_kantone(data_dirs: list[str] | str,
             download_url: str | None = None,
             download_target: str | None = None,
             min_file_size: int = 50_000,
             verbose: bool = True) -> gpd.GeoDataFrame | None
```

**Was sie tut:** Lädt Schweizer Kantonsgrenzen aus einem GeoPackage-Cache. Probiert mehrere Pfad-Kandidaten (`data_dirs` — Liste oder einzelner String) nacheinander, nimmt den ersten der existiert und grösser als `min_file_size` Bytes ist. Optional: falls alle Pfade fehlschlagen und `download_url` gesetzt ist, wird die ZIP heruntergeladen und die `.gpkg` extrahiert. Normalisiert das CRS auf EPSG:4326 und ergänzt eine `KAB`-Spalte mit 2-Buchstaben-Kürzeln (z.B. `'ZH'`, `'BE'`), die über drei Strategien ermittelt wird: (1) direkte Spalte `icc`/`kab`/`abbreviation`, (2) Zahlenspalte 1-26 via `KANT_NUM_TO_ABK`, (3) Kürzel-Spalte case-insensitive matching gegen `KANT_ABK_SET`.

**Warum extrahiert:** Konsolidierung drei inline-Varianten aus K_01 (6'530 chars), K_01c (2'084 chars), K_01d (inline). K_01 hatte Download-Fallback, K_01c und K_01d hatten nur Multi-Path-Cache. Zentrale Funktion deckt alle Use-Cases ab und ist robuster gegen BFE-CSV-Schema-Änderungen.

**Aufgerufen von:** `K_01`, `K_01c`, `K_01d`. Für jede NB wird die Kantonskarte als Base-Layer für Visualisierung geladen.

**Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `gpd.read_file(path, layer=...)` | `geopandas` | Lädt Geodaten aus GeoPackage/Shapefile/GeoJSON. `layer=` wählt einen Layer in GeoPackage (die kann mehrere enthalten). |
| `gpd.list_layers(path)` | `geopandas` | Listet alle Layer in einem GeoPackage. Gibt DataFrame mit `name`-Spalte zurück. |
| `.to_crs(epsg=4326)` | `geopandas` | Transformiert die Geometrien in ein anderes Koordinatensystem. `epsg=4326` = WGS84 (Lon/Lat). BFE-Daten kommen oft in CH1903+ (EPSG:2056). |
| `requests.get(url, stream=True, timeout=120)` | `requests` | HTTP GET-Request. `stream=True` für Chunk-basierten Download grosser Dateien. |
| `zipfile.ZipFile(path)` + `.open(name)` | `zipfile` | Liest Einzeldateien aus ZIP-Archiv ohne volles Entpacken. |

**Konstanten (im Modul exportiert)**

| Konstante | Typ | Beschreibung |
|---|---|---|
| `KANT_NUM_TO_ABK` | `dict[int, str]` | Mapping Kantons-Nummer (1-26) → 2-Buchstaben-Kürzel (`{1: 'ZH', 2: 'BE', ...}`). Nützlich für BFE-Daten die Kantone numerisch ausweisen. |
| `KANT_ABK_SET` | `set[str]` | Alle 26 gültigen Kürzel als Set. Für schnelles Matching `vals.isin(KANT_ABK_SET)`. |

---

## `lib.map_animation` <a id="lib-map-animation"></a>

Performance-optimierter Karten-GIF-Renderer.

### `make_gif_fast_map(draw_background, draw_dynamic, n_frames, fps, path, map_xlim, map_ylim, dpi=90, fig_size_in=(14, 9), facecolor='#0d1117', ax_facecolor='#090d14', bg_cache_key=None, skip_check=None, save_frames=True, verbose=True)` <a id="lib-map-animation-make-gif-fast-map"></a>

```python
make_gif_fast_map(draw_background: Callable,
                  draw_dynamic: Callable,
                  n_frames: int, fps: int, path: str,
                  map_xlim: tuple, map_ylim: tuple,
                  dpi: int = 90, fig_size_in: tuple = (14, 9),
                  facecolor: str = '#0d1117',
                  ax_facecolor: str = '#090d14',
                  bg_cache_key: str | None = None,
                  skip_check: Callable | None = None,
                  save_frames: bool = True,
                  verbose: bool = True) -> None
```

**Was sie tut:** Erzeugt ein animiertes GIF mit statischem Kartenhintergrund + dynamischen Layern pro Frame. Der Hintergrund wird **einmal** via `draw_background(ax)` gerendert und als NumPy-Array (RGBA) in `_BG_CACHE` gecacht (wenn `bg_cache_key` gesetzt). Pro Frame wird dann eine frische `plt.figure` erzeugt, das gecachte Array via `ax.imshow(...)` platziert, und `draw_dynamic(ax, frame_idx, n_frames)` für die Overlay-Layer aufgerufen. Das Ergebnis wird als PNG in einen BytesIO-Buffer gerendert, in `<path>_frames/` gespeichert (falls `save_frames=True` — für Slider-Modus von `show_animation`) und zusammen mit allen anderen Frames als GIF gespeichert. `skip_check`-Callback ermöglicht frühzeitigen Return wenn das GIF bereits existiert.

**Warum extrahiert:** Phase 7b — zuvor hatten K_01c (`make_gif_fast` mit PIL-Compositing) und K_01d (`make_gif_fast_d` mit imshow-Methode) zwei Varianten derselben Logik. Die imshow-Methode (K_01d) ist pixel-perfekt und wurde als Lead übernommen. Background-Cache liefert 3-5× Speedup bei schwerem GeoPandas-Hintergrund mit 96 Frames.

**Aufgerufen von:** `K_01c` (10×, verschiedene `zone_alpha`-Werte mit eigenen Cache-Keys `bg_0.06`/`bg_0.08`/`bg_0.12`), `K_01d` (4×, gemeinsamer Cache-Key `'grid'` weil der Topologie-Hintergrund für alle Animationen gleich ist).

**Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `fig.canvas.draw()` | `matplotlib.figure` | Rendert die Figure in den internen Canvas-Buffer, ohne sie anzuzeigen. Nötig damit `buffer_rgba()` gültige Daten liefert. |
| `fig.canvas.get_width_height()` | `matplotlib.figure` | Aktuelle Canvas-Pixel-Grösse als `(w, h)`-Tuple. |
| `fig.canvas.buffer_rgba()` | `matplotlib.figure` | Gibt das gerenderte Bild als RGBA-Byte-Buffer zurück. |
| `np.asarray(buf).reshape(h, w, 4)` | `numpy` | Konvertiert zu 3D-Array `(height, width, 4)`. `.copy()` ist wichtig weil der Buffer ungültig wird sobald die Figure geschlossen ist. |
| `ax.imshow(arr, extent=[xmin, xmax, ymin, ymax], origin='upper', zorder=0)` | `matplotlib.axes` | Zeichnet ein Array als Bild in die Axes. `extent` = Achsen-Koordinaten der Ränder, `origin='upper'` weil Bild-Arrays top-down indiziert sind, `zorder=0` legt das Bild in den Hintergrund. |

### `clear_background_cache()` <a id="lib-map-animation-clear-background-cache"></a>

```python
clear_background_cache() -> None
```

**Was sie tut:** Leert den Modul-weiten `_BG_CACHE`. Nützlich bei iterativer Entwicklung — wenn die Hintergrund-Layer geändert wurden, müssen die gecachten Arrays verworfen werden.

**Warum extrahiert:** Der Cache ist ein Modul-Global — ohne diese Funktion wäre ein vollständiger Kernel-Restart nötig um ihn zu leeren.

**Aufgerufen von:** Optional in Development-Zellen von K_01c, K_01d (auskommentiert, wird nur bei Bedarf aktiviert).

---

# Organisation (`organisation/`)

## O_01 — Projektübersicht (`O_01_Project_Overview.ipynb`)
Einstiegspunkt des Projekts. Enthält Motivation, Methodik, Notebook-Map, Ordnerstruktur, Projektplan, Aufgabenverteilung und potenzielle Erweiterungen. Kein fachlicher Recheninhalt ausser der Projektplan-Tabelle.

### Zelle 1 — Projektplan
**Was passiert:** Status-Konstanten werden definiert (`⬜ Offen`, `🔄 In Arbeit`, `✅ Erledigt`). Eine Liste aller Projektaufgaben mit Verantwortlichkeit, Frist und Status wird als formatierte Tabelle ausgegeben. Versionsanzeige von `pandas` und Ausführungszeitpunkt.
**Warum so:** Ein einziger Blick zeigt den kompletten Projektstatus. `pandas` ist die einfachste Lösung für eine formatierte Tabelle im Notebook.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.DataFrame()` | `pandas` | Erstellt einen tabellarischen Datensatz (Zeilen × Spalten) aus einer Python-Liste oder einem Dictionary. Grundbaustein für alle Tabellenoperationen im Projekt. |

---

## O_02 — Glossar (`O_02_Glossar.ipynb`)
Reines Markdown-Notebook. Kein ausführbarer Code. Definiert alle Fachbegriffe aus Energiemarkt, Finanzen, Technik und Statistik mit NB-Querverweisen. Enthält Anker-IDs (`<a id="g-...">`) für direkte Verlinkung aus anderen Notebooks.

Abschnitte: Energiemarkt · Finanzen & Wirtschaftlichkeit · Batterie & Technik · Statistik & Modell · Projektspezifische Begriffe · Abkürzungen.

Neu in dieser Version: Einträge für **Dispatch-Break-even-Bedingung** (`p(discharge_q) × η > p(charge_q)`), **Mindest-Spread** (`Spread_min = p(charge_q) × (1/η − 1)`) und **Relativer Effizienzverlust** (`(1/η − 1)`).

---

## O_03 — Konventionen (`O_03_Konventionen.ipynb`)
Lebendes Regelwerk für alle Notebooks. Die einzige Code-Zelle zeigt eine Muster-Lade-Sequenz (vollständig auskommentiert — nur Referenz, kein ausführbarer Code).

Themen: Markdown-Konventionen · Konfigurationsabhängige Werte (⚙/📊-Marker) · Zentrale Konfiguration (`../sync/config.json`) · Datenzeitraum-Empfehlungen · Ergebnistransfer (`../sync/transfer.json`) · Chart-Naming · Visualisierungskonventionen · Abschlussblock · Review-Checkliste · Musterzellen · Sprach- & Terminologiekonvention · Ordnerstruktur & Pfad-Konvention · Notebook-Struktur Pflicht vs. Kür · Kür-Erweiterbarkeit.

**Sektion 12.3 (Hinweis):** `01b_Daten_Sim.ipynb` und `02b_Sim_Analyse.ipynb` wurden per 15.04.2026 entfernt. `MODE='sim'` ist in verbleibenden Notebooks als toter Code erhalten, aber nicht mehr unterstützt.

---

## O_04 — Review-Protokoll (`O_04_Review_Protokoll.ipynb`)
Dokumentiert Qualitätssicherung, rollenbasierte Reviews und protokollierte Korrektur-Iterationen. Eine Code-Zelle liest `../sync/transfer.json` und zeigt eine Verifikationsübersicht.

---

## O_99 — Datenprovenienz (`O_99_Datenprovenienz.ipynb`)
Dokumentiert alle Datenquellen: Herkunft, Lizenz, Verarbeitungsschritte. **Manuell ausführen** — nicht Teil von `run_all`.

### Zellen 1–2 — Setup & dataindex laden
**Was passiert:** Libraries laden, Versionsanzeige. `../sync/dataindex.csv` laden — das Register, das NB01 automatisch befüllt hat. Alle Einträge nach Typ kategorisieren.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.notna()` | `pandas` | Prüft elementweise ob Werte NICHT NaN sind. Gegenteil von `pd.isna()`. Hier für bedingte Formatierung: Zeilenzahl nur anzeigen wenn vorhanden. |

### Zellen 3–7 — Charts A–D
**Was passiert:** Chart A: Zeitlinie aller dataindex-Einträge als Scatter-Plot. Chart B: Dateigrössenvergleich aller aktiven Dateien. Chart C: Pipeline-Flussdiagramm (Datenfluss von Rohdaten durch alle Notebooks). Chart D: Versionshistorie (active/superseded/error-Anteile) und Pipeline-Volumen.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `import matplotlib.dates as mdates` | `matplotlib.dates` | Modul für datumsbezogene Achsenformatierung. `mdates.DateFormatter('%b %Y')` formatiert Ticks als 'Jan 2024'. `mdates.AutoDateLocator()` wählt automatisch sinnvolle Tick-Abstände. |
| `mpatches.FancyBboxPatch()` | `matplotlib.patches` | Rechteck mit abgerundeten Ecken. `boxstyle='round,pad=0.3'` = abgerundete Ecken mit Innenabstand. Hier für Pipeline-Flussdiagramm-Knoten. |

---

# Pflicht (`notebooks/`)

## NB01 — Daten laden (`01_Daten_Laden.ipynb`)
Einziger Zweck: echte Rohdaten von der ENTSO-E-API herunterladen und auf der Festplatte speichern. Alle nachgelagerten Notebooks bauen darauf auf.

### Zelle 1 — Abhängigkeitsprüfung
**Was passiert:** Für vier Pakete (`pandas`, `requests`, `numpy`, `entsoe-py`) wird geprüft, ob sie installiert sind. Fehlt eines, wird es automatisch über `pip install` nachinstalliert.
**Warum so:** Jupyter-Notebooks laufen auf unterschiedlichen Rechnern. Diese Zelle stellt sicher, dass das Notebook überall ohne manuelle Installation funktioniert.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `subprocess.check_call()` | `subprocess` | Führt einen externen Befehl aus (hier: `pip install`) und blockiert bis zum Abschluss. Wirft eine Exception wenn der Befehl fehlschlägt. |
| `__import__()` | `builtins` | Versucht ein Modul zu importieren. Hier für Existenzprüfung: schlägt fehl → `ImportError` → Paket wird nachinstalliert. |

### Zelle 2 — Konfiguration laden
**Was passiert:** Libraries werden geladen, `../sync/config.json` wird als Python-Dictionary `CFG` eingelesen. Daraus werden Reload-Schalter, Datenzeitraum und Verzeichnispfade extrahiert. Für Cache-Validierung wird [`needs_download`](#lib-io-ops-needs-download) aus `lib.io_ops` verwendet (prüft Datei-Existenz, Mindestgrösse und `FORCE_RELOAD`-Flags aus Config).
**Warum so:** `../sync/config.json` ist der einzige Ort, wo Einstellungen gesetzt werden (Single Source of Truth). Code enthält nie hardcodierte Pfade oder Parameter.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `json.load()` | `json` | Liest eine JSON-Datei und gibt ein Python-Dictionary/-List zurück. Hier für `../sync/config.json` (Einstellungen) und `../sync/transfer.json` (Notebook-zu-Notebook-Übergabe). |
| `json.dump()` | `json` | Schreibt ein Python-Objekt als JSON in eine Datei. `indent=2` für lesbare Formatierung, `ensure_ascii=False` für Umlaute. |
| `os.path.join()` | `os` | Setzt Pfadteile plattformunabhängig zusammen (Backslash auf Windows, Slash auf Linux/Mac). Immer dieser Funktion statt Stringverkettung. |
| `os.makedirs()` | `os` | Erstellt ein Verzeichnis inkl. aller fehlenden Elternverzeichnisse. `exist_ok=True` unterdrückt den Fehler wenn das Verzeichnis bereits existiert. |
| `os.path.exists()` | `os` | Prüft ob ein Pfad (Datei oder Verzeichnis) existiert. Gibt `True`/`False` zurück. |
| `os.path.getsize()` | `os` | Gibt die Dateigrösse in Bytes zurück. Wird zur Validierung genutzt: Datei existiert aber ist zu klein → unvollständig, neu laden. |

### Zelle 3 — Datenregister-Aufruf
**Was passiert:** Nach jedem erfolgreichen Download wird [`log_dataindex`](#lib-io-ops-log-dataindex) aus `lib.io_ops` aufgerufen. Die Funktion schreibt einen Eintrag in `../sync/dataindex.csv` und markiert vorherige Einträge derselben Datei als `superseded`. Bei fehlgeschlagenen Downloads wird stattdessen [`log_missing`](#lib-io-ops-log-missing) genutzt (schreibt sowohl in `data/missing.txt` als auch in dataindex.csv mit `status='error'`).
**Warum so:** Forschungsprojekte brauchen Nachvollziehbarkeit: Woher kommen die Daten? Von wann? Wurden sie aktualisiert? Das beantwortet die `../sync/dataindex.csv` automatisch. Die Helferfunktionen sind zentral in `lib.io_ops`, nicht mehr pro Notebook dupliziert (siehe O_04 Review-Protokoll R-07).

### Zelle 4 — API-Verbindung & Spotpreis-Download
**Was passiert:** Der ENTSO-E API-Schlüssel wird aus `../sync/config.json` gelesen. Dann wird geprüft, ob der API-Endpunkt erreichbar ist (HTTP-Status-Interpretation: 400 = erreichbar aber fehlende Parameter, 401 = ungültiger Key, 503 = Server überlastet). Für jeden Jahrgang wird [`fetch_entsoe_yearly`](#lib-data-fetchers-fetch-entsoe-yearly) aus `lib.data_fetchers` mit einer Lambda-Funktion aufgerufen, die den gewünschten ENTSO-E-Endpunkt kapselt (hier `client.query_day_ahead_prices('CH', ...)`). Die Lib-Funktion übernimmt die 503-Retry-Logik automatisch.
**Warum so:** Die ENTSO-E-API ist gelegentlich überlastet (503). Jahresweise Anfragen mit Retry-Logik ist robuster als ein einzelner Gesamtrequest. API-Keys werden nie im Code gespeichert — immer in der Config. Die Retry-Logik ist in `lib.data_fetchers` zentralisiert, damit sie auch von K_02 (Cross-Border-Flows) gleich verwendet wird.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `requests.get()` | `requests` | Sendet einen HTTP GET-Request. `params=` für URL-Parameter, `timeout=` verhindert ewiges Warten. |
| `pd.Timestamp()` | `pandas` | Erzeugt einen einzelnen Zeitpunkt mit Zeitzoneninfo. `tz='Europe/Zurich'` ist wichtig für korrekte Winterzeit/Sommerzeit-Behandlung. |
| `EntsoePandasClient()` | `entsoe` | Client für die ENTSO-E Transparency Platform API. Wandelt die komplexen XML-Antworten automatisch in pandas DataFrames/Series um. |
| `.query_day_ahead_prices()` | `entsoe` | Lädt Day-Ahead-Spotpreise für ein Land und Zeitraum (hier Schweiz `'CH'`). Gibt eine pandas Series zurück: Index = Timestamp, Werte = EUR/MWh. |
| `.query_load()` | `entsoe` | Lädt die tatsächliche Systemlast (Netzlast) für ein Land. Index = Timestamp, Werte = MW. |

### Zellen 5 & 7 — Verifikation
**Was passiert:** Nach jedem Download: Shape, Zeitraum, Nullwerte und Wertebereich ausgeben, erste Zeilen anzeigen.
**Warum so:** Datenfehler (falsche Einheit, fehlende Monate, API-Antwortformat geändert) fallen sofort auf.

### Zelle 6 — Netzlast-Download
**Was passiert:** Strukturell identisch zu Zelle 4 — gleiche Retry-Logik, andere API-Methode (`query_load`). Resultat: stündliche Systemlast des Schweizer Regelblocks in GW.

### Zelle 8 — Transfer-Output
**Was passiert:** Datenzeitraum (Startjahr, Endjahr, Anzahl tatsächlicher Jahre) wird via [`save_transfer`](#lib-io-ops-save-transfer) aus `lib.io_ops` in `../sync/transfer.json` unter dem Top-Level-Key `datenzeitraum` abgelegt. NB02 liest diesen Wert für korrekte Jahresdurchschnitt-Berechnungen.
**Warum so:** `../sync/transfer.json` ist der Kommunikationskanal zwischen Notebooks. Kein Notebook macht Annahmen über Datenzeiträume — es liest immer aus dieser Datei. `save_transfer` hat eingebaute Merge-Logik (bestehende Keys bleiben erhalten) — kritisch damit später K_06, K_09, K_99 ihre eigenen Keys schreiben können ohne `datenzeitraum` zu überschreiben.

### Zelle 9 — Abschlusskontrolle
**Was passiert:** Alle Output-Dateien werden auf Existenz und Mindestgrösse geprüft. ✅/❌ Ausgabe. Inhalt von `../sync/dataindex.csv` anzeigen.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `os.listdir()` | `os` | Gibt alle Dateien und Verzeichnisse in einem Ordner als Liste zurück. Hier für die Abschlusskontrolle: welche Dateien wurden erzeugt? |

---

## NB02 — Daten Bereinigung (`02_Daten_Bereinigung.ipynb`)
Lädt die Rohdaten aus `data/raw/` und bereinigt sie zu analysierbaren Zeitreihen in `data/processed/`. Kein Dispatch, keine Wirtschaftlichkeitsrechnung — nur Datenqualität.

### Zellen 1–3 — Setup, Konfiguration, Transfer
**Was passiert:** Libraries importieren, `../sync/config.json` als `CFG` laden. Reload-Schalter, Datenzeitraum und Verzeichnisse extrahieren. Dann `n_years` via [`load_transfer`](#lib-io-ops-load-transfer) aus `lib.io_ops` lesen (von NB01 mit `save_transfer` geschrieben). [`log_dataindex`](#lib-io-ops-log-dataindex) wird aus `lib.io_ops` importiert statt lokal definiert.
**Warum so:** SSOT-Prinzip. Alle Parameter aus Config, Datenzeitraum aus Transfer-Datei. Die früheren lokalen `log_dataindex`-Duplikate in allen NBs sind durch die zentrale lib-Funktion ersetzt (Review-Protokoll R-07).

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `json.loads()` | `json` | Parst JSON direkt aus einem String (nicht aus einer Datei). Hier zum Lesen einer Datei mit leerem Inhalt-Guard: `json.loads(f.read() or '{}')`. |
| `warnings.filterwarnings()` | `warnings` | Unterdrückt Python-Warnmeldungen. `'ignore'` schaltet alle aus — sinnvoll für Notebooks um die Ausgabe lesbar zu halten. |

### Zelle 4 — Rohdaten laden
**Was passiert:** `data/raw/ch_spot_prices_raw.csv` und `data/raw/ch_netzlast_raw.csv` einlesen. Timestamps auf UTC normieren. Shape und Wertebereich prüfen.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.read_csv()` | `pandas` | Lädt eine CSV-Datei von der Festplatte in einen DataFrame. `parse_dates` konvertiert Spalten direkt zu Datetime-Objekten. |
| `pd.to_datetime()` | `pandas` | Konvertiert Strings oder Unix-Timestamps in pandas-Timestamp-Objekte. `utc=True` normiert auf UTC-Zeitzone. |

### Zelle 5 — Bereinigung
**Was passiert:** Bereinigung in 5 Schritten:
1. Vollständigen Stundenraster erzwingen: `pd.date_range(...) + .reindex()` → fehlende Stunden werden als NaN eingefügt
2. Lücken bis 3h linear interpolieren
3. Längere Lücken mit `.ffill(limit=6).bfill(limit=6)` auffüllen
4. Extreme Ausreisser kappen: < -500 oder > 3000 EUR/MWh
5. Zeitfeatures ableiten: Stunde, Monat, Wochentag, Jahreszeit  
Bereinigte Daten werden als `data/processed/ch_spot_prices_clean.csv` gespeichert.  
**Warum so:** Vollständiger Stundenraster ist Voraussetzung für tagesbasierte Dispatch-Simulation. Ausreisser würden die p25/p75-Schwellenwerte verzerren.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.date_range()` | `pandas` | Erzeugt einen lückenlosen Zeitreihen-Index. `freq='1h'` = stündlich, `tz='UTC'`, `name='timestamp'` setzt den Spaltennamen nach `reset_index()` automatisch. |
| `.set_index()` | `pandas` | Setzt eine Spalte als DataFrame-Index. Wird mit `.reindex()` kombiniert um fehlende Zeitstempel einzufügen. |
| `.reindex()` | `pandas` | Richtet den DataFrame auf einen neuen Index aus. Fehlende Werte werden als `NaN` eingefügt. |
| `.reset_index()` | `pandas` | Verwandelt den Index zurück in eine normale Spalte. Typisch nach `set_index()` + `reindex()`. |
| `.interpolate()` | `pandas` | Füllt NaN-Werte durch lineare Interpolation. `limit=3` begrenzt auf maximal 3 aufeinanderfolgende NaN. |
| `.ffill()` | `pandas` | Forward Fill: füllt NaN mit dem letzten bekannten Wert. `limit=6` begrenzt die Anzahl auffüllbarer NaN. |
| `.bfill()` | `pandas` | Backward Fill: füllt NaN mit dem nächsten bekannten Wert. Wird nach `ffill()` für verbleibende NaN am Anfang verwendet. |
| `.clip()` | `pandas / numpy` | Begrenzt Werte auf ein Intervall [min, max]. Verhindert Ausreisser-Effekte auf Berechnungen. |
| `.dt.hour` | `pandas (.dt)` | Zugriff auf Datetime-Komponenten. `.dt.hour` = Stunde (0–23), `.dt.month` = Monat (1–12), `.dt.dayofweek` = Wochentag (0=Montag). |

### Zelle 6 — Verifikation
**Was passiert:** Shape, Nullwerte, Wertebereich und erste Zeilen der bereinigten Preise ausgeben.

---

## NB03 — Daten Analyse (`03_Daten_Analyse.ipynb`)
Das Herzstück des Projekts. Liest bereinigte Daten aus `data/processed/`, simuliert den Batterie-Dispatch, berechnet wirtschaftliche Kennzahlen und schreibt Ergebnisse in `../sync/transfer.json`.

### Zellen 1–3 — Setup, Konfiguration, Transfer
**Was passiert:** Identische Initialisierungssequenz wie NB02 — Libraries, `../sync/config.json`, `n_years` via [`load_transfer`](#lib-io-ops-load-transfer), [`log_dataindex`](#lib-io-ops-log-dataindex) aus `lib.io_ops`. Dann alle Simulations- und Wirtschaftlichkeitsparameter als Named Aliases laden: `EFFICIENCY`, `CHARGE_Q`, `DISCHARGE_Q`, `SOC_MIN_PCT`, `SOC_MAX_PCT`, `CAPEX_EUR_KWH`, `OPEX_RATE`, `LIFETIME_J`.
**Warum Named Aliases?** SSOT-Prinzip: Parameter kommen aus `../sync/config.json`, aber Funktions-Defaults dürfen diese nie hardcoden — Named Aliases machen den Fluss sichtbar und verhindern versehentliche Duplikation.

### Zelle 4 — Bereinigte Daten laden
**Was passiert:** `data/processed/ch_spot_prices_clean.csv` und `data/processed/ch_netzlast_clean.csv` einlesen. Timestamps auf UTC normieren.

### Zelle 5 — Tagesprofil & Spread-Analyse
**Was passiert:** Für jede Stunde des Tages (0–23) werden Durchschnitt und Standardabweichung des Preises berechnet. Die günstigsten und teuersten Stunden werden identifiziert. Arbitrage-Spread und saisonale Durchschnitte werden ausgegeben.
**Warum so:** Beantwortet die Kernfrage: Wie gross ist das Arbitrage-Potential im Tages-Rhythmus?

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.groupby()` | `pandas` | Gruppiert einen DataFrame nach einer oder mehreren Spalten. Ermöglicht Aggregation pro Gruppe. |
| `.agg()` | `pandas` | Wendet mehrere Aggregationsfunktionen auf eine Gruppe an. `agg(mean='mean', std='std')` berechnet Mittelwert und Standardabweichung in einem Durchgang. |
| `.nsmallest()` | `pandas` | Gibt die n kleinsten Werte einer Serie zurück. Hier: die günstigsten Stunden. |
| `.nlargest()` | `pandas` | Gibt die n grössten Werte zurück. Hier: die teuersten Stunden. |

### Zelle 6 — Dispatch-Aufruf (Kernfunktion)
**Was passiert:** Der algorithmische Kern des Projekts ist [`simulate_battery_dispatch`](#lib-simulation-simulate-battery-dispatch) aus `lib.simulation`. Die Funktion implementiert das Schwellenwertmodell:
- **Schritt 1:** Für jeden Tag werden p(charge_q) und p(discharge_q) *einmalig vorab* als NumPy-Arrays berechnet (O(n), nicht O(n²))
- **Schritt 2:** Preise und Schwellenwerte werden als NumPy-Arrays extrahiert (kein `iterrows()`)
- **Schritt 3:** Stunden-Simulation: Preis ≤ p(charge_q) UND SoC < soc_max → laden; Preis ≥ p(discharge_q) UND SoC > soc_min → einspeisen; sonst → idle

**Break-even-Bedingung** (im Docstring der lib-Funktion dokumentiert):
`p(discharge_q) × η > p(charge_q)` — nur wenn diese Bedingung erfüllt ist, deckt der Erlös die Rundlaufverluste. Äquivalent: `Spread > Spread_min = p(charge_q) × (1/η − 1)`. Tage ohne qualifizierten Spread bleiben vollständig **idle**. Siehe Glossar: `O_02_Glossar.ipynb#g-dispatch-breakeven`.

**Warum NumPy?** Für 26.000 Stunden (3 Jahre) wäre `iterrows()` ca. 50× langsamer. NumPy läuft in optimiertem C-Code.
**Warum sequenziell?** Der SoC einer Stunde hängt vom SoC der Vorherigen ab — das kann nicht vektorisiert werden.

**Warum in lib?** Die gleiche Logik wird in K_06 (Dispatch-Vergleich reaktiv vs. day-ahead-optimal) wieder benötigt. Vor Phase 6.4 war die Funktion als Byte-gleiches Duplikat in beiden NBs — Review-Protokoll R-09. Die Extraktion wurde mit bit-identischer Verifikation durchgeführt (Jahres-Erlöse identisch auf 0.01 EUR).

### Zellen 7–8 — Simulation aller Segmente
**Was passiert:** [`simulate_battery_dispatch`](#lib-simulation-simulate-battery-dispatch) wird für alle 4 Segmente ausgeführt (Privat 10 kWh / Gewerbe 100 kWh / Industrie 1 MWh / Utility 10 MWh). Parameter kommen als Named Aliases aus `CFG['pflicht']['simulation']`, nicht hardcoded in der Lib-Signatur. Jahreserlös = Gesamterlös ÷ `n_years`. Ergebnisse werden tabellarisch ausgegeben.
**Warum Durchschnitt statt nur ein Jahr?** Jahres-Preise schwanken stark. Durchschnitt über mehrere Jahre ist realistischer.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.dt.year` | `pandas (.dt)` | Extrahiert das Jahr aus einer Datetime-Spalte. `.dt.year.nunique()` = Anzahl verschiedener Jahre — Fallback für `n_years`. |

### Zellen 9–10 — CAPEX / ROI / Amortisation
**Was passiert:** Für jedes Segment: CAPEX (kWh × EUR/kWh aus Config), OPEX (OPEX_RATE × CAPEX/Jahr), Netto-Erlös (Jahreserlös − OPEX), Amortisationszeit (CAPEX ÷ Netto), ROI (Netto/CAPEX × 100). Ergebnisse als CSV nach `data/intermediate/`. Verifikationsausgabe mit Shape und Wertebereich.

### Zelle 11 — Gleichzeitigkeits-Szenarien
**Was passiert:** 4 Szenarien (Status Quo, Moderat 2027, Ambitioniert 2030, Transformativ 2035). Gleichzeitigkeitsrate aus Config (z.B. 40%) skaliert die theoretische Leistung auf die reale Netzentlastung in MW. CSV nach `data/intermediate/`.
**Warum Gleichzeitigkeit?** 50.000 Heimspeicher à 5 kW = 250 MW theoretisch. Bei 40% = 100 MW real — nicht alle speisen zur gleichen Sekunde ein.

### Zellen 12–13 — Spread/Volatilität Zeitreihe
**Was passiert:** Für jeden Tag: Intra-Tag-Spread (p75 − p25). Optimiert: einmaliges `.quantile([0.25, 0.75]).unstack()` statt zweier Lambda-Aufrufe. Tageswerte werden pro Monat zum Median aggregiert. Zusätzlich: Volatilität, Durchschnittspreis, Negativpreis-Stunden. CSV nach `data/intermediate/`. Verifikation auf Shape und Wertebereich.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.quantile()` | `pandas` | Berechnet Quantile einer Serie. `.quantile([0.25, 0.75])` gibt beide auf einmal zurück. Nachgelagertes `.unstack()` verwandelt das MultiIndex-Ergebnis in Spalten. |
| `.unstack()` | `pandas` | Klappt den innersten Index einer MultiIndex-Serie in Spalten um. Typisch nach `.groupby().quantile([...])`. |
| `.merge()` | `pandas` | Verknüpft zwei DataFrames per Schlüsselspalte (wie SQL JOIN). |
| `.dt.to_period()` | `pandas (.dt)` | Konvertiert Timestamps in Zeiträume (z.B. `'M'` = Monat). `.dt.to_timestamp()` wandelt zurück. Für monatliche Aggregation. |
| `.median()` | `pandas` | Berechnet den Median — robuster gegen Ausreisser als der Mittelwert. |

### Zelle 14 — Transfer-Output
**Was passiert:** Alle berechneten Kennzahlen werden in `../sync/transfer.json` geschrieben: Spread-Statistiken, `n_years`, ROI/Erlös/CAPEX pro Segment. Optimiert: `zip()`-basierte Dict-Comprehension statt `iterrows()`.
**Warum?** NB04 (Visualisierungen), K_00 (Business Strategy) und alle nachgelagerten Kür-Notebooks lesen diese Werte statt selbst zu berechnen.

### Zelle 15 — Abschlusskontrolle
**Was passiert:** Alle Pflicht-Ausgabedateien auf Existenz und Mindestgrösse prüfen. ✅/❌ Ausgabe.

---

## NB04 — Visualisierungen (`04_Visualisierungen.ipynb`)
Erzeugt alle Pflicht-Charts (5 Hauptcharts + Einzelplots + Langzeit-Chart). Liest aus `data/processed/` und `data/intermediate/`. Keine eigenen Berechnungen — stellt grafisch dar was NB03 berechnet hat.

### Zellen 1–3 — Setup & Daten laden
**Was passiert:** Libraries laden, `../sync/config.json` lesen, Farb- und Stil-Konstanten aus Config entpacken, `matplotlib.rcParams` global setzen. Dann CSVs aus `data/processed/` und `data/intermediate/` laden. Verifikation aller Eingabe-DataFrames auf Shape und Spalten.
**Warum rcParams global?** Ohne diese Einstellung müsste jeder Chart dieselben Formatierungszeilen wiederholen.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `matplotlib.rcParams.update()` | `matplotlib` | Setzt globale Standardwerte für alle nachfolgenden Plots: Hintergrundfarbe, Tick-Farbe, Schriftgrössen. Gilt für alle Charts des Notebooks. |
| `.map()` | `pandas` | Ersetzt Werte einer Spalte anhand eines Dictionaries. Vektorisiert — kein Python-Loop. |

### Zellen 4–6 — Chart 1: Wirtschaftlichkeit (4 Panels + Einzelplots + Langzeit)
**Was passiert:** Ein 2×2-Panel-Chart. Cashflow-Schleifen nutzen `zip()` statt `itertuples()`, Cashflow als NumPy-Vektoroperation: `-capex + net_annual * years`.
Panel 1: Kumulierte Cashflow-Kurven (symlog-Skala). Panel 2: ROI-Balken mit Ziel-ROI-Linie. Panel 3: Erlös/kWh. Panel 4: CAPEX vs. kumulierter Erlös. Zusätzlich: Einzelplots für Bericht-Einbettung + Langzeit-Chart (20 Jahre).

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.arange()` | `numpy` | Erstellt ein Array mit gleichmässigem Abstand. `np.arange(0, 13)` = [0,1,...,12]. Hier als Jahres-Achse für Cashflow-Kurven. |
| `ax.set_yscale()` | `matplotlib.axes` | Setzt die Skalierung der Y-Achse. `'symlog'` = symmetrisch-logarithmisch: linear nahe der Null, logarithmisch für grosse Beträge. |
| `mticker.FuncFormatter()` | `matplotlib.ticker` | Definiert eine eigene Tick-Beschriftungsformel. Hier: Werte ≥ 1000 als `'123k'` anzeigen. |
| `ax.annotate()` | `matplotlib.axes` | Fügt eine Beschriftung mit Pfeil an einen Datenpunkt. `xy=` = Pfeilspitze, `xytext=` = Textposition. |
| `ax.axhline()` | `matplotlib.axes` | Zeichnet eine horizontale Linie über die gesamte Achsenbreite. Hier für Break-Even-Linie (y=0) und Ziel-ROI-Referenz. |
| `ax.axvline()` | `matplotlib.axes` | Zeichnet eine vertikale Linie über die gesamte Achsenhöhe. Hier für Marker bei Jahr 12. |

### Zellen 7–8 — Chart 2: Heatmap Stunde × Monat
**Was passiert:** Eine 24×12-Matrix (Stunden × Monate) als Heatmap. Optimiert: ein kombinierter `pivot_table(aggfunc=['mean','std'])` statt zwei separater Aufrufe. `origin='lower'` setzt 00:00 unten.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.pivot_table()` | `pandas` | Erstellt eine Kreuztabelle: Zeilen × Spalten mit aggregierten Werten. Hier: Mittelwert des Preises pro Stunde × Monat. |
| `ax.imshow()` | `matplotlib.axes` | Stellt eine Matrix als farbcodiertes Bild (Heatmap) dar. `cmap=` = Farbpalette, `origin='lower'` = Zeile 0 unten. |
| `plt.colorbar()` | `matplotlib.pyplot` | Fügt eine Farblegende neben dem Plot hinzu. |
| `ax.axvspan()` | `matplotlib.axes` | Zeichnet eine farbige vertikale Zone. Hier für Lade- und Einspeisezeitfenster-Markierungen. |

### Zellen 9–10 — Chart 3: Tagesprofil mit Doppelachse
**Was passiert:** Netzlast (GW) und Preis (EUR/MWh) als Doppelachsen-Chart. Die günstigsten Stunden werden blau, die teuersten rot hinterlegt.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `ax.twinx()` | `matplotlib.axes` | Erstellt eine zweite Y-Achse rechts, die dieselbe X-Achse teilt. Ermöglicht zwei verschiedene Skalen im selben Chart. |
| `ax.fill_between()` | `matplotlib.axes` | Füllt die Fläche zwischen zwei Kurven mit Farbe. Alpha-Wert steuert die Transparenz. |
| `mpatches.Patch()` | `matplotlib.patches` | Erzeugt ein farbiges Rechteck für die Legende. Für Legenden-Einträge ohne echtes Plot-Objekt. |
| `ax.get_legend_handles_labels()` | `matplotlib.axes` | Gibt die aktuellen Legenden-Einträge zurück. Zum Zusammenführen von Legenden mehrerer Achsen. |

### Zellen 11–14 — Charts 4 & 5: Szenarien & Saisonales Profil
**Was passiert:** Chart 4: Netzentlastungsszenarien als Balken mit dynamischer Einfärbung via `Normalize` und `cm.get_cmap()`. Chart 5a: Saisonales Tagesprofil für alle 4 Jahreszeiten mit einheitlichen Y-Achsen. Chart 5b: Monatlicher Spread und Dispatch-Stunden. Alle Charts + Einzelplots als PNG gespeichert.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `Normalize()` | `matplotlib.colors` | Skaliert Werte auf [0,1] für Colormaps. `vmin`/`vmax` definieren den Eingabebereich. |
| `cm.get_cmap()` | `matplotlib.cm` | Lädt eine benannte Farbpalette als Objekt. `cmap(value)` gibt die RGBA-Farbe zurück. |
| `cm.ScalarMappable()` | `matplotlib.cm` | Verbindet Colormap mit Normalisierung — für Colorbars ohne direkte `imshow()`/`scatter()`. |

---

## NB00 — Business Case (`00_Business_Case.ipynb`)
Kein eigener Chart-Code. Lädt und zeigt die von NB04 erzeugten PNGs. Reiner Berichtsmodus — das Hauptdokument für den Leistungsnachweis.

### Zellen 1–3 — Setup & Konfiguration
**Was passiert:** `../sync/config.json` laden, Charts-Verzeichnis und ⚙-Prüfwerte definieren. Für die Chart-Anzeige wird [`show_chart`](#lib-plotting-show-chart) aus `lib.plotting` importiert — die kanonische Anzeige-Funktion projektweit (löst auto nach Endung: `.gif` via HTML-Tag, sonst via `IPython.display.Image`).

### Abschnitte 1–5 — Bericht
**Was passiert:** Strukturierter Bericht in 5 Abschnitten:
1. **Einleitung** — Forschungsfrage, Projektkontext
2. **Daten** — Datenquellen-Übersicht
3. **Methodik** — Dispatch-Modell (Laden/Einspeisen/Idle-Logik mit Break-even-Bedingung `p75 × η > p25`), Segmente, Wirtschaftlichkeitsrechnung
4. **Ergebnisse** — Chart-Anzeige: Preis-Heatmap, Tagesprofil, Amortisation, ROI, Netzentlastung, Saisonale Rentabilität
5. **Fazit und Empfehlungen** — kein Segment erreicht Ziel-ROI durch reine Arbitrage; Erlösstacking als Lösungsweg

---

# Kür (`kuer/`)

## K_00 — Business Strategy (`K_00_Business_Strategy.ipynb`)
Grösstes Kür-Notebook (63 Zellen). Fasst alle Ergebnisse aus Pflicht und Kür zu einer Strategie-Empfehlung zusammen. Reines Präsentations-/Synthesedokument — lädt Charts aus allen anderen Notebooks und baut daraus eine kohärente Marktargumention auf.

**lib-Imports:** [`show_source`](#lib-plotting-show-source), [`show_chart`](#lib-plotting-show-chart), [`show_animation`](#lib-widgets-show-animation), [`load_transfer`](#lib-io-ops-load-transfer), [`save_transfer`](#lib-io-ops-save-transfer).

### Setup
**Was passiert:** `../sync/config.json` laden. `../sync/transfer.json` via [`load_transfer`](#lib-io-ops-load-transfer) laden — alle Werte die NB01–K_99 dort geschrieben haben, sind verfügbar. `check_aktiv()`-Funktion (NB-lokal) prüft ob abhängige Kür-Notebooks aktiv sind bevor deren Charts geladen werden.

### Strategie-Kapitel (Sektion 1–10)
**Was passiert:** Jede Sektion lädt die relevanten Chart-PNGs und baut daraus eine Argumentation:
- **1** — Marktüberblick: Preis-Heatmap, Saisonale Spread-Animation (K_04)
- **2–3** — Arbitrage-ROI, Amortisation, Segmentempfehlungen
- **4** — Dispatch-Optimierung: Tagesprofil, saisonale Muster, DA-optimal vs. reaktiv (K_06)
- **5** — Räumliche Analyse: BVI-Karten, Standortoptimierung (K_01)
- **6** — Skalierung & Netzentlastung
- **7** — FCR-Mechanismus (Verfügbarkeitsprämie), Revenue Stacking (K_05)
- **8** — CAPEX-Lernkurve, Sensitivitätsheatmap, VPP-Multiplikator (K_03)
- **9** — Import/Export-Validierung (K_02)
- **10** — Kombinationsmatrix: Vier Wege zur Rentabilität

---

## K_01 — Räumliche Analyse (`K_01_Raeumliche_Analyse.ipynb`)
Komplexestes Kür-Notebook (88 Zellen). GeoPandas, echte Schweizer Geodaten, Kartenerzeugung, Battery Value Index (BVI).

**lib-Imports:** [`log_dataindex`](#lib-io-ops-log-dataindex), [`show_source`](#lib-plotting-show-source), [`show_chart`](#lib-plotting-show-chart), [`should_skip`](#lib-plotting-should-skip), [`make_gif_chart`](#lib-plotting-make-gif-chart), [`show_animation`](#lib-widgets-show-animation), [`load_kantone`](#lib-grid-topo-load-kantone) (inkl. `KANT_NUM_TO_ABK`/`KANT_ABK_SET`), [`find_col`](#lib-columns-find-col).

### Zelle 1 — Setup & Bibliotheken
**Was passiert:** Fehlende Libraries bei Bedarf installieren: `geopandas`, `scipy`. Config laden, vollständiger Farb- und Stil-Ladeblock aus `../sync/config.json`.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `gpd.read_file()` | `geopandas` | Lädt Geodaten aus GeoPackage (`.gpkg`), Shapefile (`.shp`) oder GeoJSON. `layer=` wählt einen Layer. |
| `gpd.list_layers()` | `geopandas` | Listet alle Layer in einer GeoPackage-Datei auf. |
| `gpd.GeoDataFrame()` | `geopandas` | Erstellt einen GeoDataFrame (pandas DataFrame mit Geometry-Spalte). |

### Zelle 2 — BFE-Anlagen laden
**Was passiert:** BFE-GeoPackage (alle Schweizer Elektrizitätsproduktionsanlagen) von swisstopo-API herunterladen (falls nicht vorhanden). Stream-Download in 512KB-Chunks. Koordinaten von CH1903+ auf WGS84 transformieren.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.iter_content()` | `requests` | Lädt eine HTTP-Antwort in Chunks. Notwendig für grosse Dateien. `chunk_size=1024*512` = 512KB pro Chunk. |
| `.to_crs()` | `geopandas` | Transformiert ein GeoDataFrame in ein anderes Koordinatensystem. `epsg=4326` = WGS84. |

### Zelle 4 — Energieträger-Mapping (vektorisiert)
**Was passiert:** Jede Anlage bekommt einen Energieträger-Label. Vektorisiert: erst `.map(SUBCAT_MAP)`, dann Fallback `.map(MAINCAT_MAP)`, Rest → `'Andere'`. Kein `apply(axis=1)`.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.to_numeric()` | `pandas` | Konvertiert zu numerischen Werten. `errors='coerce'` verwandelt nicht-konvertierbare Werte in `NaN`. |
| `.str.strip()` | `pandas (.str)` | Entfernt führende/nachfolgende Leerzeichen aus Strings. |
| `.fillna()` | `pandas` | Ersetzt NaN-Werte durch Standardwert oder andere Serie. |

### Zellen 5–6 — BFS Bevölkerungsdaten
**Was passiert:** BFS STATPOP-Daten via PXWeb-API (POST-Request mit JSON-Query). Non-breaking Spaces und Tausendertrennzeichen bereinigen.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `requests.post()` | `requests` | HTTP POST-Request mit JSON-Body. Für die PXWeb-API. |
| `requests.head()` | `requests` | Sendet nur den HTTP-Header. Schneller Verbindungstest. |
| `.raise_for_status()` | `requests` | Wirft eine Exception bei 4xx/5xx-Statuscodes. Verhindert stilles Scheitern. |
| `io.StringIO()` | `io` | In-Memory-Textpuffer. `pd.read_csv(io.StringIO(text))` liest CSV direkt aus String. |
| `pd.isna()` | `pandas` | Prüft elementweise ob Werte NaN sind. |

### Zelle 8 — Zonenzuweisung (vektorisiert)
**Was passiert:** Jede Anlage wird einer von 5 Netzregionen (Nord/Mitte/West/Süd/Ost) zugewiesen — primär per Kanton-Dict, Fallback via `np.select()` auf Koordinaten.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.select()` | `numpy` | Wählt aus mehreren Arrays basierend auf Bedingungsliste. Vektorisierte Alternative zu if/elif-Ketten. |

### Zellen 9–11 — Kapazitätsfaktoren, Zonenbilanzen, BVI
**Was passiert:** Installierte Kapazität × Kapazitätsfaktor = mittlere Einspeisung pro Zone. Zonenimbalance = Produktion − Verbrauch. BVI-Index = Imbalance × Engpass-Multiplikator, normiert auf 10.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.abs()` | `numpy` | Betrag eines Arrays. Für BVI: Vorzeichen der Imbalance ist egal, nur die Grösse zählt. |

### Zellen 13–21 — Kartenerzeugung & Heatmaps
**Was passiert:** Schweizer Kantonsgrenzen von swisstopo laden. Karten: Bevölkerungsdichte (Choropleth), Kraftwerksstandorte (Scatter), Kombinierte Karte mit Engpasskorridoren. Für 300k+ Solar-Anlagen: Stichprobe + `rasterized=True`. Tages-Lastprofil-Heatmap pro Zone.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.column_stack()` | `numpy` | Stapelt Arrays als Spalten zu einer 2D-Matrix. Effizienter als `list(zip(x,y))`. |
| `np.percentile()` | `numpy` | Berechnet ein Quantil. Hier für robuste Grössenskalierung von Kraftwerks-Punkten. |
| `np.clip()` | `numpy` | Begrenzt Array-Werte auf [min, max]. |
| `.geometry.x` | `geopandas` | Extrahiert X-Koordinate aus der Geometry-Spalte als Series. |
| `.geometry.centroid` | `geopandas` | Berechnet den geometrischen Schwerpunkt. Für Kanton-Beschriftungen. |
| `.sample()` | `pandas` | Zieht eine zufällige Stichprobe. `random_state=42` für Reproduzierbarkeit. |
| `ax.set_axis_off()` | `matplotlib.axes` | Blendet alle Achsenelemente aus. Standard für Karten. |
| `rasterized=True` | `matplotlib` | Wandelt viele Punkte in ein Pixel-Bild um. Entscheidend für Performance bei 100k+ Punkten. |
| `mcolors.TwoSlopeNorm()` | `matplotlib.colors` | Normalisierung mit zwei Slopes: für divergente Colormaps (Rot=Defizit, Blau=Überschuss). |
| `cKDTree()` | `scipy.spatial` | k-d-Baum für schnelle räumliche Nachbarschaftssuche. O(log n) statt O(n). |

### Zellen 20–21 — Lastprofile
**Was passiert:** Synthetische stündliche Last- und Produktionsprofile je Zone mit Gauss-Kurven modelliert.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.exp()` | `numpy` | Berechnet e^x. Für Gauss-Kurven: `np.exp(-((h-peak)**2)/width)`. |
| `np.sin()` | `numpy` | Sinusfunktion. Hier für Solar-Tagesprofil. |
| `np.ones()` | `numpy` | Array mit lauter Einsen. Für Kernkraft-Baseload. |
| `np.full()` | `numpy` | Array mit konstantem Wert. |

---

## K_02 — Cross-Border-Analyse (`K_02_Cross_Border.ipynb`)
Analysiert Stromflüsse zwischen der Schweiz und DE/AT/IT/FR und deren Einfluss auf Spotpreise.

### Zellen 1–2 — Setup & Grenzfluss-Download
**Was passiert:** Standard-Setup. ENTSO-E API für Grenzflüsse: `query_crossborder_flows()` für alle 4 Grenzpaare, jahresweise mit Retry.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.query_crossborder_flows()` | `entsoe` | Lädt physikalische Grenzflüsse (MW) zwischen zwei Regelzonen. Positiv = Export, negativ = Import. |

### Zellen 3–6 — Analyse & Charts
**Was passiert:** Netto-Import/-Export pro Saison. Korrelation zwischen Grenzflüssen und Spotpreis. Streudiagramme: Mehr Import aus DE → tiefere CH-Preise?

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.corr()` | `pandas` | Berechnet Pearson-Korrelationskoeffizienten zwischen allen Spaltenpaaren. |
| `.dropna()` | `pandas` | Entfernt Zeilen mit NaN-Werten. Wichtig vor Korrelationsberechnungen. |

---

## K_03 — Marktdynamik (`K_03_Marktdynamik.ipynb`)
Untersucht Spread-Trend über Zeit und CAPEX-Lernkurven für die Wirtschaftlichkeitsprojektion.

### Zellen 1–3 — Spread-Trend
**Was passiert:** Historische Spread-Zeitreihe aus `data/intermediate/` laden. Lineare Regression via `np.polyfit()`, Trendlinie via `np.polyval()`. Berechnung: ab welchem Spread-Niveau ist Privatarbitrage Break-Even?

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.polyfit()` | `numpy` | Berechnet Koeffizienten eines Polynoms (Kleinste-Quadrate). Grad 1: [Steigung, Achsenabschnitt]. |
| `np.polyval()` | `numpy` | Wertet ein Polynom an gegebenen X-Werten aus. Für die Regressionsgerade. |
| `LinearSegmentedColormap` | `matplotlib.colors` | Definiert eigene Farbpalette durch lineare Interpolation zwischen Stützpunkten. |

### Zellen 4–6 — CAPEX-Lernkurve & Sensitivitätsheatmap
**Was passiert:** CAPEX-Preisentwicklung modellieren (jährliche Kostensenkung via Lernrate aus Config). Berechnung in welchem Jahr die Privatarbitrage Break-Even erreicht. CAPEX × Spread Sensitivitätsheatmap.

---

## K_04 — Saisonale Animationen (`K_04_Animationen.ipynb`)
Erstellt animierte GIFs der Preis- und Lastzeitreihen über 52 Kalenderwochen.

### Zellen 1–3 — Setup & Wochenaggregation
**Was passiert:** Standard-Setup. Preise und Last pro Kalenderwoche × Stunde aggregieren: Mittelwert, p25, p75. `dt.isocalendar().week` für ISO-Kalenderwochen (1–52).

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.dt.isocalendar()` | `pandas (.dt)` | Gibt ISO-Kalenderwoche, Wochentag und Jahr zurück. ISO-KW beginnt montags. |

### Zellen 4–6 — Animationen A, B & C
**Was passiert:** Animation A: 4 GIFs (Tageszeiten 00/07/12/19 Uhr), 52 Frames. Pre-Indexierung VOR der Animations-Schleife für O(1)-Lookup statt Boolean-Filter. Animation B: 4-Panel-Chart alle Tageszeiten gleichzeitig. Animation C: Spread-Animation mit wöchentlichem Spread, Negativpreis-Anteil und Dispatch-Stunden als aufbauende Kurven.

Alle drei Animationen werden mit [`make_gif_chart`](#lib-plotting-make-gif-chart) aus `lib.plotting` erzeugt. Die Funktion nimmt die Figure, eine Update-Callback-Funktion und die Frame-Sequenz entgegen und baut PIL-basiert das animierte GIF zusammen. Wenn `cfg=CFG` mitgegeben wird, konsultiert sie [`should_skip`](#lib-plotting-should-skip) und kehrt ohne Rendering zurück falls das GIF schon existiert (Standard über `config.json → animation.modus: 'skip_if_exists'`). Bei `animation.einzelbilder: true` in der Config werden zusätzlich die Einzelframes als PNG gespeichert — diese nutzt dann [`show_animation`](#lib-widgets-show-animation) im `mode='slider'` für interaktive Anzeige in K_00.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.join()` | `pandas` | Verknüpft zwei DataFrames per Index. Schneller als `merge()` wenn Join-Key der Index ist. |
| `ax.errorbar()` | `matplotlib.axes` | Datenpunkte mit Fehlerbalken. `yerr=[[unten],[oben]]` für asymmetrische Balken. Für Preiskerzen. |
| `.set_data()` | `matplotlib.lines.Line2D` | Aktualisiert X- und Y-Daten einer bestehenden Linie. Effizient in Animationen. Wird in der Update-Callback-Funktion verwendet die `make_gif_chart` pro Frame aufruft. |
| `.set_height()` | `matplotlib.patches.Rectangle` | Ändert die Höhe eines Balken-Patches zur Laufzeit. Für frame-by-frame Balkendiagramme. |

**Hinweis:** K_04 nutzte früher direkt `matplotlib.animation.FuncAnimation` + `PillowWriter`. Seit Phase 6.1 läuft die GIF-Erzeugung über `lib.plotting.make_gif_chart` (PIL-basiert), die identisch in K_01 verwendet wird. Die interaktive Anzeige (Slider/Play) ist nicht mehr "potenzielle Erweiterung" sondern produktiv verfügbar via `show_animation(..., mode='slider')`, wird in K_00 und K_01d genutzt.

---

## K_05 — Revenue Stacking (`K_05_Revenue_Stacking.ipynb`)
Berechnet Mehrertrag durch Systemdienstleistungen (FCR/aFRR) zusätzlich zur Arbitrage.

### Zellen 1–3 — Setup & Erlösstacking-Modell
**Was passiert:** Literaturbasierte Schätzwerte für FCR- und aFRR-Erlöse (EUR/kWh/Jahr) definieren. Für jedes Segment und jeden Erlöstyp: Mehrertrag bei 20% reservierter FCR-Kapazität. Wichtige Erkenntnis: FCR zahlt für **Verfügbarkeit**, nicht für gelieferte Energie — die Batterie verdient die Prämie auch ohne Zyklus.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `ax.barh()` | `matplotlib.axes` | Horizontales Balkendiagramm. Praktisch wenn Kategorien-Labels lang sind. |

### Zellen 4–5 — Charts
**Was passiert:** Gestapelter Balken: Arbitrage-Erlös als Basis, FCR und aFRR als Aufstockung. Break-Even-Analyse: ab wann macht FCR die Investition rentabel?

---

## K_06 — Dispatch-Optimierung (`K_06_Dispatch_Optimierung.ipynb`)
Vergleicht reaktiven (NB03-Schwellenwert) mit day-ahead-optimalem Dispatch.

### Zellen 1–2 — DA-optimaler Dispatcher
**Was passiert:** Zwei Dispatch-Varianten werden verglichen:
- **Reaktiv:** [`simulate_battery_dispatch`](#lib-simulation-simulate-battery-dispatch) aus `lib.simulation` — identisch zu NB03, p25/p75 des laufenden Tages
- **DA-optimal:** NB-lokale Funktion `simulate_battery_da_optimal()` — nutzt bekannte DA-Preise des gesamten nächsten Tages (ENTSO-E publiziert DA-Preise täglich um 12:00)

Die Break-even-Bedingung `p(discharge_q) × η > p(charge_q)` ist im Docstring der lib-Funktion dokumentiert — Tage ohne qualifizierten Spread bleiben idle.

Effizienzgewinn DA vs. Reaktiv ist meist gering (~5–15%) weil beide denselben p25/p75-Schwellenwert verwenden. DA-optimal ist trotzdem NB-lokal, weil die Parametrierung (Blick auf den nächsten Tag statt auf den laufenden) strukturell vom Quantil-Modell in `lib.simulation` abweicht.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.where()` | `numpy` | Gibt Indices zurück wo eine Bedingung erfüllt ist. `np.where(p <= q25)` = alle Lade-Positionen. Vektorisiert statt Python-Loop. |

### Zellen 3–7 — Vergleich & Sensitivitätsanalyse
**Was passiert:** Reaktiv vs. DA-optimal für alle Segmente: Erlös, Zyklen, Effizienz. Sensitivitätsanalyse C-Rate: wie verändert sich der Jahreserlös wenn die Leistung (kW) relativ zur Kapazität (kWh) variiert?

### Zelle 8 — Transfer-Output
**Was passiert:** DA-optimal vs. reaktiv Kennzahlen (`roi_reaktiv_pct`, `roi_da_optimal_pct`, `delta_pct`) je Segment werden via [`save_transfer`](#lib-io-ops-save-transfer) nach `../sync/transfer.json` unter `dispatch_optimierung` geschrieben. Die Merge-Logik in `save_transfer` stellt sicher, dass bereits vorhandene Keys (`datenzeitraum` aus NB01, `simulation` aus NB03) erhalten bleiben.

---

## K_07 — Technologievergleich (`K_07_Technologievergleich.ipynb`)
Vergleicht Li-Ion mit Redox-Flow, Vanadium-Flow, CAES, Schwungrad — Kosten, Lebensdauer, Wirkungsgrad.

### Zellen 1–2 — Technologiedaten laden
**Was passiert:** Daten aus lokaler CSV oder NREL Annual Technology Baseline API (öffentliche AWS S3 CSV). HTTP GET → `pd.read_csv(io.StringIO(resp.text))`.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.log()` | `numpy` | Natürlicher Logarithmus. Für Lernkurven-Regression: Linearisierung durch Logarithmieren. |
| `np.linspace()` | `numpy` | n gleichmässig verteilte Werte in [start, stop]. Garantiert genau n Punkte. Für glatte Kurven. |
| `curve_fit()` | `scipy.optimize` | Passt eine Funktion `f(x, *params)` an Datenpunkte an (nichtlineare Kleinste-Quadrate). |

### Zellen 3–6 — Vergleich & Radar-Chart
**Was passiert:** Wirtschaftlichkeit für alle Technologien. Radar-Chart (Spinnennetz) mit 5 Dimensionen: Kosten, Lebensdauer, Wirkungsgrad, Energiedichte, Skalierbarkeit. Lernkurven mit Trendlinie.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.array()` | `numpy` | Erstellt ein NumPy-Array aus einer Python-Liste. Für Radar-Chart-Winkel und Technologieparameter. |

---

## K_08 — Alternative Speicher (`K_08_Alternative_Speicher.ipynb`)
Analyse von Pumpspeichern und saisonalen Wärmespeichern als Li-Ion-Alternativen für die Schweiz.

### Zellen 1–3 — Daten, Berechnung, Chart
**Was passiert:** Schweizer Pumpspeicher-Kapazitäten aus BFE-Daten. Vergleich: Pumpspeicher arbitriert saisonal (Sommer pumpen, Winter erzeugen), Batterie nur täglich/stündlich.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `ax.set_yticks()` | `matplotlib.axes` | Setzt Y-Achsen-Tick-Positionen manuell. `.set_yticklabels()` setzt die Labels. |

---

## K_09 — Eigenverbrauchsoptimierung (`K_09_Eigenverbrauch.ipynb`)
Berechnet Mehrwert einer Batterie für PV-Haushalte (Eigenverbrauchsoptimierung statt Grid-Arbitrage).

### Zellen 1–3 — Setup & Simulation
**Was passiert:** Haushaltstarife (HT/NT) aus Config in EUR. Synthetisches Tagesprofil: Solarertrag als Sinus-Glockenkurve, Haushaltsverbrauch mit Morgen- und Abendspitze. Simulation: Solarüberschuss → Batterie (wenn nicht voll), abends → Batterie entladen, sonst → Netzstrom. `np.where()` für vektorisierte Tarifwahl.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.where(arr, val_true, val_false)` | `numpy` | Ternärer Operator auf Arrays. `np.where(is_nt, NT_PREIS, HT_PREIS)` = vektorisierte Tarifwahl. |
| `.cumsum()` | `pandas / numpy` | Kumulierte Summe. Für SoC-Verlauf: jede Stunde wird Lade-/Entladeleistung summiert. |

### Zellen 4–6 — Wirtschaftlichkeit & Transfer
**Was passiert:** Eigenverbrauchsnutzen (Einsparung durch weniger Netzstrom) wird berechnet und mit Arbitrage-Erlös verglichen. Transfer-Output in `../sync/transfer.json` unter `eigenverbrauch`.

---

## K_10 — Produktsteckbrief (`K_10_Produkt_Steckbrief.ipynb`)
Erstellt einen formatierten Produkt-Datenblatt für ein konkretes Heimspeicher-Produkt. Enthält eine dedizierte Konfigurationszelle für Produktparameter.

### Zelle 1 — Produktkonfiguration
**Was passiert:** Eine einzelne Konfigurationszelle (mit `╔═══╗`-Rahmen deutlich markiert) enthält alle produktspezifischen Parameter: Name, Hersteller, Kapazität (kWh), Leistung (kW), Verkaufspreis (EUR), HT/NT-Tarife, Tagesverbrauch. **Nur diese Zelle anpassen** — alle nachfolgenden Berechnungen folgen automatisch.

### Zellen 2–4 — Berechnung: Arbitrage, Eigenverbrauch, Kombiniert
**Was passiert:** Grid-Arbitrage-Kennzahlen: ROI und Erlös/Jahr skaliert aus NB03-Ergebnissen (kapazitätsunabhängiger ROI × Produktpreis, C-Rate-Korrekturfaktor). Eigenverbrauch: HT/NT-Preisdifferenz × Tagesenergie × 365. Kombinierter Case: 70% Eigenverbrauch + 30% Arbitrage.

### Zellen 5–6 — Steckbrief-Ausgabe & Transfer
**Was passiert:** Formatierter Steckbrief als Textausgabe. Transfer in `../sync/transfer.json` unter `produkt`.

**Potenzielle Erweiterung:** ipywidgets Slider für Kapazität, Leistung und Preis mit Live-ROI-Berechnung — vorerst nicht implementiert wegen `run_all`-Inkompatibilität (→ O_01 Section 13).

---

## K_99 — Kombinierte Simulation (`K_99_Kombinierte_Simulation.ipynb`)
Synthese-Notebook. Simuliert alle vier Dispatch-Strategien (Arbitrage, Eigenverbrauch, Hybrid statisch, Hybrid optimiert) in einem Lauf.

### Zellen 1–4 — Setup & Simulation
**Was passiert:** Config und Transfer via [`load_transfer`](#lib-io-ops-load-transfer) laden. Die Arbitrage-Simulation wird **NICHT** von der eigenständigen `sim_arbitrage()`-Definition übernommen (die in Phase 6.4b als toter Code entfernt wurde) — stattdessen greift K_99 auf die Ergebnisse zu die NB03 bereits in `transfer.json → simulation` geschrieben hat. Drei weitere lokale Simulations-Funktionen sind definiert:
- `sim_eigenverbrauch()`: HT/NT-optimiert wie K_09
- `sim_hybrid_statisch()`: fester EV-Anteil (70%), Arbitrage mit Rest
- `sim_hybrid_optimiert()`: EV-Anteil variiert täglich nach Spread-Grösse

Diese drei sind NB-lokal und nicht in `lib.simulation` — sie haben andere Parametrierungen als das zentrale Quantil-Dispatch-Modell. Siehe Review-Protokoll R-09 und F-rückbezogen auf `sim_arbitrage`.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.tile()` | `numpy` | Wiederholt ein Array n-mal. `np.tile(np.arange(24), 365)` = Jahres-Stundenvektor. |
| `np.sum()` | `numpy` | Summiert alle Elemente eines Arrays. |
| `mlines.Line2D()` | `matplotlib.lines` | Legenden-Objekt mit Liniensymbol ohne echten Datenpunkt. |
| `mcolors.Normalize()` | `matplotlib.colors` | Normiert Werte auf [0,1] für Colormaps. |
| `plt.suptitle()` | `matplotlib.pyplot` | Haupttitel über alle Subplots einer Figure. |

### Zellen 5–9 — Charts & Transfer
**Was passiert:** Vergleichs-Charts: ROI aller 4 Modi nebeneinander, Break-Even-Vergleich, Cashflow-Kurven, 2×2 Heatmap-Panel (ROI × Segment × Strategie), CAPEX-Szenarien. Schlüsselkennzahlen via [`save_transfer`](#lib-io-ops-save-transfer) in `../sync/transfer.json` unter `hybrid_simulation` geschrieben.

---

# Bekannte Bezeichnungsleichen

Bei der Überarbeitung auf die neue Struktur wurden folgende veralteten Bezeichnungen in Notebook-Titeln gefunden, die noch nicht angepasst wurden:

| Datei | Aktueller Titel | Korrekter Titel |
|---|---|---|
| `organisation/O_04_Review_Protokoll.ipynb` | `NB00c – Review-Protokoll & Qualitätssicherung` | `O_04 – Review-Protokoll & Qualitätssicherung` |
| `organisation/O_99_Datenprovenienz.ipynb` | `NB99 – Daten-Provenienz & Werdegang` | `O_99 – Daten-Provenienz & Werdegang` |
| `notebooks/00_Business_Case.ipynb` | `NB00 – Business Case` | `NB00 – Business Case` *(akzeptabel, da Datei `00_Business_Case.ipynb`)* |

**Empfehlung:** O_04 und O_99 sollten in der jeweiligen Titel-Zelle (cell[0]) angepasst werden. Der Titelfix ist minimal — nur die erste Zeile der Markdown-Zelle betrifft.
