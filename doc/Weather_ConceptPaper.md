# Concept Paper: Strompreis-Wetter-Korrelationsanalyse

**Projekt:** SC26_Gruppe_2 — Battery Storage Arbitrage Economics  
**Status:** Geplante Erweiterung (post Kür-Freeze 30.03.2026)  
**Autor:** Patrik Neunteufel  
**Datum:** 2026-04-14  

---

## 1. Motivation

Strompreise an liberalisierten Spot-Märkten werden massgeblich durch das Wetter beeinflusst. Der sogenannte **Merit-Order-Effekt** beschreibt, wie erneuerbare Einspeisung (Wind, Solar) günstige konventionelle Kraftwerke aus dem Markt verdrängt und so die Spot-Preise senkt. Umgekehrt führen wetterbedingte Engpässe ("Dunkelflaute") zu Preisspitzen — genau jene Situationen, in denen Batterie-Arbitrage am profitabelsten ist.

Dieses Notebook untersucht diese Kausalität quantitativ und schafft damit eine methodische Grundlage für:
- Bessere Arbitrage-Strategie-Optimierung (→ K_Strategie)
- Fundierung der FCR-Relevanz in Peaksituationen (→ K_FCR)
- Differenzierung zwischen Ländern im Rahmen der geplanten Ländererweiterung

---

## 2. Forschungsfragen

1. Wie stark korreliert die Windeinspeisung mit dem Day-Ahead-Spotpreis in CH, DE, AT?
2. Welchen Einfluss hat die Temperatur (Heiz-/Kühlbedarf) auf das Preisniveau?
3. Lassen sich Preisspitzen (Top-10%-Stunden) durch Wettervariablen vorhersagen?
4. Unterscheiden sich die Korrelationsprofile signifikant zwischen Ländern (CH hydro-dominiert vs. DE windreich)?

---

## 3. Methodik

### 3.1 Datenbeschaffung

| Quelle | Inhalt | Granularität | API |
|---|---|---|---|
| **Open-Meteo** | Wind (10m, 100m), Temperatur, Globalstrahlung | Stündlich, historisch | REST, kostenlos, kein Key |
| **ENTSO-E** (bereits integriert) | Actual Generation per Source (Wind on/offshore, Solar) | Stündlich | entsoe-py |
| **ENTSO-E** (bereits integriert) | Day-Ahead Prices | Stündlich | entsoe-py |

Open-Meteo-Koordinaten werden je Bieterzone auf repräsentative Standorte gemappt (z.B. DE: Nordsee-Küste für Windprofil, München für Temperatur/Solar).

### 3.2 Analyseschritte

1. **Datenladen & Alignment** — Zeitreihen auf stündliche UTC-Basis synchronisieren
2. **Explorative Analyse** — Scatter-Plots Preis vs. Wettervar., saisonal aufgeteilt
3. **Korrelationsmatrix** — Pearson + Spearman (robust gegen Ausreisser)
4. **Lag-Analyse** — Preisreaktion auf Wetterveränderungen (0–6h Versatz)
5. **Extremwert-Analyse** — Wetterbedingungen bei Preis-Top/Bottom-10%
6. **Ländervergleich** — Profile CH / DE / AT nebeneinander

### 3.3 Visualisierungen (geplant)

- Heatmap: Monat × Tageszeit, gefärbt nach mittlerem Preis, überlagert mit Windsignal
- Scatter: Windeinspeisung (GW) vs. Spotpreis (EUR/MWh), nach Saison gefärbt
- Zeitreihe: Dunkelflaute-Episoden markiert mit Preisspitzen
- Balkendiagramm: Korrelationskoeffizienten im Ländervergleich

---

## 4. Technische Anforderungen

```python
# Neue Abhängigkeiten (zu requirements.txt hinzufügen)
openmeteo-requests
requests-cache
retry-requests
```

Alle übrigen Abhängigkeiten (pandas, matplotlib, numpy, scipy) bereits vorhanden.

### SSOT-Integration

```json
// config.json — Ergänzung unter "kuer" (Key-Name bei Umsetzung gemäss vergebener Nummer)
"weather": {
  "locations": {
    "CH": {"lat": 46.8, "lon": 8.2, "label": "Schweiz (Zentrum)"},
    "DE": {"lat": 53.6, "lon": 8.5, "label": "Deutschland (Nordsee-Küste)"},
    "AT": {"lat": 47.8, "lon": 13.0, "label": "Österreich (Salzburg)"}
  },
  "weather_variables": ["wind_speed_10m", "wind_speed_100m", "temperature_2m", "shortwave_radiation"],
  "correlation_methods": ["pearson", "spearman"],
  "price_quantile_threshold": 0.10
}
```

---

## 5. Einordnung im Notebook-Pipeline

**Pflicht/Kür:** Eindeutig **Kür**  
**Abhängigkeiten:** Preisdaten aus K_Pflicht bereits verfügbar; Wetterdaten werden eigenständig im ersten Kür-Notebook geladen, das sie benötigt (Konvention)  
**Ländererweiterung:** `BZ_CODE`-parametrisiert, kompatibel mit allen ~30 ENTSO-E-Zonen

Outputs via `transfer.json`:
- Korrelationskoeffizienten (je Land, je Wettervar.)
- Extremwert-Statistiken
- Länder-Profile

---

## 6. Erwartete Erkenntnisse

| Hypothese | Erwartetes Ergebnis |
|---|---|
| Wind ↑ → Preis ↓ (DE) | Starke negative Korrelation (r ≈ −0.4 bis −0.6) |
| Wind ↑ → Preis ↓ (CH) | Schwächere Korrelation (Hydro dämpft Effekt) |
| Temperatur-Extrema → Preis ↑ | U-förmige Beziehung (Heizen + Kühlen) |
| Dunkelflaute-Stunden → Top-Preise | Überlappung >50% bei DE |

Diese Erkenntnisse würden direkt die Arbitrage-Timing-Strategie verfeinern: Ladezeitpunkte präferentiell bei hoher Windeinspeisung, Entladung bei prognostizierter Dunkelflaute.

---

## 7. Aufwandschätzung

| Phase | Aufwand |
|---|---|
| Datenbeschaffung & API-Integration | ~2h |
| Analyse & Korrelationsberechnung | ~3h |
| Visualisierungen | ~3h |
| Ländervergleich & Dokumentation | ~2h |
| **Total** | **~10h** |

---

## 8. Ausblick / Folgeschritte

- **ML-Erweiterung:** Einfaches Regressionsmodell (XGBoost) zur Preisprognose auf Basis von Wettervorhersagen — Grundlage für prädiktive Ladestrategie
- **Intraday-Dimension:** Kombination mit ENTSO-E Intraday-Preisen für kurzfristige Wetterreaktionen
- **Visualisierungs-Dashboard:** Interaktives Länder-Switching (Jupyter Widgets / ipywidgets)

---

*Dieses Concept Paper dient als Planungsgrundlage. Notebook-Nummer wird bei Umsetzung gemäss K_##-Schema vergeben. Implementierung frühestens nach Abgabe 11.05.2026.*
