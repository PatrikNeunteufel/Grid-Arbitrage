"""SC26_Gruppe_2 — Gemeinsame Funktionsbibliothek.

Dieses Package bündelt projektweite Helferfunktionen, damit Notebooks sie per
``from lib.<modul> import <n>`` importieren können statt sie zu duplizieren.

Verzeichnisstruktur siehe O_01 §6 und O_03 §5 (lib/-Nutzung).

Standard-Importblock in Notebooks:

    import sys
    from pathlib import Path
    _lib_root = Path('..').resolve()
    if str(_lib_root) not in sys.path:
        sys.path.insert(0, str(_lib_root))

    from lib.io_ops import log_dataindex, needs_download
    from lib.plotting import show_source, should_skip

    %load_ext autoreload
    %autoreload 2

Für die Darstellung eines Funktions-Quellcodes im Notebook (Prüfungs-
transparenz) siehe ``lib.plotting.show_source``.

Dieses Modul exportiert zusätzlich ``ensure_installed()`` — einen Meta-Helper,
der fehlende pip-Pakete nachinstalliert. Wird vom Installer-Notebook
``organisation/O_00_Installer.ipynb`` und von einzelnen Notebooks genutzt.
"""

__version__ = "0.1.0"


def ensure_installed(packages, verbose=True, quiet_install=True):
    """Prüft pip-Pakete und installiert fehlende nach.

    Ersetzt das bisherige ``try: __import__(...) except ImportError:
    subprocess.check_call(...)``-Muster, das in den meisten Notebooks vor dem
    eigentlichen Import-Block dupliziert ist.

    Parameter
    ---------
    packages : list
        Liste von Paket-Spezifikationen. Jedes Element ist entweder:

        * ``str`` — der Name wird sowohl für ``pip install`` als auch für
          ``importlib.import_module`` verwendet (z.B. ``'numpy'``).
        * ``tuple[str, str]`` — ``(pip_name, import_name)``. Nötig wenn diese
          sich unterscheiden, z.B. ``('Pillow', 'PIL')`` oder
          ``('entsoe-py', 'entsoe')``.
    verbose : bool, default True
        Ob jeder Check einen Status-Print erzeugt.
    quiet_install : bool, default True
        Ob pip mit ``-q`` aufgerufen wird (unterdrückt Progress-Output).

    Rückgabe
    --------
    dict
        ``{'installed': [...], 'already': [...], 'failed': [...]}``

    Beispiel
    --------
    >>> from lib import ensure_installed
    >>> ensure_installed([
    ...     'numpy',
    ...     'pandas',
    ...     ('Pillow', 'PIL'),
    ...     ('entsoe-py', 'entsoe'),
    ... ])
    """
    import importlib
    import subprocess
    import sys

    result = {'installed': [], 'already': [], 'failed': []}

    for pkg in packages:
        if isinstance(pkg, str):
            pip_name = import_name = pkg
        elif isinstance(pkg, (tuple, list)) and len(pkg) == 2:
            pip_name, import_name = pkg
        else:
            if verbose:
                print(f"  ⚠️ Ungültige Paket-Spezifikation: {pkg!r} — übersprungen")
            result['failed'].append(str(pkg))
            continue

        try:
            importlib.import_module(import_name)
            result['already'].append(import_name)
            if verbose:
                print(f"  ✓ {import_name:20s} bereits installiert")
        except ImportError:
            if verbose:
                print(f"  → {pip_name:20s} wird installiert …")
            cmd = [sys.executable, '-m', 'pip', 'install', pip_name]
            if quiet_install:
                cmd.append('-q')
            try:
                subprocess.check_call(cmd)
                result['installed'].append(pip_name)
                if verbose:
                    print(f"  ✅ {pip_name:20s} installiert")
            except subprocess.CalledProcessError as e:
                result['failed'].append(pip_name)
                if verbose:
                    print(f"  ❌ {pip_name:20s} Installation fehlgeschlagen: {e}")

    if verbose:
        n_new = len(result['installed'])
        n_ok = len(result['already'])
        n_bad = len(result['failed'])
        print(f"\nErgebnis: {n_ok} bereits da, {n_new} neu installiert, {n_bad} Fehler")

    return result
