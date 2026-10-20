"""Build the Helen brand-reveal compositions from src/film.html.

Writes index.html (1920x1080) and portrait.html (1080x1920) from one template, and the
vector wordmark-pattern tile. All cut times come from the track's beat grid (108 BPM),
quantized to the 30 fps frame grid, so HTML clip windows and GSAP tweens share one clock.

Usage: python3 -I tools/build.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BPM = 108.0
BEAT = 60.0 / BPM
FPS = 30
END = 48.167  # final hit (bar 22) + ring-out; equals the bgm duration
FINAL_BAR = 22


def T(bar, beat=0.0):
    """Time of `beat` (0-based, may be fractional) in `bar` (1-based), snapped to a frame."""
    return round(((bar - 1) * 4 + beat) * BEAT * FPS) / FPS


def logo_paths(prefix):
    svg = (ROOT / "assets/brand/logo.svg").read_text()
    paths = re.findall(r'<path id="([^"]+)" d="([^"]+)"', svg)
    return {pid: d for pid, d in paths}


def logo_svg(prefix, width_css, with_hat_stroke=False, cls="logo"):
    p = logo_paths(prefix)
    letters = "".join(
        f'<path id="{prefix}-{k}" class="{prefix}-letter" d="{p["l-" + k]}" fill="#FEA300" fill-rule="evenodd"/>'
        for k in ("H", "e1", "l", "e2", "n")
    )
    hat_fill = "".join(
        f'<path class="{prefix}-hatfill" d="{p[k]}" fill="#FEA300" fill-rule="evenodd"/>' for k in ("hat-a", "hat-b")
    )
    hat_stroke = ""
    if with_hat_stroke:
        hat_stroke = "".join(
            f'<path class="{prefix}-hatstroke" d="{p[k]}" fill="none" stroke="#FEA300" stroke-width="0.85" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
            for k in ("hat-a", "hat-b")
        )
    return (
        f'<svg class="{cls}" id="{prefix}-svg" viewBox="108.817 272.310 287.396 119.929" '
        f'style="width:{width_css};overflow:visible" aria-label="Helen">'
        f'<g id="{prefix}-letters">{letters}</g>'
        f'<g id="{prefix}-hat">{hat_fill}{hat_stroke}</g></svg>'
    )


def wordmark_tile():
    """Brick-offset tile of the untouched wordmark (orange on beige), as on manual page 5."""
    p = logo_paths("t")
    lw, lh = 287.396, 119.929
    gx, gy = 78.0, 52.0
    cw, ch = lw + gx, lh + gy
    tw, th = cw, 2 * ch
    body = "".join(f'<path d="{d}" fill-rule="evenodd"/>' for d in p.values())
    sym = f'<symbol id="w" viewBox="108.817 272.310 {lw} {lh}" overflow="visible">{body}</symbol>'
    uses = [
        (gx / 2, gy / 2),
        (gx / 2 + cw / 2, gy / 2 + ch),
        (gx / 2 - cw / 2, gy / 2 + ch),
    ]
    use = "".join(f'<use href="#w" x="{x:.2f}" y="{y:.2f}" width="{lw}" height="{lh}"/>' for x, y in uses)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {tw:.2f} {th:.2f}" width="{tw:.2f}" height="{th:.2f}">'
        f'<defs>{sym}</defs><rect width="100%" height="100%" fill="#E3D8C5"/>'
        f'<g fill="#FEA300">{use}</g></svg>\n'
    )
    (ROOT / "assets/brand/pattern-wordmark-tile.svg").write_text(svg)
    return tw / th


def build(name, W, H):
    portrait = H > W
    tpl = (ROOT / "src/film.html").read_text()
    times = {f"T{b}": T(b) for b in range(1, FINAL_BAR + 1)}
    logo_w = "84cqw" if portrait else "57.3cqw"
    close_w = "80cqw" if portrait else "51cqw"
    subs = {
        "W": str(W),
        "H": str(H),
        "RES": "portrait" if portrait else "landscape",
        "ORIENT": "portrait" if portrait else "landscape",
        "END": f"{END:.3f}",
        "LOGO_MAIN": logo_svg("lg", logo_w, with_hat_stroke=True),
        "LOGO_CLOSE": logo_svg("cl", close_w),
        "TIMES_JSON": json.dumps(times),
    }
    # clip windows: start + duration per scene
    scenes = {
        "LOGO": (0.0, T(5)),
        "CONCEPT": (T(5), T(8)),
        "PALETTE": (T(8), T(10)),
        "TYPE": (T(10), T(11)),
        "HATS": (T(11), T(12)),
        "ICONS": (T(12), T(14)),
        "FOOD": (T(14), T(18)),
        "APPS": (T(18), T(21)),
        "CLOSE": (T(21), END),
    }
    for k, (a, b) in scenes.items():
        subs[f"{k}_START"] = f"{a:.4f}"
        subs[f"{k}_DUR"] = f"{b - a:.4f}"
    out = tpl
    for k, v in subs.items():
        out = out.replace(f"@@{k}@@", v)
    left = re.findall(r"@@[A-Z0-9_]+@@", out)
    assert not left, left
    (ROOT / name).write_text(out)
    print(f"wrote {name} {W}x{H}")


if __name__ == "__main__":
    wordmark_tile()
    build("index.html", 1920, 1080)
    build("vertical/index.html", 1080, 1920)
    print(json.dumps({f"bar{b}": T(b) for b in range(1, FINAL_BAR + 1)}))
