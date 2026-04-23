# Phase 3a — Struktur-Harmonisierung: Pflicht-Notebooks

Die 5 Pflicht-Notebooks (`notebooks/NB00–NB04`) haben jetzt einheitlich das
kanonische Schema:

```
1. Titel
2. Navigations-Links
3. Inhaltsverzeichnis
4. Einleitung          ← inhaltlich: Motivation, Scope, Erwartung
5. Initialisierung     ← technisch: Imports, Config, Pfade
6. Hauptteil §1..§n    ← nummerierte Sachabschnitte
7. Fazit               ← inhaltlich: Kernerkenntnisse, Schlüsselzahlen
8. Abschluss           ← technisch: Datei-Check, transfer.json
9. Navigations-Links
```

**Strukturelle Abschnitte** (4, 5, 7, 8) sind jetzt konsistent **ohne Nummer**.
Nummeriert wird nur der **Hauptteil** (§1, §2, ...).

## Änderungen pro Notebook

### NB00 — Business Case
- **Einleitung ↔ Initialisierung getauscht** (vorher stand Init vor Einleitung)
- Hauptteil §1–3 statt §2–4 (Daten / Methodik / Ergebnisse)
- §5 "Fazit und Empfehlungen" → ohne Nummer
- §6 "Kür-Notebooks" → "Kür-Erweiterungen" (ohne Nummer), jetzt als **Anhang vor Abschluss**
- Neuer **"## Abschluss"-Header** mit Anker `abschluss_NB_00` vor der Abschlusskontroll-Code-Zelle
- TOC um Initialisierung, Fazit, Kür-Erweiterungen, Abschluss erweitert

### NB01 — Daten Laden
- Neue **Einleitung**: ENTSO-E API, Datensätze DS1/DS2, Retry-Logik, Output-Struktur
- Neues **Fazit**: Datenqualität, Datenzeitraum, Transfer-Übergabe an NB02
- `## Abschluss & Verifikation` → `## Abschluss` (Titel vereinheitlicht)
- Anker `abschluss-verifikation_NB_01` → `abschluss_NB_01`
- TOC um Einleitung, Fazit erweitert; Abschluss-Linkziel aktualisiert

### NB02 — Daten Bereinigung
- Neue **Einleitung**: UTC-Normierung, Deduplizierung, Kurzlücken-Interpolation
- Neues **Fazit**: Datenqualität-Kennzahlen, Ausgangsbasis für NB03
- `## 1. Initialisierung` → `## Initialisierung` (Nummer weg)
- `## 2. Datenbereinigung Spot-Preise` → `## 1. ...` (jetzt §1 des Hauptteils)
- `## Abschluss & Verifikation` → `## Abschluss`
- Anker `abschluss-verifikation_NB_02` → `abschluss_NB_02`
- TOC um Einleitung, Fazit erweitert

### NB03 — Daten Analyse
- Neue **Einleitung**: 5-Punkte-Übersicht der Analyseschritte
- Neues **Fazit**: ROI-Aussagen je Segment, Saisonalitäts-Kernzahlen
  (Frühling ~139 EUR/MWh, Winter ~85 EUR/MWh Spread)
- Hauptteil-Nummerierung 2→1, 3→2, 4→3, 5→4, 6→5
- `## Abschluss & Verifikation` → `## Abschluss`
- Anker `abschluss-verifikation_NB_03` → `abschluss_NB_03`
- TOC vollständig aktualisiert

### NB04 — Visualisierungen
- Neue **Einleitung**: Aufgaben-Mapping (Aufgabe a → Chart 1, Aufgabe b → Chart 2)
- Neues **Fazit**: Kernaussagen aller 5 Pflicht-Charts
- Chart-Überschriften umbenannt zu §-Nummerierung:
  - `## Chart 1 (Aufgabe a): Summary...` → `## 1. Summary-Diagramm – Wirtschaftlichkeit (Pflichtaufgabe a)`
  - `## Chart 2 (Aufgabe b): Heatmap...` → `## 2. Heatmap – Spot-Preis nach Stunde × Monat (Pflichtaufgabe b)`
  - `## Chart 3: Tagesprofil...` → `## 3. Tagesprofil Netzlast & Spot-Preis`
  - `## Chart 4: Netzentlastung...` → `## 4. Netzentlastungsszenarien`
  - Cell 33 `## 5. Saisonale Arbitrage-Analyse` bleibt
  - Cell 34 `## Chart 5:...` → **H3** `### 5.1 Saisonale Analyse...` (Unterabschnitt von §5)
- **Anker bleiben erhalten** (damit keine Cross-NB-Links brechen)
- TOC vollständig aktualisiert

## Qualitäts-Checks

| Check | Status |
|---|---|
| JSON-Validität aller 5 NBs | ✅ |
| Alle Cell-IDs erhalten (nbformat 5.1+) | ✅ |
| Keine Anker mit führender Ziffer (projektweit) | ✅ |
| Keine dangling Links (projektweit) | ✅ |
| Kein Cross-NB-Link aus Kür/Experimental/Organisation zeigt auf alte Abschluss-Anker | ✅ |

## Installation

```bash
cd /pfad/zum/projekt
cp <diese_ZIP>/patched_notebooks/*.ipynb notebooks/
```

Es werden nur die 5 Pflicht-NBs überschrieben. Der Rest des Projekts bleibt
unangetastet.

## Verifikation nach Installation

1. Jedes NB öffnen, TOC-Links durchklicken — alle müssen korrekt springen
2. `Kernel → Restart & Run All` einmal pro NB — muss durchlaufen, die Strukturänderungen sind rein Markdown, keine Code-Änderungen
3. Neue Einleitungs- und Fazit-Texte lesen — bei Bedarf an eigene Formulierungen anpassen (die Texte sind fachlich korrekt, aber das kannst du natürlich stilistisch nachschärfen)

## Nächste Schritte

- **Phase 3b** — Kür-Notebooks (`kuer/K_00–K_99`, 12 NBs)
- **Phase 3c** — Organisation (`O_04` TOC-Reposition)
- **Phase 3d** — Experimental (inkl. K_01d_slider → ersetzt K_01d)
