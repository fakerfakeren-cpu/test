"""Synthesises every Astralfall sound effect (mono Ogg Vorbis, deterministic)."""
import os

import numpy as np
import soundfile as sf

SR = 44100
OUT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'assets', 'astralfall', 'sounds')
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


def main():
    # meteors
    for i, (dur, p) in enumerate(((3.2, 1.0), (2.6, 1.15))):
        n = int(SR * dur)
        whistle = sweep(1800 * p, 350 * p, dur, curve=0.7) * np.linspace(0.2, 1, n) ** 2 * 0.35
        roar = lowpass(noise(n), np.linspace(400, 2500, n)) * np.linspace(0.1, 1, n) ** 2
        crackle = (rng.random(n) > 0.9985) * rng.standard_normal(n) * 4 * np.linspace(0, 1, n)
        save(f'meteor_incoming{i + 1}', mix(whistle, roar, crackle))
    save('meteor_impact1', boom(2.8, 50))
    save('meteor_impact2', boom(2.4, 62))
    # chimes
    for i, root in enumerate((880, 1046.5, 1318.5)):
        save(f'star_chime{i + 1}', mix(bell(root, 2.0), pad(bell(root * 1.5, 1.6) * 0.6, 0.12), pad(bell(root * 2, 1.2) * 0.35, 0.25)), 0.7)
    n = int(SR * 5)
    chord = sum(np.sin(2 * np.pi * f * t(5)) for f in (110, 164.8, 220, 261.6, 329.6)) * adsr(n, 0.4, 1.0, 0.3)
    chord = lowpass(chord, np.linspace(200, 2000, n))
    sparkle = mix(*(pad(bell(f, 1.0) * 0.3, s) for f, s in ((1760, 1.0), (2093, 1.8), (1568, 2.6), (2637, 3.3))))
    save('starstorm', mix(chord, sparkle))
    # wisp
    for i, base in enumerate((1568, 1760)):
        y = mix(*(pad(bell(base * r, 0.5, 6) * 0.5, k * 0.07) for k, r in enumerate((1, 1.25, 1.5, 2))))
        save(f'wisp_ambient{i + 1}', y, 0.5)
    save('wisp_hurt', sweep(2400, 900, 0.3) * env(int(SR * 0.3), 0.005, 0.2, 3), 0.6)
    # stalker
    for i in range(2):
        n = int(SR * 2.2)
        base = lowpass(highpass(noise(n), 800), 4500)
        formant = 0.5 + 0.5 * np.sin(2 * np.pi * (3 + i) * t(2.2)) * np.sin(2 * np.pi * 0.7 * t(2.2))
        save(f'stalker_ambient{i + 1}', base * formant * adsr(n, 0.2, 1.0, 0.4), 0.6)
    n = int(SR * 1.3)
    scream = np.tanh(3 * (sweep(900, 180, 1.3, 'saw') + 0.4 * sweep(1210, 250, 1.3, 'saw')))
    scream = mix(scream * env(n, 0.02, 0.8, 1.5), highpass(noise(n), 2000) * env(n, 0.01, 0.5, 2) * 0.5)
    save('stalker_scream', scream)
    n = int(SR * 0.45)
    blink = whoosh(0.45, 300, 6000)[::-1] + sweep(200, 1600, 0.45) * env(n, 0.3, 0.2, 4) * 0.4
    save('stalker_blink', blink)
    # crawler
    n = int(SR * 1.6)
    rolls = mix(lowpass(noise(n), 250) * 2, *(pad(lowpass(noise(int(SR * 0.05)), 3000) * 0.8, s) for s in rng.uniform(0, 1.5, 14)))[:n]
    save('crawler_roll', rolls * adsr(n, 0.1, 1, 0.3))
    save('crawler_hurt', mix(lowpass(noise(int(SR * 0.4)), 1200) * env(int(SR * 0.4), 0.002, 0.15, 5), sweep(160, 60, 0.4) * env(int(SR * 0.4), 0.002, 0.3, 3)))
    # gazer
    n = int(SR * 2.0)
    charge = sweep(200, 1400, 2.0, curve=1.6) * (0.6 + 0.4 * np.sin(2 * np.pi * np.linspace(4, 24, n) * t(2.0))) * np.linspace(0.2, 1, n)
    save('gazer_charge', charge, 0.7)
    n = int(SR * 0.9)
    beam = np.tanh(2 * (sweep(1400, 300, 0.9, 'saw') + sweep(700, 150, 0.9, 'square') * 0.5)) * env(n, 0.003, 0.5, 2)
    save('gazer_beam', mix(beam, whoosh(0.9, 800, 4000, 0.6)))
    # boss
    for i, p in enumerate((1.0, 0.85)):
        dur = 2.8
        n = int(SR * dur)
        vib = 1 + 0.03 * np.sin(2 * np.pi * 6 * t(dur))
        tt = t(dur)
        f = (95 * p) * vib * (1 - 0.3 * tt / dur)
        ph = 2 * np.pi * np.cumsum(f) / SR
        saw = 2 * ((ph / (2 * np.pi)) % 1.0) - 1
        roar = np.tanh(2.5 * (saw + 0.5 * np.sin(ph * 1.5) + 0.3 * lowpass(noise(n), 900)))
        roar = lowpass(roar, 2200) * adsr(n, 0.08, 1.0, 0.35)
        save(f'boss_roar{i + 1}', mix(roar, lowpass(noise(n), 120) * adsr(n, 0.1, 1, 0.4) * 2))
    n = int(SR * 5.5)
    drone = sum(np.sin(2 * np.pi * f * t(5.5)) * a for f, a in ((41.2, 1.0), (55, 0.7), (82.4, 0.5), (110, 0.3)))
    choir = lowpass(sum(sweep(f, f * 1.5, 5.5, 'saw') for f in (220, 277, 330)), 1500) * np.linspace(0, 1, n) ** 2 * 0.4
    save('boss_summon', mix(drone * adsr(n, 0.2, 1, 0.2), choir))
    n = int(SR * 3.0)
    tt = t(3.0)
    beam = (np.sin(2 * np.pi * 220 * tt) + 0.6 * np.sin(2 * np.pi * 330 * tt) + 0.4 * np.sin(2 * np.pi * 660 * tt + np.sin(2 * np.pi * 7 * tt)))
    beam = np.tanh(1.5 * beam) * adsr(n, 0.05, 1, 0.2) + highpass(noise(n), 3000) * 0.15
    save('boss_beam', beam, 0.8)
    death = mix(boom(3.0, 40), pad(boom(2.0, 60) * 0.7, 0.8), pad(sum(sweep(f, f * 0.5, 4.0) for f in (440, 554, 659)) * env(int(SR * 4.0), 0.3, 1.5, 1.5) * 0.5, 1.2))
    save('boss_death', death)
    save('shockwave', mix(boom(1.6, 70), whoosh(1.2, 200, 3000, 0.8)))
    # singularity
    n = int(SR * 2.0)
    tt = t(2.0)
    hum = (np.sin(2 * np.pi * 48 * tt) + 0.5 * np.sin(2 * np.pi * 96.5 * tt)) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * tt))
    save('singularity_hum', mix(hum, lowpass(noise(n), 300) * 0.4) * adsr(n, 0.2, 1, 0.3), 0.7)
    rev = whoosh(1.2, 200, 5000)[::-1] * np.linspace(0.2, 1.5, int(SR * 1.2))
    save('singularity_collapse', mix(rev, pad(boom(2.0, 45), 1.1)))
    # player weapons
    for i, (f0, f1) in enumerate(((900, 5500), (700, 4800))):
        save(f'star_slash{i + 1}', mix(whoosh(0.35, f0, f1), pad(bell(2093 + i * 200, 0.6, 6) * 0.3, 0.08)))
    n = int(SR * 0.4)
    save('star_bolt', mix(sweep(2600, 1200, 0.4) * env(n, 0.002, 0.25, 4), bell(3136, 0.4, 8) * 0.4), 0.7)
    n = int(SR * 0.9)
    tt = t(0.9)
    grab = np.sin(2 * np.pi * (180 + 300 * tt) * tt + 3 * np.sin(2 * np.pi * 9 * tt)) * adsr(n, 0.05, 1, 0.3)
    save('gravity_grab', grab, 0.7)
    save('gravity_throw', mix(whoosh(0.6, 400, 6000, 1.2), sweep(600, 120, 0.6) * env(int(SR * 0.6), 0.005, 0.4, 3) * 0.5))
    n = int(SR * 0.5)
    tt = t(0.5)
    zap = np.sin(2 * np.pi * (1200 * np.exp(-6 * tt)) * tt * 8) * env(n, 0.002, 0.3, 3)
    save('void_blink', mix(zap, whoosh(0.5, 3000, 300, 0.6)))
    nova = mix(boom(3.0, 45), whoosh(2.0, 300, 7000, 0.8), pad(sum(bell(f, 2.5, 1.5) for f in (523, 659, 784, 1046)) * 0.4, 0.3))
    save('eclipse_nova', nova)
    n = int(SR * 2.4)
    grind = lowpass(noise(n), 500 + 300 * np.sin(2 * np.pi * 11 * t(2.4))) * adsr(n, 0.05, 1, 0.3) * 1.5
    save('vault_open', mix(grind, pad(bell(659, 2.0) * 0.5, 1.4), pad(bell(988, 1.5) * 0.4, 1.6)))
    print('sounds written:', len([f for f in os.listdir(OUT) if f.endswith('.ogg')]))


if __name__ == '__main__':
    main()
