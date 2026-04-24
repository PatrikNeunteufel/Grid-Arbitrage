"""lib.simulation — Batterie-Dispatch-Simulation.

Eine Funktion:

* ``simulate_battery_dispatch`` — Schwellenwert-Dispatch-Modell auf Basis
  tagesbasierter Preisquantile (p_charge, p_discharge). Kern-Logik aus NB03
  extrahiert, konsolidiert NB03.simulate_battery und
  K_06.simulate_battery_reactive (Byte-gleiche Schleifen-Logik).

K_99.sim_arbitrage ist bewusst NICHT hier — es ist ein eigenständiges,
schlankeres Modell mit anderer Parametrierung (globale Constants statt
Funktions-Args) und anderen SoC-Bounds-Berechnungen.
"""
from __future__ import annotations


def simulate_battery_dispatch(prices_df, capacity_kwh, power_kw,
                              efficiency, charge_q, discharge_q,
                              soc_min_pct, soc_max_pct):
    """Schwellenwert-Dispatch auf Basis tagesbasierter Preisquantile.

    Regel pro Stunde:
      LADEN      : Preis ≤ p(charge_q) des Tages  UND  SoC < SoC_max
      ENTLADEN   : Preis ≥ p(discharge_q) des Tages  UND  SoC > SoC_min
      sonst      : idle

    Break-even-Bedingung (Dispatch lohnt sich nur wenn):
        p(discharge_q) × η  >  p(charge_q)
    Äquivalent:
        Spread  >  Spread_min  =  p(charge_q) × (1/η − 1)

    Parameter
    ---------
    prices_df : pd.DataFrame
        Muss Spalten ``timestamp`` und ``price_eur_mwh`` enthalten (jede Zeile
        = 1 Stunde).
    capacity_kwh : float
        Batterie-Energiekapazität in kWh.
    power_kw : float
        Leistungs-Limit pro Stunde (sowohl Laden als auch Entladen).
    efficiency : float
        Roundtrip-Effizienz, 0 < η ≤ 1 (typisch 0.90–0.92). Wird als
        ``sqrt(η)`` symmetrisch auf Lade- und Entlade-Pfad verteilt.
    charge_q : float
        Quantil für Ladeschwelle, 0 ≤ q < 1 (typisch 0.25).
    discharge_q : float
        Quantil für Entladeschwelle, 0 < q ≤ 1 (typisch 0.75).
    soc_min_pct, soc_max_pct : float
        SoC-Grenzen als Bruchteil der Kapazität (typisch 0.10 / 0.90).

    Return
    ------
    pd.DataFrame mit Spalten
        ``timestamp``      — wie Input
        ``action``         — 'charge' | 'discharge' | 'idle'
        ``cashflow_eur``   — Geldstrom pro Stunde (negativ beim Laden,
                             positiv beim Entladen; Einheit EUR)
        ``grid_delta_kw``  — Netzbezug (positiv) bzw. -einspeisung (negativ)
                             in kWh (Leistung × 1h)

    Notes
    -----
    Optimierung: Tages-Quantile werden einmal vorab berechnet, nicht für
    jede Zeile neu — reduziert Laufzeit von O(n²) auf O(n).
    """
    import numpy as np
    import pandas as pd

    # ── Schritt 1: Tages-Quantile vorab berechnen ─────────────────────────────
    df = prices_df[['timestamp', 'price_eur_mwh']].copy()
    df['date'] = df['timestamp'].dt.date
    day_q = df.groupby('date')['price_eur_mwh'].agg(
        p_lo=lambda x: x.quantile(charge_q),
        p_hi=lambda x: x.quantile(discharge_q),
    )
    df = df.join(day_q, on='date')

    # ── Schritt 2: NumPy-Arrays — kein iterrows() ─────────────────────────────
    prices   = df['price_eur_mwh'].to_numpy()
    p_los    = df['p_lo'].to_numpy()
    p_his    = df['p_hi'].to_numpy()
    n        = len(prices)

    soc_max  = capacity_kwh * soc_max_pct
    soc_min  = capacity_kwh * soc_min_pct
    sqrt_eff = efficiency ** 0.5
    soc      = capacity_kwh * 0.5   # Startzustand

    actions    = np.empty(n, dtype='U10')
    cashflows  = np.zeros(n)
    grid_delta = np.zeros(n)

    # ── Schritt 3: Simulation ────────────────────────────────────────────────
    for idx in range(n):
        price = prices[idx]
        if price <= p_los[idx] and soc < soc_max:
            e = min(power_kw, (soc_max - soc) / sqrt_eff)
            soc += e * sqrt_eff
            actions[idx]    = 'charge'
            cashflows[idx]  = -(e * price / 1000)
            grid_delta[idx] = +e
        elif price >= p_his[idx] and soc > soc_min:
            e = min(power_kw, soc * sqrt_eff)
            soc -= e / sqrt_eff
            actions[idx]    = 'discharge'
            cashflows[idx]  = +(e * sqrt_eff * price / 1000)
            grid_delta[idx] = -e
        else:
            actions[idx] = 'idle'

    return pd.DataFrame({
        'timestamp':     df['timestamp'].values,
        'action':        actions,
        'cashflow_eur':  cashflows,
        'grid_delta_kw': grid_delta,
    })
