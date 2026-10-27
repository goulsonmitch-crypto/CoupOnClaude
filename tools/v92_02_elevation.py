"""v92 item 2 — elevation and radius scale.

Six elevation tokens (--e0 flush .. --e5 modal) plus one upward variant for
bottom-docked surfaces, and five radius tokens (--r-xs .. --r-pill).

Every box-shadow declaration (CSS, keyframes, inline markup, JS-emitted styles)
is parsed into layers. Black drop-shadow layers (the "elevation" part) are
replaced as a group by the elevation token that matches their depth (largest
blur). Coloured glows, focus/selection rings and insets are state, not height,
so they stay as layers next to the token. Every px border-radius is quantised
onto the radius scale; 50% circles stay circles.
"""
import re, collections
from v92_lib import Patch

P = Patch()
print('v92_02_elevation')

TOKENS = """  /* ── elevation: e0 flush → e5 modal. Two layers each: a tight contact shadow + a soft ambient one ── */
  --e0: 0 0 0 0 transparent;
  --e1: 0 1px 2px rgba(0,0,0,0.5), 0 2px 5px rgba(0,0,0,0.32);
  --e2: 0 2px 4px rgba(0,0,0,0.45), 0 6px 14px rgba(0,0,0,0.42);
  --e3: 0 4px 8px rgba(0,0,0,0.45), 0 12px 28px rgba(0,0,0,0.55);
  --e4: 0 8px 16px rgba(0,0,0,0.5), 0 18px 44px rgba(0,0,0,0.6);
  --e5: 0 12px 24px rgba(0,0,0,0.55), 0 28px 80px rgba(0,0,0,0.8);
  --e-up: 0 -2px 6px rgba(0,0,0,0.4), 0 -8px 28px rgba(0,0,0,0.55);
  /* ── radius ── */
  --r-xs: 3px;
  --r-sm: 6px;
  --r-md: 9px;
  --r-lg: 14px;
  --r-pill: 999px;
"""
P.rep("  --signal-bad-rgb: 244,67,54;\n}\n", "  --signal-bad-rgb: 244,67,54;\n" + TOKENS + "}\n", 'add elevation + radius tokens')

def split_layers(v):
    out, d, cur = [], 0, ''
    for ch in v:
        if ch == '(': d += 1
        if ch == ')': d -= 1
        if ch == ',' and d == 0: out.append(cur.strip()); cur = ''
        else: cur += ch
    if cur.strip(): out.append(cur.strip())
    return out

BLACK = re.compile(r'rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*[\d.]+\s*\)')
def classify(layer):
    if 'inset' in layer: return 'state', None
    if not BLACK.search(layer): return 'state', None
    bare = re.sub(r'rgba?\([^)]*\)|var\([^)]*\)|inset', ' ', layer)
    nums = [float(t[:-2] if t.endswith('px') else t) for t in bare.split() if re.fullmatch(r'-?[\d.]+(px)?', t)] + [0, 0, 0, 0]
    x, y, blur, spread = nums[:4]
    if '0 0 0' in layer and blur == 0: return 'state', None    # hard black outline ring
    if spread > 0 and blur == 0: return 'state', None
    return ('up' if y < 0 else 'drop'), blur

def elevation_for(blurs):
    b = max(blurs)
    return '--e1' if b <= 5 else '--e2' if b <= 14 else '--e3' if b <= 30 else '--e4' if b <= 50 else '--e5'

report = collections.Counter()
def remap_value(val):
    v = val.strip()
    if v in ('none', 'inherit', 'initial') or v.startswith('var(--e'): return val
    layers = split_layers(v)
    drops, ups, keep = [], [], []
    for L in layers:
        kind, blur = classify(L)
        if kind == 'drop': drops.append(blur)
        elif kind == 'up': ups.append(blur)
        else: keep.append(L)
    if not drops and not ups:
        report['state-only (glow/ring/inset kept)'] += 1
        return val
    lead = []
    if ups: lead.append('var(--e-up)'); report['--e-up'] += 1
    if drops:
        t = elevation_for(drops); lead.append(f'var({t})'); report[t] += 1
    new = ', '.join(keep + lead)       # state layers first so rings paint above the drop shadow
    lead_ws = val[:len(val) - len(val.lstrip())]
    return lead_ws + new

BS = re.compile(r'(box-shadow\s*:\s*)([^;}"`]+?)(\s*(?:!important)?\s*[;}"`])')
total = [0]
def f(m):
    total[0] += 1
    return m.group(1) + remap_value(m.group(2)) + m.group(3)
P.src = BS.sub(f, P.src)
print(f'  ok: {total[0]} box-shadow declarations parsed; {dict(report)}')
assert total[0] >= 100

# hard-coded JS boxShadow assignments
n_js = len(re.findall(r"\.boxShadow\s*=", P.src))
print(f'  info: {n_js} JS .boxShadow assignments (left as runtime state)')

# ---- radius
RAD = re.compile(r'(border-radius\s*:\s*)([^;}"`]+?)(\s*(?:!important)?\s*[;}"`])')
rcount = collections.Counter()
def rq(px):
    p = float(px)
    if p == 0: return '0'
    if p <= 3: return 'var(--r-xs)'
    if p <= 6: return 'var(--r-sm)'
    if p <= 10: return 'var(--r-md)'
    if p <= 16: return 'var(--r-lg)'
    return 'var(--r-pill)'
rtotal = [0]
def rf(m):
    rtotal[0] += 1
    v = m.group(2)
    if 'var(--r-' in v: return m.group(0)
    if '%' in v:
        rcount['50% circle kept'] += 1
        return m.group(0)
    nv = re.sub(r'(\d+(?:\.\d+)?)px', lambda q: rq(q.group(1)), v)
    nv = re.sub(r'(?<![\w.-])0(?![\w.%])', '0', nv)
    for t in re.findall(r'var\(--r-[\w]+\)', nv): rcount[t] += 1
    return m.group(1) + nv + m.group(3)
P.src = RAD.sub(rf, P.src)
# shorthand radius inside JS cssText strings use the same syntax, so they were covered above
print(f'  ok: {rtotal[0]} border-radius declarations; {dict(rcount)}')
left = [m.group(0) for m in RAD.finditer(P.src) if re.search(r'\d+px', m.group(2))]
assert not left, left[:5]
P.write()
