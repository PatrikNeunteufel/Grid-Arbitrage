# Phase 3b — Fix: Abschluss-Code-Zellen nachgereicht

## Was war das Problem

Bei K_07, K_08, K_09, K_10 hatte ich in Phase 3b nur den **Markdown-Header**
`## Abschluss` neu angelegt, die zugehörige **Code-Zelle** mit Datei-Check fehlte.
Damit sahen die Abschluss-Sektionen dieser NBs "leer" aus — anders als bei
K_00, K_01, K_02, K_03, K_04, K_05, K_06, K_99, wo Abschlüsse bereits
ursprünglich mit Code existierten.

## Was wurde gemacht

In allen 4 NBs wurde direkt nach dem `## Abschluss`-MD-Header eine Code-Zelle
eingefügt, analog zum bestehenden Muster in K_03 / K_05 / K_06:

```python
# ── Abschlusskontrolle K_XX ─────────────────────────────────────────────────
print('K_XX – Abschlusskontrolle')
print('=' * 60)
_charts=[f for f in os.listdir(CHARTS_DIR) if f.startswith('kuer_kXX_')] if os.path.exists(CHARTS_DIR) else []
for _f in sorted(_charts): print(f'  ✅  {_f}')
print('→ Weiter mit nächstem Notebook.')
```

Mit angepasstem `kXX`-Präfix je Notebook.

## Baseline pro NB

| NB | Baseline |
|---|---|
| K_07 | Phase 3b Teil 2 Output (meine Version) |
| K_08 | **User-Upload** (enthält TOC-Anpassungen vom User) |
| K_09 | Phase 3b Teil 2 Output (meine Version) |
| K_10 | **User-Upload** (enthält TOC-Anpassungen vom User) |

**Für K_07 und K_09:** Falls du diese zwei NBs inzwischen auch schon mit
angepassten TOCs versehen hast (wie bei K_00–K_05, K_08, K_10), nutze deine
lokale Version und füge nur die Abschluss-Code-Zelle manuell ein — die Patch-
Stelle ist direkt nach `## Abschluss`, siehe den Diff.

## Installation

```bash
cd /pfad/zum/projekt
cp <diese_ZIP>/patched_notebooks/kuer/K_08_Alternative_Speicher.ipynb kuer/
cp <diese_ZIP>/patched_notebooks/kuer/K_10_Produkt_Steckbrief.ipynb kuer/

# Nur wenn du K_07/K_09 noch nicht manuell angepasst hast:
cp <diese_ZIP>/patched_notebooks/kuer/K_07_Technologievergleich.ipynb kuer/
cp <diese_ZIP>/patched_notebooks/kuer/K_09_Eigenverbrauch.ipynb kuer/
```

## Qualitäts-Checks

| Check | Status |
|---|---|
| Alle 4 NBs haben MD `## Abschluss` direkt gefolgt von Code `Abschlusskontrolle` | ✅ |
| Korrekte `kuer_kXX_`-Präfixe je NB | ✅ |
| JSON-Validität, Cell-IDs erhalten | ✅ |

## Verifikation nach Installation

Jedes der 4 NBs einmal `Kernel → Restart & Run All` durchlaufen lassen. Die
neue Abschluss-Code-Zelle greift auf `os` und `CHARTS_DIR` zurück — beide sind
aus dem Initialisierungs-Block im Scope (identisch zu K_03/K_05/K_06). Falls
Charts mit dem Präfix fehlen, wird nur nichts gelistet — kein Fehler.
