# Notebook-Dokumentation — Grid-Arbitrage mit Batteriespeichern
**SC26_Gruppe_2 · ZHAW CAS Information Engineering Scripting**

> **Für wen ist dieses Dokument?**
> Für jemanden, der grundlegendes Python versteht, aber noch nicht tief in Data Science eingetaucht ist. Jede Code-Zelle wird erklärt: was sie tut, warum sie es so tut, und welche Libraries dabei eine Rolle spielen.

> **Projektidee in einem Satz:** Kann man Geld verdienen, indem man Strom kauft wenn er billig ist (nachts/mittags bei Solarüberschuss), ihn in einer Batterie speichert, und wieder einspeist wenn er teuer ist? Das Projekt berechnet das für die Schweiz mit echten Marktdaten.

---

## NB00 — Projektübersicht (`00_Project_Overview.ipynb`)

Dieses Notebook ist reine Verwaltung: Es zeigt den Projektstatus als formatierte Tabelle und hat keinen fachlichen Recheninhalt.

### Zelle 1
**Was passiert:** Drei Statusbeschriftungen werden als Konstanten definiert (offene Aufgabe, in Arbeit, erledigt), dann wird eine verschachtelte Liste mit allen Projektaufgaben, Verantwortlichen, Fristen und Status aufgebaut. Am Ende druckt `pandas` das als lesbare Tabelle.

**Warum so:** Ein einziger Blick auf die Ausgabe zeigt den aktuellen Projektstand. Pandas ist hier die einfachste Lösung für eine formatierte Tabelle im Notebook.

**Verwendete Library:** `pandas` — die Standardbibliothek für tabellarische Daten in Python. Stell dir vor: Excel für Python.

---

## NB00b — Konventionen & Architektur (`00b_Konventionen.ipynb`)

Dieses Notebook enthält keine ausführbare Logik — es ist ein lebendiges Handbuch für das Team. Die einzige Code-Zelle ist auskommentiert.

### Zelle 1
**Was passiert:** Alle Zeilen beginnen mit `#` — das ist Python-Kommentar, der Code wird nicht ausgeführt. Die Zelle zeigt ein Musterbeispiel, wie man korrekt eine CSV-Datei lädt und dann sofort in der nächsten Zelle verifiziert (Shape, Zeitraum, Nullwerte, Wertebereich). Am Ende steht `print('Musterzelle — nur zur Demonstration.')` — das ist das einzige, was beim Ausführen passiert.

**Warum so:** Das Team braucht ein Referenzbeispiel für den korrekten Ladeprozess, ohne dass echte Daten angefasst werden. Auskommentierter Code als Vorlage ist eine gängige Notebook-Praxis.

---

## NB01 — Daten laden (`01_Daten_Laden.ipynb`)

Dieses Notebook hat einen einzigen Zweck: echte Rohdaten von der ENTSO-E-API herunterladen und auf der Festplatte speichern. Alle anderen Notebooks bauen darauf auf.

**ENTSO-E** ist die europäische Vereinigung der Übertragungsnetzbetreiber — sie betreiben eine öffentliche API mit Strom-Marktdaten für ganz Europa.

### Zelle 1
**Was passiert:** Das Skript prüft, ob vier Python-Pakete installiert sind (`pandas`, `requests`, `numpy`, `entsoe-py`). Fehlt eines, wird es automatisch nachinstalliert.

**Warum so:** Jupyter-Notebooks laufen auf verschiedenen Rechnern. Wer das Notebook zum ersten Mal öffnet, hat vielleicht nicht alle Abhängigkeiten installiert. Diese Zelle sorgt dafür, dass das Notebook überall funktioniert, ohne manuelle Installation.

**Warum `subprocess`?** Weil man aus Python heraus den Paket-Manager `pip` aufrufen muss — das ist wie das Starten eines Terminal-Befehls (`pip install pandas`) direkt aus dem Python-Code.

### Zelle 2
**Was passiert:** Alle benötigten Libraries werden geladen, dann wird `config.json` geöffnet und als Python-Dictionary (`CFG`) gelesen. Aus diesem Dictionary werden die wichtigsten Einstellungen als Variablen extrahiert: der Modus (`data` für echte Daten), ob ein Neuladen erzwungen werden soll, und der Zeitraum (Startjahr bis "heute"). Alle Verzeichnisse für Rohdaten, verarbeitete Daten und Zwischenergebnisse werden definiert und angelegt (falls nicht vorhanden).

**Warum so:** Die `config.json` ist die einzige Stelle im Projekt, wo Einstellungen gesetzt werden dürfen. Wenn man den Modus oder den Zeitraum ändern will, macht man das in der Config — nicht im Code. Das nennt man "Single Source of Truth" (SSOT). Die Funktion `needs_download()` prüft, ob eine Datei noch nicht existiert, zu klein ist (also offensichtlich unvollständig), oder ob ein Neuladen erzwungen wurde.

**Verwendete Libraries:** `os` — Dateisystem (Pfade, Verzeichnisse anlegen). `json` — JSON-Dateien lesen und schreiben. `numpy` — wird hier nur geladen, aber im Projekt für numerische Berechnungen gebraucht. `warnings` — Unterdrückt harmlose Warnmeldungen, die Notebooks unlesbar machen würden.

### Zelle 3
**Was passiert:** Zwei Hilfsfunktionen werden definiert. `log_dataindex()` schreibt einen Eintrag in die `dataindex.csv` — ein zentrales Register aller Datensätze mit Zeitstempel, Herkunft und Status. Wenn ein Eintrag für dieselbe Datei bereits existiert, wird der alte als "superseded" (abgelöst) markiert. `log_missing()` schreibt fehlende Daten in eine `missing.txt`-Datei.

**Warum so:** Bei Forschungsprojekten ist Nachvollziehbarkeit wichtig. "Woher kommen diese Daten? Von wann sind sie? Wurden sie neu geladen?" — das beantwortet die `dataindex.csv` automatisch. Der "superseded"-Mechanismus stellt sicher, dass man immer weiss, was aktuell gültig ist.

**Technisches Detail:** `pd.concat([df_idx, pd.DataFrame([row])], ignore_index=True)` fügt eine neue Zeile am Ende der Tabelle hinzu. Das ist sicherer als `df.append()` (welches in neueren Pandas-Versionen entfernt wurde).

### Zelle 4
**Was passiert:** Der ENTSO-E API-Schlüssel wird aus der `config.json` gelesen (niemals im Code selbst). Dann wird geprüft, ob der ENTSO-E-Server erreichbar ist — nicht die Website, sondern direkt der API-Endpunkt. HTTP-Antwortcodes werden interpretiert: 400 bedeutet "Server erreichbar, aber fehlende Parameter" (erwartet), 401 bedeutet "ungültiger Key", 503 bedeutet "Server überlastet". Danach wird eine Funktion `_fetch_prices_year()` definiert, die Spotpreise für ein einzelnes Jahr herunterlädt — mit bis zu 3 automatischen Wiederholungsversuchen bei 503-Fehlern.

**Warum so:** Der ENTSO-E-Server ist manchmal überlastet und antwortet mit 503. Ein direkter Download für mehrere Jahre auf einmal schlägt dann fehl. Die Lösung: jahresweise laden, bei Fehler kurz warten und nochmal versuchen. Das nennt man "Retry-Logik".

**Verwendete Library:** `requests` — HTTP-Anfragen aus Python. Wie ein Browser, der eine Webseite aufruft, nur programmatisch. `entsoe-py` — ein spezielles Paket für die ENTSO-E-API, das die komplexen XML-Antworten automatisch in pandas DataFrames umwandelt.

### Zelle 5
**Was passiert:** Die heruntergeladenen Spotpreisdaten werden kurz verifiziert: Wie viele Zeilen? Welcher Zeitraum? Gibt es fehlende Werte? Welcher Preisbereich? Dann werden die ersten drei Zeilen angezeigt.

**Warum so:** Nach jedem Daten-Download ist eine sofortige Verifikation Pflicht. Liefert die API plötzlich Werte in einer anderen Einheit? Fehlen ganze Monate? Das fällt hier sofort auf.

### Zelle 6
**Was passiert:** Analog zu Zelle 4 — dieselbe Retry-Logik, aber jetzt für die Netzlastdaten (wie viel Strom die Schweiz zu jedem Zeitpunkt verbraucht). Die Funktion `_fetch_load_year()` ist strukturell identisch mit `_fetch_prices_year()`.

**Warum so:** Spotpreise und Netzlast kommen von derselben API, haben dieselben Probleme (503-Fehler, Zeitzonenkomplikationen), und brauchen deshalb dieselbe Lösung. Code-Wiederholung statt Abstraktion ist hier bewusst gewählt, damit jede Funktion für sich lesbar ist.

### Zelle 7
**Was passiert:** Dieselbe Verifikation wie in Zelle 5, jetzt für die Netzlastdaten. Einheit ist Gigawatt (GW), nicht Megawatt/h.

### Zelle 8
**Was passiert:** Der Datenzeitraum (Startjahr, Endjahr, Anzahl tatsächlicher Jahre) wird in die `transfer.json` geschrieben. Diese Datei ist der Kommunikationskanal zwischen Notebooks — NB02 liest diesen Wert, um Jahresdurchschnitte korrekt zu berechnen.

**Warum so:** Wenn man NB01 mit mehr Daten neu ausführt (z.B. jetzt auch 2026), sollen alle nachgelagerten Notebooks automatisch mit der richtigen Anzahl Jahre rechnen. `transfer.json` ist die "Schnittstelle" zwischen den Notebooks — kein Notebook macht Annahmen über Zeiträume, es liest immer aus dieser Datei.

**Technisches Detail:** Der Code prüft zuerst, ob `transfer.json` bereits existiert und nicht leer ist, und lädt dann den bestehenden Inhalt — so werden nur die relevanten Schlüssel aktualisiert, der Rest bleibt erhalten.

### Zelle 9
**Was passiert:** Abschlusskontrolle: Für jede Pflicht-Datei wird geprüft, ob sie existiert und mindestens die Mindestgrösse hat. Ergebnis wird mit ✅/❌ angezeigt. Am Ende wird der Inhalt der `dataindex.csv` angezeigt.

**Warum so:** Ein klares "Go / No-Go" am Ende jedes Notebooks. Wer NB02 starten will, sieht auf einen Blick, ob alle Voraussetzungen erfüllt sind.

---

## NB02 — Datenanalyse & Dispatch-Simulation (`02_Daten_Analyse.ipynb`)

Das Herzstück des Projekts. Hier werden die Rohdaten bereinigt, der Batterie-Dispatch simuliert und die wirtschaftlichen Kennzahlen berechnet. Die Ergebnisse fliessen in alle anderen Notebooks ein.

### Zelle 1
**Was passiert:** Libraries laden, `config.json` lesen. Alle Simulations-Parameter werden aus der Config extrahiert: Lade-Quantil (0.25 = laden wenn Preis im untersten Viertel des Tages), Entlade-Quantil (0.75), minimaler/maximaler Ladezustand (5%/95%), Wirkungsgrad (92%). Wirtschaftlichkeits-Parameter: CAPEX pro kWh je Segment, OPEX-Rate (1.5%/Jahr), Lebensdauer (12 Jahre), daraus wird der Ziel-ROI berechnet (100/12 ≈ 8.3%/Jahr). Gleichzeitigkeitsszenario aus der Config laden und alle nötigen Verzeichnisse definieren.

**Warum so:** Dieselbe Struktur wie NB01. Alle Parameter kommen aus der Config — so kann man z.B. auf `optimistisch` wechseln, ohne eine Zeile Code zu ändern. Der Ziel-ROI wird berechnet (nicht aus der Config geladen), weil er eine abgeleitete Grösse ist: "Wie viel Rendite pro Jahr brauche ich, um in 12 Jahren die Investition zurückzuhaben?"

### Zelle 2
**Was passiert:** `transfer.json` wird geöffnet und `n_years` (Anzahl der simulierten Jahre) wird ausgelesen. Diesen Wert hat NB01 dort hineingeschrieben. Falls die Datei fehlt, gibt es eine Warnung.

**Warum so:** `n_years` ist entscheidend für alle Wirtschaftlichkeitsrechnungen. Wenn man z.B. Daten von 2023 bis 2025 hat, sind das 3 Jahre. Den Jahres-Erlös berechnet man dann als Gesamterlös ÷ 3. Dieser Wert muss aus NB01 kommen, nicht selbst geschätzt werden.

### Zelle 3
**Was passiert:** Dieselben Hilfsfunktionen `log_dataindex()` und `log_missing()` wie in NB01, plus `needs_rebuild()` — prüft ob eine verarbeitete Datei neu berechnet werden muss.

**Warum so:** Diese Funktionen werden in jedem Notebook neu definiert, das Dateien schreibt. Das ist Wiederholung, aber jedes Notebook bleibt damit für sich ausführbar — man muss nicht zuerst ein anderes Notebook laufen lassen, um diese Hilfsfunktionen verfügbar zu haben.

### Zelle 4
**Was passiert:** Die beiden Rohdatensätze (Spotpreise, Netzlast) werden von der Festplatte geladen und kurz auf ihre Struktur geprüft.

**Warum so:** NB01 hat die Daten gespeichert, NB02 liest sie — das ist die saubere Trennung: Laden und Verarbeiten sind zwei verschiedene Schritte.

### Zelle 5
**Was passiert:** Die Rohdaten werden bereinigt:
1. Zeitstempel werden auf UTC normiert (einheitliche Zeitzone für alle Berechnungen)
2. Ein lückenloser Stundenraster wird erzwungen — fehlen Stunden in den Daten, werden sie als leere Zeilen eingefügt
3. Lücken bis zu 3 Stunden werden linear interpoliert (geschätzter Mittelwert), längere Lücken mit dem letzten bekannten Wert aufgefüllt
4. Extreme Ausreisser werden gekappt (unter -500 EUR/MWh oder über 3000 EUR/MWh)
5. Zeitliche Merkmale werden berechnet: Stunde des Tages, Monat, Wochentag, Jahreszeit
6. Die bereinigte Datei wird als `ch_spot_prices_clean.csv` gespeichert

**Warum so:** Echte API-Daten sind selten perfekt. Stunden können fehlen (API-Ausfall, Sommerzeit-Umstellung). Negative Preise bis -500 EUR/MWh sind real (zu viel Solar), aber -9999 ist ein Datenfehler. Zeitfeatures braucht man für die Dispatch-Logik (welche Stunde des Tages ist es?). Das `reindex` auf den vollständigen Stundenraster ist ein eleganter Pandas-Trick: statt Lücken zu suchen, sagt man einfach "mein Index soll jede Stunde haben" und Pandas ergänzt die fehlenden.

**Verwendete Funktion:** `.interpolate(method='linear', limit=3)` füllt bis zu 3 aufeinanderfolgende NaN-Werte durch lineare Interpolation (Linie zwischen den Nachbarn).

### Zelle 6
**Was passiert:** Verifikation der bereinigten Daten: Form, Datentypen, neue Spalten, fehlende Werte, erste Zeilen anzeigen.

### Zelle 7
**Was passiert:** Das Tagesprofil der Strompreise wird analysiert. Für jede Stunde des Tages (0–23) werden Durchschnitt und Standardabweichung berechnet. Die 4 günstigsten und 4 teuersten Stunden werden identifiziert. Der Arbitrage-Spread (Preisunterschied zwischen teuren und günstigen Stunden) wird berechnet. Saisonale Durchschnitte werden ausgegeben.

**Warum so:** Dieser Abschnitt beantwortet die Kernfrage: Wie gross ist das Arbitrage-Potential im Durchschnitt? Wenn der Spread 30 EUR/MWh beträgt und die Batterie 10 kWh fasst, kann man theoretisch 0.30 EUR pro vollständigem Lade-/Entladezyklus verdienen.

### Zelle 8
**Was passiert:** Die Dispatch-Simulation wird als Funktion `simulate_battery()` definiert. Dies ist der algorithmische Kern des Projekts:

**Schritt 1:** Für jeden Tag wird der 25%-Quantil-Preis (Ladechwellenwert) und 75%-Quantil-Preis (Entladeschwellenwert) berechnet — einmalig vorab für alle Tage, nicht für jede Stunde separat.

**Schritt 2:** Alle Daten werden als NumPy-Arrays aufbereitet. Das ist entscheidend für die Geschwindigkeit: Python-Schleifen über Pandas-Zeilen (`iterrows()`) sind extrem langsam, Arrays in NumPy laufen in optimiertem C-Code.

**Schritt 3:** Die eigentliche Stunden-für-Stunden-Simulation. Für jede Stunde: Wenn Preis unter dem Tagesschwellenwert und Batterie nicht voll → laden. Wenn Preis über dem Schwellenwert und Batterie nicht leer → entladen. Der Wirkungsgrad (92%) wird auf den Ladevorgang angewendet (Square-Root-Trick: beim Laden geht Energie verloren, beim Entladen auch, zusammen macht das ~85% Round-Trip).

**Warum NumPy statt Pandas-Loop?** Für 26.000 Stunden (3 Jahre) wäre ein `iterrows()`-Loop etwa 50-mal langsamer als NumPy-Arrays. Bei 4 Segmenten wäre das spürbar. Mit NumPy läuft die gesamte Simulation in Sekunden.

**Verwendete Library:** `numpy` — Numerische Berechnungen mit Arrays. Stell dir vor: Taschenrechner-Operationen auf tausende Zahlen gleichzeitig, statt eine nach der anderen.

### Zelle 9
**Was passiert:** Die Simulation wird für alle vier Marktsegmente ausgeführt:
- Privat (10 kWh, 5 kW Leistung)
- Gewerbe (100 kWh, 30 kW)
- Industrie (1 MWh, 200 kW)
- Utility (10 MWh, 1000 kW)

Der jährliche Erlös wird als Durchschnitt über alle simulierten Jahre berechnet (Gesamterlös ÷ n_years). Ergebnisse werden tabellarisch ausgegeben.

**Warum Durchschnitt statt nur ein Jahr?** Weil Preise von Jahr zu Jahr schwanken. Ein einzelnes Jahr könnte ungewöhnlich hohe oder niedrige Spreads haben. Der Durchschnitt über mehrere Jahre ist ein realistischerer Massstab.

### Zelle 10
**Was passiert:** Für jedes Segment werden die wirtschaftlichen Kennzahlen berechnet:
- **CAPEX:** Anfangsinvestition (Kapazität × CAPEX pro kWh aus der Config)
- **OPEX:** Jährliche Betriebskosten (1.5% des CAPEX)
- **Netto-Erlös:** Jahreserlös minus OPEX
- **Amortisation:** CAPEX ÷ Netto-Erlös = Anzahl Jahre bis zur Rückzahlung
- **ROI:** Netto-Erlös ÷ CAPEX × 100 = Rendite in Prozent pro Jahr

Alles wird als CSV gespeichert.

**Warum OPEX abziehen?** Weil eine Batterie Wartung, Versicherung und Monitoring kostet, auch wenn sie nichts einspeist. Diese Kosten fressen einen Teil des Erlöses auf. 1.5% ist ein branchenüblicher Schätzwert für Heimspeicher in der Schweiz.

### Zelle 11
**Was passiert:** Kurze Verifikation der Wirtschaftlichkeitstabelle: Anzahl Segmente, erste Zeilen.

### Zelle 12
**Was passiert:** Szenarien für die Netzentlastung werden berechnet. Es gibt vier Zeitpunkte (Status Quo, Moderat 2027, Ambitioniert 2030, Transformativ 2035) mit jeweils unterschiedlicher Anzahl Batteriesysteme je Segment. Die Gleichzeitigkeitsrate aus der Config (z.B. 40% beim "realistischen" Szenario) skaliert die theoretische Leistung — weil nicht alle Batterien gleichzeitig einspeisen. Das Ergebnis: wie viele MW Spitzenlast werden vom Netz entlastet?

**Warum Gleichzeitigkeit?** Stell dir vor, 50.000 Privathaushalte haben je eine 5-kW-Batterie. Theoretisch wären das 250 MW. Aber nicht alle laden/entladen zur exakt gleichen Sekunde. Bei 40% Gleichzeitigkeit sind es real nur 100 MW, die das Netz gleichzeitig entlasten. Das ist trotzdem bedeutsam für den Netzbetrieb.

### Zelle 13
**Was passiert:** Die monatliche Spread-Zeitreihe wird berechnet: Für jeden Tag wird der Intra-Tag-Spread berechnet (p75-Preis minus p25-Preis). Diese Tageswerte werden pro Monat zu einem Median aggregiert. Zusätzlich: Volatilität, Durchschnittspreis und Anzahl Stunden mit negativen Preisen pro Monat. Alles wird als `spread_zeitreihe.csv` gespeichert.

**Warum Median statt Mittelwert?** Der Median ist robuster gegen einzelne extreme Tage. Ein Sturm-Tag mit extremem Spread würde den Monatsdurchschnitt verzerren, den Median kaum.

### Zelle 14
**Was passiert:** Verifikation der Spread-Zeitreihe.

### Zelle 15
**Was passiert:** Alle berechneten Kennzahlen werden in `transfer.json` geschrieben: Spread-Statistiken, Anzahl Simulationsjahre, und für jedes Segment ROI, Netto-Erlös, Jahreserlös, CAPEX und Amortisationszeit.

**Warum so:** Alle nachgelagerten Notebooks (NB05 Business Strategy, NB08 Marktdynamik usw.) brauchen diese Werte. Statt überall neu zu berechnen, liest jedes Notebook einfach aus `transfer.json`. Wenn NB02 neu läuft, werden automatisch alle anderen Notebooks mit aktuellen Werten versorgt.

### Zelle 16
**Was passiert:** Abschlusskontrolle für NB02: Alle Output-Dateien werden auf Existenz und Mindestgrösse geprüft. Dann ein Hinweis: Grenzflüsse und BFE-Daten werden erst in den Kür-Notebooks NB06/NB07 geladen.

---

## NB03 — Visualisierungen (`03_Visualisierungen.ipynb`)

Dieses Notebook erzeugt alle 8 Pflicht-Charts. Es berechnet nichts — es liest die bereits berechneten Daten aus NB02 und stellt sie grafisch dar.

### Zelle 1
**Was passiert:** Libraries laden, config.json lesen. Wichtig: Die Farben und Stil-Konstanten werden aus der Config geladen (`_viz = CFG.get('visualisierung', {}).get('farben', {})`). `matplotlib.rcParams` wird global gesetzt — das bedeutet, alle nachfolgenden Charts erben automatisch die dunkle Hintergrundfarbe, die Tick-Farben, Schriftgrössen etc. Dann werden vier CSV-Dateien geladen: bereinigte Preise, Wirtschaftlichkeit, Netzentlastungsszenarien, Netzlastdaten.

**Warum rcParams global?** Ohne globale Einstellungen müsste jeder der 8 Charts dieselben 10 Zeilen Formatierungs-Code wiederholen (`ax.set_facecolor(...)`, `ax.tick_params(...)`, usw.). Mit `rcParams.update()` wird das einmal definiert und gilt überall.

**Verwendete Library:** `matplotlib` — die Standard-Visualisierungsbibliothek für Python. Denk an eine programmatische Version von Excel-Charts.

### Zelle 2
**Was passiert:** Verifikation der geladenen Daten.

### Zelle 3 — Chart 1: Wirtschaftlichkeit-Summary
**Was passiert:** Ein 2×2-Grid aus vier Panels wird erstellt:
- **Panel 1 (oben links):** Kumulierte Cashflow-Kurven für alle 4 Segmente über die 12-jährige Lebensdauer. Jede Kurve zeigt, wann (falls überhaupt) die Investition amortisiert ist.
- **Panel 2 (oben rechts):** Balkendiagramm: ROI pro Jahr je Segment, mit einer gestrichelten Linie für den Ziel-ROI (8.3%/Jahr).
- **Panel 3 (unten links):** Erlös pro kWh Kapazität — normiert auf die Grösse, damit die Segmente vergleichbar sind.
- **Panel 4 (unten rechts):** CAPEX versus kumulierter Netto-Erlös als Doppelbalken.

**Warum Symlog-Skala bei Panel 1?** Die CAPEX-Werte unterscheiden sich um Faktor 1000 (Privat: 4.000 EUR, Utility: 1.800.000 EUR). Eine normale Skala würde die kleinen Segmente nicht zeigen. Symlog ist eine "symmetrische logarithmische" Skala: linear nahe der Null (damit negative Werte korrekt dargestellt werden), logarithmisch für grosse Werte.

### Zellen 4–8 — Charts 2–5
**Was passiert (allgemeines Muster):** Jede dieser Zellen erstellt einen Chart mit demselben Grundgerüst:
1. `fig, ax = plt.subplots(...)` — neues Bild und Achse erstellen
2. `fig.patch.set_facecolor(BG_DARK)` — Hintergrundfarbe setzen (wird von rcParams manchmal überschrieben bei savefig)
3. Daten aufbereiten und plotten
4. Achsenbeschriftungen, Titel, Legende
5. `plt.savefig(...)` — Chart als PNG speichern (in `output/charts/<szenario>/`)
6. `plt.show()` — Chart im Notebook anzeigen

**Chart 2:** Tagesprofil der Spotpreise — Durchschnittspreis pro Stunde (0–23 Uhr) als Flächen-Linienchart. Zeigt deutlich das Mittags-Solar-Tal und die Abend-Spitze.

**Chart 3:** Saisonale Spread-Analyse — für jede Jahreszeit die Verteilung des täglichen Spreads als Violin-Plot. Ein Violin-Plot ist wie ein Boxplot, aber zeigt zusätzlich die Dichteverteilung der Werte.

**Chart 4:** Netzentlastung — Balken für die drei Szenarien (2027/2030/2035), wie viel MW Spitzenlast entlastet werden.

**Chart 5:** Spread-Zeitreihe — monatlicher Median-Spread von 2023 bis heute als Linienchart, mit farbigen Jahresbereichen.

### Zellen 9–14 — Charts 6–8 und Abschlusskontrolle
**Was passiert:** 
**Chart 6:** Preisverteilung als Histogramm — alle Stundenpreise von 2023–heute. Zeigt, wie oft welche Preisbereiche vorkommen, inklusive negativer Preise.

**Chart 7:** Dispatch-Übersicht — für ein Beispielwoche wird gezeigt, wann die Batterie lädt (blau), entlädt (rot), und was der Strompreis (orange) war.

**Chart 8:** Wirtschaftlichkeit-Heatmap — eine Matrix: Segmente vs. Szenarien, Farbe = ROI.

**Abschlusskontrolle:** Alle 8 PNG-Dateien werden auf Existenz geprüft.

---

## NB04 — Business Case (`04_Business_Case.ipynb`)

Dieses Notebook erzeugt keinen eigenen Code-Output — es ist ein lesbarer Bericht. Die Code-Zellen laden und zeigen nur die Charts, die NB03 bereits gespeichert hat.

### Zelle 1
**Was passiert:** `config.json` laden, Pfad zum Charts-Verzeichnis definieren. Eine Hilfsfunktion `show_chart()` wird definiert: Sie lädt eine PNG-Datei und zeigt sie im Notebook an. Falls die Datei nicht existiert, gibt es eine lesbare Fehlermeldung statt eines kryptischen Fehlers.

**Warum so:** NB04 ist für die Präsentation — jemand, der den Business Case liest, soll die Charts sehen, nicht den Code. `display(Image(...))` rendert ein Bild direkt im Notebook.

### Zellen 2–13
**Was passiert:** Jede Zelle ruft `show_chart('nb03_....png')` auf und zeigt einen der 8 Pflicht-Charts. Zwischen den Charts stehen Markdown-Zellen mit der Interpretation.

### Zelle 14
**Was passiert:** Eine Zusammenfassungstabelle der Wirtschaftlichkeitskennzahlen wird direkt aus `wirtschaftlichkeit.csv` geladen und als formatierte Tabelle angezeigt. Zusätzlich werden einige wichtige Schlussfolgerungen als Text berechnet und ausgegeben (z.B. "Kein Segment erreicht den Ziel-ROI durch Arbitrage allein").

---

## NB05 — Business Strategy (`05_Business_Strategy.ipynb`)

Das grösste Notebook: 27 Code-Zellen. Fasst alle Ergebnisse aus Pflicht und Kür zu einer Strategie-Empfehlung zusammen. Liest aus `transfer.json`, lädt Charts der Kür-Notebooks und zeigt sie mit Interpretation.

### Zelle 1 — Setup
**Was passiert:** Libraries und config.json laden. `transfer.json` komplett lesen — alle Werte, die NB01–NB15 dort hinterlegt haben, sind jetzt verfügbar. Verzeichnisse für Charts aller Kür-Notebooks werden definiert.

### Zellen 2–26
**Was passiert (Muster):** Jede Zelle behandelt einen Aspekt der Strategie:
- Marktpotential: wie viele Batterien gibt es in der Schweiz? (aus transfer.json)
- Revenue-Stack: welche Einnahmequellen gibt es neben Arbitrage? (FCR, aFRR, Eigenverbrauch)
- Technologievergleich: Li-Ion vs. Redox-Flow vs. Schwungrad (aus NB11)
- Räumliche Analyse: wo in der Schweiz ist das Potential am grössten? (aus NB06)
- Fazit und Handlungsempfehlungen

### Zelle 27 — Transfer-Output
**Was passiert:** Alle Strategie-Schlüsselkennzahlen werden in `transfer.json` unter dem Schlüssel `strategie` gespeichert, für eventuelle weitere Notebooks.

---

## NB06 — Räumliche Analyse (`06_Raeumliche_Analyse.ipynb`)

Das komplexeste Kür-Notebook: 29 Zellen, GeoPandas, echte Geodaten der Schweiz. Ziel: Zeigen, in welchen Regionen der Schweiz Batteriespeicher den grössten Nutzen hätten.

### Zelle 1 — Setup & Bibliotheken
**Was passiert:** Mehrere spezielle Libraries werden bei Bedarf installiert: `geopandas` (Geodaten), `requests` (HTTP), `scipy` (wissenschaftliche Algorithmen), `shapely` (geometrische Berechnungen). Dann config.json laden und Farb-/Stil-Konstanten setzen. Pfade für Geodaten und Charts werden definiert.

**Warum GeoPandas?** GeoPandas ist wie Pandas, aber für räumliche Daten. Es kann Schweizer Kantonsgrenzen laden, Punkte auf einer Karte darstellen, und räumliche Operationen wie "Welche BFE-Anlage liegt in welchem Kanton?" ausführen.

### Zellen 2–4 — Schweizer Geometrien laden
**Was passiert:** Die Schweizer Kantonsgrenzen und Gemeindegrenzen werden von `swisstopo` (dem Schweizer Bundesamt für Landestopografie) heruntergeladen — als GeoPackage-Datei (`.gpkg`), ein standardisiertes Format für Geodaten. Falls die Datei bereits vorhanden ist, wird sie nicht nochmal heruntergeladen.

**Warum nicht einfach ein Bild der Schweiz?** Weil wir Datenpunkte (Kraftwerksstandorte, Kantonsgrenzen) auf der Karte platzieren wollen. Dafür brauchen wir echte Koordinaten — die GeoPackage-Datei gibt uns Polygone der Kantonsgrenzen als Koordinaten.

### Zellen 5–8 — BFE-Daten laden
**Was passiert:** Das Bundesamt für Energie (BFE) stellt eine Datenbank aller Schweizer Elektrizitätsproduktionsanlagen bereit. Diese wird heruntergeladen und gefiltert: Nur Batteriespeicher und relevante Anlagen. Die Koordinaten werden in das Standard-Koordinatensystem (WGS84 = Längen-/Breitengrad) umgerechnet, da Schweizer Daten im nationalen CH1903+-System gespeichert sind.

**Was ist ein Koordinatensystem?** Die Schweiz hat ihr eigenes System mit Koordinaten wie (2600000, 1200000) — das sind Meter vom nationalen Referenzpunkt. Google Maps kennt nur Längengrad/Breitengrad. Die Umrechnung macht `pyproj` im Hintergrund von GeoPandas.

### Zellen 9–14 — Bevölkerungsdaten
**Was passiert:** Die BFS (Bundesamt für Statistik) STATPOP-Daten werden via PXWeb-API geladen — Bevölkerungszahlen pro Kanton und Gemeinde für 2023. Diese werden mit den Geodaten verknüpft: Jeder Kanton bekommt seine Einwohnerzahl.

**Warum Bevölkerungsdaten?** Weil das Potential für Heimspeicher proportional zur Bevölkerung ist: Mehr Menschen = mehr potenzielle Heimspeicher.

### Zellen 15–22 — BVI-Index berechnen
**Was passiert:** Der "Batterie-Verwertbarkeits-Index" (BVI) wird für jede Region berechnet. Er kombiniert drei Faktoren (mit Gewichten aus config.json):
- **Netzimbalance** (Gewicht 50%): Wie oft ist die Region überlastet?
- **Engpassnähe** (Gewicht 30%): Wie nah ist sie an bekannten Netzengpässen?
- **Saisonal** (Gewicht 20%): Wie stark schwankt der lokale Verbrauch saisonal?

Jeder Faktor wird auf 0-100 normiert, dann gewichtet summiert.

**Warum ein zusammengesetzter Index?** Kein einzelner Wert sagt alles. Eine Region kann viel Solarenergie produzieren (gut für Batterien), aber gleichzeitig gute Netzanschlüsse haben (weniger Engpassnutzen). Der Index kombiniert alle relevanten Faktoren.

### Zellen 23–29 — Karten erstellen
**Was passiert:** Für jede Analyse wird eine Schweizer Karte erstellt:
- Karte 1: Bevölkerungsdichte pro Kanton (Choropleth-Karte — eingefärbte Flächen)
- Karte 2: Bekannte Netzengpässe und BVI-Index
- Karte 3: Standorte bestehender Batteriespeicher
- Karte 4: Kombinierte Empfehlungskarte

**Was ist eine Choropleth-Karte?** Eine thematische Karte, bei der Gebiete nach einem Wert eingefärbt werden (ähnlich wie politische Karten, die Länder nach BIP einfärben).

---

## NB07 — Cross-Border-Analyse (`07_Cross_Border.ipynb`)

Analysiert die Stromflüsse zwischen der Schweiz und ihren Nachbarn (DE, AT, IT, FR) und ob diese eine Rolle für die Arbitrage-Strategie spielen.

### Zelle 1 — Setup & Grenzfluss-Download
**Was passiert:** Neben dem üblichen Setup wird die ENTSO-E-API für Grenzfluss-Daten (physikalische Stromflüsse über Grenzkuppelleitungen) abgerufen. Für jede Grenze (CH-DE, CH-AT, etc.) werden Import- und Exportdaten jahresweise heruntergeladen.

**Warum Grenzflüsse?** Die Schweiz ist ein wichtiges Durchgangsland für europäischen Strom. Wenn grosse Mengen Strom von Deutschland nach Italien fliessen (z.B. bei viel Solarenergie in DE), drückt das den Schweizer Spotpreis. Diese Korrelation zu verstehen hilft, bessere Dispatch-Strategien zu entwickeln.

### Zellen 2–4 — Analyse
**Was passiert:** Nettoimport/-export pro Monat und Saison wird berechnet. Korrelation zwischen Grenzflüssen und Spotpreis wird analysiert. Ein Streudiagramm zeigt: Mehr Import aus Deutschland → tiefere Schweizer Preise?

### Zellen 5–7 — Charts und Transfer
**Was passiert:** Grenzfluss-Charts werden erstellt und gespeichert. Schlüsselkennzahlen (z.B. "CH war 2024 netto Stromexporteur mit X TWh") werden in transfer.json geschrieben.

---

## NB08 — Marktdynamik (`08_Marktdynamik.ipynb`)

Untersucht, wie sich der Arbitrage-Spread über die Zeit verändert hat und wie er sich entwickeln könnte — und wie sinkende CAPEX-Kosten die Wirtschaftlichkeit verbessern.

### Zelle 1 — Setup
**Was passiert:** Zusätzliche Parameter aus dem Kür-Abschnitt der config.json geladen: Spread-Break-Even-Wert (unter welchem Spread ist Arbitrage nicht mehr wirtschaftlich?), CAPEX-Lernrate (jährliche Kostensenkung durch Skaleneffekte).

### Zellen 2–3 — Spread-Trend
**Was passiert:** Die historische Spread-Zeitreihe aus `spread_zeitreihe.csv` wird auf einen Trend analysiert. Eine lineare Regression wird berechnet: Steigt oder sinkt der Spread über die Zeit? Bei welchem Spread wäre Privatarbitrage Break-Even?

**Warum Regression?** Weil man aus historischen Daten eine Tendenz ableiten will. `numpy.polyfit` berechnet die beste Gerade durch die Monatspunkte.

### Zellen 4–6 — CAPEX-Lernkurve
**Was passiert:** Die erwartete Preisentwicklung für Batterien wird modelliert. CAPEX sinkt jährlich um die Lernrate (z.B. 10%). Es wird berechnet, in welchem Jahr die Privatarbitrage Break-Even erreicht — basierend auf sinkenden Kosten, nicht steigendem Spread.

**Was ist eine Lernkurve?** In der Industrie gilt: Wenn sich die Produktionsmenge verdoppelt, sinken die Stückkosten um einen festen Prozentsatz (historisch ~15-20% bei Batterien). Das ist der Grund, warum Tesla-Batterien heute zehnmal günstiger sind als 2010.

---

## NB08a — Animationen (`08a_Animationen.ipynb`)

Erstellt animierte GIFs der wichtigsten Zeitreihen.

### Zelle 1 — Setup
**Was passiert:** Zusätzlich zu den Standard-Libraries wird `matplotlib.animation` importiert — das Modul für animierte Charts. `PillowWriter` erlaubt das Exportieren als GIF.

### Zellen 2–4 — Preis-Animation
**Was passiert:** Eine Animation wird erstellt, die den Spot-Preis über das Jahr "abrollt" — wie ein Ticker. Für jeden Monat wird ein Frame gerendert, alle Frames werden zu einem GIF zusammengefügt.

**Warum GIF und nicht Video?** GIFs laufen ohne Video-Player direkt im Browser und in Präsentationen. Für wissenschaftliche Dokumentation sind sie einfacher einzubetten.

**Technisches Detail:** `FuncAnimation(fig, update_func, frames=n)` ruft `update_func(frame_nr)` für jeden Frame auf. Diese Funktion ändert die Datenmenge, die der Chart zeigt. Dann wird alles als GIF gespeichert.

### Zellen 5–8 — Weitere Animationen
**Was passiert:** Analog: Animationen für Spread-Entwicklung, saisonale Preisverteilung, Dispatch-Simulation einer Beispielwoche.

---

## NB09 — Revenue Stacking (`09_Revenue_Stacking.ipynb`)

Berechnet, wie viel Mehrertrag möglich wäre, wenn die Batterie nicht nur Arbitrage macht, sondern auch Systemdienstleistungen erbringt (Frequenzhaltung, Regelenergie).

### Zellen 1–2 — Setup & Marktpreise laden
**Was passiert:** Neben config.json werden historische Preise für FCR (Frequency Containment Reserve — bezahlte Bereitschaft, die Frequenz zu stabilisieren) und aFRR (automatische Frequenzwiederherstellung) geladen. Diese Preise kommen aus öffentlichen Quellen (Swissgrid, ENTSO-E).

**Was ist FCR?** Wenn ein grosses Kraftwerk plötzlich ausfällt, muss die Netzfrequenz (50 Hz) innerhalb von 30 Sekunden stabilisiert werden. Batterien sind ideal dafür: Sie können in Millisekunden reagieren. Netzbetreiber bezahlen für die blosse Bereitschaft dazu — auch wenn die Batterie nicht eingesetzt wird.

### Zellen 3–5 — Berechnung & Transfer
**Was passiert:** Für jedes Segment wird berechnet, wie viel zusätzlicher Erlös durch FCR und aFRR möglich wäre, wenn 20% der Kapazität dafür reserviert werden. Das wird mit dem reinen Arbitrage-Erlös verglichen. Ergebnis in `transfer.json`.

---

## NB10 — Dispatch-Optimierung (`10_Dispatch_Optimierung.ipynb`)

Vergleicht den einfachen reaktiven Dispatch (NB02: Schwellenwertmodell) mit einem Day-Ahead-optimalen Dispatch (als ob man die morgigen Preise perfekt kennen würde).

### Zellen 1–2 — Setup & Optimaler Dispatch
**Was passiert:** Der "Oracle"-Dispatch wird simuliert: Er kennt alle Preise eines Tages im Voraus und lädt/entlädt perfekt optimal. Das ist die theoretische Obergrenze — in der Realität unmöglich, aber nützlich als Vergleichsgrösse.

**Warum vergleichen?** Das zeigt die "Effizienzlücke": Wie viel lässt man auf dem Tisch liegen, weil man nicht in die Zukunft sehen kann? Wenn der reaktive Dispatch 80% des optimalen erreicht, ist er gut. Wenn nur 40%, lohnt es sich, bessere Prognosen zu entwickeln.

### Zellen 3–7 — Analyse & Charts
**Was passiert:** Beide Dispatch-Strategien werden für alle Segmente verglichen: Erlös, Anzahl Lade-/Entlade-Zyklen, Effizienz. Charts zeigen die Unterschiede. Ergebnisse in `transfer.json`.

---

## NB11 — Technologievergleich (`11_Technologievergleich.ipynb`)

Vergleicht Lithium-Ionen-Batterien mit alternativen Speichertechnologien.

### Zellen 1–2 — Setup & Technologiedaten
**Was passiert:** Technologieparameter werden geladen — entweder aus einer lokalen CSV (manuell zusammengestellt) oder aus der NREL Annual Technology Baseline (ATB), einer US-amerikanischen öffentlichen Datenbank mit Kostenprojektionen für Energietechnologien auf AWS S3 gespeichert.

**Technologien:** Li-Ion (Standard), Redox-Flow (längere Lebensdauer, tiefere Energiedichte), Vanadium-Flow (sehr langlebig, teuer), Compressed Air (gross, billig), Schwungrad (sehr schnell, wenig Kapazität).

### Zellen 3–6 — Vergleich & Charts
**Was passiert:** Für jede Technologie werden dieselben Wirtschaftlichkeitskennzahlen wie in NB02 berechnet, dann nebeneinander verglichen. Ein Radar-Chart (Spinnennetz) zeigt alle Dimensionen gleichzeitig: Kosten, Lebensdauer, Wirkungsgrad, Leistungsdichte, Skalierbarkeit.

---

## NB12 — Alternative Speicher (`12_Alternative_Speicher.ipynb`)

Ergänzung zu NB11: Tiefere Analyse von zwei besonders interessanten Alternativen für die Schweiz — Pumpspeicher und saisonale Wärmespeicher.

### Zellen 1–3 — Daten, Berechnung, Chart
**Was passiert:** Schweizer Pumpspeicherkapazitäten aus BFE-Daten. Vergleich: Ein Pumpspeicher kann saisonal arbitrieren (Wasser im Sommer hochpumpen, im Winter Strom erzeugen). Eine Batterie kann nur stündlich/täglich arbitrieren. Chart zeigt die Grössenordnungen.

---

## NB13 — Eigenverbrauch (`13_Eigenverbrauch.ipynb`)

Berechnet den Mehrwert einer Batterie für Haushalte mit Photovoltaik-Anlage — unabhängig von der Netz-Arbitrage.

### Zelle 1 — Setup
**Was passiert:** Zusätzliche Parameter aus config.json: Haushalt-Tarif (Hochtarif/Niedertarif in CHF), umgerechnet in EUR. Eine Batterie kann Solar-Überschuss vom Mittag speichern und abends verwenden — statt ihn für wenig Geld einzuspeisen.

### Zellen 2–3 — Eigenverbrauchssimulation
**Was passiert:** Ein synthetisches Tagesprofil wird erzeugt: Solarertrag (Glockenkurve um Mittag), Haushaltsverbrauch (morgens und abends Spitzen). Die Batterie entscheidet: Solarüberschuss speichern oder ins Netz einspeisen? Abends: aus der Batterie versorgen oder teuren Netzstrom kaufen?

**Warum synthetisches Profil?** Echte Messdaten pro Haushalt sind aus Datenschutzgründen nicht verfügbar. Synthetische Profile (aus Norm-Lastprofilen der Energiebranche) sind realistische Approximationen.

### Zellen 4–6 — Wirtschaftlichkeit & Vergleich
**Was passiert:** Der Eigenverbrauchsnutzen (Einsparung durch weniger Netzstrom-Kauf) wird berechnet und mit dem Arbitrage-Erlös verglichen. Für viele Privathaushalte ist Eigenverbrauch wirtschaftlich interessanter als Grid-Arbitrage.

---

## NB14 — Produkt-Steckbrief (`14_Produkt_Steckbrief.ipynb`)

Erstellt formatierte Steckbrief-Karten für drei konkrete Produkt-Pakete (Privat, Gewerbe, Industrie) als druckbare Infografiken.

### Zellen 1–2 — Setup & Daten
**Was passiert:** Alle relevanten Kennzahlen aus `transfer.json` und `wirtschaftlichkeit.csv` werden geladen. Drei Produktpakete werden definiert: konkrete Empfehlungen für Grösse, Leistung, erwarteter Erlös, Amortisationszeit.

### Zellen 3–8 — Steckbrief-Charts
**Was passiert:** Für jedes Produktpaket wird ein formatierter "Produktsteckbrief" als matplotlib-Figure erstellt — ähnlich wie ein technisches Datenblatt. Kein Koordinatenachsensystem, sondern freie Text- und Geometrie-Positionierung.

**Technisch:** `ax.text(x, y, text, ...)` und `ax.add_patch(Rectangle(...))` werden direkt auf dem Figure-Koordinatensystem verwendet, ohne eigentliche Plot-Daten. So kann man beliebige Layouts erstellen.

### Zelle 9 — Abschlusskontrolle
**Was passiert:** Alle Steckbrief-PNGs werden auf Existenz geprüft.

---

## NB15 — Kombinierte Simulation (`15_Kombinierte_Simulation.ipynb`)

Simuliert alle vier Dispatch-Strategien (Arbitrage, Eigenverbrauch, Hybrid statisch, Hybrid optimiert) für alle Segmente in einem einzigen Lauf und vergleicht die Ergebnisse.

### Zelle 1 — Setup
**Was passiert:** Alle Simulations-Parameter aus config.json laden. Spezifisch für NB15: lokale Alias-Variablen für die vier Dispatch-Modi werden definiert, die auf die globalen Farbvariablen zeigen.

### Zellen 2–4 — Datenladen & Simulation
**Was passiert:** Preisdaten und (falls vorhanden) Solarprofil-Daten werden geladen. Die `simulate_battery()`-Logik aus NB02 wird hier reimplementiert (keine Abhängigkeit — jedes Notebook ist für sich lauffähig), erweitert um zwei hybride Modi: Der statische Hybrid wechselt je nach Tageszeit zwischen Eigenverbrauch und Arbitrage. Der optimierte Hybrid maximiert den kombinierten Nutzen mit einem einfachen Look-Ahead-Algorithmus.

### Zellen 5–9 — Vergleichs-Charts
**Was passiert:** Für jeden der vier Modi werden Charts erstellt: Cashflow über Zeit, Lade-/Entlade-Häufigkeit, ROI-Vergleich. Ein Übersichts-Chart zeigt alle vier Modi nebeneinander.

### Zellen 10–11 — Transfer & Abschluss
**Was passiert:** Die Vergleichswerte werden in `transfer.json` unter `kombinierte_simulation` geschrieben. Abschlusskontrolle mit ✅/❌.

---

## NB99 — Datenprovenienz (`99_Datenprovenienz.ipynb`)

Dokumentiert alle verwendeten Datenquellen: Woher kommen die Daten? Wie wurden sie aufbereitet? Welche Lizenz haben sie? Das ist die wissenschaftliche Nachvollziehbarkeit des Projekts.

### Zelle 1 — Setup
**Was passiert:** Libraries laden, `dataindex.csv` lesen (das Register aller Datensätze, das NB01 und NB02 automatisch gefüllt haben).

### Zellen 2–3 — Quellen-Übersicht
**Was passiert:** Alle Einträge aus `dataindex.csv` werden nach Typ kategorisiert (Rohdaten, verarbeitete Daten, Zwischenergebnisse) und als formatierte Tabelle angezeigt.

### Zellen 4–6 — Detaildokumentation
**Was passiert:** Für jede Hauptdatenquelle wird ein ausführlicher Block ausgegeben:
- **ENTSO-E Spotpreise:** Quelle, Zeitraum, Einheit (EUR/MWh), Häufigkeit (stündlich), Lizenz, Verarbeitungsschritte
- **ENTSO-E Netzlast:** analog
- **swisstopo Geodaten:** Koordinatensystem, Lizenz (Open Government Data)
- **BFE Anlagenregister:** Beschreibung, Attribute, Lizenz
- **NREL ATB:** Quelle, Jahr, Einheiten

### Zellen 7–8 — Reproduzierbarkeits-Statement & Gesamtübersicht
**Was passiert:** Ein formales Statement wird ausgegeben: "Alle Daten können mit denselben API-Keys und NB01 neu geladen werden. Die Analyse ist vollständig reproduzierbar." Eine abschliessende Visualisierung zeigt den Datenfluss: Welche Rohdaten fliessen in welche Notebooks?
