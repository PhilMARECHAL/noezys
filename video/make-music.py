#!/usr/bin/env python3
"""Bande-son des vidéos NOEZYS — électro dynamique, transitions FLUIDES.

Usage: python3 make-music.py out.wav "0,2,5,11.2,17.2,23.2,28.2" 11.2 23.2 34.5
  arg1: fichier WAV de sortie
  arg2: frontières de scènes (secondes)
  arg3-4: héritage CLI (ignorés, la montée est progressive)
  arg5: durée totale (défaut 30.0)

Fluidité (prescriptions du panel de 10 experts audio) :
- frontières musicales quantifiées sur la grille de temps (120 BPM)
- niveau en RAMPE continue (crescendo d'une seconde avant chaque palier)
- crossfade equal-power des nappes (sin/cos), chevauchement large
- chaque couche rythmique entre en fondu sur 2 mesures
- mini-riser d'annonce sur TOUTES les frontières, impacts hiérarchisés et adoucis
- drone continu discret qui lie tout le morceau
- outro : les percussions s'éteignent en fondu, l'accord final porte la fin (fade 2,5 s)
- limiteur détendu (tanh 1.5) pour supprimer l'écrasement autour des impacts
"""
import sys, wave
import numpy as np

OUT = sys.argv[1]
RAW_BOUNDS = [float(x) for x in sys.argv[2].split(',')]

SR = 44100
DUR = float(sys.argv[5]) if len(sys.argv) > 5 else 30.0
BEAT = 0.5  # 120 BPM
# frontières musicales calées sur la grille de temps (évite le « trébuchement »)
b = [round(x / BEAT) * BEAT for x in RAW_BOUNDS]
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(42)

def st(sec): return max(0, min(N, int(sec * SR)))

def add(sig, start, left=1.0, right=1.0):
    i0 = st(start); i1 = min(N, i0 + len(sig))
    if i1 <= i0: return
    L[i0:i1] += sig[:i1-i0] * left
    R[i0:i1] += sig[:i1-i0] * right

def env_xfade(n, attack, release):
    """Enveloppe equal-power : attaque en sin, release en cos."""
    e = np.ones(n)
    a = min(n, int(attack*SR)); r = min(n, int(release*SR))
    if a: e[:a] = np.sin(np.linspace(0, np.pi/2, a))
    if r: e[-r:] *= np.cos(np.linspace(0, np.pi/2, r))
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

# ── niveau : RAMPE CONTINUE (crescendo 1 s avant chaque palier) ──────
ramp_full = [0.7, 0.78, 0.86, 0.94, 1.0]
nsteps = min(len(b), len(ramp_full))
ramp = ramp_full[:nsteps] if nsteps >= 2 else [0.85, 1.0]
xs = [0.0]; ys = [ramp[0]]
for i in range(1, nsteps):
    xs += [max(xs[-1] + 1e-4, b[i] - 1.0), b[i]]
    ys += [ramp[i-1], ramp[i]]
xs += [DUR]; ys += [ys[-1]]
def level(t): return float(np.interp(t, xs, ys))
level_curve = np.interp(np.arange(N)/SR, xs, ys)

# ── progression : Am9 → Fmaj9 → Cmaj9 → Gadd9, résolution Cmaj9 ──────
CHORDS = [
    ['A2','E3','B3','C4','G4','E5'],
    ['F2','C3','G3','A3','E4','C5'],
    ['C3','G3','D4','E4','B4','G5'],
    ['G2','D3','A3','B3','D4','B4'],
]
seg_bounds = b + [DUR]
def chord_at(t):
    for i in range(len(b)):
        if seg_bounds[i] <= t < seg_bounds[i+1]:
            return CHORDS[2] if i == len(b)-1 else CHORDS[i % 4]
    return CHORDS[2]

# ── nappes : crossfade equal-power, large chevauchement, niveau continu
for i in range(len(b)):
    a_, b_ = seg_bounds[i], seg_bounds[i+1]
    chord = CHORDS[2] if i == len(b)-1 else CHORDS[i % 4]
    start = max(0.0, a_ - 0.4)
    dur = (b_ - start) + 0.8
    n = int(dur*SR); tt = np.arange(n)/SR
    lv_arr = np.interp(start + tt, xs, ys)
    for k, name in enumerate(chord[:5]):
        f = nfreq(name)
        sig = np.zeros(n)
        for mul, amp in ((1,1.0),(2,0.4),(3,0.18),(4,0.08)):
            ph = 2*np.pi*f*mul*tt
            sig += amp*(np.sin(ph*1.002) + np.sin(ph*0.998))
        sig /= np.abs(sig).max()
        sig *= env_xfade(n, 0.4, 0.8) * 0.045 * lv_arr
        pan = 0.5 + 0.4*np.sin(k*2.1)
        add(sig, start, left=1-pan+0.5, right=pan+0.5)

# ── drone continu discret (A3, présent sur les 4 accords) ────────────
tt = np.arange(N)/SR
fA = nfreq('A3')
drone = (np.sin(2*np.pi*fA*tt*1.001) + np.sin(2*np.pi*fA*tt*0.999)) * 0.5
drone *= (0.85 + 0.15*np.sin(2*np.pi*0.07*tt))          # respiration très lente
fi = int(1.5*SR); drone[:fi] *= np.linspace(0, 1, fi)
fo = int(2.5*SR); drone[-fo:] *= np.linspace(1, 0, fo)
add(drone * 0.018 * level_curve, 0)

def gain_in(t, t_start, ramp_s=4.0):
    """Fondu d'entrée d'une couche sur 2 mesures."""
    return min(1.0, max(0.0, (t - t_start) / ramp_s))

def gain_out(t):
    """Outro : extinction douce des éléments percussifs avant la fin."""
    return min(1.0, max(0.0, (DUR - 1.2 - t) / 2.0))

# ── batterie : grille 120 BPM ────────────────────────────────────────
t = 0.0
while t < DUR - 0.8:
    lv = level(t) * gain_out(t)
    if lv > 0.01:
        n = int(0.3*SR); tk = np.arange(n)/SR
        f = 160*np.exp(-tk*22) + 44
        kick = np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-tk*13) * 0.30 * lv
        add(kick, t)
        beat_idx = round(t/BEAT)
        if beat_idx % 2 == 1 and len(b) > 2:
            g = gain_in(t, b[2])
            if g > 0:
                cl = band_noise(int(0.25*SR), 1600, 1200, 22) * 0.16 * lv * g
                cl2 = band_noise(int(0.22*SR), 1800, 1200, 24) * 0.10 * lv * g
                add(cl, t); add(cl2, t + 0.022)
        hat = band_noise(int(0.09*SR), 9000, 4000, 70) * 0.075 * lv
        add(hat, t + BEAT/2, left=0.8, right=1.2)
        if len(b) > 3:
            g16 = gain_in(t, b[3])
            if g16 > 0:
                h2 = band_noise(int(0.06*SR), 10000, 4000, 90) * 0.045 * lv * g16
                add(h2, t + BEAT/4, left=1.2, right=0.8)
                add(h2, t + 3*BEAT/4, left=1.2, right=0.8)
    t += BEAT

# ── basse pulsée en croches ──────────────────────────────────────────
t = 0.0
while t < DUR - 1.0:
    g = gain_out(t)
    if g > 0.01:
        chord = chord_at(t)
        froot = nfreq(chord[0])
        n = int(0.32*SR); tb = np.arange(n)/SR
        sig = np.sin(2*np.pi*froot*tb) + 0.5*np.sin(2*np.pi*froot*2*tb) + 0.2*np.sin(2*np.pi*froot*3*tb)
        sig = np.tanh(sig*1.8)
        on_beat = abs((t/BEAT) - round(t/BEAT)) < 0.05
        v = 0.13 if on_beat else 0.17
        sig *= np.exp(-tb*7) * v * level(t) * g
        add(sig, t + 0.01)
    t += BEAT/2

# ── arpège 16èmes (entrée en fondu dès la 2e frontière) ─────────────
if len(b) > 1:
    t = b[1]
    step = 0
    while t < DUR - 1.0:
        g = gain_in(t, b[1]) * gain_out(t)
        if g > 0.01:
            chord = chord_at(t)
            tones = chord[2:6]
            f = nfreq(tones[step % len(tones)]) * 2
            n = int(0.3*SR); ta = np.arange(n)/SR
            pl = (np.sin(2*np.pi*f*ta) + 0.3*np.sin(2*np.pi*f*2*ta)) * np.exp(-ta*14)
            v = 0.05 * level(t) * g
            pan = 0.35 if step % 2 else 0.65
            add(pl*v, t, left=1-pan+0.5, right=pan+0.5)
            add(pl*v*0.4, t + 0.375, left=pan+0.5, right=1-pan+0.5)
        step += 1
        t += BEAT/4

# ── lead : entrée en fondu à pleine puissance ───────────────────────
if len(b) >= 5:
    t = b[4]
    step = 0
    while t < DUR - 1.5:
        g = gain_in(t, b[4]) * gain_out(t)
        if g > 0.01:
            chord = chord_at(t)
            f = nfreq(chord[4 if step % 4 in (0, 3) else 5])
            n = int(1.1*SR); tl = np.arange(n)/SR
            vib = 0.4*np.sin(2*np.pi*5*tl)
            sig = np.sin(2*np.pi*f*tl + vib) + 0.4*np.sin(2*np.pi*f*2*tl + vib)
            sig *= env_xfade(n, 0.05, 0.5) * 0.05 * g
            add(sig, t, left=1.1, right=0.9)
        step += 1
        t += BEAT*2

# ── annonces et impacts hiérarchisés ────────────────────────────────
def riser(end_at, dur=1.8, vol=0.16, roll=True):
    n = int(dur*SR); tr = np.arange(n)/SR
    nz = band_noise(n, 2000, 2500, 0)
    nz *= (tr/dur)**2.2 * vol
    add(nz, end_at - dur)
    if roll:
        rt = end_at - 1.0
        k = 0
        while rt < end_at - 0.02:
            sn = band_noise(int(0.1*SR), 1800, 1400, 40) * (0.05 + 0.09*(rt-(end_at-1.0)))
            add(sn, rt)
            k += 1
            rt += 0.125 if k < 4 else 0.0625

def impact(at, vol=1.0):
    n = int(0.6*SR); ti = np.arange(n)/SR
    th = np.sin(2*np.pi*(85*np.exp(-ti*7)+32)*ti) * np.exp(-ti*6) * 0.24
    nz = band_noise(n, 900, 900, 10) * 0.10
    crash = band_noise(int(1.3*SR), 7000, 5000, 3.5) * 0.07
    add((th+nz)*vol, at); add(crash*vol, at)

majors = [b[i] for i in (3, 4) if i < len(b)] + [b[-1]]
for m in majors:
    riser(m); impact(m, 1.0)
for bb in b[1:]:
    if bb not in majors:
        riser(bb, dur=0.9, vol=0.07, roll=False)   # chaque frontière est annoncée
        impact(bb, 0.5)

# ── finale : accord tenu qui porte la fin (les percussions s'éteignent)
fin = b[-1]
n = int((DUR-fin)*SR); tf = np.arange(n)/SR
for k, name in enumerate(['C2','C3','G3','E4','B4','D5','G5']):
    f = nfreq(name)
    sig = np.sin(2*np.pi*f*tf*1.002) + np.sin(2*np.pi*f*tf*0.998) + 0.3*np.sin(2*np.pi*f*2*tf)
    sig *= env_xfade(n, 0.3, 2.0) * 0.05
    pan = 0.5 + 0.35*np.sin(k*1.7)
    add(sig, fin, left=1-pan+0.5, right=pan+0.5)

# ── mastering : limiteur détendu, long fade-out ─────────────────────
mix = np.stack([L, R])
fi = int(0.05*SR); mix[:, :fi] *= np.linspace(0, 1, fi)
fo = int(2.5*SR); mix[:, -fo:] *= np.linspace(1, 0, fo)**1.5
mix = np.tanh(mix * 1.5)
mix *= 0.92 / np.abs(mix).max()

pcm = (mix.T * 32767).astype(np.int16)
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"OK → {OUT} ({DUR}s, peak {np.abs(mix).max():.2f})")
