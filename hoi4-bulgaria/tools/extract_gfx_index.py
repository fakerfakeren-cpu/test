"""Build reference/*.gfx sprite catalogues from the yard1/HoI4-GFX-Search index.html
(a scrape of the live game's interface/*.gfx files, last updated 2026-06-15).
Only sprites the index marks as base game (class dlc-base) are written."""
import re, sys, os, collections
src, out = sys.argv[1], sys.argv[2]
html = open(src, encoding='utf-8').read()
sec_re = re.compile(r'id="([A-Za-z]+Section)"')
item_re = re.compile(r'title="([^"]+)" class="icon dlc-([a-z0-9:,_-]+)">\s*<img src="([^"]+)"')
PREFIX = {'ideasSection': 'GFX_idea_', 'characterIdeasSection': 'GFX_idea_'}  # the index strips this prefix
# split by section markers
pos = [(m.start(), m.group(1)) for m in sec_re.finditer(html)]
pos.append((len(html), None))
data = collections.defaultdict(list)
for (s, name), (e, _) in zip(pos, pos[1:]):
    for m in item_re.finditer(html, s, e):
        n = m.group(1)
        if not n.startswith('GFX_'): n = PREFIX.get(name, '') + n
        data[name].append((n, m.group(2), m.group(3).replace('\\', '/')))
names = {'goalsSection': 'goals.gfx', 'ideasSection': 'ideas.gfx', 'characterIdeasSection': 'ideas_characters.gfx',
         'eventsSection': 'eventpictures.gfx', 'decisionsSection': 'decisions.gfx', 'texticonsSection': 'texticons.gfx'}
for sec, items in data.items():
    fn = names.get(sec, sec + '.gfx')
    seen = set()
    with open(os.path.join(out, fn), 'w', encoding='utf-8') as f:
        f.write('# Reference catalogue reconstructed from yard1/HoI4-GFX-Search (index updated 2026-06-15).\n')
        f.write('# Only base-game (non-DLC) sprites. Texture paths are the .dds the index converted to .png.\n')
        f.write('spriteTypes = {\n')
        for n, dlc, p in items:
            if dlc != 'base' or n in seen: continue
            seen.add(n)
            f.write('\tspriteType = { name = "%s" texturefile = "%s" }\n' % (n, re.sub(r'\.png$', '.dds', p)))
        f.write('}\n')
    print(sec, fn, len(items), 'base:', len(seen))
