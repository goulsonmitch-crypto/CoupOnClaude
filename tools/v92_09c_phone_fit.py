"""v92 item 9 (follow-up) — layout fits found by the 360x640 screenshots.

All but the last are pre-existing v91 bugs, exposed by the verification run:
* #table-center is absolutely positioned at left:50%, so its shrink-to-fit width
  was capped at HALF the arena (measured 180px on a 360px phone). The centre
  zone therefore wrapped into two rows even when one would fit, pushing the
  treasury and deck up under the frames. It now sizes to max-content (capped
  at the arena width) and stays centred.
* Flex-centred scroll containers clip their top when content is taller than the
  screen (justify-content:center has no "safe" fallback): the phone landing
  logo, the character picker's title and first row, and the winner portrait
  were unreachable on short phones. They now centre with auto margins, which
  top-align (and scroll) when there isn't room.
* The settings modal could be taller than a 640px screen with no way to reach
  its Done button; modals now cap at the visible height and scroll.
* Short phones (<=700px tall) get a slightly lower action grid and a lower
  table centre so the arc, centre and dock never collide.
"""
from v92_lib import Patch

P = Patch()
print('v92_09c_phone_fit')
CSS = """
/* ══ v92 fit fixes (item 9c) ══ */
#table-center { width: max-content; max-width: calc(100% - 12px); }
#table-center .center-zone { row-gap: 6px; }
.landing-grid { flex-shrink: 0; }
#screen-character { justify-content: flex-start; }
.char-screen-inner { margin-top: auto; margin-bottom: auto; flex-shrink: 0; }
#screen-winner { justify-content: flex-start; overflow-y: auto; }
#screen-winner > * { flex-shrink: 0; }
#screen-winner > :first-child { margin-top: auto; }
#screen-winner > :last-child { margin-bottom: auto; }
.modal { max-height: calc(100vh - 3rem); max-height: calc(100dvh - 3rem); overflow-y: auto; overscroll-behavior: contain; }
@media (max-width: 599px) {
  #table-center { bottom: 106px; }
  .landing-grid { align-items: flex-start; }
}
@media (max-width: 599px) and (max-height: 700px) {
  :root { --act-h: 118px; }
  .action-card { height: 56px; }
  .action-card .ac-emoji { font-size: var(--fs-base); }
  #table-center { bottom: 104px; }
  .disc-stack { width: 42px; height: 58px; }
  .discard-stacks { min-height: 60px; padding: 3px 8px 4px 2px; gap: 10px; }
  #table-center .center-zone { row-gap: 2px; }
}
"""
P.css(CSS, 'fit fixes')
P.write()
