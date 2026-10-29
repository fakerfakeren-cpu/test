# DESIGN — Bulgaria: The Tsar's Balance (`bfx_bulgaria` v2)

Target **Hearts of Iron IV 1.19.4** (`supported_version = "1.19.*"`), base game only, Road to 56 compatible.
Generated from `tools/build/*.py` by `tools/write_docs.py`. The mod itself comes from the same data.

## Scope (v2 rework)
The mod is about the Bulgaria that existed: **Tsar Boris III's non-aligned kingdom** and the **Legionary (fascist) movement**
that wanted to replace it, plus one **secret path**. The Communist and Agrarian/democratic paths from v1 were removed.

| Block | Focuses | What it does |
|---|---|---|
| Opening | 20 | 1936 crisis, Velchev trial, partyless regime, IMRO (crush or tolerate), Neuilly (Salonika vs. tear it up), the Italian Queen, **Open the Chancelleries** (factions, guarantees, volunteers and pacts for a non-aligned state) |
| Tsar Boris | 40 | (a) *Walking Between the Raindrops*: Axis opportunist (Turkish pact, Craiova, Tripartite Pact, the Axis Partition, Outlands, Bessarabian Bulgarians, Eastern Front yes/no, Greater Bulgaria, Straits, San Stefano). (b) *The Balkan Hegemon*: own faction (Sofia Pact), Hungarian partner, Soviet pact, Albanian protectorate, four war plans (Yugoslavia, Greece, Romania, Turkey), client kings, Balkan Tsardom |
| The Legions | 38 | Needs Legion influence 40. The March on Sofia (appointment or civil war). (a) *Lukov's Axis Legion*: Into the Axis, Balkan Blitz, New Order, Crusade in the East, Budjak, Odessa corridor, Thrace to the Bosporus. (b) *Tsankov's Imperium*: fascist but independent, Pact of Iron with Hungary, rival to Rome, wars for Macedonia, the Aegean, the Danube and the Straits, the Bulgarian Imperium |
| Secret: the Coburg Restoration | 19 | Hidden (`allow_branch`) until Boris dies (Aug 1943+, random) or three letters from Coburg arrive. Ferdinand returns. (a) Third Bulgarian Empire: Simeon's borders, Tsar of the Vlachs, Tarnovo coronation, Kaloyan's revenge. (b) Tsargrad: Basileus, Hagia Sophia, the Themes, the Varangian Guard, Orthodox crusade, capital moved to Constantinople |
| Industry | 41 | Tobacco and rose exports (3 stages), German clearing vs. diversification with a follow-up event, Pernik coal and Balkan iron, Kremikovtsi, Kazanlak and Sopot arsenals, electrification and the Iskar dams, railways, ports, roads, chemicals, Tyulenovo oil, synthetic fuel, fuel reserves, war economy. **Nuclear line**: Nadjakov's laboratory, Bukhovo uranium, Atomic Commission, reactor, the Kozloduy pile, the Rila device (date-gated 1938–1944) |
| Military | 51 | Army doctrine 12 (mountain warfare, Chataldzha lessons, staff academy, bayonet tradition, armoured brigade), equipment 8, **manpower 9** (reservists, emigration volunteers, Rhodope battalions, veterans, women's auxiliary, universal service, mobilisation law, national army), navy 10, air 11 (PZL and Avia purchases, Dornier bombers, paratroopers) |

Total **209 focuses**; plain stat bumps 16 (7%). Every exclusive choice says what it rules out.
Every focus has `search_filters` and `ai_will_do`.

## Realism and balance rules
* **Cores only on historically Bulgarian lands**: Southern Dobrudja (77), Vardar Macedonia (106), Western Thrace (184), Edirne (341),
  and Central Macedonia (731) once compliance passes 40%. Everything else is **claims and war goals**, which is where the aggression comes from.
* **Integration decisions** core other held land only once its *compliance* is high enough: Bulgarian lands 35%, Greece and Albania 60%,
  Serbia and Romania 65%, Anatolia 70%, the Pontic coast 75%. They cost political power and a little stability, and can be repeated as compliance rises.
* **Diplomacy works**: *Open the Chancelleries* (and the Legionary State) lift the non-aligned limits with `set_rule`. The *Sofia Chancellery*
  decisions propose non-aggression pacts (Turkey, Romania, Greece, Yugoslavia, USSR, Hungary, Italy), ask for guarantees (Germany, Italy, Britain, France),
  invite countries to your faction, give guarantees and demand Southern Dobruja. Several focuses do the same by event (Turkish pact 1941,
  Craiova 1940, the Sobolev mission 1940, the Albanian protectorate, joining the Axis).
* **Land by diplomacy**: Craiova returns Dobruja peacefully (much likelier with German backing). The Axis Partition hands over Macedonia and Thrace
  when allies hold them (as in April 1941). Skopje can ask to join after the uprising.
* Industry gives about one building per focus, two research slots at most in a playthrough, and the nuclear line is date-gated.

## Mechanic 1: Shackles of Neuilly (reworked)
* `bfx_rearm` (0–100) cancels the Neuilly penalties through the *Covert Rearmament* dynamic modifier. It **rusts by 1 a month**
  (0 after *Hidden Arsenals*).
* `bfx_suspicion` (0–100, starts at 15) **grows every month by 1 + rearmament/25**, so heavy rearmament is noticed fast.
* Thresholds 25 (protests), 50 (the Entente guarantees each other), 75 (embargo), 100 (the Petrich crisis) **re-arm** once suspicion
  falls 15 points below them, so penalties recur.
* Ends via the Salonika Agreement (negotiated: XP, good relations) or Tear Up Neuilly / Ferdinand burning the treaty (embargo and crisis).

## Mechanic 2: The Tsar's Balance (new)
Four blocs with influence 0–100, shown with their effects in the decision tab, driving the *Tsar's Balance* dynamic modifier:
* **Crown** → stability (−10%..+10%, minus IMRO violence) and political power (0..+20%). Drifts −1/month unless stability > 60%.
* **Army** → organisation (0..+8%) and army XP gain (0..+20%). Grows at war or with rearmament above 50.
* **Legions** → war support (−5%..+15%) and conscription (0..+10%). Grows with war support and fascist popularity; the Tsar's rule wears it down.
  **40 is required for the Legionary path.**
* **IMRO** → war-goal justification (0..−30%) at a stability cost. Grows while IMRO is tolerated.
* Crises (each re-arms after recovery): Army > 80 *The League Stirs*; Legions > 80 *The Legions March on Sofia*; IMRO > 80 *Murder in Sofia*;
  Crown < 20 *The Crown Totters*; Army < 15 *The Army Sulks*.
* **The death of Tsar Boris** (from August 1943, 25% a month while he rules): a regency under Filov, and the secret path is revealed.
* Nine court decisions: audiences, promotions, purges, patronage or bans for the Legions, subsidies or arrests for IMRO,
  the Metropolitan's blessing, and answering Ferdinand's letters.

## Mechanic 3: The Macedonian Uprising (new)
Tolerating IMRO unlocks raids, newspapers and arms caches that raise **unrest in Vardar Macedonia**. At 70 IMRO can raise the Ilinden banner:
Yugoslavia gets a **civil war** limited to Macedonia (25% of its forces defect). The rebels become the **Independent State of Macedonia**
(own name, flag and map colour, led by Ivan Mihaylov, with the *Ilinden Fervour* spirit). Bulgaria can send volunteers (manpower),
rifles, mountain guns and *Officers on Leave*, recognise and guarantee the state, or intervene openly. If the rising survives
8 months, or Yugoslavia starts to collapse, Belgrade makes peace. Six months later Skopje asks to join: annex it (cores) or keep it as a client.
If it is crushed, Bulgaria pays in stability and IMRO influence.

## Formables and colours
| Cosmetic tag | Name | Map colour |
|---|---|---|
| `bfx_greater_bulgaria` | Greater Bulgaria | rgb(34, 128, 76) |
| `bfx_san_stefano_bulgaria` | San Stefano Bulgaria | rgb(20, 150, 100) |
| `bfx_balkan_tsardom` | Tsardom of the Balkans | rgb(150, 32, 44) |
| `bfx_legionary_bulgaria` | Legionary State of Greater Bulgaria | rgb(70, 96, 40) |
| `bfx_bulgarian_imperium` | Bulgarian Imperium | rgb(96, 34, 30) |
| `bfx_third_empire` | Third Bulgarian Empire | rgb(122, 22, 64) |
| `bfx_byzantium` | Empire of the Romans and Bulgars | rgb(112, 24, 112) |
| `bfx_independent_macedonia` | Independent State of Macedonia | rgb(196, 52, 40) |
| `bfx_bulgarian_empire` | Bulgarian Empire | rgb(60, 110, 60) |

Colours are in `common/countries/bfx_cosmetic.txt`. Every formable has its own generated flag.
*Proclaim the Bulgarian Empire* is open to every path that holds Macedonia, Thrace, Dobrudja and Edirne; its fascist name is the *Legionary Empire of Bulgaria*.

### Not done: new provinces and states
Splitting provinces or states (for example exact San Stefano borders) means editing the map definition, the province bitmap and the vanilla
`history/states` files. That overrides vanilla files and breaks Road to 56 and every other map-touching mod, which this mod's rules forbid.
Border realism therefore works at state level: historical cores, claims elsewhere, compliance-gated integration.

## Events (41) and decisions (63)
Events cover the opening, Neuilly thresholds, the court crises and Boris's death, diplomacy answers (pacts, guarantees, invitations,
Craiova, the Albanian protectorate, Axis entry), the March on Sofia and the attempt on Lukov, the uprising (news, peace, defeat, union),
the Coburg letters, Ferdinand's return, Hagia Sophia and Tarnovo, and five random flavour events.
Decision categories: Shackles of Neuilly, The Tsar's Balance, The Sofia Chancellery, The Macedonian Uprising, Integration, Tsargrad Propaganda.

## AI
On startup an AI Bulgaria rolls Tsar 72% (Raindrops 70% / Hegemon 30%) or Legions 28% (Axis 60% / Imperium 40%), and a 30% chance
to take the secret path if it is revealed. Fascist AIs patronise the Legions until they reach 40. No game rule needed.

## National spirits (77)
| ID | Name | Modifiers |
|---|---|---|
| `bfx_neuilly_shackles` | Shackles of Neuilly | conscription_factor -0.3, army_org_factor -0.1, training_time_army_factor +0.25, air_accidents_factor +0.5, production_speed_dockyard_factor -0.25 |
| `bfx_balkan_embargo` | Balkan Embargo | local_resources_factor -0.15, consumer_goods_factor +0.04, stability_factor -0.05 |
| `bfx_border_crisis` | The Petrich Crisis | war_support_factor +0.1, stability_factor -0.1, army_attack_factor +0.05 |
| `bfx_salonika_freedom` | Free of Neuilly | training_time_army_factor -0.1, experience_gain_army_factor +0.1, stability_factor +0.03 |
| `bfx_imro_state_within_state` | IMRO: A State Within the State | stability_factor -0.05, political_power_factor -0.05 |
| `bfx_imro_crushed` | IMRO Broken | stability_factor +0.03, political_power_factor +0.05 |
| `bfx_imro_tolerated` | IMRO Tolerated | war_support_factor +0.05, stability_factor -0.03, justify_war_goal_time -0.1 |
| `bfx_imro_liberation_army` | The Macedonian Volunteer Corps | war_support_factor +0.08, justify_war_goal_time -0.15, army_attack_factor +0.03 |
| `bfx_imro_fervour` | Ilinden Fervour | army_defence_factor +0.15, army_attack_factor +0.1, army_org_factor +0.1, conscription_factor +0.2 |
| `bfx_imro_bulgarian_officers` | Officers on Leave | army_org_factor +0.1, planning_speed +0.2, army_attack_factor +0.05 |
| `bfx_military_league_intrigue` | The Military League | stability_factor -0.05, experience_gain_army_factor +0.05 |
| `bfx_army_loyal_to_crown` | An Army Loyal to the Crown | stability_factor +0.03, army_org_factor +0.03 |
| `bfx_partyless_regime` | A Kingdom Without Parties | political_power_gain +0.1, democratic_drift -0.02, communism_drift -0.02, stability_factor -0.03 |
| `bfx_tsars_personal_regime` | The Tsar's Personal Regime | political_power_gain +0.15, stability_factor +0.05, drift_defence_factor +0.15 |
| `bfx_royal_propaganda` | The Directorate of National Propaganda | war_support_factor +0.05, stability_factor +0.03, drift_defence_factor +0.1 |
| `bfx_open_chancelleries` | Open Chancelleries | opinion_gain_monthly_factor +0.2, improve_relations_maintain_cost_factor -0.25 |
| `bfx_tsar_unifier` | Tsar Unifier | political_power_gain +0.15, war_support_factor +0.1, justify_war_goal_time -0.2, stability_factor +0.05 |
| `bfx_san_stefano_irredentism` | The San Stefano Dream | war_support_factor +0.1, justify_war_goal_time -0.15 |
| `bfx_raindrops_diplomacy` | Walking Between the Raindrops | stability_factor +0.05, opinion_gain_monthly_factor +0.15, enemy_justify_war_goal_time +0.25 |
| `bfx_axis_junior_partner` | Junior Axis Partner | army_org_factor +0.03, war_support_factor +0.05, production_speed_buildings_factor +0.05 |
| `bfx_occupation_corps` | The Occupation Corps | compliance_growth +0.1, resistance_growth -0.1 |
| `bfx_no_eastern_front` | Not One Soldier for the Steppe | stability_factor +0.08, war_support_factor -0.03, army_core_defence_factor +0.05 |
| `bfx_eastern_crusade` | Crusade in the East | war_support_factor +0.08, experience_gain_army_factor +0.1, stability_factor -0.05 |
| `bfx_balkan_hegemon` | The Balkan Hegemon | justify_war_goal_time -0.2, war_support_factor +0.1, army_core_attack_factor +0.05 |
| `bfx_hegemon_army` | The Hegemon's Army | army_org_factor +0.05, army_morale_factor +0.05, planning_speed +0.1 |
| `bfx_client_kings` | Client Kings | puppet_cost_factor -0.3, annex_cost_factor -0.15, compliance_growth +0.05 |
| `bfx_imperial_mandate` | The Imperial Mandate | stability_factor +0.1, political_power_gain +0.1, compliance_growth +0.1, war_support_factor +0.05 |
| `bfx_legionary_state` | The Legionary State | war_support_factor +0.1, political_power_gain +0.1, stability_factor -0.05, fascism_drift +0.05 |
| `bfx_brannik` | The Brannik | conscription_factor +0.05, war_support_factor +0.03, training_time_army_factor -0.05 |
| `bfx_legionary_militia` | The Legionary Militia | conscription_factor +0.05, army_core_defence_factor +0.05 |
| `bfx_anti_comintern` | Anti-Comintern Bulwark | war_support_factor +0.05, communism_drift -0.03, drift_defence_factor +0.1 |
| `bfx_german_instructors` | German Instructors | army_org_factor +0.05, training_time_army_factor -0.1 |
| `bfx_total_mobilisation` | Total Mobilisation | conscription_factor +0.1, industrial_capacity_factory +0.05, consumer_goods_factor +0.05, stability_factor -0.05 |
| `bfx_national_social_economy` | The National Social Economy | production_factory_max_efficiency_factor +0.05, consumer_goods_factor -0.03, stability_factor +0.03 |
| `bfx_imperium_army` | The Army of the Imperium | army_attack_factor +0.05, army_morale_factor +0.05, justify_war_goal_time -0.15 |
| `bfx_pact_of_iron` | The Pact of Iron | opinion_gain_monthly_factor +0.15, war_support_factor +0.05 |
| `bfx_ferdinand_restoration` | The Coburg Restoration | political_power_gain +0.2, war_support_factor +0.15, stability_factor -0.1 |
| `bfx_third_empire_zeal` | The Third Empire | political_power_gain +0.15, war_support_factor +0.15, justify_war_goal_time -0.25, army_morale_factor +0.05, stability_factor -0.05 |
| `bfx_byzantine_pretension` | Basileus of the Romans and Bulgars | war_support_factor +0.1, justify_war_goal_time -0.2, annex_cost_factor -0.15, stability_factor +0.05 |
| `bfx_royal_natural_history_institute` | Royal Natural History Institute | research_speed_factor +0.04 |
| `bfx_tobacco_monoculture` | Tobacco Monoculture | political_power_gain +0.05, stability_factor -0.02, research_speed_factor -0.03 |
| `bfx_tobacco_and_rose_exports` | Tobacco and Rose Exports | political_power_gain +0.1, consumer_goods_factor -0.02, stability_factor +0.02 |
| `bfx_valley_of_roses` | The Valley of Roses | political_power_gain +0.15, consumer_goods_factor -0.04, stability_factor +0.05 |
| `bfx_german_clearing` | The German Clearing Account | industrial_capacity_factory +0.05, production_speed_buildings_factor +0.1, fascism_drift +0.03 |
| `bfx_german_clearing_deep` | Bound to Berlin | industrial_capacity_factory +0.08, production_speed_buildings_factor +0.1, research_speed_factor +0.03, fascism_drift +0.05, stability_factor -0.03 |
| `bfx_diversified_trade` | Many Buyers | research_speed_factor +0.03, stability_factor +0.05 |
| `bfx_open_markets` | Open Markets | research_speed_factor +0.04, stability_factor +0.05, production_speed_buildings_factor +0.05, trade_opinion_factor +0.2 |
| `bfx_pernik_coal_works` | Pernik Coal Works | production_speed_buildings_factor +0.05, local_resources_factor +0.05 |
| `bfx_pernik_coal_works_2` | Coal and Iron of the Balkan Range | production_speed_buildings_factor +0.08, local_resources_factor +0.1 |
| `bfx_electrification` | Electrification | production_factory_efficiency_gain_factor +0.05 |
| `bfx_iskar_hydro` | Iskar Hydroelectric Grid | production_factory_efficiency_gain_factor +0.1, production_factory_max_efficiency_factor +0.03 |
| `bfx_railway_age` | The Railway Age | production_speed_infrastructure_factor +0.25 |
| `bfx_railway_age_2` | The Main Lines | production_speed_infrastructure_factor +0.25, supply_consumption_factor -0.05 |
| `bfx_state_arsenals` | The State Arsenals | production_speed_arms_factory_factor +0.1, production_factory_start_efficiency_factor +0.05 |
| `bfx_war_economy` | The War Economy | industrial_capacity_factory +0.05, consumer_goods_factor +0.02 |
| `bfx_dispersed_industry` | Dispersed Industry | industry_repair_factor +0.2, production_speed_buildings_factor +0.05 |
| `bfx_chemical_industry` | The Chemical Combine | local_resources_factor +0.05, production_speed_synthetic_refinery_factor +0.2 |
| `bfx_trudovaks` | The Labour Service | production_speed_buildings_factor +0.08, conscription_factor +0.03 |
| `bfx_atomic_commission` | The Atomic Commission | research_speed_factor +0.03 |
| `bfx_mountain_army` | Rhodope Rangers | special_forces_cap +0.15, army_defence_factor +0.03 |
| `bfx_balkan_mountain_doctrine` | Balkan Mountain Doctrine | special_forces_cap +0.25, army_defence_factor +0.05, army_attack_factor +0.03, terrain_penalty_reduction +0.1 |
| `bfx_bayonet_tradition` | The Bayonet Tradition | army_attack_factor +0.04, army_morale_factor +0.05 |
| `bfx_general_staff_academy` | The General Staff Academy | planning_speed +0.1, max_planning +0.05 |
| `bfx_reservist_associations` | The Reservist Associations | conscription_factor +0.03, land_reinforce_rate +0.03 |
| `bfx_veterans_of_1912` | Veterans of the Balkan Wars | army_org_factor +0.03, training_time_army_factor -0.05 |
| `bfx_womens_auxiliary` | The Women's Auxiliary | conscription_factor +0.02, production_speed_buildings_factor +0.03 |
| `bfx_national_army` | The National Army | conscription_factor +0.05, land_reinforce_rate +0.05, army_org_factor +0.03 |
| `bfx_open_conscription` | Universal Service | conscription_factor +0.1, training_time_army_factor -0.05 |
| `bfx_black_sea_flotilla` | The Black Sea Flotilla | experience_gain_navy_factor +0.15, navy_org_factor +0.05 |
| `bfx_black_sea_fleet` | The Black Sea Squadrons | experience_gain_navy_factor +0.15, navy_org_factor +0.1, production_speed_dockyard_factor +0.1, naval_coordination +0.05 |
| `bfx_black_sea_raiders` | Black Sea Raiders | convoy_raiding_efficiency_factor +0.15, naval_strike_attack_factor +0.1 |
| `bfx_minefields` | The Varna Minefields | naval_mine_hit_chance +0.1, naval_mines_damage_factor +0.15 |
| `bfx_clandestine_aviation` | Clandestine Aviation | experience_gain_air_factor +0.1, air_training_xp_gain_factor +0.1 |
| `bfx_vazdushni_voyski` | His Majesty's Air Force | experience_gain_air_factor +0.1, air_superiority_efficiency +0.05, production_speed_air_base_factor +0.25, air_accidents_factor -0.2 |
| `bfx_foreign_air_instructors` | Foreign Flight Instructors | air_training_xp_gain_factor +0.15, air_ace_generation_chance_factor +0.2 |
| `bfx_sofia_air_defence` | Sofia Fighter Command | air_superiority_efficiency +0.05 |
| `bfx_wings_over_the_mountains` | Wings over the Mountains | air_mission_efficiency +0.05, air_training_xp_gain_factor +0.1 |

## Characters (15)
| ID | Name | Roles | Biography |
|---|---|---|---|
| `bfx_BUL_boris_iii` | Boris III | leader (despotism) | Tsar 1918–1943; personal regime from 1935; famous for 'walking between the raindrops'; died Aug 1943 after meeting Hitler. |
| `bfx_BUL_ferdinand_i` | Ferdinand I | leader (despotism) | Prince 1887, Tsar 1908–1918; abdicated after WWI, lived in Coburg until 1948; noted botanist and entomologist. |
| `bfx_BUL_hristo_lukov` | Hristo Lukov | leader (fascism_ideology), corps_commander | General; War Minister 1935–1938; led the Union of Bulgarian National Legions; assassinated in Sofia in February 1943. |
| `bfx_BUL_bogdan_filov` | Bogdan Filov | advisor (political_advisor), leader (despotism) | Archaeologist; PM 1940–1943, signed the Tripartite Pact; regent 1943–44 after Boris's death; executed 1945. |
| `bfx_BUL_georgi_kyoseivanov` | Georgi Kyoseivanov | advisor (political_advisor) | Diplomat; PM 1935–1940; signed the 1937 pact with Yugoslavia and the 1938 Salonika Agreement. |
| `bfx_BUL_kimon_georgiev` | Kimon Georgiev | advisor (political_advisor) | Zveno leader; PM after the 19 May 1934 coup and again 1944–1946. |
| `bfx_BUL_ivan_mihaylov` | Ivan Mihaylov | advisor (political_advisor) | IMRO leader 1924–1934; fled after the Zveno crackdown; died in Rome in 1990. |
| `bfx_BUL_aleksandar_tsankov` | Aleksandar Tsankov | advisor (political_advisor) | PM 1923–1926; founded the National Social Movement in 1932; headed the pro-German government in exile in 1944–45. |
| `bfx_BUL_ivan_dochev` | Ivan Dochev | advisor (political_advisor) | A leading figure of the Union of Bulgarian National Legions; emigrated after 1944. |
| `bfx_BUL_dobri_bozhilov` | Dobri Bozhilov | advisor (political_advisor) | Banker; Finance Minister 1938–1943 and PM 1943–1944. |
| `bfx_BUL_teodosi_daskalov` | Teodosi Daskalov | advisor (high_command) | General; succeeded Lukov as War Minister in 1938. |
| `bfx_BUL_konstantin_lukash` | Konstantin Lukash | advisor (army_chief) | General; Chief of the General Staff 1941–1944; executed by the People's Court in 1945. |
| `bfx_BUL_stoyan_stoyanov` | Stoyan Stoyanov | advisor (air_chief) | Bulgaria's leading fighter ace of the Second World War. |
| `bfx_BUL_nikola_zhekov` | Nikola Zhekov | field_marshal | Commander-in-chief 1915–1918; War Minister 1918; pro-German; died in exile 1949. |
| `bfx_BUL_vladimir_zaimov` | Vladimir Zaimov | corps_commander | General, Military League member; arrested in 1942 as a Soviet agent and executed. |

## Full focus list
| ID | Name | x,y | Prerequisites | Exclusive with | Reward (one line) |
|---|---|---|---|---|---|
| `bfx_tsars_dilemma` | The Tsar's Dilemma | 50,0 | — | — | country_event = bfx.1, unlock_decision_category_tooltip = bfx_court_category, custom_effect_tooltip = bfx_tt_court_p5, add_to_variable = { b |
| `bfx_velchev_trial` | The Velchev Trial | 43,1 | bfx_tsars_dilemma | — | country_event = bfx.2 |
| `bfx_neuilly_ledger` | The Neuilly Ledger | 47,1 | bfx_tsars_dilemma | — | unlock_decision_category_tooltip = bfx_neuilly_category, custom_effect_tooltip = bfx_tt_neuilly_r10_s4, add_to_variable = { bfx_rearm = 10 } |
| `bfx_eternal_friendship` | Eternal Friendship with Belgrade | 53,1 | bfx_tsars_dilemma | — | custom_effect_tooltip = bfx_tt_neuilly_r0_sm15, add_to_variable = { bfx_suspicion = -15 }, bfx_neuilly_recalc = yes |
| `bfx_macedonian_question` | The Macedonian Question | 58,1 | bfx_tsars_dilemma | — | add_political_power = 25, recruit_character = bfx_BUL_ivan_mihaylov |
| `bfx_kingdom_without_parties` | A Kingdom Without Parties | 43,2 | bfx_velchev_trial | — | add_ideas = bfx_partyless_regime, custom_effect_tooltip = bfx_tt_court_p10, add_to_variable = { bfx_inf_palace = 10 }, bfx_court_recalc = ye |
| `bfx_war_ministry_cellars` | Cellars of the War Ministry | 46,2 | bfx_neuilly_ledger | — | set_country_flag = bfx_arms_fronts_open, custom_effect_tooltip = bfx_tt_arms_fronts, custom_effect_tooltip = bfx_tt_neuilly_r6_s3, add_to_va |
| `bfx_hidden_arsenals` | Hidden Arsenals | 49,2 | bfx_neuilly_ledger | — | set_country_flag = bfx_hidden_arsenals, custom_effect_tooltip = bfx_tt_hidden_arsenals, custom_effect_tooltip = bfx_tt_neuilly_r5_s2, add_to |
| `bfx_kyoseivanov_cabinet` | The Kyoseivanov Cabinet | 53,2 | bfx_eternal_friendship | — | recruit_character = bfx_BUL_georgi_kyoseivanov, add_stability = 0.03, custom_effect_tooltip = bfx_tt_neuilly_r0_sm5, add_to_variable = { bfx |
| `bfx_crush_imro` | Crush IMRO | 56,2 | bfx_macedonian_question | bfx_tolerate_imro | set_country_flag = bfx_imro_crushed, custom_effect_tooltip = bfx_tt_court_p10_im30, add_to_variable = { bfx_inf_palace = 10 } add_to_variabl |
| `bfx_tolerate_imro` | Tolerate IMRO | 59,2 | bfx_macedonian_question | bfx_crush_imro | set_country_flag = bfx_imro_tolerated, unlock_decision_category_tooltip = bfx_imro_category, custom_effect_tooltip = bfx_tt_court_i15, add_t |
| `bfx_elections_of_1938` | The Partyless Elections of 1938 | 41,3 | bfx_kingdom_without_parties | — | country_event = bfx.3 |
| `bfx_the_tsars_balance` | The Tsar's Balance | 44,3 | bfx_kingdom_without_parties | — | add_political_power = 50, custom_effect_tooltip = bfx_tt_court_p10, add_to_variable = { bfx_inf_palace = 10 }, bfx_court_recalc = yes, add_i |
| `bfx_tear_up_neuilly` | Tear Up Neuilly | 47,3 | bfx_war_ministry_cellars | bfx_salonika_agreement | bfx_end_neuilly_torn = yes |
| `bfx_salonika_agreement` | The Salonika Agreement | 52,3 | bfx_kyoseivanov_cabinet | bfx_tear_up_neuilly | bfx_end_neuilly_negotiated = yes |
| `bfx_italian_queen` | The Italian Queen | 55,3 | bfx_kyoseivanov_cabinet | — | custom_effect_tooltip = bfx_tt_court_p5, add_to_variable = { bfx_inf_palace = 5 }, bfx_court_recalc = yes |
| `bfx_shadow_legions` | The Shadow Parties | 58,3 | bfx_crush_imro or bfx_tolerate_imro | — | country_event = bfx.4 |
| `bfx_royal_tour` | The Royal Tour | 44,4 | bfx_the_tsars_balance | — | add_stability = 0.05, custom_effect_tooltip = bfx_tt_court_p10, add_to_variable = { bfx_inf_palace = 10 }, bfx_court_recalc = yes |
| `bfx_hour_of_decision` | The Hour of Decision | 50,4 | bfx_elections_of_1938; bfx_shadow_legions | — | add_political_power = 50, custom_effect_tooltip = bfx_tt_hour_of_decision |
| `bfx_open_the_chancelleries` | Open the Chancelleries | 55,4 | bfx_italian_queen | — | set_rule = { can_create_factions = yes can_join_factions = yes can_guarantee_other_ideologies = yes can_send_volunteers = yes can_only_justi |
| `bfx_tsar_steps_forward` | The Tsar Steps Forward | 40,5 | bfx_hour_of_decision | bfx_fas_legions_march | retire_country_leader = yes, recruit_character = bfx_BUL_boris_iii, promote_character = bfx_BUL_boris_iii, set_country_flag = bfx_boris_rule |
| `bfx_tsar_muzzle_the_league` | Muzzle the Military League | 38,6 | bfx_tsar_steps_forward | — | recruit_character = bfx_BUL_nikola_zhekov, custom_effect_tooltip = bfx_tt_court_p10_am15, add_to_variable = { bfx_inf_palace = 10 } add_to_v |
| `bfx_tsar_propaganda_directorate` | The Directorate of Propaganda | 41,6 | bfx_tsar_steps_forward | — | add_war_support = 0.05, custom_effect_tooltip = bfx_tt_court_p5_lm5, add_to_variable = { bfx_inf_palace = 5 } add_to_variable = { bfx_inf_le |
| `bfx_tsar_raindrops` | Walking Between the Raindrops | 34,7 | bfx_tsar_muzzle_the_league | bfx_tsar_stands_alone | add_ideas = bfx_raindrops_diplomacy, recruit_character = bfx_BUL_bogdan_filov, custom_effect_tooltip = bfx_tt_court_p5, add_to_variable = {  |
| `bfx_tsar_berlin_credits` | Arms Credits from Berlin | 31,8 | bfx_tsar_raindrops | — | add_equipment_to_stockpile = { type = infantry_equipment amount = 1500 }, add_tech_bonus = { name = bfx_tsar_berlin_credits bonus = 0.5 uses |
| `bfx_tsar_turkish_pact` | The Turkish Non-Aggression Pact | 34,8 | bfx_tsar_raindrops | — | custom_effect_tooltip = bfx_tt_turkish_nap |
| `bfx_tsar_craiova` | Towards Craiova | 37,8 | bfx_tsar_raindrops | — | add_state_claim = 77, custom_effect_tooltip = bfx_tt_craiova |
| `bfx_tsar_sign_the_pact` | Sign the Tripartite Pact | 31,9 | bfx_tsar_berlin_credits | — | add_ideas = bfx_axis_junior_partner |
| `bfx_tsar_romes_blessing` | Rome's Blessing | 34,9 | bfx_tsar_turkish_pact | — | add_political_power = 25 |
| `bfx_tsar_dobrujan_settlers` | The Dobrujan Settlers | 37,9 | bfx_tsar_craiova | — | 77 = { add_compliance = 20 }, add_manpower = 8000 |
| `bfx_tsar_axis_partition` | The Axis Partition | 32,10 | bfx_tsar_sign_the_pact; bfx_tsar_romes_blessing | — | transfer_state = 106, transfer_state = 184, transfer_state = 731, 106 = { owner = { save_event_target_as = bfx_wg_target } }, create_wargoal |
| `bfx_tsar_western_outlands` | The Western Outlands | 37,10 | bfx_tsar_dobrujan_settlers | — | add_state_claim = 106 |
| `bfx_tsar_occupation_corps` | The Occupation Corps | 31,11 | bfx_tsar_axis_partition | — | add_ideas = bfx_occupation_corps |
| `bfx_tsar_aegean_littoral` | The Aegean Littoral | 34,11 | bfx_tsar_axis_partition | — | add_state_claim = 184, add_state_claim = 731, 184 = { owner = { save_event_target_as = bfx_wg_target } }, create_wargoal = { type = take_sta |
| `bfx_tsar_bessarabian_bulgars` | The Bulgarians of Bessarabia | 37,11 | bfx_tsar_western_outlands | — | add_claim_by = ROOT, add_state_claim = 971, add_war_support = 0.03 |
| `bfx_tsar_no_eastern_front` | Not One Soldier for the Steppe | 31,12 | bfx_tsar_occupation_corps | bfx_tsar_crusade_east | add_ideas = bfx_no_eastern_front, custom_effect_tooltip = bfx_tt_court_p10, add_to_variable = { bfx_inf_palace = 10 }, bfx_court_recalc = ye |
| `bfx_tsar_crusade_east` | The Crusade in the East | 34,12 | bfx_tsar_aegean_littoral | bfx_tsar_no_eastern_front | add_ideas = bfx_eastern_crusade, custom_effect_tooltip = bfx_tt_court_a10_l10, add_to_variable = { bfx_inf_army = 10 } add_to_variable = { b |
| `bfx_tsar_greater_bulgaria` | Greater Bulgaria | 32,13 | bfx_tsar_no_eastern_front or bfx_tsar_crusade_east | — | set_cosmetic_tag = bfx_greater_bulgaria |
| `bfx_tsar_straits_question` | The Straits Question | 31,14 | bfx_tsar_greater_bulgaria | — | add_state_claim = 341, add_state_claim = 797, 341 = { owner = { save_event_target_as = bfx_wg_target } }, create_wargoal = { type = take_sta |
| `bfx_tsar_three_seas` | Bulgaria on Three Seas | 34,14 | bfx_tsar_greater_bulgaria | — | add_claim_by = ROOT |
| `bfx_tsar_adrianople` | Return to Adrianople | 31,15 | bfx_tsar_straits_question | — | 341 = { add_compliance = 20 }, add_stability = 0.03 |
| `bfx_tsar_san_stefano` | The Map of San Stefano | 34,15 | bfx_tsar_three_seas | — | set_cosmetic_tag = bfx_san_stefano_bulgaria, add_war_support = 0.05 |
| `bfx_tsar_of_the_bulgarians` | Tsar of All the Bulgarians | 32,16 | bfx_tsar_adrianople; bfx_tsar_san_stefano | — | add_ideas = bfx_imperial_mandate, add_political_power = 150, army_experience = 50, custom_effect_tooltip = bfx_tt_court_p20, add_to_variable |
| `bfx_tsar_stands_alone` | Bulgaria Stands Alone | 46,7 | bfx_tsar_propaganda_directorate | bfx_tsar_raindrops | add_ideas = bfx_balkan_hegemon, custom_effect_tooltip = bfx_tt_court_p5_a10, add_to_variable = { bfx_inf_palace = 5 } add_to_variable = { bf |
| `bfx_tsar_sofia_pact` | The Sofia Pact | 43,8 | bfx_tsar_stands_alone | — | set_rule = { can_create_factions = yes can_join_factions = yes can_guarantee_other_ideologies = yes can_send_volunteers = yes can_only_justi |
| `bfx_tsar_soviet_pact` | The Sobolev Mission | 46,8 | bfx_tsar_stands_alone | — | add_political_power = 25 |
| `bfx_tsar_albanian_protectorate` | The Albanian Protectorate | 49,8 | bfx_tsar_stands_alone | — | add_claim_by = ROOT |
| `bfx_tsar_revisionist_brothers` | Revisionist Brothers in Budapest | 43,9 | bfx_tsar_sofia_pact | — |  |
| `bfx_tsar_hegemon_army` | The Hegemon's Army | 46,9 | bfx_tsar_soviet_pact | — | add_ideas = bfx_hegemon_army, army_experience = 25 |
| `bfx_tsar_durres_concession` | The Durrës Concession | 49,9 | bfx_tsar_albanian_protectorate | — | navy_experience = 20, add_extra_state_shared_building_slots = 1, add_building_construction = { type = dockyard level = 1 instant_build = yes |
| `bfx_tsar_war_plan_west` | War Plan West: Yugoslavia | 43,10 | bfx_tsar_revisionist_brothers | — | add_state_claim = 106 |
| `bfx_tsar_war_plan_south` | War Plan South: Greece | 46,10 | bfx_tsar_hegemon_army | — | add_state_claim = 184, add_state_claim = 731, set_country_flag = bfx_integration_unlocked, unlock_decision_category_tooltip = bfx_integratio |
| `bfx_tsar_war_plan_north` | War Plan North: Romania | 49,10 | bfx_tsar_durres_concession | — | add_state_claim = 77, add_state_claim = 971 |
| `bfx_tsar_client_kings` | Client Kings | 43,11 | bfx_tsar_war_plan_west | — | add_ideas = bfx_client_kings |
| `bfx_tsar_war_plan_east` | War Plan East: Turkey | 46,11 | bfx_tsar_war_plan_south | — | add_state_claim = 341, add_state_claim = 797 |
| `bfx_tsar_danube_line` | The Danube Line | 49,11 | bfx_tsar_war_plan_north | — |  |
| `bfx_tsar_balkan_tsardom` | The Balkan Tsardom | 46,12 | bfx_tsar_war_plan_east; bfx_tsar_client_kings | — | set_cosmetic_tag = bfx_balkan_tsardom |
| `bfx_tsar_imperial_council` | The Imperial Council | 44,13 | bfx_tsar_balkan_tsardom | — | recruit_character = bfx_BUL_kimon_georgiev, add_political_power = 75 |
| `bfx_tsar_black_sea_dominion` | Dominion of the Black Sea | 47,13 | bfx_tsar_balkan_tsardom; bfx_tsar_danube_line | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = dockyard level = 2 instant_build = yes }, navy_experience =  |
| `bfx_tsar_master_of_the_peninsula` | Master of the Peninsula | 46,14 | bfx_tsar_imperial_council; bfx_tsar_black_sea_dominion | — | add_ideas = bfx_imperial_mandate, add_stability = 0.10, custom_effect_tooltip = bfx_tt_court_p20, add_to_variable = { bfx_inf_palace = 20 }, |
| `bfx_fas_legions_march` | The Legions March | 61,5 | bfx_hour_of_decision | bfx_tsar_steps_forward | country_event = bfx_fas.1 |
| `bfx_fas_legionary_state` | The Legionary State | 61,6 | bfx_fas_legions_march | — | add_ideas = bfx_legionary_state, recruit_character = bfx_BUL_ivan_dochev, custom_effect_tooltip = bfx_tt_court_pm15_l20, add_to_variable = { |
| `bfx_fas_legionary_militia` | The Legionary Militia | 58,7 | bfx_fas_legionary_state | — | add_ideas = bfx_legionary_militia, add_manpower = 10000 |
| `bfx_fas_brannik` | Found the Brannik | 64,7 | bfx_fas_legionary_state | — | add_ideas = bfx_brannik |
| `bfx_fas_into_the_axis` | Into the Axis | 56,8 | bfx_fas_legionary_militia | bfx_fas_national_social_state | add_ideas = bfx_axis_junior_partner |
| `bfx_fas_anti_comintern` | The Anti-Comintern Bulwark | 55,9 | bfx_fas_into_the_axis | — | add_ideas = bfx_anti_comintern |
| `bfx_fas_german_instructors` | German Instructors | 58,9 | bfx_fas_into_the_axis | — | add_ideas = bfx_german_instructors, army_experience = 20 |
| `bfx_fas_dobruja_ultimatum` | The Dobruja Ultimatum | 53,10 | bfx_fas_anti_comintern | — | add_state_claim = 77 |
| `bfx_fas_balkan_blitz` | The Balkan Blitz | 56,10 | bfx_fas_anti_comintern; bfx_fas_german_instructors | — | 106 = { owner = { save_event_target_as = bfx_wg_target } }, create_wargoal = { type = take_state_focus target = event_target:bfx_wg_target g |
| `bfx_fas_axis_air_bases` | Axis Air Bases | 59,10 | bfx_fas_german_instructors | — | capital_scope = { add_building_construction = { type = air_base level = 2 instant_build = yes } }, air_experience = 25 |
| `bfx_fas_new_order` | The New Order in the Balkans | 56,11 | bfx_fas_balkan_blitz | — | transfer_state = 106, transfer_state = 184, transfer_state = 731, set_country_flag = bfx_integration_unlocked, unlock_decision_category_tool |
| `bfx_fas_total_mobilisation` | Total Mobilisation | 59,11 | bfx_fas_axis_air_bases | — | add_ideas = bfx_total_mobilisation |
| `bfx_fas_crusade_east` | Crusade in the East | 55,12 | bfx_fas_new_order | — | add_ideas = bfx_eastern_crusade, custom_effect_tooltip = bfx_tt_court_l10, add_to_variable = { bfx_inf_legion = 10 }, bfx_court_recalc = yes |
| `bfx_fas_legionary_bulgaria` | Legionary Greater Bulgaria | 58,12 | bfx_fas_new_order; bfx_fas_total_mobilisation | — | set_cosmetic_tag = bfx_legionary_bulgaria, add_war_support = 0.05 |
| `bfx_fas_budjak` | The Budjak Bulgarians | 53,13 | bfx_fas_crusade_east | — | add_claim_by = ROOT, add_state_claim = 971 |
| `bfx_fas_odessa_corridor` | The Odessa Corridor | 56,13 | bfx_fas_crusade_east | — |  |
| `bfx_fas_aegean_fleet` | The Aegean Fleet | 59,13 | bfx_fas_legionary_bulgaria | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = dockyard level = 2 instant_build = yes }, navy_experience =  |
| `bfx_fas_legionary_empire` | The Legionary Empire | 56,14 | bfx_fas_budjak; bfx_fas_odessa_corridor; bfx_fas_aegean_fleet | — | add_ideas = bfx_imperial_mandate |
| `bfx_fas_thrace_to_bosporus` | Thrace to the Bosporus | 55,15 | bfx_fas_legionary_empire | — | add_state_claim = 341, add_state_claim = 797, 341 = { owner = { save_event_target_as = bfx_wg_target } }, create_wargoal = { type = take_sta |
| `bfx_fas_legion_of_st_george` | The Legion of St George | 58,15 | bfx_fas_legionary_empire | — | army_experience = 50, add_manpower = 25000 |
| `bfx_fas_new_bulgarian_order` | The New Bulgarian Order | 56,16 | bfx_fas_thrace_to_bosporus; bfx_fas_legion_of_st_george | — | add_stability = 0.10, add_political_power = 150, custom_effect_tooltip = bfx_tt_court_l10, add_to_variable = { bfx_inf_legion = 10 }, bfx_co |
| `bfx_fas_national_social_state` | The National Social State | 65,8 | bfx_fas_brannik | bfx_fas_into_the_axis | add_ideas = bfx_national_social_economy, recruit_character = bfx_BUL_aleksandar_tsankov |
| `bfx_fas_corporatist_economy` | The Corporations | 64,9 | bfx_fas_national_social_state | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes }, add_extr |
| `bfx_fas_pact_of_iron` | The Pact of Iron | 67,9 | bfx_fas_national_social_state | — | add_ideas = bfx_pact_of_iron |
| `bfx_fas_imperium_army` | The Army of the Imperium | 64,10 | bfx_fas_corporatist_economy | — | add_ideas = bfx_imperium_army, add_tech_bonus = { name = bfx_fas_imperium_army bonus = 0.5 uses = 1 category = artillery } |
| `bfx_fas_budapest_axis` | The Budapest-Sofia Axis | 67,10 | bfx_fas_pact_of_iron | — |  |
| `bfx_fas_rival_to_rome` | A Rival to Rome | 70,10 | bfx_fas_pact_of_iron | — | add_claim_by = ROOT |
| `bfx_fas_war_for_macedonia` | The War for Macedonia | 64,11 | bfx_fas_imperium_army | — | add_state_claim = 106 |
| `bfx_fas_war_for_the_aegean` | The War for the Aegean | 67,11 | bfx_fas_imperium_army; bfx_fas_budapest_axis | — | add_state_claim = 184, add_state_claim = 731, set_country_flag = bfx_integration_unlocked, unlock_decision_category_tooltip = bfx_integratio |
| `bfx_fas_adriatic_ambitions` | Adriatic Ambitions | 70,11 | bfx_fas_rival_to_rome | — | add_claim_by = ROOT, navy_experience = 15 |
| `bfx_fas_war_for_the_danube` | The War for the Danube | 65,12 | bfx_fas_war_for_macedonia; bfx_fas_war_for_the_aegean | — | add_state_claim = 77, add_state_claim = 971, 77 = { owner = { save_event_target_as = bfx_wg_target } }, create_wargoal = { type = take_state |
| `bfx_fas_war_for_the_straits` | The War for the Straits | 68,12 | bfx_fas_war_for_the_aegean; bfx_fas_adriatic_ambitions | — | add_state_claim = 341, add_state_claim = 797, 341 = { owner = { save_event_target_as = bfx_wg_target } }, create_wargoal = { type = take_sta |
| `bfx_fas_bulgarian_imperium` | The Bulgarian Imperium | 67,13 | bfx_fas_war_for_the_danube; bfx_fas_war_for_the_straits | — | set_cosmetic_tag = bfx_bulgarian_imperium, add_war_support = 0.05 |
| `bfx_fas_settle_new_provinces` | Settle the New Provinces | 65,14 | bfx_fas_bulgarian_imperium | — | add_ideas = bfx_occupation_corps |
| `bfx_fas_imperial_navy` | The Imperial Navy | 68,14 | bfx_fas_bulgarian_imperium | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = dockyard level = 2 instant_build = yes }, navy_experience =  |
| `bfx_fas_legions_of_the_imperium` | Legions of the Imperium | 65,15 | bfx_fas_settle_new_provinces | — | army_experience = 50, add_manpower = 20000 |
| `bfx_fas_mediterranean_window` | A Window on the Mediterranean | 68,15 | bfx_fas_imperial_navy | — | add_state_claim = 187, navy_experience = 15 |
| `bfx_fas_tsardom_of_three_seas` | The Imperium on Three Seas | 67,16 | bfx_fas_legions_of_the_imperium; bfx_fas_mediterranean_window | — | add_ideas = bfx_imperial_mandate, add_stability = 0.10, add_political_power = 150 |
| `bfx_alt_old_fox_stirs` | The Old Fox Returns | 20,6 | — | — | country_event = bfx_secret.10 |
| `bfx_alt_burn_the_treaty` | Burn the Treaty on the Steps of Neuilly | 19,7 | bfx_alt_old_fox_stirs | — |  |
| `bfx_alt_entomologist_tsar` | The Entomologist Tsar | 22,7 | bfx_alt_old_fox_stirs | — | add_ideas = bfx_royal_natural_history_institute |
| `bfx_alt_imperial_life_guard` | The Imperial Life Guard | 19,8 | bfx_alt_burn_the_treaty | — | army_experience = 25, add_equipment_to_stockpile = { type = infantry_equipment amount = 2000 }, add_manpower = 10000 |
| `bfx_alt_coburg_capital` | Coburg Capital | 22,8 | bfx_alt_entomologist_tsar | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes }, add_extr |
| `bfx_alt_third_empire` | Proclaim the Third Bulgarian Empire | 17,9 | bfx_alt_imperial_life_guard | bfx_alt_tsargrad | add_ideas = bfx_third_empire_zeal, set_cosmetic_tag = bfx_third_empire, add_state_claim = 77, add_state_claim = 106, add_state_claim = 184,  |
| `bfx_alt_simeons_borders` | The Borders of Simeon the Great | 17,10 | bfx_alt_third_empire | — | add_claim_by = ROOT |
| `bfx_alt_tsar_of_the_vlachs` | Tsar of Bulgarians and Vlachs | 16,11 | bfx_alt_simeons_borders | — | add_claim_by = ROOT |
| `bfx_alt_restore_preslav` | Restore Preslav | 19,11 | bfx_alt_simeons_borders | — | add_stability = 0.05, add_political_power = 75 |
| `bfx_alt_coronation_at_tarnovo` | Coronation at Tarnovo | 17,12 | bfx_alt_tsar_of_the_vlachs; bfx_alt_restore_preslav | — | country_event = bfx_secret.12 |
| `bfx_alt_kaloyans_revenge` | Kaloyan's Revenge | 17,13 | bfx_alt_coronation_at_tarnovo | — | add_state_claim = 731, 731 = { owner = { save_event_target_as = bfx_wg_target } }, create_wargoal = { type = take_state_focus target = event |
| `bfx_alt_empire_of_the_bulgars` | Empire of the Bulgars | 17,14 | bfx_alt_kaloyans_revenge | — | add_ideas = bfx_imperial_mandate, add_stability = 0.10 |
| `bfx_alt_tsargrad` | Tsargrad! | 23,9 | bfx_alt_coburg_capital | bfx_alt_third_empire | add_ideas = bfx_byzantine_pretension, add_state_claim = 797, add_state_claim = 341, 797 = { owner = { save_event_target_as = bfx_wg_target } |
| `bfx_alt_basileus` | Basileus of the Romans and Bulgars | 23,10 | bfx_alt_tsargrad | — | add_claim_by = ROOT, add_political_power = 50 |
| `bfx_alt_hagia_sophia` | Mass in Hagia Sophia | 22,11 | bfx_alt_basileus | — | set_cosmetic_tag = bfx_byzantium, add_stability = 0.15, news_event = { id = bfx_secret.11 days = 1 } |
| `bfx_alt_restore_the_themes` | Restore the Themes | 25,11 | bfx_alt_basileus | — | add_claim_by = ROOT |
| `bfx_alt_varangian_guard` | The New Varangian Guard | 23,12 | bfx_alt_hagia_sophia; bfx_alt_restore_the_themes | — | army_experience = 40, add_manpower = 15000 |
| `bfx_alt_orthodox_crusade` | The Orthodox Crusade | 23,13 | bfx_alt_varangian_guard | — | add_state_claim = 187, add_state_claim = 182 |
| `bfx_alt_new_rome` | New Rome | 23,14 | bfx_alt_orthodox_crusade | — | add_ideas = bfx_imperial_mandate, add_stability = 0.05 |
| `bfx_eco_rose_and_leaf` | The Rose and the Leaf | 86,0 | — | — | add_political_power = 30, set_country_flag = bfx_trade_question |
| `bfx_eco_german_clearing` | The German Clearing Account | 77,1 | bfx_eco_rose_and_leaf | bfx_eco_diversify | add_ideas = bfx_german_clearing |
| `bfx_eco_diversify` | Diversify the Buyers | 80,1 | bfx_eco_rose_and_leaf | bfx_eco_german_clearing | add_ideas = bfx_diversified_trade |
| `bfx_eco_pernik_coal` | Pernik Coal | 86,1 | bfx_eco_rose_and_leaf | — | add_ideas = bfx_pernik_coal_works, capital_scope = { add_resource = { type = steel amount = 4 } } |
| `bfx_eco_bdz` | Modernise the BDŽ | 92,1 | bfx_eco_rose_and_leaf | — | add_ideas = bfx_railway_age |
| `bfx_eco_sofia_university` | Sofia University Institutes | 97,1 | bfx_eco_rose_and_leaf | — | add_tech_bonus = { name = bfx_eco_sofia_university bonus = 0.5 uses = 1 category = electronics }, add_tech_bonus = { name = bfx_eco_sofia_un |
| `bfx_eco_tobacco_boom` | The Plovdiv Tobacco Boom | 79,2 | bfx_eco_german_clearing or bfx_eco_diversify | — |  |
| `bfx_eco_balkan_iron` | Iron from the Balkan Range | 85,2 | bfx_eco_pernik_coal | — | capital_scope = { add_resource = { type = steel amount = 4 } } |
| `bfx_eco_electrification` | Electrify the Plain | 88,2 | bfx_eco_pernik_coal | — | add_ideas = bfx_electrification, add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level =  |
| `bfx_eco_main_line` | The Sofia–Varna Main Line | 92,2 | bfx_eco_bdz | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes } |
| `bfx_eco_nadjakov_laboratory` | Nadjakov's Laboratory | 97,2 | bfx_eco_sofia_university | — | add_tech_bonus = { name = bfx_eco_nadjakov_laboratory bonus = 0.5 uses = 2 category = electronics } |
| `bfx_eco_valley_of_roses` | The Valley of Roses | 79,3 | bfx_eco_tobacco_boom | — |  |
| `bfx_eco_kremikovtsi_steel` | The Kremikovtsi Steelworks | 85,3 | bfx_eco_balkan_iron | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = arms_factory level = 1 instant_build = yes }, capital_scope  |
| `bfx_eco_iskar_dams` | Dams on the Iskar | 88,3 | bfx_eco_electrification | — |  |
| `bfx_eco_danube_ports` | The Danube Ports | 91,3 | bfx_eco_main_line | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes }, add_tech |
| `bfx_eco_black_sea_ports` | Ports of Varna and Burgas | 94,3 | bfx_eco_main_line | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = dockyard level = 2 instant_build = yes } |
| `bfx_eco_bukhovo_uranium` | The Bukhovo Deposits | 97,3 | bfx_eco_nadjakov_laboratory | — | capital_scope = { add_extra_state_shared_building_slots = 1 }, add_tech_bonus = { name = bfx_eco_bukhovo_uranium bonus = 0.5 uses = 1 catego |
| `bfx_eco_hard_currency` | Hard Currency for Machines | 79,4 | bfx_eco_valley_of_roses | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes } |
| `bfx_eco_kazanlak_arsenal` | The Kazanlak Arsenal | 83,4 | bfx_eco_kremikovtsi_steel | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = arms_factory level = 1 instant_build = yes }, add_tech_bonus |
| `bfx_eco_sopot_works` | The Sopot Rifle Works | 86,4 | bfx_eco_kremikovtsi_steel | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = arms_factory level = 1 instant_build = yes }, add_tech_bonus |
| `bfx_eco_hydro_grid` | The National Grid | 89,4 | bfx_eco_iskar_dams | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes }, add_tech |
| `bfx_eco_labour_brigades` | The Labour Service Brigades | 94,4 | bfx_eco_black_sea_ports | — | add_ideas = bfx_trudovaks, custom_effect_tooltip = bfx_tt_neuilly_r6_s3, add_to_variable = { bfx_rearm = 6 } add_to_variable = { bfx_suspici |
| `bfx_eco_atomic_commission` | The Atomic Commission | 97,4 | bfx_eco_bukhovo_uranium | — | add_ideas = bfx_atomic_commission, add_tech_bonus = { name = bfx_eco_atomic_commission bonus = 0.5 uses = 1 category = nuclear } |
| `bfx_eco_ledger_of_trade` | The Ledger of Trade | 79,5 | bfx_eco_hard_currency | — | country_event = bfx.10 |
| `bfx_eco_state_arsenals` | The State Arsenals | 85,5 | bfx_eco_kazanlak_arsenal; bfx_eco_sopot_works | — | add_ideas = bfx_state_arsenals |
| `bfx_eco_chemical_combine` | The Chemical Combine | 89,5 | bfx_eco_hydro_grid | — | add_ideas = bfx_chemical_industry, add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level  |
| `bfx_eco_road_network` | The Trans-Balkan Roads | 94,5 | bfx_eco_labour_brigades | — |  |
| `bfx_eco_reactor_project` | The Reactor Project | 97,5 | bfx_eco_atomic_commission | — | add_tech_bonus = { name = bfx_eco_reactor_project bonus = 1.0 uses = 1 category = nuclear } |
| `bfx_eco_plovdiv_fair` | The Plovdiv International Fair | 77,6 | bfx_eco_ledger_of_trade | — | add_tech_bonus = { name = bfx_eco_plovdiv_fair bonus = 0.5 uses = 2 category = industry } |
| `bfx_eco_export_drive` | The Export Drive | 80,6 | bfx_eco_ledger_of_trade | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes }, add_poli |
| `bfx_eco_war_economy` | The War Economy | 85,6 | bfx_eco_state_arsenals | — | add_ideas = bfx_war_economy, add_extra_state_shared_building_slots = 1, add_building_construction = { type = arms_factory level = 1 instant_ |
| `bfx_eco_tyulenovo_oil` | Petroleum at Tyulenovo | 88,6 | bfx_eco_chemical_combine | — |  |
| `bfx_eco_synthetic_fuel` | Synthetic Fuel from Lignite | 91,6 | bfx_eco_chemical_combine | — | capital_scope = { add_extra_state_shared_building_slots = 1 add_building_construction = { type = synthetic_refinery level = 1 instant_build  |
| `bfx_eco_kozloduy_reactor` | The Kozloduy Pile | 97,6 | bfx_eco_reactor_project | — | capital_scope = { add_building_construction = { type = nuclear_reactor level = 1 instant_build = yes } } |
| `bfx_eco_national_bank` | Reform the National Bank | 79,7 | bfx_eco_plovdiv_fair; bfx_eco_export_drive | — | add_stability = 0.05, add_political_power = 75 |
| `bfx_eco_industrial_ring` | The Sofia Industrial Ring | 83,7 | bfx_eco_war_economy | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes }, add_extr |
| `bfx_eco_dispersed_industry` | Dispersed Industry | 86,7 | bfx_eco_war_economy | — | add_ideas = bfx_dispersed_industry, add_extra_state_shared_building_slots = 1, add_building_construction = { type = arms_factory level = 1 i |
| `bfx_eco_fuel_reserves` | Strategic Fuel Reserves | 89,7 | bfx_eco_tyulenovo_oil; bfx_eco_synthetic_fuel | — | capital_scope = { add_building_construction = { type = fuel_silo level = 1 instant_build = yes } }, add_tech_bonus = { name = bfx_eco_fuel_r |
| `bfx_eco_rila_device` | The Rila Device | 97,7 | bfx_eco_kozloduy_reactor | — | add_tech_bonus = { name = bfx_eco_rila_device bonus = 1.0 uses = 2 category = nuclear }, add_war_support = 0.05 |
| `bfx_eco_academy_of_sciences` | The Academy of Sciences | 80,8 | bfx_eco_national_bank | — | add_research_slot = 1 |
| `bfx_eco_total_war_production` | Total War Production | 85,8 | bfx_eco_industrial_ring; bfx_eco_dispersed_industry | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = arms_factory level = 1 instant_build = yes }, add_extra_stat |
| `bfx_mil_neuilly_army` | The Army Neuilly Built | 115,0 | — | — | army_experience = 10, custom_effect_tooltip = bfx_tt_neuilly_r5_s2, add_to_variable = { bfx_rearm = 5 } add_to_variable = { bfx_suspicion =  |
| `bfx_mil_rhodope_rangers` | Rhodope Rangers | 101,1 | bfx_mil_neuilly_army | — | add_ideas = bfx_mountain_army, add_tech_bonus = { name = bfx_mil_rhodope_rangers bonus = 0.75 uses = 1 category = mountaineers_tech } |
| `bfx_mil_chataldzha_lessons` | Lessons of Chataldzha | 104,1 | bfx_mil_neuilly_army | — | add_mastery_bonus = { bonus = 0.20 days = 365 name = bfx_mil_chataldzha_lessons folder = land }, army_experience = 15 |
| `bfx_mil_mountain_doctrine` | Balkan Mountain Doctrine | 101,2 | bfx_mil_rhodope_rangers | — |  |
| `bfx_mil_staff_academy` | The General Staff Academy | 104,2 | bfx_mil_chataldzha_lessons | — | add_ideas = bfx_general_staff_academy, recruit_character = bfx_BUL_konstantin_lukash |
| `bfx_mil_mountain_brigades` | The Mountain Brigades | 101,3 | bfx_mil_mountain_doctrine | — | add_tech_bonus = { name = bfx_mil_mountain_brigades bonus = 0.5 uses = 1 category = mountaineers_tech }, army_experience = 15 |
| `bfx_mil_bayonet_tradition` | The Bayonet Tradition | 104,3 | bfx_mil_staff_academy | — | add_ideas = bfx_bayonet_tradition |
| `bfx_mil_balkan_war_plan` | The Balkan War Plan | 103,4 | bfx_mil_mountain_brigades; bfx_mil_bayonet_tradition | — | army_experience = 25, recruit_character = bfx_BUL_teodosi_daskalov |
| `bfx_mil_officer_corps` | Expand the Officer Corps | 101,5 | bfx_mil_balkan_war_plan | — | army_experience = 20, recruit_character = bfx_BUL_vladimir_zaimov |
| `bfx_mil_combined_arms` | Combined Arms | 104,5 | bfx_mil_balkan_war_plan | — | add_mastery_bonus = { bonus = 0.20 days = 365 name = bfx_mil_combined_arms folder = land } |
| `bfx_mil_royal_guard` | The Royal Guard Division | 101,6 | bfx_mil_officer_corps | — | add_equipment_to_stockpile = { type = infantry_equipment amount = 1500 }, army_experience = 15, custom_effect_tooltip = bfx_tt_court_p5_a5,  |
| `bfx_mil_armoured_brigade` | The Armoured Brigade | 104,6 | bfx_mil_combined_arms | — | add_tech_bonus = { name = bfx_mil_armoured_brigade bonus = 0.5 uses = 1 category = armor }, add_tech_bonus = { name = bfx_mil_armoured_motor |
| `bfx_mil_mountain_blitz` | Blitzkrieg in the Mountains | 103,7 | bfx_mil_royal_guard; bfx_mil_armoured_brigade | — | add_mastery_bonus = { bonus = 0.25 days = 365 name = bfx_mil_mountain_blitz folder = land }, army_experience = 25 |
| `bfx_mil_small_arms` | Small Arms Standardisation | 109,1 | bfx_mil_neuilly_army | — | add_tech_bonus = { name = bfx_mil_small_arms bonus = 0.5 uses = 1 category = infantry_weapons } |
| `bfx_mil_mountain_guns` | Mountain Guns | 107,2 | bfx_mil_small_arms | — | add_tech_bonus = { name = bfx_mil_mountain_guns bonus = 0.5 uses = 1 category = artillery } |
| `bfx_mil_machine_guns` | The Machine-Gun Companies | 110,2 | bfx_mil_small_arms | — | add_equipment_to_stockpile = { type = infantry_equipment amount = 1000 }, add_tech_bonus = { name = bfx_mil_machine_guns bonus = 0.5 uses =  |
| `bfx_mil_rifle_contracts` | The Mauser Contracts | 107,3 | bfx_mil_mountain_guns | — | add_equipment_to_stockpile = { type = infantry_equipment amount = 2000 } |
| `bfx_mil_anti_tank` | Anti-Tank Companies | 110,3 | bfx_mil_machine_guns | — | add_tech_bonus = { name = bfx_mil_anti_tank bonus = 0.5 uses = 1 category = artillery }, army_experience = 10 |
| `bfx_mil_field_artillery` | The Field Artillery Regiments | 109,4 | bfx_mil_rifle_contracts; bfx_mil_anti_tank | — | add_equipment_to_stockpile = { type = artillery_equipment amount = 150 }, add_tech_bonus = { name = bfx_mil_field_artillery bonus = 0.5 uses |
| `bfx_mil_support_companies` | Support Companies | 109,5 | bfx_mil_field_artillery | — | add_tech_bonus = { name = bfx_mil_support_companies bonus = 0.5 uses = 2 category = support_tech } |
| `bfx_mil_supply_columns` | The Supply Columns | 109,6 | bfx_mil_support_companies | — | add_tech_bonus = { name = bfx_mil_supply_columns bonus = 0.5 uses = 1 category = motorized_equipment }, add_equipment_to_stockpile = { type  |
| `bfx_mil_reservists` | The Reservist Associations | 115,1 | bfx_mil_neuilly_army | — | add_ideas = bfx_reservist_associations, add_manpower = 5000, custom_effect_tooltip = bfx_tt_neuilly_r4_s2, add_to_variable = { bfx_rearm = 4 |
| `bfx_mil_macedonian_emigration` | Volunteers of the Emigration | 113,2 | bfx_mil_reservists | — | add_manpower = 12000, custom_effect_tooltip = bfx_tt_court_i5, add_to_variable = { bfx_inf_imro = 5 }, bfx_court_recalc = yes |
| `bfx_mil_pomak_battalions` | The Rhodope Battalions | 116,2 | bfx_mil_reservists | — | add_manpower = 8000, add_tech_bonus = { name = bfx_mil_pomak_battalions bonus = 0.25 uses = 1 category = mountaineers_tech } |
| `bfx_mil_veterans_1912` | Veterans of the Balkan Wars | 113,3 | bfx_mil_macedonian_emigration | — | add_ideas = bfx_veterans_of_1912 |
| `bfx_mil_womens_auxiliary` | The Women's Auxiliary | 116,3 | bfx_mil_pomak_battalions | — | add_ideas = bfx_womens_auxiliary |
| `bfx_mil_universal_service` | Universal Service, Openly | 115,4 | bfx_mil_veterans_1912; bfx_mil_womens_auxiliary | — | add_manpower = 25000, add_ideas = bfx_open_conscription |
| `bfx_mil_mobilisation_law` | The Mobilisation Law | 113,5 | bfx_mil_universal_service | — | add_manpower = 15000, army_experience = 10 |
| `bfx_mil_training_camps` | Training Camps in the Rhodopes | 116,5 | bfx_mil_universal_service | — | add_tech_bonus = { name = bfx_mil_training_camps bonus = 0.25 uses = 1 category = infantry_weapons }, army_experience = 15, add_manpower = 5 |
| `bfx_mil_national_army` | The National Army | 115,6 | bfx_mil_mobilisation_law; bfx_mil_training_camps | — | add_ideas = bfx_national_army |
| `bfx_nav_black_sea_flotilla` | The Black Sea Flotilla | 121,1 | bfx_mil_neuilly_army | — | add_ideas = bfx_black_sea_flotilla, navy_experience = 10 |
| `bfx_nav_varna_naval_school` | The Varna Naval School | 119,2 | bfx_nav_black_sea_flotilla | — | navy_experience = 15, add_extra_state_shared_building_slots = 1, add_building_construction = { type = dockyard level = 1 instant_build = yes |
| `bfx_nav_danube_flotilla` | The Danube Flotilla | 122,2 | bfx_nav_black_sea_flotilla | — | navy_experience = 10, add_extra_state_shared_building_slots = 1, add_building_construction = { type = dockyard level = 1 instant_build = yes |
| `bfx_nav_torpedo_squadrons` | Torpedo Boat Squadrons | 119,3 | bfx_nav_varna_naval_school | — | custom_effect_tooltip = bfx_tt_neuilly_r4_s3, add_to_variable = { bfx_rearm = 4 } add_to_variable = { bfx_suspicion = 3 }, bfx_neuilly_recal |
| `bfx_nav_minelayers` | The Varna Minefields | 122,3 | bfx_nav_danube_flotilla | — | add_ideas = bfx_minefields |
| `bfx_nav_coastal_batteries` | Coastal Batteries at Galata | 119,4 | bfx_nav_torpedo_squadrons | — |  |
| `bfx_nav_naval_aviation` | Naval Aviation | 122,4 | bfx_nav_minelayers | — | air_experience = 10, navy_experience = 10 |
| `bfx_nav_black_sea_raiders` | Black Sea Raiders | 121,5 | bfx_nav_coastal_batteries; bfx_nav_naval_aviation | — | add_ideas = bfx_black_sea_raiders, navy_experience = 20 |
| `bfx_nav_submarine_flotilla` | The Submarine Flotilla | 119,6 | bfx_nav_black_sea_raiders | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = dockyard level = 1 instant_build = yes }, navy_experience =  |
| `bfx_nav_destroyer_squadron` | The Destroyer Squadron | 122,6 | bfx_nav_black_sea_raiders | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = dockyard level = 1 instant_build = yes }, navy_experience =  |
| `bfx_air_aero_clubs` | Aero Clubs and Gliders | 127,1 | bfx_mil_neuilly_army | — | add_ideas = bfx_clandestine_aviation, air_experience = 10, custom_effect_tooltip = bfx_tt_neuilly_r6_s3, add_to_variable = { bfx_rearm = 6 } |
| `bfx_air_dar_works` | The DAR Works at Bozhurishte | 125,2 | bfx_air_aero_clubs | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = arms_factory level = 1 instant_build = yes }, air_experience |
| `bfx_air_polish_fighters` | PZL Fighters from Warsaw | 128,2 | bfx_air_aero_clubs | — | air_experience = 20 |
| `bfx_air_avia_biplanes` | Avia Biplanes from Prague | 125,3 | bfx_air_dar_works | — | air_experience = 15 |
| `bfx_air_foreign_instructors` | Foreign Instructors | 128,3 | bfx_air_polish_fighters | — | add_ideas = bfx_foreign_air_instructors, air_experience = 15 |
| `bfx_air_vazdushni_voyski` | Proclaim the Vazdushni Voyski | 127,4 | bfx_air_avia_biplanes; bfx_air_foreign_instructors | — | capital_scope = { add_building_construction = { type = air_base level = 3 instant_build = yes } }, recruit_character = bfx_BUL_stoyan_stoyan |
| `bfx_air_fighter_regiment` | The Fighter Regiment | 125,5 | bfx_air_vazdushni_voyski | — | add_ideas = bfx_sofia_air_defence, air_experience = 15 |
| `bfx_air_dornier_bombers` | Dornier Bombers | 128,5 | bfx_air_vazdushni_voyski | — | air_experience = 20, add_tech_bonus = { name = bfx_air_dornier_bombers bonus = 0.25 uses = 1 category = industry } |
| `bfx_air_sofia_flak` | Flak over Sofia | 125,6 | bfx_air_fighter_regiment | — | capital_scope = { add_building_construction = { type = anti_air_building level = 3 instant_build = yes } } |
| `bfx_air_wings_over_mountains` | Wings over the Mountains | 128,6 | bfx_air_dornier_bombers | — | add_ideas = bfx_wings_over_the_mountains |
| `bfx_air_paratroopers` | The Parachute Battalion | 127,7 | bfx_air_sofia_flak; bfx_air_wings_over_mountains | — | add_tech_bonus = { name = bfx_air_paratroopers bonus = 0.5 uses = 1 category = para_tech }, army_experience = 15 |
