"""The land remembers the Order: worldgen for the overworld landmarks (LandFeatures.java) and the lumenite cluster's
art, models and loot.

data.py calls worldgen(), loot() and tags(); run directly to write the cluster's assets:
    python3 -m tools.oath.landmarks
"""
import json
import math
import os

import numpy as np

from . import data as D
from .paint import Img, Ramp

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ASSETS = os.path.join(ROOT, 'src/main/resources/assets/oathbound')

TEMPERATE = ['minecraft:plains', 'minecraft:sunflower_plains', 'minecraft:meadow', 'minecraft:forest', 'minecraft:birch_forest',
             'minecraft:taiga', 'minecraft:savanna', 'minecraft:windswept_hills', 'minecraft:snowy_plains', 'minecraft:flower_forest']
# feature: (step, placement, biomes)
FEATURES = {
    'waystone': ('surface_structures', [{'type': 'minecraft:rarity_filter', 'chance': 14}], TEMPERATE),
    'order_ruin': ('surface_structures', [{'type': 'minecraft:rarity_filter', 'chance': 40}], TEMPERATE + ['minecraft:dark_forest']),
    'glimmer_glade': ('vegetal_decoration', [{'type': 'minecraft:rarity_filter', 'chance': 6}],
                      ['#minecraft:is_forest', '#minecraft:is_taiga', 'minecraft:dark_forest']),
    'mossy_boulder': ('local_modifications', [{'type': 'minecraft:rarity_filter', 'chance': 8}],
                      ['#minecraft:is_taiga', 'minecraft:old_growth_birch_forest', 'minecraft:dark_forest', 'minecraft:windswept_hills',
                       'minecraft:windswept_forest', 'minecraft:meadow']),
    'lumen_clusters': ('underground_decoration', [
        {'type': 'minecraft:count', 'count': 5},
        {'type': 'minecraft:height_range', 'height': {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': -52},
                                                        'max_inclusive': {'absolute': 48}}}], ['#minecraft:is_overworld']),
}


def worldgen():
    for fid, (step, extra, biomes) in FEATURES.items():
        D.write(f'worldgen/configured_feature/{fid}.json', {'type': f'oathbound:{fid}', 'config': {}})
        placement = list(extra) + [{'type': 'minecraft:in_square'}]
        if step != 'underground_decoration':
            placement.append({'type': 'minecraft:heightmap', 'heightmap': 'WORLD_SURFACE_WG'})
        placement.append({'type': 'minecraft:biome'})
        D.write(f'worldgen/placed_feature/{fid}.json', {'feature': f'oathbound:{fid}', 'placement': placement})
        D.tag(f'worldgen/biome/has_landmark/{fid}', biomes)
        D.write(f'forge/biome_modifier/{fid}.json', {'type': 'forge:add_features', 'biomes': f'#oathbound:has_landmark/{fid}',
                                                     'features': [f'oathbound:{fid}'], 'step': step})


def loot():
    D.write('loot_table/blocks/lumenite_cluster.json', D.silk_or('lumenite_cluster', 'lumenite_shard', 2, 4))


def tags():
    D.tag('block/mineable/pickaxe', ['lumenite_cluster'], 'minecraft')


# ====================================================================== the cluster's art
LUMEN = Ramp('#4a2c08', '#8a5a12', '#c88a1c', '#f0b83a', '#ffd97a', '#fff6d0')


def cluster_art():
    """Five crystal spears fanning from a root, amber at the base and near-white at the tips; and a glow layer."""
    im, glow = Img(16, 16), Img(16, 16)
    spears = [(8.0, 15.8, 0.05, 14.5, 1.35), (5.0, 15.8, -0.38, 10.0, 1.05), (11.2, 15.8, 0.42, 11.0, 1.1), (2.8, 15.8, -0.85, 6.0, 0.8),
              (13.4, 15.8, 0.8, 6.5, 0.8)]
    for bx, by, ang, length, half in spears:
        dx, dy = math.sin(ang), -math.cos(ang)
        for y in range(16):
            for x in range(16):
                cx, cy = x + 0.5 - bx, y + 0.5 - by
                u = cx * dx + cy * dy
                v = cx * dy - cy * dx
                if u < 0 or u > length:
                    continue
                k = u / length
                w = half if k < 0.45 else half * (1 - (k - 0.45) / 0.55) ** 0.8
                if abs(v) > w + 0.15:
                    continue
                # a lit facet on one side, a shadowed one on the other, brighter toward the tip
                facet = 0.18 if v < -0.1 else -0.08
                im.put(x, y, LUMEN.at(min(0.999, max(0.0, 0.3 + k * 0.55 + facet))))
                if abs(v) < 0.55 or k > 0.75:
                    glow.put(x, y, LUMEN.at(min(0.999, 0.7 + k * 0.3)), int(90 + 150 * k))
    im.outline(LUMEN.at(0.05))
    return im, glow


def write_json(rel, obj):
    path = os.path.join(ASSETS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)


def cross(tex, emission=None):
    els = []
    for ang in (45, -45):
        el = {'from': [0.8, 0, 8], 'to': [15.2, 16, 8], 'shade': False,
              'rotation': {'origin': [8, 8, 8], 'axis': 'y', 'angle': ang, 'rescale': True},
              'faces': {'north': {'uv': [0, 0, 16, 16], 'texture': tex}, 'south': {'uv': [0, 0, 16, 16], 'texture': tex}}}
        if emission:
            el['light_emission'] = emission
        els.append(el)
    return els


def assets():
    im, glow = cluster_art()
    im.save(os.path.join(ASSETS, 'textures/block/lumenite_cluster.png'))
    glow.save(os.path.join(ASSETS, 'textures/block/lumenite_cluster_glow.png'))
    write_json('models/block/lumenite_cluster.json', {
        'parent': 'minecraft:block/block', 'ambientocclusion': False,
        'textures': {'particle': 'oathbound:block/lumenite_cluster', 'cross': 'oathbound:block/lumenite_cluster',
                     'glow': 'oathbound:block/lumenite_cluster_glow'},
        'elements': cross('#cross') + cross('#glow', 12)})
    rot = {'up': {}, 'down': {'x': 180}, 'north': {'x': 90}, 'south': {'x': 90, 'y': 180}, 'east': {'x': 90, 'y': 90}, 'west': {'x': 90, 'y': 270}}
    variants = {}
    for facing, r in rot.items():
        for wet in ('false', 'true'):
            variants[f'facing={facing},waterlogged={wet}'] = {'model': 'oathbound:block/lumenite_cluster', **r}
    write_json('blockstates/lumenite_cluster.json', {'variants': variants})
    write_json('models/item/lumenite_cluster.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'oathbound:block/lumenite_cluster'}})
    write_json('items/lumenite_cluster.json', {'model': {'type': 'minecraft:model', 'model': 'oathbound:item/lumenite_cluster'}})
    print('lumenite cluster written')


NAMES = {'lumenite_cluster': 'Lumenite Cluster'}


if __name__ == '__main__':
    assets()
