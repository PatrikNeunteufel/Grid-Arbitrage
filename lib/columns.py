"""lib.columns — DataFrame-Spalten-Helfer.

Eine Funktion:

* ``find_col`` — sucht in einem DataFrame die erste Spalte, deren Name
  (case-insensitiv) eines der gegebenen Keywords enthält. Nützlich für
  heterogene externe Datenquellen, wo die Spalten nicht genau gleich heissen
  (BFE vs. BFS vs. swisstopo etc.).
"""
from __future__ import annotations


def find_col(df, *kws):
    """Sucht die erste Spalte in ``df``, deren Name ein Keyword enthält.

    Keyword-Match ist case-insensitiv und sucht Substring. Reihenfolge in
    ``kws`` bestimmt Priorität: das erste Keyword, das einen Match liefert,
    gewinnt.

    Parameter
    ---------
    df : pd.DataFrame
        DataFrame mit zu durchsuchenden Spalten.
    *kws : str
        Keywords (z.B. ``'canton'``, ``'kanton'``, ``'kt'``).

    Return
    ------
    str oder None
        Name der ersten matching Spalte, oder None wenn kein Match.

    Beispiel
    --------
    >>> col = find_col(gdf_bfe, 'SubCategory', 'Kategorie', 'Tech')
    >>> col
    'SubCategory'
    """
    for kw in kws:
        for c in df.columns:
            if kw.lower() in c.lower():
                return c
    return None
