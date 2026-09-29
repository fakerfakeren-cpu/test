"""Every Oathbound sound event, synthesised, plus sounds.json.

Run from the repository root:  python3 -m tools.oath.sounds
"""
import json
import os

import numpy as np
import soundfile as sf

from .audio import *  # noqa: F401,F403
from . import audio as A

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'src/main/resources/assets/oathbound/sounds')


def rv(x, length=1.6, decay=0.45, mixv=0.25):
    return A.reverb(x, length, decay, mixv)


# ====================================================================== lantern, chronicle, quests
def lantern_ignite(i):
    fire = A.lowpass(A.noise(0.6, 'pink'), A.glide(300, 3500, 0.6)) * A.env_swell(0.6, 0.25, 1.6)
    chime = A.chime(A.note('E6') * (1 + 0.02 * i), 1.4, 0.5) * 0.35
    return rv(A.mix(fire, A.at(chime, 0.08)), 1.4, 0.4, 0.3)


def lantern_seek(i):
    f = A.glide(A.note('A5'), A.note('E6'), 0.25)
    ping = A.sine(np.concatenate([f, np.full(int(1.1 * A.SR), A.note('E6'))]), 1.35) * A.env_exp(1.35, 0.4)
    ping += 0.3 * A.sine(A.note('E7'), 1.35) * A.env_exp(1.35, 0.2)
    return A.reverb(A.echo(ping, 0.18, 0.45, 4), 2.0, 0.6, 0.35)


def chronicle_page(i):
    r = np.random.default_rng(100 + i)
    dur = 0.32 + 0.05 * i
    body = A.bandpass(A.noise(dur, 'pink', seed=200 + i), A.glide(1800, 4200, dur), 1.0) * A.env_swell(dur, 0.35, 1.2)
    crinkle = A.crackle(dur, 90, seed=300 + i) * 0.35 * A.env_swell(dur, 0.5, 1.0)
    return A.mix(body, crinkle)


def quest_complete(i):
    notes = ['C5', 'E5', 'G5', 'C6']
    out = np.zeros(int(2.4 * A.SR))
    for k, nme in enumerate(notes):
        c = A.bell(A.note(nme), 1.8, 0.8, 0.8) * 0.5
        out = A.mix(out, A.at(c, k * 0.09))
    sparkle = A.highpass(A.crackle(1.2, 40, 9), 5000) * 0.2
    return rv(A.mix(out, A.at(sparkle, 0.3)), 2.2, 0.7, 0.35)


def wayshrine_kindle(i):
    whoosh = A.lowpass(A.noise(1.2, 'pink'), A.glide(200, 4000, 1.2)) * A.env_swell(1.2, 0.35, 1.3) * 0.9
    low = A.sine(A.note('C3'), 2.6) * A.env_swell(2.6, 0.3, 1.5) * 0.35
    arp = np.zeros(int(2.8 * A.SR))
    for k, nme in enumerate(['G4', 'C5', 'E5', 'G5', 'C6']):
        arp = A.mix(arp, A.at(A.chime(A.note(nme), 1.5, 0.6) * 0.3, 0.35 + k * 0.12))
    return rv(A.mix(whoosh, low, arp), 2.4, 0.7, 0.35)


# ====================================================================== puzzles
BELL_NOTES = ['G4', 'A4', 'C5', 'D5']


def chapel_bell(tone):
    def f(i):
        b = A.bell(A.note(BELL_NOTES[tone]) * (1 + 0.003 * i), 4.0, 1.6)
        return A.reverb(b, 3.0, 1.0, 0.35)
    return f


def bell_wrong(i):
    a = A.bell(A.note('C#4'), 1.6, 0.4, 0.6)
    b = A.bell(A.note('D4') * 1.06, 1.6, 0.35, 0.6)
    thud = A.drum(90, 0.5, 0.5, 1.0) * 0.8
    return rv(A.mix((a, 0.5), (b, 0.5), thud), 1.4, 0.4, 0.3)


def puzzle_solved(i):
    out = np.zeros(int(3.2 * A.SR))
    for k, nme in enumerate(['D5', 'F#5', 'A5', 'D6', 'F#6']):
        out = A.mix(out, A.at(A.chime(A.note(nme), 1.8, 0.8) * 0.35, k * 0.1))
    pad = A.choir(A.note('D4'), 2.8, 'a', 0.5, 1.2) * 0.25 + A.choir(A.note('A4'), 2.8, 'a', 0.6, 1.2) * 0.2
    return rv(A.mix(out, A.at(pad, 0.2)), 2.6, 0.9, 0.4)


def ward_dissolve(i):
    dur = 1.6
    out = np.zeros(int(dur * A.SR))
    r = np.random.default_rng(40 + i)
    for k in range(14):
        f0 = r.uniform(1800, 5200)
        s = A.sine(A.glide(f0, f0 * r.uniform(0.4, 0.7), dur), dur) * A.env_exp(dur, r.uniform(0.2, 0.7), 0.01)
        out = A.mix(out, A.at(s * 0.12, r.uniform(0, 0.4)))
    hiss = A.highpass(A.noise(dur), 3000) * A.env_exp(dur, 0.5) * 0.3
    return rv(A.mix(out, hiss), 1.8, 0.6, 0.35)


def dial_turn(i):
    dur = 0.45
    grind = A.bandpass(A.noise(dur, 'brown', seed=50 + i), 500, 1.2) * A.env_swell(dur, 0.4, 1.0) * 0.8
    clicks = np.zeros(int(dur * A.SR))
    for k in range(4):
        c = A.clink(1400 + 200 * k, 0.08) * 0.3
        clicks = A.mix(clicks, A.at(c, 0.05 + k * 0.08))
    return A.mix(grind, clicks)


def tomb_open(i):
    dur = 2.4
    grind = A.lowpass(A.noise(dur, 'brown'), 220) * A.env_swell(dur, 0.5, 0.8) * 2.2
    scrape = A.bandpass(A.noise(dur, 'pink'), A.glide(400, 900, dur), 2.0) * A.env_swell(dur, 0.6, 1.0) * 0.6
    thud = A.at(A.drum(55, 1.0, 0.2, 1.0), dur - 0.4)
    return rv(A.mix(grind, scrape, thud), 2.0, 0.8, 0.35)


def liar_wakes(i):
    dur = 2.2
    groan = A.formant(A.saw(A.glide(70, 55, dur), dur), 'o') * A.env_swell(dur, 0.4, 1.3) * 0.9
    whisper = A.formant(A.noise(dur), 'e', 1.3) * A.env_swell(dur, 0.6, 1.5) * 0.9
    return A.reverb(A.mix(groan, whisper), 2.6, 0.9, 0.45)


def gate_open(i):
    dur = 4.5
    boom = A.drum(38, 3.0, 0.6, 1.5) * 1.2
    rumble = A.rumble(dur, 160) * A.env_swell(dur, 0.3, 1.2) * 0.8
    swell = A.pad(A.note('D3'), dur, 5, 0.012, A.glide(300, 3000, dur), 1.5, 1.5) * 0.6
    choir_ = A.choir(A.note('A3'), dur, 'a', 1.2, 1.5) * 0.3
    return A.reverb(A.mix(boom, rumble, swell, choir_), 3.5, 1.3, 0.4)


def gate_hum(i):
    dur = 3.0
    hum = A.sine(55, dur) * 0.5 + A.sine(110.5, dur) * 0.25 + A.sine(165.3, dur) * 0.12
    wob = 1 + 0.25 * np.sin(2 * np.pi * 0.66 * A.t(dur))
    shimmer = A.highpass(A.noise(dur), 4000) * 0.04
    x = (hum * wob + shimmer)
    return A.fade(x, 0.3, 0.3)


# ====================================================================== weapons
def riposte(i):
    ring = A.clink(1900 + 150 * i, 0.7) * 0.6
    swoosh = A.whoosh(0.35, 600, 4000) * 0.8
    return rv(A.mix(swoosh, A.at(ring, 0.08)), 1.0, 0.3, 0.2)


def halberd_thrust(i):
    return A.mix(A.whoosh(0.4, 300, 2200, 1.4) * 1.0, A.at(A.clink(900, 0.3) * 0.4, 0.25))


def anchor_throw(i):
    chain = np.zeros(int(0.8 * A.SR))
    r = np.random.default_rng(60 + i)
    for k in range(10):
        chain = A.mix(chain, A.at(A.clink(r.uniform(1100, 2400), 0.12) * 0.25, k * 0.06 + r.uniform(0, 0.02)))
    return A.mix(chain, A.whoosh(0.6, 250, 1500) * 0.7)


def anchor_hit(i):
    thud = A.drum(70, 0.7, 0.8, 2.0)
    ring = A.clink(420 + 30 * i, 1.0) * 0.5
    return rv(A.mix(thud, ring, A.lowpass(A.noise(0.2), 2000) * A.env_exp(0.2, 0.05) * 0.6), 1.2, 0.35, 0.25)


def arcane_chain(i):
    dur = 0.7
    zap = A.crackle(dur, 220, 70 + i) * A.env_exp(dur, 0.25) * 0.9
    buzz = A.square(A.glide(1400, 600, dur), dur, 8) * A.env_exp(dur, 0.2) * 0.2
    return rv(A.mix(zap, buzz), 0.8, 0.25, 0.2)


def arcane_orb(i):
    dur = 0.9
    fm = A.sine(A.note('A4') * (1 + 0.3 * np.sin(2 * np.pi * 9 * A.t(dur))), dur) * A.env_swell(dur, 0.2, 1.2)
    sh = A.chime(A.note('E6'), dur, 0.3) * 0.2
    return rv(A.mix((fm, 0.6), sh), 1.0, 0.3, 0.25)


def orb_reflect(i):
    ting = A.chime(A.note('B6'), 0.8, 0.25) * 0.6
    back = A.whoosh(0.4, 3000, 600) * 0.6
    return rv(A.mix(ting, back), 0.9, 0.3, 0.2)


def warhorn(i):
    dur = 2.8
    f = np.concatenate([A.glide(A.note('A2'), A.note('D3'), 0.35), np.full(int(2.45 * A.SR), A.note('D3'))])
    h = A.horn(f, dur, 0.1, 0.6, 1800)
    h2 = A.horn(f * 1.5, dur, 0.15, 0.6, 1400) * 0.4
    return A.reverb(A.mix(h, h2), 3.0, 1.2, 0.4)


def dawn_charge(i):
    dur = 1.6
    whine = A.sine(A.glide(200, 1600, dur), dur) * A.env_swell(dur, 0.9, 1.0) * 0.5
    harm = A.sine(A.glide(400, 3200, dur), dur) * A.env_swell(dur, 0.9, 1.0) * 0.2
    sparkle = A.crackle(dur, 60, 81) * A.env_swell(dur, 0.9, 1.0) * 0.3
    return A.mix(whine, harm, sparkle)


def dawn_burst(i):
    dur = 2.4
    blast = A.lowpass(A.noise(dur, 'pink'), A.glide(8000, 300, dur)) * A.env_exp(dur, 0.35) * 1.2
    boom = A.drum(45, 1.6, 0.4, 2.0) * 0.9
    chord = np.zeros(int(dur * A.SR))
    for nme in ('D5', 'F#5', 'A5', 'D6'):
        chord = A.mix(chord, A.chime(A.note(nme), dur, 0.9) * 0.25)
    return A.reverb(A.mix(blast, boom, chord), 2.5, 0.9, 0.35)


def sickle_reap(i):
    swish = A.whoosh(0.45, 1200, 5000, 2.0) * 0.8
    ghost = A.sine(A.glide(A.note('E5'), A.note('B4'), 0.6), 0.6) * A.env_exp(0.6, 0.25) * 0.25
    return A.reverb(A.mix(swish, ghost), 1.0, 0.4, 0.3)


def flask_shatter(i):
    r = np.random.default_rng(90 + i)
    dur = 0.9
    out = np.zeros(int(dur * A.SR))
    for k in range(26):
        f = r.uniform(2500, 9000)
        out = A.mix(out, A.at(A.sine(f, 0.12) * A.env_exp(0.12, 0.02) * r.uniform(0.1, 0.4), r.uniform(0, 0.12)))
    burst = A.highpass(A.noise(0.25), 2500) * A.env_exp(0.25, 0.04) * 0.8
    glow = A.chime(A.note('A6'), dur, 0.35) * 0.2
    return rv(A.mix(out, burst, glow), 1.0, 0.3, 0.25)


def sun_arrow(i):
    whistle = A.sine(A.glide(2600, 1800, 0.5), 0.5) * A.env_swell(0.5, 0.2, 1.2) * 0.3
    air = A.whoosh(0.5, 2000, 5000, 3.0) * 0.5
    return A.mix(whistle, air)


def sunmark(i):
    ting = A.chime(A.note('E6'), 1.0, 0.4) * 0.5
    warm = A.pad(A.note('E4'), 1.0, 3, 0.01, 1600, 0.05, 0.6) * 0.3
    return rv(A.mix(ting, warm), 1.2, 0.4, 0.3)


# ====================================================================== creatures
def gloamling_ambient(i):
    r = np.random.default_rng(110 + i)
    out = np.zeros(int(0.8 * A.SR))
    for k in range(r.integers(3, 6)):
        d = r.uniform(0.05, 0.1)
        f = r.uniform(700, 1100)
        chirp = A.formant(A.saw(A.glide(f, f * r.uniform(1.1, 1.5), d), d, 20), 'i', r.uniform(1.0, 1.4)) * A.env_swell(d, 0.3, 1.0)
        out = A.mix(out, A.at(chirp * 0.8, k * 0.11 + r.uniform(0, 0.03)))
    return A.reverb(out, 0.6, 0.2, 0.2)


def gloamling_hurt(i):
    d = 0.3
    return A.formant(A.saw(A.glide(1300, 800, d), d, 20), 'e', 1.3) * A.env_exp(d, 0.1)


def gloamling_death(i):
    d = 0.9
    wail = A.formant(A.saw(A.glide(1000, 300, d), d, 20), 'u', 1.2) * A.env_exp(d, 0.35)
    poof = A.lowpass(A.noise(0.4, 'pink'), 1500) * A.env_exp(0.4, 0.12) * 0.6
    return A.reverb(A.mix(wail, A.at(poof, 0.4)), 1.2, 0.4, 0.3)


def forsworn_ambient(i):
    d = 1.3
    breath = A.bandpass(A.noise(d, 'pink', seed=130 + i), 600, 1.5) * A.env_swell(d, 0.45, 1.2) * 0.8
    clink = A.at(A.clink(700 + 90 * i, 0.4) * 0.35, 0.8)
    return A.reverb(A.mix(breath, clink), 1.2, 0.5, 0.35)


def forsworn_collapse(i):
    r = np.random.default_rng(140 + i)
    out = np.zeros(int(1.4 * A.SR))
    tt = 0.0
    for k in range(9):
        out = A.mix(out, A.at(A.clink(r.uniform(300, 900), 0.35) * (0.6 - k * 0.05), tt))
        tt += r.uniform(0.04, 0.15)
    thud = A.drum(70, 0.6, 0.3, 1.0) * 0.6
    return rv(A.mix(out, thud), 1.2, 0.4, 0.3)


def forsworn_rise(i):
    rev = forsworn_collapse(i)[::-1]
    groan = A.formant(A.saw(A.glide(80, 110, 1.4), 1.4), 'o') * A.env_swell(1.4, 0.7, 1.2) * 0.6
    return A.mix(A.lowpass(rev, 3000) * 0.6, groan)


def wight_ambient(i):
    d = 2.2
    f = A.note('A3') * (1 + 0.1 * i) * (1 + 0.02 * np.sin(2 * np.pi * 5.5 * A.t(d)))
    moan = A.formant(A.saw(f * A.glide(1.0, 0.8, d), d, 30), 'o') * A.env_swell(d, 0.4, 1.3)
    air = A.highpass(A.noise(d), 2500) * A.env_swell(d, 0.5, 1.2) * 0.2
    return A.reverb(A.mix(moan, air), 2.5, 1.0, 0.5)


def wight_hurt(i):
    d = 0.55
    shriek = A.formant(A.saw(A.glide(900, 600, d), d), 'i', 1.2) * A.env_exp(d, 0.2)
    return A.reverb(shriek, 1.2, 0.5, 0.4)


def veilhound_howl(i):
    d = 2.2
    f = np.concatenate([A.glide(300, 520, 0.5), np.full(int(1.0 * A.SR), 520.0), A.glide(520, 380, 0.7)])
    f = A._freq(f, int(d * A.SR)) * (1 + 0.01 * np.sin(2 * np.pi * 6 * A.t(d)))
    howl = A.formant(A.saw(f, d, 30), 'u', 1.1) * A.env_swell(d, 0.3, 1.0)
    return A.reverb(howl, 3.0, 1.2, 0.45)


def veilhound_growl(i):
    d = 1.0
    am = 0.6 + 0.4 * np.sin(2 * np.pi * 28 * A.t(d))
    g = A.lowpass(A.saw(A.glide(70, 60, d), d, 30) + A.noise(d, 'brown') * 0.5, 700) * am * A.env_swell(d, 0.3, 1.0)
    return A.drive(g * 1.4, 2.0)


def tome_flutter(i):
    d = 0.7
    am = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * (14 + 3 * i) * A.t(d)))
    return A.bandpass(A.noise(d, 'pink', seed=150 + i), 2600, 0.9) * am * A.env_swell(d, 0.4, 1.0)


def tome_cast(i):
    fwip = A.whoosh(0.3, 900, 3500, 1.5) * 0.7
    tone = A.chime(A.note('F#6'), 0.8, 0.3) * 0.35
    return rv(A.mix(fwip, A.at(tone, 0.1)), 0.9, 0.3, 0.25)


def moth_flutter(i):
    d = 0.9
    am = 0.5 + 0.5 * np.sin(2 * np.pi * 22 * A.t(d))
    return A.lowpass(A.noise(d, 'pink', seed=160 + i), 1200) * am * A.env_swell(d, 0.5, 1.0) * 0.8


def housecarl_rise(i):
    d = 1.8
    cry = A.choir(A.note('D3'), d, 'a', 0.2, 0.8) * 0.7
    ghost = A.highpass(A.noise(d), 3000) * A.env_swell(d, 0.3, 1.0) * 0.15
    return A.reverb(A.mix(cry, ghost), 2.5, 1.0, 0.5)


# ====================================================================== bosses
def roar(base, dur, vowel='a', grit=2.5, reverb_len=2.5):
    f = base * np.concatenate([A.glide(0.8, 1.15, dur * 0.3), A.glide(1.15, 0.9, dur * 0.7)])[:int(dur * A.SR)]
    src = A.saw(f, dur, 40) + A.noise(dur, 'pink') * 0.35
    v = A.formant(src, vowel, 0.8) * A.env_swell(dur, 0.25, 1.2)
    return A.reverb(A.drive(v * 1.5, grit), reverb_len, 1.0, 0.35)


def caldris_roar(i):
    return A.mix(roar(95, 2.0, 'o'), A.lowpass(A.noise(2.0, 'pink'), 700) * A.env_swell(2.0, 0.3, 1.0) * 0.3)


def shield_block(i):
    clang = A.clink(320 + 40 * i, 1.0) * 0.8
    thud = A.drum(90, 0.4, 0.6, 1.5) * 0.6
    return rv(A.mix(clang, thud), 1.2, 0.35, 0.25)


def shield_charge(i):
    out = np.zeros(int(1.2 * A.SR))
    for k in range(5):
        out = A.mix(out, A.at(A.mix((A.drum(60, 0.3, 0.3, 1.0), 0.7), (A.clink(500, 0.2), 0.2)), k * 0.2))
    return A.mix(out, A.whoosh(1.2, 200, 900) * 0.4)


def undertow(i):
    d = 2.2
    swirl = A.bandpass(A.noise(d, 'pink'), 500 + 350 * np.sin(2 * np.pi * 1.5 * A.t(d)) ** 2 + 150, 2.0) * A.env_swell(d, 0.5, 1.0) * 1.2
    r = np.random.default_rng(170 + i)
    bubbles = np.zeros(int(d * A.SR))
    for k in range(20):
        f0 = r.uniform(300, 900)
        bd = r.uniform(0.04, 0.09)
        bubbles = A.mix(bubbles, A.at(A.sine(A.glide(f0, f0 * 1.8, bd), bd) * A.env_exp(bd, 0.03) * 0.25, r.uniform(0, d - 0.1)))
    return A.reverb(A.mix(swirl, bubbles), 1.8, 0.6, 0.35)


def veyl_laugh(i):
    out = np.zeros(int(2.0 * A.SR))
    f = 190.0
    for k in range(5):
        d = 0.16
        syl = A.formant(A.saw(A.glide(f, f * 0.92, d), d, 30) + A.noise(d) * 0.3, 'a', 1.1) * A.env_swell(d, 0.2, 1.0)
        out = A.mix(out, A.at(syl, k * 0.22))
        f *= 0.95
    return A.reverb(A.echo(out, 0.3, 0.35, 3), 2.8, 1.1, 0.5)


def veyl_blink(i):
    d = 0.4
    return A.mix(A.sine(A.glide(2200, 300, d), d) * A.env_exp(d, 0.12) * 0.5, A.whoosh(d, 3000, 500) * 0.5)


def veyl_mirror(i):
    d = 1.4
    out = np.zeros(int(d * A.SR))
    for nme in ('C6', 'E6', 'G#6', 'B6'):
        out = A.mix(out, A.chime(A.note(nme), d, 0.6) * 0.25)
    return A.reverb(A.mix(out, A.highpass(A.noise(d), 5000) * A.env_exp(d, 0.3) * 0.2), 2.0, 0.8, 0.45)


def hrodgar_roar(i):
    return A.mix(roar(60, 2.6, 'o', 3.0, 3.0), A.rumble(2.6, 120) * A.env_swell(2.6, 0.3, 1.0) * 0.5)


def flail_slam(i):
    boom = A.drum(40, 1.6, 0.8, 2.5) * 1.2
    crunch = A.lowpass(A.noise(0.5, 'pink'), 2500) * A.env_exp(0.5, 0.1) * 0.8
    chain = A.at(A.clink(800, 0.3) * 0.3, 0.05)
    return A.reverb(A.mix(boom, crunch, chain, A.rumble(1.6, 100) * A.env_exp(1.6, 0.6) * 0.6), 2.0, 0.8, 0.3)


def tether_snap(i):
    crack = A.highpass(A.noise(0.08), 1500) * A.env_exp(0.08, 0.015) * 1.2
    shimmer = A.chime(A.note('C#6'), 0.8, 0.35)[::-1] * 0.4
    return rv(A.mix(shimmer, A.at(crack, 0.75)), 1.2, 0.4, 0.3)


def morvane_voice(i):
    d = 2.6
    r = np.random.default_rng(190 + i)
    out = np.zeros(int(d * A.SR))
    tt = 0.1
    vowels = ['o', 'a', 'u', 'e', 'o']
    for k in range(5):
        sd = r.uniform(0.25, 0.45)
        src = A.noise(sd) * 0.8 + A.saw(A.glide(62, 55, sd), sd, 40) * 0.6
        syl = A.formant(src, vowels[k], 0.85) * A.env_swell(sd, 0.3, 1.0)
        out = A.mix(out, A.at(syl, tt))
        tt += sd + r.uniform(0.03, 0.12)
    return A.reverb(A.drive(out * 1.3, 1.5), 3.5, 1.4, 0.55)


def morvane_roar(i):
    return A.mix(roar(52, 3.0, 'a', 3.5, 3.5), A.rumble(3.0, 100) * A.env_swell(3.0, 0.3, 1.0) * 0.6,
                 A.choir(A.note('D2'), 3.0, 'o', 0.3, 1.0) * 0.25)


def blade_crown(i):
    d = 1.6
    out = np.zeros(int(d * A.SR))
    for k, f in enumerate((1180, 1410, 1765, 2120, 2350, 2790)):
        am = 0.6 + 0.4 * np.sin(2 * np.pi * (3 + k) * A.t(d) + k)
        out = A.mix(out, A.sine(f, d) * am * A.env_swell(d, 0.4, 1.0) * 0.14)
    return A.reverb(out, 1.8, 0.6, 0.4)


def eclipse_pillar(i):
    d = 1.6
    rise = A.lowpass(A.noise(d, 'brown'), A.glide(80, 900, d)) * A.env_swell(d, 0.85, 1.4) * 1.5
    boom = A.at(A.drum(50, 0.8, 0.4, 2.0), d - 0.35)
    return A.reverb(A.mix(rise, boom), 2.0, 0.8, 0.35)


def lantern_snuff(i):
    fff = A.bandpass(A.noise(0.5, 'pink'), A.glide(3000, 600, 0.5), 1.2) * A.env_exp(0.5, 0.15) * 0.8
    thunk = A.at(A.drum(110, 0.3, 0.2, 1.0) * 0.4, 0.2)
    return rv(A.mix(fff, thunk), 1.0, 0.4, 0.3)


def lantern_relight(i):
    return lantern_ignite(i + 3)


def unveiled(i):
    d = 3.0
    boom = A.drum(42, 2.0, 0.6, 2.0)
    ch = A.mix(A.choir(A.note('D4'), d, 'a', 0.05, 1.5) * 0.35, A.choir(A.note('F4'), d, 'a', 0.05, 1.5) * 0.3,
               A.choir(A.note('A4'), d, 'a', 0.05, 1.5) * 0.3)
    return A.reverb(A.mix(boom, ch), 3.0, 1.2, 0.45)


def crown_shatter(i):
    d = 3.2
    glass = flask_shatter(i + 5) * 1.1
    metal = A.clink(260, 1.8) * 0.6
    choir_ = A.mix(A.choir(A.note('D4'), d, 'a', 0.6, 1.5) * 0.3, A.choir(A.note('A4'), d, 'a', 0.7, 1.5) * 0.25,
                   A.choir(A.note('F#5'), d, 'a', 0.8, 1.5) * 0.2)
    return A.reverb(A.mix(glass, metal, A.at(choir_, 0.3)), 3.5, 1.4, 0.45)


def boss_slash(i):
    return A.mix(A.whoosh(0.4, 500 + 100 * i, 3500, 1.3), A.at(A.clink(1500, 0.25) * 0.2, 0.2))


# ====================================================================== music & ambience (stereo)
def stereo(x, width=0.0):
    return np.stack([x, x], axis=1)


def place(buf, x, start):
    i = int(start * A.SR)
    n = min(len(x), len(buf) - i)
    if n > 0:
        buf[i:i + n] += x[:n]


def theme_keeper():
    """Battle theme for the seal keepers: a driving drum ostinato under minor strings and horn calls (D minor)."""
    bpm = 112
    beat = 60 / bpm
    bars = 16
    dur = bars * 4 * beat
    L = np.zeros(int(dur * A.SR) + A.SR * 3)
    chords = [['D3', 'F3', 'A3'], ['Bb2', 'D3', 'F3'], ['C3', 'E3', 'G3'], ['A2', 'C#3', 'E3']]
    for b in range(bars):
        t0 = b * 4 * beat
        ch = chords[b % 4]
        for nme in ch:
            place(L, A.strings(A.note(nme), 4 * beat * 1.02, 0.15, 0.3, 1800) * 0.16, t0)
        # drum ostinato: boom . boom boom . snare
        for k, (off, kind) in enumerate(((0, 'k'), (1, 'k'), (1.5, 'k'), (2, 's'), (3, 'k'), (3.5, 'k'))):
            place(L, (A.drum(52, 0.6, 0.4, 2.5) * 0.8 if kind == 'k' else A.snare(0.35) * 0.5), t0 + off * beat)
        if b % 4 == 3:
            place(L, A.cymbal(2.0) * 0.4, t0 + 3.5 * beat)
    melody = [('D4', 1), ('F4', 1), ('A4', 2), ('G4', 1), ('F4', 1), ('E4', 2), ('F4', 1), ('G4', 1), ('A4', 1), ('C5', 1),
              ('A4', 3), (None, 1)]
    for rep in (4, 8, 12):
        tt = rep * 4 * beat
        for nme, ln in melody:
            if nme:
                place(L, A.horn(A.note(nme), ln * beat * 0.95, 0.06, 0.25, 2200) * 0.22, tt)
            tt += ln * beat
    # ostinato pluck
    for b in range(bars):
        t0 = b * 4 * beat
        root = chords[b % 4][0]
        for k in range(8):
            place(L, A.pluck(A.note(root) * (2 if k % 2 else 1), 0.4, 0.99) * 0.12, t0 + k * beat / 2)
    x = A.reverb(A.normalize(L, 0.8), 2.2, 0.8, 0.25, stereo=True)
    return A.fade(x, 0.02, 1.5)


def theme_morvane():
    """The Hollow King: a slow, heavy organ-and-choir figure in D minor that breaks into drums."""
    bpm = 88
    beat = 60 / bpm
    bars = 20
    dur = bars * 4 * beat
    L = np.zeros(int(dur * A.SR) + A.SR * 4)
    prog = [['D3', 'F3', 'A3'], ['C#3', 'E3', 'A3'], ['Bb2', 'D3', 'F3'], ['G2', 'Bb2', 'D3'],
            ['D3', 'F3', 'Bb3'], ['C3', 'Eb3', 'G3'], ['A2', 'C#3', 'E3'], ['A2', 'C#3', 'E3']]
    for b in range(bars):
        t0 = b * 4 * beat
        ch = prog[b % 8]
        for nme in ch:
            place(L, A.pad(A.note(nme), 4 * beat * 1.05, 4, 0.006, 1100, 0.3, 0.6, 'square') * 0.1, t0)
            place(L, A.choir(A.note(nme) * 2, 4 * beat * 1.02, 'o', 0.4, 0.6) * 0.1, t0)
        place(L, A.drum(36, 1.5, 0.5, 2.0) * 0.9, t0)
        if b >= 8:
            for off in (1, 2.5, 3):
                place(L, A.drum(48, 0.6, 0.4, 2.5) * 0.7, t0 + off * beat)
            place(L, A.snare(0.4) * 0.5, t0 + 2 * beat)
        if b % 4 == 0:
            place(L, A.bell(A.note('D5'), 4.0, 1.4) * 0.12, t0)
    melody = [('A4', 2), ('Bb4', 1), ('A4', 1), ('G4', 2), ('F4', 2), ('E4', 3), ('D4', 1), ('E4', 2), ('F4', 2), ('D4', 4)]
    for rep in (8, 14):
        tt = rep * 4 * beat
        for nme, ln in melody:
            place(L, A.strings(A.note(nme), ln * beat, 0.2, 0.4, 2600) * 0.2, tt)
            tt += ln * beat
    x = A.reverb(A.normalize(L, 0.8), 3.0, 1.2, 0.3, stereo=True)
    return A.fade(x, 0.02, 2.0)


def music_gloaming():
    """Wandering music for the Gloaming: a sparse music-box melody over a slow pad in E Phrygian."""
    beat = 60 / 64
    bars = 24
    dur = bars * 4 * beat
    L = np.zeros(int(dur * A.SR) + A.SR * 5)
    prog = [['E3', 'B3', 'G4'], ['F3', 'C4', 'A4'], ['D3', 'A3', 'F4'], ['E3', 'B3', 'E4']]
    for b in range(0, bars, 2):
        t0 = b * 4 * beat
        for nme in prog[(b // 2) % 4]:
            place(L, A.pad(A.note(nme), 8 * beat * 1.05, 3, 0.01, 900, 2.0, 2.5) * 0.12, t0)
    melody = [('E5', 2), ('F5', 1), ('G5', 1), ('B5', 3), ('A5', 1), ('G5', 2), ('F5', 2), ('E5', 4), (None, 4),
              ('B4', 1), ('C5', 1), ('E5', 2), ('F5', 2), ('E5', 1), ('C5', 1), ('B4', 4), (None, 4)]
    tt = 4 * 4 * beat
    for rep in range(2):
        for nme, ln in melody:
            if nme:
                place(L, A.chime(A.note(nme), 3.0, 1.0) * 0.2, tt)
            tt += ln * beat
        tt += 8 * beat
    x = A.reverb(A.normalize(L, 0.7), 4.0, 1.8, 0.45, stereo=True)
    return A.fade(x, 1.0, 3.0)


def gloaming_ambient():
    """A dusk that hums: slow detuned drone, distant wind, and far-off bells."""
    dur = 32.0
    drone = A.pad(A.note('E2'), dur, 5, 0.004, 500, 4.0, 4.0) * 0.5 + A.pad(A.note('B2'), dur, 3, 0.006, 700, 5.0, 4.0) * 0.3
    wind = A.lowpass(A.noise(dur, 'pink'), 700 + 400 * np.sin(2 * np.pi * 0.05 * A.t(dur)) ** 2) * 0.4
    L = drone + wind
    r = np.random.default_rng(5)
    for k in range(6):
        place(L, A.bell(A.note(r.choice(['E5', 'G5', 'B5', 'F5'])), 5.0, 1.8) * 0.06, 2 + k * 5 + r.uniform(0, 2))
    x = A.reverb(A.normalize(L, 0.6), 4.0, 2.0, 0.4, stereo=True)
    return A.fade(x, 2.0, 2.0)


def gloaming_mood(i):
    d = 4.0
    whisper = A.formant(A.noise(d), 'e', 1.1 + 0.1 * i) * A.env_swell(d, 0.5, 1.5) * 0.8
    tone = A.sine(A.note('F#3'), d) * A.env_swell(d, 0.5, 1.5) * 0.15
    return A.reverb(A.mix(whisper, tone), 3.5, 1.5, 0.5)


# ====================================================================== the catalogue
SFX = {
    # name: (generator, variants, subtitle)
    'lantern_ignite': (lantern_ignite, 2, 'Lantern kindles'),
    'lantern_seek': (lantern_seek, 1, 'Lantern seeks'),
    'chronicle_page': (chronicle_page, 3, 'Page turns'),
    'quest_complete': (quest_complete, 1, 'Quest complete'),
    'wayshrine_kindle': (wayshrine_kindle, 1, 'Wayshrine kindles'),
    'bell_0': (chapel_bell(0), 1, 'Chapel bell tolls'),
    'bell_1': (chapel_bell(1), 1, 'Chapel bell tolls'),
    'bell_2': (chapel_bell(2), 1, 'Chapel bell tolls'),
    'bell_3': (chapel_bell(3), 1, 'Chapel bell tolls'),
    'bell_wrong': (bell_wrong, 1, 'Bells clash'),
    'puzzle_solved': (puzzle_solved, 1, 'A seal answers'),
    'ward_dissolve': (ward_dissolve, 2, 'Ward dissolves'),
    'dial_turn': (dial_turn, 2, 'Rune dial turns'),
    'tomb_open': (tomb_open, 1, 'Tomb grinds open'),
    'liar_wakes': (liar_wakes, 1, 'Something wakes'),
    'gate_open': (gate_open, 1, 'The Gate opens'),
    'gate_hum': (gate_hum, 1, 'Gate hums'),
    'riposte': (riposte, 2, 'Riposte'),
    'halberd_thrust': (halberd_thrust, 2, 'Halberd thrusts'),
    'anchor_throw': (anchor_throw, 2, 'Anchor thrown'),
    'anchor_hit': (anchor_hit, 2, 'Anchor strikes'),
    'arcane_chain': (arcane_chain, 2, 'Arcane chain crackles'),
    'arcane_orb': (arcane_orb, 2, 'Arcane orb hums'),
    'orb_reflect': (orb_reflect, 1, 'Orb reflected'),
    'warhorn': (warhorn, 1, 'Warhorn sounds'),
    'dawn_charge': (dawn_charge, 1, 'Dawnbreaker gathers light'),
    'dawn_burst': (dawn_burst, 1, 'Dawn Rite'),
    'sickle_reap': (sickle_reap, 2, 'Sickle reaps'),
    'flask_shatter': (flask_shatter, 2, 'Flask shatters'),
    'sun_arrow': (sun_arrow, 2, 'Sun-arrow flies'),
    'sunmark': (sunmark, 1, 'Sunmark burns'),
    'gloamling_ambient': (gloamling_ambient, 3, 'Gloamling giggles'),
    'gloamling_hurt': (gloamling_hurt, 2, 'Gloamling hurts'),
    'gloamling_death': (gloamling_death, 1, 'Gloamling dies'),
    'forsworn_ambient': (forsworn_ambient, 2, 'Forsworn Knight breathes'),
    'forsworn_collapse': (forsworn_collapse, 2, 'Forsworn Knight collapses'),
    'forsworn_rise': (forsworn_rise, 1, 'Forsworn Knight rises'),
    'wight_ambient': (wight_ambient, 3, 'Barrow Wight moans'),
    'wight_hurt': (wight_hurt, 2, 'Barrow Wight shrieks'),
    'veilhound_howl': (veilhound_howl, 2, 'Veilhound howls'),
    'veilhound_growl': (veilhound_growl, 2, 'Veilhound growls'),
    'tome_flutter': (tome_flutter, 2, 'Tome flutters'),
    'tome_cast': (tome_cast, 2, 'Tome casts'),
    'moth_flutter': (moth_flutter, 2, 'Lanternmoth flutters'),
    'housecarl_rise': (housecarl_rise, 2, 'Housecarl rises'),
    'caldris_roar': (caldris_roar, 1, 'Sir Caldris bellows'),
    'shield_block': (shield_block, 2, 'Shield blocks'),
    'shield_charge': (shield_charge, 1, 'Shield charge'),
    'undertow': (undertow, 1, 'Undertow swirls'),
    'veyl_laugh': (veyl_laugh, 1, 'Archmage Veyl laughs'),
    'veyl_blink': (veyl_blink, 2, 'Archmage Veyl blinks'),
    'veyl_mirror': (veyl_mirror, 1, 'Mirror images appear'),
    'hrodgar_roar': (hrodgar_roar, 1, 'Hrodgar roars'),
    'flail_slam': (flail_slam, 2, 'Flail slams'),
    'tether_snap': (tether_snap, 2, 'Tether snaps'),
    'morvane_voice': (morvane_voice, 3, 'Morvane speaks'),
    'morvane_roar': (morvane_roar, 1, 'Morvane roars'),
    'blade_crown': (blade_crown, 1, 'Crown of Blades hums'),
    'eclipse_pillar': (eclipse_pillar, 2, 'Eclipse pillar erupts'),
    'lantern_snuff': (lantern_snuff, 2, 'Ward lantern gutters'),
    'lantern_relight': (lantern_relight, 1, 'Ward lantern relit'),
    'unveiled': (unveiled, 1, 'Morvane is unveiled'),
    'crown_shatter': (crown_shatter, 1, 'The Hollow Crown shatters'),
    'boss_slash': (boss_slash, 3, 'Blade swings'),
    'gloaming_mood': (gloaming_mood, 2, 'The Gloaming whispers'),
}

STREAMS = {
    'theme_keeper': (theme_keeper, 'Keeper battle theme'),
    'theme_morvane': (theme_morvane, 'The Hollow King'),
    'music_gloaming': (music_gloaming, None),
    'gloaming_ambient': (gloaming_ambient, 'The Gloaming hums'),
}


def write_ogg(path, x, quality=0.4):
    """Writes in blocks: libsndfile's Vorbis encoder can silently drop very large single writes."""
    x = np.clip(x, -1, 1).astype(np.float32)
    channels = 1 if x.ndim == 1 else x.shape[1]
    with sf.SoundFile(path, 'w', A.SR, channels, format='OGG', subtype='VORBIS', compression_level=1 - quality) as f:
        for i in range(0, len(x), 32768):
            f.write(x[i:i + 32768])
    if sf.info(path).frames < len(x) * 0.99:
        raise RuntimeError(f'{path}: encoder wrote {sf.info(path).frames} of {len(x)} frames')


def generate(only=None):
    os.makedirs(OUT, exist_ok=True)
    defs = {}
    for name, (fn, variants, subtitle) in SFX.items():
        entries = []
        for v in range(variants):
            fname = name if variants == 1 else f'{name}_{v + 1}'
            if only is None or name in only:
                x = A.fade(A.normalize(fn(v), 0.85), 0.002, 0.03)
                write_ogg(os.path.join(OUT, fname + '.ogg'), x, 0.45)
            entries.append({'name': f'oathbound:{fname}'})
        defs[name] = {'sounds': entries, 'subtitle': f'subtitles.oathbound.{name}'}
    for name, (fn, subtitle) in STREAMS.items():
        if only is None or name in only:
            x = A.normalize(fn(), 0.8)
            write_ogg(os.path.join(OUT, name + '.ogg'), x, 0.35)
        d = {'sounds': [{'name': f'oathbound:{name}', 'stream': True}]}
        if subtitle:
            d['subtitle'] = f'subtitles.oathbound.{name}'
        defs[name] = d
    with open(os.path.join(os.path.dirname(OUT), 'sounds.json'), 'w') as f:
        json.dump(defs, f, indent=2)
    return {n: s for n, (_, _, s) in SFX.items()} | {n: s for n, (_, s) in STREAMS.items() if s}


if __name__ == '__main__':
    import sys
    subs = generate(set(sys.argv[1:]) or None)
    print(len(subs), 'sound events')
