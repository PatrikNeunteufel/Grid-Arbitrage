# Phase 2 — Anker-Hygiene

Mechanische Bereinigung aller ID-Anker mit führenden Ziffern und Auflösung
redundanter Doppel-Anker. 8 Notebooks betroffen, 27 Anker umbenannt, 2 entfernt,
19 Links umgebogen.

## Was geändert wurde

### Rename-Operationen (27 Anker)

| Notebook | Alter Anker | Neuer Anker |
|---|---|---|
| `experimental/K_01b` | `3-daten-laden_K_01b` | `daten-laden_K_01b` |
| `experimental/K_01b` | `4-zonenzuweisung_K_01b` | `zonenzuweisung_K_01b` |
| `experimental/K_01b` | `5-bilanzen-bvi_K_01b` | `bilanzen-bvi_K_01b` |
| `experimental/K_01b` | `6-vergleich_K_01b` | `vergleich_K_01b` |
| `experimental/K_01b` | `7-config-doku_K_01b` | `config-doku_K_01b` |
| `kuer/K_01` | `61-heatmap-tages-lastprofil-pro-zone_K_01` | `heatmap-tages-lastprofil-pro-zone_K_01` |
| `kuer/K_02` | `11-entso-e-grenzflüsse-ch-download_K_02` | `entso-e-grenzflüsse-ch-download_K_02` |
| `kuer/K_02` | `12-importexport-analyse-berechnen_K_02` | `importexport-analyse-berechnen_K_02` |
| `kuer/K_02` | `21-kernthese_K_02` | `kernthese_K_02` |
| `kuer/K_02` | `22-ergebnisse_K_02` | `ergebnisse_K_02` |
| `organisation/O_01` | `1-motivation_O_01` | `motivation_O_01` |
| `organisation/O_01` | `2-business-case_O_01` | `business-case_O_01` |
| `organisation/O_01` | `3-datenquellen_O_01` | `datenquellen_O_01` |
| `organisation/O_01` | `4-methodisches-vorgehen_O_01` | `methodisches-vorgehen_O_01` |
| `organisation/O_01` | `46-konfigurationsdateien-configjson-und-transferjson_O_01` | `konfigurationsdateien_O_01` |
| `organisation/O_01` | `5-notebook-map_O_01` | `notebook-map_O_01` |
| `organisation/O_01` | `6-ordner-und-dateistruktur_O_01` | `ordner-und-dateistruktur_O_01` |
| `organisation/O_01` | `7-bewertung-der-datenqualitaet_O_01` | `bewertung-der-datenqualitaet_O_01` |
| `organisation/O_01` | `8-validierung-mittels-simulation_O_01` | `validierung-mittels-simulation_O_01` |
| `organisation/O_01` | `9-einsatz-von-ki-tools_O_01` | `einsatz-von-ki-tools_O_01` |
| `organisation/O_01` | `10-projektplan_O_01` | `projektplan_O_01` |
| `organisation/O_01` | `11-aufgabenverteilung_O_01` | `aufgabenverteilung_O_01` |
| `organisation/O_01` | `12-einreichung_O_01` | `einreichung_O_01` |
| `organisation/O_01` | `13-potenzielle-erweiterungen_O_01` | `potenzielle-erweiterungen_O_01` |
| `organisation/O_03` | `1-hauptabschnitt-nummeriert-mit-fuehrendem-_O_03` | `hauptabschnitt_O_03` |
| `organisation/O_03` | `2-3-markdown-werte_O_03` | `markdown-werte_O_03` |
| `organisation/O_04` | `1-zweck-dieses-dokuments_O_04` | `zweck-dieses-dokuments_O_04` |

### Removal-Operationen (2 Doppelanker aufgelöst)

| Notebook | Entfernter Anker | Redirect auf |
|---|---|---|
| `kuer/K_03` cell 3 | `daten-laden_K_03` (redundant, neben `initialisierung_K_03`) | `initialisierung_K_03` |
| `kuer/K_09` cell 3 | `0-setup_K_09` (redundant, neben `initialisierung_K_09`) | `initialisierung_K_09` |

### Verbliebene erwartete Mehrfach-Anker (kein Bug)

Diese Zellen haben bewusst mehrere Anker und bleiben so:

- `organisation/O_02_Glossar.ipynb` — Glossar-Zellen mit 5–17 `g-*`-Begriffanchors pro Kapitel
- `kuer/K_02_Cross_Border.ipynb` cell 16 — `analyse_K_02` (Haupt-§2) + `kernthese_K_02` (Unter-§2.1)
- `organisation/O_03_Konventionen.ipynb` cell 3 — `markdown-konventionen_O_03` (Haupt-§2) + `hauptabschnitt_O_03` (Anker im Beispielcode-Block, zeigt den neuen Stil)

### Bonus: Dangling Link automatisch behoben

In `organisation/O_04_Review_Protokoll.ipynb` zeigte ein TOC-Link bereits auf
`#zweck-dieses-dokuments_O_04`, während der Anker noch `#1-zweck-...` hiess.
Durch den Rename passen Link und Anker jetzt zusammen.

## Verifikation

- Vor Patch: 27 Anker mit führender Ziffer, 1 dangling link, 4 echte Doppelanker
- Nach Patch: 0 Anker mit führender Ziffer ✅, 0 dangling links ✅, 0 echte Doppelanker ✅
- JSON-Validität aller 8 gepatchten Notebooks: ✅
- Cell-IDs in allen Zellen vorhanden (nbformat 5.1+ compliant): ✅

## Installation

Im Ordner `patched_notebooks/` liegen die 8 geänderten Notebooks in der
Original-Ordner-Struktur. Einfach **ins Projekt drüberkopieren**:

```bash
cd /pfad/zum/projekt
cp -r <diese_ZIP>/patched_notebooks/* .
```

Es werden nur die 8 geänderten Notebooks überschrieben, keine anderen Dateien.

## Verifikation nach Installation

Öffne `organisation/O_01_Project_Overview.ipynb` und klicke ein paar TOC-Links
durch — sie sollten alle auf die richtigen Abschnitte springen. Dasselbe in
`O_04_Review_Protokoll.ipynb` (der Link aus dem TOC sollte jetzt funktionieren,
der vorher dangling war).

Wenn alles passt: **Phase 2 abgeschlossen, weiter mit Phase 3** (Struktur-
Harmonisierung Einleitung/Fazit/Abschluss).

## Nicht angefasst

- Phase 1 hat bereits `lib/` und `organisation/O_00_Installer.ipynb` +
  `test/Test_Phase1.ipynb` geliefert. Die sind hier nicht nochmals enthalten.
- `K_01d_Grid_Topologie_slider.ipynb` wird in Phase 3d als
  `experimental/K_01d_Grid_Topologie.ipynb` integriert — dort dann auch
  Anker-Check neu.
