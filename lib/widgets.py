"""lib.widgets — interaktive Widget-Helfer für Animations-Anzeige.

Zwei öffentliche Funktionen:

* ``slide_or_play``   — interaktiver Frame-Viewer mit Play-Button & Slider.
  Erwartet einen Ordner mit ``frame_*.png``-Dateien (der aus der
  Einzelbild-Speicherung von make_gif_chart stammt, wenn
  ``animation.einzelbilder: true`` in config.json).

* ``show_animation``  — Wrapper-Funktion, die wahlweise das fertige GIF
  inline zeigt oder ``slide_or_play`` auf dem zugehörigen ``_frames/``-Ordner
  aufruft. Per Parameter ``mode='gif'|'slider'`` pro Anzeige frei wählbar.

Typische Nutzung in einer NB-Anzeige-Zelle::

    from lib.widgets import show_animation
    _p = os.path.join(CHARTS_DIR, 'kuer_k04_anim_A.gif')
    show_animation(_p, mode='gif')     # oder mode='slider'
"""
from __future__ import annotations

import os
import glob
import threading
import time
import base64


# ═══════════════════════════════════════════════════════════════════════════════
# slide_or_play — interaktiver Frame-Betrachter mit Play-Button & Slider
# ═══════════════════════════════════════════════════════════════════════════════

def _find_frame_dir(name_or_path: str, charts_dir: str | None = None) -> str:
    """Findet den Frame-Ordner robust; akzeptiert verschiedene Input-Varianten.

    Reihenfolge der Suchkandidaten:
      1. Input ist bereits ein Ordner (z.B. '.../myanim_frames')
      2. Input ist ein GIF-Pfad ('.../myanim.gif') → ersetze .gif durch _frames
      3. Input + '_frames' (bei Basename ohne Extension)
      4. {charts_dir}/{input}_frames (wenn charts_dir übergeben)
    """
    # 1. Direkt ein Ordner
    if os.path.isdir(name_or_path):
        return name_or_path
    # 2. GIF-Pfad → ersetze .gif durch _frames
    if name_or_path.endswith(".gif"):
        candidate = name_or_path[:-4] + "_frames"
        if os.path.isdir(candidate):
            return candidate
    # 3. Input + '_frames'
    candidate = name_or_path + "_frames"
    if os.path.isdir(candidate):
        return candidate
    # 4. Unter charts_dir suchen
    if charts_dir is not None:
        for stem in (name_or_path, name_or_path.replace(".gif", "")):
            candidate = os.path.join(charts_dir, stem + "_frames")
            if os.path.isdir(candidate):
                return candidate
    raise FileNotFoundError(
        f"Kein Frame-Ordner gefunden für {name_or_path!r}. "
        f"Erwartet: <gif_basename>_frames/ mit frame_*.png Dateien. "
        f"Hinweis: config.json → animation.einzelbilder muss true sein, "
        f"damit Frames beim GIF-Erzeugen gespeichert werden."
    )


def slide_or_play(
    name_or_path: str,
    framerate: int = 10,
    image_width: str = "100%",
    charts_dir: str | None = None,
) -> None:
    """Interaktiver Frame-Viewer mit Play-Button und Slider.

    Verhalten
    ---------
    * Play-Button startet automatisch vom aktuellen Slider-Stand im Loop
    * Slider-Bewegung (Drag) stoppt Play → Anzeige folgt dem Slider
    * Play-Button erneut drückbar → spielt wieder vom aktuellen Stand ab
    * Loop am Ende zurück auf Frame 0

    Parameter
    ---------
    name_or_path : str
        Name der Animation (z.B. 'kuer_k04_anim_A') oder direkter Pfad
        (entweder zum _frames-Ordner oder zur .gif-Datei).
    framerate : int, default 10
        Bilder pro Sekunde beim Play.
    image_width : str, default '100%'
        CSS-Breite des Bildes ('100%', '900px', ...).
    charts_dir : str, optional
        Basisverzeichnis wenn name_or_path nur ein Basename ist.

    Voraussetzung
    -------------
    ``ipywidgets`` muss installiert sein (Pflicht-NB ``O_00_Installer`` Gruppe
    ``kuer_anim`` bzw. ``exp_widgets`` deckt das ab). Ohne ipywidgets wird
    eine Warnung gedruckt und die Funktion tut nichts.
    """
    try:
        import ipywidgets as widgets
        from IPython.display import display
    except ImportError:
        print(
            "⚠️  ipywidgets nicht verfügbar — slide_or_play braucht ipywidgets. "
            "Installation: pip install ipywidgets jupyterlab_widgets"
        )
        return

    frame_dir = _find_frame_dir(name_or_path, charts_dir=charts_dir)
    files = sorted(glob.glob(os.path.join(frame_dir, "frame_*.png")))
    if not files:
        print(f"⚠️  Keine frame_*.png in {frame_dir}")
        return

    n_frames = len(files)
    delay_ms = 1000.0 / max(1, framerate)

    # Frames einmal in Memory → flüssiges Abspielen
    # (Jedes Frame ~100-500 KB, 300 Frames ≈ 30-150 MB — akzeptabel)
    print(f"📼 Lade {n_frames} Frames aus {frame_dir}...")
    frame_data_uris = []
    for f in files:
        with open(f, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("ascii")
            frame_data_uris.append(f"data:image/png;base64,{b64}")
    print(f"   ✅ geladen ({sum(len(u) for u in frame_data_uris)//1024//1024} MB RAM)")

    # ── Widgets ──────────────────────────────────────────────────────────────
    img_widget = widgets.HTML(
        value=f'<img src="{frame_data_uris[0]}" style="width:{image_width};display:block">',
    )
    slider = widgets.IntSlider(
        value=0, min=0, max=n_frames - 1, step=1,
        description="Frame", continuous_update=True,
        layout=widgets.Layout(width="70%"),
    )
    play_btn = widgets.ToggleButton(
        value=False, description="▶ Play", button_style="success",
        tooltip="Starten / Pausieren",
        layout=widgets.Layout(width="100px"),
    )
    info_label = widgets.Label(
        value=f"{n_frames} Frames @ {framerate} fps = {n_frames/framerate:.1f}s",
        layout=widgets.Layout(margin="0 0 0 10px"),
    )

    # Flag um Thread- vs User-Slider-Änderungen zu unterscheiden
    state = {"internal_update": False, "stop_event": threading.Event()}

    def update_image(fi: int) -> None:
        img_widget.value = (
            f'<img src="{frame_data_uris[fi]}" style="width:{image_width};display:block">'
        )

    def on_slider_change(change):
        update_image(change["new"])
        # User-Änderung stoppt Play
        if not state["internal_update"] and play_btn.value:
            play_btn.value = False

    slider.observe(on_slider_change, names="value")

    def play_loop():
        while not state["stop_event"].is_set() and play_btn.value:
            time.sleep(delay_ms / 1000.0)
            if state["stop_event"].is_set() or not play_btn.value:
                break
            nxt = (slider.value + 1) % n_frames
            state["internal_update"] = True
            slider.value = nxt
            state["internal_update"] = False

    def on_play_toggle(change):
        if change["new"]:  # Play gedrückt
            play_btn.description = "⏸ Pause"
            play_btn.button_style = "warning"
            state["stop_event"].clear()
            t = threading.Thread(target=play_loop, daemon=True)
            t.start()
        else:  # Pause
            play_btn.description = "▶ Play"
            play_btn.button_style = "success"
            state["stop_event"].set()

    play_btn.observe(on_play_toggle, names="value")

    controls = widgets.HBox(
        [play_btn, slider, info_label],
        layout=widgets.Layout(align_items="center", margin="5px 0"),
    )
    display(widgets.VBox([img_widget, controls]))


# ═══════════════════════════════════════════════════════════════════════════════
# show_animation — Anzeige-Wrapper: GIF oder Slider, per Parameter wählbar
# ═══════════════════════════════════════════════════════════════════════════════

def show_animation(
    path: str,
    mode: str = "gif",
    framerate: int = 10,
    width=1100,
    caption: str | None = None,
) -> None:
    """Zeigt eine Animation an — als GIF (inline) oder als Slider (interaktiv).

    Parameter
    ---------
    path : str
        Voller Pfad zur .gif-Datei. Bei mode='slider' wird der zugehörige
        ``<basename>_frames/``-Ordner automatisch gefunden.
    mode : {'gif', 'slider'}, default 'gif'
        ``'gif'``    — zeigt das fertige GIF inline
        ``'slider'`` — interaktiver Play/Slide-Viewer (Voraussetzung: ipywidgets
        installiert und Frames im _frames/-Ordner vorhanden)
    framerate : int, default 10
        fps bei mode='slider'. Bei mode='gif' ignoriert (fps steckt im GIF).
    width : int or str, default 1100
        Anzeigebreite. Int → Pixel (z.B. 900), Str → CSS (z.B. '100%', '900px').
    caption : str, optional
        Bildunterschrift. Wird nach der Animation ausgegeben.

    Beispiele
    ---------
    >>> show_animation('/output/charts/kuer_k04_anim_A.gif', mode='gif')
    >>> show_animation('/output/charts/kuer_k04_anim_A.gif', mode='slider',
    ...                framerate=15, width='100%')
    """
    from IPython.display import display, Image, HTML

    if mode not in ("gif", "slider"):
        raise ValueError(
            f"mode muss 'gif' oder 'slider' sein, nicht {mode!r}"
        )

    # Für beide Modi: Existenz prüfen (bei slider auf _frames-Ordner via slide_or_play)
    if mode == "gif":
        if not os.path.exists(path):
            print(f"⚠️  Datei nicht gefunden: {path}")
            return
        # Int width → px (Image-Parameter), Str width → CSS über HTML-img
        if isinstance(width, int):
            display(Image(filename=path, width=width))
        else:
            display(HTML(f'<img src="{path}" style="width:{width};display:block">'))
    else:  # mode == 'slider'
        # Breite als CSS-String für slide_or_play
        if isinstance(width, int):
            width_css = f"{width}px"
        else:
            width_css = width
        slide_or_play(path, framerate=framerate, image_width=width_css)

    if caption:
        print(f"\n{caption}\n")
