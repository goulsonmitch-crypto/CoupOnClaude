"""v92 item 3 — type scale, numerals, smoothing, tracking.

* Type tokens: a 1.125 (major-second) modular scale anchored at 1rem, and family
  tokens --font-display (Cinzel) / --font-body (Crimson Pro) / --font-mono
  (JetBrains Mono) / --font-num (tabular lining figures).
* Every rem/px font-size >= 11px is snapped to the nearest step (log distance).
  Values below 11px are left for item 4, which owns the legibility floor.
* All 125 font-family declarations point at the family tokens.
* Antialiasing / kerning hints on the document.
* font-variant-numeric: tabular-nums on every number that changes during play.
  Cinzel has no tabular figures, so counters that were set in Cinzel switch to
  the numeral face (Crimson Pro lining tabular figures) to stop width jitter.
* Letter-spacing tightens as size grows: large display type is capped
  (>=2.5rem: 0.14em, 1.5-2.5rem: 0.16em, 1-1.5rem: 0.18em). Room codes keep
  their wide spacing because it separates characters you have to read aloud.
"""
import re, math, collections
from v92_lib import Patch

P = Patch()
print('v92_03_type')

STEPS = [  # name, rem
    ('xs', 0.7023), ('sm', 0.7901), ('md', 0.8889), ('base', 1.0), ('lg', 1.125), ('xl', 1.2656),
    ('2xl', 1.4238), ('3xl', 1.6018), ('4xl', 1.8020), ('5xl', 2.0273), ('6xl', 2.2807), ('7xl', 2.5658),
    ('8xl', 2.8865), ('9xl', 3.2473), ('10xl', 3.6532), ('11xl', 4.1099),
]
TOK = """  /* ── type: 1.125 modular scale (11.2px floor), families, numerals ── */
""" + ''.join(f'  --fs-{n}: {r}rem;\n' for n, r in STEPS) + """  --font-display: 'Cinzel', 'Trajan Pro', Georgia, serif;
  --font-body: 'Crimson Pro', Georgia, serif;
  --font-mono: 'JetBrains Mono', ui-monospace, Menlo, monospace;
  --font-num: 'Crimson Pro', Georgia, serif;
  --num: tabular-nums lining-nums;
"""
P.rep("  --r-pill: 999px;\n}\n", "  --r-pill: 999px;\n" + TOK + "}\n", 'add type tokens')

def nearest(px):
    rem = px / 16
    return min(STEPS, key=lambda s: abs(math.log(s[1] / rem)))[0]

FS = re.compile(r'(font-size\s*:\s*)(\d*\.?\d+)(rem|px)(?![\w-])')
stat = collections.Counter()
def f(m):
    v = float(m.group(2)); px = v * 16 if m.group(3) == 'rem' else v
    if px < 11:
        stat['sub-11 left for item 4'] += 1
        return m.group(0)
    if px == 0: return m.group(0)
    n = nearest(px); stat[n] += 1
    return f'{m.group(1)}var(--fs-{n})'
# skip the :root block (it now contains no font-size declarations, but stay explicit)
P.src = FS.sub(f, P.src)
print(f'  ok: font-size snapped to scale {dict(stat)}')

# ---- families
FAM = [
    (r"font-family\s*:\s*'Cinzel'\s*,\s*serif", 'font-family:var(--font-display)'),
    (r"font-family\s*:\s*Cinzel\s*,\s*serif", 'font-family:var(--font-display)'),
    (r"font-family\s*:\s*'Crimson Pro'\s*,\s*serif", 'font-family:var(--font-body)'),
    (r"font-family\s*:\s*'JetBrains Mono'\s*,\s*monospace", 'font-family:var(--font-mono)'),
]
tot = 0
for pat, rep in FAM:
    P.src, n = re.subn(pat, rep, P.src); tot += n
print(f'  ok: {tot} font-family declarations -> family tokens')
left = re.findall(r"font-family\s*:\s*(?!var\(--font-|inherit)([^;}\"`]+)", P.src)
assert not left, left
# SVG text attribute in the auction spotlight
P.rep('font-family="Cinzel,Georgia,serif"', 'style="fill:var(--gold-4);font-family:var(--font-display)"', 'auction svg font attr')
P.rep('style="fill:var(--gold-4)" style="fill:var(--gold-4);font-family:var(--font-display)"',
      'style="fill:var(--gold-4);font-family:var(--font-display)"', 'merge auction svg style attrs')

# ---- document-level rendering hints
P.rep("html, body { height: 100%; background: var(--surface-0); color: var(--text-1); font-family:var(--font-mono); overflow: hidden; }",
      "html, body { height: 100%; background: var(--surface-0); color: var(--text-1); font-family:var(--font-mono); overflow: hidden; }\n"
      "html { -webkit-text-size-adjust: 100%; text-size-adjust: 100%; }\n"
      "body { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; text-rendering: optimizeLegibility;\n"
      "  font-kerning: normal; font-feature-settings: 'kern' 1, 'liga' 1; font-optical-sizing: auto; }\n"
      "/* every number that changes during play keeps a fixed advance width */\n"
      ".me-coins, .af-coins, .seat-coins, .timer-num, #tb-round, .deck-count, .disc-badge, .dp-count, .fan-count,\n"
      ".step-val, .auction-timer-num, .auction-counter, .auction-status, .auction-deck-count, .auction-bid-info,\n"
      ".reveal-stat-num, .timing-val, .timing-dc-sub-val, .bluff-bar-label, .player-count-badge, #lose-countdown,\n"
      "#exch-countdown, .center-label, .me-coins-sub, .dp-meta, .auction-hist-tag {\n"
      "  font-variant-numeric: var(--num); font-feature-settings: 'tnum' 1, 'lnum' 1; }\n"
      "/* Cinzel has no tabular figures: counters set in it use the numeral face instead */\n"
      ".deck-count, .disc-badge, .dp-count, .fan-count, .auction-timer-num, .reveal-stat-num, .timing-val, .timing-dc-sub-val { font-family: var(--font-num); font-weight: 700; }",
      'document smoothing + tabular numerals')

# ---- tracking: cap letter-spacing on large display type, per rule
RULE = re.compile(r'([^{}]+)\{([^{}]*)\}')
capped = collections.Counter()
def cap_rule(m):
    sel, body = m.group(1), m.group(2)
    if 'room-code' in sel: return m.group(0)
    fsm = re.search(r'font-size\s*:\s*(?:var\(--fs-([\w]+)\)|clamp\([^,]+,[^,]+,\s*([\d.]+)rem\))', body)
    lsm = re.search(r'letter-spacing\s*:\s*([\d.]+)em', body)
    if not fsm or not lsm: return m.group(0)
    rem = dict(STEPS)[fsm.group(1)] if fsm.group(1) else float(fsm.group(2))
    ls = float(lsm.group(1))
    cap = 0.14 if rem >= 2.5 else 0.16 if rem >= 1.5 else 0.18 if rem >= 1.0 else None
    if cap is None or ls <= cap: return m.group(0)
    capped[f'{ls}->{cap}'] += 1
    body = body[:lsm.start()] + f'letter-spacing:{cap}em' + body[lsm.end():]
    return sel + '{' + body + '}'
a, b = P.region('css')
P.src = P.src[:a] + RULE.sub(cap_rule, P.src[a:b]) + P.src[b:]
print(f'  ok: tracking tightened on large type {dict(capped)}')
P.write()
