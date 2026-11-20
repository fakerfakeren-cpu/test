"""World events: news that every district sees, and random events of city life that can happen to anyone.

Event: title, description, picture (flags, mood), options [(text, effect, AI chance, trigger)], and for the random
events a mean time to happen and a trigger. In news, FROM is the country the news is about. Random events fire at
most once per country (a country flag remembers them), and after one fires a country gets no other for two years.
"""

NEWS = {   # namespace evil_sofia_news; major news is shown to every country
    "1": ("Red Flag over the Largo",
          "Sredets has gone communist. Late last night Victor Kolev appeared on the steps of the Party House before a "
          "crowd of several thousand and declared the Sredets Commune. Red flags have replaced the district colours "
          "on every public building around the Largo, and the ministries have been sealed by armed workers.\\n\\n"
          "In Vitosha, Daniel-Henry Capel's mother received reporters at her door with a cup of coffee and a "
          "satisfied smile. She has been saying it for years, she told them: the people of the centre were always "
          "communists. Tonight they simply stopped pretending. Asked whether she had a message for Victor Kolev, she "
          "said only that she hoped he was proud of himself.",
          (["SRD_RED"], "dusk"),
          [("The revolution has begun.", "", 1, "tag = SRD"),
           ("Henry's mother was right.", "", 1, "tag = VIT"),
           ("The centre has gone mad.", "", 1, "NOT = { tag = SRD tag = VIT }")]),
    "2": ("Order in the Centre",
          "Sredets will have no parties and no slogans. Victor Kolev has announced that he will govern the district "
          "in person, by decree, until order returns to Sofia. Checkpoints have gone up on every bridge into the "
          "centre and the trams, for the first time this year, are running on time.",
          (["SRD"], "day"),
          [("Order, at last.", "", 1, "tag = SRD"),
           ("One more strongman. Sofia has plenty.", "", 1, "NOT = { tag = SRD }")]),
    "3": ("The North-South Pact",
          "Sredets and Oborishte have signed an agreement dividing Sofia between them. Witnesses describe a map of "
          "the city on a table in the Party House and a single red line drawn from Lyulin to Kremikovtsi. Everything "
          "north of it is promised to Anton Zafirov, everything south to Victor Kolev.\\n\\nNo other district was "
          "consulted.",
          (["SRD_RED", "OBR_RED"], "night"),
          [("The city will be red, from north to south.", "", 1, "OR = { tag = SRD tag = OBR }"),
           ("They have divided us before they have beaten us.", "", 1, "NOT = { tag = SRD tag = OBR }")]),
    "4": ("Oborishte Falls",
          "The red flag flies over the Holy Synod. After a short and bitter fight around the cathedral, Oborishte "
          "has fallen to the Red Guards of Sredets, and Anton Zafirov has disappeared from public life. The centre "
          "of Sofia now answers to a single man.",
          (["OBR"], "fire"),
          [("The centre is ours.", "", 1, "tag = SRD"),
           ("Who is next?", "", 1, "NOT = { tag = SRD }")]),
    "5": ("Boyana Falls",
          "Vitosha has fallen. Red Guards have taken the villas of Boyana and the forest roads up to Dragalevtsi, and "
          "Daniel-Henry Capel's government no longer controls a single street. His mother, interviewed in the "
          "garden of her requisitioned villa, says she has nothing to add.",
          (["VIT"], "rain"),
          [("The mountain is red.", "", 1, "tag = SRD"),
           ("Even the mountain could not stop them.", "", 1, "NOT = { tag = SRD }")]),
    "6": ("The Sofia Commune",
          "There is one Sofia again. From Bankya to Pancharevo, from Novi Iskar to the top of Vitosha, every "
          "district now answers to the Party House. Victor Kolev has proclaimed the Sofia Commune from the balcony "
          "over the Largo, to a crowd that filled the square and the boulevards around it.",
          (["SRD_SOFIA"], "day"),
          [("One city, one flag.", "", 1, "tag = SRD"),
           ("Sofia is red.", "", 1, "NOT = { tag = SRD }")]),
    "7": ("North and South Sofia",
          "The last free district has fallen, and the city has been divided exactly along the line drawn in the "
          "North-South Pact. Sredets is now South Sofia, Oborishte North Sofia, and their alliance has taken the "
          "name of the city itself. Victor Kolev and Anton Zafirov shook hands for the cameras on Eagles' Bridge.",
          (["SRD_SOUTH", "OBR_NORTH"], "day"),
          [("Two halves, one Sofia.", "", 1, "OR = { tag = SRD tag = OBR }"),
           ("Sofia is red, twice over.", "", 1, "NOT = { tag = SRD tag = OBR }")]),
    "8": ("A District Falls",
          "[From.GetName] has capitulated. Its guards have laid down their arms, its leader has fled or been "
          "taken, and its streets are filling with foreign patrols. One district fewer stands between someone and "
          "the rule of the whole city.",
          (["SOFIA"], "rain"),
          [("Sofia shrinks.", "", 1, "")]),
    "9": ("The Free Sredets Is Proclaimed",
          "Victor Kolev has called the patrols off the Largo and proclaimed the Free Sredets: free papers, free "
          "speech, free trade and no curfew, ever again. In the same speech he announced that the centre will join "
          "no alliance and ask no district for help. Diplomats report that the cafés on Vitosha Boulevard are full "
          "again and that a blue flag flies over the district hall.\\n\\nIn Vitosha, Daniel-Henry Capel's mother "
          "is not impressed. A communist in a blue coat, she told reporters, is still a communist. She has seen the "
          "people of the centre before, and she will believe they have changed when she sees it with her own eyes.",
          (["SRD_FREE"], "day"),
          [("Sredets is free.", "", 1, "tag = SRD"),
           ("Mom isn't buying it.", "", 1, "tag = VIT"),
           ("Let them talk. We will see how long it lasts.", "", 1, "NOT = { tag = SRD tag = VIT }")]),
    "10": ("The Evil Gang Rides Again",
           "An old group chat has become the most talked-about alliance in Sofia. Victor Kolev of Sredets has "
           "proposed the return of the Evil Gang, and letters are said to be on their way, one a month, to Georgi "
           "Poryazov of Mladost, Daniel-Henry Capel of Vitosha and Stefan Kartunov of Krasna Polyana. Before the city "
           "fell apart, they were his closest friends. Whether they still are is another question.",
           (["SRD", "MLA", "KRP"], "night"),
           [("The gang is back.", "", 1, "tag = SRD"),
            ("Check the letterbox.", "", 1, "OR = { tag = MLA tag = VIT tag = KRP }"),
            ("Are we on the list?", "", 1, "NOT = { tag = SRD tag = MLA tag = VIT tag = KRP }")]),
    "11": ("The C Class Hools Take to the Streets",
           "Hundreds of young men in scarves and hoods marched through the centre of Sofia last night, lighting "
           "flares and singing. They call themselves the C Class Hools, they answer to Sredets, and their leaders "
           "say they will be visiting every neighbouring district soon.",
           (["SRD"], "fire"),
           [("Nobody stops the C Class.", "", 1, "tag = SRD"),
            ("Lock the doors.", "", 1, "NOT = { tag = SRD }")]),
    "12": ("A Physics Teacher Seizes Sredets",
           "The people of Sredets have waited long enough. A year of curfews and promises, and Victor Kolev has still "
           "not told them what the centre is for. This morning his former physics teacher, Konstantin Ilchev, walked "
           "into the Party House with a red pen and a stack of marked exam papers and declared that the lesson was "
           "over. The guards, who all sat in his classes too, let him straight through. Victor has been sent to "
           "detention, and Ilchev governs Sredets.",
           (["SRD"], "day"),
           [("Class is in session.", "", 1, "tag = SRD"),
            ("Sofia has gone completely mad.", "", 1, "NOT = { tag = SRD }")]),
    "13": ("The Free Centre of Sofia",
           "From Lagera to the Eagles' Bridge, the centre of Sofia now answers to one council in Sredets, and it has "
           "taken a new name: the Free Centre of Sofia. Victor Kolev has abolished every checkpoint in it and "
           "promised its people the same rights as his own. In the outer districts, people have started asking why "
           "theirs are different.",
           (["SRD_FREE_CENTRE"], "dusk"),
           [("One free city.", "", 1, "tag = SRD"),
            ("Free, and much too close.", "", 1, "NOT = { tag = SRD }")]),
    "14": ("Henry's Mom Was Wrong",
           "Daniel-Henry Capel's mother went to the free centre this week expecting red flags, commissars and "
           "queues for bread. She found cafés full until midnight, eleven newspapers arguing with each other on "
           "Rakovski Street, a market on Vitosha Boulevard where nobody asked for a party card, and Victor Kolev "
           "himself, who carried her shopping to the tram stop.\\n\\nLast night she told reporters, very quietly, "
           "that she was wrong. The people of the centre are not communists. Henry is said to have dropped his fork.",
           (["SRD_FREE", "VIT"], "day"),
           [("Told you so, Mrs Capel.", "", 1, "tag = SRD"),
            ("Mom... was wrong?", "", 1, "tag = VIT"),
            ("If even she admits it...", "", 1, "NOT = { tag = SRD tag = VIT }")]),
    "15": ("The Vitosha Award",
           "Vitosha has been carved up at a table in the Party House. With the map of Henry's district spread in front "
           "of him, Victor Kolev drew the new lines himself. Sredets took nothing: the villas of Boyana, the slopes and "
           "the villages all go to the members of the Evil Gang who stood by him. Nobody from Vitosha was invited.",
           (["SRD", "VIT"], "dusk"),
           [("Everyone gets their share.", "", 1, "tag = SRD"),
            ("A fair share for a loyal friend.", "", 1, "AND = { NOT = { tag = SRD } is_in_faction_with = SRD }"),
            ("Today Vitosha. Tomorrow?", "", 1, "AND = { NOT = { tag = SRD } NOT = { is_in_faction_with = SRD } }")]),
    "16": ("The Centre Is United",
           "From the Women's Market to the villas of Lozenets, the centre of Sofia answers to one district hall again. "
           "Victor Kolev has called it the end of a long dream. In the districts beyond the boulevards, people are "
           "asking whether the dream ends at the edge of the centre.",
           (["SRD"], "day"),
           [("One centre.", "", 1, "tag = SRD"),
            ("And where does it stop?", "", 1, "NOT = { tag = SRD }")]),
    "17": ("The Directorate of Sofia",
           "From the balcony of the Party House, Victor Kolev has proclaimed the Directorate of Sofia and named himself "
           "its Director. The centre of the city answers to him alone, its districts have been told they are provinces, "
           "and a new flag, gold on black, hangs over the Largo. Every district hall in Sofia received a copy of the "
           "proclamation. None of them was asked for an opinion.",
           (["SRD_DIRECTORATE"], "dusk"),
           [("One city, one Director.", "", 1, "tag = SRD"),
            ("A district that calls itself a city.", "", 1, "NOT = { tag = SRD }")]),
    "18": ("Krum's Cup",
           "Serdika has fallen, and with it the strangest ruler Sofia has seen in this war. Khan Krum is gone, and his "
           "famous cup now stands on Victor Kolev's desk in the Party House. Visitors report that nobody drinks from "
           "it, and that everybody looks at it.",
           (["SRD", "SRK"], "fire"),
           [("To the victor, the cup.", "", 1, "tag = SRD"),
            ("Even the Khan could not hold out.", "", 1, "NOT = { tag = SRD }")]),
    "19": ("A Temporary Emergency",
           "The free centre is free no longer. Victor Kolev has declared a temporary emergency: the curfew is back, the "
           "newspapers on Rakovski Street are closed until further notice, and the blue flag has been taken down for "
           "cleaning. Nobody has said when it will go back up.\\n\\nIn Vitosha, Daniel-Henry Capel's mother has told "
           "reporters that she always knew. A tyrant in a blue coat, she says, is still a tyrant.",
           (["SRD"], "night"),
           [("Just until it is safe.", "", 1, "tag = SRD"),
            ("Mom was right after all.", "", 1, "tag = VIT"),
            ("So much for the free centre.", "", 1, "NOT = { tag = SRD tag = VIT }")]),
    "20": ("A Coup from Below",
           "[From.GetName] has fallen in a single night. Armed men climbed out of the cellars of its district hall, the "
           "guard changed sides, and by morning [From.GetName] answered to Sredets. Nobody can say how they got in. "
           "In every district of Sofia, people have started listening to their cellars at night.",
           (["SRD"], "night"),
           [("The centre reaches far.", "", 1, "tag = SRD"),
            ("There was nothing we could do.", "", 1, "tag = FROM"),
            ("Check the cellars.", "", 1, "NOT = { tag = SRD tag = FROM }")]),
}

FLAVOUR = {   # namespace evil_sofia_flavour: random events of city life, for every district
    "1": ("The Trams Stop",
          "The tram drivers of [Root.GetName] have walked off the job. Their demands are simple: paid wages, a "
          "working heater in every carriage and an end to being shot at on the lines that run near the front. "
          "Without the trams, nobody gets to work.",
          (["SOFIA"], "rain"), 4200, "",
          [("Pay them. We need the trams.", "add_political_power = -40", 60, ""),
           ("Soldiers can drive trams.", "add_stability = -0.04\nadd_war_support = 0.02", 40, "")]),
    "2": ("Derby Day",
          "Levski and CSKA are playing tonight, war or no war. Half of [Root.GetName] supports one side, half the "
          "other, and the guards are asking whether the match should be stopped before the stands turn into a "
          "front line of their own.",
          (["LEVSKI", "CSKA"], "night"), 3600, "",
          [("Let them play. People need something to cheer.", "add_stability = 0.03\nadd_war_support = -0.02", 60, ""),
           ("Call it off. Send the fans to the recruiting office.", "add_manpower = 2000\nadd_stability = -0.03", 40, "")]),
    "3": ("The Big Snow",
          "Snow has been falling on [Root.GetName] for three days. The streets are impassable, the trucks are stuck "
          "and the guards spend more time digging than drilling. Everyone with a shovel is needed.",
          (["SOFIA"], "snow"), 4500, "",
          [("Everyone out with a shovel.", "add_political_power = -25\nadd_stability = 0.02", 50, ""),
           ("The front first, the streets later.", "add_stability = -0.03", 50, "")]),
    "4": ("The Pothole Committee",
          "A delegation of furious residents has arrived at the district hall of [Root.GetName] with photographs of "
          "the worst potholes in the district. One of them has swallowed an army truck. They will not leave until "
          "something is done.",
          (["SOFIA"], "day"), 4500, "",
          [("Fill them in. All of them.", "add_political_power = -30\nadd_stability = 0.03", 50, ""),
           ("Potholes slow down enemy tanks too.", "add_war_support = 0.02\nadd_stability = -0.02", 50, "")]),
    "5": ("The Price of a Döner",
          "The price of a döner in [Root.GetName] has doubled in a month. The kebab shops blame the war, the war "
          "blames the kebab shops, and the soldiers are eating bread and lyutenitsa again. Morale is suffering.",
          (["SOFIA"], "night"), 3900, "",
          [("Fix the price. The soldiers must eat.", "add_political_power = -35\nadd_war_support = 0.03", 60, ""),
           ("Bread and lyutenitsa never hurt anybody.", "add_war_support = -0.03", 40, "")]),
    "6": ("The Stray Dogs of Sofia",
          "Packs of stray dogs have taken over the parks of [Root.GetName]. They follow patrols, steal from the "
          "field kitchens and bark at night until nobody can sleep. A guard sergeant has proposed adopting the "
          "whole pack as the district's mascot.",
          (["SOFIA"], "dusk"), 4800, "",
          [("Adopt them. Every unit gets a dog.", "add_stability = 0.02\nadd_war_support = 0.02", 50, ""),
           ("Round them up and send them to the countryside.", "add_political_power = 20", 50, "")]),
    "7": ("Weddings on Every Block",
          "The war has started a wave of weddings in [Root.GetName]. Every weekend the brass bands play in the "
          "courtyards of the panel blocks, and the young men go off to the front a few days later with rings on "
          "their fingers.",
          (["SOFIA"], "dusk"), 4500, "",
          [("Wish them luck, and give them rifles.", "add_manpower = 1500\nadd_war_support = 0.02", 60, ""),
           ("Grant every groom a month of leave.", "add_stability = 0.04\nadd_political_power = -15", 40, "")]),
    "8": ("A Black Market on the Women's Market",
          "Everything is for sale in [Root.GetName] if you know whom to ask: rifles, petrol, cigarettes, ammunition "
          "and, for the right price, a commission in the district guard.",
          (["SOFIA"], "night"), 4200, "",
          [("Close it down.", "add_stability = 0.02\nadd_political_power = -20", 50, ""),
           ("Tax it.", "add_political_power = 40\nadd_stability = -0.03", 50, "")]),
    "9": ("Hikers on Cherni Vrah",
           "A group of hikers from [Root.GetName] has climbed Cherni Vrah, the highest peak of Vitosha, and planted "
           "the district flag on the summit. The photograph is in every newspaper of the city.",
           (["VIT"], "snow"), 5400, "",
           [("Print it on the posters.", "add_war_support = 0.03", 70, ""),
            ("Send them to the mountain troops.", "army_experience = 5", 30, "")]),
}
