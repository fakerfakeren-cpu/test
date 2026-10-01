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


# quest id -> the items whose recipes its page shows (cycled in the picture plate)
RECIPES = {
    'oathsteel': ['oathsteel_blend', 'oathsteel_ingot'], 'lantern': ['wardens_lantern', 'oathsteel_nugget'],
    'wayshrine': ['wayshrine_brazier'], 'oathsteel_arms': ['oathsteel_longsword', 'wardens_halberd'],
    'oathsteel_armor': ['oathsteel_helmet', 'oathsteel_chestplate', 'oathsteel_leggings', 'oathsteel_boots'],
    'arcanist': ['arcanist_hood', 'arcanist_robe', 'arcanist_leggings', 'arcanist_boots'], 'dawnstring': ['dawnstring_longbow'],
    'oathkey': ['oathkey'], 'sickle': ['shadowreap_sickle'], 'elixir': ['elixir_of_dawn'], 'flask': ['lumen_flask'],
    'everflame': ['everflame_lantern'],
    'alchemist': ['elixir_of_the_wayfarer', 'elixir_of_shrouds', 'elixir_of_valor', 'elixir_of_tides', 'elixir_of_wards', 'elixir_of_dawn'],
}
RECIPE_DIR = os.path.join(ROOT, 'src/main/resources/data/oathbound/recipe')
CRAFT, COOK = ('minecraft:crafting_shaped', 'minecraft:crafting_shapeless'), ('minecraft:smelting', 'minecraft:blasting')


def find_recipe(item):
    """The recipe that makes oathbound:<item>, as a 3x3 grid (crafting) or a single input (smelting)."""
    import json
    best = None
    for f in sorted(os.listdir(RECIPE_DIR)):
        d = json.load(open(os.path.join(RECIPE_DIR, f)))
        res = d.get('result', {})
        rid = res.get('id') if isinstance(res, dict) else res
        if rid != f'oathbound:{item}' or d['type'] not in CRAFT + COOK:
            continue
        if d['type'] == 'minecraft:crafting_shaped':
            grid = [''] * 9
            for r, row in enumerate(d['pattern']):
                for c, ch in enumerate(row):
                    if ch != ' ':
                        grid[r * 3 + c] = d['key'][ch]
            rec = {'kind': 'craft', 'grid': grid}
        elif d['type'] == 'minecraft:crafting_shapeless':
            ings = list(d['ingredients'])
            rec = {'kind': 'craft', 'grid': ings + [''] * (9 - len(ings))}
        else:
            ing = d['ingredient']
            rec = {'kind': 'smelt', 'grid': [ing if isinstance(ing, str) else ing[0]]}
        rec['result'] = rid
        rec['count'] = res.get('count', 1) if isinstance(res, dict) else 1
        if best is None or (best['kind'] == 'smelt' and rec['kind'] == 'craft' and item != 'oathsteel_ingot'):
            best = rec
    return best


def recipes():
    import json
    out = {}
    for quest, items in RECIPES.items():
        recs = [r for r in (find_recipe(i) for i in items) if r]
        missing = [i for i in items if not find_recipe(i)]
        assert not missing, (quest, missing)
        out[quest] = recs
    path = os.path.join(ROOT, 'src/main/resources/assets/oathbound/chronicle/recipes.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(out, f, indent=1)
    print('chronicle recipes:', sum(len(v) for v in out.values()))


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
    recipes()
