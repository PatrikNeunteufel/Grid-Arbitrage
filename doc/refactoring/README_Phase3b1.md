# Phase 3b (Teil 1 von 2) — Struktur-Harmonisierung: Kür-Notebooks K_00–K_05

6 Kür-Notebooks auf das kanonische Schema gebracht:

```
Titel → Nav → TOC → Einleitung → Initialisierung → §1..§n → Fazit → Abschluss → Nav
```

## Änderungen pro Notebook

### K_00 — Business Strategy (analog NB00)
- **Einleitung ↔ Initialisierung getauscht** (Einleitung jetzt vor Init)
- Hauptteil um 1 dekrementiert: §2–12 → §1–11 (Daten, Marktlage, Wertquellen, ...)
- §13 "Strategisches Fazit" → ohne Nummer, Titel bleibt
- Abschluss unverändert
- TOC vollständig aktualisiert (15 Einträge statt 14)

### K_01 — Räumliche Analyse
- Neue **Einleitung** mit Datenquellen-Übersicht (BFE, BFS, swissBOUNDARIES3D)
- §8 "Fazit: Was die räumliche Analyse zeigt" → ohne Nummer
- Neuer **"## Abschluss"** mit Datei-Check (fehlte komplett)
- TOC-Bug (fehlende Nummer vor Initialisierung) behoben, Einleitung + Abschluss eingetragen

### K_02 — Cross-Border (Sonderaufgabe)
- Neue **Einleitung** mit Kernthese
- Hauptteil umnumeriert: §2 Analyse → §1, §3 Visualisierung → §2
- **Abschluss ↔ Fazit getauscht** — bisher falsch: `Abschlusskontrolle` vor `Fazit`, jetzt korrekt: `Fazit` vor `Abschluss`
- `## Abschlusskontrolle` → `## Abschluss`, Anker `abschlusskontrolle_K_02` → `abschluss_K_02`
- TOC-Bug (5× "1.") behoben → sauber 1–6

### K_03 — Marktdynamik
- Neue **Einleitung** mit 4-Punkte-Übersicht
- Neues **Fazit** mit Monitoring-Trigger-Kernaussage
- `## 1. Initialisierung` → `## Initialisierung` (Nummer weg)
- Hauptteil umnumeriert: §2–6 → §1–5
- TOC vollständig aktualisiert (9 Einträge)

### K_04 — Animationen
- Neue **Einleitung** mit Options-Übersicht (A/B/C) und Konfig-Bezug
- Neues **Fazit** mit visueller Frühling/Sommer/Winter-Validierung
- Hauptteil umnumeriert: §2–6 → §1–5
- Reihenfolge: §5 Option C → Fazit → "Potenzielle Erweiterungen" → Abschluss
- TOC ergänzt um "Potenzielle Erweiterungen" (Anker `erweiterungen_K_04` existiert bereits)

### K_05 — Revenue Stacking
- Neue **Einleitung** mit FCR-Verfügbarkeitsprämie-Klarstellung
- Hauptteil umnumeriert: §2–4 → §1–3
- §4 "## 4. Fazit" → "## Fazit" (ohne Nummer)
- TOC aktualisiert

## Qualitäts-Checks

| Check | Status |
|---|---|
| JSON-Validität aller 6 NBs | ✅ |
| Alle Cell-IDs erhalten (nbformat 5.1+) | ✅ |
| Keine Anker mit führender Ziffer (projektweit) | ✅ |
| Keine dangling Links (projektweit) | ✅ |
| K_04 Erweiterungs-Anker und TOC-Link konsistent | ✅ |

## Installation

```bash
cd /pfad/zum/projekt
cp <diese_ZIP>/patched_notebooks/kuer/*.ipynb kuer/
```

Es werden nur die 6 genannten K-Notebooks überschrieben. K_06–K_10, K_99 bleiben
unberührt und kommen in Phase 3b Teil 2.

## Was als Nächstes kommt

- **Phase 3b Teil 2** — K_06, K_07, K_08, K_09, K_10, K_99
  - K_06 hat ein Sonderproblem: eine fehlerhafte H1 "Skizze — nicht produktiv"
    mitten im Dokument (muss auf H4 heruntergestuft werden)
  - K_07, K_09, K_10 brauchen neuen Abschluss (fehlt komplett)
  - K_08 § "Motivation" soll die Einleitung werden
  - K_99 braucht ein inhaltliches Fazit (Zusammenfassung der kombinierten Simulation)
- **Phase 3c** — organisation/O_04 TOC-Reposition
- **Phase 3d** — experimental/ + K_01d_slider-Integration
