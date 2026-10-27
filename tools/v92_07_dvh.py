"""v92 item 7 — dynamic viewport units.

The v91 file had 3 plain vh units and 1 dvh (the brief estimated 23; the
measured count is 3 + 1). On iOS Safari vh resolves against the LARGEST
viewport, so anything sized in vh is taller than what is visible while the
toolbar shows. Each one now has a vh fallback line followed by:
  * dvh where the element should track the visible viewport (screens, confetti),
  * svh where the element must never be clipped (the seat modal and the live
    faces strip are capped by the SMALLEST viewport so they always fit).
"""
from v92_lib import Patch

P = Patch()
print('v92_07_dvh')
P.rep(".screen { display: none; width: 100vw; height: 100dvh; overflow: hidden; }",
      ".screen { display: none; width: 100vw; height: 100vh; height: 100dvh; overflow: hidden; }",
      'screens: vh fallback before dvh')
P.rep("max-height:90vh; overflow-y:auto;", "max-height:90vh; max-height:90svh; overflow-y:auto;", 'seat modal: svh, never clipped')
P.rep("@keyframes cfall { to{transform:translateY(110vh) rotate(720deg);opacity:0} }",
      "@keyframes cfall { to{transform:translateY(110vh) rotate(720deg);transform:translateY(110dvh) rotate(720deg);opacity:0} }",
      'confetti falls the visible height')
P.rep("max-height:calc(100vh - 132px);", "max-height:calc(100vh - 132px); max-height:calc(100svh - 132px);", 'faces strip: svh, never clipped')
import re
plain = [m for m in re.finditer(r'(?<![\w.])(\d+(?:\.\d+)?)vh\b', P.src)]
modern = re.findall(r'\d(?:dvh|svh)\b', P.src)
print(f'  info: {len(plain)} vh (all are fallback lines) / {len(modern)} dvh+svh')
P.write()
