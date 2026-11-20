"""Default military advisors for every district, like vanilla's generic ones: two theorists (army and air
experience), two high command experts and an air chief. Written by tools/build_focus.py to
common/characters/evil_sofia_military.txt; their traits go into common/country_leader/evil_sofia_traits.txt.
"""
import numpy as np

# key: (name, description, modifiers, slot, cost)
TRAITS = {
    "evil_sofia_army_theorist": ("Army Theorist", "Has read every manual since Napoleon and rewritten half of them.",
                                 "experience_gain_army = 0.1", "theorist", 100),
    "evil_sofia_air_theorist": ("Air Theorist", "Believes the next war will be won over the rooftops.",
                                "experience_gain_air = 0.1", "theorist", 100),
    "evil_sofia_artillery_expert": ("Artillery Expert", "Can drop a shell on any courtyard in Sofia.",
                                    "army_artillery_attack_factor = 0.10", "high_command", 100),
    "evil_sofia_entrenchment_expert": ("Entrenchment Expert", "Every pavement can be a trench by morning.",
                                       "dig_in_speed_factor = 0.25\narmy_defence_factor = 0.02", "high_command", 100),
    "evil_sofia_guard_chief": ("Chief of the District Guard", "Knows every unit, every barracks and every excuse.",
                               "army_org_factor = 0.05\narmy_morale_factor = 0.05", "army_chief", 100),
    "evil_sofia_air_chief": ("Chief of the Air Guard", "Three aeroplanes, five pilots and a plan for both.",
                             "air_attack_factor = 0.05\nair_defence_factor = 0.05", "air_chief", 100),
}
RANKS = {"theorist": "Colonel", "high_command": "General", "air_chief": "Major", "army_chief": "General"}
FIRST = ["Bogomil", "Danail", "Evtim", "Filip", "Gancho", "Hristofor", "Ilia", "Kamen", "Lachezar", "Metodi",
         "Nayden", "Ognyan", "Pancho", "Rangel", "Sotir", "Tihomir", "Valeri", "Yanko", "Zdravko", "Boyan",
         "Velin", "Darin", "Krastyu", "Mladen", "Neno", "Pravdomir", "Rosen", "Tanyo", "Hrabar", "Tsanko"]
SURNAMES = ["Arnaudov", "Boyadzhiev", "Chernev", "Dragnev", "Enchev", "Filipov", "Gospodinov", "Hadzhiev",
            "Ivanchev", "Kalchev", "Lilov", "Manolov", "Nedev", "Ognyanov", "Petkov", "Raykov", "Shishkov",
            "Topalov", "Vazov", "Zlatev", "Bakalov", "Gerdzhikov", "Kardzhiev", "Minchev", "Panov", "Sirakov"]


def advisors(tags):
    """[(character id, display name, tag, trait)] for every country, the same on every build."""
    rng = np.random.default_rng(1885)
    out, taken = [], set()
    for tag in tags:
        for i, trait in enumerate(TRAITS, 1):
            slot = TRAITS[trait][3]
            while True:
                name = f"{RANKS[slot]} {FIRST[rng.integers(len(FIRST))]} {SURNAMES[rng.integers(len(SURNAMES))]}"
                if name not in taken:
                    taken.add(name)
                    break
            out.append((f"{tag}_military_{i}", name, tag, trait))
    return out
