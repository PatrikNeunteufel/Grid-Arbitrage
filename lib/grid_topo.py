"""lib.grid_topo — Grid-/Topologie-Helfer für Kantonsgrenzen.

Eine Funktion aktuell:

* ``load_kantone`` — lädt Schweizer Kantonsgrenzen aus einem lokalen
  GeoPackage-Cache (swissBOUNDARIES3D oder K_01-Cache), mit automatischer
  Kürzel-Detektion ('ZH', 'BE', etc.) in der Spalte ``KAB``.

Konsolidiert drei inline-Varianten aus K_01, K_01c, K_01d. Die Funktion
deckt alle Use-Cases ab:

  - K_01: lädt aus lokalem Pfad, Fallback auf swissBOUNDARIES3D-Download
  - K_01c: lädt aus K_01-Cache oder alternativen Pfaden
  - K_01d: lädt aus K_01-Produktiv-Daten

Download-Fallback (swissBOUNDARIES3D) ist optional via ``download_url``.
Wenn nicht gesetzt, wird bei fehlendem Cache None zurückgegeben.
"""
from __future__ import annotations
import os


# ═════════════════════════════════════════════════════════════════════════════
# Konstanten
# ═════════════════════════════════════════════════════════════════════════════

#: Mapping von Kantons-Nummer (1..26) auf 2-Buchstaben-Kürzel
KANT_NUM_TO_ABK = {
    1: 'ZH',  2: 'BE',  3: 'LU',  4: 'UR',  5: 'SZ',  6: 'OW',
    7: 'NW',  8: 'GL',  9: 'ZG', 10: 'FR', 11: 'SO', 12: 'BS',
    13: 'BL', 14: 'SH', 15: 'AR', 16: 'AI', 17: 'SG', 18: 'GR',
    19: 'AG', 20: 'TG', 21: 'TI', 22: 'VD', 23: 'VS', 24: 'NE',
    25: 'GE', 26: 'JU',
}

#: Alle gültigen Kürzel (als Set für schnelles Matching)
KANT_ABK_SET = set(KANT_NUM_TO_ABK.values())


# ═════════════════════════════════════════════════════════════════════════════
# Hauptfunktion
# ═════════════════════════════════════════════════════════════════════════════

def load_kantone(data_dirs, download_url=None, download_target=None,
                 min_file_size=50_000, verbose=True):
    """Lädt Schweizer Kantonsgrenzen aus GeoPackage-Cache.

    Probiert mehrere Pfad-Kandidaten nacheinander, wählt den ersten der
    existiert und gross genug ist. Normalisiert auf EPSG:4326, ergänzt
    eine ``KAB``-Spalte mit 2-Buchstaben-Kürzeln.

    Parameter
    ---------
    data_dirs : list[str] oder str
        Liste von Dateipfaden zu kantone.gpkg oder swissboundaries3d.gpkg
        die nacheinander probiert werden. Einzelner String wird automatisch
        in eine Liste gewandelt.
    download_url : str, optional
        URL zu einem swissBOUNDARIES3D ZIP. Wenn gesetzt UND alle Pfade
        fehlschlagen, wird das ZIP heruntergeladen, .gpkg extrahiert und
        unter ``download_target`` gespeichert.
    download_target : str, optional
        Zielpfad für den Download (nur genutzt wenn ``download_url`` gesetzt).
    min_file_size : int, default 50_000 (50 KB)
        Minimale Dateigrösse in Bytes für eine Cache-Datei als gültig.
    verbose : bool, default True
        Status-Meldungen auf stdout.

    Return
    ------
    geopandas.GeoDataFrame oder None
        Kantone-GeoDataFrame mit Spalten inkl. ``KAB`` (2-Buchstaben-Kürzel)
        und CRS EPSG:4326. ``None`` wenn kein Cache gefunden UND
        (Download nicht versucht ODER fehlgeschlagen).
    """
    import geopandas as gpd

    if isinstance(data_dirs, str):
        data_dirs = [data_dirs]

    # ── Schritt 1: Cache-Datei finden ─────────────────────────────────────────
    kant_file = None
    for path in data_dirs:
        if os.path.exists(path) and os.path.getsize(path) > min_file_size:
            kant_file = path
            break

    # ── Schritt 2: Download-Fallback ──────────────────────────────────────────
    if kant_file is None and download_url and download_target:
        if verbose:
            print(f'Kantone-Cache fehlt — lade swissBOUNDARIES3D...')
        try:
            import requests
            import zipfile
            zip_path = download_target + '.zip'
            r = requests.get(download_url, timeout=120, stream=True)
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(1024 * 512):
                    f.write(chunk)
            with zipfile.ZipFile(zip_path) as z:
                gpkg_in_zip = next((n for n in z.namelist()
                                    if n.lower().endswith('.gpkg')), None)
                if gpkg_in_zip:
                    with z.open(gpkg_in_zip) as src, open(download_target, 'wb') as dst:
                        dst.write(src.read())
                    kant_file = download_target
                    if verbose:
                        print(f'  Extrahiert: {kant_file}')
        except Exception as e:
            if verbose:
                print(f'  Download fehlgeschlagen: {e}')

    if kant_file is None:
        if verbose:
            print('⚠️  Kantone nicht gefunden — Karte ohne Grenzen')
        return None

    # ── Schritt 3: Laden + CRS-Normalisierung ─────────────────────────────────
    try:
        layers = gpd.list_layers(kant_file)
        lname = next((l for l in layers['name'] if 'kanton' in l.lower()),
                     layers['name'].iloc[0])
        gdf = gpd.read_file(kant_file, layer=lname)
        if gdf.crs and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)
    except Exception as e:
        if verbose:
            print(f'  Ladefehler: {e}')
        return None

    # ── Schritt 4: KAB-Spalte ableiten (3 Strategien) ────────────────────────
    if 'KAB' not in gdf.columns:
        kab_col = None

        # Strategie 1: Spalten-Name ist icc/kab/abbreviation
        for col in gdf.columns:
            if col.lower() in ('icc', 'kab', 'abbreviation', 'abb'):
                kab_col = col
                break

        # Strategie 2: Spalte enthält Zahlen 1..26 (Kantons-Nummer)
        if kab_col is None:
            for col in gdf.columns:
                if col == 'geometry':
                    continue
                try:
                    import pandas as pd
                    nums = pd.to_numeric(gdf[col], errors='coerce')
                    if nums.between(1, 26).sum() >= 20:
                        gdf['KAB'] = nums.map(KANT_NUM_TO_ABK).fillna('??')
                        if verbose:
                            print(f'  KAB via Nummer-Spalte "{col}"')
                        break
                except Exception:
                    continue

        # Strategie 3: Spalte enthält direkt Kürzel (case-insensitive)
        if 'KAB' not in gdf.columns:
            for col in gdf.columns:
                if col == 'geometry':
                    continue
                vals = gdf[col].astype(str).str.strip().str.upper()
                if vals.isin(KANT_ABK_SET).sum() >= 20:
                    gdf['KAB'] = vals
                    if verbose:
                        print(f'  KAB via Kürzel-Spalte "{col}"')
                    break

        # Nutzung einer spezifizierten Spalte
        if kab_col and 'KAB' not in gdf.columns:
            s = gdf[kab_col].astype(str).str.strip()
            if s.str.isnumeric().all():
                gdf['KAB'] = s.astype(int).map(KANT_NUM_TO_ABK)
            else:
                gdf['KAB'] = s.str.upper().str[:2]

    if verbose:
        n_valid = gdf['KAB'].isin(KANT_ABK_SET).sum() if 'KAB' in gdf.columns else 0
        print(f'Kantone: {len(gdf)} | {n_valid} valide Kürzel | {os.path.basename(kant_file)}')

    return gdf
