# Phase 3e — TOC-Retrofit: 6 NBs aufs neue Schema

Reine TOC-Umstellung. Kein Content wurde angefasst, kein Anker geändert,
keine Struktur verschoben — nur die TOC-Zelle je NB wird ausgetauscht.

## Neues TOC-Schema (Erinnerung)

```markdown
## Inhaltsverzeichnis<a id='toc_XX'></a>

[Strukturell](#anchor_XX)  
1 [Hauptteil-1](#anchor1_XX)  
2 [Hauptteil-2](#anchor2_XX)  
...
```

- Strukturelle Einträge (Einleitung, Init, Fazit, Abschluss) **ohne Nummer**
- Hauptteil **mit `N [Titel]`** (Zahl + Space, **kein Punkt**, keine MD-Liste)
- Jede Zeile endet mit **2 Leerzeichen** + Newline (MD-Hardbreak)

## Mapping-Entscheidungen je NB

| NB | Strukturell (ohne Nr) | Hauptteil (mit Nr) |
|---|---|---|
| **00_Business_Case** | Einleitung, Init, Fazit und Empfehlungen, Kür-Erweiterungen, Abschluss | §1 Daten, §2 Methodik, §3 Ergebnisse |
| **O_00_Installer** | Einleitung, Init, Abschluss | §1–10 Installationsgruppen (Grundausstattung bis Profile) |
| **O_01_Project_Overview** | — (keine) | §1–13 (Motivation bis Potenzielle Erweiterungen) |
| **O_02_Glossar** | — (keine) | §1–6 (Energiemarkt bis Abkürzungen) |
| **O_03_Konventionen** | — (keine) | §1–18 (Zellstruktur bis Kür-Erweiterbarkeit) |
| **O_99_Datenprovenienz** | Setup, Zusammenfassung | §1 Daten laden, §2–5 Charts A–D |

## Qualitäts-Checks

| Check | Status |
|---|---|
| Alle 6 TOCs im neuen Format (keine MD-Liste, 2-Space-Endung) | ✅ |
| Alle TOC-Links zeigen auf existierende Anker (keine dangling links) | ✅ |
| JSON-Validität, Cell-IDs erhalten | ✅ |
| Struktur + Content der NBs unverändert | ✅ (nur TOC-Zelle ersetzt) |

## Installation

```bash
cd /pfad/zum/projekt

# Pflicht-NB
cp <ZIP>/patched_notebooks/notebooks/00_Business_Case.ipynb notebooks/

# Organisation-NBs
cp <ZIP>/patched_notebooks/organisation/O_*.ipynb organisation/
```

## Status nach Phase 3e — Alle NBs einheitlich

| Ordner | NBs | Status |
|---|---|---|
| `notebooks/` | NB00–NB04 | ✅ Struktur + TOC |
| `kuer/` | K_00–K_10, K_99 | ✅ Struktur + TOC |
| `experimental/` | K_01b, K_01c, K_01d | ✅ Struktur + TOC |
| `organisation/` | O_00, O_01, O_02, O_03, O_04, O_99 | ✅ Struktur + TOC |

Damit ist **Phase 3 (Struktur-Harmonisierung) vollständig abgeschlossen**. Alle
Projekt-NBs folgen dem kanonischen Schema und nutzen das einheitliche TOC-Format.

## Was als Nächstes kommt

- **Phase 4** — Animations-Schalter in `config.json` + `should_skip()`-Nutzung
  in den Chart-/GIF-Zellen
- **Phase 5** — `slide_or_play` nach `lib/widgets.py` migrieren + GIF-Fallback
- **Phase 6** — Lib-Migration: Funktionen aus Notebooks nach `lib/`-Modulen
  ziehen (step-by-step je NB)
