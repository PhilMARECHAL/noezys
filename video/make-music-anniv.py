#!/usr/bin/env python3
"""Bande-son « Happy Birthday Romain » — big-room festival (25,5 s).

Style mainstage : kick 4/4 massif, pompage sidechain, montées avec roulements,
et la mélodie de « Happy Birthday to You » (domaine public) en lead supersaw
sur les drops. Structure calée sur les scènes :
  0-3    intro percutante (motif « hap-py » en pluck)
  3-6    build : roulement + riser + arpèges
  6-13   DROP 1 : phrases 1 & 2 de la mélodie en supersaw plein pot (les toasts)
  13-17  breakdown chaleureux : phrase 3 (« dear Romain », le saut d'octave) en pluck
  17-19  build 2 : la plus grosse montée
  19-25.5 DROP 2 final : phrase 4 + accord final sous les confettis
Usage : python3 make-music-anniv.py out.wav
"""
import sys
import numpy as np

OUT = sys.argv[1] if len(sys.argv) > 1 else 'music-anniv.wav'
SR = 44100
DUR = 25.5
BEAT = 0.5           # 120 BPM
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(42)

INTRO, BUILD, DROP1, BREAK, BUILD2, DROP2 = 0.0, 3.0, 6.0, 13.0, 17.0, 19.0

def st(sec): return max(0, min(N, int(sec * SR)))

def add(sig, start, left=1.0, right=1.0):
    i0 = st(start); i1 = min(N, i0 + len(sig))
    if i1 <= i0: return
    L[i0:i1] += sig[:i1-i0] * left
    R[i0:i1] += sig[:i1-i0] * right

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

def saw(freq, tt, nh=12):
    """Saw band-limitée par série harmonique."""
    out = np.zeros_like(tt)
    for h in range(1, nh+1):
        if freq*h > 16000: break
        out += np.sin(2*np.pi*freq*h*tt)/h
    return out

def supersaw(freq, dur, vol=1.0, nh=12):
    """Lead festival : 6 saws désaccordées + sous-octave, attaque nette."""
    n = int(dur*SR); tt = np.arange(n)/SR
    out = np.zeros(n)
    for det in (-0.011, -0.006, -0.002, 0.002, 0.006, 0.011):
        out += saw(freq*(1+det), tt, nh)
    out += 0.7*saw(freq/2, tt, 8)
    out /= np.abs(out).max() + 1e-9
    env = np.ones(n)
    a = int(0.012*SR); env[:a] = np.linspace(0, 1, a)
    r = min(n, int(0.09*SR)); env[-r:] *= np.linspace(1, 0, r)
    return out * env * vol

def pluck(freq, dur=0.42, vol=1.0):
    n = int(dur*SR); tt = np.arange(n)/SR
    sig = np.sin(2*np.pi*freq*tt) + 0.45*np.sin(2*np.pi*freq*2*tt) + 0.15*np.sin(2*np.pi*freq*3*tt)
    return sig * np.exp(-tt*9) * vol

def kick_big(t, vol=1.0):
    n = int(0.34*SR); tt = np.arange(n)/SR
    f = 190*np.exp(-tt*26) + 46
    body = np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-tt*10)
    click = band_noise(int(0.012*SR), 4500, 3500, 160) * 0.5
    k = body * 0.47 * vol
    add(k, t); add(click*vol, t)

def clap_fest(t, vol=1.0):
    for off, v in ((0, 1.0), (0.014, 0.7), (0.03, 0.5)):
        add(band_noise(int(0.22*SR), 1700, 1300, 24) * 0.14 * v * vol, t + off)

def snare(t, vol):
    add(band_noise(int(0.12*SR), 1900, 1500, 34) * vol, t)

def roll(start, end, v0=0.05, v1=0.2):
    """Roulement qui s'accélère : croches → 16èmes → 32èmes."""
    t = start
    while t < end - 0.02:
        p = (t - start) / (end - start)
        snare(t, v0 + (v1 - v0) * p)
        step = 0.25 if p < 0.5 else (0.125 if p < 0.8 else 0.0625)
        t += step

def sweep_up(end, dur, vol=0.16):
    n = int(dur*SR); tt = np.arange(n)/SR
    nz = band_noise(n, 2600, 3000, 0)
    add(nz * (tt/dur)**2 * vol, end - dur)

def sweep_down(start, dur=1.6, vol=0.12):
    n = int(dur*SR); tt = np.arange(n)/SR
    nz = band_noise(n, 2600, 3000, 0)
    add(nz * (1 - tt/dur)**2.5 * vol, start)

def impact(t, vol=1.0):
    n = int(0.7*SR); tt = np.arange(n)/SR
    th = np.sin(2*np.pi*(90*np.exp(-tt*7)+30)*tt) * np.exp(-tt*5) * 0.3
    crash = band_noise(int(1.6*SR), 6500, 5000, 3.0) * 0.11
    add(th*vol, t); add(crash*vol, t)

# ═══ mélodie Happy Birthday (do majeur, domaine public) — durées en temps ═══
P1 = [('G3',.5),('G3',.5),('A3',1),('G3',1),('C4',1),('B3',2)]     # happy birthday to you
P2 = [('G3',.5),('G3',.5),('A3',1),('G3',1),('D4',1),('C4',2)]     # happy birthday to you
P3 = [('G3',.5),('G3',.5),('G4',1),('E4',1),('C4',1),('B3',1),('A3',1)]  # happy birthday dear Romain
P4 = [('F4',.5),('F4',.5),('E4',1),('C4',1),('D4',1),('C4',2)]     # happy birthday to you

def play_melody(phr, start, octave=2.0, style='lead', vol=0.16):
    t = start
    for name, beats in phr:
        f = nfreq(name) * octave
        dur = beats * BEAT
        if style == 'lead':
            sig = supersaw(f, dur*0.96, vol)
            add(sig, t, left=0.95, right=1.05)
            add(supersaw(f*2, dur*0.96, vol*0.18, nh=6), t)   # brillance
        else:
            sig = pluck(f, min(0.5, dur), vol)
            add(sig, t, left=0.9, right=1.1)
            add(pluck(f, min(0.5, dur), vol*0.35), t + 0.25, left=1.1, right=0.9)
        t += dur
    return t

# ═══ batterie & basse ═══
t = 0.0
while t < DUR - 0.6:
    in_drop = (DROP1 <= t < BREAK - 0.5) or (DROP2 <= t < DUR - 1.5)
    in_build = (BUILD <= t < DROP1) or (BUILD2 <= t < DROP2)
    vol = 1.0 if in_drop else (0.8 if in_build else 0.7)
    if not (BREAK - 0.5 <= t < BREAK + 3.4):        # le breakdown respire sans kick
        kick_big(t, vol)
    beat_idx = round(t / BEAT)
    if in_drop:
        if beat_idx % 2 == 1: clap_fest(t)
        add(band_noise(int(0.07*SR), 9500, 4200, 80) * 0.06, t + BEAT/2, left=0.8, right=1.2)
        add(band_noise(int(0.05*SR), 11000, 4500, 100) * 0.035, t + BEAT/4)
        add(band_noise(int(0.05*SR), 11000, 4500, 100) * 0.035, t + 3*BEAT/4)
        # basse off-beat big-room (Do)
        fb = nfreq('C2')
        nb = int(0.24*SR); tb = np.arange(nb)/SR
        bass = np.tanh((np.sin(2*np.pi*fb*tb) + 0.6*np.sin(2*np.pi*fb*2*tb))*2.2)
        add(bass * np.exp(-tb*8) * 0.2, t + BEAT/2)
    t += BEAT

# ═══ structure ═══
# intro 0-3 : motif « hap-py » en pluck qui répond au kick
for i, tt0 in enumerate([0.5, 1.0, 2.0, 2.5]):
    f = nfreq('G3') * 2 if i % 2 == 0 else nfreq('A3') * 2
    add(pluck(f, 0.4, 0.11), tt0)
sweep_up(3.0, 1.2, 0.1); impact(3.0, 0.7)

# build 3-6 : arpèges do majeur + roulement + riser
tt0 = 3.0
arp = ['C4','E4','G4','C5']
i = 0
while tt0 < 6.0 - 0.05:
    add(pluck(nfreq(arp[i % 4]), 0.3, 0.09 + 0.05*(tt0-3)/3), tt0, left=0.4+0.02*i, right=1.6-0.02*i)
    i += 1; tt0 += 0.25
roll(4.5, 6.0, 0.05, 0.22)
sweep_up(6.0, 2.0, 0.2)
impact(6.0, 1.2)

# DROP 1 (6-13) : phrases 1 et 2 en supersaw lead
tend = play_melody(P1, 6.0, octave=2.0, style='lead', vol=0.17)
play_melody(P2, tend, octave=2.0, style='lead', vol=0.17)
sweep_down(6.0)

# breakdown 13-17 : phrase 3 (« dear Romain ») en pluck chaleureux + nappe
impact(13.0, 0.8)
nb = int(4.2*SR); tb = np.arange(nb)/SR
for name, v in (('C3',.032),('G3',.028),('E4',.025),('C5',.013)):
    f = nfreq(name)
    pad = np.sin(2*np.pi*f*tb*1.002) + np.sin(2*np.pi*f*tb*0.998)
    env = np.ones(nb); a=int(0.4*SR); env[:a]=np.linspace(0,1,a); r=int(0.8*SR); env[-r:]*=np.linspace(1,0,r)
    add(pad*env*v, 13.0)
play_melody(P3, 13.5, octave=2.0, style='pluck', vol=0.12)

# build 2 (17-19) : la grosse montée
roll(17.0, 19.0, 0.06, 0.26)
sweep_up(19.0, 2.0, 0.24)

# DROP 2 final (19-25.5) : phrase 4 doublée + accord final
impact(19.0, 1.3)
tend = play_melody(P4, 19.0, octave=2.0, style='lead', vol=0.18)
play_melody(P4, tend, octave=4.0, style='pluck', vol=0.1)   # écho aigu scintillant
# accord final Do majeur massif à 24.5
nf = int((DUR-24.5)*SR); tf = np.arange(nf)/SR
for k, name in enumerate(['C2','C3','G3','E4','G4','C5']):
    f = nfreq(name)
    sig = np.sin(2*np.pi*f*tf*1.002)+np.sin(2*np.pi*f*tf*0.998)+0.3*np.sin(2*np.pi*f*2*tf)
    env = np.ones(nf); a=int(0.05*SR); env[:a]=np.linspace(0,1,a)
    pan = 0.5+0.35*np.sin(k*1.7)
    add(sig*env*0.055, 24.5, left=1-pan+0.5, right=pan+0.5)
impact(24.5, 1.1)

# ═══ pompage sidechain global sur les couches soutenues, puis mastering ═══
tt_all = np.arange(N)/SR
pump = 1 - 0.5*np.exp(-((tt_all % BEAT)/0.085)**2)
# le pompage ne s'applique qu'aux sections avec kick 4/4
zone = ((tt_all < BREAK) | (tt_all >= BREAK + 3.4)).astype(float)
gain = zone*pump + (1-zone)*1.0
L *= gain; R *= gain

mix = np.stack([L, R])
fi = int(0.03*SR); mix[:, :fi] *= np.linspace(0, 1, fi)
fo = int(0.8*SR); mix[:, -fo:] *= np.linspace(1, 0, fo)**1.2
mix = np.tanh(mix * 2.4)
mix *= 0.94 / np.abs(mix).max()

pcm = (mix.T * 32767).astype(np.int16)
import wave
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"OK → {OUT} ({DUR}s, peak {np.abs(mix).max():.2f})")
