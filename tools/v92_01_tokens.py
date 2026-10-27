"""v92 item 1 — unify the colour system.

* Replaces the 26-token :root with a real scale: surface 0-5, gold 0-5, text 0-3,
  border 0-2, a base/tint/shade/glow quartet per card role, status colours, felt
  and rail colours, plus "-rgb" channel tokens so alpha variants share the scale.
* Renames every var(--old-name) reference to the new scale.
* Migrates every hex literal outside :root onto a token:
    - CSS, markup and JS-emitted UI styles -> design tokens
    - role-card SVG art and the dormant legacy-roster SVG art -> an illustration
      palette (--ill-*), with near-duplicates (<=3%, max channel delta 8) collapsed;
      SVG presentation attributes are rewritten as style declarations so var() resolves
    - per-character signature colours -> --char-* tokens
* Migrates the large rgba() families (gold, role colours, surfaces, status) onto
  rgba(var(--x-rgb), a).
Visual result: identical layout; colours agree with themselves.
"""
import re, colorsys, collections
from v92_lib import Patch

P = Patch()
print('v92_01_tokens')

# ---------------------------------------------------------------- 1. new :root
OLD_ROOT_START = ':root {\n  --bg: #080608;'
a = P.src.index(OLD_ROOT_START)
b = P.src.index('}\n', a) + 2
old_root = P.src[a:b]
assert old_root.count('--') == 25, 'expected the 25-token v91 root'

ROOT = """:root {
  color-scheme: dark;
  /* ── surfaces: 0 = deepest page, 5 = most raised ── */
  --surface-0: #080608;
  --surface-1: #0e0b10;
  --surface-2: #13101a;
  --surface-3: #1a1624;
  --surface-4: #221d30;
  --surface-5: #2e2740;
  /* ── antique gold: 0 = ink, 5 = highlight ── */
  --gold-0: #14100a;
  --gold-1: #5a4515;
  --gold-2: #7a6020;
  --gold-3: #a8842f;
  --gold-4: #d4a843;
  --gold-5: #f0c966;
  /* ── text: 0 = brightest, 3 = faint (raised from #3d3545 for legibility) ── */
  --text-0: #fff8ea;
  --text-1: #e8dcc8;
  --text-2: #8a7a8a;
  --text-3: #645a70;
  --parchment: #f5ecd8;
  --ink: #000;
  /* ── borders: 0 = hairline, 1 = gold hairline, 2 = gold rule ── */
  --border-0: #1e1828;
  --border-1: rgba(212,168,67,0.25);
  --border-2: rgba(212,168,67,0.55);
  /* ── card roles: base / tint / shade / glow ── */
  --duke: #7d3c98;        --duke-tint: #bb8fce;        --duke-shade: #1e0c26;        --duke-glow: rgba(125,60,152,0.45);
  --assassin: #6a6070;    --assassin-tint: #b4aabd;    --assassin-shade: #16101a;    --assassin-glow: rgba(150,140,160,0.45);
  --captain: #2471a3;     --captain-tint: #5dade2;     --captain-shade: #08141f;     --captain-glow: rgba(36,113,163,0.45);
  --ambassador: #148f77;  --ambassador-tint: #76d7c4;  --ambassador-shade: #061a16;  --ambassador-glow: rgba(20,143,119,0.45);
  --contessa: #c0392b;    --contessa-tint: #e8967a;    --contessa-shade: #1e0806;    --contessa-glow: rgba(192,57,43,0.45);
  /* ── status ── */
  --danger: #e74c3c;
  --danger-tint: #ffd5cc;
  --danger-deep: #8a1010;
  --ok: #58d68d;
  --ok-deep: #1e8449;
  --warn: #ca6f1e;
  --warn-tint: #f0b27a;
  --blitz: #ff9944;
  --blitz-hot: #ff6644;
  --stamp-bluff: #ff4444;
  --stamp-honest: #44ff88;
  --signal-ok: #4caf50;
  --signal-warn: #ffc107;
  --signal-bad: #f44336;
  /* ── table: felt and rail ── */
  --felt-0: #08291c;  --felt-1: #0e3d2c;  --felt-2: #17553f;
  --rail-0: #2a1f0e;
  --felt-dc-0: #0a1a0e;  --felt-dc-1: #0f2415;  --felt-dc-2: #1a3520;  --rail-dc-0: #4a1a10;  --rail-dc-1: #221008;
  --felt-blue-0: #030f1e;  --felt-blue-1: #071d32;  --felt-blue-2: #0d2d4a;  --rail-blue-0: #1d3d5a;  --rail-blue-1: #0a1d30;
  --felt-red-0: #1e0303;  --felt-red-1: #320808;  --felt-red-2: #4a0d0d;  --rail-red-0: #5a1515;  --rail-red-1: #2a0808;
  /* ── channel tokens for alpha variants: rgba(var(--x-rgb), a) ── */
  --surface-0-rgb: 8,6,8;
  --surface-1-rgb: 14,11,16;
  --gold-4-rgb: 212,168,67;
  --gold-5-rgb: 240,201,102;
  --text-0-rgb: 255,248,234;
  --parchment-rgb: 245,236,216;
  --duke-rgb: 125,60,152;
  --duke-tint-rgb: 187,143,206;
  --captain-rgb: 36,113,163;
  --captain-tint-rgb: 93,173,226;
  --ambassador-rgb: 20,143,119;
  --contessa-rgb: 192,57,43;
  --danger-rgb: 231,76,60;
  --ok-rgb: 88,214,141;
  --ok-deep-rgb: 30,132,73;
  --warn-rgb: 202,111,30;
  --blitz-rgb: 255,153,68;
  --stamp-bluff-rgb: 255,68,68;
  --stamp-honest-rgb: 68,255,136;
  --signal-ok-rgb: 76,175,80;
  --signal-warn-rgb: 255,193,7;
  --signal-bad-rgb: 244,67,54;
}
"""
P.rep(old_root, ROOT, 'replace :root with token scale')

# ---------------------------------------------------------------- 2. rename var(--old) references
RENAME = {
    'bg': 'surface-0', 'bg2': 'surface-1', 'surface': 'surface-2', 'surface2': 'surface-3', 'surface3': 'surface-4',
    'gold': 'gold-4', 'gold-light': 'gold-5', 'gold-dim': 'gold-2',
    'red': 'contessa', 'red-bright': 'danger', 'blue': 'captain', 'blue-light': 'captain-tint',
    'green': 'ok-deep', 'green-light': 'ok', 'purple': 'duke', 'purple-light': 'duke-tint',
    'teal': 'ambassador', 'teal-light': 'ambassador-tint', 'orange': 'warn', 'orange-light': 'warn-tint',
    'text': 'text-1', 'text-dim': 'text-2', 'text-faint': 'text-3', 'border': 'border-0', 'border-gold': 'border-1',
}
ren_re = re.compile(r'var\(--(' + '|'.join(sorted(map(re.escape, RENAME), key=len, reverse=True)) + r')(?![\w-])')
n_before = len(ren_re.findall(P.src))
P.src = ren_re.sub(lambda m: 'var(--' + RENAME[m.group(1)], P.src)
assert not ren_re.search(P.src)
print(f'  ok: renamed {n_before} var(--legacy-name) references')
# fallback forms that carried a hex
P.rep('var(--duke-tint,#c89ae8)', 'var(--duke-tint)', 'drop hex fallback on purple-light')
P.rep('var(--surface-4,#221d30)', 'var(--surface-4)', 'drop hex fallback on surface3')

# ---------------------------------------------------------------- 3. special cases before the generic map
P.rep('.conn-dot.gray   { background:#555; }', '.conn-dot.gray   { background:var(--text-3); }', 'offline dot uses faint text, not the assassin grey')
P.rep("box-shadow:0 0 3px #4caf5066; }", "box-shadow:0 0 3px rgba(var(--signal-ok-rgb),0.4); }", 'conn green glow')
P.rep("box-shadow:0 0 3px #ffc10766; }", "box-shadow:0 0 3px rgba(var(--signal-warn-rgb),0.4); }", 'conn yellow glow')
P.rep("box-shadow:0 0 3px #f4433666; }", "box-shadow:0 0 3px rgba(var(--signal-bad-rgb),0.4); }", 'conn red glow')
# auction spotlight SVG (UI, not art) uses presentation attributes
P.rep('<stop offset="0%" stop-color="#1e1830"/>', '<stop offset="0%" style="stop-color:var(--surface-4)"/>', 'auction svg stop 0')
P.rep('<stop offset="100%" stop-color="#12101c"/>', '<stop offset="100%" style="stop-color:var(--surface-2)"/>', 'auction svg stop 1')
P.rep('fill="#d4a843" font-family="Cinzel,Georgia,serif"', 'style="fill:var(--gold-4)" font-family="Cinzel,Georgia,serif"', 'auction svg label')

# ---------------------------------------------------------------- 4. UI hex -> design tokens (CSS, markup, JS UI)
UI = {
    '#fff': 'text-0', '#ffffff': 'text-0', '#fff8ea': 'text-0', '#000': 'ink',
    '#14100a': 'gold-0', '#231603': 'gold-0', '#5a4515': 'gold-1', '#3a2a0e': 'gold-1', '#4a3410': 'gold-1',
    '#7a6020': 'gold-2', '#8a6000': 'gold-2', '#8a6920': 'gold-3', '#aa8000': 'gold-3',
    '#d4a843': 'gold-4', '#d4a017': 'gold-4', '#f0c966': 'gold-5', '#ffe066': 'gold-5',
    '#080608': 'surface-0', '#0a0710': 'surface-0', '#0e0b10': 'surface-1', '#0f0a14': 'surface-1',
    '#13101a': 'surface-2', '#12101c': 'surface-2', '#171020': 'surface-2',
    '#1a1624': 'surface-3', '#1a1424': 'surface-3', '#1a1628': 'surface-3',
    '#221d30': 'surface-4', '#221c30': 'surface-4', '#201c30': 'surface-4', '#1e1830': 'surface-4', '#241c2e': 'surface-4',
    '#333': 'surface-5',
    '#e8dcc8': 'text-1', '#8a7a8a': 'text-2', '#3d3545': 'text-3', '#f5ecd8': 'parchment', '#1e1828': 'border-0',
    '#7d3c98': 'duke', '#bb8fce': 'duke-tint', '#8a6aaa': 'duke-tint',
    '#6a6070': 'assassin', '#555': 'assassin', '#666': 'assassin', '#8a8090': 'assassin-tint', '#bbb': 'assassin-tint',
    '#2471a3': 'captain', '#5dade2': 'captain-tint',
    '#148f77': 'ambassador', '#76d7c4': 'ambassador-tint',
    '#c0392b': 'contessa', '#e8967a': 'contessa-tint', '#e88': 'contessa-tint',
    '#e74c3c': 'danger', '#ffd5cc': 'danger-tint', '#ffb3ab': 'danger-tint', '#7a1010': 'danger-deep', '#a00000': 'danger-deep',
    '#58d68d': 'ok', '#2ecc71': 'ok', '#1e8449': 'ok-deep', '#ca6f1e': 'warn', '#e67e22': 'warn', '#f0b27a': 'warn-tint',
    '#3498db': 'captain-tint', '#9b59b6': 'duke-tint',
    '#ff9944': 'blitz', '#ff6644': 'blitz-hot', '#ff4444': 'stamp-bluff', '#44ff88': 'stamp-honest',
    '#4caf50': 'signal-ok', '#ffc107': 'signal-warn', '#f44336': 'signal-bad',
    '#08291c': 'felt-0', '#0e3d2c': 'felt-1', '#17553f': 'felt-2', '#2a1f0e': 'rail-0',
    '#0a1a0e': 'felt-dc-0', '#0f2415': 'felt-dc-1', '#1a3520': 'felt-dc-2', '#4a1a10': 'rail-dc-0', '#221008': 'rail-dc-1',
    '#030f1e': 'felt-blue-0', '#071d32': 'felt-blue-1', '#0d2d4a': 'felt-blue-2', '#1d3d5a': 'rail-blue-0', '#0a1d30': 'rail-blue-1',
    '#1e0303': 'felt-red-0', '#320808': 'felt-red-1', '#4a0d0d': 'felt-red-2', '#5a1515': 'rail-red-0', '#2a0808': 'rail-red-1',
    '#e8a030': 'gold-4',
}
HEX = re.compile(r'#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-zA-Z_-])')

def ui_map(seg, what):
    miss = collections.Counter()
    def f(m):
        h = m.group(0).lower()
        if h in UI:
            return f'var(--{UI[h]})'
        miss[h] += 1
        return m.group(0)
    out, n = HEX.subn(f, seg)
    return out, n - sum(miss.values()), miss

def remap_region(lo, hi, what, skip=()):
    seg = P.src[lo:hi]
    # never touch the :root definitions themselves, element ids in CSS selectors, or #ids in JS
    parts, last = [], 0
    for s0, s1 in skip:
        parts.append((last, s0, True)); parts.append((s0, s1, False)); last = s1
    parts.append((last, len(seg), True))
    out, total, misses = '', 0, collections.Counter()
    for x, y, doit in parts:
        if doit:
            o, n, miss = ui_map(seg[x:y], what); out += o; total += n; misses += miss
        else:
            out += seg[x:y]
    P.src = P.src[:lo] + out + P.src[hi:]
    print(f'  ok: {what}: {total} hex literals -> tokens; unmapped: {dict(misses)}')
    return misses

# CSS: only colour positions. Selector ids like #screen-landing are not hex (contain non-hex letters) except a few.
css_lo, css_hi = P.region('css')
root_lo = P.src.index(':root {', css_lo); root_hi = P.src.index('}\n', root_lo) + 2
m = remap_region(css_lo, css_hi, 'css', skip=[(root_lo - css_lo, root_hi - css_lo)])
assert not m, f'unmapped css hex {m}'
mk_lo, mk_hi = P.region('markup')
m = remap_region(mk_lo, mk_hi, 'markup')
assert not m, f'unmapped markup hex {m}'

# JS UI: everything in the main script except the SVG art and the data tables handled below.
js_lo, js_hi = P.region('js')
skips = []
for nm in ('legacy-svg', 'role-svg'):
    x, y = P.region(nm); skips.append((x - js_lo, y - js_lo))
for start, end in (('const AVATAR_COLORS', '\n'), ('const AKIVA_SKIN = {', '};'), ('const CHAR_LOG_COLORS = {', '};')):
    x = P.src.index(start, js_lo); y = P.src.index(end, x)
    skips.append((x - js_lo, y - js_lo))
x = P.src.index("// Rabbi Akiva skin-tone replacements", js_lo); y = P.src.index('\n', x); skips.append((x - js_lo, y - js_lo))
x = P.src.index("base.split('#e6c8a0')", js_lo); skips.append((x - js_lo, x - js_lo + len("base.split('#e6c8a0')")))
skips.sort()
m = remap_region(js_lo, js_hi, 'js-ui', skip=skips)
assert not m, f'unmapped js hex {m}'

# ---------------------------------------------------------------- 5. data tables
P.rep("const AVATAR_COLORS = ['#7d3c98','#2471a3','#148f77','#ca6f1e','#c0392b','#1e8449'];",
      "const AVATAR_COLORS = ['var(--duke)','var(--captain)','var(--ambassador)','var(--warn)','var(--contessa)','var(--ok-deep)'];",
      'avatar colours -> role tokens')
x = P.src.index('const CHAR_LOG_COLORS = {'); y = P.src.index('};', x)
tbl = P.src[x:y]
pairs = re.findall(r"(\w+):\s*'(#[0-9a-fA-F]{6})'", tbl)
assert len(pairs) == 32, len(pairs)
char_tokens = ''.join(f'  --char-{re.sub(r"([A-Z])", lambda m: "-" + m.group(1).lower(), k)}: {v.lower()};\n' for k, v in pairs)
new_tbl = re.sub(r"(\w+):(\s*)'(#[0-9a-fA-F]{6})'",
                 lambda m: f"{m.group(1)}:{m.group(2)}'var(--char-{re.sub(r'([A-Z])', lambda q: '-' + q.group(1).lower(), m.group(1))})'", tbl)
P.src = P.src[:x] + new_tbl + P.src[y:]
print('  ok: 32 character signature colours -> --char-* tokens')

# ---------------------------------------------------------------- 6. SVG art -> illustration palette
def rgb(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

DESIGN = {}   # exact design-token values usable by the art
for line in ROOT.splitlines():
    for name, val in re.findall(r'--([\w-]+):\s*(#[0-9a-fA-F]{3,6});', line):
        DESIGN.setdefault(rgb(val), name)

def near(a, b): return max(abs(p - q) for p, q in zip(a, b)) <= 8   # ~3% of 255

art_hex = collections.Counter()
for nm in ('legacy-svg', 'role-svg'):
    x, y = P.region(nm)
    art_hex.update(h.lower() for h in HEX.findall(P.src[x:y]))
for h in ['#e6c8a0']: art_hex[h] += 0
assignments = {}      # hex -> token name
ill = []              # (rgb, name)
def hue_name(c):
    r, g, b = [v / 255 for v in c]
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    L = round(ll * 100)
    if ss < 0.12 or L < 7: fam = 'grey' if L > 12 else 'ink'
    else:
        d = hh * 360
        fam = ('red' if d < 15 or d >= 345 else 'orange' if d < 40 else 'amber' if d < 55 else 'yellow' if d < 70 else
               'lime' if d < 95 else 'green' if d < 160 else 'teal' if d < 190 else 'blue' if d < 250 else 'violet' if d < 290 else 'rose')
        if fam in ('orange', 'amber', 'red') and L > 55 and ss < 0.75: fam = 'skin' if L < 90 else 'cream'
    return f'{fam}-{L}'
for h, _ in sorted(art_hex.items(), key=lambda kv: -kv[1]):
    c = rgb(h)
    hit = next((n for v, n in DESIGN.items() if near(v, c)), None)
    if hit: assignments[h] = hit; continue
    hit = next((n for v, n in ill if near(v, c)), None)
    if hit: assignments[h] = hit; continue
    name = 'ill-' + hue_name(c)
    while any(n == name for _, n in ill): name += 'b'
    ill.append((c, name)); assignments[h] = name

def art_convert(seg):
    """Rewrite fill/stroke/stop-color="#hex" attributes into one style="" per element."""
    def el(m):
        tag = m.group(0)
        props = []
        def at(mm):
            props.append(f'{mm.group(1)}:var(--{assignments[mm.group(2).lower()]})')
            return ''
        body = re.sub(r'\s(fill|stroke|stop-color)="(#[0-9a-fA-F]{3,6})"', at, tag)
        if not props: return tag
        assert 'style="' not in body
        end = '/>' if body.endswith('/>') else '>'
        return body[:-len(end)].rstrip() + f' style="{";".join(props)}"' + end
    out = re.sub(r'<[a-zA-Z][^<>]*>', el, seg)
    # object-literal colours (legacy CHARACTERS[].color), unused at runtime but kept consistent
    out = re.sub(r"color:\s*'(#[0-9a-fA-F]{6})'", lambda m: f"color: 'var(--{assignments[m.group(1).lower()]})'", out)
    return out

for nm in ('legacy-svg', 'role-svg'):
    x, y = P.region(nm)
    before = len(HEX.findall(P.src[x:y]))
    new = art_convert(P.src[x:y])
    left = HEX.findall(new)
    assert not left, f'{nm} unconverted {left[:5]}'
    P.src = P.src[:x] + new + P.src[y:]
    print(f'  ok: {nm}: {before} hex literals -> palette tokens')

# Rabbi Akiva: the skin-swap now targets the skin token string, and the variant skins are tokens too
akiva_skin_tok = f"var(--{assignments['#e6c8a0']})"
x, y = P.region('legacy-svg')
assert P.src[x:y].count(akiva_skin_tok) >= 1
P.rep("// Rabbi Akiva skin-tone replacements (skin hex #e6c8a0 → variant skin)",
      f"// Rabbi Akiva skin-tone replacements (skin token {akiva_skin_tok} → variant skin)", 'akiva comment')
P.rep("base.split('#e6c8a0')", f"base.split('{akiva_skin_tok}')", 'akiva skin swap target')
x = P.src.index('const AKIVA_SKIN = {'); y = P.src.index('};', x)
ak = re.findall(r"(\w+):\s*'(#[0-9a-fA-F]{6})'", P.src[x:y])
assert len(ak) == 7
akiva_tokens = ''.join(f'  --ill-akiva-{k}: {v};\n' for k, v in ak)
P.src = P.src[:x] + re.sub(r"(\w+):(\s*)'(#[0-9a-fA-F]{6})'", lambda m: f"{m.group(1)}:{m.group(2)}'var(--ill-akiva-{m.group(1)})'", P.src[x:y]) + P.src[y:]
print('  ok: akiva variant skins -> tokens')

def hexof(c): return '#%02x%02x%02x' % c
ILL_ROOT = ("/* ── illustration palette: SVG role-card art and the dormant legacy roster.\n"
            "   Near-duplicates (within ~3%) collapsed; art colours that match a design token use it. ── */\n:root {\n"
            + ''.join(f'  --{n}: {hexof(c)};\n' for c, n in sorted(ill, key=lambda t: t[1]))
            + akiva_tokens
            + "  /* character signature colours (event-log names) */\n" + char_tokens + "}\n")
P.rep(ROOT, ROOT + ILL_ROOT, 'append illustration + character palettes')

# ---------------------------------------------------------------- 7. rgba families -> channel tokens
RGBA = {
    (212, 168, 67): 'gold-4-rgb', (240, 201, 102): 'gold-5-rgb', (255, 215, 0): 'gold-5-rgb',
    (192, 57, 43): 'contessa-rgb', (231, 76, 60): 'danger-rgb',
    (36, 113, 163): 'captain-rgb', (93, 173, 226): 'captain-tint-rgb',
    (125, 60, 152): 'duke-rgb', (187, 143, 206): 'duke-tint-rgb', (20, 143, 119): 'ambassador-rgb',
    (8, 6, 8): 'surface-0-rgb', (14, 11, 16): 'surface-1-rgb', (13, 10, 16): 'surface-1-rgb', (10, 7, 12): 'surface-1-rgb',
    (10, 8, 12): 'surface-1-rgb', (14, 10, 18): 'surface-1-rgb', (14, 11, 18): 'surface-1-rgb',
    (30, 132, 73): 'ok-deep-rgb', (88, 214, 141): 'ok-rgb', (46, 204, 113): 'ok-rgb',
    (202, 111, 30): 'warn-rgb', (255, 153, 68): 'blitz-rgb', (240, 220, 180): 'parchment-rgb',
    (255, 255, 255): 'text-0-rgb', (255, 68, 68): 'stamp-bluff-rgb', (68, 255, 136): 'stamp-honest-rgb',
}
rg = re.compile(r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,')
root_lo = P.src.index(':root {'); root_hi = P.src.index('}\n', P.src.index(':root {', root_lo + 5)) + 2
head, body, tail = P.src[:root_lo], P.src[root_lo:root_hi], P.src[root_hi:]
cnt = [0]
def rf(m):
    k = tuple(int(v) for v in m.groups())
    if k in RGBA: cnt[0] += 1; return f'rgba(var(--{RGBA[k]}),'
    return m.group(0)
head = rg.sub(rf, head); tail = rg.sub(rf, tail)
P.src = head + body + tail
print(f'  ok: {cnt[0]} rgba() literals -> channel tokens')

# ---------------------------------------------------------------- 8. final audit
roots = [m.start() for m in re.finditer(r':root \{', P.src)]
spans = [(r, P.src.index('}\n', r)) for r in roots]
outside = 0
for m in HEX.finditer(P.src):
    if any(a0 <= m.start() <= b0 for a0, b0 in spans): continue
    ctx = P.src[max(0, m.start() - 30):m.end() + 5]
    # CSS id selectors (e.g. #ctx-menu, #add) are not colours
    if re.match(r'#[0-9a-fA-F]+[\s,{.:>\[)]', P.src[m.start():m.end() + 1]) and re.search(r'(^|[\s,}>(])$', P.src[max(0, m.start() - 1):m.start()]):
        if P.src[m.end():m.end() + 1] in ' ,{.:>[)' and not re.search(r'(color|background|border|fill|stroke|shadow)[^;{}]*$', P.src[max(0, m.start() - 60):m.start()]):
            continue
    outside += 1
    print('   LEFT:', repr(ctx))
assert outside == 0, f'{outside} hex colour literals remain outside :root'
print('  ok: zero hex colour literals outside :root')
P.write()
