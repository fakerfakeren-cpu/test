"""What each event picture should show. The build writes tools/event_pictures/PICTURES.md from this, with the
file name and size of every picture; a PNG saved under that name in tools/event_pictures/ replaces the drawn
picture at the next build (any size: it is scaled and cropped from the middle).
"""

HEADER = """# Event pictures

Save each picture as a PNG with the file name below in `evil-sofia/tools/event_pictures/`. The next build uses it
instead of the drawn flag picture. Any size works: it is scaled and cropped from the middle, so keep the subject
in the centre and use the same proportions as the size given.

Vanilla style: old photographs from the 1930s and 40s, black and white or sepia, a little grainy and soft, no
modern objects in focus. Country events are 210x176 (nearly square), news events 397x153 (wide).

| File | Size | Event | What it should show | Status |
|---|---|---|---|---|"""

BRIEFS = {
    # Sredets tree
    "evil_sofia_srd_1": "A crowd with red flags filling a city square at dusk, a speaker on the steps of a large "
                        "government building.",
    "evil_sofia_srd_2": "A man in a coat waiting alone in the hallway of an old apartment building, a staircase "
                        "behind him.",
    "evil_sofia_srd_3": "Two men shaking hands in front of a cathedral, a small crowd watching.",
    "evil_sofia_srd_4": "A man walking away alone down an empty street at night, a cathedral dome behind.",
    "evil_sofia_srd_5": "A young man tearing up letters at a desk in a villa, an older woman standing behind him.",
    "evil_sofia_srd_6": "Trucks and armed militiamen on a forest road leading down a mountain.",
    "evil_sofia_srd_7": "A man on the telephone late at night, a desk lamp and a city map on the table.",
    "evil_sofia_srd_8": "Soldiers at the gate of a barracks before dawn, a district hall with a new flag.",
    "evil_sofia_srd_9": "Two old friends embracing, militiamen marching past behind them.",
    "evil_sofia_srd_10": "A man hanging up a telephone, looking out of a rainy window.",
    "evil_sofia_srd_11": "A young man reading a message, a group photograph pinned to the wall behind him.",
    "evil_sofia_srd_12": "A small group of young men in coats laughing together on the steps of a theatre.",
    "evil_sofia_srd_13": "An empty chair at a long table, a single glass left on it.",
    "evil_sofia_srd_14": "A dozen young men in scarves and hoods outside a district hall, one holding a lit flare.",
    "evil_sofia_srd_15": "Football fans with scarves raised marching together through a street.",
    "evil_sofia_srd_16": "A street fight at night between two groups of young men, smoke from flares.",
    # news
    "evil_sofia_news_1": "Red banners over a large square in front of a monumental government building, crowds below.",
    "evil_sofia_news_2": "Armed police at a checkpoint on a bridge, a tram waiting behind them.",
    "evil_sofia_news_3": "Two men signing a document over a city map spread on a table.",
    "evil_sofia_news_4": "Smoke over the domes of a cathedral, soldiers in the square in front of it.",
    "evil_sofia_news_5": "Soldiers in the garden of a hillside villa, pine forest and a mountain behind.",
    "evil_sofia_news_6": "A huge rally in a square, a man speaking from a balcony hung with a red flag.",
    "evil_sofia_news_7": "Two leaders shaking hands on a bridge with bronze eagles, photographers around them.",
    "evil_sofia_news_8": "Soldiers laying down rifles in a pile in a city street, civilians watching.",
    "evil_sofia_news_9": "Soldiers taking down a checkpoint barrier on a city boulevard while crowds fill the cafés.",
    "evil_sofia_news_13": "A crowd celebrating on a city square under an old cathedral, flags waved from balconies.",
    "evil_sofia_news_10": "A group of young men posing on the steps of a theatre, a newspaper photograph.",
    "evil_sofia_news_11": "A march of young men with scarves and lit flares through a city centre at night.",
    "evil_sofia_news_12": "A teacher with a stack of papers walking past saluting guards into a government building.",
    # random events
    "evil_sofia_flavour_1": "Trams standing still in a rainy street, drivers gathered beside them.",
    "evil_sofia_flavour_2": "A packed football stadium at night, two sets of fans with scarves.",
    "evil_sofia_flavour_3": "People shovelling deep snow in a city street, a stuck truck.",
    "evil_sofia_flavour_4": "Angry residents with photographs at the door of a town hall, a broken road.",
    "evil_sofia_flavour_5": "A queue outside a small kebab shop at night, soldiers in it.",
    "evil_sofia_flavour_6": "A pack of stray dogs in a park, a soldier crouching to feed one.",
    "evil_sofia_flavour_7": "A wedding with a brass band in the courtyard of an apartment block.",
    "evil_sofia_flavour_8": "A crowded street market at night, crates being handed over in the shadows.",
    "evil_sofia_flavour_9": "Hikers planting a flag on a snowy mountain summit.",
}
