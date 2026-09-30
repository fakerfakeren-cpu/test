"""Voices of the wider roster (fauna.py): calls, cries and warnings, synthesised like the rest of Oathbound's sound.

sounds.py merges VOICES into its SFX table: name -> (function(variant) -> mono array, variants, subtitle).
"""
import numpy as np

from . import audio as A


def _rv(x, length=1.2, decay=0.4, mix=0.3):
    return A.reverb(x, length, decay, mix)


def fawn_call(i):
    d = 0.6
    f = A._freq(np.concatenate([A.glide(620 + 40 * i, 880 + 30 * i, 0.2), A.glide(880 + 30 * i, 700, 0.4)]), int(d * A.SR))
    f = f * (1 + 0.012 * np.sin(2 * np.pi * 7 * A.t(d)))
    bleat = A.formant(A.saw(f, d, 24), 'e', 1.1) * A.env_swell(d, 0.25, 1.4)
    return _rv(bleat * 0.8, 1.6, 0.6, 0.35)


def fawn_hurt(i):
    d = 0.3
    return A.formant(A.saw(A.glide(1100 + 60 * i, 800, d), d, 24), 'i', 1.2) * A.env_exp(d, 0.12)


def hare_squeak(i):
    d = 0.16
    return A.formant(A.saw(A.glide(1500 + 150 * i, 1900, d), d, 16), 'i', 1.4) * A.env_exp(d, 0.06)


def tortoise_hiss(i):
    d = 0.9
    hiss = A.bandpass(A.noise(d, 'white', seed=300 + i), 3200 + 300 * i, 1.4) * A.env_swell(d, 0.2, 1.0)
    return hiss * 0.7


def beetle_click(i):
    r = np.random.default_rng(310 + i)
    out = np.zeros(int(0.4 * A.SR))
    for k in range(r.integers(3, 6)):
        c = A.highpass(A.noise(0.012, 'white', seed=311 + k + i * 7), 3000) * A.env_exp(0.012, 0.004)
        out = A.mix(out, A.at(c, k * r.uniform(0.04, 0.08)))
    return out


def heron_croak(i):
    d = 0.5
    am = 0.55 + 0.45 * np.sin(2 * np.pi * 34 * A.t(d))
    croak = A.formant(A.saw(A.glide(210 + 20 * i, 170, d), d, 30), 'a', 0.9) * am * A.env_swell(d, 0.15, 1.2)
    return _rv(A.drive(croak, 1.6), 1.0, 0.4, 0.25)


def boar_grunt(i):
    r = np.random.default_rng(320 + i)
    out = np.zeros(int(0.7 * A.SR))
    for k in range(2):
        d = 0.18
        g = A.lowpass(A.saw(A.glide(95 + 10 * i, 80, d), d, 30) + A.noise(d, 'brown', seed=321 + k) * 0.6, 900)
        out = A.mix(out, A.at(g * A.env_exp(d, 0.1), k * r.uniform(0.22, 0.3)))
    return A.drive(out, 1.8)


def boar_squeal(i):
    d = 0.45
    f = A.glide(900 + 60 * i, 1350, d) * (1 + 0.02 * np.sin(2 * np.pi * 12 * A.t(d)))
    return A.formant(A.saw(f, d, 24), 'i', 1.3) * A.env_swell(d, 0.2, 1.2) * 0.8


def warden_rumble(i):
    d = 1.6
    grind = A.lowpass(A.noise(d, 'brown', seed=330 + i), 320) * A.env_swell(d, 0.4, 1.0)
    thud = A.drum(50 - 5 * i, 1.0, 0.5, 1.5) * 0.6
    chime = A.at(A.bell(A.note('D4'), 1.4, 1.0) * 0.08, 0.3)
    return _rv(A.mix(grind, thud, chime), 1.6, 0.6, 0.3)


def wisp_chime(i):
    notes = [('E6', 'B6', 'G#6'), ('C#6', 'A6', 'E6'), ('B5', 'F#6', 'D#6')][i % 3]
    out = np.zeros(int(1.4 * A.SR))
    for k, n in enumerate(notes):
        out = A.mix(out, A.at(A.chime(A.note(n), 1.0, 0.5) * 0.4, k * 0.09))
    return _rv(out, 2.0, 0.8, 0.45)


def monk_chant(i):
    d = 2.6
    root = [A.note('D3'), A.note('C3'), A.note('F3')][i % 3]
    voice = A.choir(root, d, 'o', 0.5, 0.9) * 0.6 + A.choir(root * 1.5, d, 'o', 0.7, 0.9) * 0.35
    drowned = A.lowpass(voice, 900 + 200 * np.sin(2 * np.pi * 0.7 * A.t(d)) ** 2)
    bubbles = A.bandpass(A.noise(d, 'white', seed=340 + i), 1800, 3.0) * (A.noise(d, 'white', seed=341 + i) > 1.8) * 0.3
    return A.reverb(A.mix(drowned, bubbles), 3.0, 1.4, 0.5)


def hag_cackle(i):
    r = np.random.default_rng(350 + i)
    out = np.zeros(int(1.3 * A.SR))
    base = 420 + 40 * i
    for k in range(6):
        d = 0.11
        f = base * (1 + k * 0.06)
        burst = A.formant(A.saw(A.glide(f, f * 1.2, d), d, 20), 'a', 1.2) * A.env_swell(d, 0.3, 1.0)
        out = A.mix(out, A.at(burst * 0.8, k * r.uniform(0.13, 0.17)))
    return _rv(out, 1.2, 0.5, 0.3)


def hag_curse(i):
    d = 1.0
    sweep = A.whoosh(0.6, 300, 2400, 1.4)
    chord = A.mix(*[A.pad(A.note(n), d, 2, 0.02, 1500, 0.05, 0.4) * 0.2 for n in ('C4', 'F#4', 'B4')])
    return _rv(A.mix(sweep, chord), 1.4, 0.5, 0.35)


def crawler_rattle(i):
    r = np.random.default_rng(360 + i)
    out = np.zeros(int(0.6 * A.SR))
    for k in range(r.integers(5, 9)):
        out = A.mix(out, A.at(A.clink(r.uniform(900, 1800), 0.06) * 0.5, r.uniform(0, 0.5)))
    return out


def stalker_snarl(i):
    d = 0.8
    am = 0.6 + 0.4 * np.sin(2 * np.pi * 38 * A.t(d))
    growl = A.lowpass(A.saw(A.glide(130 + 15 * i, 100, d), d, 30) + A.noise(d, 'pink', seed=370 + i) * 0.4, 1400) * am
    hiss = A.highpass(A.noise(d, 'white', seed=371 + i), 4000) * 0.25
    return A.drive(A.mix(growl, hiss) * A.env_swell(d, 0.25, 1.0) * 1.3, 2.0)


def wraith_wail(i):
    d = 2.0
    f = A._freq(np.concatenate([A.glide(420 + 30 * i, 640, 0.8), A.glide(640, 300, 1.2)]), int(d * A.SR))
    wail = A.formant(A.saw(f, d, 30), 'o', 1.2) * A.env_swell(d, 0.35, 1.0)
    air = A.highpass(A.noise(d, 'white', seed=380 + i), 2500) * A.env_swell(d, 0.5, 1.0) * 0.2
    return A.reverb(A.mix(wail, air), 3.0, 1.4, 0.55)


def mite_chitter(i):
    d = 0.5
    am = (np.sin(2 * np.pi * 45 * A.t(d)) > 0.6).astype(float)
    return A.bandpass(A.noise(d, 'white', seed=390 + i), 5200 - 400 * i, 3.0) * am * A.env_swell(d, 0.2, 1.0) * 0.8


def revenant_roar(i):
    d = 1.4
    growl = A.formant(A.saw(A.glide(95 + 10 * i, 70, d), d, 30), 'a', 0.8) * A.env_swell(d, 0.2, 1.0)
    fire = A.crackle(d, 90, 400 + i) * 0.3
    return A.reverb(A.drive(A.mix(growl, fire) * 1.4, 2.2), 1.8, 0.7, 0.3)


def elderhorn_bellow(i):
    """A rutting stag the size of a cart: a long rising-and-falling bellow over a chest rumble."""
    d = 2.4
    f = A._freq(np.concatenate([A.glide(95 + 8 * i, 150 + 10 * i, 0.9), A.glide(150 + 10 * i, 70, 1.5)]), int(d * A.SR))
    f = f * (1 + 0.02 * np.sin(2 * np.pi * 6 * A.t(d)))
    voice = A.formant(A.saw(f, d, 40), 'o', 0.8) * A.env_swell(d, 0.35, 1.2)
    rough = A.bandpass(A.noise(d, 'pink', seed=400 + i), 700, 1.5) * A.env_swell(d, 0.4, 1.0) * 0.35
    chest = A.rumble(d, 90) * A.env_swell(d, 0.4, 1.0) * 0.6
    leaves = A.highpass(A.noise(d, 'white', seed=401 + i), 5000) * A.env_swell(d, 0.6, 1.0) * 0.08
    return A.reverb(A.drive(A.mix(voice, rough, chest, leaves) * 1.3, 1.8), 2.6, 1.2, 0.4)


def colossus_roar(i):
    """A furnace given a throat: a grinding growl, a roaring draught and the ring of hot iron."""
    d = 2.2
    growl = A.formant(A.saw(A.glide(70 + 6 * i, 48, d), d, 40), 'a', 0.7) * A.env_swell(d, 0.3, 1.0)
    draught = A.lowpass(A.noise(d, 'brown', seed=410 + i), 600) * A.env_swell(d, 0.5, 1.0) * 0.9
    fire = A.crackle(d, 160, 411 + i) * 0.35
    iron = A.mix(A.at(A.clink(310 + 20 * i, 1.4) * 0.3, 0.15), A.at(A.clink(465, 1.2) * 0.2, 0.2))
    return A.reverb(A.drive(A.mix(growl, draught, fire, iron) * 1.4, 2.4), 2.2, 0.9, 0.35)


VOICES = {
    'elderhorn_bellow': (elderhorn_bellow, 2, 'Elderhorn bellows'),
    'colossus_roar': (colossus_roar, 2, 'Cinder Colossus roars'),
    'fawn_call': (fawn_call, 3, 'Glimmerfawn calls'),
    'fawn_hurt': (fawn_hurt, 2, 'Glimmerfawn cries'),
    'hare_squeak': (hare_squeak, 2, 'Duskhare squeaks'),
    'tortoise_hiss': (tortoise_hiss, 2, 'Mossback hisses'),
    'beetle_click': (beetle_click, 3, 'Beetle clicks'),
    'heron_croak': (heron_croak, 2, 'Tidewader croaks'),
    'boar_grunt': (boar_grunt, 3, 'Boar grunts'),
    'boar_squeal': (boar_squeal, 2, 'Boar squeals'),
    'warden_rumble': (warden_rumble, 2, 'Stonewarden grinds'),
    'wisp_chime': (wisp_chime, 3, 'Runewisp chimes'),
    'monk_chant': (monk_chant, 3, 'Choirmonk chants'),
    'hag_cackle': (hag_cackle, 2, 'Mire Hag cackles'),
    'hag_curse': (hag_curse, 2, 'Mire Hag curses'),
    'crawler_rattle': (crawler_rattle, 3, 'Bones rattle'),
    'stalker_snarl': (stalker_snarl, 2, 'Gloam Stalker snarls'),
    'wraith_wail': (wraith_wail, 3, 'Shade Wraith wails'),
    'mite_chitter': (mite_chitter, 2, 'Mite chitters'),
    'revenant_roar': (revenant_roar, 2, 'Ashen Revenant roars'),
}
