"""v92 items 18-19 — one version constant.

captureFrozenState() exported version 'v63' in every bug report while the
banner said 91. GAME_VERSION is now declared once, in the first <script> in
<head> (so it exists before any markup or game code runs), and both the landing
tagline and the frozen-state export read it, so they can never drift again.
The tagline is written by a synchronous inline script right after its element,
so there is no empty first paint.
"""
from v92_lib import Patch

P = Patch()
print('v92_18_version')
P.rep("<script>\n// ── Mobile rules overlay ───────────────────────────────────────────────\n",
      "<script>\n// v92: the single source of truth for the build number (banner + bug-report export)\nconst GAME_VERSION = '92';\n"
      "// ── Mobile rules overlay ───────────────────────────────────────────────\n", 'GAME_VERSION constant in <head>')
P.rep('<div class="logo-tagline">VERSION 91 · LIVE AT THE TABLE</div>',
      '<div class="logo-tagline" id="logo-tagline"></div>\n'
      "        <script>document.getElementById('logo-tagline').textContent = 'VERSION ' + GAME_VERSION + ' · LIVE AT THE TABLE';</script>",
      'tagline rendered from the constant')
P.rep("    version: 'v63',", "    version: 'v' + GAME_VERSION,", 'frozen-state export uses the constant')
assert 'VERSION 91' not in P.src
P.write()
