"""lib.data_fetchers — HTTP-/API-Loader mit Retry-Logik.

Aktuell eine Funktion:

* ``fetch_entsoe_yearly`` — Wrapper um beliebige ENTSO-E-Queries mit
  jahresweisem Download und 503-Retry. Die konkrete Query (Preise, Last,
  Grenzflüsse, Erzeugung, ...) wird als Callable übergeben.

Der Vorteil gegenüber spezifischen Wrappern (z.B. ``fetch_prices_year``,
``fetch_load_year``) ist, dass neue Queries ohne Änderung am Modul
hinzugefügt werden können — einfach eine andere ``client.query_*``-Methode
in die Lambda-Funktion packen.

BFE/swisstopo-Downloads sind bewusst NICHT hier — sie passieren nur an
einer Stelle (K_01) und haben kein Duplikations-Problem.
"""
from __future__ import annotations


def fetch_entsoe_yearly(query_fn, year, max_retries=3, wait_s=20,
                        tz='Europe/Zurich'):
    """Ruft eine ENTSO-E-Query jahresweise mit 503-Retry auf.

    ENTSO-E gibt bei Serverüberlastung HTTP 503 zurück. Jahresweiser Abruf
    mit Wartezeit zwischen Versuchen ist zuverlässiger als ein grosser
    Mehrjahresrequest.

    Parameter
    ---------
    query_fn : callable
        Funktion mit Signatur ``query_fn(start, end) -> result``. Typisch
        als Lambda: ``lambda s, e: client.query_day_ahead_prices('CH', start=s, end=e)``.
    year : int
        Jahr (z.B. 2023). Start = 1.1. 00:00, End = 31.12. 23:00 in ``tz``.
    max_retries : int, default 3
        Maximale Anzahl Versuche pro Jahr.
    wait_s : int, default 20
        Sekunden Pause zwischen Retries.
    tz : str, default 'Europe/Zurich'
        Timezone für die Jahres-Grenzen.

    Return
    ------
    Das Ergebnis von ``query_fn`` — typisch ein pandas DataFrame oder Series
    (abhängig von der ENTSO-E-Methode und -Version).

    Raises
    ------
    HTTPError
        Wenn nach ``max_retries`` weiterhin 503 kommt, oder bei anderen
        HTTP-Fehlern (z.B. 401 — ungültiger API-Key).

    Beispiele
    ---------
    Day-Ahead-Preise:

        client = EntsoePandasClient(api_key=key)
        ts = fetch_entsoe_yearly(
            lambda s, e: client.query_day_ahead_prices('CH', start=s, end=e),
            year=2023
        )

    Grenzflüsse CH -> DE:

        flows = fetch_entsoe_yearly(
            lambda s, e: client.query_crossborder_flows('CH', 'DE', start=s, end=e),
            year=2023
        )
    """
    import time
    import pandas as pd
    from requests.exceptions import HTTPError

    start = pd.Timestamp(f'{year}-01-01',       tz=tz)
    end   = pd.Timestamp(f'{year}-12-31 23:00', tz=tz)

    for attempt in range(1, max_retries + 1):
        try:
            return query_fn(start, end)
        except HTTPError as e:
            if '503' in str(e) and attempt < max_retries:
                print(f'  Jahr {year}: 503 → Versuch {attempt}/{max_retries}, '
                      f'warte {wait_s}s...')
                time.sleep(wait_s)
            else:
                raise  # Anderer Fehler oder max Retries erreicht
