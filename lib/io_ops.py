"""lib.io_ops — I/O- und Daten-Provenienz-Helfer.

Eine Funktion:

* ``log_dataindex`` — append-only Daten-Provenienz-Logger (schreibt nach
  ``sync/dataindex.csv``, markiert vorherige Einträge desselben Dateinamens
  als ``superseded``).

Das Datenprotokoll ermöglicht nachträgliches Nachvollziehen:
  * welche Rohdaten wann geladen wurden
  * welche verarbeiteten Dateien aus welchen Quellen abgeleitet sind
  * wann alte Versionen durch neue ersetzt wurden
"""
from __future__ import annotations

import os
from datetime import datetime


DATAINDEX_COLUMNS = [
    'timestamp', 'filename', 'source_url', 'local_path', 'data_type',
    'rows', 'size_kb', 'status', 'superseded_at', 'note',
]


def log_dataindex(filename, source_url, local_path, data_type,
                  rows=None, size_kb=None, status='active', note='',
                  dataindex_path=None):
    """Schreibt einen Eintrag ins Daten-Provenienz-Protokoll.

    Existiert bereits ein aktiver Eintrag mit demselben ``filename``, wird
    dieser als ``superseded`` markiert (mit Zeitstempel in ``superseded_at``).

    Parameter
    ---------
    filename : str
        Dateiname (ohne Pfad).
    source_url : str
        Quelle (URL, Bibliotheksname, o.Ä.).
    local_path : str
        Relativer lokaler Pfad der Datei.
    data_type : {'raw','intermediate','processed','output'}
        Art der Datei in der Pipeline.
    rows : int, optional
        Anzahl Zeilen (für tabellarische Daten).
    size_kb : float, optional
        Grösse in Kilobyte (wird auf 1 Nachkommastelle gerundet).
    status : {'active','superseded','deleted'}, default 'active'
        Status des Eintrags.
    note : str, default ''
        Freitext-Kommentar.
    dataindex_path : str, optional
        Pfad zur ``dataindex.csv``. Wenn ``None``, wird im NB-Scope die
        globale Variable ``DATAINDEX`` gesucht (Rückwärtskompatibilität);
        Fallback ``"../sync/dataindex.csv"``.

    Return
    ------
    None. Schreibt nach ``dataindex.csv``.
    """
    import pandas as pd

    # dataindex_path auflösen
    if dataindex_path is None:
        # Versuche globale Variable DATAINDEX aus dem aufrufenden Scope
        import inspect
        caller_globals = inspect.stack()[1].frame.f_globals
        dataindex_path = caller_globals.get('DATAINDEX', '../sync/dataindex.csv')

    ts = datetime.utcnow().isoformat(timespec='seconds') + 'Z'

    if os.path.exists(dataindex_path):
        df_idx = pd.read_csv(dataindex_path)
        mask = (df_idx['filename'] == filename) & (df_idx['status'] == 'active')
        if mask.any():
            df_idx.loc[mask, 'status']         = 'superseded'
            df_idx.loc[mask, 'superseded_at']  = ts
    else:
        df_idx = pd.DataFrame(columns=DATAINDEX_COLUMNS)

    row = {
        'timestamp':      ts,
        'filename':       filename,
        'source_url':     source_url,
        'local_path':     local_path,
        'data_type':      data_type,
        'rows':           rows,
        'size_kb':        round(size_kb, 1) if size_kb else None,
        'status':         status,
        'superseded_at':  '',
        'note':           note,
    }
    pd.concat(
        [df_idx, pd.DataFrame([row])],
        ignore_index=True,
    ).to_csv(dataindex_path, index=False)

    print(f'  dataindex: {filename} [{status}]')



# ═══════════════════════════════════════════════════════════════════════════════
# transfer.json — Ergebnistransfer zwischen Notebooks
# ═══════════════════════════════════════════════════════════════════════════════
#
# transfer.json ist die SSOT für berechnete Outputs, die zwischen NBs geteilt
# werden (Simulationsergebnisse, Kennzahlen). Pipeline-Überblick:
#
#   NB01 → schreibt 'datenzeitraum'
#   NB03 → schreibt 'simulation'
#   K_06 → schreibt 'dispatch_optimierung'   (und liest 'simulation')
#   K_09 → schreibt 'eigenverbrauch'
#   K_10 → schreibt 'produkt'                (liest 'hybrid_simulation', 'simulation')
#   K_99 → schreibt 'hybrid_simulation'
#
# Downstream-Leser: NB00, NB02, NB03, K_00, K_05, K_06, K_10, K_99

def load_transfer(path='../sync/transfer.json', key=None, default=None):
    """Lädt transfer.json und gibt das ganze Dict oder einen Teil zurück.

    Verhalten
    ---------
    * Datei existiert nicht oder ist leer → Rückgabe ist ``default`` (bei
      key=None: ``default`` oder ``{}``). Gibt Warnung auf stdout aus.
    * Datei existiert → gibt bei ``key=None`` das ganze Dict zurück, bei
      gegebenem ``key`` nur den entsprechenden Teilbaum (``default``, wenn
      Key fehlt).

    Parameter
    ---------
    path : str, default '../sync/transfer.json'
        Pfad zur transfer.json.
    key : str, optional
        Top-Level-Key ('datenzeitraum', 'simulation', ...). Bei None wird
        das komplette Dict zurückgegeben.
    default : any, optional
        Rückgabewert bei fehlender Datei oder fehlendem Key. Bei key=None
        ist der Default ``{}``.

    Return
    ------
    dict oder der Wert des angefragten Keys.
    """
    import json as _json

    if default is None and key is None:
        default = {}

    if not os.path.exists(path) or os.path.getsize(path) == 0:
        print(f'⚠️  {path} nicht gefunden oder leer — NB01/NB02 zuerst ausführen')
        return default

    with open(path, encoding='utf-8') as _f:
        data = _json.load(_f)

    if key is None:
        return data
    return data.get(key, default)


def save_transfer(data, path='../sync/transfer.json', key=None):
    """Schreibt Daten nach transfer.json — mit Merge-Logik.

    Verhalten
    ---------
    * Wenn ``path`` existiert und nicht leer ist, wird das bestehende Dict
      geladen und mit den neuen Daten gemerged (bestehende andere Keys
      bleiben erhalten — wichtig für die Pipeline!).
    * Bei ``key=None`` muss ``data`` ein Dict sein und wird in die oberste
      Ebene gemerged (``existing.update(data)``).
    * Bei gegebenem ``key`` wird ``data`` unter diesem Top-Level-Key
      abgelegt (``existing[key] = data``).

    Parameter
    ---------
    data : dict oder any
        Zu schreibende Daten.
    path : str, default '../sync/transfer.json'
        Zieldatei.
    key : str, optional
        Top-Level-Key. Bei None muss ``data`` ein Dict sein.

    Return
    ------
    Das komplette Dict nach dem Write (nützlich für Chaining / Verifikation).
    """
    import json as _json

    # Bestehendes laden (wenn vorhanden)
    existing = {}
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, encoding='utf-8') as _f:
            existing = _json.load(_f)

    # Mergen
    if key is None:
        if not isinstance(data, dict):
            raise TypeError(
                f"Bei key=None muss data ein dict sein, bekam {type(data).__name__}"
            )
        existing.update(data)
    else:
        existing[key] = data

    # Schreiben
    with open(path, 'w', encoding='utf-8') as _f:
        _json.dump(existing, _f, indent=2, ensure_ascii=False)

    return existing



# ═══════════════════════════════════════════════════════════════════════════════
# File-Gate-Helfer (ersetzt lokale Duplikate in NB01/NB02/NB03/K_01/K_02)
# ═══════════════════════════════════════════════════════════════════════════════

def needs_download(path, min_kb, key, force_reload=None):
    """True wenn Datei fehlt, zu klein ist, oder force_reload[key] gesetzt.

    Typische Nutzung: vor externem Download entscheiden, ob Cache valide ist.

    Parameter
    ---------
    path : str
        Pfad zur Cache-Datei.
    min_kb : float
        Minimale erwartete Dateigrösse in KB.
    key : str
        Key für den force_reload-Dict (z.B. 'prices', 'netzlast').
    force_reload : dict, optional
        Dict mit ``{key: bool}``. Wenn ``None``, wird im Caller-Scope die
        globale Variable ``FORCE_RELOAD`` gesucht (aus config.json).

    Return
    ------
    bool
        True → Download nötig; False → Cache-Datei ist gut genug.
    """
    if force_reload is None:
        import inspect
        caller_globals = inspect.stack()[1].frame.f_globals
        force_reload = caller_globals.get('FORCE_RELOAD', {})

    if force_reload.get(key, False):
        print(f'  FORCE_RELOAD={key} → neu laden')
        return True
    if not os.path.exists(path):
        return True
    if os.path.getsize(path) < min_kb * 1024:
        return True
    return False


def needs_rebuild(filepath, min_rows, ds_key, force_reload=None):
    """True wenn Datei fehlt, zu wenige Zeilen, oder force_reload gesetzt.

    Pendant zu needs_download, aber zeilen-basiert — für Intermediate-CSV-
    Dateien, wo die Byte-Grösse wenig aussagt.

    Parameter
    ---------
    filepath : str
        Pfad zur zu prüfenden Datei.
    min_rows : int
        Minimale erwartete Anzahl Datenzeilen (Header zählt nicht).
    ds_key : str
        Key für den force_reload-Dict.
    force_reload : dict, optional
        Wie in needs_download — Fallback auf ``FORCE_RELOAD`` im Caller-Scope.

    Return
    ------
    bool
        True → muss neu erzeugt werden.
    """
    if force_reload is None:
        import inspect
        caller_globals = inspect.stack()[1].frame.f_globals
        force_reload = caller_globals.get('FORCE_RELOAD', {})

    if force_reload.get(ds_key, False):
        print(f'  FORCE_RELOAD={ds_key} → neu erzeugen')
        return True
    if not os.path.exists(filepath):
        return True
    try:
        n = sum(1 for _ in open(filepath)) - 1
        if n < min_rows:
            print(f'  Zu wenig Zeilen ({n} < {min_rows}) → neu erzeugen')
            return True
    except Exception:
        return True
    return False


def log_missing(source, reason, data_folder='../data', dataindex_path=None):
    """Protokolliert fehlende/fehlerhafte externe Datenquelle.

    Schreibt zwei Einträge:
      1. ``<data_folder>/missing.txt`` (Klartext-Log, append)
      2. ``dataindex.csv``-Eintrag mit ``status='error'`` via :func:`log_dataindex`

    Parameter
    ---------
    source : str
        URL oder Bezeichner der fehlenden Quelle.
    reason : str
        Beschreibung des Fehlers (z.B. "HTTP 404", "Timeout").
    data_folder : str, default '../data'
        Ordner für missing.txt.
    dataindex_path : str, optional
        Pfad zum dataindex.csv (Fallback über log_dataindex).
    """
    from datetime import datetime
    ts = datetime.utcnow().isoformat(timespec='seconds')
    os.makedirs(data_folder, exist_ok=True)
    with open(os.path.join(data_folder, 'missing.txt'), 'a') as f:
        f.write(f'[{ts}] MISSING {source}: {reason}\n')
    log_dataindex(os.path.basename(source), source, '', 'raw',
                  status='error', note=reason,
                  dataindex_path=dataindex_path)
    print(f'  missing.txt: {reason}')
