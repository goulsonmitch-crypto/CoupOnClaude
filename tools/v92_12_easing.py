"""v92 item 12 — standardise easing and duration.

Tokens:
  --ease-enter    cubic-bezier(0.22, 1, 0.36, 1)   decelerate in (things arriving)
  --ease-exit     cubic-bezier(0.55, 0, 1, 0.45)   accelerate out (things leaving)
  --ease-spring   cubic-bezier(0.2, 1.4, 0.4, 1)   small overshoot (cards landing, bubbles)
  --ease-emphasis cubic-bezier(0.4, 0, 0.2, 1)     standard state change (hover, select, toggle)
  --dur-fast 150ms / --dur-base 250ms / --dur-slow 450ms

Every transition (CSS, inline markup, JS-assigned) maps onto them: durations
bin to fast (<=0.18s) / base (0.2-0.32s) / slow (0.35-0.6s); keyword and ad-hoc
bezier easings map to the token of the same intent. Clock-synced motion keeps
its exact timing and linear easing (the 1s timer bar tick, the 0.9s auction
ring, the 1s bluff-rate fill) because it must line up with the countdown.

Animations: one-shot entrances use --ease-enter, exits --ease-exit, overshoot
entrances --ease-spring, with the same duration bins. Infinite loops keep
ease-in-out and their rhythm (that is the correct curve for an oscillation).
"""
import re, collections
from v92_lib import Patch

P = Patch()
print('v92_12_easing')

TOK = """  /* ── motion ── */
  --ease-enter: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-exit: cubic-bezier(0.55, 0, 1, 0.45);
  --ease-spring: cubic-bezier(0.2, 1.4, 0.4, 1);
  --ease-emphasis: cubic-bezier(0.4, 0, 0.2, 1);
  --dur-fast: 150ms;
  --dur-base: 250ms;
  --dur-slow: 450ms;
"""
P.rep("  --num: tabular-nums lining-nums;\n", "  --num: tabular-nums lining-nums;\n" + TOK, 'motion tokens')

BEZ = {
    'cubic-bezier(0.4,0,0.2,1)': 'emphasis', 'cubic-bezier(0.4,0.0,0.2,1)': 'emphasis',
    'cubic-bezier(0.22,1,0.36,1)': 'enter', 'cubic-bezier(0.3,0.9,0.4,1)': 'enter', 'cubic-bezier(.3,.7,.4,1)': 'enter',
    'cubic-bezier(0.2,1.4,0.4,1)': 'spring', 'cubic-bezier(0.2,1.3,0.4,1)': 'spring',
}
def secs(t):
    return float(t[:-2]) / 1000 if t.endswith('ms') else float(t[:-1])
def dur_tok(s):
    if s <= 0.18: return 'var(--dur-fast)'
    if s <= 0.32: return 'var(--dur-base)'
    if s <= 0.6: return 'var(--dur-slow)'
    return None

def split_top(v):
    out, d, cur = [], 0, ''
    for ch in v:
        d += (ch == '(') - (ch == ')')
        if ch == ',' and d == 0: out.append(cur.strip()); cur = ''
        else: cur += ch
    if cur.strip(): out.append(cur.strip())
    return out

stat = collections.Counter()
def map_transition(v, exit_hint=False):
    items = split_top(v)
    out = []
    for it in items:
        toks = re.findall(r'cubic-bezier\([^)]*\)|var\([^)]*\)|\S+', it)
        times = [t for t in toks if re.fullmatch(r'\d*\.?\d+m?s', t)]
        ease = [t for t in toks if t.startswith('cubic-bezier') or t in ('ease', 'ease-in', 'ease-out', 'ease-in-out', 'linear')]
        props = [t for t in toks if t not in times and t not in ease]
        if any(t.startswith('var(--') for t in toks) or not times:
            out.append(it); continue
        d = secs(times[0]); delay = times[1] if len(times) > 1 else ''
        e = re.sub(r'\s', '', ease[0]) if ease else 'ease'
        if e == 'linear' or d > 0.6:
            stat['clock-synced kept'] += 1
            out.append(it); continue
        if e.startswith('cubic-bezier'): et = BEZ[e]
        elif exit_hint or e == 'ease-in': et = 'exit'
        else: et = 'emphasis'
        stat[f'{et}'] += 1
        out.append(' '.join(props + [dur_tok(d), f'var(--ease-{et})'] + ([delay] if delay else [])))
    return ', '.join(out)

# template-literal transition (the generic pass below can't parse a value that starts with a backtick)
P.rep("transition: `transform ${durMs}ms cubic-bezier(0.4, 0.0, 0.2, 1), opacity 0.25s`,",
      "transition: `transform ${durMs}ms var(--ease-emphasis), opacity var(--dur-base) var(--ease-exit)`,", 'card flights use emphasis/exit')
TR = re.compile(r'(transition\s*:\s*)([^;}"`\']+?)(\s*(?:!important)?\s*[;}"`\'])')
n = [0]
def f(m):
    n[0] += 1
    return m.group(1) + map_transition(m.group(2)) + m.group(3)
P.src = TR.sub(f, P.src)
# JS-assigned transition strings
P.rep("b.style.transition = 'opacity 0.5s';", "b.style.transition = 'opacity var(--dur-slow) var(--ease-exit)';", 'intro bubble fade-out uses exit')
print(f'  ok: {n[0]} transition declarations; mapped {dict(stat)}')

# one-shot animations
ENTRANCE = {'evIn', 'modIn', 'toastIn', 'flashIn', 'auctionCardIn', 'fadeIn', 'cardFlipIn', 'coinPulseAnim', 'clickPop', 'shuffleAnim', 'stampIn',
            'deathShake', 'challengeShake', 'justSwappedFlash', 'targetedFlash', 'v92Flash', 'borderPulse'}
EXIT = {'toastOut', 'flashOut', 'auctionCardOut'}
SPRING = {'claimBubbleIn', 'pitCardIn', 'bubbleIn', 'winFrameIn'}
AN = re.compile(r'(animation\s*:\s*)([^;}"`\']+?)(\s*(?:!important)?\s*[;}"`\'])')
astat = collections.Counter()
def map_anim(v):
    out = []
    for it in split_top(v):
        toks = re.findall(r'cubic-bezier\([^)]*\)|var\([^)]*\)|\S+', it)
        if not toks or 'infinite' in toks or any(t.startswith('var(--ease') for t in toks):
            out.append(it); continue
        name = toks[0]
        times = [t for t in toks if re.fullmatch(r'\d*\.?\d+m?s', t)]
        if name in SPRING: kind = 'spring'
        elif name in EXIT: kind = 'exit'
        elif name in ENTRANCE: kind = 'enter' if name.endswith('In') or name in ('fadeIn',) else 'emphasis'
        else:
            out.append(it); continue
        rest = [t for t in toks[1:] if not (t.startswith('cubic-bezier') or t in ('ease', 'ease-in', 'ease-out', 'ease-in-out', 'linear'))]
        if times:
            d = secs(times[0]); dt = dur_tok(d) if d <= 0.6 else times[0]
            rest[rest.index(times[0])] = dt
        astat[kind] += 1
        # easing goes right after the duration
        if times:
            i = [k for k, t in enumerate(rest) if t.startswith('var(--dur') or re.fullmatch(r'\d*\.?\d+m?s', t)][0]
            rest.insert(i + 1, f'var(--ease-{kind})')
        else:
            rest.append(f'var(--ease-{kind})')
        out.append(' '.join([name] + rest))
    return ', '.join(out)
na = [0]
def g(m):
    na[0] += 1
    return m.group(1) + map_anim(m.group(2)) + m.group(3)
a, b = P.region('css')
P.src = P.src[:a] + AN.sub(g, P.src[a:b]) + P.src[b:]
print(f'  ok: {na[0]} animation declarations; one-shots mapped {dict(astat)}')

left = re.findall(r'cubic-bezier\(([^)]*)\)', P.src)
left = [x for x in left if x.replace(' ', '') not in ('0.22,1,0.36,1', '0.55,0,1,0.45', '0.2,1.4,0.4,1', '0.4,0,0.2,1')]
assert not left, f'ad-hoc beziers remain: {left}'
print('  ok: no ad-hoc cubic-bezier left outside the four tokens')
P.write()
