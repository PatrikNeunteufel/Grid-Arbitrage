# Änderungsprotokoll — Grid-Arbitrage Notebooks
**SC26_Gruppe_2 | März 2026**

---

## Übergreifende Änderungen

- **Ordnerstruktur:** `data/intermediate/` aufgeteilt in `pessimistisch/`, `realistisch/`, `optimistisch/` — szenario-abhängige CSVs landen je in ihrem Unterordner
- **Ausgabe-Ordner:** Umbenannt von `charts/` zu `output/charts/` (Pflicht), `output/kuer/<szenario>/` (Kür)
- **Moodle-Hinweise** aus allen Produkt-Notebooks entfernt — nur noch in NB00 (Abschnitt 12)
- **Navigation:** Alle Notebooks haben am Ende (und Anfang) eine Navigationszeile mit Links
- **Leere Zellen:** Entfernt aus NB01, NB02

---

## config.json

| Was | Alt | Neu |
|-----|-----|-----|
| Struktur | Flach | `pflicht.*` / `kuer.*` getrennt |
| GLEICHZEITIGKEIT | Hardcoded im NB | `kuer.szenarien.gleichzeitigkeit_aktiv` |
| Szenarien | `rate_optimistisch / rate_realistisch` | `kuer.szenarien.optionen.{pessimistisch,realistisch,optimistisch}` mit je `rate`, `n_privat_YYYY` etc. |
| Neu | — | `pessimistisch` als dritte Szenario-Option hinzugefügt |
| Kür-Parameter | — | `kuer.raeumlich`, `kuer.crossborder`, `kuer.markt`, `kuer.dispatch` neu |
| `output_dpi` | Fehlte | `visualisierung.output_dpi: 150` hinzugefügt |

---

## 00_Project_Overview.ipynb (NB00)

| Änderung | Detail |
|----------|--------|
| **Projektplan_Grid_Arbitrage.docx** absorbiert | Kein separates docx mehr nötig |
| **Motivation** neu (Abschnitt 1) | Extrinsisch (Leistungsnachweis) + intrinsisch (beruflicher Kontext PN) |
| **Notebook-Map** erweitert | Tabelle mit Status-Badges, Links, Verantwortlichen |
| In-Planung-Status | NB07–NB10 als `📋 in Planung` gelistet mit Hinweis auf Erweiterbarkeit |
| Ordnerstruktur | Vollständige neue Struktur inkl. `intermediate/<szenario>/` und `output/` |
| Projekterweiterungen (alt §7) | In Notebook-Map integriert |
| Notebook-Struktur (alt §8) | Erweitert und in Ordnerstruktur (§6) überführt |
| Einreichung (§12) | Moodle-URLs konkret genannt, zip-Struktur präzisiert |

---

## 00b_Konventionen.ipynb (NB00b)

| Änderung | Detail |
|----------|--------|
| Header | Geltungsbereich auf NB01–NB10 erweitert, 99_Datenprovenienz als manuell markiert |
| Sektion 5 config.json | Hinweis auf neue `pflicht`/`kuer`-Trennung und Szenario-Schalter |
| Review-Checkliste | Zwei neue Punkte: config.json korrekt lesen, Kür-Outputs in Szenario-Ordner |

---

## 01_Daten_Laden.ipynb (NB01)

| Änderung | Detail |
|----------|--------|
| **MODE hardcoded → config.json** | `MODE` kommt jetzt aus `config.json` (nie mehr im Code anpassen) |
| FORCE_RELOAD aus config | Ebenfalls aus config.json geladen |
| Verzeichnisse | `output/charts/`, `data/intermediate/{pessimistisch,realistisch,optimistisch}/` werden beim Start erstellt |
| DS-Nummerierung | Header DS3 Grenzflüsse / Code-Kommentar "Datensatz 4" → vereinheitlicht auf DS3 |
| **Moodle-Hinweis entfernt** | Zelle 8 (DS2-Header) enthielt Hinweis auf Moodle-Eintrag → entfernt |
| Quellenblöcke | Vor jedem Dataset: Quelle, Methode, Zweck klar getrennt als Markdown |
| Navigation | Fusszellen mit Links zu NB00 / NB02 |
| Leere Zellen | Zellen 19, 20 entfernt |
| Abschluss | Erweitert mit ✅/❌ Symbolen und Segment-Beschriftungen |

---

## 02_Daten_Analyse.ipynb (NB02)

| Änderung | Detail |
|----------|--------|
| **MODE hardcoded → config.json** | Setup-Zelle liest alles aus config.json |
| **FORCE_RELOAD → config.json** | Keine hardcodierten FORCE_RELOAD-Dicts mehr |
| **GLEICHZEITIGKEIT → config.json** | `kuer.szenarien.gleichzeitigkeit_aktiv` steuert die Szenario-Wahl |
| Szenarien-Zahlen | Aus `config.json kuer.szenarien.optionen.<aktiv>` gelesen |
| **Szenario-Outputpfad** | `wirtschaftlichkeit.csv` und `netzentlastung_szenarien.csv` → `data/intermediate/<szenario>/` |
| CAPEX/OPEX/LIFETIME | Aus `config.pflicht.wirtschaftlichkeit` gelesen (nicht mehr hardcodiert) |
| Abschluss-Zelle | Neu: prüft alle erwarteten Ausgabedateien |
| Navigation | Kopf- und Fusszellen mit Links |
| Leere Zelle | Zelle 23 entfernt |

---

## 03_Visualisierungen.ipynb (NB03)

| Änderung | Detail |
|----------|--------|
| Titel / Header | Gruppenname, Verantwortlichkeit, Datum ergänzt |
| **`charts/` → `output/charts/`** | `DIR_CHARTS`/`CHARTS_DIR` auf neuen Pfad umgestellt |
| Navigation | Kopf- und Fussnavigation |

---

## 04_Business_Case.ipynb (NB04)

| Änderung | Detail |
|----------|--------|
| Titel | Platzhalter `SC26_Gruppe_XX` / `Person A/B/C` durch reale Namen ersetzt |
| Navigation | Kopf- und Fussnavigation |

---

## Umbenennung Kür-Notebooks

| Alt | Neu | Grund |
|-----|-----|-------|
| `04_Business_Strategy.ipynb` | `05_Business_Strategy.ipynb` | NB04 = Pflicht-Abschluss; Kür ab 05 |
| `05_Raeumliche_Analyse.ipynb` | `06_Raeumliche_Analyse.ipynb` | Logische Reihenfolge |
| `06_Datenprovenienz.ipynb` | `99_Datenprovenienz.ipynb` | Dev/Helper, nicht im normalen Flow |

---

## 05_Business_Strategy.ipynb (ex 04_Business_Strategy)

| Änderung | Detail |
|----------|--------|
| Titel / Nummerierung | NB05 statt NB4_Business_Strategy |
| Navigation | Links zu NB04 und NB06 |

---

## 06_Raeumliche_Analyse.ipynb (ex 05_Raeumliche_Analyse)

| Änderung | Detail |
|----------|--------|
| Titel / Nummerierung | NB06 |
| Navigation | Links zu NB05 und NB07 (in Planung) |

---

## 99_Datenprovenienz.ipynb (ex 06_Datenprovenienz)

| Änderung | Detail |
|----------|--------|
| Nummerierung `99` | Signalisiert Anhang / manuelles Werkzeug |
| Titel | Klargestellt: manuell ausführen, nicht Teil von run_all.sh |
| Navigation | Link zu NB00 Übersicht |

---

## 01b_Daten_Sim.ipynb / 02b_Sim_Analyse.ipynb

| Änderung | Detail |
|----------|--------|
| Titel | Dev/Helper-Kennzeichnung |
| Verzeichnisse | `sim/intermediate/{pessimistisch,realistisch,optimistisch}/` werden erstellt |
| Szenario-Outputs | `wirtschaftlichkeit.csv` / `netzentlastung_szenarien.csv` → `sim/intermediate/realistisch/` |

---

## Nicht geändert (bewusst)

- Alle bestehenden Code-Zellen NB03–NB06 wurden **nicht inhaltlich verändert** (Charts, Dispatch-Logik, BVI-Berechnung etc.)
- `07_Erweiterungen.ipynb` wurde **aufgelöst** — Inhalt verteilt auf NB05 (Trigger-Matrix), NB08 (Spread/CAPEX), NB09 (VPP/Stacking), NB10 (DA-Dispatch). Das Notebook selbst ist nicht mehr Teil des finalen Sets.
- Alle `dataindex`-Helfer-Funktionen unverändert

---
*Erstellt: März 2026 | SC26_Gruppe_2*
