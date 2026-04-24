# Phase 8 — Schritt 4: O_03_Konventionen Library-Ergänzungen

## Was geändert wurde

**Bestehende Sektionen aktualisiert** (ohne Kernaussagen zu verändern):

- **Cell 1 (TOC)**: Einträge 19 und 20 ergänzt
- **Cell 9 (§7 Ergebnistransfer):** Manuelle JSON-Lade/Speicher-Snippets durch
  `load_transfer` / `save_transfer` aus `lib.io_ops` ersetzt. Mit Begründung
  für die Merge-Logik (historischer Bugquell vor der lib-Zentralisierung).
- **Cell 12 (§10 Datenprotokoll):** Expliziter `from lib.io_ops import log_dataindex`-
  Import im Code-Beispiel. Hinweis auf `log_missing` als Pendant bei Fehlern.
  Verbot einer lokalen `log_dataindex`-Definition klargestellt.
- **Cell 18 (§16.1 Ordnerstruktur):** `lib/`-Ordner und `experimental/`-Ordner
  im ASCII-Baum ergänzt.

**Neue Sektionen hinzugefügt:**

### §19 Library-Konvention (lib/)

5 Unterpunkte:
- **19.1 Zweck:** lib/ als SSOT für Code, analog zu config.json für Parameter
- **19.2 Wann lib, wann NB-lokal?** Konkrete Regel mit Ein-/Ausschlusskriterien
- **19.3 Bootstrap-Import** — das Standard-Muster aus jedem NB
- **19.4 Änderungs-Regeln** — Review-Pflicht, Breaking-Changes-Prüfung,
  numerische Tests bei Dispatch-Funktionen
- **19.5 Keine lokalen Kopien** — mit explizit dokumentierten Ausnahmen
  (`simulate_battery_da_optimal`, `sim_eigenverbrauch`/`sim_hybrid_*`,
  `check_aktiv`)

### §20 `show_source`-Block-Konvention

5 Unterpunkte:
- **20.1 Zweck:** Transparenz für Reviewer — Quellcode der lib-Funktionen
  inline sichtbar ohne `.py`-Datei zu öffnen
- **20.2 Pattern:** das 2-Zellen-Block-Muster (Markdown + Code)
- **20.3 Wann anwenden?** — bei jeder **ersten** Verwendung pro NB, nicht
  bei jedem Aufruf
- **20.4 Bei mehreren lib-Funktionen** — pro Funktion eigener Block am
  passenden Kontext, nicht gesammelt am Anfang
- **20.5 Ausschluss:** NB-lokale Funktionen brauchen keinen show_source-
  Block (Code steht schon im NB)

## Qualitäts-Checks (alle ✅)

```
TOC hat Eintrag 19                    ✅
TOC hat Eintrag 20                    ✅
§7 nutzt load_transfer                ✅
§7 nutzt save_transfer                ✅
§10 importiert log_dataindex          ✅
§16.1 hat lib/ im Baum                ✅
§16.1 hat experimental/               ✅
§19 Library-Konvention da             ✅
§19 Wann lib, wann NB-lokal           ✅
§19 Keine lokalen Kopien              ✅
§20 show_source-Konvention da         ✅
§20 2-Zellen-Block erklärt            ✅
Gesamtzellen (war 24 → jetzt 26)      ✅
```

## Was nicht verändert wurde

- **Sektionen 1-6, 8-9, 11-18** unverändert (außer den 3 gezielten
  Ersetzungen)
- Code-Zelle 22 (Muster-Laden) unverändert
- Cell 21 (Navigationsleiste) unverändert
- Cell 23 (leer) unverändert

## Phase 8 abgeschlossen — Überblick

| Schritt | Dokument | Status |
|---|---|---|
| 1 | O_01 §5 Notebook-Map + §6.1 Library-Architektur | ✅ |
| 2 | O_04 §2 Review-Protokoll + §4 Zusammenfassung | ✅ |
| 3a | Notebook_Dokumentation.md neues Library-Kapitel | ✅ |
| 3b | Notebook_Dokumentation.md Inline-Verweise in NBs | ✅ |
| 4 | O_03 Library- und show_source-Konventionen | ✅ |

Die Dokumentation spiegelt jetzt den vollständigen Zustand nach Phasen 1-7b
Refactoring.

## Installation

```bash
cp <ZIP>/O_03_Konventionen.ipynb organisation/
```

## Was noch offen ist für die Abgabe

- **Phase 9 — Regressionstest run_all:** Einmal den gesamten Pipeline-Lauf
  mit allen NBs, idealerweise mit `animation.modus: 'skip_if_exists'` damit
  die GIFs cached sind. Stellt sicher dass alle lib-Importe resolven und
  alle Provenance-Logs geschrieben werden.
- **Refactoring_Plan.md Update:** der existierende Plan ist noch auf Stand
  Phase 7 — alle Fix-Patches nach Phase 7b (Einrückung, `_render_grid_background`,
  show_source-Nachzug) fehlen. Sollte vor Abgabe nachgezogen werden damit
  der Plan den tatsächlichen Projektverlauf dokumentiert.
- **30.04.2026 Entscheidung:** welche Kür-NBs in die Abgabe kommen (K_01b/c/d
  sind `experimental/` und damit standardmässig draussen)
- **11.05.2026 Abgabe:** finale Packung für Moodle
