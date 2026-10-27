"""v92 item 9 — consolidate breakpoints.

v91 used eight widths (380, 560, 640, 720, 768, 900, 1000, 1150) in two
syntaxes, plus portrait/landscape orientation queries, and the JS frame sizer
used a ninth idea of "narrow" (720). iPad portrait (768-834) fell between them:
CSS gave it the phone arena while JS sized its frames as desktop, so the arc
overflowed. Now there are four named breakpoints, one syntax, and JS reads the
same numbers:

    phone    <= 599px
    tablet   600px - 1023px   (explicit layout block below)
    desktop  >= 1024px        (iPad landscape lands here)
    wide     >= 1280px        (reserved; the salon walls use desktop)

The landscape-phone blocker (orientation: landscape) and (max-height: 500px),
the short-desktop (max-height: 840px) refinement and (pointer: coarse) are not
width breakpoints and keep their conditions.
"""
from v92_lib import Patch

P = Patch()
print('v92_09_breakpoints')

PHONE = '@media (max-width: 599px)'
TABLET = '@media (min-width: 600px) and (max-width: 1023px)'
DESKTOP = '@media (min-width: 1024px)'

MAP = [
    ('@media (min-width: 1150px) {', DESKTOP + ' {', 1),
    ('@media (max-width: 720px) {', PHONE + ' {', 4),
    ('@media(max-width:560px){', PHONE + ' {', 1),
    ('@media(max-width:380px){', PHONE + ' {', 1),
    ('@media (max-width:640px) {', PHONE + ' {', 1),
    ('@media (max-width:720px){', PHONE + ' {', 1),
    ('@media (max-width: 768px) and (orientation: portrait) {', PHONE + ' {', 4),
    ('@media (min-width: 1000px) {', DESKTOP + ' {', 1),
    ('@media (min-width: 1000px) and (max-height: 840px) {', '@media (min-width: 1024px) and (max-height: 840px) {', 1),
    ('@media (max-width:560px) {', PHONE + ' {', 1),
    ('@media (max-width:720px) {', PHONE + ' {', 1),
    ('@media (max-width: 900px) {', TABLET + ' {', 1),
    ('@media (max-width: 560px) {', PHONE + ' {', 1),
]
for old, new, n in MAP:
    P.rep(old, new, f'{old} -> {new}', count=n)

TABLET_CSS = f"""
/* ══ v92 tablet (600-1023): an explicit layout instead of inheriting desktop or phone by accident ══ */
{TABLET} {{
  #event-log-col {{ width: 196px; }}
  #event-log-col.collapsed {{ width: 28px; }}
  #av-fab.on-game {{ right: 212px; }}
  #arena-arc {{ gap: 10px; }}
  .action-card {{ width: 74px; height: 98px; }}
  .respond-zone {{ min-width: 116px; padding: 0.6rem 1rem; }}
  .pit-claim {{ max-width: 230px; }}
  .lobby-grid {{ max-width: 600px; }}
  .char-grid {{ grid-template-columns: repeat(auto-fill, minmax(118px, 1fr)); }}
  .auction-side-panel {{ width: 136px; }}
  .reveal-grid {{ max-width: 620px; }}
}}
"""
P.rep("\n</style>\n</head>", TABLET_CSS + "\n</style>\n</head>", 'tablet layout block')

# JS: same numbers, and size the arc from the arena's real width (the log column takes space)
P.rep("function isMobilePortrait() {\n  return window.innerWidth <= 768 && window.innerWidth < window.innerHeight;\n}",
      "// v92: the four named breakpoints, shared with the CSS media queries\n"
      "const BP = { phoneMax: 599, tabletMax: 1023, wideMin: 1280 };\n"
      "function isMobilePortrait() {\n  return window.innerWidth <= BP.tabletMax && window.innerWidth < window.innerHeight;\n}",
      'BP constants')
P.rep("    const vw = window.innerWidth || 1200;\n    const narrow = vw <= 720;",
      "    const vw = window.innerWidth || 1200;\n    const narrow = vw <= BP.phoneMax;\n"
      "    const arenaEl = document.getElementById('arena');\n"
      "    const aw = (arenaEl && arenaEl.clientWidth) || vw;   // the event log column is not table space",
      'frame sizer uses BP + arena width')
P.rep("      vwCap = Math.floor((vw - 18) / others) - 6;", "      vwCap = Math.floor((aw - 18) / others) - 6;", 'narrow cap from arena width')
P.rep("      vwCap = Math.floor((vw - 48) / others) - 14;", "      vwCap = Math.floor((aw - 48) / others) - 14;", 'wide cap from arena width')

import re
heads = sorted(set(re.findall(r'@media[^{]+', P.src)))
print('  info: media conditions now in use:')
for h in heads: print('     ', h.strip())
P.write()
