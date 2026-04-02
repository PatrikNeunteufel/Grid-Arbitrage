# Notebook-Dokumentation — Grid-Arbitrage mit Batteriespeichern
**SC26_Gruppe_2 · ZHAW CAS Information Engineering Scripting**

> **Zielgruppe:** Grundlegendes Python vorhanden, Data-Science-Einsteiger.
> Jede Code-Zelle wird erklärt: was sie tut, warum, welche Library-Funktionen dabei eine Rolle spielen.
> Jede Library-Funktion wird nur beim **ersten Auftreten** in einem eigenen Tabellenabschnitt beschrieben.
> 
> **Projektidee:** Kaufe Strom günstig (Preis-Tief), speichere ihn in einer Batterie, speise teuer ein (Preis-Hoch). Lohnt sich das in der Schweiz?

---
## NB00 — Projektübersicht (`00_Project_Overview.ipynb`)
Reine Projektverwaltung. Kein fachlicher Recheninhalt — nur Statustracking.

### Zelle 1
**Was passiert:** Status-Konstanten für Aufgaben werden definiert (`⬜ Offen`, `🔄 In Arbeit`, `✅ Erledigt`). Eine verschachtelte Liste aller Projektaufgaben mit Verantwortlichkeit, Frist und Status wird aufgebaut und als formatierte Tabelle ausgegeben.
**Warum so:** Ein einziger Blick zeigt den kompletten Projektstatus. `pandas` ist die einfachste Lösung für eine formatierte Tabelle im Notebook.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.DataFrame()` | `pandas` | Erstellt einen tabellarischen Datensatz (Zeilen × Spalten) aus einer Python-Liste oder einem Dictionary. Grundbaustein für alle Tabellenoperationen im Projekt. |

---
## NB00b — Konventionen & Architektur (`00b_Konventionen.ipynb`)
Lebendes Handbuch für das Team. Die einzige Code-Zelle ist vollständig auskommentiert.

### Zelle 1
**Was passiert:** Alle Zeilen beginnen mit `#` — Python-Kommentar, kein ausführbarer Code. Die Zelle zeigt ein Musterbeispiel für den korrekten Ladeprozess (CSV laden, sofort verifizieren). Beim Ausführen passiert nur `print('Musterzelle — nur zur Demonstration.')`.
**Warum so:** Referenzbeispiel für das Team, ohne echte Daten anzufassen.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.read_csv()` | `pandas` | Lädt eine CSV-Datei von der Festplatte in einen DataFrame. Optionen: `parse_dates` konvertiert Spalten direkt zu Datetime-Objekten. |
| `pd.to_datetime()` | `pandas` | Konvertiert Strings, Unix-Timestamps oder gemischte Formate in pandas-Timestamp-Objekte. `utc=True` normiert auf UTC-Zeitzone. |

---
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
**Was passiert:** Libraries werden geladen, `config.json` wird als Python-Dictionary `CFG` eingelesen. Daraus werden Mode, Reload-Schalter, Datenzeitraum und Verzeichnispfade extrahiert. Die Hilfsfunktion `needs_download()` prüft, ob eine Datei fehlt, zu klein ist oder ein Neuladen erzwungen wird.
**Warum so:** `config.json` ist der einzige Ort, wo Einstellungen gesetzt werden (Single Source of Truth). Code enthält nie hardcodierte Pfade oder Parameter.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `json.load()` | `json` | Liest eine JSON-Datei und gibt ein Python-Dictionary/-List zurück. Hier für `config.json` (Einstellungen) und `transfer.json` (Notebook-zu-Notebook-Übergabe). |
| `json.dump()` | `json` | Schreibt ein Python-Objekt als JSON in eine Datei. `indent=2` für lesbare Formatierung, `ensure_ascii=False` für Umlaute. |
| `os.path.join()` | `os` | Setzt Pfadteile plattformunabhängig zusammen (Backslash auf Windows, Slash auf Linux/Mac). Immer dieser Funktion statt Stringverkettung. |
| `os.makedirs()` | `os` | Erstellt ein Verzeichnis inkl. aller fehlenden Elternverzeichnisse. `exist_ok=True` unterdrückt den Fehler wenn das Verzeichnis bereits existiert. |
| `os.path.exists()` | `os` | Prüft ob ein Pfad (Datei oder Verzeichnis) existiert. Gibt `True`/`False` zurück. |
| `os.path.getsize()` | `os` | Gibt die Dateigrösse in Bytes zurück. Wird zur Validierung genutzt: Datei existiert aber ist zu klein → unvollständig, neu laden. |
### Zelle 3 — Datenregister-Hilfsfunktionen
**Was passiert:** Zwei Funktionen werden definiert. `log_dataindex()` schreibt jeden geladenen Datensatz in `dataindex.csv` — ein historisches Register mit Zeitstempel, Herkunft und Status. Wenn ein Eintrag für dieselbe Datei bereits existiert, wird der alte als `superseded` markiert. `log_missing()` schreibt fehlende Daten in `missing.txt`.
**Warum so:** Forschungsprojekte brauchen Nachvollziehbarkeit: Woher kommen die Daten? Von wann? Wurden sie aktualisiert? Das beantwortet die `dataindex.csv` automatisch.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.concat()` | `pandas` | Fügt mehrere DataFrames zusammen (vertikal oder horizontal). Ersetzt das veraltete `df.append()`. `ignore_index=True` setzt den Index neu. |
| `datetime.utcnow()` | `datetime` | Gibt den aktuellen UTC-Zeitstempel zurück. `.isoformat(timespec='seconds')` formatiert als `2024-01-15T10:30:00` — maschinenlesbar und sortierbar. |
### Zelle 4 — API-Verbindung & Spotpreis-Download
**Was passiert:** Der ENTSO-E API-Schlüssel wird aus `config.json` gelesen. Dann wird geprüft, ob der API-Endpunkt erreichbar ist (HTTP-Status-Interpretation: 400 = erreichbar aber fehlende Parameter, 401 = ungültiger Key, 503 = Server überlastet aber erreichbar). Eine Funktion `_fetch_prices_year()` lädt Day-Ahead-Spotpreise für ein einzelnes Jahr mit bis zu 3 automatischen Wiederholungsversuchen bei 503-Fehlern.
**Warum so:** Die ENTSO-E-API ist gelegentlich überlastet (503). Jahresweise Anfragen mit Retry-Logik ist robuster als ein einzelner Gesamtrequest. API-Keys werden nie im Code gespeichert — immer in der Config.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `requests.get()` | `requests` | Sendet einen HTTP GET-Request. `params=` für URL-Parameter, `timeout=` verhindert ewiges Warten, `stream=True` für grosse Dateien in Stücken. |
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
**Was passiert:** Datenzeitraum (Startjahr, Endjahr, Anzahl tatsächlicher Jahre) wird in `transfer.json` geschrieben. NB02 liest diesen Wert für korrekte Jahresdurchschnitt-Berechnungen.
**Warum so:** `transfer.json` ist der Kommunikationskanal zwischen Notebooks. Kein Notebook macht Annahmen über Datenzeiträume — es liest immer aus dieser Datei.
### Zelle 9 — Abschlusskontrolle
**Was passiert:** Alle Output-Dateien werden auf Existenz und Mindestgrösse geprüft. ✅/❌ Ausgabe. Inhalt von `dataindex.csv` anzeigen.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `os.listdir()` | `os` | Gibt alle Dateien und Verzeichnisse in einem Ordner als Liste zurück. Hier für die Abschlusskontrolle: welche Charts/Dateien wurden erzeugt? |

---
## NB02 — Datenanalyse & Dispatch-Simulation (`02_Daten_Analyse.ipynb`)
Das Herzstück des Projekts. Rohdaten bereinigen, Batterie-Dispatch simulieren, wirtschaftliche Kennzahlen berechnen.

### Zelle 1 — Konfiguration & Parameter
**Was passiert:** Alle Simulations- und Wirtschaftlichkeitsparameter werden aus `config.json` geladen: Lade-/Entladequantil (0.25/0.75), SoC-Grenzen (5%/95%), Wirkungsgrad (92%), CAPEX pro kWh je Segment, OPEX-Rate (1.5%/Jahr), Lebensdauer (12 Jahre). Der Ziel-ROI wird lokal als `100/12 ≈ 8.3%/Jahr` berechnet — nie in der Config gespeichert, weil er eine abgeleitete Grösse ist.
**Warum so:** SSOT-Prinzip. Alles aus der Config, keine Magie-Zahlen im Code.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `warnings.filterwarnings()` | `warnings` | Unterdrückt Python-Warnmeldungen (z.B. pandas DeprecationWarnings). `'ignore'` schaltet alle aus — sinnvoll für Notebooks um die Ausgabe lesbar zu halten. |
### Zelle 2 — n_years aus transfer.json
**Was passiert:** `transfer.json` wird geöffnet, `n_years` (Anzahl tatsächlich simulierter Datenjahre) wird ausgelesen. Dieser Wert kommt von NB01. Falls die Datei fehlt: Warnung und `n_years = None`.
**Warum so:** Jahresdurchschnitt = Gesamterlös ÷ n_years. Dieser Wert muss aus NB01 kommen, damit er mit den tatsächlich geladenen Daten übereinstimmt.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `json.loads()` | `json` | Parst JSON direkt aus einem String (nicht aus einer Datei). Hier zum Lesen einer Datei mit leerem Inhalt-Guard: `json.loads(f.read() or '{}')` |
### Zelle 3 — Hilfsfunktionen (Datenregister)
**Was passiert:** `log_dataindex()` und `log_missing()` wie in NB01. Zusätzlich: `needs_rebuild()` — prüft ob eine verarbeitete Datei neu berechnet werden muss (fehlt, zu wenig Zeilen, oder FORCE_RELOAD gesetzt).
**Warum so:** Jedes Notebook ist für sich ausführbar. Deswegen werden diese Helfer in jedem Notebook neu definiert statt importiert.
### Zellen 4–6 — Rohdaten laden & bereinigen
**Was passiert:** Rohdaten von der Festplatte laden. Dann Bereinigung in 5 Schritten:
1. Zeitstempel auf UTC normieren und sortieren
2. Vollständigen Stundenraster erzwingen: `pd.date_range(..., name='timestamp')` + `.reindex()` → fehlende Stunden werden als NaN eingefügt, kein `.rename()` mehr nötig
3. Lücken bis 3h linear interpolieren, längere mit `.ffill(limit=6).bfill(limit=6)` auffüllen
4. Extreme Ausreisser kappen: < -500 oder > 3000 EUR/MWh
5. Zeitfeatures ableiten: Stunde, Monat, Wochentag, Jahreszeit via `(month % 12) // 3`


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.date_range()` | `pandas` | Erzeugt einen lückenlosen Zeitreihen-Index. `freq='1h'` = stündlich, `tz='UTC'` = UTC-Zeitzone, `name='timestamp'` setzt den Spaltennamen nach `reset_index()` automatisch. |
| `.set_index()` | `pandas` | Setzt eine Spalte als DataFrame-Index. Wird mit `.reindex()` kombiniert um fehlende Zeitstempel einzufügen. |
| `.reindex()` | `pandas` | Richtet den DataFrame auf einen neuen Index aus. Fehlende Werte werden als `NaN` eingefügt — so werden Lücken im Stunden-Raster sichtbar gemacht. |
| `.reset_index()` | `pandas` | Verwandelt den Index zurück in eine normale Spalte. Typisch nach `set_index()` + `reindex()`. |
| `.interpolate()` | `pandas` | Füllt NaN-Werte durch Interpolation. `method='linear'` zieht eine Gerade zwischen zwei bekannten Werten. `limit=3` begrenzt auf maximal 3 aufeinanderfolgende NaN. |
| `.ffill()` | `pandas` | Forward Fill: füllt NaN mit dem letzten bekannten Wert (vorwärts). `limit=6` begrenzt die Anzahl auffüllbarer aufeinanderfolgender NaN. Modernere Alternative zu `fillna(method='ffill')`. |
| `.bfill()` | `pandas` | Backward Fill: füllt NaN mit dem nächsten bekannten Wert (rückwärts). Wird nach `ffill()` verwendet um verbleibende NaN am Anfang der Serie zu füllen. |
| `.clip()` | `pandas / numpy` | Begrenzt Werte auf ein Intervall [min, max]. Werte ausserhalb werden auf den nächsten Grenzwert gesetzt. Verhindert Ausreisser-Effekte auf Berechnungen. |
| `.dt.hour` | `pandas (.dt)` | Zugriff auf Datetime-Komponenten einer Spalte. `.dt.hour` = Stunde (0–23), `.dt.month` = Monat (1–12), `.dt.dayofweek` = Wochentag (0=Montag). |
| `.dt.date` | `pandas (.dt)` | Extrahiert das Datum (ohne Uhrzeit) als `datetime.date`-Objekt. Wird für tagesweise Gruppenbildung verwendet. |
### Zelle 7 — Tagesprofil & Spread-Analyse
**Was passiert:** Für jede Stunde des Tages (0–23) werden Durchschnitt und Standardabweichung des Preises berechnet. Die 4 günstigsten und 4 teuersten Stunden werden identifiziert. Der Arbitrage-Spread (Preisunterschied) wird berechnet. Saisonale Durchschnitte werden ausgegeben.
**Warum so:** Beantwortet die Kernfrage: Wie gross ist das Arbitrage-Potential im Tages-Rhythmus? Wie unterscheiden sich die Jahreszeiten?


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.groupby()` | `pandas` | Gruppiert einen DataFrame nach einer oder mehreren Spalten. Ermöglicht Aggregation pro Gruppe. Hier z.B. Durchschnittspreis pro Stunde oder pro Saison. |
| `.agg()` | `pandas` | Wendet mehrere Aggregationsfunktionen auf eine Gruppe an. `agg(mean='mean', std='std')` berechnet Mittelwert und Standardabweichung in einem Durchgang. |
| `.nsmallest()` | `pandas` | Gibt die n kleinsten Werte einer Serie zurück (schneller als sort + head). Hier: die 4 günstigsten Stunden. |
| `.nlargest()` | `pandas` | Gibt die n grössten Werte zurück. Hier: die 4 teuersten Stunden. |
### Zelle 8 — Dispatch-Simulation (Kernfunktion)
**Was passiert:** `simulate_battery()` wird definiert — der algorithmische Kern des Projekts. Das Schwellenwertmodell:
- **Schritt 1:** Für jeden Tag werden p25 und p75 *einmalig vorab* als NumPy-Arrays berechnet (O(n), nicht O(n²))
- **Schritt 2:** Preise und Schwellenwerte werden als NumPy-Arrays extrahiert (kein `iterrows()`)
- **Schritt 3:** Stunden-Simulation: Preis ≤ p25 UND SoC < 95% → laden; Preis ≥ p75 UND SoC > 5% → einspeisen
**Warum NumPy?** Für 26.000 Stunden (3 Jahre) wäre `iterrows()` etwa 50× langsamer. NumPy läuft in optimiertem C-Code.
**Warum sequenziell?** Der SoC (Ladezustand) einer Stunde hängt vom SoC der Vorherigen ab — das kann nicht vektorisiert werden.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.empty()` | `numpy` | Erstellt ein uninitialisiertes Array mit gegebener Form und dtype. Schneller als `np.zeros()` wenn alle Werte sofort überschrieben werden. Hier für das `actions`-Array (Strings). |
| `np.zeros()` | `numpy` | Erstellt ein Array mit lauter Nullen. Geeignet für Cashflow- und Grid-Delta-Initialisierung — Standard-Startwert ist 0. |
| `.to_numpy()` | `pandas` | Konvertiert eine pandas Series in ein NumPy-Array. Ermöglicht schnellen Zugriff ohne Python-Overhead. Notwendig für die Dispatch-Simulation. |
### Zelle 9 — Simulation aller Segmente
**Was passiert:** `simulate_battery()` wird für alle 4 Segmente ausgeführt (Privat 10 kWh, Gewerbe 100 kWh, Industrie 1 MWh, Utility 10 MWh). Jahreserlös = Gesamterlös ÷ n_years. Ergebnisse werden tabellarisch ausgegeben.
**Warum Durchschnitt statt nur ein Jahr?** Jahres-Preise schwanken stark. Durchschnitt über mehrere Jahre ist realistischer.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.dt.year` | `pandas (.dt)` | Extrahiert das Jahr aus einer Datetime-Spalte. `.dt.year.nunique()` = Anzahl verschiedener Jahre im Datensatz — wird als Fallback für n_years verwendet. |
### Zelle 10 — CAPEX / ROI / Amortisation
**Was passiert:** Für jedes Segment: CAPEX (Investition = kWh × EUR/kWh), OPEX (1.5% CAPEX/Jahr), Netto-Erlös (Jahreserlös − OPEX), Amortisationszeit (CAPEX ÷ Netto), ROI (Netto/CAPEX × 100). Alles wird als CSV gespeichert.
**Warum OPEX abziehen?** Wartung, Versicherung, Monitoring kosten auch wenn die Batterie nichts verdient. 1.5% ist ein Branchenwert für Heimspeicher CH.
### Zelle 12 — Gleichzeitigkeits-Szenarien
**Was passiert:** 4 Szenarien (Status Quo, Moderat 2027, Ambitioniert 2030, Transformativ 2035) mit unterschiedlicher Anzahl Batteriesysteme. Gleichzeitigkeitsrate aus Config (z.B. 40%) skaliert die theoretische Leistung auf die reale Netzentlastung in MW.
**Warum Gleichzeitigkeit?** 50.000 Heimspeicher à 5 kW = 250 MW theoretisch. Bei 40% Gleichzeitigkeit = 100 MW real — weil nicht alle zur gleichen Sekunde einspeisen.
### Zelle 13 — Spread-Zeitreihe
**Was passiert:** Für jeden Tag wird der Intra-Tag-Spread berechnet (p75 − p25). Optimiert: statt zweier Lambda-`agg()`-Aufrufe ein einziger `.quantile([0.25, 0.75]).unstack()`. Tageswerte werden pro Monat zum Median aggregiert. Zusätzlich: Volatilität, Durchschnittspreis, Negativpreis-Stunden.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.quantile()` | `pandas` | Berechnet Quantile einer Serie. `.quantile([0.25, 0.75])` gibt beide auf einmal zurück. Nachgelagertes `.unstack()` verwandelt das MultiIndex-Ergebnis in Spalten `p25`/`p75`. |
| `.unstack()` | `pandas` | Klappt den innersten Index einer MultiIndex-Serie in Spalten um. Typisch nach `.groupby().quantile([...])` um eine breite Tabelle zu erhalten. |
| `.merge()` | `pandas` | Verknüpft zwei DataFrames per Schlüsselspalte (wie SQL JOIN). `on='yearmonth'` = beide DataFrames haben eine Spalte `yearmonth` als gemeinsamen Schlüssel. |
| `.dt.to_period()` | `pandas (.dt)` | Konvertiert Timestamps in Zeiträume (z.B. `'M'` = Monat). `.dt.to_timestamp()` wandelt zurück in den Perioden-Beginn. Wird für monatliche Aggregation genutzt. |
| `.median()` | `pandas` | Berechnet den Median (mittlerer Wert) — robuster gegen Ausreisser als der Mittelwert. Ein extremer Spread-Tag verzerrt den Monats-Median kaum. |
### Zelle 15 — Transfer-Output
**Was passiert:** Alle berechneten Kennzahlen werden in `transfer.json` geschrieben: Spread-Statistiken, n_years, ROI/Erlös/CAPEX pro Segment. Optimiert: statt `iterrows()` eine `zip()`-basierte Dict-Comprehension über die 4 Segmentspalten.
**Warum?** Alle nachgelagerten Notebooks (NB05/NB08 usw.) lesen diese Werte statt selbst zu berechnen.

---
## NB03 — Visualisierungen (`03_Visualisierungen.ipynb`)
Erzeugt alle Pflicht-Charts (8 Charts + Einzelplots). Keine Berechnungen — liest aus NB02, stellt grafisch dar.

### Zelle 1 — Setup & Daten laden
**Was passiert:** Libraries laden, Config lesen, Farb- und Stil-Konstanten aus `config.json` entpacken, `matplotlib.rcParams` global setzen. Dann vier CSVs laden. FIX: `rev_per_kwh` wird falls fehlend vektorisiert berechnet: `(df_econ['annual_rev'] * 2) / df_econ['segment'].map(CAP_MAP)` — kein `apply(axis=1)` mehr.
**Warum rcParams global?** Ohne diese Einstellung müsste jeder der 8 Charts dieselben 10 Zeilen Formatierungscode wiederholen.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `matplotlib.rcParams.update()` | `matplotlib` | Setzt globale Standardwerte für alle nachfolgenden Matplotlib-Plots: Hintergrundfarbe, Tick-Farbe, Schriftgrössen, Linienbreiten, Legenden-Stile. Gilt für alle Charts des Notebooks. |
| `.map()` | `pandas` | Ersetzt Werte einer Spalte anhand eines Dictionaries. Vektorisiert — kein Python-Loop. Hier: Segment-Name → Kapazitätswert aus `CAP_MAP`. |
| `pd.Series()` | `pandas` | Erzeugt eine einspaltige Datenstruktur mit Index. Hier als Initialisierung mit Standardwert `'Andere'` vor der vektorisierten ET-Zuweisung. |
### Zellen 3–5 — Chart 1: Wirtschaftlichkeit (4 Panels + Einzelplots + Langzeit)
**Was passiert:** Ein 2×2-Panel-Chart wird erstellt. Alle Cashflow-Schleifen über `df_econ` nutzen jetzt `zip(df_econ['segment'], df_econ['capex'], df_econ['net_annual'])` statt `itertuples()`, und der Cashflow wird als NumPy-Vektoroperation berechnet: `-capex + net_annual * years` (kein List-Comprehension-Loop mehr).
Panel 1: Kumulierte Cashflow-Kurven (symlog-Skala). Panel 2: ROI-Balken mit Ziel-ROI-Linie. Panel 3: Erlös/kWh. Panel 4: CAPEX vs. kumulierter Erlös.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.arange()` | `numpy` | Erstellt ein Array mit gleichmässigem Abstand (Ganzzahlen). `np.arange(0, 13)` = [0,1,2,...,12]. Hier als Jahres-Achse für Cashflow-Kurven. NumPy-Alternative zu `range()`. |
| `ax.set_yscale()` | `matplotlib.axes` | Setzt die Skalierung der Y-Achse. `'symlog'` = symmetrisch-logarithmisch: linear nahe der Null (für negative Werte), logarithmisch für grosse Beträge. `linthresh` definiert den linearen Bereich. |
| `mticker.FuncFormatter()` | `matplotlib.ticker` | Definiert eine eigene Tick-Beschriftungsformel als Python-Funktion. Hier: Werte ≥ 1000 als `'123k'` statt `'123000'` anzeigen. |
| `ax.annotate()` | `matplotlib.axes` | Fügt eine Beschriftung mit einem Pfeil an einen Datenpunkt an. `xy=` = Pfeilspitze, `xytext=` = Textposition. `arrowprops=` steuert Pfeilform und Farbe. |
| `ax.axhline()` | `matplotlib.axes` | Zeichnet eine horizontale Linie über die gesamte Breite der Achse. Hier für die Break-Even-Linie bei y=0 und die Ziel-ROI-Referenzlinie. |
| `ax.axvline()` | `matplotlib.axes` | Zeichnet eine vertikale Linie über die gesamte Höhe der Achse. Hier für den Marker bei Jahr 12 (Ende Simulationszeitraum). |
### Zellen 6–7 — Chart 2: Heatmap Stunde × Monat
**Was passiert:** Eine 24×12-Matrix (Stunden × Monate) wird als Heatmap dargestellt. Optimiert: statt zwei separater `pivot_table()`-Aufrufe ein kombinierter: `df_prices.pivot_table(..., aggfunc=['mean','std'])` — Pandas gruppiert nur einmal. `origin='lower'` setzt 00:00 unten (mathematische Konvention, nicht Bild-Konvention).


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.pivot_table()` | `pandas` | Erstellt eine Kreuztabelle: `index`-Spalte als Zeilen, `columns`-Spalte als Spalten, `values` aggregiert mit `aggfunc`. Hier: Mittelwert des Preises pro Stunde × Monat. |
| `ax.imshow()` | `matplotlib.axes` | Stellt eine Matrix als farbcodiertes Bild (Heatmap) dar. `cmap=` = Farbpalette, `origin='lower'` = Zeile 0 unten, `aspect='auto'` = Zellen füllen die Achse. |
| `plt.colorbar()` | `matplotlib.pyplot` | Fügt eine Farblegende (Colorbar) neben dem Plot hinzu. Zeigt welcher Farbwert welchem Zahlenwert entspricht. |
| `ax.axvspan()` | `matplotlib.axes` | Zeichnet eine farbige vertikale Zone (Rechteck über die volle Höhe). Hier für Lade- und Einspeisezeitfenster-Markierungen. |
### Zellen 8–9 — Chart 3: Tagesprofil mit Doppelachse
**Was passiert:** Netzlast (GW) und Preis (EUR/MWh) werden als Doppelachsen-Chart dargestellt. Die 4 günstigsten Stunden werden blau, die 4 teuersten rot hinterlegt.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `ax.twinx()` | `matplotlib.axes` | Erstellt eine zweite Y-Achse auf der rechten Seite, die dieselbe X-Achse teilt. Ermöglicht zwei verschiedene Skalen im selben Chart (hier: GW und EUR/MWh). |
| `ax.fill_between()` | `matplotlib.axes` | Füllt die Fläche zwischen zwei Kurven (oder einer Kurve und der X-Achse) mit Farbe. Alpha-Wert steuert die Transparenz. |
| `mpatches.Patch()` | `matplotlib.patches` | Erzeugt ein einfaches farbiges Rechteck für die Legende. Wird genutzt wenn kein echter Plot-Objekt für den Legenden-Eintrag vorhanden ist. |
| `ax.get_legend_handles_labels()` | `matplotlib.axes` | Gibt die aktuellen Legenden-Einträge (Handles + Labels) einer Achse zurück. Wird genutzt um Legenden von mehreren Achsen zusammenzuführen. |
### Zellen 10–13 — Charts 4 & 5: Szenarien & Saisonales Profil
**Was passiert:** Chart 4: Netzentlastungsszenarien als Balken und Prozent-Reduktion mit dynamischer Einfärbung via `Normalize` und `cm.get_cmap()`. Chart 5: Saisonales Tagesprofil für alle 4 Jahreszeiten mit einheitlichen Y-Achsen (vorab berechnet) und farbigen Zeitfenstern.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `Normalize()` | `matplotlib.colors` | Skaliert Werte auf den Bereich [0,1] für Colormaps. `vmin`/`vmax` definieren den Eingabebereich. Wird mit `cm.get_cmap()` kombiniert um Farben datengesteuert zuzuweisen. |
| `cm.get_cmap()` | `matplotlib.cm` | Lädt eine benannte Farbpalette als Objekt. `cmap(value)` gibt dann die RGBA-Farbe für einen Wert aus [0,1] zurück. |
| `cm.ScalarMappable()` | `matplotlib.cm` | Verbindet eine Colormap mit einer Normalisierung — wird benötigt um eine Colorbar für Daten zu erzeugen, die nicht direkt via `imshow()`/`scatter()` geplottet wurden. |
### Zelle 14 — Chart 5b: Monatlicher Spread
**Was passiert:** Pro Monat: Intra-Tag-Spread (p75 − p25 der Stundenmittelwerte) und Negativpreis-Stunden. Gesamtchart + Einzelplots werden gespeichert.

---
## NB04 — Business Case (`04_Business_Case.ipynb`)
Kein eigener Chart-Code. Lädt und zeigt die von NB03 erzeugten PNGs. Reiner Berichtsmodus.

### Zelle 1 — Setup & show_chart()
**Was passiert:** `config.json` laden, Charts-Verzeichnis definieren. Hilfsfunktion `show_chart()` rendert ein PNG direkt im Notebook. Szenariodaten aus NB02-CSV laden.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `display()` | `IPython.display` | Gibt ein Objekt im Notebook-Output aus. Notwendig für `Image`-Objekte — normales `print()` würde nur den Objektpfad zeigen. |
| `Image()` | `IPython.display` | Lädt ein Bild von der Festplatte und rendert es im Notebook-Output. `width=` setzt die Anzeigebreite in Pixeln. |
### Zellen 2–13 — Chart-Anzeige
**Was passiert:** `show_chart('nb03_....png')` aufrufen — lädt und zeigt jeden der 8 Pflicht-Charts. Zwischen den Charts stehen Markdown-Zellen mit Interpretation.
### Zelle 14 — Zusammenfassung
**Was passiert:** Wirtschaftlichkeitstabelle aus CSV laden, als formatierte Tabelle anzeigen. Schlussfolgerungen als Text ausgeben (z.B. kein Segment erreicht Ziel-ROI durch Arbitrage allein).

---
## NB05 — Business Strategy (`05_Business_Strategy.ipynb`)
Grösstes Notebook (27 Zellen). Fasst alle Ergebnisse aus Pflicht und Kür zu einer Strategie-Empfehlung zusammen.

### Zelle 1 — Setup
**Was passiert:** `transfer.json` komplett laden — alle Werte, die NB01–NB15 dort geschrieben haben, sind jetzt verfügbar. Charts-Verzeichnisse für alle Kür-Notebooks definieren.
### Zellen 2–26 — Strategie-Kapitel
**Was passiert:** Je eine Zelle pro Thema: Marktpotential, Revenue-Stack (FCR/aFRR/Eigenverbrauch), Technologievergleich, Räumliche Analyse, Cross-Border, Kostenentwicklung, Fazit. Jede Zelle lädt die relevanten Chart-PNGs der Kür-Notebooks und zeigt sie.
### Zelle 27 — Transfer-Output
**Was passiert:** Strategie-Schlüsselkennzahlen in `transfer.json` unter `strategie` schreiben.

---
## NB06 — Räumliche Analyse (`06_Raeumliche_Analyse.ipynb`)
Komplexestes Kür-Notebook (29 Zellen). GeoPandas, echte Schweizer Geodaten, Kartenerzeugung, BVI-Index.

### Zelle 1 — Setup & Bibliotheken
**Was passiert:** Fehlende Libraries werden bei Bedarf installiert: `geopandas`, `scipy`. Config laden, vollständiger Farb- und Stil-Ladeblock aus config.json. Verzeichnisse anlegen.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `gpd.read_file()` | `geopandas` | Lädt Geodaten aus Dateiformaten wie GeoPackage (`.gpkg`), Shapefile (`.shp`) oder GeoJSON. `layer=` wählt einen Layer in GPKG. Gibt einen GeoDataFrame zurück. |
| `gpd.list_layers()` | `geopandas` | Listet alle Layer in einer GeoPackage-Datei auf. Notwendig weil GPKG mehrere Geometrie-Typen enthalten kann. |
| `gpd.GeoDataFrame()` | `geopandas` | Erstellt einen GeoDataFrame (ein pandas DataFrame mit einer Geometry-Spalte). Hier z.B. um einzelne Geometrien für das Plotten vorzubereiten. |
### Zelle 2 — BFE-Anlagen laden
**Was passiert:** Das BFE-GeoPackage (alle Schweizer Elektrizitätsproduktionsanlagen) wird von der swisstopo-API heruntergeladen (falls nicht vorhanden). Stream-Download in 512KB-Chunks. Koordinaten werden von CH1903+ (Schweizer Landeskoordinaten) auf WGS84 (Längen-/Breitengrad) transformiert.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.iter_content()` | `requests` | Lädt eine HTTP-Antwort in Chunks (Stücken) statt auf einmal. Notwendig für grosse Dateien: verhindert Speicher-Überlauf. `chunk_size=1024*512` = 512KB pro Chunk. |
| `.to_crs()` | `geopandas` | Transformiert ein GeoDataFrame in ein anderes Koordinatensystem (CRS). `epsg=4326` = WGS84 (GPS-Koordinaten). Notwendig weil Schweizer Daten im nationalen CH1903+-System vorliegen. |
### Zelle 4 — Energieträger-Mapping (vektorisiert)
**Was passiert:** Jede Anlage bekommt einen Energieträger-Label basierend auf den BFE-Subcategory-Codes. Vektorisierte Implementierung: erst `.map(SUBCAT_MAP)` auf die SubCategory-Spalte, dann für nicht zugeordnete Einträge `.map(MAINCAT_MAP)` auf die MainCategory, Rest → `'Andere'`. Kein `apply(axis=1)` über 300'000+ Zeilen mehr.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.to_numeric()` | `pandas` | Konvertiert eine Spalte zu numerischen Werten. `errors='coerce'` verwandelt nicht-konvertierbare Werte (Strings, None) in `NaN` statt eine Exception zu werfen. |
| `.str.strip()` | `pandas (.str)` | Entfernt führende und nachfolgende Leerzeichen (inkl. non-breaking spaces) aus String-Spalten. `.str.lower()` konvertiert zu Kleinbuchstaben. |
| `.fillna()` | `pandas` | Ersetzt NaN-Werte durch einen Standardwert oder aus einer anderen Serie. Hier: falls SubCategory-Mapping kein Ergebnis liefert, MainCategory-Mapping versuchen. |
### Zelle 5–6 — BFS Bevölkerungsdaten
**Was passiert:** Die BFS STATPOP-Daten (Einwohner pro Kanton) werden via PXWeb-API abgerufen. POST-Request mit JSON-Query, Antwort als CSV-Stream. Non-breaking Spaces und Apostrophe als Tausendertrennzeichen werden bereinigt.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `requests.post()` | `requests` | Sendet einen HTTP POST-Request mit JSON-Body. Hier für die PXWeb-API: die Abfrage-Parameter (Kanton, Jahr) werden als JSON-Dictionary gesendet. |
| `requests.head()` | `requests` | Sendet nur den HTTP-Header (kein Body). Schneller Verbindungstest: Ist der Server erreichbar? |
| `.raise_for_status()` | `requests` | Wirft eine `HTTPError`-Exception wenn der HTTP-Statuscode einen Fehler anzeigt (4xx/5xx). Verhindert stilles Scheitern bei API-Fehlern. |
| `io.StringIO()` | `io` | Erstellt einen In-Memory-Textpuffer. `pd.read_csv(io.StringIO(text))` liest CSV direkt aus einem String — kein temporäres Schreiben auf die Festplatte nötig. |
| `pd.isna()` | `pandas` | Prüft elementweise ob Werte NaN/None/NaT sind. Gibt eine Boolean-Serie zurück. Gegenteil: `pd.notna()`. |
### Zelle 8 — Zonenzuweisung (vektorisiert)
**Was passiert:** Jede Anlage wird einer von 5 Netzregionen (Nord, Mitte, West, Süd, Ost) zugewiesen — primär per Kanton-Dict-Mapping. Fallback (wenn kein Kanton vorhanden): geografische Zuweisung via `np.select()` auf Koordinaten statt Python-`apply()`.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.select()` | `numpy` | Wählt aus mehreren Arrays basierend auf einer Liste von Bedingungen. `condlist=[cond1, cond2, ...]`, `choicelist=[val1, val2, ...]`, `default=`. Vektorisierte Alternative zu if/elif-Ketten in Python-Loops. |
### Zellen 9–11 — Kapazitätsfaktoren, Zonenbilanzen, BVI
**Was passiert:** Installierte Kapazität × Kapazitätsfaktor (je Energieträger) = mittlere Einspeisung pro Zone. Zonenimbalance = Produktion − Verbrauch. BVI-Index = Imbalance × Engpass-Multiplikator, normiert auf 10.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.abs()` | `numpy` | Betrag (absoluter Wert) eines Arrays. Hier für die BVI-Berechnung: Vorzeichen der Imbalance ist egal, nur die Grösse zählt. |
### Zellen 13–19 — Kartenerzeugung
**Was passiert:** Schweizer Kantonsgrenzen von swisstopo laden. Mehrere Karten erstellen: Bevölkerungsdichte (Choropleth), Kraftwerksstandorte (Scatter mit Grössenskalierung), Kombinierte Karte mit Engpasskorridoren. Scatter-Plots für 300k+ Solar-Anlagen: Stichprobe + `rasterized=True` für schnelles Rendering.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.column_stack()` | `numpy` | Stapelt Arrays als Spalten zu einer 2D-Matrix. `np.column_stack([x, y])` erzeugt ein (n,2)-Array aus X- und Y-Koordinaten — effizienter als `list(zip(x,y))` für grosse Arrays. |
| `np.percentile()` | `numpy` | Berechnet ein Quantil (Perzentil) eines Arrays. `np.percentile(kw, 95)` = der 95%-Quantil-Wert. Hier für robuste Grössenskalierung von Kraftwerks-Punkten. |
| `np.clip()` | `numpy` | Begrenzt Array-Werte auf [min, max]. Hier für Punkt-Grössenberechnung: zu kleine Kraftwerke erhalten Mindestgrösse, zu grosse werden gekappt. |
| `.geometry.x` | `geopandas` | Extrahiert die X-Koordinate (Längengrad) aus der Geometry-Spalte als pandas Series. `.to_numpy()` konvertiert zu NumPy für schnelle scatter-Plots. |
| `.geometry.centroid` | `geopandas` | Berechnet den geometrischen Schwerpunkt einer Geometrie (Polygon). Wird für Kanton-Beschriftungen verwendet. |
| `.sample()` | `pandas` | Zieht eine zufällige Stichprobe. `n=` Anzahl Zeilen, `random_state=42` für Reproduzierbarkeit. Hier: 160k der 320k Solar-Anlagen für schnelleres Rendering. |
| `ax.set_axis_off()` | `matplotlib.axes` | Blendet alle Achsenelemente aus (Rahmen, Ticks, Labels). Standard für Karten: keine Koordinatenachsen erwünscht. |
| `rasterized=True` | `matplotlib` | Parameter für `scatter()` und `plot()`. Wandelt viele kleine Punkte in ein Pixel-Bild um statt in Vektoren. Entscheidend für Performance bei 100k+ Punkten. |
| `mcolors.TwoSlopeNorm()` | `matplotlib.colors` | Normalisierung mit zwei Slopes: unter `vcenter` linear auf [vmin, vcenter], über `vcenter` linear auf [vcenter, vmax]. Für divergente Colormaps (z.B. Rot=Defizit, Blau=Überschuss). |
| `cKDTree()` | `scipy.spatial` | k-d-Baum-Datenstruktur für schnelle räumliche Nachbarschaftssuche. Nach einmaliger Konstruktion: Nächste-Nachbarn-Anfragen in O(log n) statt O(n). Hier für Kraftwerks-Zuweisung zu Netzregionen. |
### Zellen 20–21 — Lastprofile & Heatmaps
**Was passiert:** Synthetische stündliche Last- und Produktionsprofile je Zone werden mit Gauss-Kurven (`np.exp()`) modelliert. Produktions-Mix-Heatmap: welche Energieträger produzieren wann wie viel?


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.exp()` | `numpy` | Berechnet e^x für jedes Array-Element. Wird für Gauss-Kurven verwendet: `np.exp(-((hours-peak)**2)/width)` ergibt eine Glockenkurve. Hier für realistische Tagesprofile. |
| `np.sin()` | `numpy` | Sinusfunktion (im Bogenmass). Hier für das Solar-Tagesprofil: sin-Kurve zwischen Sonnenaufgang (Stunde 6) und Sonnenuntergang (Stunde 19). |
| `np.ones()` | `numpy` | Erstellt ein Array mit lauter Einsen. Hier für das Kernkraft-Lastprofil: konstante Baseload, unabhängig von der Tageszeit. |
| `np.full()` | `numpy` | Erstellt ein Array gefüllt mit einem konstanten Wert. Hier für Kernkraft-Profil: `np.full(24, inst * 0.90)` = 24 Stunden mit 90% Auslastung. |
### Zellen 22 — Tagesverlauf-Animation
**Was passiert:** Eine animierte GIF zeigt den stündlichen Verbrauch vs. Produktion pro Netzzone (0–23 Uhr). `blit=False` weil die Bar-Farben sich ändern (blit=True würde nur bestimmte Artists neu zeichnen).


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `FuncAnimation()` | `matplotlib.animation` | Erstellt eine Animation durch wiederholten Aufruf einer Update-Funktion `func(frame)`. `frames=` = Liste der Frame-Parameter (hier: Stunden 0–23), `interval=` = Pause zwischen Frames in ms, `blit=` = Optimierung. |
| `PillowWriter()` | `matplotlib.animation` | Speichert eine Animation als GIF-Datei via Pillow. `fps=` = Frames pro Sekunde. Einfachste Option ohne externe Abhängigkeiten (ffmpeg etc.). |
| `.save()` | `FuncAnimation` | Rendert alle Frames und speichert als Datei. Hier: `.save(path, writer=PillowWriter(fps=3))` |
### Zellen 23–29 — BVI-Charts & Saisonale Analyse
**Was passiert:** BVI-gewichtete vs. naive Rollout-Szenarien als gestapelte Balken. Saisonale Kapazitätsfaktoren je Energieträger und Zone. Heatmap: BVI-Index nach Zone × Saison.

---
## NB07 — Cross-Border-Analyse (`07_Cross_Border.ipynb`)
Analysiert Stromflüsse zwischen der Schweiz und DE/AT/IT/FR und deren Einfluss auf Spotpreise.

### Zelle 1–2 — Setup & Grenzfluss-Download
**Was passiert:** Standard-Setup. ENTSO-E API wird für Grenzflüsse abgerufen: `query_crossborder_flows(from_country, to_country, ...)` für alle 4 Grenzpaare, jahresweise mit Retry. Ergebnis: Import/Export in MW pro Stunde.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.query_crossborder_flows()` | `entsoe` | Lädt die physikalischen Grenzflüsse (in MW) zwischen zwei Regelzonen. Positiv = Export, negativ = Import. Datenbasis für die Cross-Border-Korrelationsanalyse. |
### Zellen 3–6 — Analyse & Charts
**Was passiert:** Netto-Import/-Export pro Saison berechnen. Korrelation zwischen Grenzflüssen und Spotpreis analysieren. Streudiagramme zeigen: Mehr Import aus DE → tiefere CH-Preise?


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.corr()` | `pandas` | Berechnet die Pearson-Korrelationskoeffizienten zwischen allen Spaltenpaaren eines DataFrames. Wert nahe +1/-1 = starke lineare Abhängigkeit, nahe 0 = kein linearer Zusammenhang. |
| `.dropna()` | `pandas` | Entfernt Zeilen (oder Spalten) die NaN-Werte enthalten. Wichtig vor Korrelationsberechnungen: `corr()` ignoriert NaN, aber `merge()` kann NaN-Zeilen erzeugen. |

---
## NB08 — Marktdynamik (`08_Marktdynamik.ipynb`)
Untersucht Spread-Trend über Zeit und CAPEX-Lernkurven für die Wirtschaftlichkeitsprojektion.

### Zellen 1–3 — Spread-Trend
**Was passiert:** Historische Spread-Zeitreihe auf Trend analysieren. Lineare Regression via `np.polyfit()`, Trendlinie via `np.polyval()`. Berechnung: ab welchem Spread-Niveau ist Privatarbitrage Break-Even?


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.polyfit()` | `numpy` | Berechnet die Koeffizienten eines Polynoms, das am besten durch die Datenpunkte passt (Kleinste-Quadrate-Regression). Für Grad 1: liefert [Steigung, Achsenabschnitt] einer Geraden. |
| `np.polyval()` | `numpy` | Wertet ein Polynom (definiert durch Koeffizienten von `polyfit`) an gegebenen X-Werten aus. Liefert die Y-Werte der Regressionsgerade. |
| `LinearSegmentedColormap` | `matplotlib.colors` | Definiert eine eigene Farbpalette durch lineare Interpolation zwischen definierten Farb-Stützpunkten. Hier für benutzerdefinierte Gradient-Visualisierungen. |
### Zellen 4–6 — CAPEX-Lernkurve
**Was passiert:** CAPEX-Preisentwicklung wird modelliert: jährliche Kostensenkung um die Lernrate (config: 10%). Berechnung in welchem Jahr die Privatarbitrage Break-Even erreicht.

---
## NB08a — Animationen (`08a_Animationen.ipynb`)
Erstellt animierte GIFs der Preis- und Lastzeitreihen über 52 Kalenderwochen.

### Zellen 1–3 — Setup & Wochenaggregation
**Was passiert:** Standard-Setup. Preise und Last werden pro Kalenderwoche × Stunde aggregiert: Mittelwert, p25, p75. Optimiert: `wh_price = df_prices.groupby(['week','hour']).agg(mean=..., p25=lambda: quantile(0.25), p75=lambda: quantile(0.75))`. `dt.isocalendar().week` liefert ISO-Kalenderwochen (1–52).


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.dt.isocalendar()` | `pandas (.dt)` | Gibt ein DataFrame mit ISO-Kalenderwoche (`week`), Wochentag und Jahr zurück. ISO-KW beginnt montags, KW1 enthält den ersten Donnerstag des Jahres. |
### Zellen 5–6 — Animationen A & B: Preiskerzen + Netzlast
**Was passiert:** 4 GIFs (je eine pro Tageszeit 00/07/12/19 Uhr): 52 Frames, eine pro Kalenderwoche. Pre-Indexierung VOR der Animations-Schleife: `_price_by_hour[stunde] = wh_price[wh_price['hour']==stunde].set_index('week')`. In `update_a()` dann O(1)-Lookup statt Boolean-Filter über den gesamten DataFrame. Animations-B: 4-Panel-Chart alle Tageszeiten gleichzeitig, gleiche Pre-Index-Strategie für `update_b()`.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `.join()` | `pandas` | Verknüpft zwei DataFrames per Index (schneller als `merge()` wenn der Join-Key der Index ist). Hier für Quantil-Tabellen aus `groupby().quantile().unstack()`. |
| `ax.errorbar()` | `matplotlib.axes` | Zeichnet Datenpunkte mit Fehlerbalken. `yerr=[[unten],[oben]]` für asymmetrische Balken. Hier für Preiskerzen: Mittelpunkt = Mittelwert, Balken = p25/p75-Bereich. |
| `.set_data()` | `matplotlib.lines.Line2D` | Aktualisiert die X- und Y-Daten einer bestehenden Linie. Effizienter als eine neue Linie zu erstellen — der Artist bleibt bestehen, nur die Daten ändern sich. |
| `.set_height()` | `matplotlib.patches.Rectangle` | Ändert die Höhe eines Balken-Patches zur Laufzeit. Wird in Animationen verwendet um Balkendiagramme frame-by-frame zu aktualisieren. |
### Zelle 7 — Animation C: Spread-Animation (optimiert)
**Was passiert:** Wöchentlicher Spread (p75 − p25), Negativpreis-Anteil und Dispatch-Stunden werden als aufbauende Kurven animiert. Optimierungen: `week_spread` via `.quantile([]).unstack().join()` statt Lambda-agg; Tages-Quantile via einmaligem `groupby.quantile().unstack()` + `.join()` statt zwei `transform(lambda)`-Aufrufen. `week_spread_idx = week_spread.set_index('week')` für O(1)-Lookup in `update_c()`.

---
## NB09 — Revenue Stacking (`09_Revenue_Stacking.ipynb`)
Berechnet Mehrertrag durch Systemdienstleistungen (FCR/aFRR) zusätzlich zur Arbitrage.

### Zellen 1–3 — Setup & Erlösstacking-Modell
**Was passiert:** Literaturbasierte Schätzwerte für FCR- und aFRR-Erlöse (EUR/kWh/Jahr) werden definiert. Für jedes Segment und jeden Erlöstyp wird berechnet, wie viel Mehrertrag bei 20% reservierter FCR-Kapazität möglich wäre.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `ax.barh()` | `matplotlib.axes` | Horizontales Balkendiagramm. Praktisch wenn Kategorien-Labels lang sind (horizontal lesbar statt rotiert). `y=` = Kategorienachse, `width=` = Werte. |
### Zellen 4–5 — Charts
**Was passiert:** Gestapelter Balkendiagramm: Arbitrage-Erlös als Basis, FCR und aFRR als Aufstockung. Break-Even-Analyse: ab wann macht FCR die Investition rentabel?

---
## NB10 — Dispatch-Optimierung (`10_Dispatch_Optimierung.ipynb`)
Vergleicht reaktiven (NB02-Schwellenwert) mit day-ahead-optimalem Dispatch.

### Zellen 1–2 — Oracle-Dispatch
**Was passiert:** Der 'perfekte' Dispatch wird simuliert: Er kennt alle Preise des Tages im Voraus und lädt/entlädt optimal. `np.where(p <= q25)` findet alle Lade-Stunden als Array von Indices statt eines Python-Loops.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.where()` | `numpy` | Gibt Indices (oder Werte) zurück wo eine Bedingung erfüllt ist. `np.where(p <= q25)` = alle Positionen wo der Preis im Lade-Quantil liegt. Vectorized Alternative zu `[i for i,v in enumerate(p) if v <= q25]`. |
### Zellen 3–7 — Vergleich & Sensitivitätsanalyse
**Was passiert:** Reaktiv vs. Oracle für alle Segmente: Erlös, Zyklen, Effizienz. Sensitivitätsanalyse: wie verändert sich der Jahreserlös wenn die C-Rate (Leistung/Kapazität) variiert?

---
## NB11 — Technologievergleich (`11_Technologievergleich.ipynb`)
Vergleicht Li-Ion mit Redox-Flow, Vanadium-Flow, CAES, Schwungrad — Kosten, Lebensdauer, Wirkungsgrad.

### Zellen 1–2 — Technologiedaten laden
**Was passiert:** Kosten- und Leistungsdaten werden aus einer lokalen CSV geladen oder von der NREL Annual Technology Baseline API (öffentliche AWS S3 CSV). HTTP GET → Text-Response → `pd.read_csv(io.StringIO(resp.text))`.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.log()` | `numpy` | Natürlicher Logarithmus (Basis e). Für Lernkurven-Regression: `CAPEX = a × Cumulative_GWh^(-b)` wird durch Logarithmieren linearisiert. |
| `np.linspace()` | `numpy` | Erstellt n gleichmässig verteilte Werte in [start, stop]. Im Unterschied zu `arange()`: garantiert genau n Punkte inkl. Endpunkt. Hier für glatte Kurven-Plots. |
| `curve_fit()` | `scipy.optimize` | Passt eine benutzerdefinierte Funktion `f(x, *params)` an Datenpunkte an (nichtlineare Kleinste-Quadrate). Gibt optimale Parameter und Kovarianzmatrix zurück. |
### Zellen 3–6 — Vergleich & Radar-Chart
**Was passiert:** Wirtschaftlichkeit für alle Technologien berechnen. Radar-Chart (Spinnennetz) mit 5 Dimensionen: Kosten, Lebensdauer, Wirkungsgrad, Energiedichte, Skalierbarkeit. Lernkurven mit Trendlinie.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.array()` | `numpy` | Erstellt ein NumPy-Array aus einer Python-Liste. Im Unterschied zu `np.arange()`: direkte Werteangabe. Hier für definierte Radar-Chart-Winkel und Technologieparameter. |

---
## NB12 — Alternative Speicher (`12_Alternative_Speicher.ipynb`)
Tiefere Analyse von Pumpspeichern und saisonalen Wärmespeichern als Li-Ion-Alternativen für die Schweiz.

### Zellen 1–3 — Daten, Berechnung, Chart
**Was passiert:** Schweizer Pumpspeicher-Kapazitäten aus BFE-Daten. Vergleich: Pumpspeicher arbitriert saisonal (Sommer pumpen, Winter erzeugen), Batterie nur täglich/stündlich. Chart zeigt die Grössenordnungen nebeneinander.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `ax.set_yticks()` | `matplotlib.axes` | Setzt die Positionen der Y-Achsen-Ticks manuell. `.set_yticklabels()` setzt die zugehörigen Labels. Hier für kategorische Y-Achse in horizontalen Balkendiagrammen. |

---
## NB13 — Eigenverbrauch (`13_Eigenverbrauch.ipynb`)
Berechnet Mehrwert einer Batterie für PV-Haushalte (Eigenverbrauchsoptimierung statt Grid-Arbitrage).

### Zellen 1–3 — Setup & Eigenverbrauchssimulation
**Was passiert:** Haushaltstarife (HT/NT) aus Config in EUR. Synthetisches Tagesprofil: Solarertrag als Sinus-Glockenkurve (`np.sin()`), Haushaltsverbrauch mit Morgen- und Abendspitze. Simulation: Solarüberschuss → Batterie (wenn nicht voll), abends → Batterie (wenn nicht leer), sonst → Netzstrom. `np.where()` für vektorisierte Tarifwahl.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.where(arr, val_true, val_false)` | `numpy` | Ternärer Operator auf Arrays. Wo `arr` True → `val_true`, sonst `val_false`. Hier: `np.where(is_nt, NT_PREIS, HT_PREIS)` = vektorisierte Tarifwahl ohne Python-Loop. |
| `.cumsum()` | `pandas / numpy` | Berechnet die kumulierte Summe. Hier für den SoC-Verlauf: jede Stunde wird die Lade-/Entladeleistung summiert. Schneller als ein Python-Loop für die Zustandsberechnung. |
### Zellen 4–6 — Wirtschaftlichkeit & Vergleich
**Was passiert:** Eigenverbrauchsnutzen (Einsparung durch weniger Netzstrom-Kauf) wird berechnet und mit dem Arbitrage-Erlös verglichen. Für viele Privathaushalte ist Eigenverbrauch wirtschaftlich attraktiver.

---
## NB14 — Produkt-Steckbrief (`14_Produkt_Steckbrief.ipynb`)
Erstellt formatierte Produkt-Datenblätter (wie technische Steckbriefe) für drei Marktsegmente.

### Zellen 1–2 — Setup & Produktpakete
**Was passiert:** Alle Kennzahlen aus `transfer.json` und `wirtschaftlichkeit.csv` laden. Drei Produktpakete mit konkreten Empfehlungen für Grösse, Leistung, erwarteter ROI und Amortisationszeit definieren.
### Zellen 3–8 — Steckbrief-Charts
**Was passiert:** Für jedes Produktpaket: eine matplotlib Figure als Infografik. Kein Koordinatensystem — stattdessen freie Text- und Geometrie-Positionierung mit `ax.text()` und `ax.add_patch()`.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `ax.add_patch()` | `matplotlib.axes` | Fügt einen geometrischen 'Patch' (Rechteck, Kreis, Pfeil...) zur Achse hinzu. Hier für die Steckbrief-Rahmen und Trennlinien. Koordinaten sind in Achsen-Einheiten. |
| `ax.axis('off')` | `matplotlib.axes` | Blendet alle Achsenelemente aus. Kompaktere Alternative zu `ax.set_axis_off()`. Notwendig für Infografiken die wie Dokument-Seiten aussehen sollen. |

---
## NB15 — Kombinierte Simulation (`15_Kombinierte_Simulation.ipynb`)
Simuliert alle vier Dispatch-Strategien (Arbitrage, Eigenverbrauch, Hybrid statisch, Hybrid optimiert) in einem Lauf.

### Zellen 1–4 — Setup & Simulation
**Was passiert:** Alle 4 Modi werden für jedes Segment simuliert. Lokale Alias-Variablen zeigen auf CFG-Farben (`C_ARB = C_PRICE`). `np.tile(np.arange(24), n_days)` erzeugt einen Stunden-Vektor für mehrere Tage. Hybrid-Modi: statisch wechselt nach Tageszeit, optimiert nutzt Look-Ahead.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `np.tile()` | `numpy` | Wiederholt ein Array n-mal. `np.tile(np.arange(24), 365)` erzeugt einen Jahres-Stundenvektor [0,1,...,23,0,1,...]. Effizient für periodische Muster. |
| `np.sum()` | `numpy` | Summiert alle Elemente eines Arrays (oder entlang einer Achse). Hier für die Zählung von Zellen in einer Matrix die eine Bedingung erfüllen. |
| `mlines.Line2D()` | `matplotlib.lines` | Erzeugt ein Linien-Objekt für die Legende ohne echten Plot-Datenpunkt. Ermöglicht Legenden-Einträge mit Linien-Symbol für gestrichelte oder farbige Linien. |
| `mcolors.Normalize()` | `matplotlib.colors` | Identisch zu `Normalize()` — normiert Werte auf [0,1]. Hier importiert als `mcolors` statt direkt aus `matplotlib.colors`. |
| `plt.suptitle()` | `matplotlib.pyplot` | Setzt einen Haupttitel über alle Subplots einer Figure. `y=` steuert die vertikale Position (>1 = über der Figure-Grenze). |
### Zellen 5–9 — Charts & Transfer
**Was passiert:** Vergleichs-Charts: ROI aller 4 Modi nebeneinander, Cashflow-Kurven, Dispatch-Effizienz. Schlüsselkennzahlen in `transfer.json` unter `kombinierte_simulation`.

---
## NB99 — Datenprovenienz (`99_Datenprovenienz.ipynb`)
Dokumentiert alle Datenquellen: Herkunft, Lizenz, Verarbeitungsschritte. Wissenschaftliche Nachvollziehbarkeit.

### Zellen 1–3 — Setup & Quellen-Übersicht
**Was passiert:** `dataindex.csv` laden (das Register, das NB01/NB02 automatisch gefüllt haben). Alle Einträge nach Typ kategorisieren und anzeigen.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `pd.notna()` | `pandas` | Prüft elementweise ob Werte NICHT NaN sind. Gegenteil von `pd.isna()`. Hier für bedingte Formatierung: Zeilenzahl nur anzeigen wenn vorhanden. |
### Zellen 4–7 — Detaildokumentation & Charts
**Was passiert:** Zeitlinie aller Datensatz-Einträge als Scatter-Plot. Für jede Hauptdatenquelle: Herkunft, Format, Lizenz, Verarbeitungsschritte. Sankey-Diagramm zeigt den Datenfluss von Rohdaten durch alle Notebooks.


**Verwendete Bibliotheksobjekte & Funktionen (Erstnennung)**

| Funktion / Objekt | Library | Beschreibung |
|---|---|---|
| `import matplotlib.dates as mdates` | `matplotlib.dates` | Modul für datumsbezogene Achsenformatierung. `mdates.DateFormatter('%b %Y')` formatiert Ticks als 'Jan 2024'. `mdates.AutoDateLocator()` wählt automatisch sinnvolle Tick-Abstände. |
| `mpatches.FancyBboxPatch()` | `matplotlib.patches` | Rechteck mit abgerundeten oder anderen Eckenformen. `boxstyle='round,pad=0.3'` = abgerundete Ecken mit Innenabstand. Hier für Datenprovenienz-Flussdiagramm-Knoten. |
| `Sankey()` | `matplotlib.sankey` | Zeichnet ein Sankey-Diagramm: Flussvisualisierung mit Breite proportional zur Menge. Hier für den Datenfluss: welche Datenmengen fliessen in welche Notebooks. |
| `Line2D()` | `matplotlib.lines` | Identisch zu `mlines.Line2D()` — erzeugt ein Linien-Objekt für die Legende. |
### Zellen 8 — Reproduzierbarkeits-Statement
**Was passiert:** Formales Statement: 'Alle Daten können mit denselben API-Keys und NB01 neu geladen werden.' Gesamtübersicht: Datenfluss-Diagramm.