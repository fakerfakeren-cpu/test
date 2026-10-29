"""bfx_ characters, their traits and the opinion modifiers used across the mod."""
from core import add_file, loc

# portrait: our generated file base name (gfx/leaders/BUL/bfx_<p>.dds + _small) or ("vanilla", "GFX_...") for a vanilla small sprite.
# Biographies checked against standard references (see DESIGN.md).
CHARS = [
    ("bfx_BUL_boris_iii", "Boris III", "boris_iii",
     [dict(kind="leader", ideology="despotism", traits=["bfx_trait_engine_driver_tsar"])],
     "Tsar 1918–1943; personal regime from 1935; famous for 'walking between the raindrops'; died Aug 1943 after meeting Hitler."),
    ("bfx_BUL_ferdinand_i", "Ferdinand I", "ferdinand_i",
     [dict(kind="leader", ideology="despotism", traits=["bfx_trait_old_fox"])],
     "Prince 1887, Tsar 1908–1918; abdicated after WWI, lived in Coburg until 1948; noted botanist and entomologist."),
    ("bfx_BUL_hristo_lukov", "Hristo Lukov", "hristo_lukov",
     [dict(kind="leader", ideology="fascism_ideology", traits=["bfx_trait_legion_commander"]),
      dict(kind="corps_commander", skill=3, attack=3, defense=2, planning=3, logistics=2)],
     "General; War Minister 1935–1938; led the Union of Bulgarian National Legions; assassinated in Sofia in February 1943."),
    ("bfx_BUL_bogdan_filov", "Bogdan Filov", "bogdan_filov",
     [dict(kind="advisor", slot="political_advisor", traits=["bfx_adv_archaeologist_premier"]),
      dict(kind="leader", ideology="despotism", traits=["bfx_trait_regent"])],
     "Archaeologist; PM 1940–1943, signed the Tripartite Pact; regent 1943–44 after Boris's death; executed 1945."),
    ("bfx_BUL_georgi_kyoseivanov", "Georgi Kyoseivanov", "georgi_kyoseivanov",
     [dict(kind="advisor", slot="political_advisor", traits=["bfx_adv_salonika_negotiator"])],
     "Diplomat; PM 1935–1940; signed the 1937 pact with Yugoslavia and the 1938 Salonika Agreement."),
    ("bfx_BUL_kimon_georgiev", "Kimon Georgiev", "kimon_georgiev",
     [dict(kind="advisor", slot="political_advisor", traits=["bfx_adv_zveno_technocrat"])],
     "Zveno leader; PM after the 19 May 1934 coup and again 1944–1946."),
    ("bfx_BUL_ivan_mihaylov", "Ivan Mihaylov", "ivan_mihaylov",
     [dict(kind="advisor", slot="political_advisor", traits=["bfx_adv_imro_supremo"])],
     "IMRO leader 1924–1934; fled after the Zveno crackdown; died in Rome in 1990."),
    ("bfx_MAC_ivan_mihaylov_f", "Ivan Mihaylov", "ivan_mihaylov",
     [dict(kind="leader", ideology="fascism_ideology", traits=["bfx_trait_imro_vozhd"])],
     "IMRO leader 1924–1934. In 1944 Germany offered him an independent Macedonia and he refused; here he accepts. Leads the Independent State of Macedonia during the uprising."),
    ("bfx_MAC_ivan_mihaylov_n", "Ivan Mihaylov", "ivan_mihaylov",
     [dict(kind="leader", ideology="despotism", traits=["bfx_trait_imro_vozhd"])],
     "IMRO leader 1924–1934. In 1944 Germany offered him an independent Macedonia and he refused; here he accepts. Leads the Independent State of Macedonia during the uprising. (Used when Yugoslavia itself is fascist, so the rising is non-aligned.)"),
    ("bfx_BUL_aleksandar_tsankov", "Aleksandar Tsankov", ("vanilla", "GFX_idea_bul_aleksandar_tsankov"),
     [dict(kind="advisor", slot="political_advisor", traits=["bfx_adv_national_socialist_ideologue"])],
     "PM 1923–1926; founded the National Social Movement in 1932; headed the pro-German government in exile in 1944–45."),
    ("bfx_BUL_ivan_dochev", "Ivan Dochev", ("vanilla", "GFX_idea_bul_ivan_dochev"),
     [dict(kind="advisor", slot="political_advisor", traits=["bfx_adv_legion_organiser"])],
     "A leading figure of the Union of Bulgarian National Legions; emigrated after 1944."),
    ("bfx_BUL_dobri_bozhilov", "Dobri Bozhilov", ("vanilla", "GFX_idea_bul_dobri_bozhilov"),
     [dict(kind="advisor", slot="political_advisor", traits=["bfx_adv_finance_minister"])],
     "Banker; Finance Minister 1938–1943 and PM 1943–1944."),
    ("bfx_BUL_teodosi_daskalov", "Teodosi Daskalov", ("vanilla", "GFX_idea_bul_theodosi_daskalov"),
     [dict(kind="advisor", slot="high_command", traits=["bfx_adv_war_minister"])],
     "General; succeeded Lukov as War Minister in 1938."),
    ("bfx_BUL_konstantin_lukash", "Konstantin Lukash", ("vanilla", "GFX_idea_bul_konstantin_lukash"),
     [dict(kind="advisor", slot="army_chief", traits=["bfx_adv_chief_of_staff"])],
     "General; Chief of the General Staff 1941–1944; executed by the People's Court in 1945."),
    ("bfx_BUL_stoyan_stoyanov", "Stoyan Stoyanov", ("vanilla", "GFX_idea_bul_stoyan_stoyanov"),
     [dict(kind="advisor", slot="air_chief", traits=["bfx_adv_fighter_ace"])],
     "Bulgaria's leading fighter ace of the Second World War."),
    ("bfx_BUL_nikola_zhekov", "Nikola Zhekov", "nikola_zhekov",
     [dict(kind="field_marshal", skill=4, attack=3, defense=4, planning=4, logistics=3)],
     "Commander-in-chief 1915–1918; War Minister 1918; pro-German; died in exile 1949."),
    ("bfx_BUL_vladimir_zaimov", "Vladimir Zaimov", "vladimir_zaimov",
     [dict(kind="corps_commander", skill=3, attack=2, defense=3, planning=3, logistics=3)],
     "General, Military League member; arrested in 1942 as a Soviet agent and executed."),
]

LEADER_TRAITS = {
    "bfx_trait_imro_vozhd": ("Vozhd of the Organisation", dict(war_support_factor=0.10, army_core_defence_factor=0.10, stability_factor=0.05),
                             "Ivan Mihaylov ran IMRO for ten years from the shadows. Now he runs a state, and the shadows come with him."),
    "bfx_trait_engine_driver_tsar": ("Engine-Driver Tsar", dict(stability_factor=0.05, opinion_gain_monthly_factor=0.15),
                                     "Boris III held a locomotive driver's licence and drove the royal train himself."),
    "bfx_trait_old_fox": ("The Old Fox", dict(political_power_gain=0.15, war_support_factor=0.05, stability_factor=-0.05),
                          "Europe's courts called Ferdinand 'Foxy Ferdinand', and not as a compliment."),
    "bfx_trait_legion_commander": ("Commander of the Legions", dict(war_support_factor=0.08, army_org_factor=0.03),
                                   "A general who leads a party, or a party that has a general. Lukov himself is not sure."),
    "bfx_trait_regent": ("Regent", dict(stability_factor=-0.05, political_power_gain=0.10),
                         "Governing for a six-year-old Tsar, with two co-regents who disagree with him."),
    "bfx_adv_archaeologist_premier": ("Archaeologist Premier", dict(political_power_gain=0.10, fascism_drift=0.03), ""),
    "bfx_adv_salonika_negotiator": ("Salonika Negotiator", dict(opinion_gain_monthly_factor=0.20, improve_relations_maintain_cost_factor=-0.20), ""),
    "bfx_adv_zveno_technocrat": ("Zveno Technocrat", dict(research_speed_factor=0.03, production_speed_buildings_factor=0.05), ""),
    "bfx_adv_imro_supremo": ("IMRO Supremo", dict(war_support_factor=0.05, justify_war_goal_time=-0.15), ""),
    "bfx_adv_national_socialist_ideologue": ("National Social Ideologue", dict(fascism_drift=0.05, political_power_gain=0.10), ""),
    "bfx_adv_legion_organiser": ("Legion Organiser", dict(conscription_factor=0.03, war_support_factor=0.03), ""),
    "bfx_adv_finance_minister": ("Banker Minister", dict(consumer_goods_factor=-0.03, production_speed_buildings_factor=0.05), ""),
    "bfx_adv_war_minister": ("War Minister of 1941", dict(army_org_factor=0.05, experience_gain_army_factor=0.10), ""),
    "bfx_adv_chief_of_staff": ("Chief of the General Staff", dict(planning_speed=0.10, army_attack_factor=0.03), ""),
    "bfx_adv_fighter_ace": ("Ace of Sofia", dict(air_superiority_efficiency=0.05, air_ace_generation_chance_factor=0.25), ""),
}

OPINION_MODS = {
    "bfx_om_eternal_friendship": (25, "Eternal Friendship Pact"),
    "bfx_om_imro_crackdown": (15, "Crushed IMRO"),
    "bfx_om_axis_courtship": (20, "Courting the Axis"),
    "bfx_om_balkan_courtship": (20, "Balkan Courtship"),
    "bfx_om_balkan_protest": (-20, "Rearmament Protest"),
    "bfx_om_neuilly_honoured": (20, "Salonika Agreement"),
    "bfx_om_neuilly_torn": (-30, "Tore Up Neuilly"),
    "bfx_om_rose_trade": (15, "Rose Oil Trade"),
    "bfx_om_royal_wedding": (25, "The Italian Queen"),
    "bfx_om_revisionist_brothers": (30, "Revisionist Brothers"),
    "bfx_om_bulgarian_threat": (-40, "Bulgarian Aggression"),
    "bfx_om_diplomatic_courtesy": (15, "Diplomatic Courtesy"),
}


def fmt(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


def portrait_paths(pic):
    if isinstance(pic, tuple):
        return None, pic[1]
    return f"\"gfx/leaders/BUL/bfx_{pic}.dds\"", f"\"gfx/interface/ideas/bfx_{pic}_small.dds\""


def generate():
    out = ["characters = {"]
    for cid, name, pic, roles, bio in CHARS:
        loc(cid, name, "characters")
        out.append(f"\t{cid} = {{")
        out.append(f"\t\tname = {cid}")
        kinds = {r["kind"] for r in roles}
        large, small = portrait_paths(pic)
        out.append("\t\tportraits = {")
        types = ["civilian"] + (["army"] if kinds & {"field_marshal", "corps_commander"} else [])
        if kinds <= {"field_marshal", "corps_commander"}:
            types = ["army"]
        for ptype in types:
            out.append(f"\t\t\t{ptype} = {{")
            if large:
                out.append(f"\t\t\t\tlarge = {large}")
            out.append(f"\t\t\t\tsmall = {small}")
            out.append("\t\t\t}")
        out.append("\t\t}")
        for r in roles:
            if r["kind"] == "leader":
                out.append("\t\tcountry_leader = {")
                out.append(f"\t\t\tideology = {r['ideology']}")
                out.append(f"\t\t\ttraits = {{ {' '.join(r['traits'])} }}")
                out.append("\t\t\texpire = \"1965.1.1.1\"")
                out.append("\t\t\tid = -1")
                out.append("\t\t}")
            elif r["kind"] == "advisor":
                out.append("\t\tadvisor = {")
                out.append(f"\t\t\tslot = {r['slot']}")
                out.append(f"\t\t\tidea_token = {cid}_advisor")
                out.append("\t\t\tallowed = { original_tag = BUL }")
                out.append(f"\t\t\ttraits = {{ {' '.join(r['traits'])} }}")
                out.append("\t\t\tcost = 150")
                out.append("\t\t\tai_will_do = { factor = 1 }")
                out.append("\t\t}")
                loc(f"{cid}_advisor", name, "characters")
            else:
                out.append(f"\t\t{r['kind']} = {{")
                out.append(f"\t\t\tskill = {r['skill']}")
                out.append(f"\t\t\tattack_skill = {r['attack']}")
                out.append(f"\t\t\tdefense_skill = {r['defense']}")
                out.append(f"\t\t\tplanning_skill = {r['planning']}")
                out.append(f"\t\t\tlogistics_skill = {r['logistics']}")
                out.append("\t\t}")
        out.append("\t}")
    out += ["}", ""]
    add_file("common/characters/bfx_BUL_characters.txt", "\n".join(out))

    tr = ["leader_traits = {"]
    for k, (name, mods, desc) in LEADER_TRAITS.items():
        tr.append(f"\t{k} = {{")
        tr.append("\t\trandom = no")
        for m, v in mods.items():
            tr.append(f"\t\t{m} = {fmt(v)}")
        tr.append("\t\tai_will_do = { factor = 1 }")
        tr.append("\t}")
        loc(k, name, "characters")
        if desc:
            loc(k + "_desc", desc, "characters")
    tr += ["}", ""]
    add_file("common/country_leader/bfx_traits.txt", "\n".join(tr))

    op = ["opinion_modifiers = {"]
    for k, (val, name) in OPINION_MODS.items():
        op.append(f"\t{k} = {{ value = {val} }}")
        loc(k, name, "misc")
    op += ["}", ""]
    add_file("common/opinion_modifiers/bfx_opinion_modifiers.txt", "\n".join(op))


def used_portraits():
    return {pic for _, _, pic, _, _ in CHARS if not isinstance(pic, tuple)}
