# Migration `xconfig.json` → `sync/config.json`

## Zweck

Die experimental-Notebooks (K_01b, K_01c, K_01d) sind **nicht Teil der Pflicht/Kür-Abgabe** und nutzen lokale Konstanten + eine eigene Config-Datei `xconfig.json`. Sobald ein experimental-Modell in den **regulären Kür-Stand** übernommen wird (z.B. K_01b ersetzt das 5-Zonen-Modell von K_01), müssen die Konfig-Werte in `sync/config.json` migriert werden.

`xconfig.json` ist **strukturell parallel** zu `config.json` aufgebaut, damit die Migration ein einfaches Mergen ist — keine Umbenennung nötig.

## Was steckt in xconfig.json (und was NICHT)

**In xconfig.json**:
- Zonenmodell-Definitionen (`kanton_to_zone`, `zone_colors`, `engpass_multiplikator`, `zone_bottleneck`)
- Switches (`experimental_aktiv.zonenmodell`, `country`, `granularity`)
- Animations-Parameter (frames, fps, gif_a/c/d-Settings)
- Country-Configs (CH/DE/AT mit bbox, Spannungsebenen)
- User-Layout-Settings für K_01d (Overlay-Positionen)
- Kapazitätsfaktoren (CF jahresdurchschnittlich + saisonal)

**NICHT in xconfig.json** (wichtig — wurde absichtlich entfernt):
- `zone_prod_installed_mw` (installierte Kapazität pro Zone × Energieträger).
  Diese Werte werden zur Laufzeit aus den **echten BFE-Daten** (`bfe_produktionsanlagen.gpkg`) via `lib.bfe_zonen.aggregate_zone_prod()` aggregiert. Hardcoded Modellwerte gehören nicht in die Config.

## Migrations-Schritte

### 1. Vorbereitung

```bash
# Aus dem Projekt-Root
cd /pfad/zu/Grid-Arbitrage
cp sync/config.json sync/config.json.backup
cp experimental/xconfig.json sync/xconfig.json.backup
```

### 2. Werte aus xconfig.json nach config.json mergen

#### 2a) Aktive Auswahl (Switches)

In `sync/config.json` neben den bestehenden Schaltern hinzufügen:

```json
{
  "szenarien": {
    "gleichzeitigkeit_aktiv": "realistisch"
  },
  "experimental_aktiv": {
    "zonenmodell":  "k01b_6zonen",
    "country":      "CH",
    "granularity":  "kantone"
  }
}
```

> **Hinweis:** Falls nur K_01b ohne Multi-Country migriert wird, kann `country`/`granularity` weggelassen werden — die Kür K_01 nutzt nur CH/Kantone.

#### 2b) Zonen-Modelle nach `kuer.k01b` und `kuer.k01_zonenmodell`

Aus `xconfig.json` → `kuer.k01b.*` und `kuer.k01_zonenmodell.*` direkt nach `sync/config.json` → `kuer.k01b.*` und `kuer.k01_zonenmodell.*` kopieren. **Pfade sind bereits identisch** — kein Umbenennen.

Inhalt: `kanton_to_zone`, `zone_colors`, `engpass_multiplikator`, `zone_bottleneck`, `spez_kw_person`.

#### 2c) Kapazitätsfaktoren (gemeinsam)

`xconfig.json` → `kuer.k01_kapazitaetsfaktoren.*` direkt nach `sync/config.json` → `kuer.k01_kapazitaetsfaktoren.*` kopieren.

#### 2d) Animations-Parameter (optional)

K_01c und K_01d nutzen GIF-spezifische Parameter, die nicht in der regulären `visualisierung.animation` enthalten sind. Bei Migration:

- `kuer.k01c.*` und `kuer.k01d.*` direkt mergen
- `kuer.k01d.country_config` ist Multi-Country-Map — nur nötig wenn Multi-Country-Feature in der Pflicht-Pipeline gewünscht ist
- `kuer.k01d.overlay_layout` enthält **User-Layout-Settings** (manuell justiert) — ohne Patrik nicht ändern

### 3. Notebook-Patches

In den NBs `K_01b/c/d` müssen Lese-Calls geändert werden:

```python
# VORHER (experimental):
with open('xconfig.json', encoding='utf-8') as f:
    XCFG = json.load(f)
KANTON_TO_ZONE_B = XCFG['kuer']['k01b']['kanton_to_zone']

# NACHHER (nach Migration):
with open('../sync/config.json', encoding='utf-8') as f:
    CFG = json.load(f)
KANTON_TO_ZONE_B = CFG['kuer']['k01b']['kanton_to_zone']
```

Das **Pfad-Suffix bleibt identisch** (`kuer.k01b.kanton_to_zone`) — nur die Datei-Quelle ändert sich.

### 4. Validierung

Nach dem Merge:

```python
import json
cfg = json.load(open('sync/config.json', encoding='utf-8'))

# Prüfe alle migrierten Pfade
assert 'k01b' in cfg['kuer']
assert 'kanton_to_zone' in cfg['kuer']['k01b']
assert len(cfg['kuer']['k01b']['kanton_to_zone']) == 26  # 26 Kantone
assert 'experimental_aktiv' in cfg
print('✓ Migration valide')
```

### 5. Cleanup

Nach erfolgreicher Migration und Validierung:

```bash
git rm experimental/xconfig.json
git rm experimental/MIGRATION.md
git commit -m "Migrate experimental k01b/k01c/k01d config to sync/config.json"
```

## Was bleibt im NB lokal?

Nicht alle Konstanten gehören in `config.json`. Folgende bleiben im NB selbst:

| Konstante | Warum lokal? |
|---|---|
| `BB`, `MAP_XLIM`, `MAP_YLIM` | Country-spezifisch in `country_config` aufgehoben |
| `KANTON_CENTROIDS`, `CH_STADTE` | Static lookup, nicht parametrisiert |
| `SUBCAT_MAP`, `MAINCAT_MAP` | Datenquellen-spezifisch, in `lib.bfe_zonen` |
| `BORDER_POINTS`, `ZONE_CENTERS` | Visuelle Hilfspunkte, kein Modell-Parameter |
| `OVERLAYS` (matplotlib-Spezifikum) | Wird aus `kuer.k01d.overlay_layout` gelesen, der Code-Block bleibt aber im NB |
| `ZONE_PROD_INSTALLED` | **Wird zur Laufzeit aus BFE aggregiert** — nicht in Config |

## Encoding-Hinweis

Alle `open()`-Calls für JSON-Configs nutzen `encoding='utf-8'`. Das ist auf Windows zwingend, weil dort der Default-Encoder CP1252 wäre und Umlaute (z.B. `'Süd'` als Zone-Name) doppelt-kodiert würden.

## Auswahl-Switches während experimentell

Solange experimental aktiv ist, kann der User in `xconfig.json` direkt umschalten:

```json
{
  "experimental_aktiv": {
    "zonenmodell": "k01b_6zonen",   // oder "k01_5zonen"
    "country":     "CH",            // oder "DE", "AT", "FR", "IT"
    "granularity": "kantone"        // oder "bezirke", "gemeinden", "nuts3"
  }
}
```

NBs lesen den aktiven Wert und wählen die passende Zonen-/Country-Definition. Analog zum Pflicht-Pattern `szenarien.gleichzeitigkeit_aktiv`.
