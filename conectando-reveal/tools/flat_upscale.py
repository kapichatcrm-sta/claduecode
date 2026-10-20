"""Upscale flat-colour illustration (the manual's patterns) without blur.

Flat artwork is a handful of inks. Cluster the pixels into those inks, upscale each ink's
coverage map smoothly, take the winning ink per output pixel at 2x supersampling and average
down: clean anti-aliased edges instead of a soft resample of the JPEG in the PDF.

Usage: python3 -I tools/flat_upscale.py <in.png> <out.png> <scale> <n_inks>
"""
import sys

import cv2
import numpy as np

src, dst, scale, k = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
img = cv2.imread(src, cv2.IMREAD_COLOR)
h, w = img.shape[:2]
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
# find the true inks on flat interiors only: JPEG edge pixels would otherwise form fake inks (halos)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
grad = cv2.magnitude(cv2.Sobel(gray, cv2.CV_32F, 1, 0), cv2.Sobel(gray, cv2.CV_32F, 0, 1))
flat = (cv2.GaussianBlur(grad, (0, 0), 1.0) < 12).reshape(-1)
crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.2)
cv2.setRNGSeed(7)
_, _, centers = cv2.kmeans(lab[flat][::5], k, None, crit, 4, cv2.KMEANS_PP_CENTERS)
# assign every pixel (edges included) to its nearest ink
d = ((lab[:, None, :] - centers[None, :, :]) ** 2).sum(-1)
lbl = d.argmin(1).reshape(h, w)
# palette in BGR = median colour of each ink's pixels (keeps the true ink, not the cluster mean)
flat_px = img.reshape(-1, 3)[flat]
flat_lbl = lbl.reshape(-1)[flat]
pal = np.array([np.median(flat_px[flat_lbl == i], axis=0) for i in range(k)], np.float32)
S = 2  # supersample
oh, ow = int(round(h * scale)), int(round(w * scale))
best = None
score = None
for i in range(k):
    m = cv2.GaussianBlur((lbl == i).astype(np.float32), (0, 0), 0.75)
    up = cv2.resize(m, (ow * S, oh * S), interpolation=cv2.INTER_CUBIC)
    if score is None:
        score, best = up, np.zeros(up.shape, np.int32)
    else:
        better = up > score
        score = np.where(better, up, score)
        best = np.where(better, i, best)
hi = pal[best]
out = cv2.resize(hi, (ow, oh), interpolation=cv2.INTER_AREA)
cv2.imwrite(dst, np.clip(out, 0, 255).astype(np.uint8))
print(f"{src} {w}x{h} -> {ow}x{oh}, {k} inks")
