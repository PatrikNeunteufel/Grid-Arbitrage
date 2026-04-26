"""lib.plotting — Plot-Helfer, GIF-Builder, Display- und Transparenz-Helper.

Dieses Modul bündelt visualisierungsbezogene Utility-Funktionen. In Phase 1
sind bereits zwei Funktionen verfügbar, die von allen Notebooks gebraucht
werden:

* ``show_source``  — zeigt Quellcode einer Funktion aufklappbar im Notebook
* ``should_skip``  — entscheidet ob ein Chart/GIF neu erzeugt werden soll

Die übrigen Plot-Helper (make_gif_chart, make_spline_h24, draw_base_map,
show_chart, highlight etc.) werden in Phase 6 aus den Notebooks hierher
verschoben.

Quelle der in späteren Phasen zu migrierenden Funktionen:

* ``make_spline_w4``   — kuer/K_04_Animationen.ipynb, Cell 8
* ``draw_base_map``    — kuer/K_01_Raeumliche_Analyse.ipynb, Cell 48
                         (lokale Variante in K_01c, Cell 17)
* ``show``, ``show_anim``, ``nb_aktiv``,
  ``check_aktiv``      — kuer/K_00_Business_Strategy.ipynb, Cell 8
* ``highlight``        — organisation/O_01_Project_Overview.ipynb, Cell 13
* ``fmt_size``, ``_nd`` — organisation/O_99_Datenprovenienz.ipynb

Bereits migriert: ``show_source``, ``should_skip``, ``make_gif_chart``,
``show_chart``, ``make_spline_h24``.

Siehe Refactoring_Plan.md §4.1 und §6.
"""

from __future__ import annotations

import os
from typing import Any, Callable


# ═══════════════════════════════════════════════════════════════════════════════
# show_source — aufklappbare Quellcode-Anzeige für Notebook-Transparenz
# ═══════════════════════════════════════════════════════════════════════════════

def show_source(
    func: Callable,
    title: str | None = None,
    collapsed: bool = True,
    mode: str = "markdown",
    style: str = "default",
) -> None:
    """Zeigt den Quellcode einer Funktion im Notebook — theme-passend oder als HTML.

    Wird in Notebooks unmittelbar nach ``from lib... import`` verwendet, damit
    Dozenten/Reviewer den Code direkt inline sehen ohne die ``.py`` öffnen zu
    müssen. Der Quellcode wird zur Render-Zeit via ``inspect.getsource`` geholt
    — bei jedem Re-Run der Zelle wird die *aktuelle* lib-Version gezeigt.

    Zwei Rendering-Modi:

    * ``mode='markdown'`` (Default): Nutzt ``IPython.display.Markdown``.
      JupyterLab rendert den Codeblock mit seinem **eigenen** Syntax-
      Highlighting, das zum aktiven Theme (hell/dunkel) passt. Kein
      Kontrastproblem. Klappbar via ``<details>`` (funktioniert in
      JupyterLab 4+).

    * ``mode='html'``: Nutzt ``IPython.display.HTML`` mit pygments-Rendering.
      Fester Style (``style``-Parameter), unabhängig vom Notebook-Theme.
      Nützlich wenn Markdown-Rendering nicht zuverlässig ist (z.B. nbviewer
      in älteren Versionen, Export als HTML-Report).

    Parameter
    ---------
    func : Callable
        Die Funktion (oder Klasse), deren Quellcode angezeigt werden soll.
    title : str, optional
        Überschreibt den automatisch generierten Titel
        ``Quellcode: <n> (aus <modul>.py)``.
    collapsed : bool, default True
        Ob die Anzeige initial zugeklappt (``<details>``) oder offen sein soll.
    mode : {'markdown', 'html'}, default 'markdown'
        Rendering-Modus.
    style : str, default 'default'
        Nur wirksam bei ``mode='html'``. Pygments-Style-Name. Empfehlungen:

        * ``'default'``  — hell, guter Kontrast (weisser HG)
        * ``'friendly'`` — hell, freundlich
        * ``'tango'``    — hell, kräftige Farben
        * ``'monokai'``  — dunkel, hoher Kontrast
        * ``'github-dark'`` — dunkel, GitHub-Stil (weniger Kontrast bei Kommentaren)
        * ``'one-dark'`` — dunkel, VS-Code-Stil

        Liste aller verfügbaren:
        ``from pygments.styles import get_all_styles; list(get_all_styles())``

    Beispiele
    --------
    >>> from lib.simulation import simulate_battery
    >>> from lib.plotting import show_source
    >>> show_source(simulate_battery)                         # Markdown, theme-passend
    >>> show_source(simulate_battery, collapsed=False)        # offen
    >>> show_source(simulate_battery, mode='html', style='monokai')  # HTML pygments
    """
    import inspect
    from IPython.display import display

    # Quellcode holen — robust gegen nicht-introspizierbare Objekte
    try:
        src = inspect.getsource(func)
    except (TypeError, OSError) as e:
        from IPython.display import Markdown
        name = getattr(func, "__name__", repr(func))
        display(Markdown(
            f"> ⚠️ Quellcode für `{name}` nicht verfügbar: {e}"
        ))
        return

    # Titel generieren
    mod = getattr(func, "__module__", "?")
    mod_path = mod.replace(".", "/")
    name = getattr(func, "__name__", "?")
    caption = title or f"Quellcode: `{name}` (aus `{mod_path}.py`)"

    if mode == "markdown":
        _show_source_markdown(src, caption, collapsed)
    elif mode == "html":
        _show_source_html(src, caption, collapsed, style)
    else:
        raise ValueError(
            f"mode muss 'markdown' oder 'html' sein, nicht {mode!r}"
        )


def _show_source_markdown(src: str, caption: str, collapsed: bool) -> None:
    """Markdown-Rendering. Nutzt JupyterLab's eigenes Syntax-Highlighting.

    Die Leerzeilen zwischen ``<details>``-Tag und Codeblock sind **wichtig**:
    Sie signalisieren dem Markdown-Parser, dass der Inhalt wieder als Markdown
    interpretiert werden soll (CommonMark HTML-block-in-markdown-Konvention).

    Backticks im caption werden in ``<code>``-Tags umgewandelt, weil innerhalb
    von ``<summary>`` Markdown in einigen Renderern nicht mehr geparst wird.
    """
    from IPython.display import Markdown, display

    # Backticks → <code> Tags für zuverlässiges Rendering in <summary>
    parts = caption.split("`")
    summary_html = parts[0]
    for i, p in enumerate(parts[1:], 1):
        tag = "<code>" if i % 2 == 1 else "</code>"
        summary_html += tag + p

    if collapsed:
        md = (
            f"<details>\n"
            f"<summary>🔎 {summary_html}</summary>\n"
            f"\n"
            f"```python\n"
            f"{src.rstrip()}\n"
            f"```\n"
            f"\n"
            f"</details>\n"
        )
    else:
        md = (
            f"**🔎 {caption}**\n"
            f"\n"
            f"```python\n"
            f"{src.rstrip()}\n"
            f"```\n"
        )

    display(Markdown(md))


def _show_source_html(src: str, caption: str, collapsed: bool, style: str) -> None:
    """HTML-Rendering via pygments. Fester Style, theme-unabhängig."""
    import html as _html
    from IPython.display import HTML, display

    # Pygments-Highlighting, Fallback auf Plain-Pre
    try:
        from pygments import highlight
        from pygments.lexers import PythonLexer
        from pygments.formatters import HtmlFormatter

        formatter = HtmlFormatter(
            noclasses=True,      # Inline styles → portabel
            style=style,
            nobackground=False,  # Style soll eigenen HG setzen
        )
        code_html = highlight(src, PythonLexer(), formatter)
        code_html = (
            '<div style="padding:4px;border-radius:4px;overflow-x:auto;'
            'font-size:12px;">' + code_html + '</div>'
        )
    except ImportError:
        # Fallback: Plain-Pre, neutral/hell
        code_html = (
            '<pre style="background:#f6f8fa;color:#24292f;padding:12px;'
            'border-radius:4px;overflow-x:auto;font-size:12px;'
            'border:1px solid #d0d7de;font-family:ui-monospace,'
            'SFMono-Regular,Consolas,monospace;">'
            f'<code>{_html.escape(src)}</code></pre>'
        )

    # caption enthält Backticks (Markdown); für HTML-Summary in <code> wandeln
    parts = caption.split("`")
    summary_html = parts[0]
    for i, p in enumerate(parts[1:], 1):
        tag = "<code>" if i % 2 == 1 else "</code>"
        summary_html += tag + p

    open_attr = "" if collapsed else " open"
    html = (
        f'<details{open_attr} style="margin:8px 0;'
        f'border:1px solid var(--jp-border-color2, #d0d7de);'
        f'border-radius:4px;">'
        f'<summary style="cursor:pointer;padding:8px 12px;user-select:none;'
        f'font-family:ui-sans-serif,system-ui,sans-serif;">'
        f'🔎 {summary_html}'
        f'</summary>'
        f'<div>{code_html}</div>'
        f'</details>'
    )
    display(HTML(html))


# ═══════════════════════════════════════════════════════════════════════════════
# should_skip — entscheidet ob Chart/GIF neu erzeugt werden muss
# ═══════════════════════════════════════════════════════════════════════════════

def should_skip(
    out_path: str,
    asset_type: str,
    name: str,
    cfg: dict[str, Any],
) -> bool:
    """Prüft anhand der Config, ob ein Chart/GIF neu erzeugt werden muss.

    Wird in jeder Zelle genutzt, die ein rechenintensives Artefakt erzeugt.
    Schema der relevanten Config-Sektion (in ``sync/config.json``):

    .. code-block:: json

        "animation": {
            "modus":          "skip_if_exists",
            "modus_statisch": "always",
            "overrides": {
                "kuer_k01_karte_verbraucher": "skip_if_exists"
            }
        }

    Entscheidungsreihenfolge
    ------------------------
    1. ``overrides[name]`` — explizit gesetzter Wert (höchste Priorität)
    2. ``asset_type == 'animation'`` → ``cfg['animation']['modus']``
       (Default: ``'skip_if_exists'``)
    3. ``asset_type == 'statisch'`` → ``cfg['animation']['modus_statisch']``
       (Default: ``'always'``). Wert ``'skip_if_exists_all'`` schaltet
       alle statischen Charts auf skip_if_exists um (Master-Schalter).

    Mode-Werte
    ----------
    * ``'skip_if_exists'``  — skip wenn Datei existiert und nicht leer
    * ``'always'``          — nie skip (Datei wird immer überschrieben)
    * ``'force_rebuild'``   — Alias für ``'always'``

    Parameter
    ---------
    out_path : str
        Zielpfad des zu erzeugenden Artefakts.
    asset_type : str
        Entweder ``'animation'`` oder ``'statisch'``.
    name : str
        Basename des Artefakts (ohne Extension), für ``overrides``-Lookup.
        Beispiel: ``'kuer_k04_anim_A_18h'``.
    cfg : dict
        Geladenes CFG-Dict aus ``sync/config.json``.

    Rückgabe
    --------
    bool
        ``True`` wenn die Erzeugung übersprungen werden kann, sonst ``False``.

    Beispiel
    --------
    >>> out = os.path.join(CHARTS_DIR, 'kuer_k04_anim_A_18h.gif')
    >>> if should_skip(out, 'animation', 'kuer_k04_anim_A_18h', CFG):
    ...     print(f"✓ Überspringe (existiert)")
    ... else:
    ...     make_gif_chart(...)
    """
    if asset_type not in ("animation", "statisch"):
        raise ValueError(
            f"asset_type muss 'animation' oder 'statisch' sein, "
            f"nicht {asset_type!r}"
        )

    anim_cfg = cfg.get("animation", {})
    overrides = anim_cfg.get("overrides", {})

    # 1. Explizit gesetzter Override (Keys mit _ sind Hinweis-Felder)
    if name in overrides and not name.startswith("_"):
        mode = overrides[name]
    # 2. Global je Asset-Typ
    elif asset_type == "animation":
        mode = anim_cfg.get("modus", "skip_if_exists")
    else:  # 'statisch'
        global_static = anim_cfg.get("modus_statisch", "always")
        # Master-Schalter: schaltet ALLE statischen Charts auf skip_if_exists
        if global_static == "skip_if_exists_all":
            mode = "skip_if_exists"
        else:
            mode = global_static

    # Validierung des Mode-Werts (nur informativ, fehlerhafte Werte → 'always')
    valid_modes = {"skip_if_exists", "always", "force_rebuild"}
    if mode not in valid_modes:
        # Nicht hart abbrechen — SSOT-Violation soll loud, aber nicht blockierend
        # sein, damit der Notebook-Lauf nicht an einem Tippfehler hängt.
        import warnings
        warnings.warn(
            f"Unbekannter Modus {mode!r} für {asset_type} '{name}'. "
            f"Erlaubt: {sorted(valid_modes)}. Fallback auf 'always'.",
            RuntimeWarning,
        )
        mode = "always"

    if mode == "skip_if_exists":
        return os.path.exists(out_path) and os.path.getsize(out_path) > 0
    # 'always' oder 'force_rebuild' → immer neu erzeugen
    return False



# ═══════════════════════════════════════════════════════════════════════════════
# make_spline_h24 — periodischer kubischer Spline für 24h-Daten (aus K_01)
# ═══════════════════════════════════════════════════════════════════════════════

def make_spline_h24(values_24):
    """Periodischer kubischer Spline für 24h-Stundenwerte.

    Erzeugt einen periodischen Spline aus 24 Stundenwerten (h=0..23). Stetigkeit
    in Wert *und* Ableitung an der Tag-Grenze (`cs(24) == cs(0)`) — geeignet für
    Last-Profile, Solar-/Wasser-Erzeugungsprofile, Mix-Anteile. Wird in K_01
    für Tagesverlaufs-Animationen (typisch 96 Zwischen-Punkte = 4f/h × 24h) und
    in den Heatmap-Plots für glatte Kurven genutzt.

    Parameter
    ---------
    values_24 : array-like, len=24
        24 Stundenwerte. Ein zusätzlicher Wert für h=24 wird intern als Kopie
        von `values_24[0]` ergänzt, damit der Spline schliesst.

    Return
    ------
    scipy.interpolate.CubicSpline
        Aufrufbar mit Stunden-Float: ``cs(12.5)`` → interpolierter Wert für
        12:30 Uhr. Akzeptiert auch Arrays: ``cs(HOUR_TIMES)`` → Array gleicher
        Länge.

    Beispiel
    --------
    >>> import numpy as np
    >>> from lib.plotting import make_spline_h24
    >>> last_24h = [3.5, 3.2, 3.0, 2.9, 2.8, 2.9, 3.4, 4.5, 5.8, 6.2, 6.4, 6.5,
    ...             6.3, 6.0, 5.7, 5.5, 5.6, 6.0, 6.5, 6.8, 6.5, 5.5, 4.5, 3.8]
    >>> cs = make_spline_h24(last_24h)
    >>> cs(12.5)        # Zwischenwert
    >>> cs(np.linspace(0, 24, 96, endpoint=False))  # 96 Punkte
    """
    import numpy as np
    from scipy.interpolate import CubicSpline

    h = np.arange(25)
    v = np.array(list(values_24) + [values_24[0]])
    return CubicSpline(h, v, bc_type='periodic')



# ═══════════════════════════════════════════════════════════════════════════════
# make_gif_chart — PIL-basierter GIF-Builder (aus K_01/K_04 extrahiert)
# ═══════════════════════════════════════════════════════════════════════════════

def make_gif_chart(fig, update_fn, frames, fps, path,
                   dpi=None, save_frames=None, cfg=None):
    """PIL-basierter GIF-Builder für animierte Charts.

    Für jeden Frame-Wert wird ``update_fn(frame_val)`` aufgerufen, das Figure
    in PNG gerendert und in die Frame-Liste aufgenommen. Am Ende werden die
    Frames als animiertes GIF gespeichert (``loop=0``).

    Parameter
    ---------
    fig : matplotlib.figure.Figure
        Die Figure, die für jeden Frame neu gerendert wird. ``update_fn`` muss
        in-place die Axes-Elemente dieser Figure aktualisieren.
    update_fn : callable
        Funktion ``update_fn(frame_val)``, aktualisiert die dynamischen
        Chart-Elemente für den aktuellen Frame-Wert.
    frames : Iterable
        Sequenz der Frame-Werte (z.B. ``HOUR_TIMES`` für Tagesanimation oder
        ``WEEK_TIMES`` für Jahresanimation).
    fps : int
        Frames pro Sekunde im Output-GIF.
    path : str
        Zieldatei (``.gif``). Bei ``save_frames=True`` werden die Einzelframes
        zusätzlich in ``<path_ohne_ext>_frames/frame_NNNN.png`` gespeichert.
    dpi : int, optional
        DPI beim Rendering. Default: ``cfg['animation']['dpi']`` (wenn cfg
        gegeben), sonst 110.
    save_frames : bool, optional
        Einzelframes zusätzlich als PNG speichern. Default:
        ``cfg['animation']['einzelbilder']`` (wenn cfg gegeben), sonst False.
    cfg : dict, optional
        Geladenes ``sync/config.json``. Wenn gegeben:
          * Skip-Check via :func:`should_skip` (liest ``animation.modus`` und
            ``animation.overrides``)
          * dpi/save_frames-Defaults aus ``animation.dpi`` / ``animation.einzelbilder``

    Return
    ------
    None. Bei ``skip_if_exists`` + existierender Datei: return ohne Rendering.
    """
    import io as _io
    from PIL import Image as _PILImage

    # Skip-Check: wenn cfg gegeben und should_skip True → nichts tun
    if cfg is not None:
        _name = os.path.basename(path).rsplit('.', 1)[0]
        if should_skip(path, 'animation', _name, cfg):
            print(f'⏭️  {_name} übersprungen (existiert)')
            return

    # Defaults aus cfg oder Fallbacks
    if cfg is not None:
        _dpi    = dpi        if dpi        is not None else cfg.get('animation', {}).get('dpi', 110)
        _einzel = save_frames if save_frames is not None else cfg.get('animation', {}).get('einzelbilder', False)
    else:
        _dpi    = dpi        if dpi        is not None else 110
        _einzel = save_frames if save_frames is not None else False

    frame_dir = path.replace('.gif', '_frames')
    if _einzel:
        os.makedirs(frame_dir, exist_ok=True)

    # Frame-Loop
    frames_pil = []
    for i, frame_val in enumerate(frames):
        update_fn(frame_val)
        buf = _io.BytesIO()
        fig.savefig(buf, format='png', dpi=_dpi,
                    bbox_inches='tight', facecolor=fig.get_facecolor())
        buf.seek(0)
        img = _PILImage.open(buf).convert('RGB').copy()
        if _einzel:
            img.save(os.path.join(frame_dir, f'frame_{i:04d}.png'), optimize=True)
        frames_pil.append(img)

    if not frames_pil:
        print('⚠️  Keine Frames')
        return

    frames_pil[0].save(path, save_all=True, append_images=frames_pil[1:],
                       duration=int(1000 / fps), loop=0, optimize=True)
    n  = len(frames_pil)
    kb = os.path.getsize(path) // 1024
    print(f'✅ {os.path.basename(path)} ({n}f @{fps}fps={n/fps:.1f}s | {kb} KB)')
    if _einzel:
        print(f'   Frames: {frame_dir}/')



# ═══════════════════════════════════════════════════════════════════════════════
# show_chart — Chart-Anzeige im Notebook (aus K_00 / NB00 extrahiert)
# ═══════════════════════════════════════════════════════════════════════════════

def show_chart(filename, caption='', width=950, charts_dir=None, as_html=None):
    """Zeigt einen erzeugten Chart (PNG, JPG, GIF) aus einem Charts-Verzeichnis.

    Der Renderer wird automatisch nach Dateiendung gewählt:
      * .gif  → HTML ``<img>``-Tag (animierte GIFs)
      * sonst → ``IPython.display.Image``

    Parameter
    ---------
    filename : str
        Dateiname der Chart-Datei (nur Name, Pfad wird ergänzt).
    caption : str, optional
        Text, der nach dem Bild ausgegeben wird.
    width : int, default 950
        Anzeige-Breite in Pixel.
    charts_dir : str, optional
        Charts-Verzeichnis. Wenn ``None``, wird im Caller-Scope die globale
        Variable ``CHARTS_DIR`` gesucht (Rückwärtskompatibilität).
    as_html : bool, optional
        Erzwingt HTML (``<img>``-Tag, für animierte GIFs) oder ``Image``
        (statisch). Bei ``None`` wird aus der Dateiendung abgeleitet
        (``.gif`` → HTML).

    Return
    ------
    None. Gibt Fehlermeldung auf stdout aus wenn die Datei fehlt.
    """
    from IPython.display import Image, HTML, display

    # charts_dir auflösen
    if charts_dir is None:
        import inspect
        caller_globals = inspect.stack()[1].frame.f_globals
        charts_dir = caller_globals.get('CHARTS_DIR')
        if charts_dir is None:
            print('⚠️  show_chart: weder charts_dir übergeben noch CHARTS_DIR im Scope')
            return

    path = os.path.join(charts_dir, filename)
    if not os.path.exists(path):
        print(f'❌  Nicht vorhanden: {path}')
        return

    # Renderer wählen
    if as_html is None:
        as_html = filename.lower().endswith('.gif')

    if as_html:
        display(HTML(f'<img src="{path}" width="{width}">'))
    else:
        display(Image(filename=path, width=width))

    if caption:
        print(f'\n{caption}\n')
