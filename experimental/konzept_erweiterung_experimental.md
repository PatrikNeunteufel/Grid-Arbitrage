# Konzept: Experimentelle Erweiterung & Länderwechsel — SC26_Gruppe_2

**Status:** Potenzielle Erweiterung nach Projektabgabe (11.05.2026)
**Scope:** K_01b/c/d (Zonenmodell, Animationen, Grid-Topologie) + Länderwechsel Pflicht/Kür

---

## 1. Struktur: experimental/ Ordner

### 1.1 Ordnerhierarchie

```
SC26_Gruppe_2/
├── kuer/                          ← Kür-Notebooks (Abgabe-relevant)
│   ├── K_00_Business_Strategy.ipynb
│   ├── K_01_Raeumliche_Analyse.ipynb
│   └── ...
├── experimental/                  ← NEU: Explorative Notebooks (NICHT Abgabe)
│   ├── K_01b_Zonenmodell_Erweitert.ipynb
│   ├── K_01c_Energiefluss_Animationen.ipynb
│   └── K_01d_Grid_Topologie.ipynb
├── data/
│   ├── raw/
│   │   ├── bfe_produktionsanlagen.gpkg      ← Standard
│   │   ├── kantone.gpkg                     ← Standard
│   │   └── EXP_*                            ← Experimentelle Downloads
│   └── intermediate/
│       ├── grid_topology/                   ← K_01d Cache
│       │   ├── CH_earthosm_substations.geojson
│       │   ├── CH_earthosm_lines.geojson
│       │   └── earth_osm_raw/               ← Geofabrik PBF-Extrakte (~100–600 MB)
│       └── EXP_*
└── output/
    └── charts/
        ├── realistisch/                     ← Standard-Charts (Pflicht + Kür)
        └── experimental/                    ← NEU: EXP_-Präfix Outputs
            ├── EXP_kuer_k01b_bvi.png
            ├── EXP_kuer_k01c_gif_a_tag_winter.gif
            └── EXP_kuer_k01d_ch_netz_statisch.png
```

### 1.2 EXP_-Präfix Konvention

Alle Dateien die aus experimental/-Notebooks stammen erhalten den Präfix `EXP_`:

| Typ | Beispiel |
|-----|---------|
| Charts | `EXP_kuer_k01b_bvi.png` |
| GIFs | `EXP_kuer_k01c_gif_a_tag_winter.gif` |
| Grid-Cache | `EXP_kuer_k01d_ch_substations.geojson` |
| Aufbereitungen | `EXP_kuer_k01d_ch_earthosm_lines.geojson` |

**Zweck:** Trennung von Abgabe-Outputs und experimentellen Outputs im gleichen `output/`-Ordner.
Die Konfiguration `EXP_CHARTS_DIR = '../output/charts/experimental'` ist in allen drei
Notebooks bereits implementiert.

### 1.3 Pfad-Anpassung bei Verschiebung nach experimental/

Wenn Notebooks von `kuer/` nach `experimental/` verschoben werden, müssen relative Pfade angepasst werden:

```python
# In kuer/:        BASE_DIR = '..'
# In experimental/: BASE_DIR = '../..'  (eine Ebene tiefer)
BASE_DIR = '..'  # ⚙ anpassen wenn Notebook verschoben

with open(os.path.join(BASE_DIR, 'sync', 'config.json')) as f:
    CFG = json.load(f)
DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
```

---

## 2. Räumliche Granularität

### 2.1 Vergleich der Auflösungsebenen für CH

| Ebene | Anzahl | Datenquelle | API | Relevanz |
|-------|--------|-------------|-----|---------|
| **Kantone** | 26 | BFS STATPOP | PXWeb ✅ | K_01 aktuell |
| **Bezirke** | ~150 | BFS STATPOP | PXWeb ✅ | Sinnvolle Zwischenebene |
| **Gemeinden** | ~2'134 | BFS STATPOP + swisstopo | PXWeb + swissBOUNDARIES3D ✅ | Verbrauchsverteilung |
| **Substations** | 147 | OSM / Swissgrid | earth-osm ✅ | Netzfluss (K_01d) |
| **Baublöcke** | ~150'000 | swisstopo | GeoPackage | Zu granular für Verbrauchsmodell |

### 2.2 Gemeinde-Auflösung implementieren

BFS STATPOP liefert Bevölkerungsdaten auf Gemeindeebene im gleichen PXWeb-Format:

```python
# In K_01b: KANTON_TO_ZONE durch GEMEINDE_TO_ZONE ersetzen
# BFS Gemeindegrenzen laden:
GMD_FILE = os.path.join(DATA_DIR, 'gemeinden.gpkg')
# Download via swisstopo swissBOUNDARIES3D (gleiche ZIP wie Kantone):
# Enthält Layer 'swissBOUNDARIES3D_1_5_TLM_HOHEITSGEBIET' mit ~2134 Gemeinden

# BFS STATPOP Gemeinden (PXWeb, gleiche API):
BFS_GMD_API = 'https://www.pxweb.bfs.admin.ch/api/v1/de/px-x-0102010000_101/px-x-0102010000_101.px'
# Der Code in K_01 ist bereits generisch — nur die Aggregationsebene (Kanton vs. Gemeinde) ändern
```

**Einschränkung:** Installierte Produktionsleistung (BFE GeoPackage) liegt auf Anlagenebene vor
und lässt sich auf Gemeindeebene aggregieren — kein Mehraufwand.

### 2.3 NUTS-3 für internationale Vergleichbarkeit

Für DACH-Erweiterung ist NUTS-3 die geeignete supranationale Ebene:

```python
# Eurostat NUTS-2/3 GeoJSON (einheitlich für ganz Europa):
NUTS_URL = 'https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2021_4326.geojson'
gdf_nuts = gpd.read_file(NUTS_URL)

# CH NUTS-3 = 26 Kantone (identisch mit Kantonsebene)
# DE NUTS-3 = 401 Kreise/kreisfreie Städte
# AT NUTS-3 = 35 Gruppen von Gemeinden
gdf_ch_nuts3 = gdf_nuts[(gdf_nuts['LEVL_CODE']==3) & (gdf_nuts['CNTR_CODE']=='CH')]
```

---

## 3. Real vs. Synthetisch — Kennzeichnungskonvention

In allen drei experimentellen Notebooks werden Zellen mit Badges markiert:

| Badge | Bedeutung |
|-------|-----------|
| `📡 ECHTE DATEN` | Zelle lädt oder verarbeitet echte Messdaten/Geodaten |
| `🔬 MODELLIERT` | Zelle erzeugt synthetische/modellierte Ausgaben |
| `✅ KALIBRIERT` | Modellwerte gegen Referenzdaten validiert |
| `⚙ KONFIGURATION` | Setup-Zelle, nur Parameter |
| `💾 DOWNLOAD` | Lädt externe Daten herunter (Internet benötigt) |

**Wichtig für Projektbericht:** Alle Lastfluss-Visualisierungen (K_01c GIF C/D/E, K_01d GIFs)
sind synthetisch modelliert — kein echter DC-Lastfluss-Solver. Nur die Topologie (Knoten/Kanten)
in K_01d basiert auf echten OSM-Daten.

---

## 4. Datenbeschaffung Grid-Topologie (K_01d)

### 4.1 Prioritätskette

```
P1: earth-osm (Geofabrik PBF)         ← vollständigste OSM-Quelle
    └── from earth_osm.eo import save_osm_data
    └── region_list=['switzerland'], primary_name='power'
    └── Cache: data/intermediate/grid_topology/CH_earthosm_*.geojson

P2: Overpass API                        ← direktes OSM, Timeout-Risiko
    └── 4 Mirror-Fallbacks
    └── Cache: data/intermediate/grid_topology/CH_substations.json

P3: PyPSA-Eur Zenodo                   ← preprocessed, inkl. elektr. Parameter
    └── zenodo.org/records/14144752
    └── buses.csv + lines.csv, Filter nach 'country'=='CH'

P4: Hardcoded Baseline                 ← offline-fähig, CH 27 Knoten
    └── Aus Swissgrid-Publikationen
```

### 4.2 earth-osm korrekte API (v3.0.2)

```python
# FALSCH (führte zu AttributeError):
import earth_osm as eo
eo.save_osm_data(...)

# KORREKT:
from earth_osm.eo import save_osm_data as _eo_save
_eo_save(
    region_list=['switzerland'],   # Geofabrik-Regionsnamen (Kleinbuchstaben)
    primary_name='power',
    feature_list=['substation', 'line'],
    out_dir='./earth_data',        # Output-Verzeichnis
    data_dir='./earth_data',       # PBF-Cache-Verzeichnis
    out_format='geojson',          # String, nicht Liste!
    out_aggregate=False,
    data_source='geofabrik',
    update=False,
    mp=False,
)
```

### 4.3 Output-Dateinamen (earth-osm v3.0.2)

earth-osm erzeugt Dateien unter `<out_dir>/out/`:
- `CH_raw_substations.geojson` (wenn region='switzerland' → ISO CH)
- `CH_raw_lines.geojson`

Bei unbekanntem Mapping: `glob.glob(out_dir + '/**/*substation*', recursive=True)`

---

## 5. Länderwechsel — Pflicht und Kür

### 5.1 Was heute schon parametrisiert ist

Die folgenden Notebooks sind **bereits ländergenerisch** durch `BZ_CODE`/`CC_CODE`:

| Notebook | Status | Änderung nötig |
|----------|--------|----------------|
| NB01 Spotpreise | ✅ über `BZ_CODE` | Nur `config.json` ändern |
| NB02–NB05 Analyse | ✅ preisneutral | Label-Anpassung (Titel) |
| NB07 Cross-Border | ✅ via `NEIGHBORS` | `nachbarn_per_land` ergänzen |
| K_01d Grid | ✅ via `CC_CODE` | `COUNTRY_CONFIG` ergänzen |

### 5.2 config.json — empfohlene Erweiterung

```json
"land": {
  "aktiv": "CH",
  "optionen": {
    "CH": {
      "label": "Schweiz",
      "entsoe_bidding_zone": "10YCH-SWISSGRIDZ",
      "entsoe_country_code": "CH",
      "waehrung": "EUR"
    },
    "DE": {
      "label": "Deutschland",
      "entsoe_bidding_zone": "10Y1001A1001A83F",
      "entsoe_country_code": "DE",
      "waehrung": "EUR"
    },
    "AT": {
      "label": "Österreich",
      "entsoe_bidding_zone": "10YAT-APG------L",
      "entsoe_country_code": "AT",
      "waehrung": "EUR"
    }
  }
}
```

**Aktivierung:** `"aktiv": "DE"` setzen → NB01–NB05, NB07, K_01d laufen für DE.

### 5.3 Was bei Länderwechsel manuell angepasst werden muss

#### NB06 (räumliche Analyse) — grösster Aufwand

| Element | CH | DE | AT | Generisch (Europa) |
|---------|----|----|----|--------------------|
| Kantonsgrenzen | swisstopo GPKG | BKG VG250 | BEV GEM | Eurostat NUTS-3 |
| Bevölkerung | BFS PXWeb | GENESIS API | Statistik Austria | Eurostat `demo_pjan` |
| Produktionsanlagen | BFE GPKG | MaStR REST | E-Control CSV | — kein EU-Register |
| Projektion | EPSG:2056 | EPSG:25832 | EPSG:31258 | EPSG:4326 |

#### K_01b (6-Zonen-Modell)

```python
# KANTON_TO_ZONE_B: durch länderspezifische Verwaltungseinheiten ersetzen
# DE: 16 Bundesländer → z.B. 5 Netzzonen (50Hertz/Amprion/TenneT/TransnetBW + Import)
# AT: 9 Bundesländer → 2-3 Zonen (West/Mitte/Ost nach APG-Struktur)

KANTON_TO_ZONE_B = {
    # DE-Beispiel:
    'DE-BB': 'Nordost-DE', 'DE-BE': 'Nordost-DE',  # 50Hertz
    'DE-NW': 'West-DE',    'DE-RP': 'West-DE',      # Amprion
    'DE-BY': 'Süd-DE',     'DE-BW': 'Süd-DE',       # TransnetBW + TenneT
    # ...
}
```

#### K_01c (Animationen)

Nur `KANTON_TO_ZONE_B` und `ZONE_CENTERS` müssen für das neue Land angepasst werden.
Das Profil-Modell (CF-Faktoren) bleibt gleich, `ZONE_PROD_INSTALLED` muss durch
ENTSO-E `query_installed_generation_capacity` für das neue Land ersetzt werden.

#### K_01d (Grid-Topologie)

Nur `CC_CODE = 'DE'` setzen — alle Loader sind bereits ländergenerisch.
Für DE/AT ohne Baseline: Overpass oder earth-osm laden ~200–800 Knoten und ~500–2000 Kanten.

---

## 6. Umsetzungsreihenfolge nach Projektabgabe

```
Woche 1:
  ✅ config.json: land.aktiv + DACH-Optionen
  ✅ NB01: BZ_CODE/CC_CODE parametrisieren (2–3 Zeilen)
  ✅ NB07: nachbarn_per_land für DE/AT
  ✅ K_01d: CC_CODE='DE' testen → automatisch Topologie via earth-osm

Woche 2:
  ⚠️ NB06 DE: BKG-Geodaten + MaStR-Anlagen (Hauptaufwand)
  ⚠️ K_01b DE: Bundesland-Zonen definieren

Woche 3:
  ⚠️ Europa generisch: Eurostat NUTS-3 + demo_pjan in NB06
  ✅ K_01d: BATCH_RUN=True für CH/DE/AT/FR Vergleichskarten

Optional (nach Bedarf):
  🔬 Echter DC-Lastfluss: PyPSA mit Zenodo-Netz (r/x vorhanden)
  🔬 Gemeinde-Auflösung K_01b CH: swissBOUNDARIES3D GMD-Layer
```

---

## 7. Bekannte Limitationen (bleiben bestehen)

- **Lastflüsse synthetisch:** Ohne DC-Solver (PyPSA) bleiben alle Flusswerte approximiert
- **Produktionsanlagen Europa:** Kein paneuropäisches Standort-Register — ENTSO-E liefert nur aggregierte MW je Technologie und Land
- **Mehrfachzonen:** NO/SE/IT haben mehrere Preiszonen — NB01 muss Zone auswählen oder aggregieren
- **Saisonale Profilkurven:** Basieren auf BFE-CH-2023-Statistik — für DE/AT müssen andere CF-Faktoren aus nationalen Statistiken kalibriert werden
- **Tarif-Modell NB13:** HT/NT-Spreizung und -Zeiten sind länderspezifisch

---

*Erstellt: April 2026 | SC26_Gruppe_2 | Nicht Teil der Abgabe 11.05.2026*
