#!/usr/bin/env python3
"""Synthèse de la bande-son 30 s des vidéos Noezys.

Usage: python3 make-music.py out.wav "0,3.5,7,10.5,14,17,20,23,26.5" 14 23
  arg1: fichier WAV de sortie
  arg2: frontières de scènes (secondes) — impacts/accords calés dessus
  arg3-4: fenêtre "énergie" (percussion + arpège), en secondes
"""
import sys, wave
import numpy as np

OUT = sys.argv[1]
BOUNDS = [float(x) for x in sys.argv[2].split(',')]
E_START, E_END = float(sys.argv[3]), float(sys.argv[4])

SR = 44100
DUR = 30.0
N = int(SR * DUR)
t_axis = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)

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

def tone(freq, dur, harmonics=((1,1.0),(2,0.35),(3,0.14),(4,0.06)), detune=0.0015, vib=0.0):
    n = int(dur*SR); tt = np.arange(n)/SR
    out = np.zeros(n)
    for mul, amp in harmonics:
        f = freq*mul
        ph = 2*np.pi*f*tt
        if vib: ph += vib*np.sin(2*np.pi*4.5*tt)
        out += amp*(np.sin(ph*(1+detune)) + np.sin(ph*(1-detune)))
    return out / np.abs(out).max()

def nfreq(name):
    names = {'C':-9,'C#':-8,'D':-7,'D#':-6,'E':-5,'F':-4,'F#':-3,'G':-2,'G#':-1,'A':0,'A#':1,'B':2}
    return 440.0 * 2**((names[name[:-1]] + (int(name[-1])-4)*12) / 12)

# ── progression : cycle Am9 → Fmaj9 → Cmaj9 → Gadd9, résolution Cmaj9 ──
CHORDS = [
    ['A2','E3','B3','C4','G4'],   # Am9
    ['F2','C3','G3','A3','E4'],   # Fmaj9
    ['C3','G3','D4','E4','B4'],   # Cmaj9
    ['G2','D3','A3','B3','D4'],   # Gadd9
]
seg_bounds = BOUNDS + [DUR]
for i in range(len(BOUNDS)):
    a, b = seg_bounds[i], seg_bounds[i+1]
    chord = CHORDS[2] if i == len(BOUNDS)-1 else CHORDS[i % 4]
    dur = (b - a) + 1.2                      # déborde pour fondu enchaîné
    energy = 1.0 if a >= E_START-0.1 and a < E_END else 0.75
    for k, name in enumerate(chord):
        f = nfreq(name)
        sig = tone(f, dur, vib=0.3 if k >= 3 else 0)
        sig *= env_ar(len(sig), 1.0, 1.4) * 0.055 * energy
        pan = 0.5 + 0.4*np.sin(k*2.1)        # léger placement stéréo
        add(sig, a - 0.15 if a > 0 else 0, left=1-pan+0.5, right=pan+0.5)
    # sub-bass : fondamentale -1 octave
    froot = nfreq(chord[0]) / 2
    sub = np.sin(2*np.pi*froot*np.arange(int(dur*SR))/SR)
    sub *= env_ar(len(sub), 0.6, 1.2) * 0.16 * energy
    add(sub, a - 0.1 if a > 0 else 0)

# ── shimmer aigu discret à partir du 3e segment ──
if len(BOUNDS) > 2:
    sh_start = BOUNDS[2]
    n = int((DUR - sh_start)*SR); tt = np.arange(n)/SR
    sh = np.sin(2*np.pi*nfreq('E6')*tt) * (0.5+0.5*np.sin(2*np.pi*0.13*tt))
    sh += np.sin(2*np.pi*nfreq('B5')*tt) * (0.5+0.5*np.cos(2*np.pi*0.11*tt))
    sh *= env_ar(n, 3.0, 2.5) * 0.012
    add(sh, sh_start, left=0.8, right=1.2)

# ── percussion douce + arpège pendant la fenêtre énergie ──
BEAT = 0.75  # ~80 BPM
beat_t = E_START
while beat_t < E_END - 0.05:
    n = int(0.22*SR); tt = np.arange(n)/SR
    f = 58*np.exp(-tt*9) + 38
    kick = np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-tt*16) * 0.16
    add(kick, beat_t)
    beat_t += BEAT

seg_idx = 0
arp_t = E_START
rng_state = 0
while arp_t < E_END - 0.05:
    # accord actif à cet instant
    for i in range(len(BOUNDS)):
        if seg_bounds[i] <= arp_t < seg_bounds[i+1]: seg_idx = i
    chord = CHORDS[seg_idx % 4]
    step = int((arp_t - E_START)/ (BEAT/2)) % 4
    f = nfreq(chord[1 + step % (len(chord)-1)]) * 2
    n = int(0.5*SR); tt = np.arange(n)/SR
    pl = np.sin(2*np.pi*f*tt) * np.exp(-tt*9) * 0.045
    pan = 0.3 if step % 2 else 0.7
    add(pl, arp_t, left=1-pan+0.5, right=pan+0.5)
    add(pl*0.35, arp_t + 0.375, left=pan+0.5, right=1-pan+0.5)  # écho croisé
    arp_t += BEAT/2

# ── impacts + risers sur les frontières ──
rng = np.random.default_rng(42)
def impact(at, vol=1.0):
    n = int(0.5*SR); tt = np.arange(n)/SR
    th = np.sin(2*np.pi*(70*np.exp(-tt*6)+30)*tt) * np.exp(-tt*7) * 0.22
    noise = rng.standard_normal(n)
    spec = np.fft.rfft(noise); freqs = np.fft.rfftfreq(n, 1/SR)
    spec *= np.exp(-((freqs-900)/900)**2)
    nz = np.fft.irfft(spec, n); nz /= np.abs(nz).max()
    add((th + nz*np.exp(-tt*11)*0.12) * vol, at)

def riser(end_at, dur=1.6, vol=0.11):
    n = int(dur*SR); tt = np.arange(n)/SR
    noise = rng.standard_normal(n)
    spec = np.fft.rfft(noise); freqs = np.fft.rfftfreq(n, 1/SR)
    spec *= np.exp(-((freqs-1400)/1400)**2)
    nz = np.fft.irfft(spec, n); nz /= np.abs(nz).max()
    nz *= (tt/dur)**2.5 * vol
    add(nz, end_at - dur)

for b in BOUNDS[1:]:
    impact(b, vol=0.9 if E_START <= b < E_END else 1.0)
# montées avant la révélation du logo (frontière 4) et la carte finale
if len(BOUNDS) >= 5: riser(BOUNDS[4])
riser(BOUNDS[-1])

# ── mastering léger ──
mix = np.stack([L, R])
# fondu d'entrée / de sortie
fi = int(0.4*SR); mix[:, :fi] *= np.linspace(0, 1, fi)
fo = int(1.6*SR); mix[:, -fo:] *= np.linspace(1, 0, fo)**1.2
# compression douce (tanh) + normalisation
mix = np.tanh(mix * 1.6)
mix *= 0.84 / np.abs(mix).max()

pcm = (mix.T * 32767).astype(np.int16)
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"OK → {OUT} ({DUR}s, peak {np.abs(mix).max():.2f})")
