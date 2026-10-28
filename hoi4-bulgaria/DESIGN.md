# DESIGN — Bulgaria: Shackles of Neuilly (`bfx_bulgaria`)

Target: **Hearts of Iron IV 1.19.4** (`supported_version = "1.19.*"`), base game only, Road to 56 compatible.
Everything below is generated from, or kept in sync with, `tools/build/*.py`, the single source of truth that
produces the mod. The focus table at the end is regenerated on every build.

## Premise
Bulgaria in 1936: twice defeated (1913, 1918), bound by the Treaty of Neuilly (20,000 volunteers, no conscription,
no air force, no real navy), dreaming of the San Stefano borders of 1878, and pulled between Tsar Boris III's
personal regime, the outlawed Communists, the Agrarians and the Zveno officers, with IMRO running Petrich as a private state.

## Structure (134 focuses)
| Block | Focuses | Contents |
|---|---|---|
| Opening | 15 | Tsar's dilemma, the Velchev trial, partyless regime and 1938 elections, IMRO crush/tolerate, Eternal Friendship with Yugoslavia, Kyoseivanov, **Salonika Agreement vs. Tear Up Neuilly**, Hour of Decision |
| Tsardom (Boris III) | 21 | (a) San Stefano revanchism → Axis, Dobruja, Vardar, Aegean, *Bulgaria on Three Seas* (Albania, Montenegro). (b) Balkan Switzerland → Balkan Concord, London or Third Way, *Danubian-Balkan Confederation* (peaceful union with faction members); capstones *Tsar of All the Balkans* and *The Imperial Federation* |
| Alt-history (Coburg restoration) | 18 | Late unlock under the Tsardom: needs Rearmament 80+ (or the treaty torn up), war support 50%+, after mid-1937. (a) Third Bulgarian Empire → Simeon's borders, Tsar of the Vlachs, *Old Great Bulgaria* (Ukraine/Crimea). (b) Tsargrad → Basileus, Hagia Sophia, Themes, *Exarchate of Ravenna* (Italy); capstones *Return to the Volga* (claims on all Soviet lands) and *The Empire of Justinian* (Egypt, the Levant) |
| Communist (BKP) | 20 | Fatherland Front, Ninth of September coup (peaceful at 40% support, civil war otherwise). (a) Dimitrov's Moscow-model republic → Comintern, Straits for Moscow, *Red Black Sea*. (b) Kolarov's Balkan Federation → partisans, independent line, *Red Danubian Federation* (Romania, Hungary, Czechoslovakia, Austria); capstones *Black Sea Socialist Union* (Anatolia, Caucasus) and *From Trieste to Odessa* |
| Agrarian / Zveno | 20 | Second 19th of May. (a) Stamboliyski's heirs → Land to the Tiller, Orange Guard, referendum, *Green International*, *Balkan Peasant Union*, *Baltic to Aegean*. (b) Zveno technocracy → Officers' State, Technocrats' Plan, Prussia of the Balkans, *Anatolian Gambit*; capstones *The Peasant Commonwealth* and *The Levant Command* |
| Economy | 20 | Rose & tobacco exports (3-stage spirit), **German clearing vs. diversification** (trade-off with a follow-up event), Pernik coal, Kremikovtsi iron, Kazanlak arsenal, BDŽ railways, Iskar dams, ports, oil prospects, labour service |
| Military | 20 | Army 9 (mountain doctrine, Chataldzha lessons, staff academy, conscription only after Neuilly ends), Navy 5 (Black Sea flotilla, torpedo boats, coastal guns, raiders), Air 6 (aero clubs, DAR works, open air force only after Neuilly ends) |

Plain stat bumps: 8 of 134 (6%). Layout: every focus has at least one empty column on each side (`X_SCALE = 2`), the whole tree starts 14 columns from the left edge (`X_OFFSET`), and the continuous-focus panel sits in that space, below the deepest row. Every real choice is a `mutually_exclusive` pair whose description says what it rules out.
Every focus has `search_filters` and `ai_will_do`.

### Coring and formables far beyond 1878
All far-reaching claims and cores are **tag-driven** (`is_core_of = TAG`), so they need no hard-coded state IDs:
Greater Bulgaria (+Albania, Montenegro, Central Macedonia, Edirne), Danubian-Balkan Confederation (peaceful annexation of faction members),
Third Bulgarian Empire / Old Great Bulgaria (Yugoslavia, Albania, Romania, Ukraine, Crimea), Empire of the Romans and Bulgars
(Istanbul, Greece, all of Anatolia, Italy via the Tsargrad *Theme* decisions), Balkan Federation / Red Danubian Federation
(integration decisions for communist neighbours), Balkan Peasant Union (peaceful union offers up to Poland and the Baltics),
Balkan Military Union (Anatolia). Ten cosmetic tags, each with its own generated flag.

**Imperial Integration** (decision category, unlocked mid-way along every branch): 14 repeatable *Integrate ...*
decisions (60 PP, −2% stability, 60-day cooldown). Each cores every held state of a region: Western Balkans, Albania, Hellas,
Wallachia and Moldavia, Pannonia, Anatolia, the Caucasus, the Levant, Egypt, Italy, Central Europe, the Pontic Steppe,
the Volga (Soviet core lands), the Baltic. **Proclaim the Bulgarian Empire** (hold Macedonia, Thrace, Dobrudja and Edirne)
cores every held Balkan state, claims Hungary and Austria and grants *The Imperial Mandate*. The name follows the
ideology: Bulgarian Empire, Bulgarian Imperium, Union of Balkan Soviet Republics or Commonwealth of the Balkans.

## The mechanic: Shackles of Neuilly
* Variables: `bfx_rearm` (Covert Rearmament, 0–100) and `bfx_suspicion` (Balkan Suspicion, 0–100; starts 10, −2/month).
* Spirit `bfx_neuilly_shackles`: conscription −30%, army organisation −10%, army training time +25%, air accidents +50%, dockyard speed −25%.
* Dynamic modifier `bfx_covert_rearmament` cancels each penalty in proportion to `bfx_rearm` (100 = fully cancelled); recomputed by `bfx_neuilly_recalc`.
* Decisions (category *Shackles of Neuilly*; the panel shows both numbers and every threshold):
  Hidden Officer Schools (+10/+6), "Civilian" Flying Clubs (+8/+5, air XP), Škoda via Swiss fronts (+12/+8, 1,500 rifles),
  Rheinmetall via a Dutch shell company (+12/+9, 120 guns), Labour Service (+8/+4, manpower), Reassure the Capitals (−12 suspicion),
  Wine and Dine the League Observers (−20 suspicion). Several focuses also add rearmament and suspicion.
* Thresholds (each fires once): **25** notes of protest; **50** Greece/Yugoslavia/Turkey/Romania guarantee each other;
  **75** Balkan embargo (timed spirit); **100** Incident at Petrich (back down: −20 rearmament; or stand firm: crisis spirit and threat).
* Endings (each path differently): Salonika Agreement (negotiated: rearmament becomes army XP, the Entente is pleased);
  Tear Up Neuilly / Ferdinand burns the treaty (loud: embargo and border crisis); Communists denounce it in the Ninth of September;
  Agrarians revise it by League petition; Zveno rearms openly by decree (suspicion rises). All endings grant *Free of Neuilly*.

## Events (35)
`bfx.1–4, 10` opening and trade; `bfx_neuilly.10–13, 20, 21` mechanic; `bfx_tsar.10–12, 20, 21, 30, 40, 50` Tsardom
(Dobruja demand, Axis entry, Concord invitations, union offers, London); `bfx_alt.1–3` (Ferdinand's return, Hagia Sophia news, coronation);
`bfx_com.1, 10, 20` (Ninth of September, Comintern, Federation committee); `bfx_agr.1, 2, 10, 20` and `bfx_zveno.1`;
random flavour `bfx_flav.1–5` (rose harvest, tobacco strike, the Tsar drives the train, St Nedelya anniversary, Rila pilgrims),
each firing at most once (about 2% per month each).
Every option has a tooltip-visible effect, except the two narrative options of the Hagia Sophia news event.

## Decisions (54 in 6 categories)
Shackles of Neuilly (7); IMRO Operations in Macedonia (Tsardom, needs IMRO tolerated: raids build unrest to an Ilinden uprising war goal);
Partisan Support (Communist: arm partisans, order risings at 45%, integrate red neighbours for cores); Peasant Cooperatives and
Directives (Agrarian or Zveno variants); Tsargrad Propaganda (alt-history: imperial fervour, and *Restore the Theme* decisions coring Thrace and Hellas, Cherson, Ravenna, Dacia, Illyricum).

## AI
On startup an AI Bulgaria rolls its path once with `random_list`: Tsardom 75% (Axis 70%, Neutral 23%, Coburg 7%), Agrarian/Zveno 13%, Communist 12%.
Path and branch focuses weight on those flags, so the default is historical (Tsardom → Axis) with some variety, and no game rule is needed.

## Balance notes
Reference points: vanilla generic and BtB-era trees give about 2 factories per 70-day industry focus, 2–3 research slots
over a whole tree, and spirits of roughly ±10–15% per stat. This tree keeps to that: 1–2 buildings per industry focus;
research slots are capped at two per playthrough (Academy plus one path focus); the strongest spirits (Zveno Modernisation
Drive, Third Empire) pay for their bonuses with stability. Each Neuilly penalty is fully offset only at 100 rearmament,
which costs about 400–500 PP of decisions plus suspicion.

## National spirits (59)
| ID | Name | Modifiers |
|---|---|---|
| `bfx_imperial_mandate` | The Imperial Mandate | stability_factor +0.1, political_power_gain +0.1, compliance_growth +0.1, war_support_factor +0.05 |
| `bfx_neuilly_shackles` | Shackles of Neuilly | conscription_factor -0.3, army_org_factor -0.1, training_time_army_factor +0.25, air_accidents_factor +0.5, production_speed_dockyard_factor -0.25 |
| `bfx_balkan_embargo` | Balkan Embargo | local_resources_factor -0.1, consumer_goods_factor +0.03, stability_factor -0.03 |
| `bfx_border_crisis` | The Petrich Crisis | war_support_factor +0.1, stability_factor -0.1, army_attack_factor +0.05 |
| `bfx_salonika_freedom` | Free of Neuilly | training_time_army_factor -0.1, experience_gain_army_factor +0.1, stability_factor +0.03 |
| `bfx_imro_state_within_state` | IMRO: A State Within the State | stability_factor -0.05, political_power_factor -0.05 |
| `bfx_imro_crushed` | IMRO Broken | stability_factor +0.03, political_power_factor +0.05 |
| `bfx_imro_tolerated` | IMRO Tolerated | war_support_factor +0.05, stability_factor -0.03, justify_war_goal_time -0.1 |
| `bfx_imro_liberation_army` | The Macedonian Liberation Army | war_support_factor +0.08, justify_war_goal_time -0.2, army_attack_factor +0.03 |
| `bfx_military_league_intrigue` | The Military League | stability_factor -0.05, experience_gain_army_factor +0.05 |
| `bfx_army_loyal_to_crown` | An Army Loyal to the Crown | stability_factor +0.03, army_org_factor +0.03 |
| `bfx_zveno_officer_state` | The Officers' State | army_org_factor +0.05, stability_factor -0.05, political_power_gain +0.15 |
| `bfx_tobacco_monoculture` | Tobacco Monoculture | political_power_gain +0.05, stability_factor -0.02, research_speed_factor -0.03 |
| `bfx_tobacco_and_rose_exports` | Tobacco and Rose Exports | political_power_gain +0.1, consumer_goods_factor -0.02, stability_factor +0.02 |
| `bfx_valley_of_roses` | The Valley of Roses | political_power_gain +0.15, consumer_goods_factor -0.04, stability_factor +0.05 |
| `bfx_german_clearing` | The German Clearing Account | industrial_capacity_factory +0.05, production_speed_buildings_factor +0.1, fascism_drift +0.03 |
| `bfx_german_clearing_deep` | Bound to Berlin | industrial_capacity_factory +0.08, production_speed_buildings_factor +0.1, research_speed_factor +0.03, fascism_drift +0.05, stability_factor -0.03 |
| `bfx_diversified_trade` | Many Buyers | research_speed_factor +0.03, stability_factor +0.05 |
| `bfx_open_markets` | Open Markets | research_speed_factor +0.04, stability_factor +0.05, production_speed_buildings_factor +0.05, trade_opinion_factor +0.2 |
| `bfx_partyless_regime` | A Kingdom Without Parties | political_power_gain +0.1, democratic_drift -0.02, communism_drift -0.02, stability_factor -0.03 |
| `bfx_tsars_personal_regime` | The Tsar's Personal Regime | political_power_gain +0.15, stability_factor +0.05, drift_defence_factor +0.15 |
| `bfx_tsar_unifier` | Tsar Unifier | political_power_gain +0.15, war_support_factor +0.1, justify_war_goal_time -0.25, stability_factor +0.05 |
| `bfx_san_stefano_irredentism` | The San Stefano Dream | war_support_factor +0.1, justify_war_goal_time -0.15 |
| `bfx_balkan_switzerland` | The Balkan Switzerland | army_core_defence_factor +0.1, enemy_justify_war_goal_time +0.5, stability_factor +0.1, political_power_gain +0.1, drift_defence_factor +0.2 |
| `bfx_straits_doorman` | Doorman of the Straits | naval_coordination +0.1, opinion_gain_monthly_factor +0.15 |
| `bfx_red_underground` | The Red Underground | communism_drift +0.03, stability_factor -0.05 |
| `bfx_fatherland_front_council` | The Fatherland Front | communism_drift +0.05, war_support_factor +0.05, political_power_gain +0.1 |
| `bfx_peoples_republic` | People's Republic of Bulgaria | stability_factor +0.05, political_power_gain +0.15, production_factory_efficiency_gain_factor +0.05, consumer_goods_factor -0.03 |
| `bfx_tkzs` | Labour-Cooperative Farms | conscription_factor +0.1, production_speed_buildings_factor +0.1, stability_factor -0.03 |
| `bfx_balkan_federation_spirit` | The Balkan Federation Idea | justify_war_goal_time -0.25, war_support_factor +0.1, political_power_gain +0.1 |
| `bfx_agrarian_union` | The Agrarian Union | stability_factor +0.05, democratic_drift +0.03 |
| `bfx_orange_guard` | The Orange Guard | stability_factor +0.05, democratic_drift +0.03, conscription_factor +0.1 |
| `bfx_green_international` | The Green International | stability_factor +0.1, opinion_gain_monthly_factor +0.2, trade_opinion_factor +0.2, political_power_gain +0.1, conscription_factor +0.1 |
| `bfx_agrarian_democracy` | Agrarian Democracy | stability_factor +0.08, political_power_gain +0.1, consumer_goods_factor -0.02 |
| `bfx_peasant_cooperatives` | Peasant Cooperatives | consumer_goods_factor -0.03, monthly_population +0.1, stability_factor +0.03 |
| `bfx_zveno_technocracy` | Zveno Technocracy | research_speed_factor +0.05, production_speed_buildings_factor +0.1, stability_factor -0.1 |
| `bfx_zveno_modernisation_drive` | The Modernisation Drive | research_speed_factor +0.07, production_speed_buildings_factor +0.15, industrial_capacity_factory +0.05, stability_factor -0.08, war_support_factor +0.05 |
| `bfx_prussia_of_the_balkans` | Prussia of the Balkans | army_org_factor +0.05, army_morale_factor +0.05, justify_war_goal_time -0.2, experience_gain_army_factor +0.1 |
| `bfx_ferdinand_restoration` | The Coburg Restoration | political_power_gain +0.2, war_support_factor +0.15, stability_factor -0.1 |
| `bfx_third_empire_zeal` | The Third Empire | political_power_gain +0.2, war_support_factor +0.2, justify_war_goal_time -0.3, army_morale_factor +0.05, stability_factor -0.05 |
| `bfx_byzantine_pretension` | Basileus of the Romans and Bulgars | war_support_factor +0.1, justify_war_goal_time -0.25, annex_cost_factor -0.2, stability_factor +0.05 |
| `bfx_royal_natural_history_institute` | Royal Natural History Institute | research_speed_factor +0.04 |
| `bfx_pernik_coal_works` | Pernik Coal Works | production_speed_buildings_factor +0.05, local_resources_factor +0.05 |
| `bfx_pernik_coal_works_2` | Coal and Iron of the Balkan Range | production_speed_buildings_factor +0.1, local_resources_factor +0.1 |
| `bfx_railway_age` | The Railway Age | production_speed_infrastructure_factor +0.25 |
| `bfx_railway_age_2` | The Main Lines | production_speed_infrastructure_factor +0.25, supply_consumption_factor -0.05 |
| `bfx_iskar_hydro` | Iskar Hydroelectric Scheme | production_factory_efficiency_gain_factor +0.1 |
| `bfx_trudovaks` | The Labour Service | production_speed_buildings_factor +0.1, conscription_factor +0.05 |
| `bfx_open_conscription` | Universal Service | conscription_factor +0.1, training_time_army_factor -0.05 |
| `bfx_mountain_army` | Rhodope Rangers | special_forces_cap +0.15, army_defence_factor +0.03 |
| `bfx_balkan_mountain_doctrine` | Balkan Mountain Doctrine | special_forces_cap +0.25, army_defence_factor +0.05, army_attack_factor +0.03, terrain_penalty_reduction +0.1 |
| `bfx_black_sea_flotilla` | The Black Sea Flotilla | experience_gain_navy_factor +0.15, navy_org_factor +0.05 |
| `bfx_black_sea_fleet` | The Black Sea Squadrons | experience_gain_navy_factor +0.15, navy_org_factor +0.1, production_speed_dockyard_factor +0.1, naval_coordination +0.05 |
| `bfx_black_sea_raiders` | Black Sea Raiders | convoy_raiding_efficiency_factor +0.15, naval_strike_attack_factor +0.1 |
| `bfx_clandestine_aviation` | Clandestine Aviation | experience_gain_air_factor +0.1, air_training_xp_gain_factor +0.1 |
| `bfx_vazdushni_voyski` | His Majesty's Air Force | experience_gain_air_factor +0.1, air_superiority_efficiency +0.05, production_speed_air_base_factor +0.25, air_accidents_factor -0.2 |
| `bfx_foreign_air_instructors` | Foreign Flight Instructors | air_training_xp_gain_factor +0.15, air_ace_generation_chance_factor +0.2 |
| `bfx_sofia_air_defence` | Sofia Fighter Command | air_superiority_efficiency +0.05 |
| `bfx_wings_over_the_mountains` | Wings over the Mountains | air_mission_efficiency +0.05, air_training_xp_gain_factor +0.1 |

## Characters (15, all new `bfx_` characters)
| ID | Name | Roles | Biography (checked) |
|---|---|---|---|
| `bfx_BUL_boris_iii` | Boris III | leader | Tsar 1918–1943; personal regime from 1935; died Aug 1943 after meeting Hitler. |
| `bfx_BUL_ferdinand_i` | Ferdinand I | leader | Prince 1887, Tsar 1908–1918; abdicated after WWI, lived in Coburg until 1948; noted botanist and entomologist. |
| `bfx_BUL_georgi_dimitrov` | Georgi Dimitrov | leader | Defended himself against Göring at the 1933 Leipzig trial; Comintern General Secretary 1935–1943; PM 1946–1949. |
| `bfx_BUL_vasil_kolarov` | Vasil Kolarov | leader | Comintern Secretary-General 1922–1924, Balkan Communist Federation figure; head of state 1946–47, PM 1949–50. |
| `bfx_BUL_nikola_petkov` | Nikola Petkov | leader | Leader of the BANU-Pladne Agrarians; Fatherland Front co-founder; executed by the communists in 1947. |
| `bfx_BUL_kimon_georgiev` | Kimon Georgiev | leader | Zveno leader; PM after the 19 May 1934 coup and again 1944–1946. |
| `bfx_BUL_bogdan_filov` | Bogdan Filov | advisor | Archaeologist; PM 1940–1943, signed the Tripartite Pact; regent 1943–44; executed 1945. |
| `bfx_BUL_georgi_kyoseivanov` | Georgi Kyoseivanov | advisor | Diplomat; PM 1935–1940; signed the 1937 pact with Yugoslavia and the 1938 Salonika Agreement. |
| `bfx_BUL_nikola_mushanov` | Nikola Mushanov | advisor | Democratic Party leader; PM 1931–1934; opposition voice under the personal regime. |
| `bfx_BUL_anton_yugov` | Anton Yugov | advisor | Communist organiser; Interior Minister 1944–1949; PM 1956–1962. |
| `bfx_BUL_konstantin_muraviev` | Konstantin Muraviev | advisor | Agrarian politician and nephew of Aleksandar Stamboliyski; PM for one week in September 1944. |
| `bfx_BUL_ivan_mihaylov` | Ivan Mihaylov | advisor | IMRO leader 1924–1934; fled after the Zveno crackdown; died in Rome in 1990. |
| `bfx_BUL_nikola_zhekov` | Nikola Zhekov | field_marshal | Commander-in-chief 1915–1918; War Minister 1918; pro-German; died in exile 1949. |
| `bfx_BUL_hristo_lukov` | Hristo Lukov | corps_commander | War Minister 1935–1938; led the Union of Bulgarian National Legions; assassinated 1943. |
| `bfx_BUL_vladimir_zaimov` | Vladimir Zaimov | corps_commander | General, Zveno and Military League member; Soviet intelligence agent; executed 1942. |

## Full focus list
| ID | Name | x,y | Prerequisites | Exclusive with | Reward (one line) |
|---|---|---|---|---|---|
| `bfx_tsars_dilemma` | The Tsar's Dilemma | 42,0 | — | — | country_event = bfx.1, unlock_decision_category_tooltip = bfx_neuilly_category |
| `bfx_velchev_trial` | The Velchev Trial | 34,1 | bfx_tsars_dilemma | — | country_event = bfx.2 |
| `bfx_neuilly_ledger` | The Neuilly Ledger | 38,1 | bfx_tsars_dilemma | — | unlock_decision_category_tooltip = bfx_neuilly_category, custom_effect_tooltip = bfx_tt_neuilly_r10_s4, add_to_variable = { bfx_rearm = 10 } |
| `bfx_eternal_friendship` | Eternal Friendship with Belgrade | 44,1 | bfx_tsars_dilemma | — | custom_effect_tooltip = bfx_tt_neuilly_r0_sm15, add_to_variable = { bfx_suspicion = -15 }, bfx_neuilly_recalc = yes |
| `bfx_macedonian_question` | The Macedonian Question | 50,1 | bfx_tsars_dilemma | — | add_political_power = 25, recruit_character = bfx_BUL_ivan_mihaylov |
| `bfx_kingdom_without_parties` | A Kingdom Without Parties | 34,2 | bfx_velchev_trial | — | add_ideas = bfx_partyless_regime |
| `bfx_war_ministry_cellars` | Cellars of the War Ministry | 38,2 | bfx_neuilly_ledger | — | set_country_flag = bfx_arms_fronts_open, custom_effect_tooltip = bfx_tt_arms_fronts, custom_effect_tooltip = bfx_tt_neuilly_r6_s3, add_to_va |
| `bfx_kyoseivanov_cabinet` | The Kyoseivanov Cabinet | 44,2 | bfx_eternal_friendship | — | recruit_character = bfx_BUL_georgi_kyoseivanov, add_stability = 0.03, custom_effect_tooltip = bfx_tt_neuilly_r0_sm5, add_to_variable = { bfx |
| `bfx_crush_imro` | Crush IMRO | 48,2 | bfx_macedonian_question | bfx_tolerate_imro | set_country_flag = bfx_imro_crushed, custom_effect_tooltip = bfx_tt_neuilly_r0_sm10, add_to_variable = { bfx_suspicion = -10 }, bfx_neuilly_ |
| `bfx_tolerate_imro` | Tolerate IMRO | 52,2 | bfx_macedonian_question | bfx_crush_imro | set_country_flag = bfx_imro_tolerated, unlock_decision_category_tooltip = bfx_imro_category, custom_effect_tooltip = bfx_tt_neuilly_r0_s10,  |
| `bfx_elections_of_1938` | The Partyless Elections of 1938 | 34,3 | bfx_kingdom_without_parties | — | country_event = bfx.3 |
| `bfx_salonika_agreement` | The Salonika Agreement | 42,3 | bfx_kyoseivanov_cabinet | bfx_tear_up_neuilly | bfx_end_neuilly_negotiated = yes |
| `bfx_tear_up_neuilly` | Tear Up Neuilly | 46,3 | bfx_war_ministry_cellars | bfx_salonika_agreement | bfx_end_neuilly_torn = yes |
| `bfx_shadow_parties` | The Shadow Parties | 50,3 | bfx_crush_imro or bfx_tolerate_imro | — | country_event = bfx.4 |
| `bfx_hour_of_decision` | The Hour of Decision | 38,4 | bfx_elections_of_1938; bfx_shadow_parties | — | add_political_power = 50, custom_effect_tooltip = bfx_tt_hour_of_decision |
| `bfx_tsar_steps_forward` | The Tsar Steps Forward | 20,5 | bfx_hour_of_decision | bfx_com_workers_party, bfx_agr_union_stirs | retire_country_leader = yes, recruit_character = bfx_BUL_boris_iii, promote_character = bfx_BUL_boris_iii, add_stability = 0.05 |
| `bfx_tsar_muzzle_the_league` | Muzzle the Military League | 20,6 | bfx_tsar_steps_forward | — | recruit_character = bfx_BUL_nikola_zhekov |
| `bfx_tsar_san_stefano_dream` | The San Stefano Dream | 16,7 | bfx_tsar_muzzle_the_league | bfx_tsar_balkan_switzerland, bfx_alt_old_fox_stirs | add_ideas = bfx_san_stefano_irredentism, recruit_character = bfx_BUL_bogdan_filov |
| `bfx_tsar_filov_cabinet` | The Filov Cabinet | 14,8 | bfx_tsar_san_stefano_dream | — | add_popularity = { ideology = fascism popularity = 0.10 } |
| `bfx_tsar_southern_dobruja` | Southern Dobruja | 18,8 | bfx_tsar_san_stefano_dream | — | add_state_claim = 77, ROM = { country_event = { id = bfx_tsar.10 days = 3 } }, custom_effect_tooltip = bfx_tt_dobruja_demand |
| `bfx_tsar_seek_the_pact` | Seek the Tripartite Pact | 14,9 | bfx_tsar_filov_cabinet | — | GER = { country_event = { id = bfx_tsar.20 days = 2 } }, custom_effect_tooltip = bfx_tt_seek_pact |
| `bfx_tsar_vardar_macedonia` | Liberate Vardar Macedonia | 16,10 | bfx_tsar_seek_the_pact; bfx_tsar_southern_dobruja | — | add_state_claim = 106, 106 = { owner = { save_event_target_as = bfx_wg_target } }, create_wargoal = { type = take_state_focus target = event |
| `bfx_tsar_aegean_outlet` | An Outlet to the Aegean | 20,9 | bfx_tsar_southern_dobruja | — | add_state_claim = 184, 184 = { owner = { save_event_target_as = bfx_wg_target } }, create_wargoal = { type = take_state_focus target = event |
| `bfx_tsar_san_stefano_restored` | San Stefano Restored | 18,11 | bfx_tsar_vardar_macedonia; bfx_tsar_aegean_outlet | — | set_country_flag = bfx_imperial_integration, unlock_decision_category_tooltip = bfx_integration_category |
| `bfx_tsar_three_seas` | Bulgaria on Three Seas | 18,12 | bfx_tsar_san_stefano_restored | — | add_claim_by = ROOT, add_state_claim = 731, add_state_claim = 341, add_core_of = ROOT, set_cosmetic_tag = bfx_greater_bulgaria, add_war_supp |
| `bfx_tsar_balkan_switzerland` | The Balkan Switzerland | 24,7 | bfx_tsar_muzzle_the_league | bfx_tsar_san_stefano_dream, bfx_alt_old_fox_stirs | add_ideas = bfx_balkan_switzerland, recruit_character = bfx_BUL_nikola_mushanov |
| `bfx_tsar_armed_neutrality` | The Armed Neutrality Doctrine | 22,8 | bfx_tsar_balkan_switzerland | — | add_building_construction = { type = bunker level = 1 instant_build = yes province = { all_provinces = yes limit_to_border = yes } }, army_e |
| `bfx_tsar_court_the_entente` | Court the Balkan Entente | 26,8 | bfx_tsar_balkan_switzerland | — | add_opinion_modifier = { target = ROOT modifier = bfx_om_balkan_courtship }, custom_effect_tooltip = bfx_tt_neuilly_r0_sm25, add_to_variable |
| `bfx_tsar_city_loans` | Loans from the City | 22,9 | bfx_tsar_armed_neutrality | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes }, add_extr |
| `bfx_tsar_balkan_concord` | The Balkan Concord | 26,9 | bfx_tsar_court_the_entente | — | country_event = { id = bfx_tsar.30 days = 2 }, custom_effect_tooltip = bfx_tt_concord, set_country_flag = bfx_imperial_integration, unlock_d |
| `bfx_tsar_guardian_of_straits` | Guardian of the Straits | 24,10 | bfx_tsar_city_loans; bfx_tsar_balkan_concord | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = dockyard level = 1 instant_build = yes }, navy_experience =  |
| `bfx_tsar_allied_alignment` | Lean towards London | 22,11 | bfx_tsar_guardian_of_straits | bfx_tsar_third_way | ENG = { country_event = { id = bfx_tsar.50 days = 2 } }, custom_effect_tooltip = bfx_tt_allied |
| `bfx_tsar_third_way` | The Third Way | 26,11 | bfx_tsar_guardian_of_straits | bfx_tsar_allied_alignment | add_research_slot = 1, add_stability = 0.05 |
| `bfx_tsar_danubian_confederation` | The Danubian-Balkan Confederation | 24,12 | bfx_tsar_allied_alignment or bfx_tsar_third_way | — | country_event = { id = bfx_tsar.40 days = 3 }, set_cosmetic_tag = bfx_balkan_confederation, add_stability = 0.05, custom_effect_tooltip = bf |
| `bfx_alt_old_fox_stirs` | The Old Fox Stirs in Coburg | 34,7 | bfx_tsar_muzzle_the_league | bfx_tsar_san_stefano_dream, bfx_tsar_balkan_switzerland | country_event = bfx_alt.1 |
| `bfx_alt_burn_the_treaty` | Burn the Treaty on the Steps of Neuilly | 34,8 | bfx_alt_old_fox_stirs | — |  |
| `bfx_alt_entomologist_tsar` | The Entomologist Tsar | 38,8 | bfx_alt_old_fox_stirs | — | add_ideas = bfx_royal_natural_history_institute |
| `bfx_alt_imperial_life_guard` | The Imperial Life Guard | 34,9 | bfx_alt_burn_the_treaty | — | army_experience = 25, add_equipment_to_stockpile = { type = infantry_equipment amount = 2000 }, add_manpower = 10000 |
| `bfx_alt_coburg_capital` | Coburg Capital | 38,9 | bfx_alt_entomologist_tsar | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes }, add_extr |
| `bfx_alt_third_empire` | Proclaim the Third Bulgarian Empire | 30,10 | bfx_alt_imperial_life_guard | bfx_alt_tsargrad | add_ideas = bfx_third_empire_zeal, set_cosmetic_tag = bfx_third_empire, add_state_claim = 77, add_state_claim = 106, add_state_claim = 184,  |
| `bfx_alt_simeons_borders` | The Borders of Simeon the Great | 30,11 | bfx_alt_third_empire | — | add_claim_by = ROOT, add_state_claim = 77, add_state_claim = 971, add_war_support = 0.05 |
| `bfx_alt_tsar_of_the_vlachs` | Tsar of Bulgarians and Vlachs | 32,12 | bfx_alt_simeons_borders | — | add_claim_by = ROOT |
| `bfx_alt_coronation_at_tarnovo` | Coronation at Tarnovo | 32,13 | bfx_alt_tsar_of_the_vlachs | — | add_stability = 0.10, add_political_power = 100, country_event = bfx_alt.3, add_core_of = ROOT |
| `bfx_alt_old_great_bulgaria` | Old Great Bulgaria | 30,13 | bfx_alt_simeons_borders | — | add_claim_by = ROOT, add_war_support = 0.05 |
| `bfx_alt_asparuhs_homecoming` | Asparuh's Homecoming | 30,14 | bfx_alt_old_great_bulgaria | — | add_core_of = ROOT, set_cosmetic_tag = bfx_old_great_bulgaria, army_experience = 30 |
| `bfx_alt_tsargrad` | Tsargrad! | 38,10 | bfx_alt_imperial_life_guard | bfx_alt_third_empire | add_ideas = bfx_byzantine_pretension, add_state_claim = 797, add_state_claim = 341, 797 = { owner = { save_event_target_as = bfx_wg_target } |
| `bfx_alt_basileus` | Basileus of the Romans and Bulgars | 38,11 | bfx_alt_tsargrad | — | add_claim_by = ROOT, add_political_power = 50 |
| `bfx_alt_hagia_sophia` | Mass in Hagia Sophia | 36,12 | bfx_alt_basileus | — | set_cosmetic_tag = bfx_byzantium, add_stability = 0.15, news_event = { id = bfx_alt.2 days = 1 } |
| `bfx_alt_restore_the_themes` | Restore the Themes | 38,13 | bfx_alt_hagia_sophia | — | add_claim_by = ROOT, add_core_of = ROOT |
| `bfx_alt_exarchate_of_ravenna` | The Exarchate of Ravenna | 38,14 | bfx_alt_restore_the_themes | — | add_claim_by = ROOT, add_core_of = ROOT |
| `bfx_com_workers_party` | Unchain the Workers' Party | 52,5 | bfx_hour_of_decision | bfx_tsar_steps_forward, bfx_agr_union_stirs | add_ideas = bfx_red_underground, add_popularity = { ideology = communism popularity = 0.15 }, recruit_character = bfx_BUL_anton_yugov |
| `bfx_com_fatherland_front` | The Fatherland Front | 52,6 | bfx_com_workers_party | — | add_popularity = { ideology = communism popularity = 0.10 }, unlock_decision_category_tooltip = bfx_partisan_category |
| `bfx_com_ninth_of_september` | The Ninth of September | 52,7 | bfx_com_fatherland_front | — | country_event = bfx_com.1 |
| `bfx_com_dimitrov_comes_home` | Dimitrov Comes Home | 48,8 | bfx_com_ninth_of_september | bfx_com_kolarovs_federation | recruit_character = bfx_BUL_georgi_dimitrov, promote_character = bfx_BUL_georgi_dimitrov |
| `bfx_com_soviet_advisers` | Soviet Military Advisers | 46,9 | bfx_com_dimitrov_comes_home | — | army_experience = 25, recruit_character = bfx_BUL_vladimir_zaimov, add_tech_bonus = { name = bfx_com_soviet_advisers bonus = 0.5 uses = 1 ca |
| `bfx_com_tkzs` | Collectivise the Villages | 50,9 | bfx_com_dimitrov_comes_home | — | add_ideas = bfx_tkzs, add_stability = -0.05 |
| `bfx_com_join_comintern` | Join the Comintern | 46,10 | bfx_com_soviet_advisers | — | custom_effect_tooltip = bfx_tt_comintern |
| `bfx_com_heavy_industry` | Steel for the Five-Year Plan | 50,10 | bfx_com_tkzs | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = arms_factory level = 1 instant_build = yes }, add_extra_stat |
| `bfx_com_straits_for_moscow` | The Straits for Moscow | 46,11 | bfx_com_join_comintern | — | add_state_claim = 341, add_state_claim = 797, 341 = { owner = { save_event_target_as = bfx_wg_target } }, create_wargoal = { type = take_sta |
| `bfx_com_red_black_sea` | A Red Black Sea | 48,12 | bfx_com_straits_for_moscow; bfx_com_heavy_industry | — | add_state_claim = 77, add_state_claim = 971, add_extra_state_shared_building_slots = 1, add_building_construction = { type = dockyard level  |
| `bfx_com_kolarovs_federation` | Kolarov's Federation | 56,8 | bfx_com_ninth_of_september | bfx_com_dimitrov_comes_home | recruit_character = bfx_BUL_vasil_kolarov, promote_character = bfx_BUL_vasil_kolarov, country_event = bfx_com.20 |
| `bfx_com_yugoslav_partisans` | Arms for the Yugoslav Partisans | 54,9 | bfx_com_kolarovs_federation | — | set_country_flag = bfx_partisans_west, custom_effect_tooltip = bfx_tt_partisans_west |
| `bfx_com_greek_comrades` | Contact the Greek Comrades | 58,9 | bfx_com_kolarovs_federation | — | set_country_flag = bfx_partisans_south, custom_effect_tooltip = bfx_tt_partisans_south |
| `bfx_com_independent_line` | An Independent Line | 56,10 | bfx_com_yugoslav_partisans; bfx_com_greek_comrades | — | add_research_slot = 1, add_stability = 0.05 |
| `bfx_com_balkan_federation` | Proclaim the Balkan Federation | 56,11 | bfx_com_independent_line | — | add_claim_by = ROOT, set_cosmetic_tag = bfx_balkan_federation, set_country_flag = bfx_federation_proclaimed, custom_effect_tooltip = bfx_tt_ |
| `bfx_com_danube_to_aegean` | From the Danube to the Aegean | 54,12 | bfx_com_balkan_federation | — | add_core_of = ROOT |
| `bfx_com_carpathian_soviets` | Carpathian Soviets | 58,12 | bfx_com_balkan_federation | — | add_claim_by = ROOT |
| `bfx_com_red_danubia` | The Red Danubian Federation | 56,13 | bfx_com_danube_to_aegean; bfx_com_carpathian_soviets | — | add_core_of = ROOT, set_cosmetic_tag = bfx_red_danubia, set_country_flag = bfx_red_danubia, add_war_support = 0.10 |
| `bfx_agr_union_stirs` | The Union Stirs Again | 68,5 | bfx_hour_of_decision | bfx_tsar_steps_forward, bfx_com_workers_party | add_ideas = bfx_agrarian_union, add_popularity = { ideology = democratic popularity = 0.10 }, recruit_character = bfx_BUL_konstantin_muravie |
| `bfx_agr_second_19_may` | A Second 19th of May | 68,6 | bfx_agr_union_stirs | — | country_event = bfx_agr.1 |
| `bfx_agr_stamboliyskis_heirs` | Stamboliyski's Heirs | 64,7 | bfx_agr_second_19_may | bfx_zveno_takes_the_helm | set_politics = { ruling_party = democratic elections_allowed = yes }, recruit_character = bfx_BUL_nikola_petkov, promote_character = bfx_BUL |
| `bfx_agr_land_to_the_tiller` | Land to the Tiller | 62,8 | bfx_agr_stamboliyskis_heirs | — | add_ideas = bfx_peasant_cooperatives, unlock_decision_category_tooltip = bfx_cooperative_category |
| `bfx_agr_orange_guard` | Revive the Orange Guard | 66,8 | bfx_agr_stamboliyskis_heirs | — |  |
| `bfx_agr_cooperative_banks` | Cooperative Banks | 62,9 | bfx_agr_land_to_the_tiller | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes }, add_extr |
| `bfx_agr_referendum` | Referendum on the Crown | 66,9 | bfx_agr_orange_guard | — | country_event = bfx_agr.2 |
| `bfx_agr_green_international` | The Green International | 64,10 | bfx_agr_cooperative_banks; bfx_agr_referendum | — | country_event = { id = bfx_agr.10 days = 2 }, custom_effect_tooltip = bfx_tt_green_int, set_country_flag = bfx_imperial_integration, unlock_ |
| `bfx_agr_balkan_peasant_union` | The Balkan Peasant Union | 64,11 | bfx_agr_green_international | — | country_event = { id = bfx_agr.20 days = 3 }, set_cosmetic_tag = bfx_peasant_union, custom_effect_tooltip = bfx_tt_peasant_union |
| `bfx_agr_baltic_to_aegean` | From the Baltic to the Aegean | 64,12 | bfx_agr_balkan_peasant_union | — | country_event = { id = bfx_agr.20 days = 3 }, add_war_support = 0.10 |
| `bfx_zveno_takes_the_helm` | Zveno Takes the Helm | 72,7 | bfx_agr_second_19_may | bfx_agr_stamboliyskis_heirs | recruit_character = bfx_BUL_kimon_georgiev, promote_character = bfx_BUL_kimon_georgiev, add_ideas = bfx_zveno_technocracy, bfx_end_neuilly_o |
| `bfx_zveno_abolish_parties` | Abolish the Parties, Again | 70,8 | bfx_zveno_takes_the_helm | — | add_political_power = 120, add_stability = -0.05, set_politics = { ruling_party = neutrality elections_allowed = no } |
| `bfx_zveno_officers_take_ministries` | The Officers' State | 74,8 | bfx_zveno_takes_the_helm | — | recruit_character = bfx_BUL_vladimir_zaimov, recruit_character = bfx_BUL_hristo_lukov, country_event = bfx_zveno.1 |
| `bfx_zveno_five_year_plan` | The Technocrats' Plan | 70,9 | bfx_zveno_abolish_parties | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes }, add_extr |
| `bfx_zveno_state_monopolies` | State Monopolies | 74,9 | bfx_zveno_officers_take_ministries | — | add_political_power = 75, add_extra_state_shared_building_slots = 1, add_building_construction = { type = arms_factory level = 1 instant_bui |
| `bfx_zveno_prussia_of_the_balkans` | The Prussia of the Balkans | 72,10 | bfx_zveno_five_year_plan; bfx_zveno_state_monopolies | — | add_ideas = bfx_prussia_of_the_balkans, army_experience = 25 |
| `bfx_zveno_officers_balkans` | An Officers' Balkans | 72,11 | bfx_zveno_prussia_of_the_balkans | — | add_state_claim = 106, add_state_claim = 184, add_state_claim = 77, 106 = { owner = { save_event_target_as = bfx_wg_target } }, create_wargo |
| `bfx_zveno_anatolian_gambit` | The Anatolian Gambit | 72,12 | bfx_zveno_officers_balkans | — | add_claim_by = ROOT, add_core_of = ROOT, set_cosmetic_tag = bfx_balkan_military_union |
| `bfx_eco_rose_and_leaf` | The Rose and the Leaf | 84,0 | — | — | add_political_power = 30, custom_effect_tooltip = bfx_tt_rose_leaf, set_country_flag = bfx_trade_question |
| `bfx_eco_german_clearing` | The German Clearing Account | 80,1 | bfx_eco_rose_and_leaf | bfx_eco_diversify | add_ideas = bfx_german_clearing |
| `bfx_eco_diversify` | Diversify the Buyers | 88,1 | bfx_eco_rose_and_leaf | bfx_eco_german_clearing | add_ideas = bfx_diversified_trade |
| `bfx_eco_tobacco_boom` | The Plovdiv Tobacco Boom | 80,2 | bfx_eco_german_clearing or bfx_eco_diversify | — |  |
| `bfx_eco_valley_of_roses` | The Valley of Roses | 80,3 | bfx_eco_tobacco_boom | — |  |
| `bfx_eco_hard_currency` | Hard Currency for Machines | 80,4 | bfx_eco_valley_of_roses | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes }, add_extr |
| `bfx_eco_ledger_of_trade` | The Ledger of Trade | 80,5 | bfx_eco_hard_currency | — | country_event = bfx.10 |
| `bfx_eco_plovdiv_fair` | The Plovdiv International Fair | 80,6 | bfx_eco_ledger_of_trade | — | add_tech_bonus = { name = bfx_eco_plovdiv_fair bonus = 0.5 uses = 2 category = industry }, add_tech_bonus = { name = bfx_eco_plovdiv_fair_e  |
| `bfx_eco_pernik_coal` | Pernik Coal | 84,2 | bfx_eco_rose_and_leaf | — | add_ideas = bfx_pernik_coal_works, capital_scope = { add_resource = { type = steel amount = 4 } } |
| `bfx_eco_balkan_iron` | Iron from the Balkan Range | 84,3 | bfx_eco_pernik_coal | — | capital_scope = { add_resource = { type = steel amount = 4 } }, add_extra_state_shared_building_slots = 1, add_building_construction = { typ |
| `bfx_eco_kazanlak_arsenal` | The Kazanlak State Arsenal | 84,4 | bfx_eco_balkan_iron | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = arms_factory level = 1 instant_build = yes }, add_extra_stat |
| `bfx_eco_sofia_ring` | The Sofia Industrial Ring | 84,5 | bfx_eco_kazanlak_arsenal | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes }, add_extr |
| `bfx_eco_academy_of_sciences` | The Academy of Sciences | 84,6 | bfx_eco_sofia_ring | — | add_research_slot = 1 |
| `bfx_eco_bdz` | Modernise the BDŽ | 90,2 | bfx_eco_rose_and_leaf | — | add_building_construction = { type = infrastructure level = 1 instant_build = yes }, add_ideas = bfx_railway_age |
| `bfx_eco_main_line` | The Sofia–Varna Main Line | 90,3 | bfx_eco_bdz | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_build = yes } |
| `bfx_eco_iskar_dams` | Dams on the Iskar | 88,4 | bfx_eco_main_line | — | add_ideas = bfx_iskar_hydro, add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 in |
| `bfx_eco_black_sea_ports` | Ports of Varna and Burgas | 92,4 | bfx_eco_main_line | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = dockyard level = 2 instant_build = yes }, add_tech_bonus = { |
| `bfx_eco_petroleum` | Petroleum Prospects | 88,5 | bfx_eco_iskar_dams | — |  |
| `bfx_eco_labour_brigades` | The Labour Service Brigades | 92,5 | bfx_eco_black_sea_ports | — | add_ideas = bfx_trudovaks, custom_effect_tooltip = bfx_tt_neuilly_r6_s2, add_to_variable = { bfx_rearm = 6 } add_to_variable = { bfx_suspici |
| `bfx_eco_national_bank` | Reform the National Bank | 90,6 | bfx_eco_petroleum; bfx_eco_labour_brigades | — | add_stability = 0.05, add_extra_state_shared_building_slots = 1, add_building_construction = { type = industrial_complex level = 1 instant_b |
| `bfx_mil_neuilly_army` | The Army Neuilly Built | 104,0 | — | — | army_experience = 10, custom_effect_tooltip = bfx_tt_neuilly_r5_s2, add_to_variable = { bfx_rearm = 5 } add_to_variable = { bfx_suspicion =  |
| `bfx_mil_rhodope_rangers` | Rhodope Rangers | 100,1 | bfx_mil_neuilly_army | — | add_ideas = bfx_mountain_army, add_tech_bonus = { name = bfx_mil_rhodope_rangers bonus = 0.75 uses = 1 category = mountaineers_tech } |
| `bfx_mil_balkan_war_lessons` | Lessons of Chataldzha | 104,1 | bfx_mil_neuilly_army | — | add_mastery_bonus = { bonus = 0.25 days = 365 name = bfx_mil_balkan_war_lessons folder = land }, army_experience = 15 |
| `bfx_mil_mountain_doctrine` | Balkan Mountain Doctrine | 100,2 | bfx_mil_rhodope_rangers | — |  |
| `bfx_mil_artillery_parks` | The Artillery Parks | 104,2 | bfx_mil_balkan_war_lessons | — | add_tech_bonus = { name = bfx_mil_artillery_parks bonus = 0.5 uses = 2 category = artillery } |
| `bfx_mil_staff_academy` | The General Staff Academy | 102,3 | bfx_mil_mountain_doctrine; bfx_mil_artillery_parks | — | army_experience = 20, recruit_character = bfx_BUL_hristo_lukov |
| `bfx_mil_universal_service` | Universal Service, Openly | 100,4 | bfx_mil_staff_academy | — | add_manpower = 25000, add_ideas = bfx_open_conscription |
| `bfx_mil_fortify_the_passes` | Fortify the Passes | 104,4 | bfx_mil_staff_academy | — | add_building_construction = { type = bunker level = 2 instant_build = yes province = { all_provinces = yes limit_to_border = yes } } |
| `bfx_mil_motorised_brigade` | The Motorised Brigade | 102,5 | bfx_mil_universal_service or bfx_mil_fortify_the_passes | — | add_tech_bonus = { name = bfx_mil_motorised_brigade bonus = 0.5 uses = 1 category = motorized_equipment }, add_tech_bonus = { name = bfx_mil |
| `bfx_nav_black_sea_flotilla` | The Black Sea Flotilla | 108,1 | bfx_mil_neuilly_army | — | add_ideas = bfx_black_sea_flotilla, navy_experience = 10 |
| `bfx_nav_varna_naval_school` | The Varna Naval School | 108,2 | bfx_nav_black_sea_flotilla | — | navy_experience = 15, add_extra_state_shared_building_slots = 1, add_building_construction = { type = dockyard level = 1 instant_build = yes |
| `bfx_nav_torpedo_squadrons` | Torpedo Boat Squadrons | 106,3 | bfx_nav_varna_naval_school | — | custom_effect_tooltip = bfx_tt_neuilly_r4_s3, add_to_variable = { bfx_rearm = 4 } add_to_variable = { bfx_suspicion = 3 }, bfx_neuilly_recal |
| `bfx_nav_coastal_batteries` | Coastal Batteries at Galata | 110,3 | bfx_nav_varna_naval_school | — | add_building_construction = { type = coastal_bunker level = 2 instant_build = yes province = { all_provinces = yes limit_to_coastal = yes }  |
| `bfx_nav_black_sea_raiders` | Black Sea Raiders | 108,4 | bfx_nav_torpedo_squadrons; bfx_nav_coastal_batteries | — | add_ideas = bfx_black_sea_raiders, navy_experience = 20 |
| `bfx_air_aero_clubs` | Aero Clubs and Gliders | 114,1 | bfx_mil_neuilly_army | — | add_ideas = bfx_clandestine_aviation, air_experience = 10, custom_effect_tooltip = bfx_tt_neuilly_r6_s3, add_to_variable = { bfx_rearm = 6 } |
| `bfx_air_dar_works` | The DAR Works at Bozhurishte | 114,2 | bfx_air_aero_clubs | — | add_extra_state_shared_building_slots = 1, add_building_construction = { type = arms_factory level = 1 instant_build = yes }, air_experience |
| `bfx_air_foreign_instructors` | Foreign Instructors | 116,3 | bfx_air_dar_works | — | air_experience = 25, add_ideas = bfx_foreign_air_instructors |
| `bfx_air_vazdushni_voyski` | Proclaim the Vazdushni Voyski | 112,3 | bfx_air_dar_works | — | capital_scope = { add_building_construction = { type = air_base level = 3 instant_build = yes } } |
| `bfx_air_fighter_regiment` | The Fighter Regiment | 112,4 | bfx_air_vazdushni_voyski | — | air_experience = 20, add_ideas = bfx_sofia_air_defence |
| `bfx_air_mountain_support` | Wings over the Mountains | 116,4 | bfx_air_foreign_instructors | — | air_experience = 20, add_ideas = bfx_wings_over_the_mountains |
| `bfx_tsar_tsar_of_the_balkans` | Tsar of All the Balkans | 18,13 | bfx_tsar_three_seas | — | add_core_of = ROOT, add_claim_by = ROOT, add_stability = 0.05 |
| `bfx_tsar_imperial_federation` | The Imperial Federation | 24,13 | bfx_tsar_danubian_confederation | — | add_core_of = ROOT, add_political_power = 100 |
| `bfx_alt_volga_bulgaria` | Return to the Volga | 30,15 | bfx_alt_asparuhs_homecoming | — | add_claim_by = ROOT, army_experience = 25, add_war_support = 0.10 |
| `bfx_alt_justinians_empire` | The Empire of Justinian | 38,15 | bfx_alt_exarchate_of_ravenna | — | add_claim_by = ROOT, add_core_of = ROOT, add_war_support = 0.05 |
| `bfx_com_black_sea_union` | The Black Sea Socialist Union | 48,13 | bfx_com_red_black_sea | — | add_claim_by = ROOT, add_core_of = ROOT |
| `bfx_com_trieste_to_odessa` | From Trieste to Odessa | 56,14 | bfx_com_red_danubia | — | add_claim_by = ROOT, add_core_of = ROOT, add_war_support = 0.05 |
| `bfx_agr_peasant_commonwealth` | The Peasant Commonwealth | 64,13 | bfx_agr_baltic_to_aegean | — | add_core_of = ROOT, add_stability = 0.10 |
| `bfx_zveno_levant_command` | The Levant Command | 72,13 | bfx_zveno_anatolian_gambit | — | add_claim_by = ROOT, add_core_of = ROOT, army_experience = 25 |
