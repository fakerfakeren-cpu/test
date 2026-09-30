"""Pictures for the Chronicle's quest pages, cut from the CI client test's real screenshots of each place.

Quests about a place show where you are going, quests about a creature show it close up, and the rest show their
item large (ChronicleScreen).  Run after a CI report has refreshed docs/oathbound/ci:  python3 -m tools.oath.questart
"""
import os

from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHOTS = os.path.join(ROOT, 'docs/oathbound/ci')
OUT = os.path.join(ROOT, 'src/main/resources/assets/oathbound/textures/gui/quest')
W, H = 304, 128

# quest id -> screenshot
PLACES = {
    'wayshrine': 'wayshrine', 'chapel': 'drowned_chapel', 'spire': 'arcanist_spire', 'barrow': 'barrow_of_kings',
    'honest_king': 'hall_of_kings', 'citadel': 'sundered_gate', 'gate': 'sundered_gate', 'gloaming': 'the_gloaming',
    'throne': 'hollow_throne', 'morvane': 'morvane', 'grove_king': 'stags_ring', 'bog_mother': 'bog_mothers_house',
    'cinder_colossus': 'cinder_sanctum', 'last_watch': 'last_watch', 'tideglass': 'tideglass_grotto', 'delve': 'lumenite_headframe',
    'star_readers': 'shattered_observatory',
}


# quest id -> close-up portrait the client test takes of the creature (Showcase "portrait_*" scenes)
CREATURES = {q: 'portrait_' + q for q in ('caldris', 'veyl', 'hrodgar', 'veilhound', 'gloamling', 'lanternmoth', 'forsworn')}


# the portraits frame the creature at the centre of the shot; smaller creatures get a closer crop
PORTRAIT_WIDTH = {'lanternmoth': 300, 'gloamling': 360, 'veilhound': 380}
PORTRAIT_CY = {'caldris': 0.41, 'veyl': 0.41}


def picture(shot):
    im = Image.open(os.path.join(SHOTS, shot + '.jpg')).convert('RGB')
    w, h = im.size
    if shot.startswith('portrait_'):
        cw = int(PORTRAIT_WIDTH.get(shot[len('portrait_'):], 440) * w / 960)
        ch = int(cw * H / W)
        cx, cy = w // 2, int(h * PORTRAIT_CY.get(shot[len('portrait_'):], 0.47))
        return im.crop((cx - cw // 2, cy - ch // 2, cx - cw // 2 + cw, cy - ch // 2 + ch)).resize((W, H), Image.LANCZOS)
    ch = int(w * H / W)
    top = max(0, min(h - ch, int((h - ch) * 0.55)))
    im = im.crop((0, top, w, top + ch)).resize((W, H), Image.LANCZOS)
    # a touch warmer and softer at the edges, like a plate in an old book
    im = ImageEnhance.Color(im).enhance(0.9)
    return im


def generate():
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for quest, shot in {**PLACES, **CREATURES}.items():
        if os.path.exists(os.path.join(SHOTS, shot + '.jpg')):
            picture(shot).save(os.path.join(OUT, quest + '.png'), optimize=True)
            n += 1
    print('quest pictures written:', n)


if __name__ == '__main__':
    generate()
