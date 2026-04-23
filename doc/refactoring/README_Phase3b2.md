# Phase 3b (Teil 2 von 2) — Struktur-Harmonisierung: Kür-Notebooks K_06–K_99

6 weitere Kür-Notebooks auf das kanonische Schema gebracht, plus **neue
TOC-Konvention** konsequent angewendet.

## Neue TOC-Konvention

```markdown
## Inhaltsverzeichnis<a id='toc_XX'></a>

[Einleitung](#einleitung_XX)  
[Initialisierung](#initialisierung_XX)  
1 [Erstes-Kapitel](#anchor1_XX)  
2 [Zweites-Kapitel](#anchor2_XX)  
...
[Fazit](#fazit_XX)  
[Abschluss](#abschluss_XX)  
```

**Regeln:**
- Strukturelle Abschnitte (Einleitung, Initialisierung, Fazit, Abschluss) **ohne Nummer**
- Hauptteil mit `N [Titel]` (Zahl + Space, **kein Punkt**, keine Markdown-Liste)
- **Jede Zeile endet mit "  " (2 Leerzeichen)** für Markdown-Hardbreak

## Änderungen pro Notebook

### K_06 — Dispatch-Optimierung
- Neue **Einleitung** mit reaktiv↔DA-optimal-Vergleich als Motivation
- Hauptteil umnumeriert: §2–6 → §1–5
- §7 "## 7. Fazit" → "## Fazit" (ohne Nr)
- TOC im neuen Schema

### K_07 — Technologievergleich
- Neue **Einleitung** mit Übersicht der Speicher-Technologien
- Hauptteil umnumeriert: §2–5 → §1–4
- §6 "## 6. Fazit" → "## Fazit"
- Neuer **"## Abschluss"** (fehlte komplett)
- TOC im neuen Schema

### K_08 — Alternative Speicher (Sonderaufgabe)
- §2 "Motivation" → **als Einleitung übernommen** (Titel + Anker umbenannt,
  Position vor Init verschoben)
  - Anker-Umbennung: `motivation-warum-alternative-speicher_K_08` → `einleitung_K_08`
- Hauptteil umnumeriert: §3–5 → §1–3
- §6 "## Fazit" bleibt
- Neuer **"## Abschluss"** (fehlte komplett)
- TOC im neuen Schema

### K_09 — Eigenverbrauchsoptimierung
- Neue **Einleitung** mit 4-Modell-Übersicht
- Hauptteil umnumeriert: §2–7 → §1–6
- §8 "## 8. Fazit" → "## Fazit"
- Neuer **"## Abschluss"** (fehlte komplett)
- TOC im neuen Schema

### K_10 — Produktsteckbrief
- Neue **Einleitung** mit 3-Modell-Strategie (Arbitrage / Eigenverbrauch / kombiniert)
- Hauptteil umnumeriert: §2–7 → §1–6
- "## Fazit" bleibt (war schon ohne Nummer)
- Neuer **"## Abschluss"** (fehlte komplett)
- TOC im neuen Schema

### K_99 — Kombinierte Simulation
- Neue **Einleitung** mit End-to-End-Synthese-Beschreibung
- Hauptteil umnumeriert: §2–5 → §1–4 (inkl. "Abschlusskontrolle & K_00-Referenz" als §4)
- Neues **inhaltliches "## Fazit"** (fehlte komplett) mit Kernaussagen
- "## Abschluss" bleibt unverändert
- TOC im neuen Schema

## Qualitäts-Checks

| Check | Status |
|---|---|
| JSON-Validität aller 6 NBs | ✅ |
| Alle Cell-IDs erhalten (nbformat 5.1+) | ✅ |
| Keine Anker mit führender Ziffer (projektweit) | ✅ |
| Keine dangling Links (projektweit) | ✅ |
| Alle TOC-Einträge enden mit `  ` (2 Spaces + Newline) | ✅ |
| K_08 Motivation-Anker-Rename bricht keine Cross-NB-Links | ✅ |

## Installation

```bash
cd /pfad/zum/projekt
cp <diese_ZIP>/patched_notebooks/kuer/*.ipynb kuer/
```

Es werden nur die 6 genannten K-Notebooks überschrieben. K_00–K_05 bleiben
unberührt (von dir schon angepasst mit der neuen TOC-Konvention).

## Status nach Phase 3b

**Alle 12 Kür-Notebooks sind jetzt strukturell einheitlich:**

```
K_00 ✅  K_01 ✅  K_02 ✅  K_03 ✅  K_04 ✅  K_05 ✅
K_06 ✅  K_07 ✅  K_08 ✅  K_09 ✅  K_10 ✅  K_99 ✅
```

## Nächste Schritte

- **Phase 3c** — `organisation/O_04` TOC-Reposition (TOC an falscher Stelle)
- **Phase 3d** — `experimental/` (K_01b, K_01c, K_01d) + **Integration von K_01d_slider**
  als Ersatz für das bestehende K_01d
- **Phase 4** — Animations-Schalter in config.json + Zellen-Header
- **Phase 5** — slide_or_play nach lib/widgets.py
- **Phase 6** — Lib-Migration
