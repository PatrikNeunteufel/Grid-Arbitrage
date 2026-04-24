# Phase 6.2b — transfer.json-Helper in lib/io_ops.py

## Selbstkorrektur

In Phase 6.2 hatte ich geschrieben "transfer.json wird aktuell gar nicht
genutzt" — das war schlicht falsch. Ich hatte im Phase-4d-Output-Verzeichnis
gesucht, das nur 3 NBs enthält (K_01, K_04, K_01c, K_01d). Im vollen Projekt
(`verified_3a`) nutzen **14 NBs** transfer.json intensiv.

Richtiges Bild nach gründlicher Inspektion:

**Schreiber (6 NBs — schreiben je 1 Top-Level-Key):**

| NB | geschriebener Key |
|---|---|
| `notebooks/01_Daten_Laden` | `datenzeitraum` |
| `notebooks/03_Daten_Analyse` | `simulation` |
| `kuer/K_06_Dispatch_Optimierung` | `dispatch_optimierung` |
| `kuer/K_09_Eigenverbrauch` | `eigenverbrauch` |
| `kuer/K_10_Produkt_Steckbrief` | `produkt` |
| `kuer/K_99_Kombinierte_Simulation` | `hybrid_simulation` |

**Leser (8 NBs):** NB00, NB02, NB03, K_00, K_05, K_06, K_10, K_99

**Boilerplate-Duplikation:** 10 LOAD-Zellen + 5 LOAD+SAVE-Zellen mit fast
identischem Muster:

```python
_tf_path = '../sync/transfer.json'
if os.path.exists(_tf_path) and os.path.getsize(_tf_path) > 0:
    TF = json.load(open(_tf_path))
    # ... aliasen ...
else:
    TF = {}; TF_N_YEARS = None; ...
    print('⚠️  ../sync/transfer.json nicht gefunden — NB01/NB02 zuerst ausführen')
```

bzw. für Schreiber:

```python
_tf = json.loads(open(_tf_path).read() or '{}') if os.path.exists(_tf_path) and os.path.getsize(_tf_path) > 0 else {}
_tf['key'] = ...
with open(_tf_path, 'w') as _f: json.dump(_tf, _f, indent=2, ensure_ascii=False)
```

## Was Phase 6.2b liefert (Teil 1 von 2)

**`lib/io_ops.py` um 2 Helper-Funktionen erweitert:**

### `load_transfer(path='../sync/transfer.json', key=None, default=None)`

```python
# Komplettes Dict laden
TF = load_transfer()

# Nur ein Teilbaum
dt = load_transfer(key='datenzeitraum')

# Mit Default bei fehlendem Key
econ = load_transfer(key='wirtschaftlichkeit', default={})
```

- Fehlende/leere Datei → gibt `default` zurück + Warnung
- `key=None` → komplettes Dict (Default `{}`)
- `key='foo'` → `dict.get('foo', default)`

### `save_transfer(data, path='../sync/transfer.json', key=None)`

Mit **Merge-Semantik** — das ist der kritische Teil der Pipeline:

```python
# Einen Top-Level-Key schreiben — andere Keys bleiben erhalten
save_transfer({'roi_pct': 1.75, ...}, key='dispatch_optimierung')

# Mehrere Keys auf einmal
save_transfer({'a': 1, 'b': 2})   # mergt in oberste Ebene
```

- **Nie** wird die Datei überschrieben ohne Read-Merge — so können parallele
  Schreiber (NB01 schreibt `datenzeitraum`, K_06 schreibt `dispatch_optimierung`)
  nicht gegenseitig ihre Daten verlieren
- Gibt das komplette Dict nach dem Write zurück (nützlich für Verifikation)
- `key=None` + non-dict → TypeError

## Was Phase 6.2b NICHT macht

**Die 15 Transfer-Zellen in den 14 NBs werden (noch) nicht umgestellt.** Das
ist Phase 6.2c, ein separater Patch. Gründe für den Split:

1. **Risiko-Minimierung:** Helper erst validieren (`run_all` mit Helpers
   parallel zu bestehender Boilerplate), dann erst migrieren
2. **Reviewbarkeit:** 14 NBs in einem Patch wären unübersichtlich
3. **Alias-Komplexität:** viele NBs haben Aliases wie `TF_N_YEARS = _dt.get(...)`
   die NB-lokal bleiben — das Helper-Pattern ersetzt nur die Boilerplate-Zeilen,
   nicht die Aliase

## Typische Migration (kommt in Phase 6.2c)

**Vorher (z.B. in K_00 Cell 9):**
```python
import json
_tf_path = '../sync/transfer.json'
if os.path.exists(_tf_path) and os.path.getsize(_tf_path) > 0:
    TF = json.load(open(_tf_path))
    _dt = TF.get('datenzeitraum', {}); _sim = TF.get('simulation', {})
    TF_N_YEARS = _dt.get('n_years', None)
    TF_SPREAD  = _sim.get('spread_mean_eur_mwh', None)
    # ... mehr Aliases ...
    print(f"../sync/transfer.json: {TF_START} – {TF_END} ...")
else:
    TF = {}; TF_N_YEARS = None; TF_SPREAD = None; ...
    print('⚠️  ../sync/transfer.json nicht gefunden — NB01/NB02 zuerst ausführen')
```

**Nachher:**
```python
TF = load_transfer()
_dt  = TF.get('datenzeitraum', {})
_sim = TF.get('simulation', {})
TF_N_YEARS = _dt.get('n_years', None)
TF_SPREAD  = _sim.get('spread_mean_eur_mwh', None)
# ... mehr Aliases wie vorher ...
if TF:
    print(f"../sync/transfer.json: {TF_START} – {TF_END} ...")
```

Spart ~10 Zeilen Boilerplate je NB. Die Aliases (`TF_N_YEARS = _dt.get(...)`)
bleiben NB-lokal — sie sind nicht duplikativ, jedes NB nimmt unterschiedliche
Aliase.

**Bei Schreibern:**

```python
# Vorher:
_tf_path = '../sync/transfer.json'
_tf = json.loads(open(_tf_path).read() or '{}') if os.path.exists(_tf_path) ... else {}
_tf['datenzeitraum'] = { 'start_date': ..., 'end_date': ..., 'n_years': ... }
with open(_tf_path, 'w') as _f: json.dump(_tf, _f, indent=2, ensure_ascii=False)

# Nachher:
save_transfer(
    { 'start_date': ..., 'end_date': ..., 'n_years': ... },
    key='datenzeitraum'
)
```

## Qualitäts-Checks (alle ✅)

| Check | Status |
|---|---|
| `lib/io_ops.py` syntaktisch valide | ✅ |
| Import `load_transfer, save_transfer` funktioniert | ✅ |
| 8 Funktional-Tests (load, save, Merge, Fehlerfälle) bestanden | ✅ |
| Rückwärtskompatibilität: bestehende NB-Zellen funktionieren weiter | ✅ (keine NB-Änderung) |

## Installation

```bash
cp <ZIP>/lib/io_ops.py lib/
```

Damit ist die Infrastruktur da — die NBs funktionieren wie bisher, nutzen
aber die Helper noch nicht.

## Nächster Schritt

**Phase 6.2c** — die 14 NBs auf `load_transfer` / `save_transfer` umstellen.
Reihenfolge der Migration nach Risiko:

1. **Schreiber-NBs zuerst** (nur 6 Zellen, exakte Schreibmuster)
2. **Reine Leser-NBs danach** (10 Zellen, mehr Variation in Aliases)

Sag Bescheid wenn die Helper gut aussehen, dann mache ich 6.2c.
