"""Original BGM for the Helen brand reveal — warm acoustic funk/soul, 108 BPM, F major.

Fully synthesized (no samples), so it is royalty-free by construction. Deterministic:
the noise generator is seeded, so the same script always writes the same file.

Arrangement (bars of 4/4, 1 bar = 2.222 s):
  1-2   intro        kick on 1/3, claps 2/4, Rhodes swells, snare pickup into bar 3
  3-7   groove A     full band from the bar-3 crash (logo reveal)
  8-9   groove A     crash on bar 8 (palette)
  10    break        bass + claps + Rhodes only (typography), fill into 11
  11-13 groove A     crash on 11 (patterns / icons)
  14-17 groove B     peak energy: tambourine, open hats, marimba hook (food)
  18-20 groove A     hook answers (applications)
  21    groove B     closing build, band pickup on beat 4
  22    final hit    beat 1 tutti + ring-out (the last golpe)

Usage: python3 -I tools/compose_bgm.py out.wav
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
BPM = 108.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
SWING = 0.58  # 16th swing ratio
LAST_BAR = 22
TAIL = 1.5
DUR = (LAST_BAR - 1) * BAR + TAIL
N = int(DUR * SR)
rng = np.random.default_rng(1977)

mixL = np.zeros(N)
mixR = np.zeros(N)
verb_send = np.zeros(N)


def t_of(bar, beat=0.0, sixteenth=0):
    """Time of bar (1-based), beat (0-based float), plus swung 16th index within that beat."""
    base = (bar - 1) * BAR + beat * BEAT
    if sixteenth:
        # swung 16ths: the 2nd and 4th 16ths are pushed late
        pos = {0: 0.0, 1: SWING * 0.5, 2: 0.5, 3: 0.5 + SWING * 0.5}[sixteenth]
        base += pos * BEAT
    return base


def add(sig, t, gain=1.0, pan=0.0, verb=0.0):
    i = int(round(t * SR))
    if i >= N:
        return
    sig = sig[: N - i]
    l = np.cos((pan + 1) * np.pi / 4) * gain
    r = np.sin((pan + 1) * np.pi / 4) * gain
    mixL[i : i + len(sig)] += sig * l
    mixR[i : i + len(sig)] += sig * r
    if verb:
        verb_send[i : i + len(sig)] += sig * gain * verb


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)


def env(n, a, d, shape=1.0):
    t = np.arange(n) / SR
    e = np.exp(-t / d) ** shape
    att = int(a * SR)
    if att > 0:
        e[:att] *= np.linspace(0, 1, att)
    return e


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ---------------------------------------------------------------- drums
def kick(strength=1.0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 48 + 95 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * env(n, 0.001, 0.22)
    click = hp(rng.standard_normal(n), 2500) * env(n, 0.0, 0.004)
    return np.tanh(1.6 * (body + 0.25 * click)) * strength


def snare(strength=1.0):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * 185 * t) + 0.5 * np.sin(2 * np.pi * 330 * t)) * env(n, 0.001, 0.05)
    noise = bp(rng.standard_normal(n), 1500, 9000) * env(n, 0.001, 0.12)
    return (0.6 * tone + 0.9 * noise) * strength


def clap(strength=1.0):
    n = int(0.4 * SR)
    out = np.zeros(n)
    for k, off in enumerate((0.0, 0.009, 0.019, 0.031)):
        i = int(off * SR)
        m = n - i
        burst = rng.standard_normal(m) * env(m, 0.0005, 0.012 if k < 3 else 0.11)
        out[i:] += burst
    return bp(out, 900, 5200) * 0.9 * strength


def shaker(strength=1.0):
    n = int(0.09 * SR)
    return hp(rng.standard_normal(n), 6000) * env(n, 0.006, 0.022) * strength


def hat(open_=False, strength=1.0):
    n = int((0.5 if open_ else 0.08) * SR)
    x = hp(rng.standard_normal(n), 7500, 3)
    return x * env(n, 0.0005, 0.16 if open_ else 0.018) * strength


def tamb(strength=1.0):
    n = int(0.2 * SR)
    t = np.arange(n) / SR
    jingle = sum(np.sin(2 * np.pi * f * t + p) for f, p in ((5200, 0), (7100, 1), (8900, 2), (10300, 3)))
    x = hp(rng.standard_normal(n), 5000) * 0.8 + 0.25 * jingle
    return x * env(n, 0.002, 0.05) * strength


def crash(strength=1.0, length=2.4):
    n = int(length * SR)
    x = hp(rng.standard_normal(n), 3500, 2)
    t = np.arange(n) / SR
    ring = sum(np.sin(2 * np.pi * f * t) for f in (3150, 4420, 5930, 7710)) * 0.05
    return (x + ring) * env(n, 0.002, 0.6) * strength


# ---------------------------------------------------------------- tonal
def bass_note(m, dur, strength=1.0):
    n = int((dur + 0.15) * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    x = np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * 2 * f * t) + 0.18 * np.sin(2 * np.pi * 3 * f * t)
    pluck = hp(rng.standard_normal(n), 300) * env(n, 0.0, 0.006) * 0.15
    e = env(n, 0.004, 0.55)
    gate = np.ones(n)
    rel = int(0.06 * SR)
    stop = int(dur * SR)
    if stop < n:
        gate[stop : stop + rel] = np.linspace(1, 0, min(rel, n - stop))
        gate[stop + rel :] = 0
    return lp(np.tanh(1.3 * (x + pluck)) * e * gate, 1400) * strength


def rhodes(midis, dur, strength=1.0, attack=0.003):
    n = int((dur + 0.6) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m in midis:
        f = mtof(m)
        idx = 2.2 * np.exp(-t / 0.18) + 0.25
        mod = np.sin(2 * np.pi * f * t) * idx
        car = np.sin(2 * np.pi * f * t + mod) + 0.12 * np.sin(2 * np.pi * 2 * f * t)
        out += car
    out /= max(1, len(midis)) ** 0.7
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * t)
    e = env(n, attack, 1.6)
    gate = np.ones(n)
    stop = int(dur * SR)
    rel = int(0.25 * SR)
    if stop < n:
        gate[stop : stop + rel] = np.linspace(1, 0, min(rel, n - stop))
        gate[stop + rel :] = 0
    return out * e * gate * trem * strength * 1.7


def marimba(m, strength=1.0):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    x = np.sin(2 * np.pi * f * t) * env(n, 0.001, 0.35) + 0.35 * np.sin(2 * np.pi * 4 * f * t) * env(n, 0.0, 0.03)
    x += 0.15 * np.sin(2 * np.pi * 10 * f * t) * env(n, 0.0, 0.008)
    return x * strength * 1.5


def guitar_chick(midis, strength=1.0):
    """Muted funk guitar 'chick' — short filtered noise + upper chord partials."""
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * mtof(m) * t) for m in midis) / len(midis)
    x = x * 0.5 + bp(rng.standard_normal(n), 1200, 4500) * 0.6
    return bp(x, 400, 5000) * env(n, 0.001, 0.025) * strength


# ---------------------------------------------------------------- harmony
# F major soul cycle: Fmaj9 | Dm9 | Gm9 | C9sus4->C7
CH = {
    "Fmaj9": dict(root=41, voicing=[57, 60, 64, 67]),  # A C E G over F
    "Dm9": dict(root=38, voicing=[57, 60, 64, 65]),  # A C E F
    "Gm9": dict(root=43, voicing=[58, 62, 65, 69]),  # Bb D F A
    "C9sus": dict(root=36, voicing=[58, 62, 65, 67]),  # Bb D F G
    "C7#9": dict(root=36, voicing=[58, 63, 64, 67]),
    "Bbmaj7": dict(root=46, voicing=[57, 62, 65, 69]),
    "Fmaj69": dict(root=41, voicing=[55, 60, 62, 64, 69]),
}
CYCLE = ["Fmaj9", "Dm9", "Gm9", "C9sus"]


def chord_for(bar):
    if bar == 1:
        return "Fmaj9"
    if bar == 2:
        return "C9sus"
    if bar == 10:
        return "Bbmaj7"
    if bar == 21:
        return "C9sus"
    if bar == 22:
        return "Fmaj69"
    return CYCLE[(bar - 3) % 4]


# bass pattern: (beat, 16th, interval-from-root, length in beats)
BASS_A = [(0, 0, 0, 0.75), (0, 3, 12, 0.25), (1, 2, 7, 0.4), (2, 0, 0, 0.5), (2, 3, 10, 0.25), (3, 1, 12, 0.3), (3, 3, 7, 0.25)]
BASS_INTRO = []
BASS_BREAK = [(0, 0, 0, 1.4), (1, 2, 7, 0.4), (2, 2, 12, 0.4), (3, 0, 10, 0.5), (3, 2, 7, 0.4)]

HOOK = [  # (bar offset in 2-bar phrase, beat, 16th, midi)
    (0, 0, 2, 72), (0, 1, 0, 74), (0, 1, 2, 77), (0, 2, 2, 74), (0, 3, 0, 72),
    (1, 0, 2, 69), (1, 1, 2, 72), (1, 2, 0, 74), (1, 3, 1, 77), (1, 3, 3, 79),
]

for bar in range(1, LAST_BAR + 1):
    name = chord_for(bar)
    ch = CH[name]
    root = ch["root"]
    intro = bar <= 2
    brk = bar == 10
    peak = 14 <= bar <= 17 or bar == 21
    final = bar == LAST_BAR

    if final:
        add(kick(1.2), t_of(bar), 0.95)
        add(crash(1.0, 2.0), t_of(bar), 0.32, -0.2, verb=0.25)
        add(crash(0.8, 2.0), t_of(bar), 0.22, 0.3, verb=0.25)
        add(snare(1.0), t_of(bar), 0.45, 0.05, verb=0.4)
        add(clap(1.0), t_of(bar), 0.4, 0.0, verb=0.4)
        add(bass_note(root, 1.35), t_of(bar), 0.85)
        add(bass_note(root - 12, 1.35), t_of(bar), 0.35)
        add(rhodes(ch["voicing"], 1.25), t_of(bar), 0.55, 0.0, verb=0.35)
        add(marimba(77), t_of(bar), 0.32, 0.25, verb=0.3)
        add(marimba(81), t_of(bar), 0.26, -0.25, verb=0.3)
        add(marimba(84), t_of(bar), 0.22, 0.0, verb=0.35)
        continue

    # ---- crashes on the structural downbeats
    if bar in (3, 8, 11, 14, 18, 21):
        add(crash(1.0), t_of(bar), 0.26 if bar != 3 else 0.33, 0.25, verb=0.2)

    # ---- kick
    if intro:
        for b in (0, 2):
            add(kick(), t_of(bar, b), 0.85)
    elif brk:
        add(kick(0.8), t_of(bar, 0), 0.7)
    else:
        for b, s in ((0, 0), (1, 3), (2, 0), (2, 2)):
            add(kick(), t_of(bar, b, s), 0.85 if s == 0 else 0.6)
        if peak:
            add(kick(0.7), t_of(bar, 3, 3), 0.45)

    # ---- backbeat: snare + clap layered on 2 and 4
    for b in (1, 3):
        add(clap(), t_of(bar, b), 0.5, 0.1, verb=0.25)
        if not intro and not brk:
            add(snare(), t_of(bar, b), 0.5, -0.05, verb=0.15)
    if not intro and not brk:  # ghost notes
        for b, s in ((1, 3), (3, 1)):
            add(snare(0.25), t_of(bar, b, s), 0.3, -0.05)

    # ---- shaker 16ths (from bar 2), hats
    if bar >= 2:
        for b in range(4):
            for s in range(4):
                acc = 1.0 if s == 2 else (0.55 if s == 0 else 0.4)
                add(shaker(acc), t_of(bar, b, s), 0.32 if not brk else 0.2, 0.45)
    if not intro and not brk:
        for b in range(4):
            add(hat(False, 0.9), t_of(bar, b), 0.22, -0.35)
            if peak:
                add(hat(True, 0.6), t_of(bar, b, 2), 0.18, -0.35)
    if peak:
        for b in range(4):
            for s in (0, 2):
                add(tamb(1.0 if s == 2 else 0.6), t_of(bar, b, s), 0.22, 0.55)

    # ---- bass
    pat = BASS_INTRO if intro else (BASS_BREAK if brk else BASS_A)
    for b, s, iv, ln in pat:
        add(bass_note(root + iv, ln * BEAT), t_of(bar, b, s), 0.8)

    # ---- Rhodes comping
    if intro:
        add(rhodes(ch["voicing"], BAR * 0.95, 0.9, attack=0.08), t_of(bar), 0.5, -0.1, verb=0.4)
    else:
        for b, s, ln in ((0, 2, 0.4), (1, 2, 0.3), (2, 3, 0.5), (3, 2, 0.3)):
            add(rhodes(ch["voicing"], ln * BEAT, 0.8), t_of(bar, b, s), 0.42 if not brk else 0.55, -0.15, verb=0.3)

    # ---- funk guitar chicks on the off-16ths (groove sections)
    if not intro and not brk:
        for b in range(4):
            add(guitar_chick([v + 12 for v in ch["voicing"][1:3]]), t_of(bar, b, 2), 0.2, 0.35)
            if peak:
                add(guitar_chick([v + 12 for v in ch["voicing"][1:3]], 0.6), t_of(bar, b, 3), 0.14, 0.35)

    # ---- marimba hook (logo reveal answer, food, applications, closing)
    if bar in (3, 4) or 14 <= bar <= 21:
        phrase_bar = (bar - 3) % 2 if bar <= 4 else (bar - 14) % 2
        for off, b, s, m in HOOK:
            if off == phrase_bar:
                gain = 0.3 if peak else 0.22
                add(marimba(m), t_of(bar, b, s), gain, 0.2, verb=0.3)
                if peak:
                    add(marimba(m - 12), t_of(bar, b, s), gain * 0.5, -0.2, verb=0.3)

    # ---- fills / pickups
    if bar == 2:  # snare roll into the logo reveal
        for k, s in enumerate((0, 1, 2, 3)):
            add(snare(0.4 + 0.15 * k), t_of(2, 3, s), 0.42, 0.0, verb=0.2)
    if bar == 10:
        for k, s in enumerate((0, 1, 2, 3)):
            add(snare(0.45 + 0.15 * k), t_of(10, 3, s), 0.45, 0.0, verb=0.2)
    if bar == 21:  # band pickup: hits on 4 and 4& then silence before the final golpe
        for s in (0, 2):
            add(snare(1.0), t_of(21, 3, s), 0.5, 0.0, verb=0.3)
            add(kick(0.9), t_of(21, 3, s), 0.7)
            add(rhodes(CH["C7#9"]["voicing"], 0.18), t_of(21, 3, s), 0.45, -0.1, verb=0.3)
            add(bass_note(36 + (0 if s == 0 else 2), 0.2), t_of(21, 3, s), 0.8)

# ---------------------------------------------------------------- reverb (synthetic room IR)
ir_n = int(1.4 * SR)
ir_t = np.arange(ir_n) / SR
ir = rng.standard_normal(ir_n) * np.exp(-ir_t / 0.32)
ir = lp(ir, 6000)
ir[: int(0.012 * SR)] = 0
ir /= np.sqrt((ir ** 2).sum())
wet = fftconvolve(verb_send, ir)[:N] * 0.55
irR = np.roll(ir, int(0.007 * SR))
wetR = fftconvolve(verb_send, irR)[:N] * 0.55

L = mixL + wet
R = mixR + wetR

# ---------------------------------------------------------------- master: glue + limiter-ish
st = np.stack([L, R])
st = hp(st, 30)
st /= np.max(np.abs(st)) + 1e-9
st = np.tanh(1.4 * st) / np.tanh(1.4)
# final tail: let the last chord ring, then a short release to true silence
fade = int(0.35 * SR)
st[:, -fade:] *= np.linspace(1, 0, fade) ** 2
st *= 10 ** (-1.0 / 20) / np.max(np.abs(st))

import soundfile as sf

out = sys.argv[1] if len(sys.argv) > 1 else "bgm.wav"
sf.write(out, st.T, SR, subtype="PCM_24")
print(f"wrote {out}: {DUR:.3f}s, {BPM} BPM, bar={BAR:.4f}s, final hit at {(LAST_BAR - 1) * BAR:.4f}s")
