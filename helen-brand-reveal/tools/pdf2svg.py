"""Convert PyMuPDF vector drawings from the Helen brand manual into SVG paths.

Usage: python3 -I tools/pdf2svg.py <pdf> <page(1-based)> <out.svg> [idx,idx,...] [--ids a,b,c] [--pad N]
Keeps the original fill colours and geometry; only the viewBox is cropped to the selection.
"""
import sys
import pymupdf as fitz


def hexcol(c):
    return "#%02X%02X%02X" % tuple(round(v * 255) for v in c)


def path_d(items):
    out, cur = [], None
    for it in items:
        op = it[0]
        if op == "l":
            a, b = it[1], it[2]
            if cur is None or abs(cur.x - a.x) > 1e-3 or abs(cur.y - a.y) > 1e-3:
                out.append(f"M{a.x:.3f} {a.y:.3f}")
            out.append(f"L{b.x:.3f} {b.y:.3f}")
            cur = b
        elif op == "c":
            a, c1, c2, b = it[1:5]
            if cur is None or abs(cur.x - a.x) > 1e-3 or abs(cur.y - a.y) > 1e-3:
                out.append(f"M{a.x:.3f} {a.y:.3f}")
            out.append(f"C{c1.x:.3f} {c1.y:.3f} {c2.x:.3f} {c2.y:.3f} {b.x:.3f} {b.y:.3f}")
            cur = b
        elif op == "re":
            r = it[1]
            out.append(f"M{r.x0:.3f} {r.y0:.3f}H{r.x1:.3f}V{r.y1:.3f}H{r.x0:.3f}Z")
            cur = None
        elif op == "qu":
            q = it[1]
            out.append(f"M{q.ul.x:.3f} {q.ul.y:.3f}L{q.ur.x:.3f} {q.ur.y:.3f}L{q.lr.x:.3f} {q.lr.y:.3f}L{q.ll.x:.3f} {q.ll.y:.3f}Z")
            cur = None
    return "".join(out)


def drawing_svg(dr, el_id=None):
    attrs = [f'd="{path_d(dr["items"]) + ("Z" if dr.get("closePath") else "")}"']
    if el_id:
        attrs.insert(0, f'id="{el_id}"')
    if dr.get("fill") is not None:
        attrs.append(f'fill="{hexcol(dr["fill"])}"')
        if dr.get("even_odd"):
            attrs.append('fill-rule="evenodd"')
    else:
        attrs.append('fill="none"')
    if dr.get("color") is not None and dr["type"] in ("s", "fs"):
        attrs.append(f'stroke="{hexcol(dr["color"])}" stroke-width="{dr.get("width") or 1:.3f}"')
        attrs.append(f'stroke-linecap="{["butt","round","square"][int((dr.get("lineCap") or [0])[0])]}"')
        attrs.append(f'stroke-linejoin="{["miter","round","bevel"][int(dr.get("lineJoin") or 0)]}"')
    return "<path " + " ".join(attrs) + "/>"


def main():
    pdf, page, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    sel = None
    ids = []
    pad = 0.0
    args = sys.argv[4:]
    while args:
        a = args.pop(0)
        if a == "--ids":
            ids = args.pop(0).split(",")
        elif a == "--pad":
            pad = float(args.pop(0))
        else:
            sel = [int(x) for x in a.split(",")]
    drs = fitz.open(pdf)[page - 1].get_drawings()
    if sel is None:
        sel = list(range(len(drs)))
    chosen = [drs[i] for i in sel]
    r = fitz.Rect(chosen[0]["rect"])
    for dr in chosen[1:]:
        r |= dr["rect"]
    r = fitz.Rect(r.x0 - pad, r.y0 - pad, r.x1 + pad, r.y1 + pad)
    body = "\n  ".join(drawing_svg(dr, ids[k] if k < len(ids) else None) for k, dr in enumerate(chosen))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{r.x0:.3f} {r.y0:.3f} {r.width:.3f} {r.height:.3f}" '
           f'width="{r.width:.3f}" height="{r.height:.3f}">\n  {body}\n</svg>\n')
    open(out, "w").write(svg)
    print(out, f"bbox={r}", f"paths={len(chosen)}")


main()
