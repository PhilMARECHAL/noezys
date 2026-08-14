#!/usr/bin/env python3
"""Bande-son 30 s des vidéos Noezys — électro dynamique, montée en puissance.

Usage: python3 make-music.py out.wav "0,3.5,7,10.5,14,17,20,23,26.5" 14 23
  arg1: fichier WAV de sortie
  arg2: frontières de scènes (secondes) — impacts/accords calés dessus
  arg3-4: fenêtre pleine puissance (héritage CLI, la montée est progressive)

Structure : beat 120 BPM dès 0 s, chaque section ajoute une couche
(basse pulsée → arpèges → claps → hats 16èmes → lead), risers + roulements
avant chaque palier, climax tenu sur la carte finale.
"""
import sys, wave
import numpy as np

OUT = sys.argv[1]
BOUNDS = [float(x) for x in sys.argv[2].split(',')]

SR = 44100
DUR = float(sys.argv[5]) if len(sys.argv) > 5 else 30.0
N = int(SR * DUR)
BEAT = 0.5  # 120 BPM
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(42)

def st(sec): return max(0, min(N, int(sec * SR)))

def add(sig, start, left=1.0, right=1.0):
    i0 = st(start); i1 = min(N, i0 + len(sig))
    if i1 <= i0: return
    L[i0:i1] += sig[:i1-i0] * left
    R[i0:i1] += sig[:i1-i0] * right

def env_ar(n, attack, release):
    e = np.ones(n)
    a = min(n, int(attack*SR)); r = min(n, int(release*SR))
    if a: e[:a] = np.linspace(0, 1, a)**2
    if r: e[-r:] *= np.linspace(1, 0, r)**1.5
    return e

def nfreq(name):
    names = {'C':-9,'C#':-8,'D':-7,'D#':-6,'E':-5,'F':-4,'F#':-3,'G':-2,'G#':-1,'A':0,'A#':1,'B':2}
    return 440.0 * 2**((names[name[:-1]] + (int(name[-1])-4)*12) / 12)

def band_noise(n, center, width, decay):
    tt = np.arange(n)/SR
    noise = rng.standard_normal(n)
    spec = np.fft.rfft(noise); freqs = np.fft.rfftfreq(n, 1/SR)
    spec *= np.exp(-((freqs-center)/width)**2)
    nz = np.fft.irfft(spec, n)
    nz /= (np.abs(nz).max() + 1e-9)
    return nz * np.exp(-tt*decay)

# ── niveau d'énergie : montée par paliers sur les frontières ─────────
b = BOUNDS
def level(t):
    if len(b) < 5:
        ramp = [0.72, 0.82, 0.92, 1.0]
    else:
        ramp = [0.7, 0.78, 0.86, 0.94, 1.0]
    for i in range(len(ramp)-1, -1, -1):
        if i < len(b) and t >= b[i]: return ramp[min(i, len(ramp)-1)]
    return ramp[0]

# ── progression : Am9 → Fmaj9 → Cmaj9 → Gadd9, résolution Cmaj9 ──────
CHORDS = [
    ['A2','E3','B3','C4','G4','E5'],
    ['F2','C3','G3','A3','E4','C5'],
    ['C3','G3','D4','E4','B4','G5'],
    ['G2','D3','A3','B3','D4','B4'],
]
seg_bounds = BOUNDS + [DUR]
def chord_at(t):
    for i in range(len(BOUNDS)):
        if seg_bounds[i] <= t < seg_bounds[i+1]:
            return CHORDS[2] if i == len(BOUNDS)-1 else CHORDS[i % 4]
    return CHORDS[2]

# ── nappes (colle harmonique, attaque rapide, présentes mais pas molles)
for i in range(len(BOUNDS)):
    a_, b_ = seg_bounds[i], seg_bounds[i+1]
    chord = CHORDS[2] if i == len(BOUNDS)-1 else CHORDS[i % 4]
    dur = (b_ - a_) + 0.8
    lv = level(a_ + 0.01)
    n = int(dur*SR); tt = np.arange(n)/SR
    for k, name in enumerate(chord[:5]):
        f = nfreq(name)
        sig = np.zeros(n)
        for mul, amp in ((1,1.0),(2,0.4),(3,0.18),(4,0.08)):
            ph = 2*np.pi*f*mul*tt
            sig += amp*(np.sin(ph*1.002) + np.sin(ph*0.998))
        sig /= np.abs(sig).max()
        sig *= env_ar(n, 0.25, 1.0) * 0.045 * lv
        pan = 0.5 + 0.4*np.sin(k*2.1)
        add(sig, max(0, a_-0.05), left=1-pan+0.5, right=pan+0.5)

# ── batterie : grille globale 120 BPM ────────────────────────────────
t = 0.0
while t < DUR - 0.8:
    lv = level(t)
    # kick 4/4, punchy
    n = int(0.3*SR); tt = np.arange(n)/SR
    f = 160*np.exp(-tt*22) + 44
    kick = np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-tt*13) * 0.30 * lv
    add(kick, t)
    # clap sur 2 et 4 (à partir du 2e palier)
    beat_idx = round(t/BEAT)
    if beat_idx % 2 == 1 and t >= b[min(2, len(b)-1)]:
        cl = band_noise(int(0.25*SR), 1600, 1200, 22) * 0.16 * lv
        cl2 = band_noise(int(0.22*SR), 1800, 1200, 24) * 0.10 * lv
        add(cl, t); add(cl2, t + 0.022)
    # hats : contretemps toujours, 16èmes à pleine puissance
    hat = band_noise(int(0.09*SR), 9000, 4000, 70) * 0.075 * lv
    add(hat, t + BEAT/2, left=0.8, right=1.2)
    if lv >= 0.9:
        h2 = band_noise(int(0.06*SR), 10000, 4000, 90) * 0.045 * lv
        add(h2, t + BEAT/4, left=1.2, right=0.8)
        add(h2, t + 3*BEAT/4, left=1.2, right=0.8)
    t += BEAT

# ── basse pulsée en croches ──────────────────────────────────────────
t = 0.0
while t < DUR - 1.0:
    chord = chord_at(t)
    froot = nfreq(chord[0])
    n = int(0.32*SR); tt = np.arange(n)/SR
    sig = np.sin(2*np.pi*froot*tt) + 0.5*np.sin(2*np.pi*froot*2*tt) + 0.2*np.sin(2*np.pi*froot*3*tt)
    # légère saturation pour le mordant
    sig = np.tanh(sig*1.8)
    on_beat = abs((t/BEAT) - round(t/BEAT)) < 0.05
    v = 0.13 if on_beat else 0.17          # duck léger sous le kick
    sig *= np.exp(-tt*7) * v * level(t)
    add(sig, t + 0.01)
    t += BEAT/2

# ── arpège 16èmes (dès le 2e segment), motif montant ────────────────
if len(b) > 1:
    t = b[1]
    step = 0
    while t < DUR - 1.0:
        chord = chord_at(t)
        tones = chord[2:6]
        f = nfreq(tones[step % len(tones)]) * 2
        n = int(0.3*SR); tt = np.arange(n)/SR
        pl = (np.sin(2*np.pi*f*tt) + 0.3*np.sin(2*np.pi*f*2*tt)) * np.exp(-tt*14)
        v = 0.05 * level(t)
        pan = 0.35 if step % 2 else 0.65
        add(pl*v, t, left=1-pan+0.5, right=pan+0.5)
        add(pl*v*0.4, t + 0.375, left=pan+0.5, right=1-pan+0.5)
        step += 1
        t += BEAT/4

# ── lead : motif en blanches à pleine puissance ─────────────────────
if len(b) >= 5:
    t = b[4]
    step = 0
    while t < DUR - 1.5:
        chord = chord_at(t)
        f = nfreq(chord[4 if step % 4 in (0, 3) else 5])
        n = int(1.1*SR); tt = np.arange(n)/SR
        vib = 0.4*np.sin(2*np.pi*5*tt)
        sig = np.sin(2*np.pi*f*tt + vib) + 0.4*np.sin(2*np.pi*f*2*tt + vib)
        sig *= env_ar(n, 0.05, 0.5) * 0.05
        add(sig, t, left=1.1, right=0.9)
        step += 1
        t += BEAT*2

# ── risers + roulements avant chaque palier majeur ──────────────────
def riser(end_at, dur=1.8, vol=0.16):
    n = int(dur*SR); tt = np.arange(n)/SR
    nz = band_noise(n, 2000, 2500, 0)
    nz *= (tt/dur)**2.2 * vol
    add(nz, end_at - dur)
    # roulement de caisse : 16èmes qui s'accélèrent
    rt = end_at - 1.0
    k = 0
    while rt < end_at - 0.02:
        sn = band_noise(int(0.1*SR), 1800, 1400, 40) * (0.05 + 0.09*(rt-(end_at-1.0)))
        add(sn, rt)
        k += 1
        rt += 0.125 if k < 4 else 0.0625

def impact(at, vol=1.0):
    n = int(0.6*SR); tt = np.arange(n)/SR
    th = np.sin(2*np.pi*(85*np.exp(-tt*7)+32)*tt) * np.exp(-tt*6) * 0.30
    nz = band_noise(n, 900, 900, 10) * 0.14
    crash = band_noise(int(1.3*SR), 7000, 5000, 3.5) * 0.09
    add((th+nz)*vol, at); add(crash*vol, at)

majors = [b[i] for i in (3, 4) if i < len(b)] + [b[-1]]
for m in majors:
    riser(m); impact(m, 1.1)
for bb in b[1:]:
    if bb not in majors: impact(bb, 0.75)

# ── finale : accord tenu massif + dernier impact ────────────────────
fin = b[-1]
n = int((DUR-fin)*SR); tt = np.arange(n)/SR
for k, name in enumerate(['C2','C3','G3','E4','B4','D5','G5']):
    f = nfreq(name)
    sig = np.sin(2*np.pi*f*tt*1.002) + np.sin(2*np.pi*f*tt*0.998) + 0.3*np.sin(2*np.pi*f*2*tt)
    sig *= env_ar(n, 0.15, 1.8) * 0.05
    pan = 0.5 + 0.35*np.sin(k*1.7)
    add(sig, fin, left=1-pan+0.5, right=pan+0.5)
impact(DUR - 1.0, 0.9)

# ── mastering ───────────────────────────────────────────────────────
mix = np.stack([L, R])
fi = int(0.05*SR); mix[:, :fi] *= np.linspace(0, 1, fi)
fo = int(0.9*SR); mix[:, -fo:] *= np.linspace(1, 0, fo)**1.2
mix = np.tanh(mix * 2.1)
mix *= 0.92 / np.abs(mix).max()

pcm = (mix.T * 32767).astype(np.int16)
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"OK → {OUT} ({DUR}s, peak {np.abs(mix).max():.2f})")
