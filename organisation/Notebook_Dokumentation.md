# Notebook-Dokumentation — Grid-Arbitrage mit Batteriespeichern
**SC26_Gruppe_2 · ZHAW CAS Information Engineering Scripting**

> **Zielgruppe:** Grundlegendes Python vorhanden, Data-Science-Einsteiger.
> Jede Code-Zelle wird erklärt: was sie tut, warum, welche Library-Funktionen dabei eine Rolle spielen.
> Jede Library-Funktion wird nur beim **ersten Auftreten** in einem eigenen Tabellenabschnitt beschrieben.
>
> **Projektidee:** Kaufe Strom günstig (Preis-Tief), speichere ihn in einer Batterie, speise teuer ein (Preis-Hoch). Lohnt sich das in der Schweiz?

---

## Projektstruktur

```
SC26_Gruppe_2/
├── sync/config.json          ← SSOT: alle Parameter (User pflegt, Notebooks lesen)
├── sync/transfer.json        ← berechnete Ergebnisse zwischen Notebooks
├── sync/dataindex.csv        ← Datenquellen-Register (append-only)
├── organisation/             ← O_01–O_04, O_99 (Querschnittsdokumente)
├── notebooks/                ← NB00–NB04 (Pflicht, Datenpipeline)
├── kuer/                     ← K_00–K_10, K_99 (Kür, erweiterbar)
├── data/raw/ processed/ intermediate/
└── output/charts/<SZ_AKTIV>/
```

**Pfad-Auflösung:** Alle Notebooks liegen eine Ebene unter dem Projektstamm. Pfade werden immer relativ aufgelöst: `BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), '..'))`.

---

# Organisation (`organisation/`)

## O_01 — Projektübersicht (`O_01_Project_Overview.ipynb`)
Einstiegspunkt des Projekts. Enthält Motivation, Methodik, Notebook-Map, Ordnerstruktur, Projektplan, Aufgabenverteilung und potenzielle Erweiterungen. Kein fachlicher Recheninhalt ausser der Projektplan-Tabelle.

### Zelle 1 — Projektplan
**Was passiert:** Status-Konstanten werden definiert (`⬜ Offen`, `🔄 In Arbeit`, `✅ Erledigt`). Eine Liste aller Projektaufgaben mit Verantwortlichkeit, Frist und Status wird als formatierte Tabelle ausgegeben. Versionsanzeige von `pandas` und Ausführungszeitpunkt.
**Warum so:** Ein einziger Blick zeigt den kompletten Projektstatus. `pandas` ist die einfachste Lösung für eine formatierte Tabelle im Notebook.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.DataFrame()` | `pandas` | Erstellt einen tabellarischen Datensatz (Zeilen × Spalten) aus einer Python-Liste oder einem Dictionary. Grundbaustein für alle Tabellenoperationen im Projekt. |

---

## O_02 — Glossar (`O_02_Glossar.ipynb`)
Reines Markdown-Notebook. Kein ausführbarer Code. Definiert alle Fachbegriffe aus Energiemarkt, Finanzen, Technik und Statistik mit NB-Querverweisen. Enthält Anker-IDs (`<a id="g-...">`) für direkte Verlinkung aus anderen Notebooks.

Abschnitte: Energiemarkt · Finanzen & Wirtschaftlichkeit · Batterie & Technik · Statistik & Modell · Projektspezifische Begriffe · Abkürzungen.

Neu in dieser Version: Einträge für **Dispatch-Break-even-Bedingung** (`p(discharge_q) × η > p(charge_q)`), **Mindest-Spread** (`Spread_min = p(charge_q) × (1/η − 1)`) und **Relativer Effizienzverlust** (`(1/η − 1)`).

---

## O_03 — Konventionen (`O_03_Konventionen.ipynb`)
Lebendes Regelwerk für alle Notebooks. Die einzige Code-Zelle zeigt eine Muster-Lade-Sequenz (vollständig auskommentiert — nur Referenz, kein ausführbarer Code).

Themen: Markdown-Konventionen · Konfigurationsabhängige Werte (⚙/📊-Marker) · Zentrale Konfiguration (`../sync/config.json`) · Datenzeitraum-Empfehlungen · Ergebnistransfer (`../sync/transfer.json`) · Chart-Naming · Visualisierungskonventionen · Abschlussblock · Review-Checkliste · Musterzellen · Sprach- & Terminologiekonvention · Ordnerstruktur & Pfad-Konvention · Notebook-Struktur Pflicht vs. Kür · Kür-Erweiterbarkeit.

**Sektion 12.3 (Hinweis):** `01b_Daten_Sim.ipynb` und `02b_Sim_Analyse.ipynb` wurden per 15.04.2026 entfernt. `MODE='sim'` ist in verbleibenden Notebooks als toter Code erhalten, aber nicht mehr unterstützt.

---

## O_04 — Review-Protokoll (`O_04_Review_Protokoll.ipynb`)
Dokumentiert Qualitätssicherung, rollenbasierte Reviews und protokollierte Korrektur-Iterationen. Eine Code-Zelle liest `../sync/transfer.json` und zeigt eine Verifikationsübersicht.

---

## O_99 — Datenprovenienz (`O_99_Datenprovenienz.ipynb`)
Dokumentiert alle Datenquellen: Herkunft, Lizenz, Verarbeitungsschritte. **Manuell ausführen** — nicht Teil von `run_all`.

### Zellen 1–2 — Setup & dataindex laden
**Was passiert:** Libraries laden, Versionsanzeige. `../sync/dataindex.csv` laden — das Register, das NB01 automatisch befüllt hat. Alle Einträge nach Typ kategorisieren.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.notna()` | `pandas` | Prüft elementweise ob Werte NICHT NaN sind. Gegenteil von `pd.isna()`. Hier für bedingte Formatierung: Zeilenzahl nur anzeigen wenn vorhanden. |

### Zellen 3–7 — Charts A–D
**Was passiert:** Chart A: Zeitlinie aller dataindex-Einträge als Scatter-Plot. Chart B: Dateigrössenvergleich aller aktiven Dateien. Chart C: Pipeline-Flussdiagramm (Datenfluss von Rohdaten durch alle Notebooks). Chart D: Versionshistorie (active/superseded/error-Anteile) und Pipeline-Volumen.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `import matplotlib.dates as mdates` | `matplotlib.dates` | Modul für datumsbezogene Achsenformatierung. `mdates.DateFormatter('%b %Y')` formatiert Ticks als 'Jan 2024'. `mdates.AutoDateLocator()` wählt automatisch sinnvolle Tick-Abstände. |
| `mpatches.FancyBboxPatch()` | `matplotlib.patches` | Rechteck mit abgerundeten Ecken. `boxstyle='round,pad=0.3'` = abgerundete Ecken mit Innenabstand. Hier für Pipeline-Flussdiagramm-Knoten. |

---

# Pflicht (`notebooks/`)

## NB01 — Daten laden (`01_Daten_Laden.ipynb`)
Einziger Zweck: echte Rohdaten von der ENTSO-E-API herunterladen und auf der Festplatte speichern. Alle nachgelagerten Notebooks bauen darauf auf.

### Zelle 1 — Abhängigkeitsprüfung
**Was passiert:** Für vier Pakete (`pandas`, `requests`, `numpy`, `entsoe-py`) wird geprüft, ob sie installiert sind. Fehlt eines, wird es automatisch über `pip install` nachinstalliert.
**Warum so:** Jupyter-Notebooks laufen auf unterschiedlichen Rechnern. Diese Zelle stellt sicher, dass das Notebook überall ohne manuelle Installation funktioniert.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `subprocess.check_call()` | `subprocess` | Führt einen externen Befehl aus (hier: `pip install`) und blockiert bis zum Abschluss. Wirft eine Exception wenn der Befehl fehlschlägt. |
| `__import__()` | `builtins` | Versucht ein Modul zu importieren. Hier für Existenzprüfung: schlägt fehl → `ImportError` → Paket wird nachinstalliert. |

### Zelle 2 — Konfiguration laden
**Was passiert:** Libraries werden geladen, `../sync/config.json` wird als Python-Dictionary `CFG` eingelesen. Daraus werden Reload-Schalter, Datenzeitraum und Verzeichnispfade extrahiert. Die Hilfsfunktion `needs_download()` prüft ob eine Datei fehlt, zu klein ist oder ein Neuladen erzwungen wird.
**Warum so:** `../sync/config.json` ist der einzige Ort, wo Einstellungen gesetzt werden (Single Source of Truth). Code enthält nie hardcodierte Pfade oder Parameter.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `json.load()` | `json` | Liest eine JSON-Datei und gibt ein Python-Dictionary/-List zurück. Hier für `../sync/config.json` (Einstellungen) und `../sync/transfer.json` (Notebook-zu-Notebook-Übergabe). |
| `json.dump()` | `json` | Schreibt ein Python-Objekt als JSON in eine Datei. `indent=2` für lesbare Formatierung, `ensure_ascii=False` für Umlaute. |
| `os.path.join()` | `os` | Setzt Pfadteile plattformunabhängig zusammen (Backslash auf Windows, Slash auf Linux/Mac). Immer dieser Funktion statt Stringverkettung. |
| `os.makedirs()` | `os` | Erstellt ein Verzeichnis inkl. aller fehlenden Elternverzeichnisse. `exist_ok=True` unterdrückt den Fehler wenn das Verzeichnis bereits existiert. |
| `os.path.exists()` | `os` | Prüft ob ein Pfad (Datei oder Verzeichnis) existiert. Gibt `True`/`False` zurück. |
| `os.path.getsize()` | `os` | Gibt die Dateigrösse in Bytes zurück. Wird zur Validierung genutzt: Datei existiert aber ist zu klein → unvollständig, neu laden. |

### Zelle 3 — Datenregister-Hilfsfunktionen
**Was passiert:** Zwei Funktionen werden definiert. `log_dataindex()` schreibt jeden geladenen Datensatz in `../sync/dataindex.csv` — ein historisches Register mit Zeitstempel, Herkunft und Status. Wenn ein Eintrag für dieselbe Datei bereits existiert, wird der alte als `superseded` markiert. `log_missing()` schreibt fehlende Daten in `data/missing.txt`.
**Warum so:** Forschungsprojekte brauchen Nachvollziehbarkeit: Woher kommen die Daten? Von wann? Wurden sie aktualisiert? Das beantwortet die `../sync/dataindex.csv` automatisch.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.concat()` | `pandas` | Fügt mehrere DataFrames zusammen (vertikal oder horizontal). Ersetzt das veraltete `df.append()`. `ignore_index=True` setzt den Index neu. |
| `datetime.utcnow()` | `datetime` | Gibt den aktuellen UTC-Zeitstempel zurück. `.isoformat(timespec='seconds')` formatiert als `2024-01-15T10:30:00` — maschinenlesbar und sortierbar. |

### Zelle 4 — API-Verbindung & Spotpreis-Download
**Was passiert:** Der ENTSO-E API-Schlüssel wird aus `../sync/config.json` gelesen. Dann wird geprüft, ob der API-Endpunkt erreichbar ist (HTTP-Status-Interpretation: 400 = erreichbar aber fehlende Parameter, 401 = ungültiger Key, 503 = Server überlastet). Eine Funktion `_fetch_prices_year()` lädt Day-Ahead-Spotpreise für ein einzelnes Jahr mit bis zu 3 automatischen Wiederholungsversuchen bei 503-Fehlern.
**Warum so:** Die ENTSO-E-API ist gelegentlich überlastet (503). Jahresweise Anfragen mit Retry-Logik ist robuster als ein einzelner Gesamtrequest. API-Keys werden nie im Code gespeichert — immer in der Config.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `requests.get()` | `requests` | Sendet einen HTTP GET-Request. `params=` für URL-Parameter, `timeout=` verhindert ewiges Warten. |
| `pd.Timestamp()` | `pandas` | Erzeugt einen einzelnen Zeitpunkt mit Zeitzoneninfo. `tz='Europe/Zurich'` ist wichtig für korrekte Winterzeit/Sommerzeit-Behandlung. |
| `EntsoePandasClient()` | `entsoe` | Client für die ENTSO-E Transparency Platform API. Wandelt die komplexen XML-Antworten automatisch in pandas DataFrames/Series um. |
| `.query_day_ahead_prices()` | `entsoe` | Lädt Day-Ahead-Spotpreise für ein Land und Zeitraum (hier Schweiz `'CH'`). Gibt eine pandas Series zurück: Index = Timestamp, Werte = EUR/MWh. |
| `.query_load()` | `entsoe` | Lädt die tatsächliche Systemlast (Netzlast) für ein Land. Index = Timestamp, Werte = MW. |

### Zellen 5 & 7 — Verifikation
**Was passiert:** Nach jedem Download: Shape, Zeitraum, Nullwerte und Wertebereich ausgeben, erste Zeilen anzeigen.
**Warum so:** Datenfehler (falsche Einheit, fehlende Monate, API-Antwortformat geändert) fallen sofort auf.

### Zelle 6 — Netzlast-Download
**Was passiert:** Strukturell identisch zu Zelle 4 — gleiche Retry-Logik, andere API-Methode (`query_load`). Resultat: stündliche Systemlast des Schweizer Regelblocks in GW.

### Zelle 8 — Transfer-Output
**Was passiert:** Datenzeitraum (Startjahr, Endjahr, Anzahl tatsächlicher Jahre) wird in `../sync/transfer.json` geschrieben. NB02 liest diesen Wert für korrekte Jahresdurchschnitt-Berechnungen.
**Warum so:** `../sync/transfer.json` ist der Kommunikationskanal zwischen Notebooks. Kein Notebook macht Annahmen über Datenzeiträume — es liest immer aus dieser Datei.

### Zelle 9 — Abschlusskontrolle
**Was passiert:** Alle Output-Dateien werden auf Existenz und Mindestgrösse geprüft. ✅/❌ Ausgabe. Inhalt von `../sync/dataindex.csv` anzeigen.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `os.listdir()` | `os` | Gibt alle Dateien und Verzeichnisse in einem Ordner als Liste zurück. Hier für die Abschlusskontrolle: welche Dateien wurden erzeugt? |

---

## NB02 — Daten Bereinigung (`02_Daten_Bereinigung.ipynb`)
Lädt die Rohdaten aus `data/raw/` und bereinigt sie zu analysierbaren Zeitreihen in `data/processed/`. Kein Dispatch, keine Wirtschaftlichkeitsrechnung — nur Datenqualität.

### Zellen 1–3 — Setup, Konfiguration, Transfer
**Was passiert:** Libraries importieren, `../sync/config.json` als `CFG` laden. Reload-Schalter, Datenzeitraum und Verzeichnisse extrahieren. Dann `n_years` aus `../sync/transfer.json` lesen (von NB01 geschrieben). `log_dataindex()`-Hilfsfunktion definieren (identisch zu NB01, lokal weil jedes Notebook autark lauffähig ist).
**Warum so:** SSOT-Prinzip. Alle Parameter aus Config, Datenzeitraum aus Transfer-Datei.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `json.loads()` | `json` | Parst JSON direkt aus einem String (nicht aus einer Datei). Hier zum Lesen einer Datei mit leerem Inhalt-Guard: `json.loads(f.read() or '{}')`. |
| `warnings.filterwarnings()` | `warnings` | Unterdrückt Python-Warnmeldungen. `'ignore'` schaltet alle aus — sinnvoll für Notebooks um die Ausgabe lesbar zu halten. |

### Zelle 4 — Rohdaten laden
**Was passiert:** `data/raw/ch_spot_prices_raw.csv` und `data/raw/ch_netzlast_raw.csv` einlesen. Timestamps auf UTC normieren. Shape und Wertebereich prüfen.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.read_csv()` | `pandas` | Lädt eine CSV-Datei von der Festplatte in einen DataFrame. `parse_dates` konvertiert Spalten direkt zu Datetime-Objekten. |
| `pd.to_datetime()` | `pandas` | Konvertiert Strings oder Unix-Timestamps in pandas-Timestamp-Objekte. `utc=True` normiert auf UTC-Zeitzone. |

### Zelle 5 — Bereinigung
**Was passiert:** Bereinigung in 5 Schritten:
1. Vollständigen Stundenraster erzwingen: `pd.date_range(...) + .reindex()` → fehlende Stunden werden als NaN eingefügt
2. Lücken bis 3h linear interpolieren
3. Längere Lücken mit `.ffill(limit=6).bfill(limit=6)` auffüllen
4. Extreme Ausreisser kappen: < -500 oder > 3000 EUR/MWh
5. Zeitfeatures ableiten: Stunde, Monat, Wochentag, Jahreszeit
Bereinigte Daten werden als `data/processed/ch_spot_prices_clean.csv` gespeichert.
**Warum so:** Vollständiger Stundenraster ist Voraussetzung für tagesbasierte Dispatch-Simulation. Ausreisser würden die p25/p75-Schwellenwerte verzerren.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.date_range()` | `pandas` | Erzeugt einen lückenlosen Zeitreihen-Index. `freq='1h'` = stündlich, `tz='UTC'`, `name='timestamp'` setzt den Spaltennamen nach `reset_index()` automatisch. |
| `.set_index()` | `pandas` | Setzt eine Spalte als DataFrame-Index. Wird mit `.reindex()` kombiniert um fehlende Zeitstempel einzufügen. |
| `.reindex()` | `pandas` | Richtet den DataFrame auf einen neuen Index aus. Fehlende Werte werden als `NaN` eingefügt. |
| `.reset_index()` | `pandas` | Verwandelt den Index zurück in eine normale Spalte. Typisch nach `set_index()` + `reindex()`. |
| `.interpolate()` | `pandas` | Füllt NaN-Werte durch lineare Interpolation. `limit=3` begrenzt auf maximal 3 aufeinanderfolgende NaN. |
| `.ffill()` | `pandas` | Forward Fill: füllt NaN mit dem letzten bekannten Wert. `limit=6` begrenzt die Anzahl auffüllbarer NaN. |
| `.bfill()` | `pandas` | Backward Fill: füllt NaN mit dem nächsten bekannten Wert. Wird nach `ffill()` für verbleibende NaN am Anfang verwendet. |
| `.clip()` | `pandas / numpy` | Begrenzt Werte auf ein Intervall [min, max]. Verhindert Ausreisser-Effekte auf Berechnungen. |
| `.dt.hour` | `pandas (.dt)` | Zugriff auf Datetime-Komponenten. `.dt.hour` = Stunde (0–23), `.dt.month` = Monat (1–12), `.dt.dayofweek` = Wochentag (0=Montag). |

### Zelle 6 — Verifikation
**Was passiert:** Shape, Nullwerte, Wertebereich und erste Zeilen der bereinigten Preise ausgeben.

---

## NB03 — Daten Analyse (`03_Daten_Analyse.ipynb`)
Das Herzstück des Projekts. Liest bereinigte Daten aus `data/processed/`, simuliert den Batterie-Dispatch, berechnet wirtschaftliche Kennzahlen und schreibt Ergebnisse in `../sync/transfer.json`.

### Zellen 1–3 — Setup, Konfiguration, Transfer
**Was passiert:** Identische Initialisierungssequenz wie NB02 — Libraries, `../sync/config.json`, `n_years` aus `../sync/transfer.json`, `log_dataindex()`-Helfer. Dann alle Simulations- und Wirtschaftlichkeitsparameter als Named Aliases laden: `EFFICIENCY`, `CHARGE_Q`, `DISCHARGE_Q`, `SOC_MIN_PCT`, `SOC_MAX_PCT`, `CAPEX_EUR_KWH`, `OPEX_RATE`, `LIFETIME_J`.
**Warum Named Aliases?** SSOT-Prinzip: Parameter kommen aus `../sync/config.json`, aber Funktions-Defaults dürfen diese nie hardcoden — Named Aliases machen den Fluss sichtbar und verhindern versehentliche Duplikation.

### Zelle 4 — Bereinigte Daten laden
**Was passiert:** `data/processed/ch_spot_prices_clean.csv` und `data/processed/ch_netzlast_clean.csv` einlesen. Timestamps auf UTC normieren.

### Zelle 5 — Tagesprofil & Spread-Analyse
**Was passiert:** Für jede Stunde des Tages (0–23) werden Durchschnitt und Standardabweichung des Preises berechnet. Die günstigsten und teuersten Stunden werden identifiziert. Arbitrage-Spread und saisonale Durchschnitte werden ausgegeben.
**Warum so:** Beantwortet die Kernfrage: Wie gross ist das Arbitrage-Potential im Tages-Rhythmus?

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.groupby()` | `pandas` | Gruppiert einen DataFrame nach einer oder mehreren Spalten. Ermöglicht Aggregation pro Gruppe. |
| `.agg()` | `pandas` | Wendet mehrere Aggregationsfunktionen auf eine Gruppe an. `agg(mean='mean', std='std')` berechnet Mittelwert und Standardabweichung in einem Durchgang. |
| `.nsmallest()` | `pandas` | Gibt die n kleinsten Werte einer Serie zurück. Hier: die günstigsten Stunden. |
| `.nlargest()` | `pandas` | Gibt die n grössten Werte zurück. Hier: die teuersten Stunden. |

### Zelle 6 — Dispatch-Funktion (Kernfunktion)
**Was passiert:** `simulate_battery()` wird definiert — der algorithmische Kern des Projekts. Das Schwellenwertmodell:
- **Schritt 1:** Für jeden Tag werden p25 und p75 *einmalig vorab* als NumPy-Arrays berechnet (O(n), nicht O(n²))
- **Schritt 2:** Preise und Schwellenwerte werden als NumPy-Arrays extrahiert (kein `iterrows()`)
- **Schritt 3:** Stunden-Simulation: Preis ≤ p(charge_q) UND SoC < soc_max → laden; Preis ≥ p(discharge_q) UND SoC > soc_min → einspeisen; sonst → idle

**Break-even-Bedingung** (direkt im Docstring dokumentiert):
`p(discharge_q) × η > p(charge_q)` — nur wenn diese Bedingung erfüllt ist, deckt der Erlös die Rundlaufverluste. Äquivalent: `Spread > Spread_min = p(charge_q) × (1/η − 1)`. Tage ohne qualifizierten Spread bleiben vollständig **idle**. Siehe Glossar: `O_02_Glossar.ipynb#g-dispatch-breakeven`.

**Warum NumPy?** Für 26.000 Stunden (3 Jahre) wäre `iterrows()` ca. 50× langsamer. NumPy läuft in optimiertem C-Code.
**Warum sequenziell?** Der SoC einer Stunde hängt vom SoC der Vorherigen ab — das kann nicht vektorisiert werden.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.empty()` | `numpy` | Erstellt ein uninitialisiertes Array. Schneller als `np.zeros()` wenn alle Werte sofort überschrieben werden. Hier für das `actions`-Array (Strings). |
| `np.zeros()` | `numpy` | Erstellt ein Array mit lauter Nullen. Für Cashflow- und Grid-Delta-Initialisierung. |
| `.to_numpy()` | `pandas` | Konvertiert eine pandas Series in ein NumPy-Array. Notwendig für die Dispatch-Simulation ohne Python-Overhead. |

### Zellen 7–8 — Simulation aller Segmente
**Was passiert:** `simulate_battery()` wird für alle 4 Segmente ausgeführt (Privat 10 kWh / Gewerbe 100 kWh / Industrie 1 MWh / Utility 10 MWh). Jahreserlös = Gesamterlös ÷ `n_years`. Ergebnisse werden tabellarisch ausgegeben.
**Warum Durchschnitt statt nur ein Jahr?** Jahres-Preise schwanken stark. Durchschnitt über mehrere Jahre ist realistischer.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.dt.year` | `pandas (.dt)` | Extrahiert das Jahr aus einer Datetime-Spalte. `.dt.year.nunique()` = Anzahl verschiedener Jahre — Fallback für `n_years`. |

### Zellen 9–10 — CAPEX / ROI / Amortisation
**Was passiert:** Für jedes Segment: CAPEX (kWh × EUR/kWh aus Config), OPEX (OPEX_RATE × CAPEX/Jahr), Netto-Erlös (Jahreserlös − OPEX), Amortisationszeit (CAPEX ÷ Netto), ROI (Netto/CAPEX × 100). Ergebnisse als CSV nach `data/intermediate/`. Verifikationsausgabe mit Shape und Wertebereich.

### Zelle 11 — Gleichzeitigkeits-Szenarien
**Was passiert:** 4 Szenarien (Status Quo, Moderat 2027, Ambitioniert 2030, Transformativ 2035). Gleichzeitigkeitsrate aus Config (z.B. 40%) skaliert die theoretische Leistung auf die reale Netzentlastung in MW. CSV nach `data/intermediate/`.
**Warum Gleichzeitigkeit?** 50.000 Heimspeicher à 5 kW = 250 MW theoretisch. Bei 40% = 100 MW real — nicht alle speisen zur gleichen Sekunde ein.

### Zellen 12–13 — Spread/Volatilität Zeitreihe
**Was passiert:** Für jeden Tag: Intra-Tag-Spread (p75 − p25). Optimiert: einmaliges `.quantile([0.25, 0.75]).unstack()` statt zweier Lambda-Aufrufe. Tageswerte werden pro Monat zum Median aggregiert. Zusätzlich: Volatilität, Durchschnittspreis, Negativpreis-Stunden. CSV nach `data/intermediate/`. Verifikation auf Shape und Wertebereich.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.quantile()` | `pandas` | Berechnet Quantile einer Serie. `.quantile([0.25, 0.75])` gibt beide auf einmal zurück. Nachgelagertes `.unstack()` verwandelt das MultiIndex-Ergebnis in Spalten. |
| `.unstack()` | `pandas` | Klappt den innersten Index einer MultiIndex-Serie in Spalten um. Typisch nach `.groupby().quantile([...])`. |
| `.merge()` | `pandas` | Verknüpft zwei DataFrames per Schlüsselspalte (wie SQL JOIN). |
| `.dt.to_period()` | `pandas (.dt)` | Konvertiert Timestamps in Zeiträume (z.B. `'M'` = Monat). `.dt.to_timestamp()` wandelt zurück. Für monatliche Aggregation. |
| `.median()` | `pandas` | Berechnet den Median — robuster gegen Ausreisser als der Mittelwert. |

### Zelle 14 — Transfer-Output
**Was passiert:** Alle berechneten Kennzahlen werden in `../sync/transfer.json` geschrieben: Spread-Statistiken, `n_years`, ROI/Erlös/CAPEX pro Segment. Optimiert: `zip()`-basierte Dict-Comprehension statt `iterrows()`.
**Warum?** NB04 (Visualisierungen), K_00 (Business Strategy) und alle nachgelagerten Kür-Notebooks lesen diese Werte statt selbst zu berechnen.

### Zelle 15 — Abschlusskontrolle
**Was passiert:** Alle Pflicht-Ausgabedateien auf Existenz und Mindestgrösse prüfen. ✅/❌ Ausgabe.

---

## NB04 — Visualisierungen (`04_Visualisierungen.ipynb`)
Erzeugt alle Pflicht-Charts (5 Hauptcharts + Einzelplots + Langzeit-Chart). Liest aus `data/processed/` und `data/intermediate/`. Keine eigenen Berechnungen — stellt grafisch dar was NB03 berechnet hat.

### Zellen 1–3 — Setup & Daten laden
**Was passiert:** Libraries laden, `../sync/config.json` lesen, Farb- und Stil-Konstanten aus Config entpacken, `matplotlib.rcParams` global setzen. Dann CSVs aus `data/processed/` und `data/intermediate/` laden. Verifikation aller Eingabe-DataFrames auf Shape und Spalten.
**Warum rcParams global?** Ohne diese Einstellung müsste jeder Chart dieselben Formatierungszeilen wiederholen.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `matplotlib.rcParams.update()` | `matplotlib` | Setzt globale Standardwerte für alle nachfolgenden Plots: Hintergrundfarbe, Tick-Farbe, Schriftgrössen. Gilt für alle Charts des Notebooks. |
| `.map()` | `pandas` | Ersetzt Werte einer Spalte anhand eines Dictionaries. Vektorisiert — kein Python-Loop. |

### Zellen 4–6 — Chart 1: Wirtschaftlichkeit (4 Panels + Einzelplots + Langzeit)
**Was passiert:** Ein 2×2-Panel-Chart. Cashflow-Schleifen nutzen `zip()` statt `itertuples()`, Cashflow als NumPy-Vektoroperation: `-capex + net_annual * years`.
Panel 1: Kumulierte Cashflow-Kurven (symlog-Skala). Panel 2: ROI-Balken mit Ziel-ROI-Linie. Panel 3: Erlös/kWh. Panel 4: CAPEX vs. kumulierter Erlös. Zusätzlich: Einzelplots für Bericht-Einbettung + Langzeit-Chart (20 Jahre).

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.arange()` | `numpy` | Erstellt ein Array mit gleichmässigem Abstand. `np.arange(0, 13)` = [0,1,...,12]. Hier als Jahres-Achse für Cashflow-Kurven. |
| `ax.set_yscale()` | `matplotlib.axes` | Setzt die Skalierung der Y-Achse. `'symlog'` = symmetrisch-logarithmisch: linear nahe der Null, logarithmisch für grosse Beträge. |
| `mticker.FuncFormatter()` | `matplotlib.ticker` | Definiert eine eigene Tick-Beschriftungsformel. Hier: Werte ≥ 1000 als `'123k'` anzeigen. |
| `ax.annotate()` | `matplotlib.axes` | Fügt eine Beschriftung mit Pfeil an einen Datenpunkt. `xy=` = Pfeilspitze, `xytext=` = Textposition. |
| `ax.axhline()` | `matplotlib.axes` | Zeichnet eine horizontale Linie über die gesamte Achsenbreite. Hier für Break-Even-Linie (y=0) und Ziel-ROI-Referenz. |
| `ax.axvline()` | `matplotlib.axes` | Zeichnet eine vertikale Linie über die gesamte Achsenhöhe. Hier für Marker bei Jahr 12. |

### Zellen 7–8 — Chart 2: Heatmap Stunde × Monat
**Was passiert:** Eine 24×12-Matrix (Stunden × Monate) als Heatmap. Optimiert: ein kombinierter `pivot_table(aggfunc=['mean','std'])` statt zwei separater Aufrufe. `origin='lower'` setzt 00:00 unten.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.pivot_table()` | `pandas` | Erstellt eine Kreuztabelle: Zeilen × Spalten mit aggregierten Werten. Hier: Mittelwert des Preises pro Stunde × Monat. |
| `ax.imshow()` | `matplotlib.axes` | Stellt eine Matrix als farbcodiertes Bild (Heatmap) dar. `cmap=` = Farbpalette, `origin='lower'` = Zeile 0 unten. |
| `plt.colorbar()` | `matplotlib.pyplot` | Fügt eine Farblegende neben dem Plot hinzu. |
| `ax.axvspan()` | `matplotlib.axes` | Zeichnet eine farbige vertikale Zone. Hier für Lade- und Einspeisezeitfenster-Markierungen. |

### Zellen 9–10 — Chart 3: Tagesprofil mit Doppelachse
**Was passiert:** Netzlast (GW) und Preis (EUR/MWh) als Doppelachsen-Chart. Die günstigsten Stunden werden blau, die teuersten rot hinterlegt.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `ax.twinx()` | `matplotlib.axes` | Erstellt eine zweite Y-Achse rechts, die dieselbe X-Achse teilt. Ermöglicht zwei verschiedene Skalen im selben Chart. |
| `ax.fill_between()` | `matplotlib.axes` | Füllt die Fläche zwischen zwei Kurven mit Farbe. Alpha-Wert steuert die Transparenz. |
| `mpatches.Patch()` | `matplotlib.patches` | Erzeugt ein farbiges Rechteck für die Legende. Für Legenden-Einträge ohne echtes Plot-Objekt. |
| `ax.get_legend_handles_labels()` | `matplotlib.axes` | Gibt die aktuellen Legenden-Einträge zurück. Zum Zusammenführen von Legenden mehrerer Achsen. |

### Zellen 11–14 — Charts 4 & 5: Szenarien & Saisonales Profil
**Was passiert:** Chart 4: Netzentlastungsszenarien als Balken mit dynamischer Einfärbung via `Normalize` und `cm.get_cmap()`. Chart 5a: Saisonales Tagesprofil für alle 4 Jahreszeiten mit einheitlichen Y-Achsen. Chart 5b: Monatlicher Spread und Dispatch-Stunden. Alle Charts + Einzelplots als PNG gespeichert.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `Normalize()` | `matplotlib.colors` | Skaliert Werte auf [0,1] für Colormaps. `vmin`/`vmax` definieren den Eingabebereich. |
| `cm.get_cmap()` | `matplotlib.cm` | Lädt eine benannte Farbpalette als Objekt. `cmap(value)` gibt die RGBA-Farbe zurück. |
| `cm.ScalarMappable()` | `matplotlib.cm` | Verbindet Colormap mit Normalisierung — für Colorbars ohne direkte `imshow()`/`scatter()`. |

---

## NB00 — Business Case (`00_Business_Case.ipynb`)
Kein eigener Chart-Code. Lädt und zeigt die von NB04 erzeugten PNGs. Reiner Berichtsmodus — das Hauptdokument für den Leistungsnachweis.

### Zellen 1–3 — Setup & Konfiguration
**Was passiert:** `../sync/config.json` laden, Charts-Verzeichnis und ⚙-Prüfwerte definieren. Hilfsfunktion `show_chart()` rendert ein PNG direkt im Notebook.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `display()` | `IPython.display` | Gibt ein Objekt im Notebook-Output aus. Notwendig für `Image`-Objekte. |
| `Image()` | `IPython.display` | Lädt ein Bild von der Festplatte und rendert es im Notebook-Output. `width=` setzt die Anzeigebreite. |

### Abschnitte 1–5 — Bericht
**Was passiert:** Strukturierter Bericht in 5 Abschnitten:
1. **Einleitung** — Forschungsfrage, Projektkontext
2. **Daten** — Datenquellen-Übersicht
3. **Methodik** — Dispatch-Modell (Laden/Einspeisen/Idle-Logik mit Break-even-Bedingung `p75 × η > p25`), Segmente, Wirtschaftlichkeitsrechnung
4. **Ergebnisse** — Chart-Anzeige: Preis-Heatmap, Tagesprofil, Amortisation, ROI, Netzentlastung, Saisonale Rentabilität
5. **Fazit und Empfehlungen** — kein Segment erreicht Ziel-ROI durch reine Arbitrage; Erlösstacking als Lösungsweg

---

# Kür (`kuer/`)

## K_00 — Business Strategy (`K_00_Business_Strategy.ipynb`)
Grösstes Kür-Notebook (63 Zellen). Fasst alle Ergebnisse aus Pflicht und Kür zu einer Strategie-Empfehlung zusammen. Reines Präsentations-/Synthesedokument — lädt Charts aus allen anderen Notebooks und baut daraus eine kohärente Marktargumention auf.

### Setup
**Was passiert:** `../sync/config.json` und `../sync/transfer.json` komplett laden — alle Werte, die NB01–K_99 dort geschrieben haben, sind verfügbar. `check_aktiv()`-Funktion prüft ob abhängige Kür-Notebooks aktiv sind bevor deren Charts geladen werden.

### Strategie-Kapitel (Sektion 1–10)
**Was passiert:** Jede Sektion lädt die relevanten Chart-PNGs und baut daraus eine Argumentation:
- **1** — Marktüberblick: Preis-Heatmap, Saisonale Spread-Animation (K_04)
- **2–3** — Arbitrage-ROI, Amortisation, Segmentempfehlungen
- **4** — Dispatch-Optimierung: Tagesprofil, saisonale Muster, DA-optimal vs. reaktiv (K_06)
- **5** — Räumliche Analyse: BVI-Karten, Standortoptimierung (K_01)
- **6** — Skalierung & Netzentlastung
- **7** — FCR-Mechanismus (Verfügbarkeitsprämie), Revenue Stacking (K_05)
- **8** — CAPEX-Lernkurve, Sensitivitätsheatmap, VPP-Multiplikator (K_03)
- **9** — Import/Export-Validierung (K_02)
- **10** — Kombinationsmatrix: Vier Wege zur Rentabilität

---

## K_01 — Räumliche Analyse (`K_01_Raeumliche_Analyse.ipynb`)
Komplexestes Kür-Notebook (88 Zellen). GeoPandas, echte Schweizer Geodaten, Kartenerzeugung, Battery Value Index (BVI).

### Zelle 1 — Setup & Bibliotheken
**Was passiert:** Fehlende Libraries bei Bedarf installieren: `geopandas`, `scipy`. Config laden, vollständiger Farb- und Stil-Ladeblock aus `../sync/config.json`.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `gpd.read_file()` | `geopandas` | Lädt Geodaten aus GeoPackage (`.gpkg`), Shapefile (`.shp`) oder GeoJSON. `layer=` wählt einen Layer. |
| `gpd.list_layers()` | `geopandas` | Listet alle Layer in einer GeoPackage-Datei auf. |
| `gpd.GeoDataFrame()` | `geopandas` | Erstellt einen GeoDataFrame (pandas DataFrame mit Geometry-Spalte). |

### Zelle 2 — BFE-Anlagen laden
**Was passiert:** BFE-GeoPackage (alle Schweizer Elektrizitätsproduktionsanlagen) von swisstopo-API herunterladen (falls nicht vorhanden). Stream-Download in 512KB-Chunks. Koordinaten von CH1903+ auf WGS84 transformieren.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.iter_content()` | `requests` | Lädt eine HTTP-Antwort in Chunks. Notwendig für grosse Dateien. `chunk_size=1024*512` = 512KB pro Chunk. |
| `.to_crs()` | `geopandas` | Transformiert ein GeoDataFrame in ein anderes Koordinatensystem. `epsg=4326` = WGS84. |

### Zelle 4 — Energieträger-Mapping (vektorisiert)
**Was passiert:** Jede Anlage bekommt einen Energieträger-Label. Vektorisiert: erst `.map(SUBCAT_MAP)`, dann Fallback `.map(MAINCAT_MAP)`, Rest → `'Andere'`. Kein `apply(axis=1)`.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.to_numeric()` | `pandas` | Konvertiert zu numerischen Werten. `errors='coerce'` verwandelt nicht-konvertierbare Werte in `NaN`. |
| `.str.strip()` | `pandas (.str)` | Entfernt führende/nachfolgende Leerzeichen aus Strings. |
| `.fillna()` | `pandas` | Ersetzt NaN-Werte durch Standardwert oder andere Serie. |

### Zellen 5–6 — BFS Bevölkerungsdaten
**Was passiert:** BFS STATPOP-Daten via PXWeb-API (POST-Request mit JSON-Query). Non-breaking Spaces und Tausendertrennzeichen bereinigen.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `requests.post()` | `requests` | HTTP POST-Request mit JSON-Body. Für die PXWeb-API. |
| `requests.head()` | `requests` | Sendet nur den HTTP-Header. Schneller Verbindungstest. |
| `.raise_for_status()` | `requests` | Wirft eine Exception bei 4xx/5xx-Statuscodes. Verhindert stilles Scheitern. |
| `io.StringIO()` | `io` | In-Memory-Textpuffer. `pd.read_csv(io.StringIO(text))` liest CSV direkt aus String. |
| `pd.isna()` | `pandas` | Prüft elementweise ob Werte NaN sind. |

### Zelle 8 — Zonenzuweisung (vektorisiert)
**Was passiert:** Jede Anlage wird einer von 5 Netzregionen (Nord/Mitte/West/Süd/Ost) zugewiesen — primär per Kanton-Dict, Fallback via `np.select()` auf Koordinaten.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.select()` | `numpy` | Wählt aus mehreren Arrays basierend auf Bedingungsliste. Vektorisierte Alternative zu if/elif-Ketten. |

### Zellen 9–11 — Kapazitätsfaktoren, Zonenbilanzen, BVI
**Was passiert:** Installierte Kapazität × Kapazitätsfaktor = mittlere Einspeisung pro Zone. Zonenimbalance = Produktion − Verbrauch. BVI-Index = Imbalance × Engpass-Multiplikator, normiert auf 10.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.abs()` | `numpy` | Betrag eines Arrays. Für BVI: Vorzeichen der Imbalance ist egal, nur die Grösse zählt. |

### Zellen 13–21 — Kartenerzeugung & Heatmaps
**Was passiert:** Schweizer Kantonsgrenzen von swisstopo laden. Karten: Bevölkerungsdichte (Choropleth), Kraftwerksstandorte (Scatter), Kombinierte Karte mit Engpasskorridoren. Für 300k+ Solar-Anlagen: Stichprobe + `rasterized=True`. Tages-Lastprofil-Heatmap pro Zone.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.column_stack()` | `numpy` | Stapelt Arrays als Spalten zu einer 2D-Matrix. Effizienter als `list(zip(x,y))`. |
| `np.percentile()` | `numpy` | Berechnet ein Quantil. Hier für robuste Grössenskalierung von Kraftwerks-Punkten. |
| `np.clip()` | `numpy` | Begrenzt Array-Werte auf [min, max]. |
| `.geometry.x` | `geopandas` | Extrahiert X-Koordinate aus der Geometry-Spalte als Series. |
| `.geometry.centroid` | `geopandas` | Berechnet den geometrischen Schwerpunkt. Für Kanton-Beschriftungen. |
| `.sample()` | `pandas` | Zieht eine zufällige Stichprobe. `random_state=42` für Reproduzierbarkeit. |
| `ax.set_axis_off()` | `matplotlib.axes` | Blendet alle Achsenelemente aus. Standard für Karten. |
| `rasterized=True` | `matplotlib` | Wandelt viele Punkte in ein Pixel-Bild um. Entscheidend für Performance bei 100k+ Punkten. |
| `mcolors.TwoSlopeNorm()` | `matplotlib.colors` | Normalisierung mit zwei Slopes: für divergente Colormaps (Rot=Defizit, Blau=Überschuss). |
| `cKDTree()` | `scipy.spatial` | k-d-Baum für schnelle räumliche Nachbarschaftssuche. O(log n) statt O(n). |

### Zellen 20–21 — Lastprofile
**Was passiert:** Synthetische stündliche Last- und Produktionsprofile je Zone mit Gauss-Kurven modelliert.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.exp()` | `numpy` | Berechnet e^x. Für Gauss-Kurven: `np.exp(-((h-peak)**2)/width)`. |
| `np.sin()` | `numpy` | Sinusfunktion. Hier für Solar-Tagesprofil. |
| `np.ones()` | `numpy` | Array mit lauter Einsen. Für Kernkraft-Baseload. |
| `np.full()` | `numpy` | Array mit konstantem Wert. |

---

## K_02 — Cross-Border-Analyse (`K_02_Cross_Border.ipynb`)
Analysiert Stromflüsse zwischen der Schweiz und DE/AT/IT/FR und deren Einfluss auf Spotpreise.

### Zellen 1–2 — Setup & Grenzfluss-Download
**Was passiert:** Standard-Setup. ENTSO-E API für Grenzflüsse: `query_crossborder_flows()` für alle 4 Grenzpaare, jahresweise mit Retry.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.query_crossborder_flows()` | `entsoe` | Lädt physikalische Grenzflüsse (MW) zwischen zwei Regelzonen. Positiv = Export, negativ = Import. |

### Zellen 3–6 — Analyse & Charts
**Was passiert:** Netto-Import/-Export pro Saison. Korrelation zwischen Grenzflüssen und Spotpreis. Streudiagramme: Mehr Import aus DE → tiefere CH-Preise?

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.corr()` | `pandas` | Berechnet Pearson-Korrelationskoeffizienten zwischen allen Spaltenpaaren. |
| `.dropna()` | `pandas` | Entfernt Zeilen mit NaN-Werten. Wichtig vor Korrelationsberechnungen. |

---

## K_03 — Marktdynamik (`K_03_Marktdynamik.ipynb`)
Untersucht Spread-Trend über Zeit und CAPEX-Lernkurven für die Wirtschaftlichkeitsprojektion.

### Zellen 1–3 — Spread-Trend
**Was passiert:** Historische Spread-Zeitreihe aus `data/intermediate/` laden. Lineare Regression via `np.polyfit()`, Trendlinie via `np.polyval()`. Berechnung: ab welchem Spread-Niveau ist Privatarbitrage Break-Even?

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.polyfit()` | `numpy` | Berechnet Koeffizienten eines Polynoms (Kleinste-Quadrate). Grad 1: [Steigung, Achsenabschnitt]. |
| `np.polyval()` | `numpy` | Wertet ein Polynom an gegebenen X-Werten aus. Für die Regressionsgerade. |
| `LinearSegmentedColormap` | `matplotlib.colors` | Definiert eigene Farbpalette durch lineare Interpolation zwischen Stützpunkten. |

### Zellen 4–6 — CAPEX-Lernkurve & Sensitivitätsheatmap
**Was passiert:** CAPEX-Preisentwicklung modellieren (jährliche Kostensenkung via Lernrate aus Config). Berechnung in welchem Jahr die Privatarbitrage Break-Even erreicht. CAPEX × Spread Sensitivitätsheatmap.

---

## K_04 — Saisonale Animationen (`K_04_Animationen.ipynb`)
Erstellt animierte GIFs der Preis- und Lastzeitreihen über 52 Kalenderwochen.

### Zellen 1–3 — Setup & Wochenaggregation
**Was passiert:** Standard-Setup. Preise und Last pro Kalenderwoche × Stunde aggregieren: Mittelwert, p25, p75. `dt.isocalendar().week` für ISO-Kalenderwochen (1–52).

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.dt.isocalendar()` | `pandas (.dt)` | Gibt ISO-Kalenderwoche, Wochentag und Jahr zurück. ISO-KW beginnt montags. |

### Zellen 4–6 — Animationen A, B & C
**Was passiert:** Animation A: 4 GIFs (Tageszeiten 00/07/12/19 Uhr), 52 Frames. Pre-Indexierung VOR der Animations-Schleife für O(1)-Lookup statt Boolean-Filter. Animation B: 4-Panel-Chart alle Tageszeiten gleichzeitig. Animation C: Spread-Animation mit wöchentlichem Spread, Negativpreis-Anteil und Dispatch-Stunden als aufbauende Kurven.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.join()` | `pandas` | Verknüpft zwei DataFrames per Index. Schneller als `merge()` wenn Join-Key der Index ist. |
| `ax.errorbar()` | `matplotlib.axes` | Datenpunkte mit Fehlerbalken. `yerr=[[unten],[oben]]` für asymmetrische Balken. Für Preiskerzen. |
| `.set_data()` | `matplotlib.lines.Line2D` | Aktualisiert X- und Y-Daten einer bestehenden Linie. Effizient in Animationen. |
| `.set_height()` | `matplotlib.patches.Rectangle` | Ändert die Höhe eines Balken-Patches zur Laufzeit. Für frame-by-frame Balkendiagramme. |
| `FuncAnimation()` | `matplotlib.animation` | Erstellt Animation durch wiederholten Aufruf einer Update-Funktion. `frames=` = Frame-Parameter, `interval=` = Pause in ms. |
| `PillowWriter()` | `matplotlib.animation` | Speichert Animation als GIF via Pillow. `fps=` = Frames pro Sekunde. |

**Potenzielle Erweiterung:** ipywidgets `IntSlider` für interaktive Einzelframe-Navigation — vorerst nicht implementiert wegen Inkompatibilität mit `run_all` und statischem Export (→ O_01 Section 13).

---

## K_05 — Revenue Stacking (`K_05_Revenue_Stacking.ipynb`)
Berechnet Mehrertrag durch Systemdienstleistungen (FCR/aFRR) zusätzlich zur Arbitrage.

### Zellen 1–3 — Setup & Erlösstacking-Modell
**Was passiert:** Literaturbasierte Schätzwerte für FCR- und aFRR-Erlöse (EUR/kWh/Jahr) definieren. Für jedes Segment und jeden Erlöstyp: Mehrertrag bei 20% reservierter FCR-Kapazität. Wichtige Erkenntnis: FCR zahlt für **Verfügbarkeit**, nicht für gelieferte Energie — die Batterie verdient die Prämie auch ohne Zyklus.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `ax.barh()` | `matplotlib.axes` | Horizontales Balkendiagramm. Praktisch wenn Kategorien-Labels lang sind. |

### Zellen 4–5 — Charts
**Was passiert:** Gestapelter Balken: Arbitrage-Erlös als Basis, FCR und aFRR als Aufstockung. Break-Even-Analyse: ab wann macht FCR die Investition rentabel?

---

## K_06 — Dispatch-Optimierung (`K_06_Dispatch_Optimierung.ipynb`)
Vergleicht reaktiven (NB03-Schwellenwert) mit day-ahead-optimalem Dispatch.

### Zellen 1–2 — DA-optimaler Dispatcher
**Was passiert:** Zwei Dispatch-Funktionen werden definiert und verglichen:
- `simulate_battery_reactive()`: p25/p75 des laufenden Tages (identisch NB03)
- `simulate_battery_da_optimal()`: nutzt bekannte DA-Preise des gesamten nächsten Tages — realistischer, da ENTSO-E die DA-Preise täglich um 12:00 publiziert

Beide Funktionen enthalten die Break-even-Bedingung im Docstring: `p(discharge_q) × η > p(charge_q)` → Tage ohne qualifizierten Spread bleiben idle.

Effizienzgewinn DA vs. Reaktiv ist meist gering (~5–15%) weil beide denselben p25/p75-Schwellenwert verwenden.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.where()` | `numpy` | Gibt Indices zurück wo eine Bedingung erfüllt ist. `np.where(p <= q25)` = alle Lade-Positionen. Vektorisiert statt Python-Loop. |

### Zellen 3–7 — Vergleich & Sensitivitätsanalyse
**Was passiert:** Reaktiv vs. DA-optimal für alle Segmente: Erlös, Zyklen, Effizienz. Sensitivitätsanalyse C-Rate: wie verändert sich der Jahreserlös wenn die Leistung (kW) relativ zur Kapazität (kWh) variiert?

### Zelle 8 — Transfer-Output
**Was passiert:** DA-optimal vs. reaktiv Kennzahlen (`roi_reaktiv_pct`, `roi_da_optimal_pct`, `delta_pct`) je Segment in `../sync/transfer.json` unter `dispatch_optimierung`.

---

## K_07 — Technologievergleich (`K_07_Technologievergleich.ipynb`)
Vergleicht Li-Ion mit Redox-Flow, Vanadium-Flow, CAES, Schwungrad — Kosten, Lebensdauer, Wirkungsgrad.

### Zellen 1–2 — Technologiedaten laden
**Was passiert:** Daten aus lokaler CSV oder NREL Annual Technology Baseline API (öffentliche AWS S3 CSV). HTTP GET → `pd.read_csv(io.StringIO(resp.text))`.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.log()` | `numpy` | Natürlicher Logarithmus. Für Lernkurven-Regression: Linearisierung durch Logarithmieren. |
| `np.linspace()` | `numpy` | n gleichmässig verteilte Werte in [start, stop]. Garantiert genau n Punkte. Für glatte Kurven. |
| `curve_fit()` | `scipy.optimize` | Passt eine Funktion `f(x, *params)` an Datenpunkte an (nichtlineare Kleinste-Quadrate). |

### Zellen 3–6 — Vergleich & Radar-Chart
**Was passiert:** Wirtschaftlichkeit für alle Technologien. Radar-Chart (Spinnennetz) mit 5 Dimensionen: Kosten, Lebensdauer, Wirkungsgrad, Energiedichte, Skalierbarkeit. Lernkurven mit Trendlinie.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.array()` | `numpy` | Erstellt ein NumPy-Array aus einer Python-Liste. Für Radar-Chart-Winkel und Technologieparameter. |

---

## K_08 — Alternative Speicher (`K_08_Alternative_Speicher.ipynb`)
Analyse von Pumpspeichern und saisonalen Wärmespeichern als Li-Ion-Alternativen für die Schweiz.

### Zellen 1–3 — Daten, Berechnung, Chart
**Was passiert:** Schweizer Pumpspeicher-Kapazitäten aus BFE-Daten. Vergleich: Pumpspeicher arbitriert saisonal (Sommer pumpen, Winter erzeugen), Batterie nur täglich/stündlich.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `ax.set_yticks()` | `matplotlib.axes` | Setzt Y-Achsen-Tick-Positionen manuell. `.set_yticklabels()` setzt die Labels. |

---

## K_09 — Eigenverbrauchsoptimierung (`K_09_Eigenverbrauch.ipynb`)
Berechnet Mehrwert einer Batterie für PV-Haushalte (Eigenverbrauchsoptimierung statt Grid-Arbitrage).

### Zellen 1–3 — Setup & Simulation
**Was passiert:** Haushaltstarife (HT/NT) aus Config in EUR. Synthetisches Tagesprofil: Solarertrag als Sinus-Glockenkurve, Haushaltsverbrauch mit Morgen- und Abendspitze. Simulation: Solarüberschuss → Batterie (wenn nicht voll), abends → Batterie entladen, sonst → Netzstrom. `np.where()` für vektorisierte Tarifwahl.

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.where(arr, val_true, val_false)` | `numpy` | Ternärer Operator auf Arrays. `np.where(is_nt, NT_PREIS, HT_PREIS)` = vektorisierte Tarifwahl. |
| `.cumsum()` | `pandas / numpy` | Kumulierte Summe. Für SoC-Verlauf: jede Stunde wird Lade-/Entladeleistung summiert. |

### Zellen 4–6 — Wirtschaftlichkeit & Transfer
**Was passiert:** Eigenverbrauchsnutzen (Einsparung durch weniger Netzstrom) wird berechnet und mit Arbitrage-Erlös verglichen. Transfer-Output in `../sync/transfer.json` unter `eigenverbrauch`.

---

## K_10 — Produktsteckbrief (`K_10_Produkt_Steckbrief.ipynb`)
Erstellt einen formatierten Produkt-Datenblatt für ein konkretes Heimspeicher-Produkt. Enthält eine dedizierte Konfigurationszelle für Produktparameter.

### Zelle 1 — Produktkonfiguration
**Was passiert:** Eine einzelne Konfigurationszelle (mit `╔═══╗`-Rahmen deutlich markiert) enthält alle produktspezifischen Parameter: Name, Hersteller, Kapazität (kWh), Leistung (kW), Verkaufspreis (EUR), HT/NT-Tarife, Tagesverbrauch. **Nur diese Zelle anpassen** — alle nachfolgenden Berechnungen folgen automatisch.

### Zellen 2–4 — Berechnung: Arbitrage, Eigenverbrauch, Kombiniert
**Was passiert:** Grid-Arbitrage-Kennzahlen: ROI und Erlös/Jahr skaliert aus NB03-Ergebnissen (kapazitätsunabhängiger ROI × Produktpreis, C-Rate-Korrekturfaktor). Eigenverbrauch: HT/NT-Preisdifferenz × Tagesenergie × 365. Kombinierter Case: 70% Eigenverbrauch + 30% Arbitrage.

### Zellen 5–6 — Steckbrief-Ausgabe & Transfer
**Was passiert:** Formatierter Steckbrief als Textausgabe. Transfer in `../sync/transfer.json` unter `produkt`.

**Potenzielle Erweiterung:** ipywidgets Slider für Kapazität, Leistung und Preis mit Live-ROI-Berechnung — vorerst nicht implementiert wegen `run_all`-Inkompatibilität (→ O_01 Section 13).

---

## K_99 — Kombinierte Simulation (`K_99_Kombinierte_Simulation.ipynb`)
Synthese-Notebook. Simuliert alle vier Dispatch-Strategien (Arbitrage, Eigenverbrauch, Hybrid statisch, Hybrid optimiert) in einem Lauf.

### Zellen 1–4 — Setup & Simulation
**Was passiert:** Config und Transfer laden. Vier Simulationsfunktionen definiert:
- `sim_arbitrage()`: p25/p75 Tagesquantil-Dispatch identisch NB03. Break-even-Bedingung im Docstring: `p(discharge_q) × η > p(charge_q)` — Tage ohne qualifizierten Spread bleiben idle.
- `sim_eigenverbrauch()`: HT/NT-optimiert wie K_09
- `sim_hybrid_statisch()`: fester EV-Anteil (70%), Arbitrage mit Rest
- `sim_hybrid_optimiert()`: EV-Anteil variiert täglich nach Spread-Grösse

**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.tile()` | `numpy` | Wiederholt ein Array n-mal. `np.tile(np.arange(24), 365)` = Jahres-Stundenvektor. |
| `np.sum()` | `numpy` | Summiert alle Elemente eines Arrays. |
| `mlines.Line2D()` | `matplotlib.lines` | Legenden-Objekt mit Liniensymbol ohne echten Datenpunkt. |
| `mcolors.Normalize()` | `matplotlib.colors` | Normiert Werte auf [0,1] für Colormaps. |
| `plt.suptitle()` | `matplotlib.pyplot` | Haupttitel über alle Subplots einer Figure. |

### Zellen 5–9 — Charts & Transfer
**Was passiert:** Vergleichs-Charts: ROI aller 4 Modi nebeneinander, Break-Even-Vergleich, Cashflow-Kurven, 2×2 Heatmap-Panel (ROI × Segment × Strategie), CAPEX-Szenarien. Schlüsselkennzahlen in `../sync/transfer.json` unter `hybrid_simulation`.

---

# Bekannte Bezeichnungsleichen

Bei der Überarbeitung auf die neue Struktur wurden folgende veralteten Bezeichnungen in Notebook-Titeln gefunden, die noch nicht angepasst wurden:

| Datei | Aktueller Titel | Korrekter Titel |
|---|---|---|
| `organisation/O_04_Review_Protokoll.ipynb` | `NB00c – Review-Protokoll & Qualitätssicherung` | `O_04 – Review-Protokoll & Qualitätssicherung` |
| `organisation/O_99_Datenprovenienz.ipynb` | `NB99 – Daten-Provenienz & Werdegang` | `O_99 – Daten-Provenienz & Werdegang` |
| `notebooks/00_Business_Case.ipynb` | `NB00 – Business Case` | `NB00 – Business Case` *(akzeptabel, da Datei `00_Business_Case.ipynb`)* |

**Empfehlung:** O_04 und O_99 sollten in der jeweiligen Titel-Zelle (cell[0]) angepasst werden. Der Titelfix ist minimal — nur die erste Zeile der Markdown-Zelle betrifft.
