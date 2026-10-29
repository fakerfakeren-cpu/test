"""National spirits (country ideas). Pictures: 'bfx_*' are our generated 64x64 icons, others are vanilla base-game."""
from core import add_file, loc

IDEAS = []  # (id, picture, modifiers dict, name, desc, removal_cost, extra)


def I(id, pic, mods, name, desc, removal_cost=-1, extra=""):
    IDEAS.append((id, pic, mods, name, desc, removal_cost, extra))


# ---------------------------------------------------------------- Neuilly
I("bfx_neuilly_shackles", "bfx_neuilly_shackles",
  dict(conscription_factor=-0.30, army_org_factor=-0.10, training_time_army_factor=0.25, air_accidents_factor=0.50,
       production_speed_dockyard_factor=-0.25),
  "Shackles of Neuilly",
  "The 1919 Treaty of Neuilly limits Bulgaria to 20,000 volunteers, bans conscription, military aviation and a real navy. Covert Rearmament offsets these penalties, but it rusts away every month and makes the neighbours more suspicious the higher it climbs.")
I("bfx_balkan_embargo", "bfx_balkan_embargo", dict(local_resources_factor=-0.15, consumer_goods_factor=0.04, stability_factor=-0.05),
  "Balkan Embargo", "The Balkan Entente has closed its markets to Bulgarian tobacco and its ports to anything that might be a rifle.")
I("bfx_border_crisis", "bfx_border_crisis", dict(war_support_factor=0.10, stability_factor=-0.10, army_attack_factor=0.05),
  "The Petrich Crisis", "Troops face each other across the border, the newspapers count bayonets and nobody sleeps in Sofia.")
I("bfx_salonika_freedom", "bfx_salonika_freedom", dict(training_time_army_factor=-0.10, experience_gain_army_factor=0.10, stability_factor=0.03),
  "Free of Neuilly", "The military clauses are gone. The army can recruit, train and parade openly, and is enjoying all three.")

# ---------------------------------------------------------------- IMRO
I("bfx_imro_state_within_state", "bul_imro", dict(stability_factor=-0.05, political_power_factor=-0.05),
  "IMRO: A State Within the State",
  "In the Petrich district the Internal Macedonian Revolutionary Organisation collects taxes, holds courts and assassinates rivals in broad daylight in Sofia.")
I("bfx_imro_crushed", "bul_imro", dict(stability_factor=0.03, political_power_factor=0.05),
  "IMRO Broken", "The committees are closed and the gunmen are in exile or in prison. Petrich pays its taxes to Sofia for the first time in fifteen years.")
I("bfx_imro_tolerated", "bul_imro", dict(war_support_factor=0.05, stability_factor=-0.03, justify_war_goal_time=-0.10),
  "IMRO Tolerated", "The government does not see the men drilling in the Pirin forests, and the men return the courtesy.")
I("bfx_imro_liberation_army", "bul_imro", dict(war_support_factor=0.08, justify_war_goal_time=-0.15, army_attack_factor=0.03),
  "The Macedonian Volunteer Corps", "IMRO's chetas have become volunteer battalions with Bulgarian rifles, Bulgarian officers and a very clear idea of where they are going.")

I("bfx_imro_fervour", "bul_imro", dict(army_defence_factor=0.15, army_attack_factor=0.10, army_org_factor=0.10, conscription_factor=0.20),
  "Ilinden Fervour", "Every village in the mountains is a depot, every shepherd a scout. The uprising fights for its life and knows it.")
I("bfx_imro_bulgarian_officers", "bul_imro", dict(army_org_factor=0.10, planning_speed=0.20, army_attack_factor=0.05),
  "Officers on Leave", "Bulgarian staff officers with false names and very real maps run the uprising's war.")

# ---------------------------------------------------------------- regime
I("bfx_military_league_intrigue", "MEX_politicised_army", dict(stability_factor=-0.05, experience_gain_army_factor=0.05),
  "The Military League", "The officers who made the coups of 1923 and 1934 still meet, still talk and still keep the keys to the barracks.")
I("bfx_army_loyal_to_crown", "bul_tsar_boris_positive", dict(stability_factor=0.03, army_org_factor=0.03),
  "An Army Loyal to the Crown", "The League is muzzled and the officers swear their oaths to the Tsar, not to their own committees.")
I("bfx_partyless_regime", "bul_tsar_boris_negative", dict(political_power_gain=0.10, democratic_drift=-0.02, communism_drift=-0.02, stability_factor=-0.03),
  "A Kingdom Without Parties", "Supra-party government: no parties, many factions, and ministers who answer only to the Palace.")
I("bfx_tsars_personal_regime", "bul_tsar_boris_positive", dict(political_power_gain=0.15, stability_factor=0.05, drift_defence_factor=0.15),
  "The Tsar's Personal Regime", "Boris III governs through loyal technicians and a calendar full of audiences. Nobody doubts who decides.")
I("bfx_royal_propaganda", "bfx_royal_propaganda", dict(war_support_factor=0.05, stability_factor=0.03, drift_defence_factor=0.10),
  "The Directorate of National Propaganda", "Newsreels of the Tsar inspecting regiments, posters of the lost provinces, and a radio that never stops talking about either.")
I("bfx_open_chancelleries", "bfx_open_chancelleries", dict(opinion_gain_monthly_factor=0.20, improve_relations_maintain_cost_factor=-0.25),
  "Open Chancelleries", "Sofia's diplomats are busy again: pacts, guarantees and alliances are back on the menu.")
I("bfx_tsar_unifier", "bfx_tsar_unifier", dict(political_power_gain=0.15, war_support_factor=0.10, justify_war_goal_time=-0.20, stability_factor=0.05),
  "Tsar Unifier", "The lost provinces are home. Boris is cheered in Skopje and Kavala as he was never cheered in Sofia.")
I("bfx_san_stefano_irredentism", "bul_bulgarian_irredentism", dict(war_support_factor=0.10, justify_war_goal_time=-0.15),
  "The San Stefano Dream", "Every classroom map shows the Bulgaria of March 1878, and every classroom wants it back.")
I("bfx_raindrops_diplomacy", "bfx_raindrops", dict(stability_factor=0.05, opinion_gain_monthly_factor=0.15, enemy_justify_war_goal_time=0.25),
  "Walking Between the Raindrops", "Boris's own phrase: lean towards Berlin without falling over, take what is offered, promise nothing that cannot be broken.")
I("bfx_axis_junior_partner", "GER_german_trade", dict(army_org_factor=0.03, war_support_factor=0.05, production_speed_buildings_factor=0.05),
  "Junior Axis Partner", "German credits, German instructors and German expectations. So far the first two outweigh the third.")
I("bfx_occupation_corps", "bfx_occupation_corps", dict(compliance_growth=0.10, resistance_growth=-0.10),
  "The Occupation Corps", "Gendarmes, schoolteachers and priests follow the army into the new provinces. Some of them are welcome.")
I("bfx_no_eastern_front", "bul_tsar_boris_positive", dict(stability_factor=0.08, war_support_factor=-0.03, army_core_defence_factor=0.05),
  "Not One Soldier for the Steppe", "Bulgarians and Russians have not fought each other in living memory, and the Tsar intends to keep it that way.")
I("bfx_eastern_crusade", "bfx_crusade_east", dict(war_support_factor=0.08, experience_gain_army_factor=0.10, stability_factor=-0.05),
  "Crusade in the East", "Bulgarian divisions march north of the Danube for the first time since Simeon. Nobody at home is quite sure why.")
I("bfx_balkan_hegemon", "bfx_balkan_hegemon", dict(justify_war_goal_time=-0.20, war_support_factor=0.10, army_core_attack_factor=0.05),
  "The Balkan Hegemon", "Bulgaria needs no patron in Berlin or London. It will be the patron.")
I("bfx_hegemon_army", "bul_prussia_of_the_balkans", dict(army_org_factor=0.05, army_morale_factor=0.05, planning_speed=0.10),
  "The Hegemon's Army", "A small country organised around a large army and a staff that has planned every war it might fight.")
I("bfx_client_kings", "bfx_balkan_hegemon", dict(puppet_cost_factor=-0.30, annex_cost_factor=-0.15, compliance_growth=0.05),
  "Client Kings", "Defeated neighbours keep their crowns, their flags and their ministers, and take their orders from Sofia.")
I("bfx_imperial_mandate", "bfx_tsar_unifier", dict(stability_factor=0.10, political_power_gain=0.10, compliance_growth=0.10, war_support_factor=0.05),
  "The Imperial Mandate", "From the Danube to the Aegean, Sofia's writ runs. Governors are appointed, schools opened and taxes collected, mostly without shooting.")

# ---------------------------------------------------------------- fascist
I("bfx_legionary_state", "bfx_legionary_state", dict(war_support_factor=0.10, political_power_gain=0.10, stability_factor=-0.05, fascism_drift=0.05),
  "The Legionary State", "General Lukov's Legions run the ministries, the schools and the streets. The Tsar still signs the decrees, when he is shown them.")
I("bfx_brannik", "bfx_brannik", dict(conscription_factor=0.05, war_support_factor=0.03, training_time_army_factor=-0.05),
  "The Brannik", "Every boy in Bulgaria wears the green shirt on Sundays and learns to shoot on Saturdays.")
I("bfx_legionary_militia", "bfx_legionary_state", dict(conscription_factor=0.05, army_core_defence_factor=0.05),
  "The Legionary Militia", "Party battalions trained to guard bridges, hunt partisans and march very loudly.")
I("bfx_anti_comintern", "bfx_crusade_east", dict(war_support_factor=0.05, communism_drift=-0.03, drift_defence_factor=0.10),
  "Anti-Comintern Bulwark", "The red menace is officially the second most important thing in Bulgaria, after Macedonia.")
I("bfx_german_instructors", "GER_german_trade", dict(army_org_factor=0.05, training_time_army_factor=-0.10),
  "German Instructors", "Wehrmacht officers teach the Bulgarian army how to fight, and occasionally how to march in step with them.")
I("bfx_total_mobilisation", "bfx_brannik", dict(conscription_factor=0.10, industrial_capacity_factory=0.05, consumer_goods_factor=0.05, stability_factor=-0.05),
  "Total Mobilisation", "Every factory works for the front and every family has someone in it.")
I("bfx_national_social_economy", "bfx_iron_fist", dict(production_factory_max_efficiency_factor=0.05, consumer_goods_factor=-0.03, stability_factor=0.03),
  "The National Social Economy", "Tsankov's corporations: one per trade, one chairman per corporation, one ministry over all of them.")
I("bfx_imperium_army", "bfx_iron_fist", dict(army_attack_factor=0.05, army_morale_factor=0.05, justify_war_goal_time=-0.15),
  "The Army of the Imperium", "Marching songs about Simeon, Samuil and Ivan Asen, and a very modern interest in artillery.")
I("bfx_pact_of_iron", "bfx_iron_fist", dict(opinion_gain_monthly_factor=0.15, war_support_factor=0.05),
  "The Pact of Iron", "Revisionists of Europe, unite: Sofia and Budapest have lost the most and want the most back.")

# ---------------------------------------------------------------- the secret path
I("bfx_ferdinand_restoration", "bfx_ferdinand_restoration", dict(political_power_gain=0.20, war_support_factor=0.15, stability_factor=-0.10),
  "The Coburg Restoration", "Ferdinand is back from exile, older, richer in grudges and absolutely certain that this time he will not lose.")
I("bfx_third_empire_zeal", "bul_third_bulgarian_state", dict(political_power_gain=0.15, war_support_factor=0.15, justify_war_goal_time=-0.25, army_morale_factor=0.05, stability_factor=-0.05),
  "The Third Empire", "Asparuh, Simeon, the Asens, Ferdinand: the fourth name is in a smaller font, but it is on the list.")
I("bfx_byzantine_pretension", "bfx_byzantine_pretension", dict(war_support_factor=0.10, justify_war_goal_time=-0.20, annex_cost_factor=-0.15, stability_factor=0.05),
  "Basileus of the Romans and Bulgars", "The double-headed eagle has a new perch. Ferdinand signs his letters as Emperor of the Romans, and has the stationery to prove it.")
I("bfx_royal_natural_history_institute", "bfx_natural_history", dict(research_speed_factor=0.04),
  "Royal Natural History Institute", "Butterflies, beetles, botany and, on the second floor, ballistics. The Tsar visits both floors.")

# ---------------------------------------------------------------- economy
I("bfx_tobacco_monoculture", "bul_tobacco_exports", dict(political_power_gain=0.05, stability_factor=-0.02, research_speed_factor=-0.03),
  "Tobacco Monoculture", "Oriental tobacco earns most of Bulgaria's foreign currency. When the harvest is good the country is rich; when it is not, the country is restless.")
I("bfx_tobacco_and_rose_exports", "bfx_tobacco_and_rose", dict(political_power_gain=0.10, consumer_goods_factor=-0.02, stability_factor=0.02),
  "Tobacco and Rose Exports", "Two luxury crops, sold to the world. The warehouses of Plovdiv and the stills of Kazanlak work around the clock.")
I("bfx_valley_of_roses", "bfx_tobacco_and_rose", dict(political_power_gain=0.15, consumer_goods_factor=-0.04, stability_factor=0.05),
  "The Valley of Roses", "Attar of roses for Paris, tobacco for Dresden and Bristol: the export economy is diversified, profitable and fragrant.")
I("bfx_german_clearing", "GER_german_trade", dict(industrial_capacity_factory=0.05, production_speed_buildings_factor=0.10, fascism_drift=0.03),
  "The German Clearing Account", "Germany buys everything and pays into an account that can only be spent in Germany. Machines arrive quickly; so does dependence.")
I("bfx_german_clearing_deep", "GER_german_trade", dict(industrial_capacity_factory=0.08, production_speed_buildings_factor=0.10, research_speed_factor=0.03, fascism_drift=0.05, stability_factor=-0.03),
  "Bound to Berlin", "Bulgaria's economy now runs on German credit, German machines and German patience.")
I("bfx_diversified_trade", "BEL_engine_of_the_economy", dict(research_speed_factor=0.03, stability_factor=0.05),
  "Many Buyers", "Tobacco to Britain, roses to France, grain to Czechoslovakia. Smaller orders, but nobody owns the till.")
I("bfx_open_markets", "BEL_engine_of_the_economy", dict(research_speed_factor=0.04, stability_factor=0.05, production_speed_buildings_factor=0.05, trade_opinion_factor=0.20),
  "Open Markets", "The lev is convertible, the Plovdiv Fair is full and Bulgarian goods sail from Varna to everyone who pays.")
I("bfx_pernik_coal_works", "bfx_pernik_coal", dict(production_speed_buildings_factor=0.05, local_resources_factor=0.05),
  "Pernik Coal Works", "Mechanised galleries and a railway spur: the mines of Pernik power the capital.")
I("bfx_pernik_coal_works_2", "bfx_pernik_coal", dict(production_speed_buildings_factor=0.08, local_resources_factor=0.10),
  "Coal and Iron of the Balkan Range", "Pernik coal meets Kremikovtsi ore. A Bulgarian steel industry, small but real.")
I("bfx_electrification", "bfx_iskar_hydro", dict(production_factory_efficiency_gain_factor=0.05),
  "Electrification", "Power lines march across the Thracian plain. Factories that ran on daylight now run on shifts.")
I("bfx_iskar_hydro", "bfx_iskar_hydro", dict(production_factory_efficiency_gain_factor=0.10, production_factory_max_efficiency_factor=0.03),
  "Iskar Hydroelectric Grid", "Turbines in the gorge, lights in the factories and the first electric railway over the Balkan range.")
I("bfx_railway_age", "bul_national_industry", dict(production_speed_infrastructure_factor=0.25),
  "The Railway Age", "New sleepers, new signals and a Tsar who drives the express himself.")
I("bfx_railway_age_2", "bul_national_industry", dict(production_speed_infrastructure_factor=0.25, supply_consumption_factor=-0.05),
  "The Main Lines", "Double track from Sofia to Varna. Troops, tobacco and timetables all move faster.")
I("bfx_state_arsenals", "bul_darzhavna_voenna_fabrika", dict(production_speed_arms_factory_factor=0.10, production_factory_start_efficiency_factor=0.05),
  "The State Arsenals", "Kazanlak makes shells, Sopot makes rifles, and both make them faster than the treaty ever allowed.")
I("bfx_war_economy", "bul_national_industry", dict(industrial_capacity_factory=0.05, consumer_goods_factor=0.02),
  "The War Economy", "Production quotas, ration cards and a War Production Board run by men who used to sell tobacco.")
I("bfx_dispersed_industry", "bul_national_industry", dict(industry_repair_factor=0.20, production_speed_buildings_factor=0.05),
  "Dispersed Industry", "Workshops in the valleys, depots in the caves: a bomber would need a map Bulgaria does not publish.")
I("bfx_chemical_industry", "bfx_chemical", dict(local_resources_factor=0.05, production_speed_synthetic_refinery_factor=0.20),
  "The Chemical Combine", "Fertiliser in peacetime, explosives in war, and a smell over Stara Zagora that never quite leaves.")
I("bfx_trudovaks", "bfx_trudovaks", dict(production_speed_buildings_factor=0.08, conscription_factor=0.03),
  "The Labour Service", "Trudova povinnost: every young man owes the state a year with a shovel, and the shovel is only sometimes a shovel.")
I("bfx_atomic_commission", "bfx_atomic", dict(research_speed_factor=0.03),
  "The Atomic Commission", "Professor Nadjakov's laboratory has a budget, a guard at the door and a very short list of visitors.")

# ---------------------------------------------------------------- army & manpower
I("bfx_mountain_army", "bfx_mountain_army", dict(special_forces_cap=0.15, army_defence_factor=0.03),
  "Rhodope Rangers", "Mountain companies trained on the smugglers' paths of the Rhodopes and the Pirin.")
I("bfx_balkan_mountain_doctrine", "bfx_mountain_army", dict(special_forces_cap=0.25, army_defence_factor=0.05, army_attack_factor=0.03, terrain_penalty_reduction=0.10),
  "Balkan Mountain Doctrine", "Hold the passes, move along the ridges, let the enemy fight the mountains first.")
I("bfx_bayonet_tradition", "bfx_bayonet", dict(army_attack_factor=0.04, army_morale_factor=0.05),
  "The Bayonet Tradition", "Lozengrad, Bulair, Doiran: the Bulgarian infantry's reputation was made at bayonet point, and it knows it.")
I("bfx_general_staff_academy", "bfx_bayonet", dict(planning_speed=0.10, max_planning=0.05),
  "The General Staff Academy", "Staff officers who can plan a campaign, not just a parade.")
I("bfx_reservist_associations", "bfx_reservists", dict(conscription_factor=0.03, land_reinforce_rate=0.03),
  "The Reservist Associations", "Veterans' clubs in every town keep rifles oiled, records current and young men interested.")
I("bfx_veterans_of_1912", "bfx_reservists", dict(army_org_factor=0.03, training_time_army_factor=-0.05),
  "Veterans of the Balkan Wars", "The sergeants of Lozengrad train their grandsons.")
I("bfx_womens_auxiliary", "bfx_reservists", dict(conscription_factor=0.02, production_speed_buildings_factor=0.03),
  "The Women's Auxiliary", "Nurses, signallers, munitions workers: the army counts on women it officially does not recruit.")
I("bfx_national_army", "bfx_reservists", dict(conscription_factor=0.05, land_reinforce_rate=0.05, army_org_factor=0.03),
  "The National Army", "Universal service, regional depots, standing reserves: the army Neuilly forbade, built in full.")
I("bfx_open_conscription", "bfx_salonika_freedom", dict(conscription_factor=0.10, training_time_army_factor=-0.05),
  "Universal Service", "Every Bulgarian man serves, and nobody has to pretend otherwise.")

# ---------------------------------------------------------------- navy & air
I("bfx_black_sea_flotilla", "bfx_black_sea_fleet", dict(experience_gain_navy_factor=0.15, navy_org_factor=0.05),
  "The Black Sea Flotilla", "A handful of torpedo boats and an officer corps with ambitions far larger than its ships.")
I("bfx_black_sea_fleet", "bfx_black_sea_fleet", dict(experience_gain_navy_factor=0.15, navy_org_factor=0.10, production_speed_dockyard_factor=0.10, naval_coordination=0.05),
  "The Black Sea Squadrons", "Fast torpedo craft, trained crews and enough slipways to keep building them.")
I("bfx_black_sea_raiders", "bfx_black_sea_fleet", dict(convoy_raiding_efficiency_factor=0.15, naval_strike_attack_factor=0.10),
  "Black Sea Raiders", "Small boats, long nights and big torpedoes.")
I("bfx_minefields", "bfx_black_sea_fleet", dict(naval_mine_hit_chance=0.10, naval_mines_damage_factor=0.15),
  "The Varna Minefields", "If Bulgaria cannot sink a battleship with guns, it can certainly do it with a mine.")
I("bfx_clandestine_aviation", "bul_dar", dict(experience_gain_air_factor=0.10, air_training_xp_gain_factor=0.10),
  "Clandestine Aviation", "Flying clubs, glider schools and a postal service whose pilots fly in suspiciously tight formation.")
I("bfx_vazdushni_voyski", "bul_dar", dict(experience_gain_air_factor=0.10, air_superiority_efficiency=0.05, production_speed_air_base_factor=0.25, air_accidents_factor=-0.20),
  "His Majesty's Air Force", "The Vazdushni Voyski fly openly at last, with roundels, ranks and a budget.")
I("bfx_foreign_air_instructors", "FIN_finnish_airforce", dict(air_training_xp_gain_factor=0.15, air_ace_generation_chance_factor=0.20),
  "Foreign Flight Instructors", "Every nationality has its own way of flying; Bulgarian pilots have learned most of them.")
I("bfx_sofia_air_defence", "FIN_finnish_airforce", dict(air_superiority_efficiency=0.05),
  "Sofia Fighter Command", "Fighters on alert from Bozhurishte and Vrazhdebna, protecting the capital's skies.")
I("bfx_wings_over_the_mountains", "FIN_finnish_airforce", dict(air_mission_efficiency=0.05, air_training_xp_gain_factor=0.10),
  "Wings over the Mountains", "Pilots trained to find a battalion in a valley and drop exactly enough on it.")


# ---------------------------------------------------------------- v3 path spirits
I("bfx_fortress_bulgaria", "bfx_fortress", dict(army_core_defence_factor=0.10, dig_in_speed_factor=0.25, max_dig_in=2),
  "Fortress Bulgaria", "Concrete in every pass, a depot behind every ridge and a reservist who knows his trench. Whoever comes pays at the border.")
I("bfx_shock_divisions", "bfx_storm", dict(army_attack_factor=0.05, breakthrough_factor=0.05),
  "Legionary Shock Divisions", "Picked volunteers with the best rifles and the newest guns, used where the line must break.")
I("bfx_storm_offensive", "bfx_storm", dict(army_attack_factor=0.15, breakthrough_factor=0.10, army_speed_factor=0.05),
  "Storm Offensive", "The Legion has spent its momentum on one great push. For two months every company attacks at dawn.")
I("bfx_legionary_prefects", "bfx_occupation_corps", dict(compliance_growth=0.10, resistance_growth=-0.15, stability_factor=-0.02),
  "Legionary Prefects", "A prefect from the movement, a gendarmerie company and a quota of Bulgarian schools in every conquered district.")


def fmt_val(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def generate():
    lines = ["ideas = {", "\tcountry = {"]
    for id, pic, mods, name, desc, removal, extra in IDEAS:
        lines.append(f"\t\t{id} = {{")
        lines.append(f"\t\t\tpicture = {pic}")
        lines.append("\t\t\tallowed = { always = no }")
        lines.append(f"\t\t\tremoval_cost = {removal}")
        lines.append("\t\t\tmodifier = {")
        for k, v in mods.items():
            lines.append(f"\t\t\t\t{k} = {fmt_val(v)}")
        lines.append("\t\t\t}")
        if extra:
            lines.append(extra)
        lines.append("\t\t}")
        loc(id, name, "ideas")
        loc(id + "_desc", desc, "ideas")
    lines += ["\t}", "}", ""]
    add_file("common/ideas/bfx_ideas.txt", "\n".join(lines))
