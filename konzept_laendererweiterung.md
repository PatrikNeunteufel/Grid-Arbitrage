# Konzept: Ländererweiterung Grid-Arbitrage — DACH + Europa

**Status:** Potenzielle Erweiterung — nicht Teil der aktuellen Abgabe  
**Scope:** DE, AT, CH (DACH) + alle ~30 ENTSO-E-Mitgliedsländer (Europa)

---

## 1. Grundidee

Das Projekt ist bereits weitgehend parametrisierbar. Eine Ländererweiterung
erfordert hauptsächlich drei Dinge:

1. **`config.json`**: Land als Parameter + Datenquellen-URLs je Land
2. **NB01**: Bidding-Zone-Code dynamisch statt `'CH'` hardcoded
3. **NB06**: Geodaten-Quellen länderspezifisch — verbleibende manuelle Arbeit

**Wichtige Erkenntnis:** ENTSO-E ist der Dachverband aller europäischen
Übertragungsnetzbetreiber. Die Transparency Platform deckt ~30 Länder ab.
`entsoe-py` abstrahiert alle über denselben API-Call — nur der Bidding-Zone-Code
ändert sich. Damit sind **NB01–NB05 und NB07 für ganz Europa generisch**, sobald
die Bidding-Zone-Tabelle in `config.json` gepflegt ist. NB06 bleibt der einzige
echte länderspezifische Aufwand.

---

## 2. Vorgeschlagene config.json-Erweiterung

```json
"land": {
  "_hint": "Aktives Analyiseland. Umschalten → NB01–NB07 neu ausführen.",
  "aktiv": "CH",
  "_hint_aktiv": "DACH: 'CH' | 'DE' | 'AT' — Europa: beliebiger Code aus entsoe_bidding_zones",

  "optionen": {

    "CH": {
      "label": "Schweiz",
      "entsoe_bidding_zone": "10YCH-SWISSGRIDZ",
      "entsoe_country_code": "CH",
      "waehrung": "EUR",
      "preise_url": "https://transparency.entsoe.eu",
      "statistik": {
        "bevoelkerung_url": "https://www.bfs.admin.ch/bfs/de/home/statistiken/bevoelkerung.html",
        "bevoelkerung_api": "https://www.pxweb.bfs.ch/api/v1/de/px-x-0102010000_101",
        "geodaten_url": "https://data.geo.admin.ch/ch.swisstopo.swissboundaries3d/",
        "produktion_url": "https://data.geo.admin.ch/ch.bfe.elektrizitaetsproduktionsanlagen/",
        "_note": "BFS PXWeb-API + swisstopo swissBOUNDARIES3D — bereits implementiert"
      },
      "regulierung": {
        "netzgebiet": "Swissgrid",
        "flexmarkt_url": "https://www.swissgrid.ch/de/home/customers/topics/ancillary-services.html"
      }
    },

    "DE": {
      "label": "Deutschland",
      "entsoe_bidding_zone": "10Y1001A1001A83F",
      "entsoe_country_code": "DE",
      "waehrung": "EUR",
      "preise_url": "https://transparency.entsoe.eu",
      "statistik": {
        "bevoelkerung_url": "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung",
        "bevoelkerung_api": "https://www-genesis.destatis.de/api/v2.2/",
        "_hint_api": "GENESIS-Online REST API — kostenlos, kein Key nötig für Basisdaten",
        "geodaten_url": "https://gdz.bkg.bund.de/index.php/default/digitale-geodaten/verwaltungsgebiete.html",
        "_hint_geo": "BKG VG250 Gemeindegrenzen (GeoPackage/Shapefile) — entspricht swisstopo",
        "produktion_url": "https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/ErneuerbareEnergien/ZahlenDaten/start.html",
        "_hint_prod": "Marktstammdatenregister (MaStR) — REST API, vollständiges Anlagenregister"
      },
      "regulierung": {
        "netzgebiet": "50Hertz / Amprion / TenneT / TransnetBW",
        "flexmarkt_url": "https://www.regelleistung.net"
      }
    },

    "AT": {
      "label": "Österreich",
      "entsoe_bidding_zone": "10YAT-APG------L",
      "entsoe_country_code": "AT",
      "waehrung": "EUR",
      "preise_url": "https://transparency.entsoe.eu",
      "statistik": {
        "bevoelkerung_url": "https://www.statistik.at/statistiken/bevoelkerung-und-soziales/bevoelkerung",
        "bevoelkerung_api": "https://data.statistik.gv.at/web/meta.jsp",
        "_hint_api": "Statistik Austria Open Data — SDMX/JSON API",
        "geodaten_url": "https://data.statistik.gv.at/web/meta.jsp?dataset=OGDEXT_GEM_1",
        "_hint_geo": "BEV Gemeindegrenzen via Open Government Data Austria",
        "produktion_url": "https://www.e-control.at/statistik/strom/betriebsstatistik"
      },
      "regulierung": {
        "netzgebiet": "APG (Austrian Power Grid)",
        "flexmarkt_url": "https://www.apg.at/markt/regelenergie"
      }
    }
  },

  "_section_europa": "Für Europa-Erweiterung: Bidding-Zone-Tabelle und Eurostat-API",

  "entsoe_bidding_zones": {
    "_hint": "Vollständige ENTSO-E Bidding-Zone-Codes. Quelle: transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html",
    "FR": "10YFR-RTE------C",
    "ES": "10YES-REE------0",
    "PT": "10YPT-REN------W",
    "IT_NORD": "10Y1001A1001A73I",
    "IT_CNORD": "10Y1001A1001A70O",
    "IT_SUD": "10Y1001A1001A788",
    "IT_CSUD": "10Y1001A1001A71M",
    "IT_SIC": "10Y1001A1001A76C",
    "IT_SAR": "10Y1001A1001A74G",
    "NL": "10YNL----------L",
    "BE": "10YBE----------2",
    "LU": "10YLU-CEGEDEL-NQ",
    "PL": "10YPL-AREA-----S",
    "CZ": "10YCZ-CEPS-----N",
    "SK": "10YSK-SEPS-----K",
    "HU": "10YHU-MAVIR----U",
    "RO": "10YRO-TEL------P",
    "SI": "10YSI-ELES-----O",
    "HR": "10YHR-HEP------M",
    "RS": "10YCS-SERBIATSО",
    "BG": "10YCA-BULGARIA-R",
    "GR": "10YGR-HTSO-----Y",
    "DK_W": "10YDK-1--------W",
    "DK_E": "10YDK-2--------M",
    "NO_1": "10YNO-1--------2",
    "NO_2": "10YNO-2--------T",
    "NO_3": "10YNO-3--------J",
    "NO_4": "10YNO-4--------9",
    "NO_5": "10Y1001A1001A48H",
    "SE_1": "10Y1001A1001A44P",
    "SE_2": "10Y1001A1001A45N",
    "SE_3": "10Y1001A1001A46L",
    "SE_4": "10Y1001A1001A47J",
    "FI": "10YFI-1--------U",
    "EE": "10Y1001A1001A39I",
    "LV": "10YLV-1001A00074",
    "LT": "10YLT-1001A0008Q",
    "GB": "10YGB----------A",
    "_hint_GB": "UK nicht EUR — Währungsumrechnung nötig (GBP)",
    "_hint_IT": "Italien hat 6 Preis-Zonen (Nord/CentroNord/CentroSud/Sud/Sicilia/Sardegna)",
    "_hint_NO_SE": "Norwegen/Schweden haben je 4–5 Preis-Zonen (regionale Engpässe)"
  },

  "eurostat": {
    "_hint": "Eurostat REST API — einheitliche Bevölkerungs- und Energiedaten für alle EU-Länder",
    "api_base": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/",
    "bevoelkerung_dataset": "demo_pjan",
    "_hint_bev": "Annual population by sex and age — alle EU/EEA Länder, NUTS-2 Regionen",
    "bevoelkerung_url": "https://ec.europa.eu/eurostat/databrowser/view/demo_pjan",
    "energie_dataset": "nrg_ind_peh",
    "_hint_energie": "Strom-Endverbrauch nach Sektor — alle EU-Länder",
    "energie_url": "https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_peh",
    "nuts_geodaten_url": "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2021_4326.geojson",
    "_hint_nuts": "NUTS-2 Regionsgrenzen für ganz Europa als GeoJSON — direkt in geopandas ladbar"
  }
}
```

---

## 3. Code-Änderungen je Notebook

### NB01 — Daten laden

```python
# Setup: Land aus config
_land    = CFG.get('land', {})
_aktiv   = _land.get('aktiv', 'CH')
_opt     = _land['optionen'][_aktiv]

BZ_CODE  = _opt['entsoe_bidding_zone']   # statt '10YCH-SWISSGRIDZ'
CC_CODE  = _opt['entsoe_country_code']   # statt 'CH'
WAEHRUNG = _opt.get('waehrung', 'EUR')

# Preise laden: einzige Änderung
ts = client.query_day_ahead_prices(BZ_CODE, ...)   # statt 'CH'
# Netzlast:
ts = client.query_load(CC_CODE, ...)               # statt 'CH'
```

### NB06 — Räumliche Analyse (grösste manuelle Arbeit)

| Schritt | CH (heute) | DE | AT | Europa generisch |
|---------|-----------|----|----|-----------------|
| Regionsgrenzen | swisstopo GeoPackage | BKG VG250 | BEV GEM | **Eurostat NUTS-2 GeoJSON** |
| Bevölkerung | BFS PXWeb API | GENESIS API | Statistik Austria API | **Eurostat `demo_pjan`** |
| Produktionsanlagen | BFE GeoPackage | MaStR API | E-Control CSV | kein EU-Register — länderspezifisch |
| Projektion | EPSG:2056 (LV95) | EPSG:25832 (UTM32N) | EPSG:31258 (MGI/AUT) | **EPSG:4326 (WGS84)** |

→ **Aufwand**: Die Lade-Logik muss je Land differenziert werden. Empfehlung: eigene
`_load_geodaten_{land}.py`-Hilfsfunktion oder bedingte Blöcke im Notebook.

### NB07 — Cross-Border (bereits parametrisiert)

`NEIGHBORS` wird bereits aus `CFG['kuer']['crossborder']['nachbarn']` gelesen —
bei DE würden andere Nachbarn relevant: `["AT","CH","FR","DK","PL","CZ","NL","LU","BE"]`

### NB02–NB05 — Keine Änderung nötig

Alle Berechnungen verwenden EUR/MWh (ENTSO-E-Standard) und sind
segment-generisch. Nur Labeling (`'CH'` in Titel) müsste angepasst werden.

---

## 4. Umsetzungsaufwand DACH (Schätzung)

| Komponente | Aufwand | Bemerkung |
|---|---|---|
| config.json Erweiterung | 1h | strukturell fertig (s. oben) |
| NB01: BZ/CC dynamisieren | 1h | 2–3 Zeilen pro Dataset |
| NB07: Nachbarn anpassen | ½h | bereits parametrisiert |
| NB06 DE: Geodaten + MaStR | 2–3 Tage | andere API, andere Projektion |
| NB06 AT: Geodaten | 1–2 Tage | ähnlich DE, kleinere Datenmenge |
| NB04/05: Labeling | ½h | Titel/Kommentare |
| **Total CH→DE** | **~3–4 Tage** | Hauptaufwand NB06 |

---

## 5. Nicht-parametrisierbare Aspekte (DACH)

- **BFS-Daten**: CH-spezifisch (26 Kantone, PXWeb-Format). DE hat 16 Bundesländer
  mit GENESIS-API, AT 9 Bundesländer mit SDMX. Unterschiedliche Granularität und
  API-Struktur → manuelle Anpassung der Aggregationslogik.
- **Engpasslinien** (NB06): hardcoded Koordinaten (`ENGPASSLINIEN`-Liste) — müssen
  je Land neu definiert werden (Swissgrid → APG / 50Hertz etc.)
- **Tarif-Modell** (NB13): HT/NT-Zeiten und Tarifniveau sind länderspezifisch.
  DE hat SmartMeter-Rollout mit anderen Zeitfenstern, AT ähnlich CH.
- **Währung**: alle drei DACH-Länder nutzen EUR → kein FX-Problem.

---

## 6. Europa-Erweiterung

### 6.1 Was ENTSO-E abdeckt

ENTSO-E ist der Verbund aller europäischen Übertragungsnetzbetreiber (TSO) und
verpflichtet zur Datenpublikation auf der Transparency Platform. Über `entsoe-py`
sind folgende Länder mit demselben API-Call erreichbar — nur der Bidding-Zone-Code
ändert sich:

| Region | Länder | Besonderheiten |
|--------|--------|---------------|
| DACH | DE, AT, CH | Eine Zone je Land; EUR |
| Westeuropa | FR, ES, PT, NL, BE, LU | Eine Zone je Land; EUR |
| Nordics | DK×2, NO×5, SE×4, FI | Mehrere Preis-Zonen je Land |
| Osteuropa | PL, CZ, SK, HU, RO, BG | Eine Zone je Land; EUR |
| Balkan | SI, HR, RS, GR | Teilweise Datenlücken |
| Baltikum | EE, LV, LT | Eine Zone je Land; EUR |
| UK | GB | GBP — Währungsumrechnung nötig |
| Italien | IT×6 | 6 Preis-Zonen (Nord bis Sizilien) |

→ Die vollständige Bidding-Zone-Tabelle ist in `config.json` unter
`entsoe_bidding_zones` hinterlegt (s. Abschnitt 2).

### 6.2 NB01–NB05 und NB07: generisch für ganz Europa

Sobald `BZ_CODE` und `CC_CODE` aus `config.json` gelesen werden (s. Abschnitt 3),
laufen diese Notebooks für jedes ENTSO-E-Land ohne weitere Anpassung:

```python
# Beispiel: Frankreich statt Schweiz — einzige Änderung in config.json:
# "aktiv": "FR"
# "entsoe_bidding_zone": "10YFR-RTE------C"
# "entsoe_country_code": "FR"

ts = client.query_day_ahead_prices(BZ_CODE, start=start, end=end)  # funktioniert für alle
ts = client.query_load(CC_CODE, start=start, end=end)              # funktioniert für alle
```

Länder mit mehreren Zonen (NO, SE, IT) brauchen eine zusätzliche Auswahl:

```python
# config.json: "entsoe_bidding_zone": "10Y1001A1001A73I"  (IT Nord)
# oder alle Zonen laden und aggregieren:
# "entsoe_bidding_zones_multi": ["10Y1001A1001A73I", "10Y1001A1001A70O", ...]
```

**NB07 (Cross-Border):** `NEIGHBORS` ist bereits aus `config.json` parametrisiert.
Länderspezifische Nachbarlisten in `config.json` ergänzen:

```json
"nachbarn_per_land": {
  "CH": ["DE", "AT", "IT", "FR"],
  "DE": ["AT", "CH", "FR", "DK", "PL", "CZ", "NL", "LU", "BE"],
  "FR": ["DE", "CH", "IT", "ES", "BE", "LU"],
  "NO": ["SE", "DK", "FI", "GB", "NL"]
}
```

### 6.3 NB06: Eurostat als europäischer Generalschlüssel

Für die räumliche Analyse bietet Eurostat zwei entscheidende Ressourcen:

**Bevölkerung (ersetzt BFS/GENESIS/Statistik Austria für alle EU-Länder):**

```python
# Eurostat REST API — identisches Format für alle EU-Länder
import requests
url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_pjan"
params = {
    "sex": "T",       # Total
    "age": "TOTAL",
    "geo": "DE",      # Beliebiger ISO-Code
    "time": "2023",
    "format": "JSON"
}
r = requests.get(url, params=params, timeout=60)
# Gleiches Format für FR, ES, PL, ... — kein länderspezifischer Parsing-Code
```

**NUTS-2 Regionsgrenzen (ersetzt swisstopo/BKG/BEV für ganz Europa):**

```python
import geopandas as gpd

# Ein einziger URL für alle europäischen NUTS-2 Regionen
NUTS_URL = "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2021_4326.geojson"
gdf_nuts = gpd.read_file(NUTS_URL)

# Nach Land filtern:
gdf_land = gdf_nuts[(gdf_nuts['LEVL_CODE'] == 2) & (gdf_nuts['CNTR_CODE'] == 'DE')]
# Projektion: WGS84 (EPSG:4326) — kein länderspezifisches CRS nötig
```

**Produktionsanlagen:** Kein einheitliches europäisches Register verfügbar.
Einzige Ausnahme: ENTSO-E Installed Capacity per Production Type
(`query_installed_generation_capacity`) gibt aggregierte MW je Technologie und
Land — kein Standort, aber ausreichend für NB06 Panel 2 (Leistung nach Zone).

### 6.4 Aufwandsmatrix Europa

| Notebook | Europa-Aufwand | Blocker |
|----------|---------------|---------|
| NB01 Preise/Last | **0h** nach BZ/CC-Parametrisierung | — |
| NB02 Analyse | **0h** | — |
| NB03 Visualisierung | **½h** Labeling (Währung, Landname) | — |
| NB04 Business Case | **0h** | — |
| NB05 Strategie | **0h** | — |
| NB06 Räumlich | **2–5 Tage** je Land | kein EU-Anlagenregister |
| NB06 mit Eurostat | **1–2 Tage** für Bev. + Grenzen | Anlagen bleiben manuell |
| NB07 Cross-Border | **½h** nachbarn_per_land ergänzen | — |
| NB08–NB15 | **0h** (preisneutral) | — |
| **Total (ohne NB06)** | **~1–2h** | — |
| **Total (mit NB06 Eurostat)** | **~1–3 Tage** | Anlagen je Land |

### 6.5 Nicht-generalisierbare Aspekte (Europa)

- **Produktionsanlagen-Standorte** (NB06 Karte 2): Kein paneuropäisches Register.
  Alternativen: OpenStreetMap `power=plant`-Tags (unvollständig), oder Karte 2
  durch ENTSO-E-Kapazitätsdaten ersetzen (nur aggregiert, kein Standort).
- **Tarif-Modell** (NB13): HT/NT-Strukturen stark länderspezifisch. NO/SE haben
  Spotpreis-direkt-Tarife ohne HT/NT-Spreizung — NB13 würde anders parametrisiert.
- **Währung UK** (GB): GBP → EUR-Umrechnung nötig. `eur_chf`-Pattern aus
  `config.json` auf `fx_rates` erweitern.
- **Datenlücken**: Balkanländer (RS, BG, GR) haben teilweise unvollständige
  ENTSO-E-Daten — Fallback auf verfügbare Jahre nötig.
- **Mehrfachzonen** (NO, SE, IT): Preis-Arbitrage zwischen Zonen möglich —
  interessante Erweiterung, aber ausserhalb des aktuellen Modells.

---

## 7. Empfohlene Umsetzungsreihenfolge

**Stufe 1 — DACH (~1–2 Tage):**
1. `config.json`: Land-Sektion + DACH-Optionen hinzufügen
2. NB01: `BZ_CODE`/`CC_CODE` parametrisieren → sofort lauffähig für DE/AT
3. NB07: `nachbarn_per_land` ergänzen
4. NB06 DE: Geodaten (BKG) + MaStR-Anlagen

**Stufe 2 — Europa Markt (~2–4h nach Stufe 1):**
1. `config.json`: `entsoe_bidding_zones`-Tabelle + `eurostat`-Sektion ergänzen
2. NB01: Keine Änderung nötig — läuft bereits mit beliebigem BZ_CODE
3. NB07: `nachbarn_per_land` für gewünschte Länder ergänzen
4. NB03/04/05: Labeling (Landname, ggf. Währungshinweis für UK)

**Stufe 3 — Europa räumlich (~1–3 Tage je Land):**
1. NB06: Eurostat NUTS-2 + `demo_pjan` für Bevölkerung einbauen
2. NB06: Anlagen je Land einzeln (oder durch ENTSO-E-Kapazitätsdaten ersetzen)
3. NB13: Tarif-Modell länderspezifisch parametrisieren

---

*Erstellt: März 2026 | SC26_Gruppe_2 | Potenzielle Erweiterung — kein Abgabe-Bestandteil*
