"""Compose the labeled storyboard sheet from `hyperframes snapshot` frames.

Usage: python3 -I tools/storyboard_sheet.py <snapshot_dir> <font.woff2> <out.jpg>
"""
import glob
import re
import sys
from PIL import Image, ImageDraw, ImageFont

LABELS = [
    ("1 INTRO", "c1-2", "gorro se dibuja, 1 trazo por golpe"),
    ("2 LOGO", "c3 · 4.43s", "CRASH: gorro aterriza sobre la e"),
    ("2 LOGO", "c4", "letras en corcheas + push"),
    ("CORTE", "c5 · 8.90s", "zoom-through por el ojo de la e"),
    ("3 CONCEPTO", "c5", "titular palabra x corchea"),
    ("3 CONCEPTO", "c6-7", "1 valor por beat"),
    ("4 PALETA", "c8 · 15.57s", "CRASH: 1 swatch por golpe"),
    ("4 PALETA", "c9 b3-4", "naranja se expande (carrier)"),
    ("5 TIPOGRAFÍA", "c10 · 20.00s", "break: persiana en corcheas"),
    ("6 PATRONES", "c11 · 22.23s", "CRASH: gorros, diagonal"),
    ("6 PATRONES", "c12 · 24.43s", "corte en el kick: wordmark"),
    ("6 ÍCONOS", "c12-13", "1 celda por corchea, dolly 2.5D"),
    ("7 COMIDA", "c14 · 28.90s", "CRASH: zoom a empanadas"),
    ("7 COMIDA", "c14 b3", "punch-in pizza"),
    ("7 COMIDA", "c15", "relleno"),
    ("7 COMIDA", "c15 b3", "canelones en marco"),
    ("7 COMIDA", "c16", "split en corcheas"),
    ("7 COMIDA", "c16 b3", "tríptico en corcheas"),
    ("7 COMIDA", "c17", "punch-in queso"),
    ("7 COMIDA", "c17 b3", "empanadas, sale en whip"),
    ("8 APLICAC.", "c18 · 37.77s", "CRASH: whip + cartel"),
    ("8 APLICAC.", "c18 b3", "vidriera (logo al centro)"),
    ("8 APLICAC.", "c19", "laptop"),
    ("8 APLICAC.", "c19 b3", "caja de pizza"),
    ("8 APLICAC.", "c20", "bolsa kraft"),
    ("8 APLICAC.", "c20 b3", "menú"),
    ("8 APLICAC.", "c20 b4", "delantal, sale en inverse zoom"),
    ("9 CIERRE", "c21 · 44.43s", "CRASH: logo llega, tagline"),
    ("9 CIERRE", "c22 · 46.67s", "ÚLTIMO GOLPE: pulso"),
    ("FIN", "48.17s", "hold 1.5 s, el tema resuena"),
]

snap, font, out = sys.argv[1:4]
fs = sorted(glob.glob(f"{snap}/frame-*.png"), key=lambda f: int(re.search(r"frame-(\d+)", f).group(1)))
times = [float(re.search(r"at-([\d.]+)s", f).group(1)) for f in fs]
tw, th, cols, pad, cap = 480, 270, 5, 14, 58
rows = -(-len(fs) // cols)
W = cols * (tw + pad) + pad
H = 110 + rows * (th + cap + pad) + pad
sheet = Image.new("RGB", (W, H), "#072305")
d = ImageDraw.Draw(sheet)
f1, f2, f3 = (ImageFont.truetype(font, s) for s in (40, 19, 16))
d.text((pad, 30), "Helen — storyboard sincronizado al tema (108 BPM · 1 compás = 2,22 s · 16:9)", font=f1, fill="#FEA300")
for i, (f, t) in enumerate(zip(fs, times)):
    r, c = divmod(i, cols)
    x, y = pad + c * (tw + pad), 110 + r * (th + cap + pad)
    sheet.paste(Image.open(f).convert("RGB").resize((tw, th)), (x, y))
    a, b, e = LABELS[i]
    d.text((x, y + th + 6), f"{t:5.2f}s  {a}  [{b}]", font=f2, fill="#F7F4ED")
    d.text((x, y + th + 31), e, font=f3, fill="#E3D8C5")
sheet.save(out, quality=88)
print(out, sheet.size)
