"""Basic decisions for every district, in the spirit of vanilla's generic ones (vanilla's own decision files are
replaced because they are written for the world map). Everything that changes support, stability or war support
does it over time, through a timed spirit, never all at once.

CATEGORIES: (key, name, description, allowed, visible, decisions); each decision a dict with id, name, desc, cost,
cooldown (days before it can be taken again, 0 = none), visible, available, effect, ai (ai_will_do script), icon.
IDEAS: like IDEAS in focus_sredets.py: key: (name, description, modifiers, (background, piece)).
"""

DAYS = 120   # how long a campaign spirit lasts

IDEAS = {
    "ES_war_propaganda": ("War Propaganda",
                          "Posters on every tram, speeches in every square: the district must be ready to fight.",
                          "war_support_weekly = 0.01", ("Army.png", "Megaphone.png")),
    "ES_public_order": ("Public Order Campaign",
                        "Extra patrols, fixed street lamps and bread at fair prices. The district calms down.",
                        "stability_weekly = 0.01", ("Circle.png", "Soldiers Saluting.png")),
    "ES_promote_communism": ("Communist Agitation",
                             "Party cells in the factories, red newspapers on the corners.",
                             "communism_drift = 0.1", ("Rectangle.png", "Hammer and Sickle.png")),
    "ES_promote_democracy": ("Democratic Clubs",
                             "Debating clubs, free newspapers and petitions in every café.",
                             "democratic_drift = 0.1", ("Shield Blue.png", "Ballot.png")),
    "ES_promote_fascism": ("Nationalist Rallies",
                           "Torchlight marches and uniforms on the boulevards.",
                           "fascism_drift = 0.1", ("Rectangle.png", "Fist.png")),
    "ES_promote_neutrality": ("Loyalty to the District",
                              "No parties, no slogans: the district hall and its guard come first.",
                              "neutrality_drift = 0.1", ("Circle.png", "Citizen.png")),
    "ES_recruitment_drive": ("Recruitment Drive",
                             "Recruiting tables in the squares and a band playing on Sundays.",
                             "conscription = 0.005", ("Army.png", "Soldier Pointing.png")),
    "ES_war_bonds": ("War Bonds",
                     "Every family buys its share of the war, and grumbles about it.",
                     "war_support_weekly = 0.005\nstability_weekly = -0.003\npolitical_power_factor = 0.10",
                     ("Rectangle.png", "Coins2.png")),
    "ES_reserves": ("Reserves Called Up",
                    "Every man who ever held a rifle is called back to the barracks.",
                    "conscription_factor = 0.15\nstability_weekly = -0.005", ("Army.png", "Soldiers in Rows.png")),
    "ES_rationing": ("Rationing",
                     "Bread cards, queues at the bakeries and the factories free to work for the front.",
                     "consumer_goods_factor = -0.05\nstability_factor = -0.05", ("Rectangle.png", "Bread.png")),
}

_PROMOTE = ["ES_promote_communism", "ES_promote_democracy", "ES_promote_fascism", "ES_promote_neutrality"]


def _no_campaign():
    return "NOT = { " + " ".join(f"has_idea = {i}" for i in _PROMOTE) + " }"


def _promote(key, ideology, name, desc, icon):
    return dict(id=f"ES_decision_{key[3:]}", name=name, desc=desc + "\n\nSupport for it grows a little every day for "
                f"{DAYS} days. Only one such campaign can run at a time.",
                cost=75, cooldown=0, visible="", available=_no_campaign(),
                effect=f"add_timed_idea = {{ idea = {key} days = {DAYS} }}",
                ai=f"factor = 0\nmodifier = {{ add = 1 has_government = {ideology} }}", icon=icon)


CATEGORIES = [
    ("ES_political_actions", "Political Actions",
     "The everyday business of running a district: keeping it calm, keeping it loyal and keeping it ready.",
     "always = yes", "always = yes", [
         dict(id="ES_decision_war_propaganda", name="War Propaganda",
              desc="Posters, speeches and parades to get the district ready for war.\n\nWar support grows every "
                   f"week for {DAYS} days.",
              cost=50, cooldown=0, visible="", available="NOT = { has_idea = ES_war_propaganda }",
              effect=f"add_timed_idea = {{ idea = ES_war_propaganda days = {DAYS} }}",
              ai="factor = 1\nmodifier = { factor = 0 has_war_support > 0.7 }", icon="generic_army_support"),
         dict(id="ES_decision_public_order", name="Public Order Campaign",
              desc="Patrols, repairs and fair bread prices to calm the district down.\n\nStability grows every "
                   f"week for {DAYS} days.",
              cost=50, cooldown=0, visible="", available="NOT = { has_idea = ES_public_order }",
              effect=f"add_timed_idea = {{ idea = ES_public_order days = {DAYS} }}",
              ai="factor = 1\nmodifier = { factor = 0 has_stability > 0.7 }", icon="generic_civil_support"),
         _promote("ES_promote_communism", "communism", "Communist Agitation",
                  "Let the party organise in the factories and the housing blocks.", "generic_political_discourse"),
         _promote("ES_promote_democracy", "democratic", "Democratic Clubs",
                  "Let the clubs, the free newspapers and the petitions spread.", "generic_political_discourse"),
         _promote("ES_promote_fascism", "fascism", "Nationalist Rallies",
                  "Let the nationalists march on the boulevards.", "generic_political_discourse"),
         _promote("ES_promote_neutrality", "neutrality", "Loyalty to the District",
                  "Remind everyone that the district hall comes before any party.", "generic_political_discourse"),
         dict(id="ES_decision_recruitment_drive", name="Recruitment Drive",
              desc=f"Recruiting tables in every square.\n\nMore of the population can be recruited for {DAYS} days.",
              cost=50, cooldown=0, visible="", available="NOT = { has_idea = ES_recruitment_drive }",
              effect=f"add_timed_idea = {{ idea = ES_recruitment_drive days = {DAYS} }}",
              ai="factor = 1\nmodifier = { factor = 0 has_war = no }", icon="generic_army_support"),
     ]),
    ("ES_war_measures", "War Measures",
     "Measures a district at war can take to keep fighting.",
     "always = yes", "has_war = yes", [
         dict(id="ES_decision_war_bonds", name="War Bonds",
              desc="Sell the war to the people, one bond at a time.\n\nFor 180 days: war support grows every week, "
                   "stability falls a little every week, more political power.",
              cost=25, cooldown=0, visible="", available="has_war = yes\nNOT = { has_idea = ES_war_bonds }",
              effect="add_timed_idea = { idea = ES_war_bonds days = 180 }",
              ai="factor = 1", icon="generic_industry"),
         dict(id="ES_decision_call_up_the_reserves", name="Call Up the Reserves",
              desc="Every man who ever held a rifle goes back to the barracks.\n\nFor 180 days: much more manpower, "
                   "stability falls every week.",
              cost=75, cooldown=0, visible="", available="has_war = yes\nNOT = { has_idea = ES_reserves }",
              effect="add_timed_idea = { idea = ES_reserves days = 180 }",
              ai="factor = 1\nmodifier = { factor = 0 has_manpower > 20000 }", icon="generic_prepare_civil_war"),
         dict(id="ES_decision_rationing", name="Rationing",
              desc="Bread cards and queues, so the factories can work for the front.\n\nFor 180 days: fewer "
                   "consumer goods, less stability.",
              cost=50, cooldown=0, visible="", available="has_war = yes\nNOT = { has_idea = ES_rationing }",
              effect="add_timed_idea = { idea = ES_rationing days = 180 }",
              ai="factor = 0", icon="generic_industry"),
     ]),
]
