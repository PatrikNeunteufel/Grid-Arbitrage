# Grid-Arbitrage mit Batteriespeichern

**CAS Information Engineering – Scripting · ZHAW School of Engineering**  
**Gruppe:** SC26_Gruppe_2 · **Abgabe:** 11. Mai 2026

---

## Projektidee

Kaufe Strom günstig (Preis-Tief), speichere ihn in einer Batterie, speise teuer ein (Preis-Hoch). Lohnt sich das in der Schweiz?

Dieses Projekt analysiert die wirtschaftliche Rentabilität von **Grid-Arbitrage mit Batteriespeichern** im Schweizer Strommarkt auf Basis realer ENTSO-E Day-Ahead-Preisdaten (2023–2026). Vier Marktsegmente werden verglichen — von Privathaushalten bis zu Utility-Grossprojekten — und durch umfangreiche Kür-Analysen zu Standort, Technologie, Revenue Stacking und Dispatch-Optimierung ergänzt.

---

## Kernergebnisse (Datenbasis: 2023–2026, 3.3 Jahre)

| Segment | Kapazität | Jahreserlös | ROI | Break-Even |
|---------|-----------|-------------|-----|------------|
| Privat | 10 kWh / 5 kW | 130 EUR | 1.7 % | > 20 J |
| Gewerbe | 100 kWh / 30 kW | 1'371 EUR | 3.1 % | > 20 J |
| Industrie | 1 MWh / 200 kW | 13'166 EUR | 4.5 % | > 20 J |
| Utility | 10 MWh / 1 MW | 79'063 EUR | 2.9 % | > 20 J |

> **Befund:** Reine Grid-Arbitrage erreicht bei aktuellen CH-Marktbedingungen (Ø Spread 24.5 EUR/MWh) in keinem Segment den Ziel-ROI. Mit Revenue Stacking (FCR/aFRR via VPP) wird Industrie/Utility rentabel; Privat profitiert primär von Eigenverbrauchsoptimierung (ROI 3.75 %, Payback 26.6 J).

---

## Einstieg

Drei Notebooks decken den kompletten Projektumfang ab:

| | Notebook | Inhalt | Öffnen |
|-|----------|--------|--------|
| 🗂 | **O_01 – Projektübersicht** | Struktur, Methodik, Notebook-Map, Projektplan, Datenquellen | [`organisation/O_01_Project_Overview.ipynb`](organisation/O_01_Project_Overview.ipynb) |
| 📋 | **00 – Business Case** | Konsolidierter Bericht: Ergebnisse, Methodik, Empfehlungen (Pflicht-Abgabe) | [`notebooks/00_Business_Case.ipynb`](notebooks/00_Business_Case.ipynb) |
| 🎯 | **K_00 – Business Strategy** | Strategische Synthese aller Kür-Analysen: Trigger-Matrix, Standort, FCR-Gamechanger | [`kuer/K_00_Business_Strategy.ipynb`](kuer/K_00_Business_Strategy.ipynb) |

---

## Alle Notebooks

### Organisation (`organisation/`)

| ID | Datei | Beschreibung |
|----|-------|--------------|
| O_01 | `O_01_Project_Overview.ipynb` | Einstiegspunkt: Struktur, Methodik, Projektplan |
| O_02 | `O_02_Glossar.ipynb` | Fachbegriffs-Glossar mit Querverweisen |
| O_03 | `O_03_Konventionen.ipynb` | Code- und Notebook-Konventionen, SSOT-Regeln |
| O_04 | `O_04_Review_Protokoll.ipynb` | QS-Prozess, KI-Einsatz, Review-Iterationen |
| O_99 | `O_99_Datenprovenienz.ipynb` | Daten-Lineage, Pipeline-Visualisierung *(manuell ausführen)* |

### Pflicht (`notebooks/`)

| NB | Datei | Beschreibung |
|----|-------|--------------|
| NB01 | `01_Daten_Laden.ipynb` | ENTSO-E API: Spot-Preise & Netzlast download |
| NB02 | `02_Daten_Bereinigung.ipynb` | Clipping, Interpolation, Feature Engineering |
| NB03 | `03_Daten_Analyse.ipynb` | Dispatch-Simulation, ROI/CAPEX, Netzentlastung |
| NB04 | `04_Visualisierungen.ipynb` | Charts 1–5: Wirtschaftlichkeit, Heatmap, Tagesprofil, Szenarien |
| NB00 | `00_Business_Case.ipynb` | **Hauptbericht** – Pflicht-Abgabe |

### Kür (`kuer/`)

| K | Datei | Beschreibung |
|---|-------|--------------|
| K_00 | `K_00_Business_Strategy.ipynb` | Strategische Synthese aller Kür-Ergebnisse ← Einstieg |
| K_01 | `K_01_Raeumliche_Analyse.ipynb` | Battery Value Index (BVI), Zonenbilanzen, CH-Karten |
| K_02 | `K_02_Cross_Border.ipynb` | Import/Export CH↔DE/AT/IT/FR – empirische Validierung |
| K_03 | `K_03_Marktdynamik.ipynb` | Spread-Trend 2023–2026, CAPEX-Lernkurven bis 2035 |
| K_04 | `K_04_Animationen.ipynb` | Animierte GIFs: Spread, Netzlast, Arbitrage-Fenster (52 KW) |
| K_05 | `K_05_Revenue_Stacking.ipynb` | FCR/aFRR, VPP, Smart Tariff – Erlösquellen neben Arbitrage |
| K_06 | `K_06_Dispatch_Optimierung.ipynb` | DA-optimal vs. reaktiv, C-Rate-Sensitivität |
| K_07 | `K_07_Technologievergleich.ipynb` | LFP vs. NMC vs. Redox-Flow vs. CAES – CAPEX-Lernkurven |
| K_08 | `K_08_Alternative_Speicher.ipynb` | Pumpspeicher, CAES, Power-to-X im CH-Kontext |
| K_09 | `K_09_Eigenverbrauch.ipynb` | HT/NT-Optimierung als Alternative zur Grid-Arbitrage |
| K_10 | `K_10_Produkt_Steckbrief.ipynb` | Produktsteckbrief: konkreter Heimspeicher-Business-Case |
| K_99 | `K_99_Kombinierte_Simulation.ipynb` | Hybrid-Dispatch: Arbitrage + Eigenverbrauch, 4-Strategie-Vergleich |

---

## Projektstruktur

```
SC26_Gruppe_2/
│
├── sync/
│   ├── config.json          <- SSOT: alle Parameter (User pflegt, Notebooks lesen)
│   ├── transfer.json        <- berechnete Ergebnisse zwischen Notebooks
│   └── dataindex.csv        <- Datenquellen-Register (append-only)
│
├── run_all.bat              <- Windows: alle Notebooks sequenziell ausführen
├── run_all.sh               <- Linux/Mac: alle Notebooks sequenziell ausführen
├── run_all.ps1              <- PowerShell: alle Notebooks sequenziell ausführen
├── requirements.txt
│
├── organisation/            <- Querschnittsdokumente (O_01–O_04, O_99)
├── notebooks/               <- Pflicht-Pipeline (NB01–NB04, NB00)
├── kuer/                    <- Kür-Erweiterungen (K_00–K_10, K_99)
│
├── data/
│   ├── raw/                 <- ENTSO-E CSV, BFE GeoPackage (nicht versioniert)
│   ├── processed/           <- Bereinigte Zeitreihen (NB02-Output)
│   └── intermediate/        <- Simulations- und Analysezwischenergebnisse
│
└── output/
    └── charts/
        └── realistisch/     <- 71 PNG-Charts + 6 GIF-Animationen
```

---

## Setup

### Voraussetzungen

- Python ≥ 3.10
- JupyterLab ≥ 4.0
- ENTSO-E API-Key → [transparency.entsoe.eu](https://transparency.entsoe.eu) (kostenlos registrieren)

### Installation

```bash
# Virtual Environment erstellen (empfohlen)
python -m venv jupyter-env
source jupyter-env/bin/activate        # Linux/Mac
jupyter-env\Scripts\activate.bat       # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### ENTSO-E API-Key konfigurieren

`sync/config.json` öffnen und eintragen:

```json
"api_keys": {
    "entsoe": "DEIN-API-KEY-HIER"
}
```

### Notebooks ausführen

```bash
# Alle Notebooks (Windows)
run_all.bat

# Nur Pflicht-Notebooks
run_all.bat pflicht

# Nur Kür-Notebooks
run_all.bat kuer

# Linux/Mac
bash run_all.sh [all|pflicht|kuer|org]
```

**Ausführungsreihenfolge:** 01 → 02 → 03 → 04 → 00 → K_01 → … → K_99 → K_00

---

## Datensätze

| # | Quelle | Datensatz | Format | Geladen in |
|---|--------|-----------|--------|------------|
| Pflicht  |        |           |        |            |
| DS1 | ENTSO-E | Day-Ahead Spot-Preise CH (2023–heute) | API | 01 |
| DS2 | ENTSO-E | Netzlast CH – stündliche Systemlast | API | 01 |
| Kür  |        |           |        |            |
| DS3 | ENTSO-E | Grenzflüsse CH↔DE/AT/IT/FR | API | K_02 |
| DS4 | BFE/Pronovo | Elektrizitätsproduktionsanlagen (322k) | GeoPackage | K_01 |
| DS5 | BFS | STATPOP – Kantonsbevölkerung | PXWeb API | K_01 |
| DS6 | swisstopo | swissBOUNDARIES3D – Kantonsgrenzen | Shapefile | K_01 |
| DS7 | Our World in Data | CAPEX Li-Ion historisch 1991–2024 | CSV | K_07 |
| DS8 | NREL ATB 2024 | CAPEX-Projektionsszenarien 2022–2050 | CSV (AWS S3) | K_07 |


---

## Kernparameter (`sync/config.json`)

| Parameter | Wert | Beschreibung |
|-----------|------|--------------|
| `mode` | `"data"` | Echte ENTSO-E/BFE-Daten |
| `eur_chf` | `0.97` | Fixkurs März 2026 (alle Berechnungen in EUR) |
| `daten.start_year` | `2023` | Erster Datenjahr |
| `daten.end_year` | `"heute"` | Aktuelles Jahr automatisch |
| `szenarien.gleichzeitigkeit_aktiv` | `realistisch` | 40% Gleichzeitigkeit |
| `pflicht.simulation.efficiency_roundtrip` | `0.92` | Round-Trip-Wirkungsgrad Li-Ion |
| `pflicht.simulation.charge_quantile` | `0.25` | Lade-Schwelle: p25 |
| `pflicht.simulation.discharge_quantile` | `0.75` | Einspeise-Schwelle: p75 |

---

## Team

| Kürzel | Name | Schwerpunkt |
|--------|------|-------------|
| PN | **Patrik Neunteufel** | Domain Expert, System Architect, NB01, K_01, K_00 |
| SE | **Senthuran Elankeswaran** | Financial Reviewer, NB02, NB03, K_02, K_03, K_05 |
| CS | **Cyril Saladin** | Financial Reviewer, NB04, K_07, K_08, K_09 |

**Supervisor:** Maurizio Milazzo · **ZHAW School of Engineering** · März–Mai 2026

---

## Lizenz / Hinweise

- Alle Analysen basieren auf **öffentlich verfügbaren Daten** (ENTSO-E, BFE, BFS, swisstopo, NREL, OWID)
- BloombergNEF (umfassendste CAPEX-Quelle) ist kostenpflichtig — für Investitionsentscheide empfohlen
- Simulationsergebnisse sind Modellwerte; keine Anlageberatung
