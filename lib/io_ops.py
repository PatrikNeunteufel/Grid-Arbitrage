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


# ═══════════════════════════════════════════════════════════════════════════════
# Notebook-Abschluss-Helfer — final_check + pipeline_overview
# ═══════════════════════════════════════════════════════════════════════════════
#
# Standardisierte End-of-Notebook-Kontrollen. Ersetzen die manuell duplizierten
# Abschluss-Code-Blöcke in NB00-NB04 und sind für Kür-NBs wiederverwendbar.
#
#   final_check       — Output-Validierung pro NB (Existenz + Mindestgrösse)
#   pipeline_overview — Mehr-Sektionen-Übersicht mit dir_listing-Modus (NB00)


def _format_size(size_bytes):
    """Formatiert Dateigrösse in KB oder MB (Schwelle 1024 KB)."""
    kb = size_bytes / 1024
    if kb < 1024:
        return f'{kb:>7.1f} KB'
    return f'{kb / 1024:>7.1f} MB'


def final_check(nb_label, files=None, *, weiter_msg=None, fehler_msg=None,
                extras=None, show_dataindex=False,
                dataindex_path='../sync/dataindex.csv', width=60):
    """Standardisierte End-of-Notebook-Kontrolle für Pflicht- und Kür-NBs.

    Prüft Existenz und Mindestgrösse der angegebenen Output-Dateien,
    gibt formatiertes Resultat aus und liefert ``all_ok`` als Bool zurück.

    Parameter
    ---------
    nb_label : str
        Label des Notebooks im Output-Header, z.B. ``"NB01"``, ``"K_03"``.
    files : list of tuple, optional
        Zu prüfende Dateien als ``(path, label, min_bytes)``-Tuples.

        * ``min_bytes = 0`` → nur Existenz prüfen, Grösse nicht ausgeben
          (z.B. für PNG-Charts).
        * ``min_bytes > 0`` → zusätzlich Grösse prüfen und in KB/MB ausgeben
          (z.B. für CSV-Dateien).

        Bei ``files=None`` oder ``files=[]`` wird kein Check ausgeführt;
        die Funktion dient dann als reiner Status-Print (für Report-NBs
        ohne eigene Outputs wie K_00).
    weiter_msg : str, optional
        Nachricht für den Erfolgsfall, z.B. ``"NB02 Daten Bereinigung"``.
        Default: ``"nächstes Notebook"``.
    fehler_msg : str, optional
        Nachricht für den Fehlerfall (Kurzform, ohne "Fehler beheben vor").
        Default: identisch mit ``weiter_msg``.
    extras : list of str, optional
        Zusätzliche Print-Zeilen zwischen Datei-Check und Weiter-/Fehler-Hinweis.
        Sinnvoll für Kür-Hinweise oder Kontext.
    show_dataindex : bool, default False
        Wenn True, wird der aktive Auszug aus ``../sync/dataindex.csv`` ausgegeben.
        Typisch für NB01.
    dataindex_path : str, default '../sync/dataindex.csv'
        Pfad zur dataindex.csv (für ``show_dataindex=True``).
    width : int, default 60
        Breite der Trennlinie aus ``=``-Zeichen.

    Return
    ------
    bool
        ``True`` wenn alle Files existieren und Mindestgrösse erfüllen,
        ``False`` sonst. Bei ``files=None``/leer immer ``True``.
    """
    print(f'{nb_label} – Abschlusskontrolle')
    print('=' * width)

    all_ok = True

    if files:
        for path, label, min_bytes in files:
            exists = os.path.exists(path)
            size = os.path.getsize(path) if exists else 0
            ok = exists and size >= min_bytes

            if min_bytes > 0:
                size_str = _format_size(size) if exists else '   FEHLT'
                print(f'  {"✅" if ok else "❌"}  {label:<45} {size_str}')
            else:
                print(f'  {"✅" if ok else "❌"}  {label}')

            if not ok:
                all_ok = False

    if extras:
        if files:
            print()
        for line in extras:
            print(line)

    if show_dataindex and os.path.exists(dataindex_path):
        import pandas as pd
        df_idx = pd.read_csv(dataindex_path)
        active = df_idx[df_idx['status'] == 'active']
        print(f'\ndataindex.csv: {len(df_idx)} Einträge total, {len(active)} active')
        print(active[['filename', 'data_type', 'rows', 'size_kb', 'timestamp']]
              .to_string(index=False))

    print()
    weiter = weiter_msg or 'nächstes Notebook'
    fehler = fehler_msg or weiter
    if all_ok:
        print(f'→ Weiter mit {weiter}.')
    else:
        print(f'→ Fehler beheben vor {fehler}.')

    return all_ok


def pipeline_overview(nb_label, sections, *, weiter_msg=None, width=60):
    """Mehr-Sektionen-Übersicht für Übersichts-NBs (NB00, K_00).

    Im Gegensatz zu :func:`final_check` zeigt diese Funktion mehrere benannte
    Sektionen mit eigenem Header, jede mit einer Liste von Dateien oder einer
    automatischen Verzeichnis-Auflistung.

    Parameter
    ---------
    nb_label : str
        Label des Notebooks, z.B. ``"NB00"``.
    sections : list of tuple
        Liste von ``(header, items)``-Tuples. ``items`` ist eine Liste von:

        * ``(path, label, min_bytes)`` — einzelne Datei (wie ``final_check``)
        * ``(path, label, min_bytes, 'file')`` — explizit Datei
        * ``(path, '', 0, 'dir_listing')`` — listet alle Files im Verzeichnis
          ``path`` auf (alphabetisch, mit Grösse). ``label`` wird ignoriert.

        Mischung aus mehreren Item-Typen pro Sektion ist erlaubt.
    weiter_msg : str, optional
        Nachricht für den Weiter-Hinweis am Ende.
    width : int, default 60
        Breite der Trennlinie.

    Return
    ------
    bool
        ``True`` wenn alle einzeln gelisteten Files OK sind. Bei ``dir_listing``
        wird Existenz des Verzeichnisses geprüft, der Inhalt aber nicht
        gegen Erwartungen verglichen (es wird gezeigt was da ist).
    """
    print(f'{nb_label} – Abschluss')
    print('=' * width)

    all_ok = True

    for header, items in sections:
        print(f'\n{header}:')

        for item in items:
            if len(item) == 4:
                path, label, min_bytes, kind = item
            else:
                path, label, min_bytes = item
                kind = 'file'

            if kind == 'dir_listing':
                if os.path.exists(path):
                    files_in_dir = sorted(f for f in os.listdir(path)
                                          if os.path.isfile(os.path.join(path, f)))
                    if not files_in_dir:
                        print(f'  ⚠️   (Verzeichnis ist leer)')
                    for f in files_in_dir:
                        fpath = os.path.join(path, f)
                        size_str = _format_size(os.path.getsize(fpath))
                        print(f'  ✅  {f:<45} {size_str}')
                    print(f'  {len(files_in_dir)} Datei(en) vorhanden')
                else:
                    print(f'  ❌  Verzeichnis nicht vorhanden: {path}')
                    all_ok = False

            else:  # kind == 'file'
                exists = os.path.exists(path)
                size = os.path.getsize(path) if exists else 0
                ok = exists and size >= min_bytes

                if min_bytes > 0:
                    size_str = _format_size(size) if exists else '   FEHLT'
                    print(f'  {"✅" if ok else "❌"}  {label:<45} {size_str}')
                else:
                    print(f'  {"✅" if ok else "❌"}  {label}')

                if not ok:
                    all_ok = False

    if weiter_msg:
        print(f'\n→ Weiter mit {weiter_msg}.')

    return all_ok
