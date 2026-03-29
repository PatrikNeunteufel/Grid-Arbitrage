# Projektjournal — Grid-Arbitrage mit Batteriespeichern (CH)

**SC26_Gruppe_2** · Patrik Neunteufel · Senthuran Elankeswaran · Cyril Saladin  
CAS Information Engineering Scripting, ZHAW · Supervisor: Maurizio Milazzo  
Abgabe: 11. Mai 2026 · Stand: 28. März 2026

---

## 1. Zweck und Aufbau

Dieses Dokument hält alle wesentlichen Stolpersteine, Bugs, Fehlanalysen und Designentscheide fest, die im Verlauf der Projektarbeit (Februar–März 2026) entstanden und behoben wurden. Es dient als strukturiertes Gedächtnis für den Restart-All-Lauf am 09.05.2026 sowie als Referenz für zukünftige Jahresauswertungen.

---

## 2. Methodische Fehler

### 2.1 ROI-Überbewertung durch Jan+Feb × 12 ⚠️ kritisch

| | |
|---|---|
| **Art** | Systematische methodische Fehlschätzung |
| **Entdeckt** | Chat «Jupyter notebook für datensatz lesen», März 2026 |
| **Auswirkung** | ROI ca. 3–5× überschätzt — Privat 10 kWh erschien mit ~5.5 % rentabel statt ~0.4 % |

**Was passierte:**  
Die Dispatch-Simulation wurde ausschliesslich über Januar und Februar durchgeführt und der Erlös dieser zwei Monate mit Faktor 12 auf ein Jahresäquivalent hochgerechnet. Die implizite Annahme war, dass alle Monate gleich sind. Diese Annahme ist falsch: Winter hat strukturell 3–5× höhere Intraday-Spreads als Sommer (Duck-Curve-Effekt im Frühling/Sommer; niedrige Volatilität im Hochsommer 2023/2024 nach dem Energiekrisen-Peak 2022).

**Korrektur:**  
Simulation auf alle 24 Monate (2023 + 2024) ausgeweitet; Jahreserlös = Summe / 2. Die korrekten Werte zeigen: Reine Grid-Arbitrage erreicht bei CH-Preisen 2023/2024 für kein Segment das 5%-ROI-Ziel. Das ist kein Fehler im Modell — es ist der reale Befund.

**Folgerungen und Designentscheid:**
- Methodologische Korrektur in NB00 Sektion 4b dokumentiert (permanente Referenz)
- NB04 Fazit-Text komplett neu geschrieben: kein Segment «klar rentabel» mehr
- Business Strategy Sektion 7 (VPP/Grid Services) rückt vom Anhang zum Kernstück
- Gleichzeitigkeits-Schalter (optimistisch 70 % / realistisch 40 %) als `config.json`-Parameter eingeführt
- Datenzeitraum von `config.json` steuerbar (`"heute"` als Endwert) — jährlicher Rerun möglich

---

### 2.2 Analysetext NB04 widersprach den eigenen Charts

| | |
|---|---|
| **Art** | Inhaltlicher Fehler — beschreibender Text vs. visuelle Daten |
| **Auswirkung** | Text behauptete Winter hätte höchsten Spread; Chart zeigte Frühling als Maximum |

**Was passierte:**  
Der ursprüngliche Analysetext in NB04 war nicht aus den echten Chartdaten abgeleitet, sondern auf Basis einer intuitiven Annahme (Winter = hohe Spreads) verfasst. Die tatsächlichen Werte laut Chart 5a:

| Jahreszeit | Spread [EUR/MWh] | Rang |
|---|---|---|
| Frühling | ~139 | 1 (höchster) |
| Herbst | ~120 | 2 |
| Sommer | ~100 | 3 |
| Winter | ~85 | 4 (niedrigster) |

**Korrektur und Folgerung:**
- Gesamter Analysetext NB04 neu geschrieben — alle konkreten Zahlenwerte aus Chart-Daten abgelesen
- Chart 5a auf einheitliche Y-Achsen aller saisonalen Panels umgestellt (verhindert visuelle Fehlinterpretation)
- **Lektion:** Beschreibungstexte nie aus dem Gedächtnis ableiten — immer aus den tatsächlichen Outputs

---

## 3. Code-Bugs

### 3.1 `portal_ok = False` bei HTTP 503 — Download-Blockade

| | |
|---|---|
| **Notebook** | NB01 Daten_Laden |
| **Symptom** | ENTSO-E-Download bricht ab, obwohl Server nur temporär überlastet ist |

**Ursache:**  
Der Connectivity-Check pingte `transparency.entsoe.eu` (die Webseite, gibt HTTP 200 zurück) statt den eigentlichen API-Endpunkt `web-api.tp.entsoe.eu`. Zusätzlich setzte die Logik `portal_ok = False` bei jedem Statuscode ≥ 400 — also auch bei 503. Das `entsoe-py` Retry-Decorator fängt nur `ConnectionError/gaierror` ab, nicht `HTTPError 503`.

**Korrekturen:**
- Connectivity-Check pingt jetzt `web-api.tp.entsoe.eu`
- `portal_ok = True` auch bei 400 und 401 (Server erreichbar, nur fehlende/ungültige Parameter)
- 503-Retry-Logik: bis zu 3 Versuche, 20 Sekunden Wartezeit
- Jahresweiser Download statt eines einzigen grossen Requests
- Kein `raise RuntimeError` mehr — graceful degradation mit Fallback auf NB01b (Simulationsdaten)

---

### 3.2 KeyError: `CFG['szenarien']['gleichzeitigkeit']` in NB06

| | |
|---|---|
| **Notebook** | NB06 BFE GeoPackage |
| **Symptom** | 24 Cascade-Fehler ausgehend von einem einzigen KeyError im Root-Abschnitt |

**Ursache:**  
NB06 versuchte auf `CFG['szenarien']['gleichzeitigkeit']` zuzugreifen. Der korrekte Key in `config.json` ist `gleichzeitigkeit_aktiv`. Da die Root-Zelle fehlschlug, schlugen alle nachfolgenden 23 Zellen ebenfalls fehl.

**Korrektur:**
- Key auf `CFG['gleichzeitigkeit_aktiv']` korrigiert
- **Lektion:** Root-Zellen-Fehler erzeugen lange Fehlerkaskaden — immer zuerst den ersten Fehler im Stack beheben

---

### 3.3 `CFG['wirtschaftlichkeit']` statt `CFG['pflicht']['wirtschaftlichkeit']`

| | |
|---|---|
| **Notebook** | NB03 Visualisierungen |
| **Symptom** | KeyError beim Laden des Wirtschaftlichkeits-CSV |

**Ursache:**  
Die verschachtelte `config.json`-Struktur hatte `wirtschaftlichkeit` unter dem `pflicht`-Schlüssel. NB03 griff direkt auf die Root-Ebene zu.

**Korrektur:** Zugriffspfad auf `CFG['pflicht']['wirtschaftlichkeit']` korrigiert.

---

### 3.4 Abschluss-Check: `> 1000 Bytes` für kleine CSV-Dateien

| | |
|---|---|
| **Notebook** | NB01 Daten_Laden |
| **Symptom** | Abschlusskontrolle meldet «fehlgeschlagen» für valide aber kleine Output-Dateien |

**Ursache:**  
Der Byte-Schwellenwert `> 1000` war pauschal gesetzt. Eine 4-zeilige Summary-CSV ist valide bei ~280 Bytes und fiel dennoch durch.

**Korrektur:**
- Schwellenwert pro Dateityp konfigurierbar gemacht (`min_kb = 0.1` statt `1.0` für kleine CSVs)
- **Lektion:** Validierungsgrenzen müssen den legitimen Kleinstfällen Rechnung tragen

---

### 3.5 O(n²) Dispatch-Simulation mit `iterrows`

| | |
|---|---|
| **Notebook** | NB02 Daten_Analyse (Dispatch-Zelle) |
| **Symptom** | Laufzeit mehrere Minuten für 17 520 Stunden × 4 Segmente |

**Ursache:**  
Die ursprüngliche Dispatch-Simulation iterierte zeilenweise über den DataFrame (`iterrows`), was O(n²)-Verhalten erzeugte.

**Korrektur:**
- Vollständiger Umbau auf O(n): Vorab-Berechnung der Tagesquantile (p25/p75 je Tag) als NumPy-Array
- Vektorisierte NumPy-Simulation statt `iterrows`
- Speedup: **~190×** (gemessen)
- Fortschrittsbalken nach Optimierung entfernt — Laufzeit zu kurz um sinnvoll

---

### 3.6 matplotlib Axes-Kopieren schlägt fehl (Panel-PNGs)

| | |
|---|---|
| **Notebook** | NB03 Visualisierungen |
| **Symptom** | Einzel-Panel-PNGs für Berichtseinbettung konnten nicht via Axes-Referenz erzeugt werden |

**Ursache:**  
Matplotlib erlaubt kein Kopieren von Axes-Objekten in neue Figures. Für Charts mit twin axes (doppelte Y-Achse), `fill_between` und Legenden war direktes Achsen-Kopieren nicht möglich.

**Korrektur und Designentscheid:**
- Einzel-Panels werden via **Daten-Reproduktion** erzeugt: gleiche Plotting-Logik, aber nur ein Panel pro Figure
- Konvention: Alle Multi-Panel-Charts müssen zusätzlich Einzel-Panel-PNGs speichern (für Bericht-Einbettung)
- In NB00b Sektion 1.5 als verbindliche Konvention dokumentiert

---

### 3.7 crossborder-Download-Code verloren gegangen

| | |
|---|---|
| **Notebooks** | NB01 → NB03 |
| **Symptom** | NB03 referenzierte `ch_crossborder_raw.csv`; NB01 enthielt nur den `FORCE_RELOAD`-Key, keinen Download-Code |

**Was passierte:**  
Der Download-Code für ENTSO-E Grenzflussdaten (CH↔DE, AT, IT, FR) war in einem früheren Chat im Generator-Script erzeugt worden, aber nie korrekt ins finale NB01 übertragen worden. Der Key `'crossborder': False` in `FORCE_RELOAD` war noch vorhanden — das war das einzige Überbleibsel.

**Korrektur:**
- DS3 (ENTSO-E Grenzflüsse) als separater Abschnitt in NB01 eingebaut (nach DS2 Netzlast)
- Berechnung `net_export_mw = Summe Export − Import` aller 4 Grenzen
- Optional markiert — NB07-Analyse läuft auch ohne Grenzfluss-Daten
- **Lektion:** Code-Übertrag aus Generator-Scripts immer explizit im Ziel-Notebook verifizieren

---

### 3.8 `import os` zerschnitt `import os, pandas as pd`

| | |
|---|---|
| **Notebook** | NB04 Business Case |
| **Symptom** | `NameError: name 'pd' is not defined` nach config.json-Umbau |

**Ursache:**  
Der `str_replace`-Schritt, der `import os` durch `import os` + `import json` ersetzte, traf die Zeile `import os, pandas as pd` und erzeugte:

```python
import os
import json as _json
, pandas as pd   # ← ungültiger Syntaxrest
```

**Korrektur:**
- Imports in beide NB04-Dateien als saubere separate Zeilen eingefügt
- **Lektion:** `str_replace` auf Import-Zeilen mit komma-separiertem Inhalt zuerst prüfen

---

### 3.9 Chart 3 `_single`: doppelter Quantil

| | |
|---|---|
| **Notebook** | NB03 Visualisierungen |
| **Symptom** | `_single`-Panel zeigte praktisch keine Preiszonen (fast unsichtbare Färbung) |

**Ursache:**  
Die Zonen-Logik für den Einzel-Panel-Plot verwendete `p25.quantile(0.25)` — ein Quantil der 24 stündlichen p25-Werte. Das ist ein doppelter Quantil, der einen extrem engen Bereich erzeugt. Der Composit-Chart verwendete korrekt `nsmallest(4)` / `nlargest(4)`.

**Korrektur:** `_single`-Logik auf identische `nsmallest/nlargest`-Methode wie der Composit umgestellt.

---

### 3.10 ENTSO-E API-Key hardcoded in NB07

| | |
|---|---|
| **Notebook** | NB07 Import/Export-Analyse |
| **Symptom** | API-Key als Klartext im Notebook — SSOT-Verletzung |

**Korrektur und Designentscheid:**
- API-Key aus NB07 entfernt; liegt jetzt ausschliesslich in `config.json` unter `api_keys.entsoe`
- NB01 und NB07 lesen via `CFG.get('api_keys', {}).get('entsoe', '')`
- Konvention in NB00b Sektion 5.3 dokumentiert
- Ein Key pro Account reicht für das gesamte Team; das heruntergeladene CSV ist im Abgabe-ZIP enthalten — Professor und Teamkollegen brauchen keinen eigenen Key

---

### 3.11 swissBOUNDARIES3D: falsches Format / falsche URL

| | |
|---|---|
| **Notebooks** | NB05 Räumliche Analyse + 3 Hilfs-Notebooks |
| **Symptom** | Download-Fehler, geopandas konnte Datei nicht öffnen |

**Ursache:**  
Das ursprünglich verwendete Format war direkt GPKG. swisstopo liefert swissBOUNDARIES3D 2026 als ZIP-Archiv mit enthaltener GPKG-Datei. Zusätzlich müssen Layer explizit via `gpd.list_layers()` selektiert werden.

**Korrektur:**
- Download auf ZIP-Format umgestellt: `swissboundaries3d_2026-01_2056_5728.gpkg.zip`
- Entpacken mit `zipfile`, Layer-Selektion via `gpd.list_layers()` vor `read_file()`
- Gleiches Pattern in alle drei betroffenen Hilfs-Notebooks übertragen

---

### 3.12 Animations-Errorbar: negative `yerr`-Werte

| | |
|---|---|
| **Notebook** | NB03 Visualisierungen, Chart 3 Option B |
| **Symptom** | `ValueError: yerr must be non-negative` bei der saisonalen Animation |

**Ursache:**  
Der untere Fehlerbalken wurde als `p25 − StdDev` berechnet. Wenn `StdDev > p25` (möglich bei schiefen Preisverteilungen), wurde `yerr` negativ.

**Korrektur:** `max(0, p25 − std)` statt direktes `p25 − std`.

---

### 3.13 `requests`-Import fehlte nach geopandas-Entfernung

| | |
|---|---|
| **Notebook** | NB01 Daten_Laden |
| **Symptom** | `NameError: name 'requests' is not defined` |

**Ursache:**  
`requests` war implizit via `geopandas` verfügbar. Als `geopandas` aus NB01 entfernt wurde (gehört in NB05/NB06), fiel der transitive Import weg.

**Korrektur:** `import requests` explizit in NB01 Setup-Zelle hinzugefügt.

---

## 4. Architektur- und Designentscheide

### 4.1 `config.json` als Single Source of Truth (SSOT)

Alle konfigurierbaren Parameter (MODE, FORCE_RELOAD, Simulationsparameter, ökonomische Parameter, Datumsbereiche, API-Key) leben ausschliesslich in `config.json`. Jedes Notebook liest via:

```python
with open('config.json') as f:
    CFG = json.load(f)
```

Hardcoded Werte und standalone config-Dicts in einzelnen Notebooks gelten als Verletzung und werden entfernt.

**Begründung:**
- Verhindert Inkonsistenzen beim jährlichen Rerun (nur `config.json` anpassen)
- ENTSO-E API-Key an einem Ort; kein versehentliches Committen in mehreren Notebooks
- Schalter (Gleichzeitigkeit, MODE, FORCE_RELOAD) sofort auffindbar

---

### 4.2 Pflicht/Kür-Trennung als nicht-verhandelbare Architekturgrenze

NB01–NB04 enthalten ausschliesslich Pflichtinhalt. Kür-Datensätze und Kür-Visualisierungen werden im ersten Notebook geladen, das sie tatsächlich benötigt:

| Notebook | Erstmaliges Kür-Laden |
|---|---|
| NB06 | BFE GeoPackage |
| NB07 | ENTSO-E Grenzflüsse, Import/Export-Analyse |

Entfernte Verletzungen: Chart 6 (Import/Export) aus NB03, saisonale Animationen A/B/C aus NB03, Charts 7 und 8 aus NB03 (lagen bereits in NB08).

---

### 4.3 Per-Szenario Chart-Speicherung

`CHARTS_DIR` ist definiert als `os.path.join('output', 'charts', SZ_AKTIV)`. Alle Charts landen in einem szenarienspezifischen Unterordner. Gleiches Muster für `DIR_INTER_SZ`.

**Begründung:** Verschiedene Szenario-Läufe überschreiben sich nicht gegenseitig; Bericht kann Charts aus spezifischen Szenarien referenzieren.

---

### 4.4 Gleichzeitigkeits-Schalter in `config.json`

Zwei Modi: `optimistisch` (70 % — koordinierter VPP-Dispatch) und `realistisch` (40 % — unkoordinierter Markt). Default: `realistisch`. Business Case und Business Strategy lesen den gesetzten Wert automatisch.

**Begründung:** Wissenschaftlich sauber, Annahme transparent und im Bericht sichtbar. Vermeidet eine zweite Szenario-Dimension, die zu viel Komplexität erzeugen würde.

---

### 4.5 Einzel-Panel-PNGs neben Multi-Panel-Charts

Jedes Multi-Panel-Chart muss zusätzlich jedes Panel als separates PNG speichern. Technische Umsetzung via Daten-Reproduktion (nicht matplotlib Axes-Kopieren — funktioniert nicht für twin axes, fill_between, Legenden).

**Begründung:** LaTeX/Word-Berichte können aus einem Multi-Panel-PNG keine einzelnen Panels extrahieren.

---

### 4.6 Einheitliche Y-Achsen bei saisonalen Panel-Charts (Chart 5a)

Chart 5a (saisonaler Spread) verwendet dieselbe Y-Achsen-Skalierung für alle vier Jahreszeiten-Panels.

**Begründung:** Autoskalierung je Panel verschleiert Grössenunterschiede zwischen Jahreszeiten — genau dieser Unterschied (Frühling > Winter) ist der Kernbefund.

---

## 5. Dokumentierte Konventionen (NB00b)

| Sektion | Konvention | Inhalt |
|---|---|---|
| 1.5 | Kür-Datenladen | Kür-Notebooks laden eigene Daten in Sektion 1; kein Laden in NB01–NB04 |
| 5.3 | API-Key-Konvention | Einzige Quelle: `config.json › api_keys.entsoe` |
| 5 | Parameter-Referenz | Vollständige Tabelle aller `config.json`-Keys mit Defaults und Beschreibungen |
| 5b | ENTSO-E Stolperfallen | Rate Limits, Lückfälle, Zeitzonenwechsel, 503-Verhalten |

---

## 6. Bekannte Einschränkungen des Modells (transparent dokumentiert)

### 6.1 Tagesbasierte Quantile = perfekte Preiskenntnis
Die Simulation nimmt an, dass die Batterie zu Beginn jeder Stunde die günstigsten und teuersten Stunden des Tages kennt. In der Realität wäre das eine Vorhersage (DA-Preise erscheinen erst am Vortag). Diese Einschränkung ist explizit in NB00 dokumentiert.

### 6.2 C-Rate-Asymmetrie
Privat (10 kWh) lädt mit 0.5C (2 Stunden Vollladung), Utility (10 MWh) mit 0.1C (10 Stunden). Das begrenzt die realisierbaren Zyklen pro Tag.

### 6.3 Datenzeitraum 2023/2024 ist ein historisch flacher Markt
Nach dem Energiekrisen-Peak 2022 waren CH-Day-Ahead-Preise 2023/2024 historisch normalisiert. Die Befunde gelten spezifisch für diesen Zeitraum. Die Jährliche-Rerun-Funktion erlaubt es, neue Zeiträume automatisch einzubeziehen.

---

## 7. Destillierte Lektionen

| Lektion | Anwendung |
|---|---|
| Root-Fehler zuerst beheben | Kaskaden entstehen durch einen einzigen KeyError im Setup |
| Text aus Daten ableiten, nicht aus Intuition | Winter-Spread-Fehler wäre durch Lesen des eigenen Charts vermeidbar gewesen |
| Stichproben-Repräsentativität prüfen | Jan+Feb repräsentieren nicht das Jahr — erzeugte 3–5× ROI-Überbewertung |
| `str_replace` auf Mehrimport-Zeilen prüfen | `import os, pandas as pd` zerschnitten durch `replace('import os', ...)` |
| Code-Übertrag aus Generator verifizieren | crossborder-Download-Code war nur im Generator, nie im Notebook |
| Validierungsgrenzen kontextabhängig setzen | 4-Zeilen-CSV ist valide bei 280 Bytes — pauschal > 1000 ist falsch |
| Realistischer Befund > schöner Befund | ROI < 5 % ist der ehrliche Befund und stärkt die VPP-Argumentation |
| Scope bewusst klein halten | Jede neue Dimension (Szenarien, Jahreszeiten) multipliziert Komplexität |

---

## 8. Noch offene Punkte (Stand 28.03.2026)

| Aufgabe | Zieldatum | Bemerkung |
|---|---|---|
| NB11 Technologievergleich erstellen | April 2026 | LFP/NMC/Redox/CAES; Tabelle in NB08 als Vorlage |
| NB12 Alternative Speicher erstellen | April 2026 | Pump-Hydro, CAES, thermischer Speicher |
| Business Case Zahlen nachziehen | Nach ENTSO-E Download | 5.5 % / 18 Jahre stimmen nicht mehr — auf echte Simulationswerte updaten |
| Restart-All Review | 09.05.2026 | Alle 16 Notebooks sequenziell von Kernel neu |
| ZIP für Abgabe erstellen | 10.05.2026 | inkl. heruntergeladenem ENTSO-E CSV |
| Moodle-Abgabe | **11.05.2026** | Deadline |

---

*Projektjournal — SC26_Gruppe_2 — CAS IE Scripting ZHAW — 2026*
