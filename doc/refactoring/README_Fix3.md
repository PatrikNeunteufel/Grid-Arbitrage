# Fix K_01d — CSV-Parse-Fehler beim Zenodo-Download

## Das Problem

```
▶ Lade PyPSA-Eur Zenodo Record 14144752 (~21 MB, Europa gesamt)...
   1/2 buses.csv (~1 MB)... HTTP 200, 857 KB
   2/2 lines.csv (~20 MB)... HTTP 200, 18.8 MB
❌ CSV-Parse-Fehler: Error tokenizing data. C error:
   Expected 31 fields in line 3, saw 177
```

Der Download klappt (richtige Dateigrössen: 857 KB + 18.8 MB — stimmt mit Zenodo-Record-Metadaten überein), aber pandas stolpert beim Parsen.

## Die Ursache

In der `lines.csv` des PyPSA-Eur Zenodo-Records v0.6 ist die `geometry`-Spalte mit **einfachen Anführungszeichen** `'` quotiert, nicht mit doppelten `"`:

```csv
line_id,bus0,bus1,voltage,...,geometry
merged_relation/10264161-225+1,way/150329778-225,...,'LINESTRING (5.972 43.157, 5.979 43.159, 5.981 43.160, ...)'
```

Der pandas-Default-Parser kennt als `quotechar` nur `"`. Er ignoriert die Apostrophe, interpretiert jedes Komma in der LINESTRING-Koordinatenliste als Feldtrenner, und scheitert entsprechend — 177 Felder statt 31.

## Der Fix

`quotechar="'"` an beide `pd.read_csv()`-Aufrufe im Zenodo-Loader übergeben:

```python
# Zenodo v0.6: geometry-Spalte nutzt einfache Anführungszeichen 'LINESTRING(...)'
# → quotechar="'" nötig, sonst zerhackt der CSV-Parser an Kommas in Koordinaten
df_buses_all = pd.read_csv(StringIO(rb.text), quotechar="'")
df_lines_all = pd.read_csv(StringIO(rl.text), quotechar="'")
```

`buses.csv` hat ebenfalls ein `geometry`-Feld (POINT statt LINESTRING) und wird vorsorglich gleich behandelt — kostet nichts wenn nicht nötig, schützt gegen zukünftige Zenodo-Schema-Änderungen.

## Cache-Dateien sind nicht betroffen

Die gecacheten `zenodo_buses_all.csv` und `zenodo_lines_all.csv` werden via `to_csv()` gespeichert — pandas schreibt dort Standard-Quoting mit `"`. Beim Re-Read aus dem Cache ist kein Fix nötig. Nur der Weg "Zenodo-Download → erstes Parsen" hatte das Problem.

## Verifikation

Beim nächsten Lauf von K_01d Cell 15 (`load_pypsa_zenodo(...)`) sollte erscheinen:

```
▶ Lade PyPSA-Eur Zenodo Record 14144752 (~21 MB, Europa gesamt)...
   1/2 buses.csv (~1 MB)... HTTP 200, 857 KB
   2/2 lines.csv (~20 MB)... HTTP 200, 18.8 MB
   Gecacht: zenodo_buses_all.csv, zenodo_lines_all.csv
   Europa gesamt: ~12000 Busse, ~15000 Leitungen
   Kanten mit ≥1 Endpunkt in CH: ~300
✅ CH: ~250 Substations, ~300 Leitungen
```

Die exakten Zahlen hängen vom Zenodo-Record-Stand ab, aber keine Fehlermeldung mehr.

## Installation

```bash
cp <ZIP>/patched_notebooks/experimental/K_01d_Grid_Topologie.ipynb experimental/
```

Falls du schon einen teilweise gefüllten Cache im `experimental/data/intermediate/grid_zenodo/` Verzeichnis hast, kannst du den behalten — der gecachte Rohdaten-Download wird beim nächsten Lauf wiederverwendet (kein erneutes Herunterladen nötig).

Wenn der Cache beschädigt ist (weil der erste Download durchgelaufen ist, aber das Parsing scheiterte — dann liegen evtl. nur unvollständige Files da), den Cache-Ordner einmal leeren:

```bash
rm -rf experimental/data/intermediate/grid_zenodo/
```

Danach lädt der Loader frisch herunter und speichert beide Files korrekt.

## Qualitäts-Checks (alle ✅)

| Check | Status |
|---|---|
| AST-Validierung der Loader-Zelle | ✅ |
| 3 Vorkommen von `quotechar` (Kommentar + 2 Calls) | ✅ |
| Keine anderen Zellen angetastet (TOC-Fixes vom User bleiben erhalten) | ✅ |
