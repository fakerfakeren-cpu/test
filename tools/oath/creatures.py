"""Oathbound creature models: geometry specs that match the Java animation rigs, painted skins, and the
generated ModelDefs.java.

Run from the repository root:  python3 -m tools.oath.creatures [preview-dir]

Every model hangs from a "hull" part pivoted at the feet (0, 24, 0), so y is measured upward as negative
numbers from the ground. Part names are the contract with the Java models (Rig.part looks them up through
ModelDefs.path), so rename them in both places or not at all.
"""
import os
import sys

import numpy as np

from .model import Model, P, C, render, save_rgba

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEX_DIR = os.path.join(ROOT, 'src/main/resources/assets/oathbound/textures/entity')
JAVA = os.path.join(ROOT, 'src/main/java/com/oathbound/client/model/ModelDefs.java')


# ====================================================================== everyday creatures
def lanternmoth():
    """A hand-sized moth whose abdomen glows like a lantern; the Lanternguard's heraldic beast."""
    return Model('lanternmoth', 64, [
        P('body', (0, -4, 0),
          C(-1.5, -1.5, -2, 3, 3, 4, 'moth_fur'),
          C(-2, -2, -2.6, 4, 4, 1, 'moth_ruff'),
          kids=[
              P('head', (0, -0.5, -2.6),
                C(-1, -1, -2, 2, 2, 2, 'moth_fur', 'moth_eyes'),
                kids=[P('antenna_l', (0.5, -1, -1.5), C(0, -4, 0, 2, 4, 0, 'moth_antenna_l'), rot=(-0.35, 0, 0.35)),
                      P('antenna_r', (-0.5, -1, -1.5), C(-2, -4, 0, 2, 4, 0, 'moth_antenna_r'), rot=(-0.35, 0, -0.35))],
                rot=(0.25, 0, 0)),
              P('abdomen', (0, 0, 2),
                C(-1.5, -1.5, 0, 3, 3, 2, 'moth_abdomen'),
                C(-1.5, -1.5, 2, 3, 3, 1, 'moth_fur', grow=0.1),
                C(-1, -1, 3, 2, 2, 2, 'moth_abdomen'),
                C(-0.5, -0.5, 5, 1, 1, 1, 'moth_abdomen'),
                rot=(-0.3, 0, 0)),
              P('left_wing', (1.5, -1, -0.5),
                C(0, 0, -4, 9, 0, 7, 'moth_wing_l'),
                C(0, 0.2, 1, 7, 0, 5, 'moth_hindwing_l')),
              P('right_wing', (-1.5, -1, -0.5),
                C(-9, 0, -4, 9, 0, 7, 'moth_wing_r'),
                C(-7, 0.2, 1, 7, 0, 5, 'moth_hindwing_r')),
          ]),
    ])


def gloamling():
    """A gangling imp of the dusk: glowing eyes, a jagged grin, long clawed arms and an ember-tipped tail."""
    leg = lambda x: P(('left' if x > 0 else 'right') + '_leg', (x, -5, 0.5),
                      C(-1, 0, -1, 2, 5, 2, 'gloam_hide'),
                      C(-1, 4, -2, 2, 1, 1, 'gloam_claw'))
    return Model('gloamling', 64, [
        leg(1.5), leg(-1.5),
        P('body', (0, -5, 0.5),
          C(-2.5, -6, -1.5, 5, 6, 3, 'gloam_hide'),
          C(-1.5, -5, -2, 3, 4, 1, 'gloam_belly'),
          C(-0.5, -6.5, 1.5, 1, 2, 1, 'horn'),
          C(-0.5, -3.5, 1.5, 1, 1, 1, 'horn'),
          kids=[
              P('head', (0, -6, -0.5),
                C(-2.5, -5, -2.5, 5, 5, 5, 'gloam_head', 'gloam_face'),
                C(-3.5, -3.5, -0.5, 1, 2, 1, 'gloam_head'),
                C(2.5, -3.5, -0.5, 1, 2, 1, 'gloam_head'),
                C(-3, -6, -1, 1, 2, 1, 'horn'),
                C(2, -6, -1, 1, 2, 1, 'horn'),
                C(-3.5, -7, 0, 1, 1, 1, 'horn'),
                C(2.5, -7, 0, 1, 1, 1, 'horn')),
              P('left_arm', (2.5, -5.5, 0),
                C(0, -0.5, -1, 2, 7, 2, 'gloam_hide'),
                C(0, 6.5, -1.5, 2, 2, 1, 'gloam_claw'),
                C(0.5, 6.5, 0, 1, 2, 1, 'gloam_claw')),
              P('right_arm', (-2.5, -5.5, 0),
                C(-2, -0.5, -1, 2, 7, 2, 'gloam_hide'),
                C(-2, 6.5, -1.5, 2, 2, 1, 'gloam_claw'),
                C(-1.5, 6.5, 0, 1, 2, 1, 'gloam_claw')),
              P('tail', (0, -1, 1.5),
                C(-0.5, -0.5, 0, 1, 1, 6, 'gloam_tail'),
                C(-1, -1, 6, 2, 2, 2, 'gloam_ember')),
          ]),
    ])


def forsworn_knight():
    """An oathbreaker of the Lanternguard in blackened plate: a broken crimson oath-sigil on the breast,
    a violet slit of light for eyes, a tattered cape and a long sword."""
    def leg(x):
        return P(('left' if x > 0 else 'right') + '_leg', (x, -13, 0),
                 C(-2, 0, -2, 4, 13, 4, 'knight_plate'),
                 C(-2.5, 5, -2.6, 5, 2, 1, 'knight_trim'),
                 C(-2, 11, -3, 4, 2, 1, 'knight_plate'))
    return Model('forsworn_knight', 128, [
        leg(2.2), leg(-2.2),
        P('body', (0, -13, 0),
          C(-4.5, -12, -2.5, 9, 12, 5, 'knight_plate', 'knight_chest'),
          C(-5, -2, -3, 10, 2, 6, 'knight_belt'),
          C(-4, 0, -3.2, 8, 4, 1, 'knight_plate'),
          C(-4, 0, 2.2, 8, 4, 1, 'knight_plate'),
          C(-3, -13, -2, 6, 1, 4, 'knight_trim'),
          kids=[
              P('head', (0, -12.5, 0),
                C(-3.5, -8, -3.5, 7, 8, 7, 'knight_helm', 'knight_visor'),
                C(-0.5, -9, -3.5, 1, 1, 7, 'knight_trim'),
                C(-2.5, -2, -4, 5, 2, 1, 'knight_helm'),
                C(-0.5, -11, -1.5, 1, 2, 6, 'plume'),
                C(-0.5, -10, 4.5, 1, 7, 2, 'plume')),
              P('left_arm', (6, -11, 0),
                C(-1.5, -2.5, -3, 5, 4, 6, 'knight_pauldron'),
                C(-1, -1, -2, 4, 12, 4, 'knight_plate'),
                C(-1.5, 8, -2.5, 5, 3, 5, 'knight_gauntlet')),
              P('right_arm', (-6, -11, 0),
                C(-3.5, -2.5, -3, 5, 4, 6, 'knight_pauldron'),
                C(-3, -1, -2, 4, 12, 4, 'knight_plate'),
                C(-3.5, 8, -2.5, 5, 3, 5, 'knight_gauntlet'),
                C(-1.5, 9, -18, 1, 2, 14, 'knight_blade'),
                C(-2, 7, -4.5, 2, 6, 1, 'knight_trim'),
                C(-1.5, 9.5, -4, 1, 1, 2, 'leather_grip'),
                C(-2, 9, 2.5, 2, 2, 1, 'knight_trim')),
              P('cape', (0, -12, 2.6),
                C(-4.5, 0, 0, 9, 17, 0, 'tattered_cape'), rot=(0.08, 0, 0)),
          ]),
    ])


def barrow_wight():
    """A drifting barrow-spirit in sea-green grave cloth; a gold torc and circlet from its burial, bone
    hands with cold-lit claws, and nothing but two teal sparks inside the hood."""
    def arm(x):
        s = 1 if x > 0 else -1
        o = -1 if s > 0 else -2
        return P(('left' if x > 0 else 'right') + '_arm', (x, -10, 0),
                 C(o, -1, -1.5, 3, 9, 3, 'wight_robe'),
                 C(o + 0.5, 8, -1, 2, 3, 2, 'bone'),
                 C(o + 0.5, 11, -1, 2, 2, 1, 'wight_claw'),
                 C(o, 4, 1.5, 3, 7, 0, 'wight_tatter'))
    return Model('barrow_wight', 128, [
        P('body', (0, -15, 0),
          C(-4, -11, -2.5, 8, 11, 5, 'wight_robe', 'ribs'),
          C(-5, -11.5, -3, 10, 3, 6, 'wight_hood'),
          C(-3, -12, -3.2, 6, 1, 5, 'grave_gold'),
          kids=[
              P('head', (0, -11.5, -0.5),
                C(-3.5, -7, -3.5, 7, 7, 7, 'wight_hood', 'wight_face'),
                C(-2.5, -8, -2, 5, 1, 5, 'wight_hood'),
                C(-3, -6, 3.5, 6, 7, 0, 'wight_tatter'),
                C(-3.5, -6, -3.5, 7, 1, 7, 'grave_gold', grow=0.25)),
              arm(4.5), arm(-4.5),
              P('tail1', (0, 0, 0),
                C(-4, 0, -2.5, 8, 8, 5, 'wight_robe'),
                kids=[P('tail2', (0, 8, 0.5), C(-3, 0, -2, 6, 7, 4, 'wight_tatter'))]),
          ]),
    ])


def animated_tome():
    """A grimoire of the Arcanist Spire that learned to fly: covers beating like wings, an eye on its
    binding, pages fluttering with rune-light and two bookmark ribbons trailing."""
    return Model('animated_tome', 64, [
        P('spine', (0, -2, 0),
          C(-1, -0.5, -4.5, 2, 1, 9, 'tome_spine'),
          C(-0.5, 0.5, 1.5, 0, 5, 1, 'tome_ribbon'),
          C(0.5, 0.5, -0.5, 0, 4, 1, 'tome_ribbon'),
          kids=[
              P('cover_left', (1, 0, 0),
                C(0, -0.5, -4.5, 6, 1, 9, 'tome_cover', 'tome_eye', face='bottom'),
                C(0.3, -1.5, -4, 5, 1, 8, 'tome_pages'),
                C(6, -0.5, -1, 1, 1, 2, 'grave_gold')),
              P('cover_right', (-1, 0, 0),
                C(-6, -0.5, -4.5, 6, 1, 9, 'tome_cover', 'tome_runes', face='bottom'),
                C(-5.3, -1.5, -4, 5, 1, 8, 'tome_pages'),
                C(-7, -0.5, -1, 1, 1, 2, 'grave_gold')),
              P('pages', (0, -0.5, 0),
                C(-0.5, -6, -3.5, 1, 6, 7, 'tome_pages', 'tome_runes', face=('left', 'right'))),
          ]),
    ])


def veilhound():
    """A lean hound of the Gloaming, darker than its own shadow, with violet crystal spines."""
    def leg(name, x, z):
        return P(name, (x, 1, z),
                 C(-1.5, 0, -1.5, 3, 5, 3, 'hound_hide'),
                 C(-1, 5, -1, 2, 3, 2, 'hound_hide'),
                 C(-1.5, 8, -2, 3, 1, 3, 'hound_paw'))
    return Model('veilhound', 64, [
        P('body', (0, -10, 0),
          C(-3.5, -4, -7, 7, 8, 7, 'hound_hide'),
          C(-3, -3.5, 0, 6, 6, 7, 'hound_hide'),
          C(-3.5, -5, -7.5, 7, 3, 5, 'hound_mane'),
          C(-0.5, -8, -6, 1, 3, 1, 'hound_spines'),
          C(-0.5, -8.5, -3.5, 1, 4, 1, 'hound_spines'),
          C(-0.5, -7, -1, 1, 3, 1, 'hound_spines'),
          C(-0.5, -6, 2, 1, 2, 1, 'hound_spines'),
          C(-2.5, -6.5, -5, 1, 2, 1, 'hound_spines'),
          C(1.5, -6.5, -5, 1, 2, 1, 'hound_spines'),
          kids=[
              P('head', (0, -2, -7),
                C(-3, -3, -5, 6, 5, 5, 'hound_head', 'hound_face'),
                C(-2, -1, -9, 4, 3, 4, 'hound_head', 'fangs'),
                C(-3, -5.5, -2, 2, 3, 1, 'hound_hide'),
                C(1, -5.5, -2, 2, 3, 1, 'hound_hide'),
                kids=[P('jaw', (0, 2, -5), C(-2, 0, -4, 4, 2, 4, 'hound_jaw', 'teeth'))]),
              leg('leg_fl', 2, -5), leg('leg_fr', -2, -5), leg('leg_bl', 2, 5), leg('leg_br', -2, 5),
              P('tail', (0, -2, 7),
                C(-1, -1, 0, 2, 2, 7, 'hound_tail'),
                C(-1.5, -1.5, 7, 3, 3, 3, 'hound_wisp')),
          ]),
    ])


def spectral_housecarl():
    """One of Hrodgar's oath-sworn guards, still keeping watch as a pale-teal ghost: mail, fur mantle,
    bearded helm, round shield and a bearded axe."""
    def leg(x):
        return P(('left' if x > 0 else 'right') + '_leg', (x, -12, 0),
                 C(-2, 0, -2, 4, 12, 4, 'spirit_trousers'),
                 C(-2.5, 8, -2.5, 5, 4, 5, 'spirit_fur'))
    return Model('spectral_housecarl', 128, [
        leg(2), leg(-2),
        P('body', (0, -12, 0),
          C(-4, -12, -2, 8, 12, 4, 'spirit_mail'),
          C(-4.5, -1.5, -2.5, 9, 2, 5, 'spirit_leather'),
          C(-4.5, 0.5, -2.5, 9, 3, 5, 'spirit_mail'),
          C(-5, -12.5, -3, 10, 3, 6, 'spirit_fur'),
          kids=[
              P('head', (0, -12, 0),
                C(-4, -8, -4, 8, 8, 8, 'spirit_helm', 'housecarl_face'),
                C(-1, -10, -1, 2, 2, 2, 'spirit_iron'),
                C(-3, -2, -5, 6, 4, 1, 'spirit_beard')),
              P('left_arm', (5, -10, 0),
                C(-1, -2, -2, 4, 12, 4, 'spirit_mail'),
                C(-1.5, 5, -2.5, 5, 3, 5, 'spirit_leather'),
                kids=[P('shield', (1, 7, 0),
                        C(-6, -6, -3.5, 12, 12, 1, 'spirit_shield'),
                        C(-1.5, -1.5, -4.5, 3, 3, 1, 'spirit_iron'),
                        rot=(0.9, 0, 0))]),
              P('right_arm', (-5, -10, 0),
                C(-3, -2, -2, 4, 12, 4, 'spirit_mail'),
                C(-3.5, 5, -2.5, 5, 3, 5, 'spirit_leather'),
                C(-1.5, 9, -17, 1, 1, 15, 'spirit_wood'),
                C(-1.5, 10, -17, 1, 4, 3, 'spirit_axehead'),
                C(-1.5, 12, -19, 1, 4, 2, 'spirit_axehead'),
                C(-1.5, 16, -20, 1, 1, 5, 'spirit_edge'),
                C(-1.5, 7, -17, 1, 2, 2, 'spirit_axehead')),
          ]),
    ])


# ====================================================================== the seal keepers
def sir_caldris():
    """Keeper of the Drowned Chapel: barnacled verdigris plate, a fin-crested helm with a tide-lit visor,
    a tower shield held before him and a ship's anchor for a weapon."""
    def leg(x, barn):
        return P(('left' if x > 0 else 'right') + '_leg', (x, -14, 0),
                 C(-2.5, 0, -2.5, 5, 14, 5, 'drowned_plate'),
                 C(-3, 6, -3, 6, 2, 1, 'drowned_trim'),
                 C(-3, 12, -3.5, 6, 2, 6, 'drowned_trim'),
                 C(barn, 3, -3, 1, 1, 1, 'barnacle'))
    return Model('sir_caldris', 128, [
        leg(2.5, 1.5), leg(-2.5, -2),
        P('body', (0, -14, 0),
          C(-5, -13, -3, 10, 13, 6, 'drowned_plate', 'wave_emblem'),
          C(-5.5, -2, -3.5, 11, 2, 7, 'drowned_trim'),
          C(-5, 0, -3.5, 10, 5, 1, 'drowned_plate'),
          C(-5, 0, 2.5, 10, 5, 1, 'drowned_plate'),
          C(-4, -14.5, -2.5, 8, 2, 5, 'drowned_trim'),
          C(3, -11, -3.4, 2, 2, 1, 'barnacle'),
          C(-4, -6, -3.4, 1, 1, 1, 'barnacle'),
          C(-3, -9, 3, 2, 1, 1, 'barnacle'),
          kids=[
              P('head', (0, -13.5, 0),
                C(-4, -9, -4, 8, 9, 8, 'drowned_helm', 'drowned_visor'),
                C(-0.5, -13, -3, 1, 4, 9, 'drowned_fin'),
                C(-5, -7, -1, 1, 4, 4, 'drowned_fin'),
                C(4, -7, -1, 1, 4, 4, 'drowned_fin')),
              P('left_arm', (7, -11.5, 0),
                C(-2, -3, -3.5, 6, 5, 7, 'drowned_pauldron'),
                C(-1.5, -1, -2.5, 5, 12, 5, 'drowned_plate'),
                C(-2, 8, -3, 6, 4, 6, 'drowned_trim'),
                kids=[P('shield', (1, 11, 0),
                        C(-6.5, 0, -8, 13, 1, 20, 'tide_shield', 'shield_emblem', face='bottom'),
                        C(-1.5, 1, 0, 3, 1, 3, 'anchor_iron'),
                        C(3, 1, 7, 2, 1, 2, 'barnacle'))]),
              P('right_arm', (-7, -11.5, 0),
                C(-4, -3, -3.5, 6, 5, 7, 'drowned_pauldron'),
                C(-3.5, -1, -2.5, 5, 12, 5, 'drowned_plate'),
                C(-4, 8, -3, 6, 4, 6, 'drowned_trim'),
                kids=[P('anchor', (-1, 10, 0),
                        C(-1, -7, -1, 2, 20, 2, 'anchor_iron'),
                        C(-4, -4, -1, 8, 1, 2, 'anchor_iron'),
                        C(-1.5, -10, -0.5, 3, 3, 1, 'anchor_iron'),
                        C(-6, 12, -1.5, 12, 2, 3, 'anchor_iron'),
                        C(-7, 8, -1, 2, 5, 2, 'anchor_iron'),
                        C(5, 8, -1, 2, 5, 2, 'anchor_iron'),
                        C(-8, 6, -1.5, 2, 3, 3, 'anchor_iron'),
                        C(6, 6, -1.5, 2, 3, 3, 'anchor_iron'),
                        C(1, 1, 1, 0, 8, 1, 'kelp'))]),
              P('cape', (0, -13, 3),
                C(-5, 0, 0, 10, 20, 0, 'kelp_cape'),
                C(-4, 18, 0.05, 1, 6, 0, 'kelp'),
                C(1, 17, 0.05, 1, 7, 0, 'kelp'),
                rot=(0.1, 0, 0)),
          ]),
    ])


def archmage_veyl():
    """Keeper of the Arcanist Spire: an archmage who never set down his work; deep-blue robes with silver
    trim and rune-lit hems, a white beard in a void of a hood, a turning halo of runes and a crystal staff."""
    return Model('archmage_veyl', 128, [
        P('body', (0, -16, 0),
          C(-4, -12, -2.5, 8, 12, 5, 'arcane_robe', 'robe_runes'),
          C(-5, -12.5, -3, 10, 4, 6, 'arcane_mantle'),
          C(-4.5, -3, -3, 9, 2, 6, 'arcane_sash'),
          C(-4, -15, 0.5, 8, 4, 2, 'arcane_mantle'),
          kids=[
              P('head', (0, -12.5, 0),
                C(-3.5, -8, -3.5, 7, 8, 7, 'hood_deep', 'veyl_face'),
                C(-2.5, -10, -1.5, 5, 2, 5, 'hood_deep'),
                C(-1, -11, 1.5, 2, 2, 3, 'hood_deep'),
                kids=[P('halo', (0, -4.5, 5), C(-8, -8, 0, 16, 16, 0, 'halo_ring'))]),
              P('left_arm', (5, -10.5, 0),
                C(-1, -1.5, -2, 4, 10, 4, 'arcane_robe'),
                C(-1.5, 6, -2.5, 5, 4, 5, 'arcane_cuff'),
                C(-0.5, 10, -1, 2, 2, 2, 'veyl_hand')),
              P('right_arm', (-5, -10.5, 0),
                C(-3, -1.5, -2, 4, 10, 4, 'arcane_robe'),
                C(-3.5, 6, -2.5, 5, 4, 5, 'arcane_cuff'),
                C(-1.5, 10, -1, 2, 2, 2, 'veyl_hand'),
                kids=[P('staff', (-1, 11, -2),
                        C(-0.5, -17, -0.5, 1, 29, 1, 'staff_wood'),
                        C(-1.5, -19, -0.5, 1, 3, 1, 'staff_wood'),
                        C(0.5, -19, -0.5, 1, 3, 1, 'staff_wood'),
                        C(-0.5, -19, -1.5, 1, 3, 1, 'staff_wood'),
                        C(-0.5, -19, 0.5, 1, 3, 1, 'staff_wood'),
                        C(-1, -23, -1, 2, 4, 2, 'staff_crystal'))]),
              P('skirt', (0, 0, 0),
                C(-4.5, 0, -3, 9, 7, 6, 'arcane_robe'),
                kids=[P('skirt2', (0, 7, 0), C(-5, 0, -3.5, 10, 8, 7, 'robe_hem'))]),
              P('left_leg', (2, 0, 0), C(-1, 0, -1, 2, 12, 2, 'arcane_robe')),
              P('right_leg', (-2, 0, 0), C(-1, 0, -1, 2, 12, 2, 'arcane_robe')),
          ]),
    ])


def hrodgar():
    """The Barrow King: a giant crowned skeleton whose soul still burns cold inside a see-through ribcage;
    a grave-iron collar and pauldrons, a royal cape gone to rags and a rune-flail on a chain."""
    def leg(x):
        return P(('left' if x > 0 else 'right') + '_leg', (x, -18, 0),
                 C(-1.5, 0, -1.5, 3, 10, 3, 'bone'),
                 C(-2.5, 9, -2.5, 5, 9, 5, 'grave_iron'),
                 C(-2.5, 16, -4, 5, 2, 2, 'grave_iron'),
                 C(-2, 8, -2.6, 4, 2, 1, 'grave_gold'))

    def arm(x):
        s = 1 if x > 0 else -1
        o = 0 if s > 0 else -2
        kids = []
        if s < 0:
            kids = [P('flail_chain', (-1, 19, -1),
                      C(-0.5, 0, -0.5, 1, 8, 1, 'chain'),
                      kids=[P('flail_head', (0, 8, 0),
                              C(-3, 0, -3, 6, 6, 6, 'soul_iron'),
                              C(-4, 2, -1, 1, 2, 2, 'grave_iron'),
                              C(3, 2, -1, 1, 2, 2, 'grave_iron'),
                              C(-1, 6, -1, 2, 1, 2, 'grave_iron'),
                              C(-1, 2, -4, 2, 2, 1, 'grave_iron'),
                              C(-1, 2, 3, 2, 2, 1, 'grave_iron'))])]
        return P(('left' if x > 0 else 'right') + '_arm', (x, -15, 0),
                 C(o - 2.5, -3, -4, 7, 6, 8, 'grave_iron'),
                 C(o - 0.5, 0, -1.5, 3, 18, 3, 'bone'),
                 C(o - 1.5, 8, -2.5, 5, 5, 5, 'grave_iron'),
                 C(o - 1.5, 15, -2.5, 5, 5, 5, 'grave_iron'),
                 kids=kids)
    return Model('hrodgar', 256, [
        leg(3.5), leg(-3.5),
        P('body', (0, -18, 0),
          C(-5, -2, -3, 10, 4, 6, 'bone'),
          C(-1.5, -12, 0, 3, 10, 3, 'bone'),
          C(-6, -16, -4, 12, 10, 8, 'rib_cage'),
          C(-2.5, -13, -2, 5, 5, 5, 'soul_core'),
          C(-5.5, -3, -3.5, 11, 2, 7, 'grave_gold'),
          C(-4, -1, -4, 8, 10, 0, 'royal_tabard'),
          C(-7, -17.5, -4.5, 14, 3, 9, 'grave_iron'),
          kids=[
              P('head', (0, -17.5, -1),
                C(-4.5, -9, -4.5, 9, 9, 9, 'skull', 'skull_face'),
                C(-3.5, -1, -4.5, 7, 2, 6, 'bone'),
                C(-5, -10, -5, 10, 2, 10, 'grave_iron'),
                C(-5, -13, -5, 1, 3, 1, 'grave_iron'),
                C(-0.5, -14, -5, 1, 4, 1, 'grave_iron'),
                C(4, -13, -5, 1, 3, 1, 'grave_iron'),
                C(-5, -12, 4, 1, 2, 1, 'grave_iron'),
                C(4, -12, 4, 1, 2, 1, 'grave_iron'),
                C(-1, -12, -5.4, 2, 2, 1, 'soul_core')),
              arm(8.5), arm(-8.5),
              P('cape', (0, -17, 4.5), C(-7, 0, 0, 14, 30, 0, 'royal_cape'), rot=(0.1, 0, 0)),
          ]),
    ])


def morvane():
    """Morvane, the Hollow King: armour with nothing inside it but a violet void, a floating crown of
    black-gold spikes, a cape that frays into dusk and a greatsword that still remembers its oath."""
    def leg(x):
        return P(('left' if x > 0 else 'right') + '_leg', (x, -15, 0),
                 C(-2.5, 0, -2.5, 5, 15, 5, 'hollow_plate'),
                 C(-3, 6, -3, 6, 2, 1, 'hollow_trim'),
                 C(-3, 13, -4, 6, 2, 7, 'hollow_trim'))

    def arm(x):
        s = 1 if x > 0 else -1
        o = 0 if s > 0 else -2
        kids = []
        if s < 0:
            kids = [P('sword', (-1, 11.5, 0),
                      C(-1.5, -1.5, 3, 3, 3, 2, 'crown_gold'),
                      C(-1, -1, -4, 2, 2, 7, 'leather_grip'),
                      C(-1.5, -5, -6, 3, 10, 2, 'crown_gold'),
                      C(-0.5, -2, -30, 1, 4, 24, 'oathblade', 'blade_runes', face=('left', 'right')),
                      C(-0.5, -1, -32, 1, 2, 2, 'oathblade'))]
        return P(('left' if x > 0 else 'right') + '_arm', (x, -12.5, 0),
                 C(o - 2.5, -3.5, -4, 7, 6, 8, 'hollow_pauldron'),
                 C(o, -6, -1, 2, 3, 2, 'hollow_trim'),
                 C(o - 1.5, -1, -2.5, 5, 13, 5, 'hollow_plate'),
                 C(o - 2, 9, -3, 6, 5, 6, 'hollow_trim'),
                 kids=kids)
    return Model('morvane', 256, [
        leg(3), leg(-3),
        P('body', (0, -15, 0),
          C(-6, -14, -3.5, 12, 14, 7, 'hollow_plate', 'hollow_core'),
          C(-5.5, -3, -4, 11, 3, 8, 'hollow_trim'),
          C(-5, 0, -4, 10, 6, 1, 'hollow_plate'),
          C(-5, 0, 3, 10, 6, 1, 'hollow_plate'),
          C(-4.5, -15.5, -3, 9, 2, 6, 'hollow_trim'),
          C(-3, -12, 3.5, 2, 3, 2, 'hollow_trim'),
          C(1, -12, 3.5, 2, 3, 2, 'hollow_trim'),
          kids=[
              P('head', (0, -15, 0),
                C(-4, -9, -4, 8, 9, 8, 'hollow_helm', 'hollow_visor'),
                C(-4.5, -3, -4.5, 9, 3, 9, 'hollow_plate'),
                C(-5, -8, -1, 1, 3, 3, 'hollow_trim'),
                C(4, -8, -1, 1, 3, 3, 'hollow_trim'),
                kids=[P('crown', (0, -10.5, 0),
                        C(-4.5, -1, -4.5, 9, 2, 9, 'crown_gold'),
                        C(-4.5, -4, -4.5, 1, 3, 1, 'crown_gold'),
                        C(-0.5, -5, -4.5, 1, 4, 1, 'crown_gold'),
                        C(3.5, -4, -4.5, 1, 3, 1, 'crown_gold'),
                        C(-4.5, -4, 3.5, 1, 3, 1, 'crown_gold'),
                        C(3.5, -4, 3.5, 1, 3, 1, 'crown_gold'),
                        C(-4.5, -3, -0.5, 1, 2, 1, 'crown_gold'),
                        C(3.5, -3, -0.5, 1, 2, 1, 'crown_gold'),
                        C(-0.5, -3, 3.5, 1, 2, 1, 'crown_gold'),
                        C(-1, -1.5, -5, 2, 2, 1, 'crown_gem'))]),
              arm(8), arm(-8),
              P('cape', (0, -14, 3.5), C(-6, 0, 0, 12, 26, 0, 'hollow_cape'), rot=(0.15, 0, 0)),
          ]),
    ])


def crown_blade():
    """One of Morvane's Crown of Blades: a spectral sword. Rendered without the living-entity flip, so +y
    is up here and the pivot sits at the blade's middle."""
    return Model('crown_blade', 64, [
        P('blade', (0, 0, 0),
          C(-1, -6, -0.5, 2, 14, 1, 'spectral_blade'),
          C(-0.5, 8, -0.5, 1, 2, 1, 'spectral_blade'),
          C(-3, -7, -1, 6, 1, 2, 'crown_gold'),
          C(-0.5, -11, -0.5, 1, 4, 1, 'leather_grip'),
          C(-1, -12, -1, 2, 1, 2, 'crown_gold')),
    ], hull=(0.0, 0.0, 0.0))


MODELS = [lanternmoth, gloamling, forsworn_knight, barrow_wight, animated_tome, veilhound, spectral_housecarl,
          sir_caldris, archmage_veyl, hrodgar, morvane, crown_blade]

# representative poses for the previews (part -> added rotation)
PREVIEW_POSES = {
    'lanternmoth': {'left_wing': (0, 0, -0.5), 'right_wing': (0, 0, 0.5)},
    'animated_tome': {'cover_left': (0, 0, -1.0), 'cover_right': (0, 0, 1.0)},
    'sir_caldris': {'left_arm': (-1.35, 0.5, 0), 'right_arm': (-0.3, 0, 0)},
    'barrow_wight': {'left_arm': (-1.2, 0, -0.2), 'right_arm': (-1.2, 0, 0.2), 'tail1': (0.3, 0, 0), 'tail2': (0.3, 0, 0)},
    'spectral_housecarl': {'left_arm': (-0.9, 0.4, 0)},
    'gloamling': {'body': (0.35, 0, 0), 'left_arm': (0, 0, -0.25), 'right_arm': (0, 0, 0.25), 'tail': (0.5, 0, 0)},
    'archmage_veyl': {'right_arm': (-0.5, 0, 0)},
    'morvane': {'right_arm': (-0.5, 0, 0)},
    'forsworn_knight': {'right_arm': (-0.35, 0, 0)},
}


def generate(preview_dir=None):
    models = [m() for m in MODELS]
    methods = []
    paths = []
    for i, m in enumerate(models):
        m.pack()
        tex, glow = m.paint(seed=101 + i * 17)
        tex.save(os.path.join(TEX_DIR, m.name + '.png'))
        glow.save(os.path.join(TEX_DIR, m.name + '_glow.png'))
        methods.append(m.java(m.name))
        for part, path in m.paths():
            paths.append((m.name, part, path))
        if preview_dir:
            os.makedirs(preview_dir, exist_ok=True)
            pose = PREVIEW_POSES.get(m.name)
            a = render(m, tex, glow, yaw=-35, pitch=15, scale=8, pose=pose, bg=(40, 44, 52, 255))
            b = render(m, tex, glow, yaw=145, pitch=15, scale=8, pose=pose, bg=(40, 44, 52, 255))
            h = max(a.shape[0], b.shape[0])
            canvas = np.zeros((h, a.shape[1] + b.shape[1], 4))
            canvas[:, :] = np.array([40, 44, 52, 255]) / 255.0
            canvas[:a.shape[0], :a.shape[1]] = a
            canvas[:b.shape[0], a.shape[1]:] = b
            save_rgba(canvas, os.path.join(preview_dir, m.name + '.png'))
        print(f'{m.name}: {m.width}x{m.height}, {sum(1 for _ in m.cubes())} cubes')
    write_java(models, methods, paths)


def write_java(models, methods, paths):
    lines = ['package com.oathbound.client.model;', '',
             'import com.oathbound.client.render.Renderers;',
             'import net.minecraft.client.model.geom.ModelLayerLocation;',
             'import net.minecraft.client.model.geom.PartPose;',
             'import net.minecraft.client.model.geom.builders.*;', '',
             'import java.util.HashMap;', 'import java.util.Map;',
             'import java.util.function.BiConsumer;', 'import java.util.function.Supplier;', '',
             '/** GENERATED by tools/oath/creatures.py: geometry for every Oathbound creature. Do not edit by hand. */',
             'public final class ModelDefs {',
             '    private ModelDefs() {}', '',
             '    private static final Map<String, String[]> PATHS = new HashMap<>();', '',
             '    /** Registers every layer with the given sink (the layer-definition event). */',
             '    public static void register(BiConsumer<ModelLayerLocation, Supplier<LayerDefinition>> sink) {']
    for m in models:
        lines.append(f'        sink.accept(Renderers.layer("{m.name}"), ModelDefs::{m.name});')
    lines += ['    }', '',
              '    /** The chain of child names from the model root to {@code part}, or null if there is none. */',
              '    public static String[] path(String model, String part) {',
              '        return PATHS.get(model + "/" + part);', '    }', '',
              '    private static void p(String key, String... path) {', '        PATHS.put(key, path);', '    }', '',
              '    static {']
    for model, part, path in paths:
        joined = ', '.join(f'"{s}"' for s in path)
        lines.append(f'        p("{model}/{part}", {joined});')
    lines += ['    }', '']
    for meth in methods:
        lines.append(meth)
        lines.append('')
    lines[-1] = '}'
    with open(JAVA, 'w') as f:
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    generate(sys.argv[1] if len(sys.argv) > 1 else None)
