"""v92 item 4 — eliminate sub-11px text.

* Every font-size below 11px (143 declarations across CSS, markup and JS-emitted
  styles; the smallest was 0.34rem = 5.4px) is raised to --fs-xs (11.24px).
* Labels that genuinely have no room switch from Cinzel (a high-contrast display
  serif that falls apart below ~11px) to a label face: Source Sans 3 semibold,
  real small caps, wider tracking.
* Where even that cannot fit, the text is replaced by an icon + title tooltip:
  dead cards inside opponents' frames already carry the role portrait and a
  title, so their name strip is dropped; the landing showcase cards keep their
  emoji and gain a title on phones.
* "(CPU)" is split into its own span in the nameplate so phones can drop it
  (the full name stays in the plate's title) and give the real name the room.
"""
import re
from v92_lib import Patch

P = Patch()
print('v92_04_legibility')

# ---- font: add the label face
P.rep("@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=JetBrains+Mono:wght@300;400;500&display=swap');",
      "@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;0,700;1,300;1,400&family=JetBrains+Mono:wght@300;400;500&family=Source+Sans+3:wght@400;600;700&display=swap');",
      'load Source Sans 3 label face')
P.rep("  --font-num: 'Crimson Pro', Georgia, serif;\n",
      "  --font-num: 'Crimson Pro', Georgia, serif;\n"
      "  --font-label: 'Source Sans 3', 'Source Sans Pro', 'Segoe UI', Roboto, Arial, sans-serif;\n",
      'label face token')

# ---- floor: every sub-11px size -> --fs-xs
FS = re.compile(r'(font-size\s*:\s*)(\d*\.?\d+)(rem|px)(?![\w-])')
n = [0]
def f(m):
    v = float(m.group(2)); px = v * 16 if m.group(3) == 'rem' else v
    if 0 < px < 11:
        n[0] += 1
        return f'{m.group(1)}var(--fs-xs)'
    return m.group(0)
P.src = FS.sub(f, P.src)
assert n[0] == 143, n[0]
print(f'  ok: {n[0]} sub-11px font-size declarations raised to --fs-xs (11.24px)')

# ---- nameplate: CPU tag as its own span so it can yield on phones
P.rep("""<span class="af-name" title="${esc(p.displayName||p.name)}">${esc(p.displayName||p.name)}</span>${cpuTag}""",
      """<span class="af-name" title="${esc(p.displayName||p.name)}">${esc(String(p.displayName||p.name).replace(/\\s*\\(CPU\\)\\s*$/i,''))}${/\\(CPU\\)\\s*$/i.test(p.displayName||p.name||'') ? '<span class="af-cpu"> (CPU)</span>' : ''}</span>${cpuTag}""",
      'split (CPU) suffix into its own span')
P.rep('<div class="af-plate">${connDot}', '<div class="af-plate" title="${esc(p.displayName||p.name)}">${connDot}', 'plate tooltip carries the full name')

# ---- landing showcase: titles so the emoji alone is enough on phones
for role, emoji, name in (('duke', '👑', 'Duke'), ('assassin', '🗡️', 'Assassin'), ('captain', '⚓', 'Captain'),
                          ('ambassador', '🌿', 'Ambassador'), ('contessa', '🌹', 'Contessa')):
    P.rep(f'<div class="showcase-card {role}">{emoji}<span class="sc-name">{name}</span></div>',
          f'<div class="showcase-card {role}" title="{name}" aria-label="{name}">{emoji}<span class="sc-name">{name}</span></div>',
          f'showcase {role} title')

CSS = """
/* ══ v92 legibility: label face for tight labels (item 4) ══ */
.sc-name, .wall-name2, .home-char-name, .center-label, .seat-card-name, .dp-card-name, .deck-name, .dp-name,
.me-you, .seat-cpu-tag, .af-cpu, .pit-chip-name, .face-tile .face-name, .avs-name, .exch-card .ec-name, .ec-badge,
.swap-badge, .char-taken-badge, .auction-deck-label, .seat-token-name, .char-mini-name, .timer-track.priority::before,
.pit-waitlbl, .faces-head, .fly-name {
  font-family: var(--font-label); font-weight: 600; font-variant-caps: all-small-caps;
  font-feature-settings: 'smcp' 1, 'c2sc' 1, 'tnum' 1; letter-spacing: 0.07em; text-transform: none; line-height: 1.1;
}
.sc-name, .wall-name2, .home-char-name, .center-label, .pit-chip-name, .face-tile .face-name, .avs-name, .faces-head { font-size: var(--fs-sm); }
.seat-card-name, .dp-card-name, .exch-card .ec-name, .swap-badge, .ec-badge, .me-you, .char-taken-badge { font-size: var(--fs-xs); letter-spacing: 0.04em; }
/* opponents' revealed cards inside the frame are 34px wide: the role portrait + title tooltip is the label */
.af-cards .seat-card .seat-card-name { display: none; }
.af-cards .seat-card .portrait-wrap { transform: scale(0.72); }
.af-cpu { color: inherit; opacity: 0.72; font-size: 0.86em; }
/* landing showcase: room for a readable name; phones fall back to emoji + title */
.showcase-card { width: 62px; height: 84px; gap: 4px; }
.sc-name { opacity: 0.85; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; padding: 0 2px; }
.showcase-card.ambassador .sc-name { letter-spacing: 0.02em; }
"""
P.rep("\n</style>\n</head>", CSS + "\n</style>\n</head>", 'append legibility block')
P.write()
