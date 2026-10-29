"""The secret Coburg restoration (hidden until unlocked)."""
from focus_core import ded, civ, mil, dock, tech, claim_states, core_if_owned, claims_on_cores_of, \
    cores_on_owned_cores_of, wargoal_on_owner, tt, neuilly, F, swap, court, ai_flag, ai_prefer, INTEGRATION, \
    transfer_if_allied, F_POL, F_STAB, F_WS, F_IND, F_RES, F_MAN, F_ANNEX, F_ARMY, F_NAVY, F_AIR, F_HIST, \
    F_MILCHAR, F_POLCHAR
from focus_opening import CHANCELLERY_RULES  # noqa: F401
from focus_path_helpers import wargoal_states, wargoal_annex  # noqa: F401


# =====================================================================================
# SECRET: the Coburg restoration (19) - hidden until unlocked
# =====================================================================================
B = "secret"
F("bfx_alt_old_fox_stirs", 4, 6, "The Old Fox Returns",
  "SECRET PATH. Ferdinand I, deposed 1918, botanist, entomologist and collector of grudges, comes back from Coburg. Revealed when Tsar Boris dies, or when all three Coburg letters have arrived.",
  "country_event = bfx_secret.10", "GFX_focus_bfx_alt_old_fox_stirs", B,
  available="NOT = { has_completed_focus = bfx_fas_legions_march }",
  allow_branch="has_country_flag = bfx_secret_unlocked", ai=ai_flag("bfx_ai_secret", 30), filters=(F_POL, F_POLCHAR))

F("bfx_alt_burn_the_treaty", 3, 7, "Burn the Treaty on the Steps of Neuilly",
  "Ferdinand signed the defeat of 1913 and abdicated after 1918. He has waited twenty years to set fire to the paperwork.",
  "if = { limit = { NOT = { has_country_flag = bfx_neuilly_ended } } bfx_end_neuilly_torn = yes }\nelse = { army_experience = 20 add_war_support = 0.05 }",
  "GFX_focus_bfx_tear_up_neuilly", B, prereq=["bfx_alt_old_fox_stirs"], cost=5, filters=(F_WS, F_ARMY))

F("bfx_alt_entomologist_tsar", 5, 7, "The Entomologist Tsar",
  "Ferdinand has a butterfly named after him. His Royal Natural History Institute will now also study artillery.",
  "add_ideas = bfx_royal_natural_history_institute", "GFX_goal_generic_scientific_exchange", B, prereq=["bfx_alt_old_fox_stirs"], filters=(F_RES,))

F("bfx_alt_imperial_life_guard", 3, 8, "The Imperial Life Guard",
  "White tunics, astrakhan caps, egret plumes and live ammunition.",
  "army_experience = 25\nadd_equipment_to_stockpile = { type = infantry_equipment amount = 2000 }\nadd_manpower = 10000",
  "GFX_goal_generic_special_forces", B, prereq=["bfx_alt_burn_the_treaty"], filters=(F_ARMY, F_MAN))

F("bfx_alt_coburg_capital", 5, 8, "Coburg Capital",
  "The Saxe-Coburg cousins own half the thrones of Europe and a fair share of its factories.",
  civ(1) + "\n" + mil(1), "GFX_goal_generic_construct_mil_factory", B, prereq=["bfx_alt_entomologist_tsar"], filters=(F_IND,), kind="stat")

F("bfx_alt_third_empire", 2, 9, "Proclaim the Third Bulgarian Empire",
  "After Asparuh's khanate and the Asens' empire, the third one. Rules out the Roman pretension.",
  "add_ideas = bfx_third_empire_zeal\nset_cosmetic_tag = bfx_third_empire\n" + claim_states(77, 106, 184) + "\n" + INTEGRATION,
  "GFX_focus_bfx_third_empire", B, prereq=["bfx_alt_imperial_life_guard"], excl=["bfx_alt_tsargrad"],
  ai=ai_flag("bfx_ai_secret_empire", 20), filters=(F_POL, F_ANNEX))

F("bfx_alt_simeons_borders", 2, 10, "The Borders of Simeon the Great",
  "In 917 Simeon's empire touched three seas. Claims on Yugoslavia and Albania.",
  claims_on_cores_of("YUG", "SER", "MAC", "ALB", "MNT") + "\n" + wargoal_annex("YUG"), "GFX_focus_BUL_bulgarian_administration_of_the_balkans", B,
  prereq=["bfx_alt_third_empire"], filters=(F_ANNEX,))

F("bfx_alt_tsar_of_the_vlachs", 1, 11, "Tsar of Bulgarians and Vlachs",
  "Kaloyan used the title in 1204. War goal on Romania; claims on its core lands.",
  claims_on_cores_of("ROM") + "\n" + wargoal_annex("ROM"), "GFX_goal_generic_territory_or_war", B, prereq=["bfx_alt_simeons_borders"], filters=(F_ANNEX,))

F("bfx_alt_restore_preslav", 3, 11, "Restore Preslav",
  "The golden capital of Simeon rises from its ruins, at least as a cathedral and a parade ground.",
  "add_stability = 0.05\nadd_political_power = 75", "GFX_goal_generic_construction", B, prereq=["bfx_alt_simeons_borders"], filters=(F_STAB,), kind="stat")

F("bfx_alt_coronation_at_tarnovo", 2, 12, "Coronation at Tarnovo",
  "Tsarevets hill, forty church bells, and a short lecture on butterflies.",
  "country_event = bfx_secret.12\nevery_owned_state = { limit = { NOT = { is_core_of = ROOT } } add_compliance = 15 }",
  "GFX_focus_BUL_consolidate_the_third_bulgarian_state", B, prereq=["bfx_alt_tsar_of_the_vlachs", "bfx_alt_restore_preslav"], filters=(F_STAB,))

F("bfx_alt_kaloyans_revenge", 2, 13, "Kaloyan's Revenge",
  "Kaloyan died besieging Thessaloniki in 1207. His heir finishes the siege. War goal on Central Macedonia's owner.",
  claim_states(731) + "\n" + wargoal_states(731, [731, 184]), "GFX_goal_generic_major_war", B, prereq=["bfx_alt_coronation_at_tarnovo"], filters=(F_ANNEX,))

F("bfx_alt_empire_of_the_bulgars", 2, 14, "Empire of the Bulgars",
  "The third empire stands: proclaimed, crowned and, most remarkably, still solvent.",
  "add_ideas = bfx_imperial_mandate\n" + core_if_owned(77, 106, 184) + "\nadd_stability = 0.10", "GFX_focus_bfx_third_empire", B,
  prereq=["bfx_alt_kaloyans_revenge"], filters=(F_STAB, F_ANNEX))

F("bfx_alt_tsargrad", 6, 9, "Tsargrad!",
  "Simeon besieged it, Krum nearly took it, and in 1912 Bulgarian guns could be heard in Pera. Rules out the purely Bulgarian empire.",
  "add_ideas = bfx_byzantine_pretension\n" + claim_states(797, 341) + "\n" + wargoal_states(797, [797, 341], "annex_everything") + "\n" + INTEGRATION,
  "GFX_focus_bfx_alt_tsargrad", B, prereq=["bfx_alt_coburg_capital"], excl=["bfx_alt_third_empire"],
  ai=ai_flag("bfx_ai_secret_byz", 20), filters=(F_ANNEX, F_WS))

F("bfx_alt_basileus", 6, 10, "Basileus of the Romans and Bulgars",
  "Simeon demanded the title in 913. Ferdinand has it printed on the stationery. Claims on all Greek core lands.",
  claims_on_cores_of("GRE") + "\nadd_political_power = 50", "GFX_focus_GRE_reviving_the_double_headed_eagle", B,
  prereq=["bfx_alt_tsargrad"], filters=(F_ANNEX, F_POL))

F("bfx_alt_hagia_sophia", 5, 11, "Mass in Hagia Sophia",
  "The first Orthodox liturgy under the great dome since 1453. Cores on Istanbul and Edirne; the realm becomes the Empire of the Romans and Bulgars.",
  core_if_owned(797, 341) + "\nset_cosmetic_tag = bfx_byzantium\nadd_stability = 0.15\nnews_event = { id = bfx_secret.11 days = 1 }",
  "GFX_focus_bfx_alt_hagia_sophia", B, prereq=["bfx_alt_basileus"], available="owns_state = 797", filters=(F_STAB, F_ANNEX))

F("bfx_alt_restore_the_themes", 7, 11, "Restore the Themes",
  "Thrakesion, Opsikion, Anatolikon: the old military provinces return with Bulgarian governors. Claims on Anatolia.",
  claims_on_cores_of("TUR") + "\n" + wargoal_annex("TUR"), "GFX_focus_GRE_byzantine_themata", B, prereq=["bfx_alt_basileus"], filters=(F_ANNEX,))

F("bfx_alt_varangian_guard", 6, 12, "The New Varangian Guard",
  "Every Basileus needs foreign bodyguards with axes. Ferdinand recruits Germans with machine guns.",
  "army_experience = 40\nadd_manpower = 15000", "GFX_goal_generic_special_forces", B, prereq=["bfx_alt_hagia_sophia", "bfx_alt_restore_the_themes"], filters=(F_ARMY,))

F("bfx_alt_orthodox_crusade", 6, 13, "The Orthodox Crusade",
  "Claims on the Aegean islands and Crete, and a war goal on Greece.",
  claim_states(187, 182) + "\n" + wargoal_annex("GRE"), "GFX_goal_generic_major_war", B, prereq=["bfx_alt_varangian_guard"], filters=(F_ANNEX,))

F("bfx_alt_new_rome", 6, 14, "New Rome",
  "The capital moves to the City. Sofia keeps the ministries; Constantinople keeps the Emperor.",
  "if = { limit = { owns_state = 797 } set_capital = { state = 797 } }\nadd_ideas = bfx_imperial_mandate\nadd_stability = 0.05",
  "GFX_focus_bfx_new_rome", B, prereq=["bfx_alt_orthodox_crusade"], available="owns_state = 797", filters=(F_STAB,))
