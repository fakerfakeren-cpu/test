"""Synthesises every Rimeheart sound effect (mono Ogg Vorbis, deterministic)."""
import os

import numpy as np
import soundfile as sf

SR = 44100
OUT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'assets', 'rimeheart', 'sounds')
rng = np.random.default_rng(1234)


def t(sec):
    return np.arange(int(SR * sec)) / SR


def env(n, a=0.01, d=0.3, curve=3.0):
    x = np.linspace(0, 1, n)
    attack = np.clip(x / max(a, 1e-4), 0, 1)
    decay = np.exp(-curve * np.clip(x - a, 0, None) / max(d, 1e-4))
    return attack * decay


def adsr(n, a, s_level, r):
    x = np.linspace(0, 1, n)
    e = np.ones(n) * s_level
    e[x < a] = x[x < a] / a * s_level
    rel = x > (1 - r)
    e[rel] = s_level * (1 - (x[rel] - (1 - r)) / r)
    return e


def noise(n):
    return rng.standard_normal(n)


def lowpass(x, cutoff):
    # one-pole low-pass, cutoff may be an array
    y = np.zeros_like(x)
    c = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    alpha = 1 - np.exp(-2 * np.pi * c / SR)
    acc = 0.0
    for i in range(len(x)):
        acc += alpha[i] * (x[i] - acc)
        y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def sweep(f0, f1, sec, shape='sine', curve=1.0):
    tt = t(sec)
    f = f0 + (f1 - f0) * (tt / sec) ** curve
    ph = 2 * np.pi * np.cumsum(f) / SR
    if shape == 'saw':
        return 2 * ((ph / (2 * np.pi)) % 1.0) - 1
    if shape == 'square':
        return np.sign(np.sin(ph))
    return np.sin(ph)


def tone(freq, sec, harmonics=(1.0,), decay=2.0):
    tt = t(sec)
    y = sum(a * np.sin(2 * np.pi * freq * (i + 1) * tt) * np.exp(-decay * (i + 1) * tt) for i, a in enumerate(harmonics))
    return y


def bell(freq, sec, decay=3.0):
    tt = t(sec)
    partials = [(1.0, 1.0), (2.76, 0.5), (5.4, 0.25), (8.93, 0.12)]
    return sum(a * np.sin(2 * np.pi * freq * r * tt) * np.exp(-decay * r * 0.6 * tt) for r, a in partials)


def mix(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        out[:len(p)] += p
    return out


def pad(x, sec):
    n = int(SR * sec)
    return np.concatenate([np.zeros(n), x])


def save(name, y, gain=0.9):
    y = np.asarray(y, dtype=float)
    fade = min(len(y) // 20, 2000)
    if fade > 0:
        y[-fade:] *= np.linspace(1, 0, fade)
    peak = np.max(np.abs(y)) or 1.0
    y = y / peak * gain
    os.makedirs(OUT, exist_ok=True)
    sf.write(os.path.join(OUT, name + '.ogg'), y.astype(np.float32), SR, format='OGG', subtype='VORBIS')


def boom(sec=2.5, pitch=55):
    n = int(SR * sec)
    sub = sweep(pitch * 2.2, pitch * 0.6, sec) * env(n, 0.005, 0.35, 4)
    crack = lowpass(noise(n), 3000) * env(n, 0.001, 0.08, 6)
    rumble = lowpass(noise(n), 180) * env(n, 0.02, 0.9, 2.5) * 3
    return mix(sub * 1.4, crack * 0.8, rumble)


def whoosh(sec, f0, f1, loud=1.0):
    n = int(SR * sec)
    cut = np.linspace(f0, f1, n)
    y = lowpass(noise(n), cut) * np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return y * loud


def shatter(sec=0.9, base=2600, seed_n=18):
    n = int(SR * sec)
    y = highpass(noise(n), 3000) * env(n, 0.001, 0.05, 8) * 1.2
    parts = [y]
    for k in range(seed_n):
        f = base * (0.6 + rng.random() * 1.6)
        parts.append(pad(bell(f, 0.35, 9) * (0.15 + rng.random() * 0.25), rng.random() * sec * 0.35))
    return mix(*parts)[:n]


def main():
    # freezing crackle
    n = int(SR * 0.7)
    crackle = (rng.random(n) > 0.994) * rng.standard_normal(n) * 3 * np.linspace(1, 0.2, n)
    save('freeze', mix(highpass(crackle, 1500), bell(1975, 0.7, 5) * 0.4, pad(bell(2637, 0.5, 6) * 0.3, 0.08)), 0.7)
    save('ice_shatter1', shatter(0.9, 2600))
    save('ice_shatter2', shatter(0.8, 3100))
    # cold snap: crack + inward whoosh + shimmer
    n = int(SR * 1.1)
    crack = highpass(noise(n), 2500) * env(n, 0.001, 0.04, 9) * 1.5
    save('cold_snap', mix(crack, whoosh(1.1, 5000, 400, 0.7), pad(mix(bell(1568, 0.8, 4), bell(2093, 0.8, 4) * 0.6) * 0.5, 0.05)))
    # glacier slam: deep boom plus shattering ice
    save('glacier_slam', mix(boom(1.8, 45), pad(shatter(0.9, 1800) * 0.7, 0.02)))
    # blizzard wind
    n = int(SR * 1.8)
    tt = t(1.8)
    howl = sweep(420, 640, 1.8) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.9 * tt)) * 0.25
    wind = lowpass(noise(n), 900 + 700 * np.sin(2 * np.pi * 0.6 * tt) ** 2) * 1.6
    save('blizzard', mix(wind, howl) * adsr(n, 0.2, 1, 0.3), 0.7)
    # icicle shot
    n = int(SR * 0.5)
    save('icicle_shoot', mix(whoosh(0.5, 800, 7000, 0.9), bell(2349, 0.4, 7) * 0.35), 0.8)
    # frost wraith voices
    for i, f0 in enumerate((180, 150)):
        dur = 1.8
        n = int(SR * dur)
        tt = t(dur)
        breath = lowpass(highpass(noise(n), 500), 3000) * (0.5 + 0.5 * np.sin(2 * np.pi * (2.5 + i) * tt))
        moan = sum(np.sin(2 * np.pi * f0 * r * tt * (1 + 0.02 * np.sin(2 * np.pi * 4 * tt))) * a for r, a in ((1, 0.5), (2, 0.25), (3.01, 0.12)))
        save(f'wraith_ambient{i + 1}', mix(breath * 0.6, moan * 0.5) * adsr(n, 0.3, 1.0, 0.4), 0.55)
    n = int(SR * 0.45)
    save('wraith_hurt', mix(sweep(900, 300, 0.45) * env(n, 0.005, 0.3, 3), highpass(noise(n), 2000) * env(n, 0.002, 0.1, 6) * 0.5), 0.7)
    n = int(SR * 1.6)
    save('wraith_death', mix(sweep(700, 90, 1.6, curve=0.6) * env(n, 0.01, 0.9, 2), whoosh(1.6, 4000, 300, 0.6), pad(shatter(0.8, 2400) * 0.5, 0.5)), 0.8)
    # shardling clicks
    n = int(SR * 0.6)
    clicks = mix(*(pad(bell(3000 + rng.random() * 1500, 0.06, 20) * 0.8, s) for s in np.sort(rng.uniform(0, 0.5, 9))))[:n]
    save('shardling_chitter', clicks, 0.6)
    # winter horn
    dur = 2.6
    n = int(SR * dur)
    tt = t(dur)
    f = 146.8 * (1 + 0.02 * np.minimum(1, tt / 0.4)) * (1 + 0.006 * np.sin(2 * np.pi * 5 * tt))
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1.0) - 1
    horn = lowpass(saw + 0.5 * np.sin(ph * 2) + 0.3 * np.sin(ph * 3), 1200) * adsr(n, 0.15, 1.0, 0.3)
    save('winter_horn', mix(horn, lowpass(noise(n), 300) * adsr(n, 0.2, 1, 0.3) * 0.5), 0.85)
    # sovereign
    for i, p in enumerate((1.0, 0.85)):
        dur = 2.6
        n = int(SR * dur)
        tt = t(dur)
        f = (80 * p) * (1 + 0.03 * np.sin(2 * np.pi * 5 * tt)) * (1 - 0.25 * tt / dur)
        ph = 2 * np.pi * np.cumsum(f) / SR
        saw = 2 * ((ph / (2 * np.pi)) % 1.0) - 1
        roar = np.tanh(2.2 * (saw + 0.5 * np.sin(ph * 1.5) + 0.3 * lowpass(noise(n), 900)))
        roar = lowpass(roar, 1800) * adsr(n, 0.1, 1.0, 0.35)
        shimmer = highpass(noise(n), 5000) * adsr(n, 0.3, 1, 0.3) * 0.3
        save(f'sovereign_roar{i + 1}', mix(roar, shimmer, lowpass(noise(n), 120) * adsr(n, 0.1, 1, 0.4) * 1.5))
    n = int(SR * 4.0)
    tt = t(4.0)
    f = 70 * (1 - 0.5 * tt / 4.0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    death = lowpass(np.tanh(2 * (2 * ((ph / (2 * np.pi)) % 1.0) - 1)), 1500) * adsr(n, 0.05, 1, 0.5)
    cascade = mix(*(pad(shatter(0.7, 2000 + k * 250) * 0.5, 0.4 + k * 0.35) for k in range(8)))
    save('sovereign_death', mix(death, cascade[:n]))
    print('sounds written')


if __name__ == '__main__':
    main()
