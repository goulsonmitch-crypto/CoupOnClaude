"""v92 item 4 (follow-up) — make the raised labels fit.

* em-relative sizes get a floor: font-size:max(<n>em, var(--fs-xs)), so a
  small parent can never drag them under 11px.
* "(CPU)" in the nameplate keeps the plate's size on desktop and is dropped on
  phones (the plate's title still carries the full name).
* Buttons in narrow rows (settings modal, character picker) were clipping their
  own label on phones because 1.5rem side padding left ~45px for text. Phones
  get tighter padding and tracking; labels may wrap rather than clip.
"""
import re
from v92_lib import Patch

P = Patch()
print('v92_04b_legibility_fit')

P.sub(r'font-size:(0\.\d+)em', r'font-size:max(\1em, var(--fs-xs))', 'floor em-relative font sizes', count=8)

CSS = """.af-cpu { font-size: inherit; }
@media (max-width: 720px) {
  .af-cpu { display: none; }
  .btn { padding-left: 0.75rem; padding-right: 0.75rem; letter-spacing: 0.08em; }
  .modal .btn, .char-screen-inner .btn { white-space: normal; line-height: 1.2; overflow-wrap: anywhere; }
  .showcase-card { width: 52px; height: 70px; }
  .showcase-card .sc-name { display: none; }
}
"""
P.rep(".showcase-card.ambassador .sc-name { letter-spacing: 0.02em; }\n",
      ".showcase-card.ambassador .sc-name { letter-spacing: 0.02em; }\n" + CSS, 'fit rules')
P.write()
