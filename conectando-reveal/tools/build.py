"""Build the CONECTANDOSTUDIO reveal: index.html (1920x1080) and vertical/index.html (1080x1920).

The logo is injected as outlined glyphs taken from the manual (defs once, <use> per instance),
and every scene window comes from the 120 BPM beat grid (1 bar = 2 s, all on the 30 fps grid).

Usage: python3 -I tools/build.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEAT = 0.5
END = 45.6  # final hit (bar 23 = 44.0 s) + ring-out; equals the bgm duration
VIEWBOX = "118 316 274 58"


def T(bar, beat=0.0):
    return round(((bar - 1) * 4 + beat) * BEAT * 30) / 30


svg = (ROOT / "assets/brand/logo-navy.svg").read_text()
DEFS = re.search(r"<defs>.*?</defs>", svg, re.S).group(0)
CAPS = re.findall(r'<use id="lg-c\d+" class="lg-cap" (xlink:href="#[^"]+" transform="[^"]+")/>', svg)
SCRIPT = re.findall(r'<use (xlink:href="#font_2_[^"]+" transform="[^"]+")/>', re.search(r'<g id="lg-script">(.*?)</g>', svg, re.S).group(1))


def logo(prefix, fill, script_fill=None, caps=True, script=True):
    out = [f'<div class="logo" id="{prefix}">']
    if caps:
        # each glyph sits in its own <g> so GSAP can move the group without touching the glyph matrix
        uses = "".join(f'<g id="{prefix}-c{i}" class="{prefix}-cap"><use {u}/></g>' for i, u in enumerate(CAPS))
        out.append(f'<svg class="lg-layer" id="{prefix}-caps" viewBox="{VIEWBOX}"><g fill="{fill}">{uses}</g></svg>')
    if script:
        uses = "".join(f"<use {u}/>" for u in SCRIPT)
        out.append(f'<svg class="lg-layer" id="{prefix}-script" viewBox="{VIEWBOX}"><g fill="{script_fill or fill}">{uses}</g></svg>')
    out.append("</div>")
    return "".join(out)


def build(name, W, H):
    tpl = (ROOT / "src/film.html").read_text()
    subs = {
        "W": str(W),
        "H": str(H),
        "RES": "portrait" if H > W else "landscape",
        "ORIENT": "portrait" if H > W else "landscape",
        "END": f"{END:.3f}",
        "LOGO_DEFS": f'<svg width="0" height="0" style="position:absolute" aria-hidden="true">{DEFS}</svg>',
        "LOGO_INTRO": logo("lg", "#3E5B79"),
        "LOGO_MAST": logo("mh", "#3E5B79"),
        "LOGO_TYPE": logo("tyq", "#AFC6CC", caps=False),
        "LOGO_CLOSE": logo("cl", "#F5EDDA"),
    }
    # scene windows (start, end); push seams overlap by half a push on each side
    P2 = 0.4  # half of a 0.8 s push
    scenes = {
        "INTRO": (0.0, T(4) + P2),
        "MAST": (T(3, 2.4), T(21)),  # starts early: the logo's flight to the masthead happens on this layer
        "ICONS": (T(4) - P2, T(8)),
        "PALETTE": (T(7, 2), T(11) + P2),
        "TYPE": (T(11) - P2, T(13)),
        "PATTERNS": (T(12, 2), T(17) + P2),
        "APPS": (T(17) - P2, T(21)),
        "CLOSE": (T(20, 2), END),
    }
    for k, (a, b) in scenes.items():
        subs[f"{k}_START"] = f"{a:.4f}"
        subs[f"{k}_DUR"] = f"{b - a:.4f}"
    out = tpl
    for k, v in subs.items():
        out = out.replace(f"@@{k}@@", v)
    left = re.findall(r"@@[A-Z0-9_]+@@", out)
    assert not left, left
    (ROOT / name).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / name).write_text(out)
    print(f"wrote {name} {W}x{H}")


if __name__ == "__main__":
    build("index.html", 1920, 1080)
    build("vertical/index.html", 1080, 1920)
    print(json.dumps({f"bar{b}": T(b) for b in range(1, 24)}))
