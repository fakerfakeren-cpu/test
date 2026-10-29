"""Compact the industry and military blocks: linked focuses are merged into one that grants all of their rewards.
Nothing is cut; a merged focus takes about as long as one of its parts, so progression is roughly twice as fast."""
import re

# keep_id (position, icon and AI come from it), absorbed ids, new name. Descriptions are joined.
MERGES = [
    # ---- industry: trade
    ("bfx_eco_tobacco_boom", ["bfx_eco_valley_of_roses"], "Tobacco and Roses"),
    ("bfx_eco_hard_currency", ["bfx_eco_ledger_of_trade"], "Hard Currency and the Ledger of Trade"),
    ("bfx_eco_plovdiv_fair", ["bfx_eco_export_drive"], "The Plovdiv Fair and the Export Drive"),
    ("bfx_eco_national_bank", ["bfx_eco_academy_of_sciences"], "The National Bank and the Academy"),
    # ---- industry: coal, steel and arms
    ("bfx_eco_balkan_iron", ["bfx_eco_kremikovtsi_steel"], "Balkan Iron and Kremikovtsi Steel"),
    ("bfx_eco_kazanlak_arsenal", ["bfx_eco_sopot_works"], "The Kazanlak and Sopot Arsenals"),
    ("bfx_eco_state_arsenals", ["bfx_eco_war_economy"], "The State Arsenals and the War Economy"),
    ("bfx_eco_industrial_ring", ["bfx_eco_dispersed_industry"], "The Industrial Ring and Dispersed Workshops"),
    # ---- industry: power and fuel
    ("bfx_eco_electrification", ["bfx_eco_iskar_dams"], "Electrify the Plain and Dam the Iskar"),
    ("bfx_eco_hydro_grid", ["bfx_eco_chemical_combine"], "The National Grid and the Chemical Combine"),
    ("bfx_eco_tyulenovo_oil", ["bfx_eco_synthetic_fuel", "bfx_eco_fuel_reserves"], "Fuel for the Army"),
    # ---- industry: transport
    ("bfx_eco_bdz", ["bfx_eco_main_line"], "Modernise the BDŽ"),
    ("bfx_eco_danube_ports", ["bfx_eco_black_sea_ports"], "The Danube and Black Sea Ports"),
    ("bfx_eco_labour_brigades", ["bfx_eco_road_network"], "Labour Brigades and the Trans-Balkan Roads"),
    # ---- industry: science and the bomb
    ("bfx_eco_sofia_university", ["bfx_eco_nadjakov_laboratory"], "Sofia University and Nadjakov's Laboratory"),
    ("bfx_eco_bukhovo_uranium", ["bfx_eco_atomic_commission"], "Bukhovo Uranium and the Atomic Commission"),
    ("bfx_eco_reactor_project", ["bfx_eco_kozloduy_reactor"], "The Kozloduy Reactor"),
    # ---- army doctrine
    ("bfx_mil_rhodope_rangers", ["bfx_mil_mountain_doctrine", "bfx_mil_mountain_brigades"], "The Mountain Army"),
    ("bfx_mil_chataldzha_lessons", ["bfx_mil_staff_academy", "bfx_mil_bayonet_tradition"], "Lessons of Chataldzha"),
    ("bfx_mil_balkan_war_plan", ["bfx_mil_officer_corps", "bfx_mil_royal_guard"], "The Balkan War Plan"),
    ("bfx_mil_combined_arms", ["bfx_mil_armoured_brigade"], "Combined Arms and the Armoured Brigade"),
    # ---- equipment
    ("bfx_mil_small_arms", ["bfx_mil_machine_guns", "bfx_mil_anti_tank"], "Infantry Weapons Programme"),
    ("bfx_mil_mountain_guns", ["bfx_mil_rifle_contracts"], "Mountain Guns and Mauser Rifles"),
    ("bfx_mil_field_artillery", ["bfx_mil_support_companies", "bfx_mil_supply_columns"], "Artillery, Support and Supply"),
    # ---- manpower
    ("bfx_mil_reservists", ["bfx_mil_macedonian_emigration", "bfx_mil_pomak_battalions"], "Reservists and Volunteers"),
    ("bfx_mil_veterans_1912", ["bfx_mil_womens_auxiliary"], "Veterans and the Women's Auxiliary"),
    ("bfx_mil_universal_service", ["bfx_mil_mobilisation_law"], "Universal Service and the Mobilisation Law"),
    ("bfx_mil_training_camps", ["bfx_mil_national_army"], "The National Army"),
    # ---- navy
    ("bfx_nav_black_sea_flotilla", ["bfx_nav_varna_naval_school"], "The Black Sea Flotilla"),
    ("bfx_nav_danube_flotilla", ["bfx_nav_minelayers"], "The Danube Flotilla and the Minefields"),
    ("bfx_nav_torpedo_squadrons", ["bfx_nav_coastal_batteries"], "Torpedo Boats and Coastal Batteries"),
    ("bfx_nav_naval_aviation", ["bfx_nav_black_sea_raiders"], "Black Sea Raiders"),
    ("bfx_nav_submarine_flotilla", ["bfx_nav_destroyer_squadron"], "Submarines and Destroyers"),
    # ---- air
    ("bfx_air_aero_clubs", ["bfx_air_dar_works"], "Aero Clubs and the DAR Works"),
    ("bfx_air_polish_fighters", ["bfx_air_avia_biplanes", "bfx_air_foreign_instructors"], "Fighters from Warsaw and Prague"),
    ("bfx_air_vazdushni_voyski", ["bfx_air_fighter_regiment", "bfx_air_sofia_flak"], "Proclaim the Vazdushni Voyski"),
    ("bfx_air_dornier_bombers", ["bfx_air_wings_over_mountains"], "Bombers and Close Support"),
]


def _merge_available(parts):
    """AND of the parts' conditions; of several 'date > X' only the latest is kept."""
    dates, other = [], []
    for a in parts:
        for line in (a or "").split("\n"):
            line = line.strip()
            if not line:
                continue
            m = re.fullmatch(r"date > (\d+)\.(\d+)\.(\d+)", line)
            if m:
                dates.append((tuple(int(x) for x in m.groups()), line))
            elif line not in other:
                other.append(line)
    if dates:
        other.insert(0, max(dates)[1])
    return "\n".join(other) or None


def compact(focuses):
    by_id = {f["id"]: f for f in focuses}
    remap = {}
    for keep, absorbed, name in MERGES:
        k = by_id[keep]
        members = [k] + [by_id[a] for a in absorbed]
        k["name"] = name
        k["desc"] = " ".join(m["desc"] for m in members)
        k["reward"] = "\n".join(m["reward"] for m in members)
        k["available"] = _merge_available([m["available"] for m in members])
        k["filters"] = list(dict.fromkeys(fl for m in members for fl in m["filters"]))
        k["kind"] = "stat" if all(m["kind"] == "stat" for m in members) else "effect"
        k["prereq"] = [g for m in members for g in m["prereq"]]
        k["excl"] = [e for m in members for e in m["excl"]]
        k["merged"] = len(members)
        for a in absorbed:
            remap[a] = keep
    focuses[:] = [f for f in focuses if f["id"] not in remap]
    ids = {f["id"] for f in focuses}
    for f in focuses:
        groups = []
        for g in f["prereq"]:
            g2 = list(dict.fromkeys(remap.get(p, p) for p in g))
            if f["id"] in g2 or g2 in groups:
                continue  # a member's link to another member of the same merge
            groups.append(g2)
        # drop a group that is implied by another (a prerequisite of a prerequisite)
        f["prereq"] = groups
        f["excl"] = list(dict.fromkeys(remap.get(e, e) for e in f["excl"] if remap.get(e, e) != f["id"]))
        assert all(p in ids for g in f["prereq"] for p in g), f["id"]
    _relayout([f for f in focuses if f["block"] in ("eco", "mil")])


def _relayout(block):
    """Rows by depth (no gaps left by merged focuses); columns kept from the original layout."""
    by_id = {f["id"]: f for f in block}
    depth = {}

    def d(fid):
        if fid not in depth:
            parents = [p for g in by_id[fid]["prereq"] for p in g if p in by_id]
            depth[fid] = 1 + max((d(p) for p in parents), default=-1)
        return depth[fid]
    for f in block:
        f["y"] = d(f["id"])
