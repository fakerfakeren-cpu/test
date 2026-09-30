"""Music for the jukebox: four full pieces pressed onto Oathbound's discs.

* The Lanternguard's Hymn  - D major, 72 bpm. A choir hymn that grows from a single horn into bells and strings.
* Wayshrine Nocturne       - A minor, 84 bpm in threes. A lute and a wooden flute by a brazier at night.
* Tides Beneath the Chapel - F# minor, 60 bpm. Drowned organ, sunken bells, the sea overhead.
* Crown of Ash             - D minor, 96 bpm. Drums, driving strings and horns for the last king.

Each returns a stereo float array; sounds.py normalises and writes them as streamed OGG.
"""
import numpy as np

from . import audio as A


def _place(buf, x, start):
    i = int(start * A.SR)
    if i < 0:
        x, i = x[-i:], 0
    n = min(len(x), len(buf) - i)
    if n > 0:
        buf[i:i + n] += x[:n]


def flute(freq, dur, attack=0.08, release=0.25, vib=5.2, breath=0.06):
    """A soft wooden flute: a sine with a touch of second harmonic, delayed vibrato and breath noise."""
    tt = A.t(dur)
    depth = 0.004 * np.clip((tt - 0.25) / 0.4, 0, 1)
    f = freq * (1 + depth * np.sin(2 * np.pi * vib * tt))
    phase = 2 * np.pi * np.cumsum(f) / A.SR
    tone = np.sin(phase) + 0.18 * np.sin(2 * phase) + 0.06 * np.sin(3 * phase)
    air = A.bandpass(A.noise(dur, 'white'), freq * 2, 2.0) * breath
    return (tone * 0.8 + air) * A.env_adsr(dur, attack, 0.1, 0.85, release)


def timpani(dur=1.6, freq=65):
    return A.drum(freq, dur, 0.15, 1.3) * 0.9 + A.lowpass(A.noise(dur, 'pink'), 300) * A.env_exp(dur, 0.25) * 0.2


def _chords(buf, prog, beat, beats_per_chord, voice, start_bar=0, bars=None, level=0.1):
    bars = bars if bars is not None else len(prog)
    for i in range(bars):
        t0 = (start_bar + i) * beats_per_chord * beat
        for nme in prog[i % len(prog)]:
            _place(buf, voice(A.note(nme), beats_per_chord * beat * 1.04) * level, t0)


def _line(buf, notes, beat, start, voice, level):
    tt = start
    for nme, ln in notes:
        if nme:
            _place(buf, voice(A.note(nme), ln * beat * 0.97) * level, tt)
        tt += ln * beat
    return tt


def _finish(L, room=2.8, decay=1.2, wet=0.32):
    x = A.reverb(A.normalize(L, 0.8), room, decay, wet, stereo=True)
    return A.fade(x, 0.5, 4.0)


# ====================================================================== The Lanternguard's Hymn
def lanternguard_hymn():
    beat = 60 / 72
    bars = 42
    L = np.zeros(int(bars * 4 * beat * A.SR) + A.SR * 8)
    prog = [['D3', 'F#3', 'A3'], ['A2', 'E3', 'A3'], ['B2', 'D3', 'F#3'], ['G2', 'B2', 'D3'],
            ['D3', 'F#3', 'A3'], ['G2', 'B2', 'E3'], ['A2', 'C#3', 'E3'], ['D3', 'F#3', 'A3']]
    bridge = [['B2', 'D3', 'F#3'], ['F#2', 'C#3', 'F#3'], ['G2', 'B2', 'D3'], ['A2', 'C#3', 'E3']]
    choir = lambda f, d: A.choir(f * 2, d, 'a', 0.9, 1.4)
    strings = lambda f, d: A.strings(f * 2, d, 0.6, 0.9, 2200, 4.5)
    # 0-7 choir alone, 8-15 horn states the hymn, 16-23 choir, strings and hymn, 24-31 the minor bridge,
    # 32-39 everything with bells, 40-41 amen
    _chords(L, prog, beat, 4, choir, 0, 8, 0.10)
    _chords(L, prog, beat, 4, choir, 8, 8, 0.09)
    _chords(L, prog, beat, 4, choir, 16, 8, 0.11)
    _chords(L, prog, beat, 4, strings, 16, 8, 0.07)
    _chords(L, bridge, beat, 4, choir, 24, 8, 0.10)
    _chords(L, bridge, beat, 4, lambda f, d: A.pad(f, d, 3, 0.006, 1200, 1.0, 1.5), 24, 8, 0.07)
    _chords(L, prog, beat, 4, choir, 32, 8, 0.13)
    _chords(L, prog, beat, 4, strings, 32, 8, 0.09)
    for nme in ('D3', 'A3', 'D4', 'F#4'):
        _place(L, A.choir(A.note(nme), 8 * beat, 'o', 1.0, 3.0) * 0.12, 40 * 4 * beat)
    hymn = [('F#4', 2), ('E4', 1), ('D4', 1), ('E4', 2), ('A4', 2), ('B4', 2), ('A4', 1), ('F#4', 1), ('G4', 2), ('F#4', 2),
            ('D4', 2), ('E4', 1), ('F#4', 1), ('G4', 2), ('E4', 2), ('A4', 3), ('G4', 1), ('F#4', 4)]
    horn = lambda f, d: A.horn(f, d, 0.12, 0.4, 2000)
    _line(L, hymn, beat, 8 * 4 * beat, horn, 0.22)
    _line(L, hymn, beat, 16 * 4 * beat, lambda f, d: A.strings(f * 2, d, 0.15, 0.5, 3000, 5.5), 0.2)
    bridge_line = [('B4', 3), ('C#5', 1), ('D5', 4), ('C#5', 2), ('A4', 2), ('B4', 4), ('D5', 3), ('C#5', 1), ('B4', 2), ('A4', 2),
                   ('G4', 4), ('A4', 4)]
    _line(L, bridge_line, beat, 24 * 4 * beat, horn, 0.2)
    _line(L, hymn, beat, 32 * 4 * beat, horn, 0.26)
    _line(L, hymn, beat, 32 * 4 * beat, lambda f, d: A.bell(f * 2, 2.5, 1.2), 0.07)
    for b in range(0, 42, 4):
        _place(L, A.bell(A.note('D5'), 5.0, 1.6) * 0.08, b * 4 * beat)
    for b in (15, 23, 31, 39):
        for k in range(4):
            _place(L, timpani(1.2, 58) * (0.25 + 0.12 * k), (b * 4 + k) * beat)
    return _finish(L, 3.4, 1.6, 0.38)


# ====================================================================== Wayshrine Nocturne
def wayshrine_nocturne():
    beat = 60 / 84
    bars = 52
    L = np.zeros(int(bars * 3 * beat * A.SR) + A.SR * 6)
    prog = [['A2', 'E3', 'A3', 'C4'], ['F2', 'C3', 'F3', 'A3'], ['G2', 'D3', 'G3', 'B3'], ['E2', 'B2', 'E3', 'G#3'],
            ['A2', 'E3', 'A3', 'C4'], ['D3', 'A3', 'D4', 'F4'], ['E2', 'B2', 'E3', 'G#3'], ['A2', 'E3', 'A3', 'C4']]
    # lute: broken chords, one note per half beat, a little uneven like a real hand
    r = np.random.default_rng(11)
    for b in range(bars):
        ch = prog[(b // 2) % len(prog)]
        pattern = [0, 2, 3, 1, 2, 3]
        for k, idx in enumerate(pattern):
            tt = b * 3 * beat + k * beat / 2 + r.uniform(-0.01, 0.012)
            _place(L, A.pluck(A.note(ch[idx]), 1.6, 0.994, 0.45) * (0.16 if k == 0 else 0.11), tt)
    for b in range(0, bars, 2):
        _place(L, A.pad(A.note(prog[(b // 2) % len(prog)][0]), 6 * beat * 1.05, 2, 0.004, 700, 1.5, 2.0) * 0.08, b * 3 * beat)
    theme = [('E5', 2), ('C5', 1), ('A4', 3), ('B4', 1), ('C5', 1), ('D5', 1), ('C5', 3), ('A4', 2), ('C5', 1), ('B4', 3),
             ('G#4', 3), ('A4', 1), ('B4', 1), ('C5', 1), ('D5', 2), ('F5', 1), ('E5', 3), ('D5', 1), ('C5', 1), ('B4', 1),
             ('A4', 6)]
    answer = [('A5', 2), ('G5', 1), ('F5', 3), ('E5', 2), ('D5', 1), ('C5', 3), ('D5', 2), ('E5', 1), ('F5', 2), ('E5', 1),
              ('D5', 3), ('B4', 3), ('C5', 2), ('B4', 1), ('A4', 6)]
    fl = lambda f, d: flute(f, d)
    tt = 8 * 3 * beat
    tt = _line(L, theme, beat, tt, fl, 0.24)
    tt = _line(L, answer, beat, tt + 3 * beat, fl, 0.22)
    tt = _line(L, theme, beat, tt + 6 * beat, lambda f, d: A.chime(f, 2.4, 0.9), 0.14)
    _line(L, theme, beat, 34 * 3 * beat, fl, 0.24)
    _line(L, answer, beat, 44 * 3 * beat, fl, 0.2)
    # crackle of the brazier underneath
    fire = A.crackle(bars * 3 * beat, 40, 9) * 0.05
    _place(L, fire, 0)
    return _finish(L, 2.2, 1.0, 0.3)


# ====================================================================== Tides Beneath the Chapel
def chapel_tides():
    beat = 60 / 60
    bars = 30
    L = np.zeros(int(bars * 4 * beat * A.SR) + A.SR * 8)
    prog = [['F#2', 'C#3', 'A3'], ['D2', 'A2', 'F#3'], ['E2', 'B2', 'G#3'], ['C#2', 'G#2', 'F3'],
            ['F#2', 'C#3', 'A3'], ['B1', 'F#2', 'D3'], ['C#2', 'G#2', 'F3'], ['F#2', 'C#3', 'F#3']]
    organ = lambda f, d: A.pad(f, d, 4, 0.004, 900, 1.2, 2.0, 'square')
    _chords(L, prog, beat, 4, organ, 0, bars, 0.08)
    _chords(L, prog, beat, 4, lambda f, d: A.choir(f * 2, d, 'o', 1.4, 2.0), 8, 22, 0.08)
    # the sea overhead: slow swells of filtered noise
    dur = bars * 4 * beat
    tt = A.t(dur)
    sea = A.lowpass(A.noise(dur, 'brown'), 500) * (0.5 + 0.5 * np.sin(2 * np.pi * tt / 9.0) ** 2) * 0.25
    _place(L, sea, 0)
    # sunken bells, slightly out of tune with each other
    r = np.random.default_rng(21)
    for k in range(18):
        nme = r.choice(['F#4', 'C#5', 'A4', 'E5', 'F#5'])
        _place(L, A.bell(A.note(nme) * (1 + r.uniform(-0.006, 0.006)), 6.0, 2.2) * 0.07, 2 + k * 6.3 + r.uniform(0, 1.5))
    melody = [('C#5', 3), ('B4', 1), ('A4', 2), ('G#4', 2), ('F#4', 4), ('A4', 3), ('B4', 1), ('C#5', 2), ('E5', 2), ('D5', 4),
              ('C#5', 3), ('B4', 1), ('A4', 2), ('B4', 2), ('G#4', 4), ('F#4', 8)]
    _line(L, melody, beat, 8 * 4 * beat, lambda f, d: A.strings(f, d, 0.8, 1.2, 1800, 4.0), 0.18)
    _line(L, melody, beat, 20 * 4 * beat, lambda f, d: A.choir(f, d, 'a', 0.8, 1.2), 0.16)
    return _finish(L, 4.5, 2.4, 0.45)


# ====================================================================== Crown of Ash
def crown_of_ash():
    beat = 60 / 96
    bars = 48
    L = np.zeros(int(bars * 4 * beat * A.SR) + A.SR * 6)
    prog = [['D3', 'F3', 'A3'], ['Bb2', 'D3', 'F3'], ['G2', 'Bb2', 'D3'], ['A2', 'C#3', 'E3']]
    climb = [['D3', 'F3', 'A3'], ['C3', 'E3', 'G3'], ['Bb2', 'D3', 'F3'], ['A2', 'C#3', 'E3'],
             ['G2', 'Bb2', 'D3'], ['F2', 'A2', 'C3'], ['E2', 'G2', 'Bb2'], ['A2', 'C#3', 'E3']]
    strings = lambda f, d: A.strings(f, d, 0.1, 0.3, 2400, 5.0)
    # 0-7 low strings and ticking drum, 8-23 full ostinato and horns, 24-31 the climb with choir,
    # 32-43 everything, 44-47 the fall
    for b in range(bars):
        t0 = b * 4 * beat
        ch = (climb if 24 <= b < 32 else prog)[b % (8 if 24 <= b < 32 else 4)]
        for nme in ch:
            _place(L, strings(A.note(nme), 4 * beat * 1.02) * (0.1 if b < 8 else 0.13), t0)
        root = A.note(ch[0])
        if b >= 4:
            for k in range(8):
                _place(L, A.strings(root * (2 if k % 2 else 1), beat / 2 * 0.9, 0.01, 0.08, 3000, 0) * 0.08, t0 + k * beat / 2)
        if b < 44:
            _place(L, A.drum(46, 0.7, 0.4, 2.4) * 0.7, t0)
            if b >= 8:
                for off in (1.5, 2.5, 3):
                    _place(L, A.drum(56, 0.5, 0.4, 2.6) * 0.55, t0 + off * beat)
                _place(L, A.snare(0.35) * 0.45, t0 + 2 * beat)
            if b % 8 == 7:
                _place(L, A.cymbal(2.5) * 0.35, t0 + 3.5 * beat)
        if 24 <= b < 44:
            for nme in ch:
                _place(L, A.choir(A.note(nme) * 2, 4 * beat, 'a', 0.3, 0.6) * 0.09, t0)
    call = [('D4', 1), ('A4', 1), ('F4', 2), ('E4', 1), ('D4', 1), ('C#4', 2), ('D4', 1), ('F4', 1), ('A4', 1), ('D5', 1),
            ('C#5', 2), ('A4', 2), ('Bb4', 2), ('A4', 1), ('G4', 1), ('F4', 2), ('E4', 2), ('D4', 4), (None, 4)]
    horn = lambda f, d: A.horn(f, d, 0.05, 0.25, 2600)
    _line(L, call, beat, 8 * 4 * beat, horn, 0.22)
    _line(L, call, beat, 16 * 4 * beat, horn, 0.24)
    high = [('A4', 4), ('C5', 4), ('D5', 4), ('E5', 4), ('F5', 4), ('E5', 4), ('D5', 4), ('C#5', 4)]
    _line(L, high, beat, 24 * 4 * beat, lambda f, d: A.strings(f, d, 0.4, 0.5, 3200, 5.5), 0.2)
    _line(L, call, beat, 32 * 4 * beat, horn, 0.28)
    _line(L, call, beat, 32 * 4 * beat, lambda f, d: A.strings(f * 2, d, 0.05, 0.3, 3400, 5.5), 0.14)
    _line(L, call, beat, 38 * 4 * beat, horn, 0.26)
    for nme in ('D2', 'A2', 'D3', 'F3'):
        _place(L, A.pad(A.note(nme), 12 * beat, 3, 0.006, 800, 0.2, 4.0) * 0.12, 44 * 4 * beat)
    _place(L, timpani(3.0, 44) * 0.8, 44 * 4 * beat)
    _place(L, A.bell(A.note('D4'), 8.0, 3.0) * 0.12, 44 * 4 * beat)
    return _finish(L, 2.6, 1.1, 0.28)


# ====================================================================== The Wild Hunt (minibosses)
def theme_wilds():
    """Battle theme for the wild keepers: E dorian in a driving 6/8, frame drums, a fiddle ostinato, a drone and a
    flute that turns into horns. Loops every 29 bars."""
    e8 = 60 / 300           # one eighth note
    bars = 29
    L = np.zeros(int(bars * 6 * e8 * A.SR) + A.SR * 3)
    prog = [['E3', 'B3'], ['E3', 'B3'], ['D3', 'A3'], ['E3', 'B3'], ['C3', 'G3'], ['D3', 'A3'], ['E3', 'B3'], ['B2', 'F#3']]
    fiddle = lambda f, d: A.strings(f, d, 0.02, 0.08, 3600, 6.0)
    for b in range(bars):
        t0 = b * 6 * e8
        ch = prog[b % 8]
        # drone
        for nme in ch:
            _place(L, A.pad(A.note(nme), 6 * e8 * 1.05, 2, 0.004, 900, 0.05, 0.2) * 0.07, t0)
        # frame drum: DUM . tek DUM tek tek
        for off, kind in ((0, 'D'), (2, 't'), (3, 'D'), (4, 't'), (5, 't')):
            if kind == 'D':
                _place(L, A.drum(70, 0.5, 0.5, 2.0) * 0.7, t0 + off * e8)
            else:
                _place(L, A.highpass(A.noise(0.08, 'white'), 2500) * A.env_exp(0.08, 0.03) * 0.25, t0 + off * e8)
        if b >= 2:
            # fiddle ostinato: root-fifth-octave rocking in eighths
            root = A.note(ch[0]) * 2
            for k, mul in enumerate((1, 1.5, 2, 1.5, 1, 1.5)):
                _place(L, fiddle(root * mul, e8 * 0.9) * 0.08, t0 + k * e8)
        if b % 8 == 7:
            _place(L, A.cymbal(1.6) * 0.25, t0 + 5 * e8)
        if b >= 20:
            _place(L, timpani(1.2, 41) * 0.5, t0)
    tune = [('E5', 3), ('D5', 1), ('B4', 2), ('A4', 3), ('B4', 3), ('D5', 3), ('E5', 2), ('F#5', 1), ('G5', 3), ('F#5', 3),
            ('E5', 2), ('D5', 1), ('B4', 3), ('A4', 2), ('G4', 1), ('A4', 3), ('B4', 6), (None, 6)]
    _line(L, tune, e8, 4 * 6 * e8, lambda f, d: flute(f, d, 0.03, 0.12, 5.6), 0.2)
    _line(L, tune, e8, 12 * 6 * e8, lambda f, d: flute(f, d, 0.03, 0.12, 5.6), 0.22)
    horn = lambda f, d: A.horn(f, d, 0.05, 0.2, 2400)
    _line(L, [(n and n[:-1] + str(int(n[-1]) - 1), ln) for n, ln in tune], e8, 20 * 6 * e8, horn, 0.2)
    _line(L, tune, e8, 20 * 6 * e8, lambda f, d: A.strings(f, d, 0.04, 0.2, 3400, 6.0), 0.12)
    return _finish(L, 2.0, 0.8, 0.24)


DISCS = {
    # sound event: (composer, English title, comparator output)
    'disc_lanternguard_hymn': (lanternguard_hymn, "The Lanternguard's Hymn", 3),
    'disc_wayshrine_nocturne': (wayshrine_nocturne, 'Wayshrine Nocturne', 6),
    'disc_chapel_tides': (chapel_tides, 'Tides Beneath the Chapel', 9),
    'disc_crown_of_ash': (crown_of_ash, 'Crown of Ash', 13),
}
