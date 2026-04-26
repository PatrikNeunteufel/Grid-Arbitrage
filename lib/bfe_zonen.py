"""
lib.bfe_zonen — BFE-Anlagen laden + nach Zonen aggregieren.

Wird von K_01b, K_01c, K_01d gemeinsam genutzt um konsistente
ZONE_PROD_INSTALLED-Aggregate aus den realen BFE-Daten zu berechnen
(statt hardcoded Modellwerte in xconfig.json).

Public API:
    load_bfe_plants(data_dir) -> GeoDataFrame    # mit ET_group + kw Spalten
    aggregate_zone_prod(gdf_plants, kanton_to_zone, kept_ets=...) -> dict[Zone, dict[ET, MW]]

Datenquelle: Bundesamt für Energie (BFE) — bfe_produktionsanlagen.gpkg
            Open Government Data, https://www.bfe.admin.ch
"""
import os
import pandas as pd

# ── ET-Mapping (BFE subcat / maincat → vereinheitlichte Namen) ──────────────
SUBCAT_MAP = {
    'subcat_1': 'Wasserkraft', 'subcat_2': 'Solar',     'subcat_3':  'Wind',
    'subcat_4': 'Biomasse',    'subcat_5': 'Geothermie', 'subcat_6':  'Kernkraft',
    'subcat_7': 'Erdoel',      'subcat_8': 'Erdgas',    'subcat_9':  'Kohle',
    'subcat_10': 'Abfall',
}
MAINCAT_MAP = {
    'maincat_1': 'Wasserkraft', 'maincat_2': 'Solar',
    'maincat_3': 'Kernkraft',   'maincat_4': 'Erdgas',
}


def _find_col(df, *candidates):
    """Findet erste passende Spalte (case-insensitive Substring-Match)."""
    cols_lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        for col_low, col_orig in cols_lower.items():
            if cand.lower() in col_low:
                return col_orig
    return None


def load_bfe_plants(data_dir):
    """Lädt BFE-Anlagen (bfe_produktionsanlagen.gpkg) und ergänzt Spalten ET_group, kw.

    Args:
        data_dir: Pfad zum data/raw-Verzeichnis (mit bfe_produktionsanlagen.gpkg).

    Returns:
        GeoDataFrame mit zusätzlichen Spalten:
          - ET_group: vereinheitlichter Energieträger ('Solar', 'Wasserkraft', ...)
          - kw:       Leistung in kW (numerisch)

    Raises:
        FileNotFoundError: wenn bfe_produktionsanlagen.gpkg fehlt.
    """
    import geopandas as gpd

    bfe_path = os.path.join(data_dir, 'bfe_produktionsanlagen.gpkg')
    if not os.path.exists(bfe_path):
        raise FileNotFoundError(
            f'BFE-Datei fehlt: {bfe_path}. '
            f'Bitte K_01 (Räumliche Analyse) zuerst ausführen — die lädt das Geopackage.'
        )

    # Layer wählen — robuste API für unterschiedliche geopandas-Versionen
    try:
        layers = gpd.list_layers(bfe_path)
        layer = layers['name'].iloc[0] if hasattr(layers, '__len__') else layers[0][0]
    except AttributeError:
        # Fallback für ältere geopandas-Versionen
        import fiona
        layer = fiona.listlayers(bfe_path)[0]

    gdf = gpd.read_file(bfe_path, layer=layer)
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    # Spalten-Mapping (BFE-Schema variiert je nach Quartals-Release)
    col_subcat   = _find_col(gdf, 'subcat', 'subcategor')
    col_maincat  = _find_col(gdf, 'maincat', 'maincategor')
    col_leistung = _find_col(gdf, 'totalpower', 'power', 'leistung')

    def _map_et(row):
        if col_subcat and not pd.isna(row.get(col_subcat, 'NaN')):
            c = str(row[col_subcat]).strip().lower()
            if c in SUBCAT_MAP:
                return SUBCAT_MAP[c]
        if col_maincat and not pd.isna(row.get(col_maincat, 'NaN')):
            c = str(row[col_maincat]).strip().lower()
            if c in MAINCAT_MAP:
                return MAINCAT_MAP[c]
        return 'Andere'

    gdf['ET_group'] = gdf.apply(_map_et, axis=1)
    if col_leistung:
        gdf['kw'] = pd.to_numeric(gdf[col_leistung], errors='coerce').fillna(0)
    else:
        raise ValueError(
            'BFE: Leistungs-Spalte (totalpower/power/leistung) nicht gefunden. '
            f'Verfügbare Spalten: {list(gdf.columns)}'
        )

    return gdf


def aggregate_zone_prod(gdf_plants, kanton_to_zone,
                        kanton_col=None,
                        kept_ets=('Solar', 'Wasserkraft', 'Kernkraft'),
                        collapse_to='Andere'):
    """Aggregiert installierte Kapazität pro Zone × Energieträger.

    Args:
        gdf_plants: GeoDataFrame aus load_bfe_plants() mit Spalten 'ET_group', 'kw'.
        kanton_to_zone: dict {Kantons-Kürzel ('ZH', 'BE', ...): Zonen-Name}.
                        Mit unterschiedlichen Mappings (5 vs. 6 Zonen) entstehen
                        unterschiedliche Aggregate aus denselben BFE-Daten.
        kanton_col: Spaltenname für Kantons-Kürzel im DataFrame.
                    None = automatisch finden (case-insensitive 'canton'/'kanton').
        kept_ets: Energieträger die als eigene Keys erhalten bleiben.
                  Default: Solar/Wasserkraft/Kernkraft (= K_01c/K_01d-Bedarf).
        collapse_to: Name des Sammel-Buckets für alle übrigen Energieträger
                     (Wind/Biomasse/Erdgas/Abfall/Geothermie/Erdoel/Kohle).
                     Bei collapse_to=None bleiben ALLE ETs als eigene Keys
                     erhalten (= K_01b-Bedarf für detaillierte CF-Berechnung).

    Returns:
        dict {zone_name: {et_name: mw_installed}}, z.B.
        {'Nordost':         {'Solar': 1850.3, 'Wasserkraft': 480.5, 'Kernkraft': 0.0, 'Andere': 220.1},
         'Mitte-Erzeugung': {'Solar': 1198.7, 'Wasserkraft': 805.2, 'Kernkraft': 4980.0, 'Andere': 290.5},
         ...}

    Raises:
        ValueError: wenn ET_group oder kw-Spalte fehlt.
    """
    if 'ET_group' not in gdf_plants.columns or 'kw' not in gdf_plants.columns:
        raise ValueError(
            'gdf_plants muss Spalten "ET_group" und "kw" enthalten — '
            'load_bfe_plants() vorher aufrufen.'
        )

    if kanton_col is None:
        kanton_col = _find_col(gdf_plants, 'canton', 'kanton')
        if kanton_col is None:
            raise ValueError(
                'Kantons-Spalte nicht gefunden. Bitte kanton_col explizit angeben. '
                f'Verfügbare Spalten: {list(gdf_plants.columns)}'
            )

    df = gdf_plants[[kanton_col, 'kw', 'ET_group']].copy()
    df['Zone'] = df[kanton_col].map(kanton_to_zone)
    df = df[df['Zone'].notna()]

    # ET_group entweder behalten oder kollabieren
    if collapse_to is not None:
        keep = set(kept_ets)
        df['ET_final'] = df['ET_group'].where(df['ET_group'].isin(keep), collapse_to)
    else:
        df['ET_final'] = df['ET_group']

    # Aggregate kW → MW
    agg = df.groupby(['Zone', 'ET_final'])['kw'].sum() / 1000.0
    pivot = agg.unstack(fill_value=0.0)

    # Sicherstellen dass alle erwarteten ETs da sind (auch wenn 0 MW)
    if collapse_to is not None:
        for et in tuple(kept_ets) + (collapse_to,):
            if et not in pivot.columns:
                pivot[et] = 0.0

    return {
        zone: {et: float(pivot.loc[zone, et]) for et in pivot.columns}
        for zone in pivot.index
    }


def aggregate_zone_total_inst(gdf_plants, kanton_to_zone, kanton_col=None):
    """Summe installierte Kapazität pro Zone (alle Energieträger zusammen) in MW.

    Komfort-Funktion für K_01b (zone_inst_b).

    Returns:
        dict {zone_name: mw_total_installed}
    """
    zp = aggregate_zone_prod(gdf_plants, kanton_to_zone,
                             kanton_col=kanton_col, collapse_to=None)
    return {z: sum(ets.values()) for z, ets in zp.items()}


def aggregate_zone_mean_prod(gdf_plants, kanton_to_zone, cf_per_et,
                             kanton_col=None):
    """Mittlere Produktion pro Zone (alle ETs, gewichtet mit Kapazitätsfaktor).

    Komfort-Funktion für K_01b (zone_prod_b).

    Args:
        cf_per_et: dict {ET: capacity_factor}, z.B. {'Solar': 0.12, 'Wasserkraft': 0.38, ...}
                   Fehlende ETs werden mit cf_per_et.get('Andere', 0.40) gefüllt.

    Returns:
        dict {zone_name: mean_mw}
    """
    zp = aggregate_zone_prod(gdf_plants, kanton_to_zone,
                             kanton_col=kanton_col, collapse_to=None)
    cf_default = cf_per_et.get('Andere', 0.40)
    return {
        z: sum(mw * cf_per_et.get(et, cf_default) for et, mw in ets.items())
        for z, ets in zp.items()
    }
