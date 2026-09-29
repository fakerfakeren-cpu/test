"""Sound synthesis toolkit for Oathbound.

Everything is built from oscillators, noise, envelopes, filters and a convolution reverb. Positional sounds
are mono (Minecraft only attenuates mono sources); music and ambience beds are stereo.
"""
import math

import numpy as np
from scipy import signal

SR = 44100
RNG = np.random.default_rng(1234)


def t(dur):
    return np.arange(int(dur * SR)) / SR


def seconds(x):
    return len(x) / SR


# ------------------------------------------------------------------ oscillators and noise
def _freq(freq, n):
    if np.ndim(freq) == 0:
        return np.full(n, float(freq))
    f = np.asarray(freq, dtype=float)
    if len(f) >= n:
        return f[:n]
    return np.concatenate([f, np.full(n - len(f), f[-1] if len(f) else 0.0)])


def sine(freq, dur, phase=0.0):
    """freq may be a number or an array (instantaneous frequency)."""
    n = int(dur * SR)
    f = _freq(freq, n)
    ph = 2 * np.pi * np.cumsum(f) / SR + phase
    return np.sin(ph)


def saw(freq, dur, harmonics=40):
    n = int(dur * SR)
    f = _freq(freq, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.zeros(n)
    fmax = float(np.max(f))
    for k in range(1, harmonics + 1):
        if k * fmax > SR * 0.45:
            break
        out += np.sin(k * ph) / k
    return out * (2 / np.pi)


def square(freq, dur, harmonics=30):
    n = int(dur * SR)
    f = _freq(freq, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.zeros(n)
    fmax = float(np.max(f))
    for k in range(1, harmonics * 2, 2):
        if k * fmax > SR * 0.45:
            break
        out += np.sin(k * ph) / k
    return out * (4 / np.pi)


def noise(dur, color='white', seed=None):
    r = np.random.default_rng(seed) if seed is not None else RNG
    n = int(dur * SR)
    w = r.standard_normal(n)
    if color == 'white':
        return w / 3
    if color == 'pink':
        b, a = [0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400]
        return signal.lfilter(b, a, w) * 2.5
    if color == 'brown':
        x = np.cumsum(w)
        x = x - signal.lfilter([1], [1, -0.995], x) * 0.005
        x = signal.lfilter([1, -1], [1, -0.999], x)
        return x / (np.max(np.abs(x)) + 1e-9)
    raise ValueError(color)


# ------------------------------------------------------------------ envelopes
def env_adsr(dur, a=0.01, d=0.1, s=0.7, r=0.2):
    n = int(dur * SR)
    e = np.zeros(n)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    ns = max(0, n - na - nd - nr)
    parts = [np.linspace(0, 1, na, endpoint=False), np.linspace(1, s, nd, endpoint=False), np.full(ns, s), np.linspace(s, 0, nr)]
    x = np.concatenate(parts)
    e[:min(n, len(x))] = x[:n]
    return e


def env_exp(dur, decay, attack=0.002):
    tt = t(dur)
    e = np.exp(-tt / max(decay, 1e-4))
    na = int(attack * SR)
    if na > 0:
        e[:na] *= np.linspace(0, 1, na)
    return e


def env_swell(dur, peak=0.5, shape=2.0):
    tt = t(dur) / dur
    up = (tt / peak) ** shape
    down = ((1 - tt) / (1 - peak)) ** shape
    return np.where(tt < peak, up, down)


def glide(f0, f1, dur, curve='exp'):
    tt = t(dur) / dur
    if curve == 'exp':
        return f0 * (f1 / f0) ** tt
    return f0 + (f1 - f0) * tt


# ------------------------------------------------------------------ filters
def lowpass(x, cutoff, q=0.707):
    if np.ndim(cutoff) == 0:
        b, a = signal.butter(2, min(cutoff, SR * 0.45) / (SR / 2), 'low')
        return signal.lfilter(b, a, x)
    return tv_filter(x, cutoff, 'low', q)


def highpass(x, cutoff):
    b, a = signal.butter(2, min(cutoff, SR * 0.45) / (SR / 2), 'high')
    return signal.lfilter(b, a, x)


def bandpass(x, center, q=4.0):
    if np.ndim(center) == 0:
        w0 = 2 * np.pi * min(center, SR * 0.45) / SR
        alpha = np.sin(w0) / (2 * q)
        b = [alpha, 0, -alpha]
        a = [1 + alpha, -2 * np.cos(w0), 1 - alpha]
        return signal.lfilter(b, a, x)
    return tv_filter(x, center, 'band', q)


def tv_filter(x, cutoff, kind, q=0.707, block=256):
    """Time-varying biquad applied block by block (state carried across blocks)."""
    out = np.zeros_like(x)
    zi = np.zeros(2)
    cutoff = np.asarray(cutoff, dtype=float)
    for i in range(0, len(x), block):
        c = float(cutoff[min(i, len(cutoff) - 1)])
        w0 = 2 * np.pi * min(max(c, 20.0), SR * 0.45) / SR
        alpha = np.sin(w0) / (2 * q)
        cw = np.cos(w0)
        if kind == 'low':
            b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]
        elif kind == 'band':
            b = [alpha, 0, -alpha]
        else:
            b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]
        a = [1 + alpha, -2 * cw, 1 - alpha]
        b = np.array(b) / a[0]
        a = np.array(a) / a[0]
        out[i:i + block], zi = signal.lfilter(b, a, x[i:i + block], zi=zi)
    return out


FORMANTS = {
    'a': [(800, 1.0, 80), (1150, 0.5, 90), (2900, 0.25, 120)],
    'o': [(450, 1.0, 70), (800, 0.4, 80), (2830, 0.15, 100)],
    'u': [(325, 1.0, 50), (700, 0.3, 60), (2530, 0.1, 170)],
    'e': [(400, 1.0, 60), (1600, 0.4, 80), (2700, 0.25, 120)],
    'i': [(250, 1.0, 60), (1750, 0.3, 90), (2600, 0.2, 100)],
}


def formant(x, vowel, shift=1.0):
    out = np.zeros_like(x)
    for f, g, bw in FORMANTS[vowel]:
        out += bandpass(x, f * shift, q=f * shift / bw) * g
    return out


# ------------------------------------------------------------------ effects
def reverb(x, length=2.0, decay=0.5, mix=0.3, stereo=False, predelay=0.01, bright=6000, seed=7):
    """Convolution reverb with a synthetic, exponentially decaying, filtered-noise impulse response."""
    r = np.random.default_rng(seed)
    n = int(length * SR)
    tt = np.arange(n) / SR
    chans = 2 if stereo else 1
    x2 = x if x.ndim == 2 else np.stack([x] * chans, axis=1) if stereo else x[:, None]
    out = []
    for c in range(chans):
        ir = r.standard_normal(n) * np.exp(-tt / decay)
        ir = lowpass(ir, bright)
        ir[:int(predelay * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
        src = x2[:, min(c, x2.shape[1] - 1)]
        wet = pad_to(signal.fftconvolve(src, ir), len(src) + n)
        dry = np.concatenate([src, np.zeros(n)])
        out.append(dry * (1 - mix) + wet * mix)
    y = np.stack(out, axis=1)
    return y if stereo else y[:, 0]


def echo(x, delay=0.25, feedback=0.4, taps=4):
    n = len(x)
    d = int(delay * SR)
    out = np.concatenate([x, np.zeros(d * taps)])
    g = 1.0
    for k in range(1, taps + 1):
        g *= feedback
        out[k * d:k * d + n] += x * g
    return out


def drive(x, amount=2.0):
    return np.tanh(x * amount) / np.tanh(amount)


def pad_to(x, n):
    if len(x) >= n:
        return x[:n]
    return np.concatenate([x, np.zeros(n - len(x))]) if x.ndim == 1 else np.concatenate([x, np.zeros((n - len(x), x.shape[1]))])


def mix(*parts):
    n = max(len(p[0]) if isinstance(p, tuple) else len(p) for p in parts)
    out = np.zeros(n)
    for item in parts:
        p, g = item if isinstance(item, tuple) else (item, 1.0)
        out[:len(p)] += p * g
    return out


def at(x, offset, total=None):
    """Shifts a sound to start `offset` seconds later."""
    pad = np.zeros(int(offset * SR))
    y = np.concatenate([pad, x])
    return pad_to(y, int(total * SR)) if total else y


def normalize(x, peak=0.89):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


def fade(x, fin=0.005, fout=0.02):
    x = x.copy()
    a, b = int(fin * SR), int(fout * SR)
    if a:
        x[:a] *= np.linspace(0, 1, a)[:, None] if x.ndim == 2 else np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)[:, None] if x.ndim == 2 else np.linspace(1, 0, b)
    return x


# ------------------------------------------------------------------ instruments
BELL_PARTIALS = [(0.5, 0.6, 1.6), (1.0, 1.0, 1.0), (1.183, 0.7, 0.8), (1.506, 0.55, 0.6), (2.0, 0.45, 0.5),
                 (2.514, 0.35, 0.35), (2.662, 0.3, 0.3), (3.011, 0.22, 0.25), (4.166, 0.15, 0.18), (5.433, 0.1, 0.12)]


def bell(freq, dur=3.0, decay=1.4, bright=1.0, detune=0.0):
    out = np.zeros(int(dur * SR))
    for ratio, amp, dk in BELL_PARTIALS:
        f = freq * ratio * (1 + detune * (RNG.random() - 0.5) * 0.01)
        if f > SR * 0.45:
            continue
        a = amp * (bright if ratio > 2 else 1.0)
        out += sine(f, dur, RNG.random() * 6.28) * env_exp(dur, decay * dk, 0.001) * a
    strike = lowpass(noise(0.03), 4000) * env_exp(0.03, 0.008)
    out[:len(strike)] += strike * 0.3
    return out


def chime(freq, dur=1.6, decay=0.6):
    out = sine(freq, dur) * env_exp(dur, decay) + 0.35 * sine(freq * 2.76, dur) * env_exp(dur, decay * 0.5) \
        + 0.2 * sine(freq * 5.4, dur) * env_exp(dur, decay * 0.25)
    return out


def pluck(freq, dur=1.5, damp=0.996, bright=0.5):
    n = int(dur * SR)
    period = max(2, int(SR / freq))
    buf = RNG.uniform(-1, 1, period)
    buf = lowpass(buf, 2000 + bright * 8000) if period > 12 else buf
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % period]
        nxt = (i + 1) % period
        buf[i % period] = damp * 0.5 * (buf[i % period] + buf[nxt])
    return out


def pad(freq, dur, voices=3, detune=0.008, cutoff=1400, attack=0.6, release=1.0, kind='saw'):
    out = np.zeros(int(dur * SR))
    for v in range(voices):
        d = 1 + detune * (v - (voices - 1) / 2)
        osc = saw(freq * d, dur, 24) if kind == 'saw' else square(freq * d, dur, 12)
        out += osc
    out = lowpass(out / voices, cutoff)
    return out * env_adsr(dur, attack, 0.2, 0.85, release)


def strings(freq, dur, attack=0.25, release=0.5, cutoff=2400, vib=5.0):
    vibr = 1 + 0.004 * np.sin(2 * np.pi * vib * t(dur)) * np.clip(t(dur) / 0.4, 0, 1)
    out = np.zeros(int(dur * SR))
    for d in (0.996, 1.0, 1.004, 1.008):
        out += saw(freq * d * vibr, dur, 30)
    return lowpass(out / 4, cutoff) * env_adsr(dur, attack, 0.1, 0.9, release)


def choir(freq, dur, vowel='a', attack=0.4, release=0.8, voices=4):
    out = np.zeros(int(dur * SR))
    for v in range(voices):
        vib = 1 + 0.006 * np.sin(2 * np.pi * (4.8 + v * 0.37) * t(dur) + v)
        src = saw(freq * (1 + 0.006 * (v - 1.5)) * vib, dur, 40) + 0.05 * noise(dur)
        out += formant(src, vowel)
    return out / voices * env_adsr(dur, attack, 0.1, 0.9, release) * 3


def horn(freq, dur, attack=0.08, release=0.3, bright=2600):
    e = env_adsr(dur, attack, 0.15, 0.8, release)
    src = saw(freq * (1 + 0.003 * np.sin(2 * np.pi * 5 * t(dur))), dur, 30)
    return lowpass(src, 400 + bright * e) * e


def drum(freq=60, dur=0.8, click=0.3, drop=3.0):
    f = freq * (1 + drop * np.exp(-t(dur) / 0.03))
    body = sine(f, dur) * env_exp(dur, 0.18)
    c = highpass(noise(0.02), 1500) * env_exp(0.02, 0.004)
    body[:len(c)] += c * click
    return body


def snare(dur=0.35):
    return (bandpass(noise(dur), 2200, 0.8) * env_exp(dur, 0.07) + 0.4 * sine(190, dur) * env_exp(dur, 0.05))


def cymbal(dur=1.5):
    return highpass(noise(dur), 5000) * env_exp(dur, 0.4) * 0.6


def whoosh(dur=0.5, f0=400, f1=2500, q=1.2, color='pink'):
    n = noise(dur, color)
    return bandpass(n, glide(f0, f1, dur), q) * env_swell(dur, 0.55, 1.5)


def crackle(dur, density=120, seed=3):
    r = np.random.default_rng(seed)
    out = np.zeros(int(dur * SR))
    for _ in range(int(density * dur)):
        i = r.integers(0, len(out) - 200)
        L = r.integers(20, 180)
        out[i:i + L] += r.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * r.uniform(0.3, 1)
    return highpass(out, 1200)


def clink(freq, dur=0.5):
    out = np.zeros(int(dur * SR))
    for ratio, amp in ((1.0, 1.0), (2.41, 0.6), (3.89, 0.4), (5.3, 0.25)):
        out += sine(freq * ratio, dur) * env_exp(dur, 0.12 / ratio ** 0.5) * amp
    return out


def rumble(dur, cutoff=120):
    return lowpass(noise(dur, 'brown'), cutoff) * 2.5


def note(name):
    names = {'C': -9, 'C#': -8, 'Db': -8, 'D': -7, 'D#': -6, 'Eb': -6, 'E': -5, 'F': -4, 'F#': -3, 'Gb': -3, 'G': -2, 'G#': -1,
             'Ab': -1, 'A': 0, 'A#': 1, 'Bb': 1, 'B': 2}
    pitch, octave = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((names[pitch] + (octave - 4) * 12) / 12)
