# Phase 1 — Auslieferung

## Was in dieser ZIP enthalten ist

```
Phase1_lib_Skeleton/
├── lib/
│   ├── __init__.py          # Package-Init + ensure_installed()
│   ├── columns.py           # Platzhalter — Phase 6b/6d
│   ├── data_fetchers.py     # Platzhalter — Phase 6a/6b/6d
│   ├── grid_topo.py         # Platzhalter — Phase 6d
│   ├── io_ops.py            # Platzhalter — Phase 6a
│   ├── plotting.py          # AKTIV: show_source() + should_skip()
│   ├── simulation.py        # Platzhalter — Phase 6a/6b
│   └── widgets.py           # Platzhalter — Phase 5
├── organisation/
│   └── O_00_Installer.ipynb # NEU: pip-Installation gruppenweise
├── test/
│   └── Test_Phase1.ipynb    # Selbsttest für Phase 1 (nicht Teil der Abgabe)
└── README_Phase1.md         # dieses File
```

## Installation im Projekt

### 1. Baseline sichern (Phase 0)

Vor jeder Änderung:

```bash
cd /pfad/zum/projekt
git add -A
git commit -m "baseline-v2-start"
```

### 2. Dateien ins Projekt einbinden

**Ziel-Struktur nach Phase 1:**

```
ZHAW_Scripting_Projekt/
├── experimental/
├── kuer/
├── lib/                     ← NEU (kompletten Ordner kopieren)
├── notebooks/
├── organisation/
│   ├── O_00_Installer.ipynb ← NEU (Datei kopieren)
│   ├── O_01_Project_Overview.ipynb
│   ├── O_02_Glossar.ipynb
│   ├── O_03_Konventionen.ipynb
│   ├── O_04_Review_Protokoll.ipynb
│   └── O_99_Datenprovenienz.ipynb
├── output/
├── sync/
├── test/                    ← NEU (nur für Entwicklung, nicht für Abgabe)
│   └── Test_Phase1.ipynb    ← NEU
└── ...
```

### 3. Test-Verzeichnis vs. Abgabe

Das `test/`-Verzeichnis ist **nicht Teil der Moodle-Abgabe**. Empfehlung:

- Im Git-Repo behalten (versioniert) — Tests sind Teil der Entwicklung
- Beim Packaging für Moodle **ausschliessen** — z.B. mit `zip -r abgabe.zip ZHAW_Scripting_Projekt -x 'ZHAW_Scripting_Projekt/test/*'`
- Ggf. später noch eine `.moodle-exclude`-Datei oder einen Eintrag im Abgabe-Script

Alternativ: `.gitignore` lassen und nur lokal haben. Hängt von eurem Workflow ab.

### 4. Erstes-Mal-Setup

Nach dem Kopieren **einmalig** ausführen:

1. `organisation/O_00_Installer.ipynb` öffnen und die "Profile: Alles auf einmal"-Zelle ausführen — installiert alle nötigen Pakete (überspringt was schon da ist)
2. **Kernel neu starten** (wichtig falls `ipywidgets` neu installiert wurde!)
3. `test/Test_Phase1.ipynb` ausführen — prüft Phase-1-Funktionalität

## Was der Installer tut

Der Installer gruppiert Pakete thematisch, damit du nur das installieren kannst, was du wirklich brauchst:

| Gruppe | Inhalt | Für |
|---|---|---|
| Grundausstattung | pandas, numpy, matplotlib, scipy, requests | alle Notebooks |
| lib/-Helper | IPython, pygments | alle (für `show_source`) |
| Pflicht | entsoe-py | `notebooks/01–04`, `kuer/K_02` |
| Kür Geo | geopandas, shapely | `kuer/K_01`, `experimental/K_01*` |
| Kür Anim | Pillow | `kuer/K_01`, `K_04`, `experimental/K_01c`, `K_01d` |
| Kür Netz | networkx | `experimental/K_01d` |
| Kür Rich | rich | `kuer/K_10` |
| Exp Topo | earth-osm | `experimental/K_01d` (optional) |
| Exp Widgets | ipywidgets, jupyterlab_widgets | `experimental/K_01d` Slider |

Jede Gruppe hat eine eigene Code-Zelle, die du einzeln ausführen kannst. Am Ende eine "Alles-auf-einmal"-Zelle und eine Abschluss-Zelle mit Versions-Check.

Intern nutzt der Installer `lib.ensure_installed()` — die Funktion ist auch aus anderen Notebooks verwendbar und kann in Phase 6 das bisherige `try/except ImportError + subprocess`-Muster in den Notebooks ersetzen.

## Was show_source kann

**Signatur:**
```python
show_source(func, title=None, collapsed=True, mode='markdown', style='default')
```

**Default (Markdown-Mode):** JupyterLab rendert den Codeblock mit seinem **eigenen** Syntax-Highlighting — passt zum aktiven Theme (hell/dunkel), kein Kontrastproblem.

**Alternativ (HTML-Mode):** `mode='html'` mit wählbarem pygments-Style, theme-unabhängig. Nützlich für HTML-Export oder feste Darstellung.

## Was should_skip tut

Entscheidet anhand `CFG['animation']`, ob eine Animation/ein Chart neu gerendert werden muss:

- `modus: 'skip_if_exists'` → überspringen wenn Datei existiert (Default für Animationen)
- `modus_statisch: 'always'` → immer rendern (Default für statische Charts)
- `modus_statisch: 'skip_if_exists_all'` → Master-Schalter: alle statischen Charts werden skip_if_exists
- `overrides[name]` → pro-Chart-Override, höchste Priorität

Kommt in Phase 4 zum Einsatz (Animations-Schalter in config.json + Zellen-Header).

## Troubleshooting

### `ModuleNotFoundError: No module named 'lib'`
`lib/` liegt nicht auf erwarteter Ebene. Prüfen: `print((_lib_root / 'lib' / '__init__.py').exists())` muss `True` ergeben.

### `show_source`-Output ist Plain-Text statt Code-Block
Notebook ist nicht "Trusted" markiert (oben rechts in JupyterLab). Oder Browser-Cache — Hard-Reload (Ctrl+Shift+R).

### `pip install` im Installer schlägt mit "externally-managed-environment" fehl
Systempython mit PEP 668. Zwei Optionen:
- Virtuelle Umgebung nutzen (empfohlen): `python -m venv .venv && source .venv/bin/activate`
- Oder in der pip-Zeile `--break-system-packages` ergänzen (nur wenn du weisst was du tust)

### ipywidgets-Installation hat keinen Effekt
- Kernel muss nach `pip install ipywidgets` neu gestartet werden
- JupyterLab komplett schliessen (nicht nur Tab, auch Server stoppen) und neu starten
- Notebook als "Trusted" markieren

## Nächste Schritte

Nach erfolgreicher Verifikation (`test/Test_Phase1.ipynb` zeigt alle ✅):

- **Phase 2** — Anker-Hygiene (8 Notebooks, mechanische String-Ersetzungen)
- **Phase 3** — Struktur-Harmonisierung (Einleitung/Fazit/Abschluss in 18+ Notebooks)
- **Phase 4** — Animations-Schalter in `config.json` + Zellen-Header
- **Phase 5** — `slide_or_play` nach `lib/widgets.py` mit GIF-Fallback
- **Phase 6** — Lib-Migration step-by-step je Notebook

Details siehe `Refactoring_Plan.md` §7.
