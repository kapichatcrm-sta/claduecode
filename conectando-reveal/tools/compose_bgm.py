"""Original BGM for the CONECTANDOSTUDIO reveal — Mediterranean deep house, 120 BPM, D minor.

Fully synthesized (no samples), so it is royalty-free by construction, and seeded, so the same
script always writes the same file.

Arrangement (bars of 4/4, 1 bar = 2.0 s):
  1-2    intro      filtered pad opening, shaker, rim; reverse-cymbal riser into bar 3
  3-6    groove A   four-on-the-floor kick, claps, off-beat hats, bass, chord stabs (drop 1)
  7-10   groove A+  kalimba hook + congas join
  11-12  break      no kick: pad, hook, held bass; riser + snare roll into bar 13
  13-16  drop B     everything, hook an octave up, crash on 13
  17-20  groove A   lighter, hook returns on 19
  21-22  build      full band, crash on 21, band pickup on bar 22 beat 4
  23     final hit  beat 1 tutti + reverb ring-out (the last golpe)

Usage: python3 -I tools/compose_bgm.py out.wav
"""
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

SR = 44100
BPM = 120.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
SWING = 0.54
FINAL_BAR = 23
TAIL = 1.6
DUR = (FINAL_BAR - 1) * BAR + TAIL
N = int(DUR * SR)
rng = np.random.default_rng(2024)

drums = np.zeros((2, N))
music = np.zeros((2, N))  # sidechained to the kick
send = np.zeros(N)


def t_of(bar, beat=0.0, s16=0):
    base = (bar - 1) * BAR + beat * BEAT
    return base + {0: 0.0, 1: SWING * 0.5, 2: 0.5, 3: 0.5 + SWING * 0.5}[s16] * BEAT


def add(bus, sig, t, gain=1.0, pan=0.0, verb=0.0):
    i = int(round(t * SR))
    if i >= N:
        return
    sig = sig[: N - i]
    bus[0, i : i + len(sig)] += sig * gain * np.cos((pan + 1) * np.pi / 4)
    bus[1, i : i + len(sig)] += sig * gain * np.sin((pan + 1) * np.pi / 4)
    if verb:
        send[i : i + len(sig)] += sig * gain * verb


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
    s = int(dur * SR)
    r = int(rel * SR)
    if s < n:
        g[s : s + r] = np.linspace(1, 0, min(r, n - s))
        g[s + r :] = 0
    return g


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------ drums
def kick(s=1.0):
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    f = 46 + 80 * np.exp(-t / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.2)
    click = filt(rng.standard_normal(n), "high", 3000) * env(n, 0, 0.003) * 0.3
    return np.tanh(1.5 * (body + click)) * s


def clap(s=1.0):
    n = int(0.45 * SR)
    out = np.zeros(n)
    for k, off in enumerate((0.0, 0.008, 0.017, 0.027)):
        i = int(off * SR)
        out[i:] += rng.standard_normal(n - i) * env(n - i, 0.0005, 0.01 if k < 3 else 0.14)
    return filt(out, "band", [1000, 6000]) * s


def rim(s=1.0):
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 1750 * t) * 0.6 + filt(rng.standard_normal(n), "band", [1500, 4000]) * 0.5
    return x * env(n, 0.0005, 0.012) * s


def hat(open_=False, s=1.0):
    n = int((0.3 if open_ else 0.06) * SR)
    return filt(rng.standard_normal(n), "high", 8000, 3) * env(n, 0.0005, 0.09 if open_ else 0.014) * s


def shaker(s=1.0):
    n = int(0.08 * SR)
    return filt(rng.standard_normal(n), "high", 6500) * env(n, 0.008, 0.02) * s


def conga(m, s=1.0):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    f = mtof(m) * (1 + 0.25 * np.exp(-t / 0.01))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.14) + filt(rng.standard_normal(n), "band", [800, 3000]) * env(n, 0, 0.006) * 0.4
    return x * s


def crash(s=1.0, length=2.6):
    n = int(length * SR)
    t = np.arange(n) / SR
    x = filt(rng.standard_normal(n), "high", 4000) + sum(np.sin(2 * np.pi * f * t) for f in (3300, 4700, 6100)) * 0.04
    return x * env(n, 0.002, 0.7) * s


def riser(length, s=1.0):
    n = int(length * SR)
    t = np.linspace(0, 1, n)
    x = rng.standard_normal(n)
    out = np.zeros(n)
    seg = n // 16
    for k in range(16):
        a, b = k * seg, (k + 1) * seg if k < 15 else n
        lo = 400 + 7000 * (k / 15) ** 2
        out[a:b] = filt(x[a:b], "band", [lo, min(lo * 2.2, 18000)])
    return out * t**2.2 * s


# ------------------------------------------------------------------ tonal
def bass(m, dur, s=1.0):
    n = int((dur + 0.1) * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sign(np.sin(2 * np.pi * f * t))
    return filt(np.tanh(1.4 * x) * env(n, 0.004, 0.35) * gate(n, dur), "low", 900) * s


def organ_stab(notes, dur=0.16, s=1.0):
    n = int((dur + 0.3) * SR)
    t = np.arange(n) / SR
    x = sum(sum(a * np.sin(2 * np.pi * mtof(m) * h * t) for h, a in ((1, 1), (2, 0.5), (3, 0.28), (4, 0.15))) for m in notes)
    x = x / len(notes)
    return filt(x * env(n, 0.003, 0.22) * gate(n, dur, 0.08), "low", 2600) * s


def pad(notes, dur, bright=1.0, s=1.0):
    n = int((dur + 0.8) * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for m in notes:
        for det in (-0.07, 0.0, 0.07):
            f = mtof(m + det)
            x += sum(np.sin(2 * np.pi * f * h * t + h) / h for h in range(1, 7))
    x /= len(notes) * 3
    e = np.minimum(1, t / 0.6) * gate(n, dur, 0.7)
    return filt(x * e, "low", 500 + 2200 * bright) * s


def kalimba(m, s=1.0):
    n = int(1.1 * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    x = np.sin(2 * np.pi * f * t) * env(n, 0.001, 0.45) + 0.4 * np.sin(2 * np.pi * 5.4 * f * t) * env(n, 0, 0.05)
    x += filt(rng.standard_normal(n), "high", 3000) * env(n, 0, 0.003) * 0.15
    return x * s


# ------------------------------------------------------------------ harmony
CH = {
    "Dm9": (38, [53, 57, 60, 64]),  # F A C E over D
    "Bbmaj7": (34, [53, 57, 58, 62]),
    "Gm9": (31, [53, 57, 58, 62]),
    "A7sus": (33, [52, 55, 57, 62]),
    "Dfinal": (38, [50, 57, 60, 64, 69]),
}
CYCLE = ["Dm9", "Bbmaj7", "Gm9", "A7sus"]
HOOK = [(0, 2, 69), (0, 3.5, 72), (1, 1, 74), (1, 2.5, 72), (1, 3, 69), (2, 1.5, 77), (2, 3, 76), (3, 0.5, 74), (3, 2, 72)]
BASS_PAT = [(0.5, 0, 0.22), (1.5, 0, 0.22), (1.75, 12, 0.12), (2.5, 0, 0.22), (3.25, 7, 0.15), (3.5, 0, 0.22)]

kicks = []
for bar in range(1, FINAL_BAR + 1):
    name = "Dfinal" if bar == FINAL_BAR else CYCLE[(bar - 1) % 4]
    root, voic = CH[name]
    intro = bar <= 2
    brk = bar in (11, 12)
    drop = 13 <= bar <= 16 or bar in (21, 22)
    hook_on = 7 <= bar <= 16 or bar >= 19

    if bar == FINAL_BAR:
        add(drums, kick(1.2), t_of(bar), 1.0)
        kicks.append(t_of(bar))
        add(drums, crash(1.0, 3.0), t_of(bar), 0.3, -0.2, 0.3)
        add(drums, clap(1.0), t_of(bar), 0.45, 0.0, 0.5)
        add(music, bass(root, 1.2), t_of(bar), 0.9)
        add(music, pad(voic, 1.0, 1.0), t_of(bar), 0.5, 0.0, 0.4)
        add(music, organ_stab(voic, 0.5), t_of(bar), 0.55, 0.0, 0.5)
        for k, m in enumerate((74, 77, 81)):
            add(music, kalimba(m), t_of(bar) + k * 0.03, 0.35, (-0.3, 0.0, 0.3)[k], 0.5)
        continue

    # ---- pad (intro opens the filter)
    bright = {1: 0.05, 2: 0.4}.get(bar, 0.9 if not brk else 0.6)
    add(music, pad(voic, BAR * 0.98, bright), t_of(bar), 0.85 if not intro else 1.1, 0.0, 0.3)

    # ---- kick / clap
    if not (intro or brk):
        for b in range(4):
            add(drums, kick(), t_of(bar, b), 0.78)
            kicks.append(t_of(bar, b))
    for b in (1, 3):
        if not intro:
            add(drums, clap(), t_of(bar, b), 0.42 if not brk else 0.3, 0.05, 0.3)
        else:
            add(drums, rim(0.8), t_of(bar, b), 0.35, 0.2, 0.2)

    # ---- hats / shaker / rim
    for b in range(4):
        for s16 in range(4):
            add(drums, shaker(1.0 if s16 == 2 else 0.5), t_of(bar, b, s16), 0.2 if not intro else 0.14, 0.4)
        if not (intro or brk):
            add(drums, hat(True, 0.9), t_of(bar, b, 2), 0.34, -0.3)
    if not intro and not brk:
        add(drums, rim(0.7), t_of(bar, 1, 3), 0.25, 0.3, 0.2)
        add(drums, rim(0.6), t_of(bar, 3, 1), 0.22, 0.3, 0.2)

    # ---- congas (groove A+ / drop)
    if (7 <= bar <= 10) or drop:
        for b, s16, m in ((0, 3, 62), (1, 2, 67), (2, 3, 62), (3, 1, 67), (3, 3, 70)):
            add(drums, conga(m), t_of(bar, b, s16), 0.32, -0.45)

    # ---- bass
    if not intro:
        if brk:
            add(music, bass(root, BAR * 0.9, 0.9), t_of(bar), 0.7)
        else:
            for beat, iv, ln in BASS_PAT:
                add(music, bass(root + iv, ln * 2), t_of(bar, beat), 0.62)

    # ---- organ stabs on the off-beats
    if not intro and not brk:
        for beat in (0.75, 1.5, 2.75, 3.5):
            add(music, organ_stab([v + 12 for v in voic]), t_of(bar, beat), 0.62, 0.15, 0.35)

    # ---- kalimba hook
    if hook_on or intro:
        oct_ = 12 if drop else 0
        for b_off, beat, m in HOOK:
            if b_off == (bar - 1) % 4 and (not intro or beat >= 2):
                add(music, kalimba(m + oct_), t_of(bar, beat), 0.6 if not intro else 0.4, 0.25, 0.45)

    # ---- crashes on the structural downbeats
    if bar in (3, 13, 21):
        add(drums, crash(), t_of(bar), 0.24, 0.3, 0.2)

# risers + fills
add(drums, riser(BAR), t_of(2), 0.18, 0.0, 0.3)
add(drums, riser(BAR), t_of(12), 0.22, 0.0, 0.3)
for k in range(8):
    add(drums, clap(0.4 + 0.08 * k), t_of(12, 2 + k * 0.25), 0.3, 0.0, 0.2)
for s in (0, 2):  # band pickup before the final hit
    add(drums, kick(0.9), t_of(22, 3, s), 0.8)
    add(drums, clap(1.0), t_of(22, 3, s), 0.4, 0.0, 0.3)
    add(music, organ_stab([v + 12 for v in CH["A7sus"][1]], 0.15), t_of(22, 3, s), 0.45, 0.0, 0.3)

# ------------------------------------------------------------------ sidechain pump on the music bus
duck = np.ones(N)
for kt in kicks:
    i = int(kt * SR)
    m = min(N - i, int(0.4 * SR))
    duck[i : i + m] = np.minimum(duck[i : i + m], 1 - 0.55 * np.exp(-np.arange(m) / SR / 0.11))
music *= duck

# ------------------------------------------------------------------ reverb (synthetic hall)
ir_n = int(2.2 * SR)
t = np.arange(ir_n) / SR
irL = filt(rng.standard_normal(ir_n) * np.exp(-t / 0.55), "low", 5500)
irR = filt(rng.standard_normal(ir_n) * np.exp(-t / 0.55), "low", 5500)
irL[: int(0.02 * SR)] = 0
irR[: int(0.025 * SR)] = 0
irL /= np.sqrt((irL**2).sum())
irR /= np.sqrt((irR**2).sum())
wet = np.stack([fftconvolve(send, irL)[:N], fftconvolve(send, irR)[:N]]) * 0.5

mix = drums + music + wet
mix = filt(mix, "high", 28)
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(1.3 * mix) / np.tanh(1.3)
fade = int(0.4 * SR)
mix[:, -fade:] *= np.linspace(1, 0, fade) ** 2
mix *= 10 ** (-1.0 / 20) / np.max(np.abs(mix))
out = sys.argv[1] if len(sys.argv) > 1 else "bgm.wav"
sf.write(out, mix.T, SR, subtype="PCM_24")
print(f"wrote {out}: {DUR:.3f}s, {BPM:.0f} BPM, bar={BAR:.3f}s, final hit at {(FINAL_BAR - 1) * BAR:.3f}s")
