"""Original synthesized sound effects for the Scar viewmodel (44.1 kHz mono): Fire, MagOut, MagIn, Tap,
RackBack, RackRelease, Equip. Layers: noise transients, damped metallic partials, low knocks, filtered
friction noise and a short synthetic room tail."""
import numpy as np, soundfile as sf, sys, os
SR = 44100
rng = np.random.default_rng(7)
def secs(d): return int(round(d * SR))
def tt(n): return np.arange(n) / SR
def noise(d): return rng.standard_normal(secs(d))
def sinc_kernel(fc, taps=301):
    n = np.arange(taps) - (taps - 1) / 2
    h = np.sinc(2 * fc / SR * n) * np.blackman(taps)
    return h / h.sum()
def lowpass(x, fc):
    h = sinc_kernel(fc); s0 = (len(h) - 1) // 2
    return np.convolve(x, h)[s0:s0 + len(x)]   # centred, same length as x (works for short x too)
def highpass(x, fc): return x - lowpass(x, fc)
def bandpass(x, f1, f2): return lowpass(highpass(x, f1), f2)
def env(d, attack, tau, hold=0.0):
    t = tt(secs(d)); e = np.exp(-np.maximum(t - attack - hold, 0) / tau)
    if attack > 0: e *= np.minimum(t / attack, 1)
    return e
def damped(f, tau, d, phase=0.0):
    t = tt(secs(d)); return np.sin(2 * np.pi * f * t + phase) * np.exp(-t / tau)
def sweep(f0, f1, glide, tau, d):
    t = tt(secs(d)); f = f1 + (f0 - f1) * np.exp(-t / glide)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / tau)
def metal(freqs, taus, d, gains=None):
    gains = gains or [1.0] * len(freqs)
    return sum(g * damped(f * (1 + 0.003 * rng.standard_normal()), ta, d, rng.uniform(0, 6.28)) for f, ta, g in zip(freqs, taus, gains))
def click(d=0.0025, hp=2500): return highpass(noise(d), hp) * env(d, 0.0002, d / 3)
def mix(*xs):
    out = np.zeros(max(len(x) for x in xs))
    for x in xs: out[:len(x)] += x
    return out
def place(buf, sig, at, gain=1.0):
    i = secs(at); j = min(len(buf), i + len(sig)); buf[i:j] += gain * sig[:j - i]
def reverb(x, wet, tau=0.22, d=0.5):
    ir = lowpass(noise(d), 3500) * np.exp(-tt(secs(d)) / tau); ir /= np.sqrt((ir ** 2).sum())
    y = np.convolve(x, ir)[:len(x)]
    return x + wet * y * (np.abs(x).max() / (np.abs(y).max() + 1e-9))
def finish(x, peak_db, drive=0.0):
    if drive > 0: x = np.tanh(drive * x / np.abs(x).max()) / np.tanh(drive)
    fade = secs(0.02); x[-fade:] *= np.linspace(1, 0, fade)
    return x / np.abs(x).max() * 10 ** (peak_db / 20)

def fire():
    d = 0.8; b = np.zeros(secs(d))
    place(b, click(0.003, 3000), 0, 0.9)                                            # supersonic crack
    place(b, lowpass(noise(0.2), 4500) * env(0.2, 0.0005, 0.02), 0, 1.25)           # blast
    place(b, bandpass(noise(0.3), 120, 1200) * env(0.3, 0.001, 0.06), 0, 0.9)       # body
    place(b, sweep(95, 50, 0.02, 0.035, 0.25), 0, 0.55)                             # short low thump
    place(b, mix(metal([2300, 3700, 5600], [0.007, 0.005, 0.004], 0.06), click(0.0015)), 0.022, 0.25)  # action cycles
    place(b, metal([2000, 3300], [0.006, 0.004], 0.05), 0.056, 0.14)                # bolt home
    place(b, lowpass(noise(0.7), 1500) * env(0.7, 0.004, 0.22), 0.005, 0.22)        # tail
    return finish(reverb(b, 0.12, tau=0.2), -1.0, drive=2.5)
def mag_out():
    d = 0.42; b = np.zeros(secs(d))
    place(b, mix(metal([1900, 3100], [0.006, 0.004], 0.04), click(0.0015, 2000)), 0, 0.7)      # release catch
    rough = 1 + 0.45 * lowpass(rng.standard_normal(secs(0.12)), 60) / 0.05
    place(b, bandpass(noise(0.12), 700, 3000) * env(0.12, 0.015, 0.04, 0.03) * np.clip(rough, 0.2, 2), 0.008, 0.35)
    place(b, mix(damped(220, 0.018, 0.08), bandpass(noise(0.08), 300, 1200) * env(0.08, 0.001, 0.015)), 0.10, 0.35)
    place(b, click(0.0012, 2500), 0.14, 0.12); place(b, click(0.0012, 2500), 0.165, 0.08)  # rattle
    return finish(reverb(b, 0.05, tau=0.12), -3.0)
def mag_in():
    d = 0.42; b = np.zeros(secs(d))
    place(b, bandpass(noise(0.06), 600, 2500) * env(0.06, 0.04, 0.01), 0, 0.3)      # sliding in
    seat = 0.055
    place(b, damped(170, 0.03, 0.15), seat, 0.6)                                    # knock
    place(b, metal([1250, 2050, 3300, 4700], [0.018, 0.012, 0.009, 0.006], 0.1, [1, .8, .6, .4]), seat, 0.5)
    place(b, click(0.002, 2000), seat, 0.6)
    place(b, metal([2600, 4100], [0.004, 0.004], 0.03), seat + 0.025, 0.35)         # latch
    return finish(reverb(b, 0.045, tau=0.12), -3.0, drive=1.4)
def tap():
    d = 0.3; b = np.zeros(secs(d))
    place(b, mix(damped(120, 0.025, 0.15), 0.6 * damped(90, 0.03, 0.15)), 0, 0.6)
    place(b, lowpass(noise(0.08), 1800) * env(0.08, 0.0005, 0.012), 0, 0.5)
    place(b, damped(1600, 0.025, 0.1), 0.003, 0.08)
    return finish(reverb(b, 0.04, tau=0.12), -4.0)
def rack_back():
    d = 0.36; b = np.zeros(secs(d))
    place(b, damped(2200, 0.004, 0.03), 0, 0.3)                                      # unlock
    n = secs(0.135); seg = np.zeros(n); src = noise(0.135); tn = np.linspace(0, 1, n)
    centres = np.linspace(0, 1, 8)
    for k, c in enumerate(centres):                                                  # friction rising in pitch,
        f = 900 + (2800 - 900) * c                                                   # bands crossfaded smoothly
        w = np.clip(1 - np.abs(tn - c) / (centres[1] - centres[0]), 0, 1)
        seg += bandpass(src, f * 0.7, f * 1.3) * w
    seg *= env(0.135, 0.02, 0.02, 0.09)
    place(b, seg, 0.005, 0.4)
    place(b, damped(1800, 0.05, 0.14), 0.01, 0.03)                                    # faint spring ring
    place(b, mix(metal([1700, 2900], [0.006, 0.004], 0.05), click(0.002, 2000)), 0.135, 0.55)  # hits the stop
    return finish(reverb(b, 0.04, tau=0.12), -3.0)
def rack_release():
    d = 0.46; b = np.zeros(secs(d))
    place(b, bandpass(noise(0.03), 1000, 4000) * env(0.03, 0.005, 0.01), 0, 0.3)     # spring snap
    hit = 0.025
    place(b, click(0.002, 2500), hit, 0.8)
    place(b, metal([1500, 2400, 3800, 5200], [0.025, 0.018, 0.012, 0.008], 0.15, [1, .8, .6, .4]), hit, 0.6)
    place(b, damped(190, 0.035, 0.15), hit, 0.6)
    place(b, metal([1800, 3000], [0.008, 0.008], 0.05), hit + 0.012, 0.3)            # second clack
    return finish(reverb(b, 0.05, tau=0.12), -2.0, drive=1.6)
def equip():
    d = 0.5; b = np.zeros(secs(d))
    am = np.clip(1 + 0.8 * lowpass(rng.standard_normal(secs(0.34)), 30) / 0.03, 0.1, 2.5)
    place(b, highpass(lowpass(noise(0.34), 3000), 300) * env(0.34, 0.08, 0.09, 0.06) * am, 0, 0.35)   # cloth
    place(b, metal([3200, 4500], [0.02, 0.015], 0.08), 0.15, 0.05)                   # small jingle
    place(b, mix(damped(300, 0.015, 0.08), 0.5 * damped(2400, 0.004, 0.03)), 0.28, 0.35)  # grip settles
    return finish(reverb(b, 0.04, tau=0.12), -5.0)

SOUNDS = {'Fire': fire, 'MagOut': mag_out, 'MagIn': mag_in, 'Tap': tap, 'RackBack': rack_back,
          'RackRelease': rack_release, 'Equip': equip}
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for name, fn in SOUNDS.items():
    x = fn().astype(np.float32)
    sf.write(f'{out}/Scar_{name}.wav', x, SR, subtype='PCM_16')
    sf.write(f'{out}/Scar_{name}.ogg', x, SR, format='OGG', subtype='VORBIS')
    print(f'{name:12s} {len(x)/SR:.2f} s  peak {20*np.log10(np.abs(x).max()):.1f} dBFS  rms {20*np.log10(np.sqrt((x**2).mean())):.1f} dBFS')
