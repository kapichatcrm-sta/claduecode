"""Original BGM for the CONECTANDOSTUDIO reveal (v2) — Mediterranean deep house, 120 BPM, D minor.

Fully synthesized and seeded: royalty-free by construction, identical on every run.
v2 replaces the single four-chord loop of v1 with a track that develops section by section:
a plucked nylon-string hook (Karplus-Strong) with a dotted-eighth delay, a felt-piano break,
different progressions per section, fills, a full stop before the second drop, a brighter
drop B (ride, bongos, octave lead, "ooh" pad), and a finale with a faster harmonic rhythm.

Landmarks the edit is cut to (bar = 2.0 s):
  1-2    intro      felt piano + pad opening, hook hinted; reverse swell into bar 3
  3-6    drop A     kick, sub bass, claps, pluck hook A with delay
  7-10   groove A2  + kalimba 16th arpeggio, congas, walking bass; tom fill into bar 11
  11-12  break      no kick: piano chords (new progression), hook on piano; riser + roll; STOP
  13-16  drop B     new progression, octave lead hook B, ride, bongos, tambourine, "ooh" pad
  17-20  groove A3  stripped (rim), hook answers in a flute-like lead; snare build in bar 20
  21-22  finale     two chords per bar, hook resolves; band pickup on bar 22 beat 4
  23     final hit  D minor(add9) tutti + ring-out (the last golpe, 44.0 s)

Usage: python3 -I tools/compose_bgm.py out.wav
"""
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, lfilter, sosfilt

SR = 44100
BPM = 120.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
SWING = 0.56
FINAL_BAR = 23
TAIL = 1.6
DUR = (FINAL_BAR - 1) * BAR + TAIL
N = int(DUR * SR)
rng = np.random.default_rng(1112)

BUS = {k: np.zeros((2, N)) for k in ("drums", "bass", "keys", "lead", "fx")}
SEND = np.zeros(N)  # reverb send
DLY = np.zeros(N)  # dotted-eighth delay send (lead)


def t_of(bar, beat=0.0, s16=0):
    return (bar - 1) * BAR + beat * BEAT + {0: 0.0, 1: SWING * 0.5, 2: 0.5, 3: 0.5 + SWING * 0.5}[s16] * BEAT


def add(bus, sig, t, gain=1.0, pan=0.0, verb=0.0, delay=0.0):
    i = int(round(t * SR))
    if i >= N or i < 0:
        return
    sig = sig[: N - i] * gain
    BUS[bus][0, i : i + len(sig)] += sig * np.cos((pan + 1) * np.pi / 4)
    BUS[bus][1, i : i + len(sig)] += sig * np.sin((pan + 1) * np.pi / 4)
    if verb:
        SEND[i : i + len(sig)] += sig * verb
    if delay:
        DLY[i : i + len(sig)] += sig * delay


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def env(n, a, d):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    k = int(a * SR)
    if k:
        e[:k] *= np.linspace(0, 1, k)
    return e


def gate(n, dur, rel=0.05):
    g = np.ones(n)
    s, r = int(dur * SR), int(rel * SR)
    if s < n:
        g[s : s + r] = np.linspace(1, 0, min(r, n - s))
        g[s + r :] = 0
    return g


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def noise(n):
    return rng.standard_normal(n)


# ====================================================================== instruments
def kick(s=1.0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t / 0.025) + 25 * np.exp(-t / 0.12)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.0008, 0.22)
    click = filt(noise(n), "band", [2500, 9000]) * env(n, 0, 0.0025) * 0.5
    return np.tanh(1.8 * (body + click)) * s


def clap(s=1.0):
    n = int(0.5 * SR)
    out = np.zeros(n)
    for k, off in enumerate((0.0, 0.007, 0.015, 0.024)):
        i = int(off * SR)
        out[i:] += noise(n - i) * env(n - i, 0.0004, 0.009 if k < 3 else 0.16)
    return filt(out, "band", [900, 7000]) * s


def snare(s=1.0):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (180 + 60 * np.exp(-t / 0.01)) * t) * env(n, 0.001, 0.05)
    return (0.5 * body + filt(noise(n), "band", [1800, 9000]) * env(n, 0.001, 0.11)) * s


def rim(s=1.0):
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1700 * t) * 0.6 + filt(noise(n), "band", [1500, 4500]) * 0.5) * env(n, 0.0005, 0.011) * s


def hat(open_=False, s=1.0):
    n = int((0.32 if open_ else 0.06) * SR)
    return filt(noise(n), "high", 8000, 3) * env(n, 0.0005, 0.1 if open_ else 0.013) * s


def shaker(s=1.0):
    n = int(0.08 * SR)
    return filt(noise(n), "high", 6500) * env(n, 0.008, 0.02) * s


def tamb(s=1.0):
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    j = sum(np.sin(2 * np.pi * f * t + p) for f, p in ((5300, 0), (7200, 1), (9100, 2)))
    return (filt(noise(n), "high", 5000) * 0.8 + 0.2 * j) * env(n, 0.002, 0.045) * s


def ride(s=1.0):
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t) for f in (3120, 4370, 5233, 6780, 8110)) / 5
    x += filt(noise(n), "high", 7000) * 0.5
    return x * (env(n, 0.001, 0.35) * 0.7 + env(n, 0, 0.02) * 0.6) * s


def drum_tom(m, s=1.0):
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    f = mtof(m) * (1 + 0.35 * np.exp(-t / 0.03))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.18) * s


def conga(m, s=1.0):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    f = mtof(m) * (1 + 0.25 * np.exp(-t / 0.01))
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.13) + filt(noise(n), "band", [800, 3000]) * env(n, 0, 0.005) * 0.4) * s


def crash(s=1.0, length=2.8):
    n = int(length * SR)
    t = np.arange(n) / SR
    x = filt(noise(n), "high", 4000) + sum(np.sin(2 * np.pi * f * t) for f in (3300, 4700, 6100)) * 0.05
    return x * env(n, 0.002, 0.8) * s


def impact(s=1.0):
    n = int(2.0 * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (38 + 40 * np.exp(-t / 0.08)) * t) * env(n, 0.002, 0.7)
    return (np.tanh(1.5 * boom) + filt(noise(n), "low", 1200) * env(n, 0, 0.15) * 0.4) * s


def riser(length, s=1.0):
    n = int(length * SR)
    x, out, seg = noise(n), np.zeros(n), n // 24
    for k in range(24):
        a, b = k * seg, (k + 1) * seg if k < 23 else n
        lo = 300 + 8000 * (k / 23) ** 2
        out[a:b] = filt(x[a:b], "band", [lo, min(lo * 2.0, 19000)])
    t = np.arange(n) / SR
    sweep = np.sin(2 * np.pi * np.cumsum(200 + 1600 * (t / t[-1]) ** 2) / SR) * 0.15
    return (out + sweep) * np.linspace(0, 1, n) ** 2.4 * s


def reverse_swell(notes, length=1.6, s=1.0):
    x = piano(notes, length, 0.9)[: int(length * SR)]
    return x[::-1] * np.linspace(0, 1, len(x)) ** 1.5 * s


# ---------------------------------------------------------------------- tonal
def pluck(m, dur=0.9, bright=0.6, s=1.0):
    """Karplus-Strong nylon string."""
    n = int((dur + 0.4) * SR)
    f = mtof(m)
    P = max(2, int(round(SR / f)))
    exc = np.zeros(n)
    burst = filt(noise(P), "low", 1500 + 7000 * bright)
    exc[:P] = burst
    g = 0.996 - 0.0006 * max(0, m - 60)
    a = np.zeros(P + 2)
    a[0], a[P], a[P + 1] = 1.0, -g * 0.5, -g * 0.5
    y = lfilter([1.0], a, exc)
    y = filt(y, "high", 80) * gate(n, dur, 0.12)
    return y / (np.max(np.abs(y)) + 1e-9) * s


def piano(notes, dur, s=1.0, soft=0.0):
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m in notes:
        f = mtof(m)
        x = np.zeros(n)
        for h in range(1, 9):
            fh = f * h * np.sqrt(1 + 0.0004 * h * h)
            if fh > 9000:
                break
            x += (0.75 ** (h - 1)) * np.sin(2 * np.pi * fh * t + h) * np.exp(-t * (0.6 + 0.9 * h) / 1.5)
        x += filt(noise(n), "band", [800, 3000]) * env(n, 0, 0.004) * 0.08
        out += x
    out /= max(1, len(notes)) ** 0.6
    return filt(out * env(n, 0.002, 2.5) * gate(n, dur, 0.4), "low", 4200 - 2400 * soft) * s


def bass(m, dur, s=1.0, bright=0.0):
    n = int((dur + 0.1) * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    sub = np.sin(2 * np.pi * f * t)
    mid = filt(np.sign(np.sin(2 * np.pi * f * t)) * 0.4 + np.sin(2 * np.pi * 2 * f * t) * 0.3, "low", 500 + 900 * bright)
    return np.tanh(1.3 * (sub + mid)) * env(n, 0.003, 0.4) * gate(n, dur) * s


def stab(notes, dur=0.18, s=1.0):
    n = int((dur + 0.3) * SR)
    t = np.arange(n) / SR
    x = sum(sum(a * np.sin(2 * np.pi * mtof(m) * h * t) for h, a in ((1, 1), (2, 0.45), (3, 0.25), (4, 0.12))) for m in notes) / len(notes)
    cut = 900 + 3200 * np.exp(-t / 0.06)
    y = np.zeros(n)
    blk = 512
    for i in range(0, n, blk):
        y[i : i + blk] = filt(x[i : i + blk], "low", cut[i])
    return y * env(n, 0.002, 0.2) * gate(n, dur, 0.08) * s


def pad(notes, dur, bright=0.7, s=1.0, ooh=False):
    n = int((dur + 1.0) * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for m in notes:
        for det in (-0.11, -0.04, 0.0, 0.05, 0.12):
            f = mtof(m + det)
            x += sum(np.sin(2 * np.pi * f * h * t + h * 0.7 + det * 30) / h for h in range(1, 8))
    x /= len(notes) * 5
    if ooh:  # vowel-ish formants
        x = filt(x, "band", [300, 900]) * 1.6 + filt(x, "band", [2000, 3000]) * 0.4
    e = np.minimum(1, t / 0.5) * gate(n, dur, 0.9)
    return filt(x * e, "low", 400 + 3000 * bright) * s


def kalimba(m, s=1.0):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    x = np.sin(2 * np.pi * f * t) * env(n, 0.001, 0.35) + 0.35 * np.sin(2 * np.pi * 5.4 * f * t) * env(n, 0, 0.04)
    return x * s


def flute(m, dur, s=1.0):
    n = int((dur + 0.2) * SR)
    t = np.arange(n) / SR
    f = mtof(m) * (1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.3))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.18 * np.sin(2 * ph) + filt(noise(n), "band", [mtof(m), mtof(m) * 3]) * 0.06
    return x * np.minimum(1, t / 0.05) * gate(n, dur, 0.12) * s


# ====================================================================== harmony & lines
CH = {
    "Dm9": (38, [53, 57, 60, 64]),
    "Bbmaj9": (34, [50, 53, 57, 60]),
    "Gm9": (31, [53, 57, 58, 62]),
    "A7sus": (33, [55, 57, 62, 64]),
    "A7": (33, [55, 61, 64, 67]),
    "Fmaj7": (41, [57, 60, 64, 65]),
    "Cadd9": (36, [55, 60, 62, 64]),
    "Am7": (33, [55, 60, 64, 67]),
    "Dfinal": (38, [57, 62, 64, 65, 69]),
}
PROG = {}
for b in range(3, 11):
    PROG[b] = [("Dm9", "Bbmaj9", "Gm9", "A7sus")[(b - 3) % 4]]
PROG[1], PROG[2] = ["Dm9"], ["Bbmaj9"]
PROG[11], PROG[12] = ["Bbmaj9"], ["Cadd9", "A7"]
for b in range(13, 17):
    PROG[b] = [("Dm9", "Fmaj7", "Cadd9", "Bbmaj9")[(b - 13) % 4]]
for b in range(17, 21):
    PROG[b] = [("Dm9", "Bbmaj9", "Gm9", "A7")[(b - 17) % 4]]
PROG[21], PROG[22] = ["Dm9", "Bbmaj9"], ["Gm9", "A7"]

HOOK_A = {  # bar-in-phrase -> [(beat, midi, dur_beats)]
    0: [(0.5, 69, 0.5), (1.0, 72, 0.5), (1.5, 74, 1.0), (2.5, 77, 0.5), (3.0, 76, 0.5), (3.5, 74, 0.5)],
    1: [(0.5, 72, 0.5), (1.0, 69, 1.0), (2.0, 67, 0.5), (2.5, 69, 1.5)],
    2: [(0.5, 70, 0.5), (1.0, 74, 0.5), (1.5, 77, 1.0), (2.5, 76, 0.5), (3.0, 74, 0.5), (3.5, 73, 0.5)],
    3: [(0.5, 76, 1.0), (2.0, 69, 1.5)],
}
HOOK_B = {
    0: [(0, 74, 0.75), (0.75, 77, 0.75), (1.5, 81, 1.0), (2.5, 79, 0.5), (3.0, 77, 1.0)],
    1: [(0, 76, 0.75), (0.75, 77, 0.75), (1.5, 79, 1.0), (2.5, 81, 0.5), (3.0, 84, 1.0)],
    2: [(0, 79, 1.0), (1.0, 76, 1.0), (2.0, 74, 0.5), (2.5, 76, 0.5), (3.0, 79, 1.0)],
    3: [(0, 77, 1.0), (1.0, 74, 1.0), (2.0, 72, 0.5), (2.5, 74, 0.5), (3.0, 77, 1.0)],
}
FINALE = {
    21: [(0, 81, 1.0), (1.0, 79, 0.5), (1.5, 77, 0.5), (2.0, 76, 1.0), (3.0, 74, 1.0)],
    22: [(0, 77, 1.0), (1.0, 76, 1.0), (2.0, 73, 0.5), (2.5, 76, 0.5), (3.0, 81, 1.0)],
}

kicks = []


def chords_of(bar):
    names = PROG[bar]
    per = 4 / len(names)
    return [(i * per, per, CH[nm]) for i, nm in enumerate(names)]


for bar in range(1, FINAL_BAR):
    sec = (
        "intro" if bar <= 2 else
        "A" if bar <= 6 else
        "A2" if bar <= 10 else
        "break" if bar <= 12 else
        "B" if bar <= 16 else
        "A3" if bar <= 20 else
        "fin"
    )
    chs = chords_of(bar)

    # -------------------------------------------------- harmony beds
    for beat, ln, (root, voic) in chs:
        t = t_of(bar, beat)
        if sec in ("intro", "break"):
            add("keys", piano(voic, ln * BEAT * 0.98, 0.9, soft=0.25 if sec == "intro" else 0.2), t, 0.55, -0.1, 0.45)
            add("keys", pad(voic, ln * BEAT, 0.25 if sec == "intro" else 0.5), t, 0.5 if sec == "intro" else 0.4, 0.0, 0.3)
        elif sec == "B":
            add("keys", pad([v + 12 for v in voic[:3]], ln * BEAT, 0.5, ooh=True), t, 0.5, 0.0, 0.4)
            add("keys", pad(voic, ln * BEAT, 0.9), t, 0.35, 0.0, 0.3)
        elif sec == "fin":
            add("keys", pad(voic, ln * BEAT, 1.0), t, 0.45, 0.0, 0.3)
            add("keys", pad([v + 12 for v in voic[:3]], ln * BEAT, 0.6, ooh=True), t, 0.35, 0.0, 0.4)
        else:
            add("keys", pad(voic, ln * BEAT, 0.6 if sec != "A3" else 0.45), t, 0.32, 0.0, 0.3)

    # -------------------------------------------------- off-beat stabs
    if sec in ("A", "A2", "B", "A3", "fin"):
        for beat in (0.75, 1.5, 2.75, 3.5):
            _, _, (root, voic) = [c for c in chs if c[0] <= beat][-1]
            add("keys", stab([v + 12 for v in voic], 0.16), t_of(bar, beat), 0.5 if sec != "A3" else 0.38, 0.15, 0.35)

    # -------------------------------------------------- bass
    for beat0, ln, (root, voic) in chs:
        if sec == "intro":
            continue
        if sec == "break":
            add("bass", bass(root, ln * BEAT * 0.95, 0.7), t_of(bar, beat0), 0.7)
            continue
        if sec in ("A", "A3"):
            pat = [(0.5, 0, 0.4), (1.5, 0, 0.4), (1.75, 12, 0.2), (2.5, 0, 0.4), (3.25, 7, 0.25), (3.5, 0, 0.4)]
        elif sec == "A2":
            pat = [(0, 0, 0.25), (0.5, 0, 0.4), (1.5, 12, 0.3), (2.0, 7, 0.3), (2.5, 0, 0.4), (3.0, 10, 0.3), (3.5, 12, 0.4)]
        else:  # B / finale: driving eighths with octave jumps
            pat = [(k * 0.5, 12 if k % 2 else 0, 0.42) for k in range(8)]
        for beat, iv, l in pat:
            if beat0 <= beat < beat0 + ln:
                add("bass", bass(root + iv, l * BEAT * 2, 0.75, bright=0.6 if sec in ("B", "fin") else 0.2), t_of(bar, beat), 0.8)

    # -------------------------------------------------- lead lines
    if sec in ("intro",) and bar == 2:
        for beat, m, d in HOOK_A[0][:4]:
            add("lead", pluck(m, d * BEAT, 0.3), t_of(bar, beat), 0.32, 0.2, 0.4, 0.25)
    if sec in ("A", "A2"):
        phrase = HOOK_A[(bar - 3) % 4]
        for beat, m, d in phrase:
            add("lead", pluck(m, d * BEAT + 0.2, 0.55 if sec == "A" else 0.7), t_of(bar, beat), 0.5, 0.15, 0.3, 0.35)
    if sec == "A2":  # kalimba 16th arpeggio counter-line
        _, _, (root, voic) = chs[0]
        arp = [voic[0] + 12, voic[2] + 12, voic[1] + 12, voic[3] + 12]
        for k in range(16):
            add("lead", kalimba(arp[k % 4] + (12 if k % 8 == 7 else 0)), t_of(bar, k // 4, k % 4), 0.16, -0.45, 0.25)
    if sec == "break":
        phrase = HOOK_A[(bar - 11) % 4]
        for beat, m, d in phrase:
            add("lead", piano([m + 12], d * BEAT + 0.4, 0.8, soft=0.1), t_of(bar, beat), 0.38, 0.2, 0.6)
    if sec == "B":
        phrase = HOOK_B[(bar - 13) % 4]
        for beat, m, d in phrase:
            add("lead", pluck(m, d * BEAT + 0.15, 0.85), t_of(bar, beat), 0.5, 0.2, 0.3, 0.4)
            add("lead", pluck(m - 12, d * BEAT + 0.15, 0.6), t_of(bar, beat), 0.3, -0.2, 0.2, 0.2)
    if sec == "A3" and bar >= 19:
        for beat, m, d in HOOK_A[(bar - 17) % 4]:
            add("lead", flute(m + 12, d * BEAT * 0.9), t_of(bar, beat), 0.22, 0.25, 0.45, 0.3)
    if sec == "fin":
        for beat, m, d in FINALE[bar]:
            add("lead", pluck(m, d * BEAT + 0.2, 0.9), t_of(bar, beat), 0.5, 0.2, 0.35, 0.35)
            add("lead", flute(m, d * BEAT * 0.95), t_of(bar, beat), 0.18, -0.2, 0.4)

    # -------------------------------------------------- drums
    four = sec in ("A", "A2", "B", "A3", "fin")
    if four:
        for b in range(4):
            add("drums", kick(), t_of(bar, b), 0.85)
            kicks.append(t_of(bar, b))
    for b in (1, 3):
        if sec == "intro":
            if bar == 2:
                add("drums", rim(0.7), t_of(bar, b), 0.3, 0.2, 0.2)
        elif sec == "break":
            add("drums", clap(0.8), t_of(bar, b), 0.3, 0.0, 0.6)
        elif sec == "A3" and bar <= 18:
            add("drums", rim(0.9), t_of(bar, b), 0.4, 0.15, 0.2)
        else:
            add("drums", clap(), t_of(bar, b), 0.45, 0.05, 0.3)
            if sec in ("B", "fin"):
                add("drums", snare(0.8), t_of(bar, b), 0.3, -0.05, 0.15)
    for b in range(4):
        for s16 in range(4):
            if sec != "intro" or bar == 2:
                add("drums", shaker(1.0 if s16 == 2 else 0.45), t_of(bar, b, s16), 0.17 if sec != "break" else 0.1, 0.4)
        if four:
            add("drums", hat(True, 0.9), t_of(bar, b, 2), 0.3 if sec not in ("B", "fin") else 0.36, -0.3)
            if sec in ("B", "fin"):
                add("drums", ride(0.8), t_of(bar, b, 2), 0.16, 0.35)
                for s16 in range(4):
                    add("drums", tamb(1.0 if s16 % 2 else 0.5), t_of(bar, b, s16), 0.12, 0.55)
    if sec == "A2" or sec in ("B", "fin"):
        for b, s16, m in ((0, 3, 62), (1, 2, 67), (2, 3, 62), (3, 1, 67), (3, 3, 70)):
            add("drums", conga(m + (5 if sec != "A2" else 0)), t_of(bar, b, s16), 0.3, -0.45)
    if bar in (3, 13, 15, 21):
        add("drums", crash(), t_of(bar), 0.26, 0.3, 0.25)
    if bar in (3, 13, 21):
        add("fx", impact(), t_of(bar), 0.55, 0.0, 0.2)

# -------------------------------------------------- transitions & fills
add("fx", reverse_swell(CH["Dm9"][1], 1.6), t_of(3) - 1.6, 0.45, 0.0, 0.3)
for k, m in enumerate((50, 47, 43, 40)):  # tom fill into the break
    add("drums", drum_tom(m), t_of(10, 3, k), 0.55, 0.3 - 0.2 * k)
add("fx", riser(BAR * 1.75), t_of(11, 1), 0.3, 0.0, 0.3)
for k in range(12):  # snare roll, accelerating, bar 12 beats 1-3.75
    add("drums", snare(0.35 + 0.05 * k), t_of(12, 1) + k * (2.5 * BEAT / 12), 0.35, 0.0, 0.2)
add("fx", riser(BAR), t_of(20), 0.25, 0.0, 0.3)
for k in range(16):  # bar 20: 16th snare build
    add("drums", snare(0.25 + 0.045 * k), t_of(20, k // 4, k % 4), 0.3, 0.0, 0.15)
for s in (0, 2):  # band pickup before the final hit
    add("drums", kick(0.95), t_of(22, 3, s), 0.85)
    add("drums", clap(1.0), t_of(22, 3, s), 0.45, 0.0, 0.3)
    add("keys", stab([v + 12 for v in CH["A7"][1]], 0.15), t_of(22, 3, s), 0.6, 0.0, 0.3)
    add("bass", bass(33 + (0 if s == 0 else 4), 0.2), t_of(22, 3, s), 0.8)

# -------------------------------------------------- final hit (bar 23)
root, voic = CH["Dfinal"]
tF = t_of(FINAL_BAR)
add("drums", kick(1.2), tF, 1.0)
kicks.append(tF)
add("drums", crash(1.0, 3.2), tF, 0.3, -0.2, 0.35)
add("drums", clap(1.0), tF, 0.45, 0.0, 0.5)
add("fx", impact(1.0), tF, 0.6, 0.0, 0.3)
add("bass", bass(root, 1.3, 1.0), tF, 0.9)
add("keys", piano(voic, 1.4, 1.0), tF, 0.6, 0.0, 0.5)
add("keys", pad(voic, 1.0, 0.9), tF, 0.4, 0.0, 0.5)
for k, m in enumerate((74, 81, 86)):
    add("lead", pluck(m, 1.3, 0.9), tF + k * 0.025, 0.4, (-0.3, 0.0, 0.3)[k], 0.5, 0.3)

# ====================================================================== mix
# sidechain pump on everything tonal
duck = np.ones(N)
for kt in kicks:
    i = int(kt * SR)
    m = min(N - i, int(0.4 * SR))
    duck[i : i + m] = np.minimum(duck[i : i + m], 1 - 0.5 * np.exp(-np.arange(m) / SR / 0.1))
for k in ("bass", "keys", "lead"):
    BUS[k] *= duck

# dotted-eighth ping-pong delay (lead)
d = int(0.75 * BEAT * SR)
fb = 0.38
dl = np.zeros(N)
dr = np.zeros(N)
src = filt(DLY, "band", [400, 6000])
for k in range(1, 6):
    sh = k * d
    if sh >= N:
        break
    seg = src[: N - sh] * fb ** (k - 1) * 0.6
    (dl if k % 2 else dr)[sh:] += seg

# hall reverb
ir_n = int(2.6 * SR)
tt = np.arange(ir_n) / SR
irs = []
for off in (0.021, 0.027):
    ir = filt(noise(ir_n) * np.exp(-tt / 0.6), "low", 6000)
    ir[: int(off * SR)] = 0
    irs.append(ir / np.sqrt((ir**2).sum()))
wet = np.stack([fftconvolve(SEND, irs[0])[:N], fftconvolve(SEND, irs[1])[:N]]) * 0.55

mix = BUS["drums"] * 1.0 + BUS["bass"] * 0.95 + BUS["keys"] * 1.0 + BUS["lead"] * 1.05 + BUS["fx"] * 0.9 + wet + np.stack([dl, dr])

# macro dynamics: an arc across the sections (gain at each bar start, linear inside the bar)
ARC = {1: 0.95, 2: 0.85, 3: 0.72, 7: 0.8, 10: 0.9, 11: 0.78, 13: 1.0, 17: 0.68, 19: 0.75, 20: 0.85, 21: 1.0, 23: 1.0}
gains = []
cur = 0.75
for bar in range(1, FINAL_BAR + 2):
    cur = ARC.get(bar, cur)
    gains.append(cur)
nodes_t = [(b - 1) * BAR for b in range(1, FINAL_BAR + 2)]
curve = np.interp(np.arange(N) / SR, nodes_t, gains)
# hold each bar's level (no slow drift across drops): step at the downbeat with a 40 ms glide
step = np.repeat(gains, int(BAR * SR))[:N]
if len(step) < N:
    step = np.pad(step, (0, N - len(step)), mode="edge")
glide = int(0.04 * SR)
step = np.convolve(step, np.ones(glide) / glide, mode="same")
# bars 7-10 and 19-20 build inside the section instead of stepping
build = (np.arange(N) / SR >= t_of(7)) & (np.arange(N) / SR < t_of(11)) | (np.arange(N) / SR >= t_of(19)) & (np.arange(N) / SR < t_of(21))
mix *= np.where(build, curve, step)

# the stop: a beat of silence before drop B (bar 12, beat 3.5 -> 4)
s0, s1 = int(t_of(12, 3.5) * SR), int(t_of(13) * SR)
fade = int(0.01 * SR)
mix[:, s0 : s0 + fade] *= np.linspace(1, 0, fade)
mix[:, s0 + fade : s1] = 0

mix = filt(mix, "high", 28)
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(1.25 * mix) / np.tanh(1.25)
fo = int(0.45 * SR)
mix[:, -fo:] *= np.linspace(1, 0, fo) ** 2
mix *= 10 ** (-1.0 / 20) / np.max(np.abs(mix))
out = sys.argv[1] if len(sys.argv) > 1 else "bgm.wav"
sf.write(out, mix.T, SR, subtype="PCM_24")
print(f"wrote {out}: {DUR:.3f}s, {BPM:.0f} BPM, final hit at {tF:.3f}s")
