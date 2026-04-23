# Phase 1 — Installation & Verifikation

Das enthaltene `lib/`-Verzeichnis und `Test_Phase1.ipynb` sind die Auslieferung der Phase 1 des Refactorings.

## Was ist drin

```
lib/
├── __init__.py              # Package-Init, Doku, Import-Pattern
├── io_ops.py                # Platzhalter — Phase 6a
├── data_fetchers.py         # Platzhalter — Phase 6a/6b/6d
├── simulation.py            # Platzhalter — Phase 6a/6b
├── plotting.py              # AKTIV: show_source() + should_skip()
├── widgets.py               # Platzhalter — Phase 5
├── columns.py               # Platzhalter — Phase 6b/6d
└── grid_topo.py             # Platzhalter — Phase 6d

Test_Phase1.ipynb            # Selbsttest-Notebook
```

## Installation im Projekt

### 1. Baseline sichern (Phase 0)

Bevor du etwas änderst:

```bash
cd /pfad/zum/projekt
git add -A
git commit -m "baseline-v2-start"
# Optional: ZIP-Kopie als zusätzliche Sicherheit
```

### 2. lib/ ins Projekt einbinden

Kopiere den `lib/`-Ordner auf **Projekt-Root-Ebene**, also parallel zu `notebooks/`, `kuer/`, `organisation/`, `experimental/`, `sync/`:

```
ZHAW_Scripting_Projekt/
├── experimental/
├── kuer/
├── lib/               ← NEU
│   ├── __init__.py
│   ├── columns.py
│   ├── data_fetchers.py
│   ├── grid_topo.py
│   ├── io_ops.py
│   ├── plotting.py
│   ├── simulation.py
│   └── widgets.py
├── notebooks/
├── organisation/
├── output/
├── sync/
└── ...
```

### 3. Abhängigkeiten prüfen

`show_source` braucht zwei zusätzliche Packages für optimale Darstellung:

```bash
pip install ipython pygments
```

`pygments` ist **optional** — ohne Package funktioniert `show_source` auch, nur ohne Syntax-Highlighting (Plain-Code-Block). Wenn pygments vorhanden ist, wird automatisch das `github-dark`-Theme genutzt.

### 4. Verifikation

Öffne `Test_Phase1.ipynb` in JupyterLab und führe alle Zellen aus.

**Wo das Notebook hinkopieren:**
- Auf Projekt-Root-Ebene → dann läuft es direkt (weil `_lib_root = Path('.')`)
- Alternativ nach `notebooks/` oder `kuer/` — dann in der Setup-Zelle ändern: `_lib_root = Path('..').resolve()`

**Erwartete Ausgabe:**
- Test 1: grüner Haken, Modul-Objekte werden gelistet
- Test 2+3: aufklappbare `<details>`-Boxen mit Syntax-Highlighting
- Test 4: 5 grüne Haken (alle Entscheidungs-Pfade)
- Test 5: 1 grüner Haken (Master-Schalter)
- Test 6: 2 grüne Haken (Error-Handling)

**Falls Test 2/3 keine aufklappbaren Boxen zeigen:**
- Notebook "Trust"-Status prüfen (oben rechts in JupyterLab)
- Browser Hard-Reload (Ctrl+Shift+R)

## Was Phase 1 NICHT tut

- **Keine Notebook-Änderungen** — bestehende Notebooks bleiben unangetastet
- **Keine Funktionen migriert** — die kommen erst in Phase 6
- **Keine Config-Änderungen** — kommt in Phase 4 (Animations-Schalter)

Phase 1 ist bewusst minimal: nur die Infrastruktur für später kommende Phasen.

## Nächste Schritte

Nach erfolgreicher Verifikation mit `Test_Phase1.ipynb`:

- **Phase 2** — Anker-Hygiene (mechanisch, 8 Notebooks bereinigen)
- **Phase 3** — Struktur-Harmonisierung (Einleitung/Fazit/Abschluss)
- **Phase 4** — Animations-Schalter in config.json + Zellen-Headers
- **Phase 5** — `slide_or_play` in lib/widgets.py + Robustheits-Fixes
- **Phase 6** — Lib-Migration step-by-step je Notebook

Details siehe `Refactoring_Plan.md` §7.

## Falls etwas schief läuft

**Test 1 scheitert mit `ModuleNotFoundError: No module named 'lib'`:**
- `lib/` liegt nicht auf der erwarteten Ebene, oder `_lib_root` zeigt auf den falschen Pfad
- Prüfen: `print((_lib_root / 'lib' / '__init__.py').exists())` muss `True` geben

**Test 2 zeigt Plain-Text statt aufklappbare Box:**
- JupyterLab hat das Notebook nicht als Trusted markiert
- Oder: Browser-Rendering hängt — Hard-Reload

**`pip install pygments` schlägt fehl:**
- `show_source` funktioniert trotzdem mit einfachem Pre-Block
- Keine kritische Abhängigkeit
