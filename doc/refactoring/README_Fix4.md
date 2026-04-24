# Fix — K_01 Regression nach Phase 7 (NameError: draw_base_map)

## Was ist passiert

Bei `run_all.bat` mit Modus=all ist K_01 fehlgeschlagen mit:

```
NameError: name 'draw_base_map' is not defined
```

Im Cell der 5.2-Karte, beim Aufruf `draw_base_map(ax, alpha=0.15, ...)`.

## Root Cause

Mein Phase-7-v2b-Patch hat in K_01 Cell 49 (Original) **zu viel ersetzt**.
Der Regex-Ende-Marker `# ── 5\.[1-9]` griff nicht, weil die Zelle keine
5.1-Unterteilung enthielt — **alles von Zeile 1 bis Zell-Ende** wurde als
"Kantone-Block" behandelt und durch den kurzen lib-Aufruf ersetzt.

Dabei verloren gingen **4 Code-Blöcke**:

1. **gdf_kant Post-Processing** (Zeilen 112-124):
   ```python
   gdf_kant['Zone']     = gdf_kant['KAB'].map(KANTON_TO_ZONE)
   gdf_kant['Pop']      = gdf_kant['KAB'].map(KANTON_POP)
   gdf_kant['ZColor']   = gdf_kant['Zone'].map(ZONE_COLORS)
   gdf_kant['Area_km2'] = gdf_area.geometry.area / 1e6
   gdf_kant['Dichte']   = ...
   ```

2. **`def draw_base_map`** (Zeilen 126-139) — Haupt-Karten-Zeichenfunktion,
   wird in mindestens 3 späteren Zellen benutzt (5.2-Karte, 5.3-Karte,
   weitere).

3. **`KANTONSHAUPTORTE`-Dict** (Zeilen 141-149) — Koordinaten für 26 Kantone.

4. **`ENGPASSLINIEN`-Liste** (Zeilen 150-154) — Engpass-Linien für die Karte.

## Der Fix

Alle 4 Blöcke wurden aus `verified_3a/kuer/K_01_Raeumliche_Analyse.ipynb`
Cell 49 extrahiert und **ans Ende der gepatchten Cell 54 angefügt**. Die
Phase-7-Lib-Migration (`load_kantone(...)`-Aufruf) bleibt unverändert.

Kleine Adaption nötig:
- Die alte `if gdf_kant is not None and KANTON_ABB_COL:`-Bedingung wurde
  vereinfacht zu `if gdf_kant is not None:`, weil `lib.grid_topo.load_kantone`
  immer die `KAB`-Spalte liefert (oder `None` zurückgibt)
- Die alte `if KANTON_ABB_COL != 'KAB':`-Normalisierung wurde entfernt
  (redundant, lib setzt direkt `KAB`)
- `kuerzel_set = set(KANTON_TO_ZONE.keys())` am Blockanfang ergänzt
  (war im Original in der Lade-Logik, die jetzt weg ist)

## Qualitäts-Checks (alle ✅)

| Check | Status |
|---|---|
| `def draw_base_map` wieder vorhanden | ✅ |
| `KANTONSHAUPTORTE`-Dict wieder vorhanden | ✅ |
| `ENGPASSLINIEN`-Liste wieder vorhanden | ✅ |
| `load_kantone`-Aufruf erhalten (Phase-7-Migration) | ✅ |
| `from lib.grid_topo import load_kantone` erhalten | ✅ |
| `gdf_kant['Zone']` Post-Processing wieder vorhanden | ✅ |
| `gdf_kant['Dichte']` Post-Processing wieder vorhanden | ✅ |
| AST-Validierung aller Code-Zellen | ✅ (0 Fehler) |

## Installation

```bash
cp <ZIP>/K_01_Raeumliche_Analyse.ipynb kuer/
```

Nach Installation: `run_all.bat` nochmal laufen lassen — K_01 sollte
durchlaufen.

## Lektion (erneut)

Dritter Fall in Folge wo meine Regex-basierten Patches **zu gross zugeschlagen**
haben:
1. log_dataindex-Nachzug (Scope zu eng)
2. grid_topo-Analyse (Pattern zu eng)
3. grid_topo-Migration in K_01 (Ende-Marker nicht robust)

**Lessons updated für Phase 8:**

> **Ende-Marker bei Regex-Ersetzungen müssen robust sein.** Wenn der
> Ende-Marker (`(?=def |# ──-Section)`) in manchen Zellen nicht existiert,
> greift die Ersetzung bis zum Zell-Ende und verschluckt wichtigen Code.
> Besser: AST-Analyse der Zelle statt String-Pattern, oder explizite
> Line-Counts nutzen, oder **nach der Ersetzung einen automatischen Test**:
> hat die neue Zelle noch alle ursprünglich-definierten Namen im Scope?

Der run_all-Test hat das sofort gezeigt — das ist ein starkes Argument
dafür, Phase 9 (Regressionstest) **nicht erst nach Phase 8 zu machen**,
sondern nach jedem grösseren Migrations-Schritt den `run_all` einmal
auszuführen. Alternativ: einen reduzierten `run_all_quick`, der nur
`nbconvert --execute` über alle NBs läuft ohne komplette Re-Generation.

## Plan-Update

Im `Refactoring_Plan.md` wird dies unter Phase 7 als "Regression-Fix nach
Run-All-Test" nachgetragen; Phase 8 (Doku-Update) und Phase 9 (run_all)
rücken entsprechend.
