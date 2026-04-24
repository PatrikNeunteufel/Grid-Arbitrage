# Phase 8 — Schritt 3a: Notebook_Dokumentation.md Library-Kapitel

## Was geändert wurde

**Neues Kapitel "Library-Module (`lib/`)"** vor dem bestehenden Kapitel
"Organisation" eingefügt. Alles andere **unverändert** (NB-Kapitel-Inhalt
bleibt gleich — deren Inline-Verweise auf die lib-Anker kommen in Schritt 3b).

## Struktur des neuen Kapitels

**Einleitung:**
- Übersichtstabelle aller 9 Module mit Anker-Links
- Bootstrap-Import-Muster als Code-Block
- Erklärung der `show_source`-Konvention

**Pro Modul:**
- Kurze Zweck-Beschreibung
- Funktions-Sektionen als H3 mit eigenem Anker

**Pro Funktion (4-Block-Schema):**
1. **Signatur** als Code-Block direkt nach dem H3-Header
2. **Was sie tut** — was der Code macht, in 2-4 Sätzen
3. **Warum extrahiert** — Refactoring-Motivation (welches Duplikat,
   welches Phase-README dokumentiert es)
4. **Aufgerufen von** — Liste der NBs die die Funktion nutzen
5. **Verwendete Bibliotheksobjekte (Erstnennung innerhalb lib)** — Tabelle
   mit pandas/numpy/etc-Funktionen die im lib-Modul zum ersten Mal auftreten

## Inhalt

9 Module, 19 öffentliche Funktionen + 2 Konstanten:

| Modul | Funktionen |
|---|---|
| `lib` (`__init__.py`) | `ensure_installed` |
| `lib.plotting` | `show_source`, `should_skip`, `make_gif_chart`, `show_chart` |
| `lib.widgets` | `slide_or_play`, `show_animation` |
| `lib.io_ops` | `log_dataindex`, `load_transfer`, `save_transfer`, `needs_download`, `needs_rebuild`, `log_missing` |
| `lib.data_fetchers` | `fetch_entsoe_yearly` |
| `lib.simulation` | `simulate_battery_dispatch` |
| `lib.columns` | `find_col` |
| `lib.grid_topo` | `load_kantone` + Konstanten `KANT_NUM_TO_ABK`, `KANT_ABK_SET` |
| `lib.map_animation` | `make_gif_fast_map`, `clear_background_cache` |

## Anker-Konvention (für Schritt 3b)

Jede Funktion hat einen stabilen Anker im Schema `#lib-<modul>-<funktion>`:

- `#lib-io-ops-log-dataindex`
- `#lib-plotting-show-chart`
- `#lib-simulation-simulate-battery-dispatch`
- usw.

In Schritt 3b werden die Inline-Verweise in den NB-Kapiteln nach diesem
Schema gebaut: `[log_dataindex()](#lib-io-ops-log-dataindex)`.

## Verwendung der intern genutzten pandas/numpy-Funktionen

Nach Vereinbarung **Option 1B** — pandas/numpy/etc-Funktionen die von
lib-Funktionen intern genutzt werden (z.B. `pd.concat` in `log_dataindex`,
`np.empty` in `simulate_battery_dispatch`) werden **in den lib-Tabellen**
erklärt, nicht in den NB-Kapiteln.

Wenn ein NB dieselbe Funktion später direkt benutzt (z.B. `pd.concat` in
einer eigenen Zelle), kann es die Erklärung aus dem lib-Kapitel einfach
verlinken statt neu zu beschreiben.

## Was bleibt für Schritt 3b

Die NB-Kapitel enthalten noch Beschreibungen wie:

> **Zelle 3 — Datenregister-Hilfsfunktionen**
> Zwei Funktionen werden definiert. `log_dataindex()` schreibt jeden
> geladenen Datensatz in ...

Diese werden in Schritt 3b umgeschrieben zu:

> **Zelle 3 — Datenregister-Aufruf**
> Ruft [`log_dataindex`](#lib-io-ops-log-dataindex) aus `lib.io_ops` auf.
> Die Funktion schreibt ...

Die Tabellen mit "Verwendete Bibliotheksobjekte (Erstnennung)" werden
dabei ausgedünnt — was schon im lib-Kapitel steht, muss nicht wiederholt
werden.

## Qualitäts-Checks (alle ✅)

```
LIB-Kapitel-Header vorhanden                   ✅
Alle 9 Modul-Anker                             ✅
Funktions-Anker aller wichtigsten Fns (19)     ✅
Kapitel kommt vor Organisation-Kapitel         ✅
Baseline-Inhalt unverändert (NB01-Kapitel da)  ✅
Importmuster im Überblick                      ✅
Alle Funktionen haben "Aufgerufen von"         ✅
```

Grösse: 740 → 1274 Zeilen (+72%, ein neues Kapitel von ~36 KB).

## Installation

```bash
cp <ZIP>/Notebook_Dokumentation.md .
```

Nach Review → Schritt 3b (Inline-Verweise in NB-Kapiteln).
