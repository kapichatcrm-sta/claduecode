"""Extract CONECTANDOSTUDIO brand assets from the manual PDF.

Writes into assets/: the logo as vector glyph outlines (each caps letter addressable), the
MovesCabse font embedded in the manual, a seamless tile of the vase pattern, and every photo /
mockup rendered at its native resolution.

Usage: python3 -I tools/extract_assets.py <manual.pdf>
"""
import re
import sys
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "assets"
pdf = fitz.open(sys.argv[1])
PW, PH = 510.236, 708.661


def page_svg(pn):
    return pdf[pn - 1].get_svg_image(text_as_path=True)


def crop_svg(svg, box, drop_bg=False):
    x, y, w, h = box
    svg = re.sub(
        r'width="[^"]*" height="[^"]*" viewBox="[^"]*"',
        f'width="{w:.2f}" height="{h:.2f}" viewBox="{x:.3f} {y:.3f} {w:.3f} {h:.3f}"',
        svg,
        count=1,
    )
    if drop_bg:
        # the first full-page filled path is the page background
        svg = re.sub(r'<path transform="matrix\(1,0,0,-1,0,708\.6614\)" d="M0 708\.6614H510\.2362V0H0Z"[^>]*/>', "", svg, count=1)
    return svg


# ---------------------------------------------------------------- logo (page 1)
svg = page_svg(1)
defs = re.search(r"<defs>.*?</defs>", svg, re.S).group(0)
uses = re.findall(r'<use data-text="([^"]*)" xlink:href="#(font_\d+_\d+)" transform="([^"]+)" fill="[^"]+"/>', svg)
caps, script = [], []
for ch, ref, tr in uses:
    if ch == " ":
        continue
    (caps if ref.startswith("font_1_") else script).append((ch, ref, tr))
# logo box from the PDF spans: caps 120.9..388.8 x 320.4..343.3, script 159.2..358.7 x 332..370.3
box = (118.0, 316.0, 274.0, 58.0)


def logo_svg(fill, prefix):
    letters = "".join(
        f'<use id="{prefix}-c{i}" class="{prefix}-cap" xlink:href="#{ref}" transform="{tr}"/>' for i, (ch, ref, tr) in enumerate(caps)
    )
    scr = "".join(f'<use xlink:href="#{ref}" transform="{tr}"/>' for ch, ref, tr in script)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="{box[0]} {box[1]} {box[2]} {box[3]}" width="{box[2]}" height="{box[3]}">'
        f"{defs}<g fill=\"{fill}\"><g id=\"{prefix}-caps\">{letters}</g><g id=\"{prefix}-script\">{scr}</g></g></svg>\n"
    )


(A / "brand").mkdir(parents=True, exist_ok=True)
(A / "brand/logo-navy.svg").write_text(logo_svg("#3E5B79", "lg"))
(A / "brand/logo-cream.svg").write_text(logo_svg("#F5EDDA", "lg"))
print("logo:", "".join(c for c, _, _ in caps), "/", "".join(c for c, _, _ in script))

# ---------------------------------------------------------------- MovesCabse (full font embedded)
(A / "fonts").mkdir(exist_ok=True)
for x in pdf[0].get_fonts(full=True):
    if "MovesCabse" in x[3]:
        name, ext, _, buf = pdf.extract_font(x[0])
        (A / "fonts/MovesCabse.ttf").write_bytes(buf)
        print("font: MovesCabse", len(buf))

# ---------------------------------------------------------------- photos & mockups at native resolution
(A / "img").mkdir(exist_ok=True)
Z = 1418 / PW
CLIPS = {
    "swatches": (2, (0, 0, PW, PH)),
    "pattern-greek": (5, (0, 0, PW, PH)),
    "roll-greek": (6, (0, 0, PW, 354)),
    "roll-masks": (6, (0, 355, PW, PH)),
    "sign": (8, (0, 0, PW, PH)),
    "swatch-masks": (11, (0, 0, PW, 355)),
    "wall-masks": (11, (0, 355, PW, PH)),
    "printer-greek": (12, (0, 0, PW, 355)),
    "printer-masks": (12, (0, 355, PW, PH)),
    "cards-wood": (14, (0, 0, PW, 284)),
    "frame-masks": (14, (0, 284, PW, 567)),
    "fabric-card": (15, (0, 0, 381, PH)),
    "cup": (17, (255, 0, PW, PH)),
    "roll-light": (17, (0, 0, 255, PH)),
    "frame-palm": (18, (0, 0, PW, PH)),
    "card-patterns": (19, (0, 0, PW, PH)),
    "wall-stickers": (4, (0, 0, PW, PH)),
}
for name, (pn, r) in CLIPS.items():
    pix = pdf[pn - 1].get_pixmap(matrix=fitz.Matrix(Z, Z), clip=fitz.Rect(*r), alpha=False)
    pix.save(str(A / f"img/{name}.jpg"), jpg_quality=93)
    print(f"img {name}: {pix.width}x{pix.height}")

# ---------------------------------------------------------------- seamless tile of the vase pattern (page 3)
# the vases repeat every 70.866 pt across and 99.213 pt down; any interior window of that size tiles
tile = fitz.open(stream=crop_svg(page_svg(3), (80.0, 40.0, 70.866, 99.213)).encode(), filetype="svg")
pix = tile[0].get_pixmap(matrix=fitz.Matrix(8, 8), alpha=False)
pix.save(str(A / "brand/pattern-vases-tile.png"))
print(f"tile: vases {pix.width}x{pix.height}")
