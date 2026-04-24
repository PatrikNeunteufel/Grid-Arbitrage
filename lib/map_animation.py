"""lib.map_animation — performance-optimierter Karten-GIF-Renderer.

Eine Funktion:

* ``make_gif_fast_map`` — erzeugt eine GIF-Animation mit statischem
  Karten-Hintergrund + dynamischen Layern pro Frame. Der Hintergrund wird
  nur einmal gerendert (als NumPy-Array) und via ``ax.imshow`` in den
  Frame-Axes wieder angezeigt → pixel-perfekte Ausrichtung.

Performance-Gewinn gegenüber naivem FuncAnimation:
  Bei N_FRAMES × schwerem Karten-Plot (GeoPandas-Polygone, viele Marker)
  entspricht der Hintergrund-Cache einer Reduktion von ``N × T_background +
  N × T_dynamic`` auf ``T_background + N × T_dynamic``. Bei 96 Frames und
  schwerem Background (Kantone + Leitungen + Knoten): typisch 3–5× schneller.

Typische Nutzung in einer NB-Zelle::

    from lib.map_animation import make_gif_fast_map

    def _draw_background(ax):
        ax.set_xlim(*MAP_XLIM); ax.set_ylim(*MAP_YLIM)
        gdf_kant.boundary.plot(ax=ax, color='#2a3d55', linewidth=0.7)
        # ... weitere statische Layer ...

    def _draw_dynamic(ax, frame_idx, n_frames):
        t_h = frame_idx / n_frames * 24.0
        # ... dynamische Marker, Flüsse, Text ...

    make_gif_fast_map(
        draw_background=_draw_background,
        draw_dynamic=_draw_dynamic,
        n_frames=96, fps=10,
        path=os.path.join(CHARTS_DIR, 'my_animation.gif'),
        map_xlim=(5.88, 10.60), map_ylim=(45.78, 47.92),
        dpi=130, fig_size_in=(14, 9),
    )
"""
from __future__ import annotations

import io
import os


# Modul-weiter Cache für Background-Arrays.
# Keys sind vom Caller vergeben (bg_cache_key). Gleicher Key → Wiederverwendung.
_BG_CACHE = {}


def make_gif_fast_map(
    draw_background,
    draw_dynamic,
    n_frames,
    fps,
    path,
    map_xlim,
    map_ylim,
    dpi=90,
    fig_size_in=(14, 9),
    facecolor='#0d1117',
    ax_facecolor='#090d14',
    bg_cache_key=None,
    skip_check=None,
    save_frames=True,
    verbose=True,
):
    """Erzeugt ein animiertes GIF mit statischem Hintergrund + dynamischen Layern.

    Rendert den Hintergrund einmal (optional gecacht), dann für jeden Frame
    eine frische Axes mit ``imshow(bg_arr)`` und dem Dynamik-Callback. Die
    Einzelbilder werden als PNGs in ``<path>_frames/`` gespeichert (Standard)
    — diese kann ``lib.widgets.show_animation(path, mode='slider')`` dann
    interaktiv durchblättern.

    Parameter
    ---------
    draw_background : callable(ax) → None
        Zeichnet die statischen Karten-Layer (Kantone, Leitungen, Knoten,
        Zonen-Füllungen) in die übergebene matplotlib Axes. Wird
        EINMAL vor dem Render-Loop aufgerufen. Alle Einstellungen ausser
        xlim/ylim und facecolor setzt der Callback selbst.
    draw_dynamic : callable(ax, frame_idx, n_frames) → None
        Zeichnet dynamische Elemente (Marker, Flüsse, Text, Overlays) für
        den aktuellen Frame. Wird pro Frame aufgerufen. Axes ist bereits
        mit xlim/ylim konfiguriert und zeigt den Hintergrund.
    n_frames : int
        Anzahl Frames im GIF (z.B. 96 = 4h Tagesverlauf bei 4-Frames/h).
    fps : int or float
        Frames pro Sekunde im GIF (z.B. 10).
    path : str
        Ausgabe-Pfad für das GIF (z.B. ``'output/charts/animation.gif'``).
    map_xlim, map_ylim : (float, float)
        Karten-Grenzen in Lon/Lat (z.B. ``(5.88, 10.60)``, ``(45.78, 47.92)``
        für die Schweiz).
    dpi : int, default 90
        Auflösung. 90 = kompakte GIFs (~1MB), 130+ = hochauflösend (~3MB).
    fig_size_in : (float, float), default (14, 9)
        Figure-Grösse in Zoll — zusammen mit dpi ergeben sich die Pixel.
    facecolor : str, default '#0d1117'
        Hintergrundfarbe der Figure (dark-theme).
    ax_facecolor : str, default '#090d14'
        Hintergrundfarbe der Axes (minimal dunkler).
    bg_cache_key : str, optional
        Key für den Modul-Cache. Gleicher Key → Hintergrund wird
        wiederverwendet (z.B. beim Erzeugen mehrerer GIFs mit gleicher
        Basis-Karte). None (Default) → kein Caching.
    skip_check : callable() → bool, optional
        Wenn gesetzt und True zurückgibt → Funktion kehrt sofort zurück
        (für Skip-Logik via config.json). Beispiel::

            skip_check=lambda: should_skip(path, 'animation', name, CFG)

    save_frames : bool, default True
        PNG-Einzelbilder in ``<path>_frames/`` speichern. Erforderlich für
        Slider-Modus von ``show_animation``.
    verbose : bool, default True
        Status-Meldungen auf stdout.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image as PILImage

    # ── Skip-Check ────────────────────────────────────────────────────────────
    if skip_check is not None and skip_check():
        if verbose:
            print(f'⏭️  {os.path.basename(path)} übersprungen (existiert)')
        return

    # ── Schritt 1: Hintergrund rendern (einmal, optional gecacht) ─────────────
    bg_arr = _render_background_cached(
        draw_background, map_xlim, map_ylim, dpi, fig_size_in,
        facecolor, ax_facecolor, bg_cache_key, verbose)
    h, w = bg_arr.shape[:2]

    fig_w = w / dpi
    fig_h = h / dpi

    # ── Schritt 2: Frame-Ordner anlegen ───────────────────────────────────────
    if save_frames:
        frame_dir = path.replace('.gif', '_frames')
        os.makedirs(frame_dir, exist_ok=True)

    frames_pil = []

    # ── Schritt 3: Frames rendern ────────────────────────────────────────────
    for fi in range(n_frames):
        fig = plt.figure(figsize=(fig_w, fig_h), facecolor=facecolor, dpi=dpi)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(*map_xlim); ax.set_ylim(*map_ylim)
        ax.set_facecolor(ax_facecolor); ax.set_axis_off()
        ax.set_aspect('auto')

        # Background via imshow — pixel-genaue Ausrichtung
        ax.imshow(bg_arr,
                  extent=[map_xlim[0], map_xlim[1], map_ylim[0], map_ylim[1]],
                  origin='upper', aspect='auto',
                  interpolation='nearest', zorder=0)

        # Callback für dynamische Layer
        draw_dynamic(ax, fi, n_frames)

        # Frame → PIL-Image
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=dpi, facecolor=facecolor,
                    bbox_inches=None, pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        frame = PILImage.open(buf).convert('RGB').copy()

        if save_frames:
            frame.save(os.path.join(frame_dir, f'frame_{fi:04d}.png'),
                       optimize=True)
        frames_pil.append(frame)

    # ── Schritt 4: GIF-Compose ────────────────────────────────────────────────
    frames_pil[0].save(path, save_all=True, append_images=frames_pil[1:],
                       duration=int(1000 / fps), loop=0, optimize=True)

    if verbose:
        kb = os.path.getsize(path) // 1024
        print(f'✅ {os.path.basename(path)}')
        print(f'   {n_frames}f @{fps}fps = {n_frames/fps:.1f}s | '
              f'{kb} KB | {w}×{h}px')
        if save_frames:
            print(f'   Frames: {frame_dir}/')


def _render_background_cached(draw_background, map_xlim, map_ylim, dpi,
                               fig_size_in, facecolor, ax_facecolor,
                               cache_key, verbose):
    """Rendert den Hintergrund zu einem NumPy-Array (RGBA). Cache optional."""
    import matplotlib.pyplot as plt
    import numpy as np

    if cache_key is not None and cache_key in _BG_CACHE:
        return _BG_CACHE[cache_key]

    if verbose:
        print(f'  Pre-render Hintergrund...', end=' ', flush=True)

    fig = plt.figure(figsize=fig_size_in, facecolor=facecolor, dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(*map_xlim); ax.set_ylim(*map_ylim)
    ax.set_facecolor(ax_facecolor); ax.set_axis_off()
    ax.set_aspect('auto')

    draw_background(ax)

    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    bg_arr = np.asarray(fig.canvas.buffer_rgba()).reshape(h, w, 4).copy()
    plt.close(fig)

    if cache_key is not None:
        _BG_CACHE[cache_key] = bg_arr

    if verbose:
        print(f'OK ({w}×{h}px)')

    return bg_arr


def clear_background_cache():
    """Leert den Background-Cache. Nützlich bei iterativer Entwicklung."""
    _BG_CACHE.clear()
