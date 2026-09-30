"""The world's own voice: birdsong by day, crickets, owls and frogs by night, and wind on the heights.

sounds.py merges AMBIENCE into its SFX table (name -> (function(variant) -> mono array, variants, subtitle)); the client
plays them around the player (client/Ambience.java).
"""
import numpy as np

from . import audio as A


def _rv(x, length=1.6, decay=0.6, mix=0.3):
    return A.reverb(x, length, decay, mix)


def _chirp(f0, f1, dur, bright=0.15):
    """A single bird note: a pure glide with a touch of its second harmonic and a fast swell."""
    f = A.glide(f0, f1, dur)
    tone = A.sine(f, dur) + bright * A.sine(f * 2, dur)
    return tone * A.env_swell(dur, 0.3, 1.6)


def birdsong(i):
    r = np.random.default_rng(500 + i)
    d = 3.2
    out = np.zeros(int(d * A.SR))
    if i == 0:
        # a warbler: a quick falling trill, twice
        for rep in range(2):
            t0 = 0.2 + rep * 1.5
            for k in range(9):
                f = 5200 - k * 180 + r.uniform(-60, 60)
                out = A.mix(out, A.at(_chirp(f, f * 0.82, 0.05) * 0.5, t0 + k * 0.065))
    elif i == 1:
        # a two-note whistle, "fee-bee", answered further off
        for t0, amp in ((0.2, 0.6), (1.7, 0.3)):
            out = A.mix(out, A.at(_chirp(3600, 3550, 0.32, 0.05) * amp, t0))
            out = A.mix(out, A.at(_chirp(3050, 2950, 0.4, 0.05) * amp, t0 + 0.4))
    else:
        # a finch's tumbling phrase
        t = 0.15
        for k in range(12):
            f = r.uniform(2800, 5600)
            dur = r.uniform(0.04, 0.11)
            out = A.mix(out, A.at(_chirp(f, f * r.uniform(0.75, 1.3), dur) * 0.45, t))
            t += dur + r.uniform(0.01, 0.06)
    return _rv(out, 1.8, 0.7, 0.35)


def crickets(i):
    d = 4.0
    tt = A.t(d)
    carrier = A.sine(4300 + 250 * i, d) + 0.3 * A.sine(8600 + 500 * i, d)
    # chirps of 3-4 pulses, about three chirps a second, from two insects slightly out of step
    out = np.zeros_like(tt)
    for phase, amp in ((0.0, 1.0), (0.13 + 0.05 * i, 0.55)):
        pulse = (np.sin(2 * np.pi * 30 * (tt + phase)) > 0.2).astype(float)
        gate = (np.sin(2 * np.pi * (2.8 + 0.3 * i) * (tt + phase)) > 0.35).astype(float)
        out += carrier * pulse * gate * amp
    out = A.lowpass(out, 9000) * A.env_swell(d, 0.5, 0.6)
    return _rv(out * 0.5, 1.0, 0.3, 0.25)


def owl(i):
    d = 2.6
    out = np.zeros(int(d * A.SR))
    notes = [(0.1, 0.45), (0.8, 0.2), (1.1, 0.55)] if i == 0 else [(0.1, 0.6), (1.0, 0.7)]
    for t0, dur in notes:
        f = A.glide(410 - 30 * i, 370 - 30 * i, dur)
        hoot = A.formant(A.sine(f, dur) + 0.2 * A.sine(f * 2, dur), 'u', 1.0) * A.env_swell(dur, 0.25, 1.4)
        breath = A.bandpass(A.noise(dur, 'pink', seed=520 + i), 600, 2.0) * A.env_swell(dur, 0.2, 1.0) * 0.15
        out = A.mix(out, A.at(A.mix(hoot, breath) * 0.8, t0))
    return A.reverb(out, 3.0, 1.6, 0.5)


def frogs(i):
    r = np.random.default_rng(530 + i)
    d = 3.5
    out = np.zeros(int(d * A.SR))
    for k in range(r.integers(4, 7)):
        dur = r.uniform(0.18, 0.3)
        base = r.uniform(380, 620) * (0.7 if i else 1.0)
        am = 0.5 + 0.5 * np.sin(2 * np.pi * r.uniform(22, 34) * A.t(dur))
        croak = A.bandpass(A.saw(A.glide(base, base * 0.8, dur), dur, 30), base * 1.6, 2.0) * am * A.env_swell(dur, 0.3, 1.0)
        out = A.mix(out, A.at(croak * r.uniform(0.3, 0.7), r.uniform(0, d - dur)))
    return _rv(out, 1.4, 0.5, 0.3)


def wind(i):
    d = 7.0
    tt = A.t(d)
    body = A.noise(d, 'pink', seed=540 + i)
    sweep = 500 + 350 * np.sin(2 * np.pi * (0.11 + 0.03 * i) * tt) + 150 * np.sin(2 * np.pi * 0.37 * tt)
    howl = A.tv_filter(body, sweep, 'band', q=3.0)
    gust = A.env_swell(d, 0.45, 1.2) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.23 * tt) ** 2)
    return A.lowpass(howl * gust, 2400) * 1.2


AMBIENCE = {
    'amb_birdsong': (birdsong, 3, 'Birds sing'),
    'amb_crickets': (crickets, 2, 'Crickets chirp'),
    'amb_owl': (owl, 2, 'An owl hoots'),
    'amb_frogs': (frogs, 2, 'Frogs croak'),
    'amb_wind': (wind, 2, 'Wind howls'),
}
