"""Cut the CONECTANDOSTUDIO motif illustrations out of the manual as standalone vector SVGs.

Page 9 holds four motifs stacked on a flat background; page 7 is the 3x4 identity grid, where
every cell has its own background rectangle. Each motif keeps its original fills and strokes and
gets a transparent background and a tight viewBox.

Usage: python3 -I tools/extract_icons.py <manual.pdf>
"""
import sys
from pathlib import Path

import pymupdf as fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pdf2svg import drawing_svg  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/icons"
OUT.mkdir(parents=True, exist_ok=True)
pdf = fitz.open(sys.argv[1])


def write(name, drs, pad=2.0):
    r = fitz.Rect(drs[0]["rect"])
    for d in drs[1:]:
        r |= d["rect"]
    r = fitz.Rect(r.x0 - pad, r.y0 - pad, r.x1 + pad, r.y1 + pad)
    body = "\n  ".join(drawing_svg(d) for d in drs)
    (OUT / f"{name}.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{r.x0:.2f} {r.y0:.2f} {r.width:.2f} {r.height:.2f}" '
        f'width="{r.width:.2f}" height="{r.height:.2f}">\n  {body}\n</svg>\n'
    )
    print(f"{name}: {len(drs)} paths, {r.width:.0f}x{r.height:.0f}")


# page 9: four motifs stacked vertically; assign each path to its motif's band (page y, pt)
BANDS = {"palmette": (120, 240), "helmet": (255, 365), "fan": (385, 465), "venus": (480, 610)}
drs = [d for d in pdf[8].get_drawings() if not (d["rect"].width > 400 and d["rect"].height > 600)]
for name, (y0, y1) in BANDS.items():
    write(name, [d for d in drs if y0 <= (d["rect"].y0 + d["rect"].y1) / 2 <= y1])

# page 7: identity grid cells holding a single motif
XS, YS = [1, 171, 341, 511], [0, 176, 351, 526, 708]
CELLS = {"bust": (0, 0), "cup": (0, 2), "fan-cream": (1, 2), "horse": (2, 1), "palmette-blue": (2, 2), "venus-line": (3, 0), "helmet-line": (3, 1)}
drs7 = pdf[6].get_drawings()
for name, (row, col) in CELLS.items():
    cell = fitz.Rect(XS[col], YS[row], XS[col + 1], YS[row + 1])
    g = [
        d
        for d in drs7
        if not (d["rect"].width > 100 and d["rect"].height > 100)
        and cell.contains(fitz.Point((d["rect"].x0 + d["rect"].x1) / 2, (d["rect"].y0 + d["rect"].y1) / 2))
    ]
    write(name, g)
