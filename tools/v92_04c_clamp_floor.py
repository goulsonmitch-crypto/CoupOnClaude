"""v92 item 4 (follow-up) — fluid font sizes get the same floor.

The item-4 pass only handled plain rem/px sizes. A clamp() whose minimum was
below 11px (the nameplate coin count: clamp(0.68rem, 0.9vw, 0.85rem) = 10.88px
on tablets) still slipped under the floor. Every clamp() minimum below 11px now
starts at --fs-xs. Run after v92_17 (see run_all.sh).
"""
import re
from v92_lib import Patch

P = Patch()
print('v92_04c_clamp_floor')
def f(m):
    v = float(m.group(2))
    return m.group(1) + 'var(--fs-xs),' if v * 16 < 11 else m.group(0)
P.sub(r'(font-size\s*:\s*clamp\(\s*)(\d*\.?\d+)rem\s*,', f, 'floor clamp() minimums')
left = [m for m in re.findall(r'font-size\s*:\s*clamp\(\s*(\d*\.?\d+)rem', P.src) if float(m) * 16 < 11]
assert not left, left
P.write()
