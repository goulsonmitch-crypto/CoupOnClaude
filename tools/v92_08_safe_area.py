"""v92 item 8 — safe-area insets.

viewport-fit=cover lets the page paint under the Dynamic Island / home
indicator; every edge-pinned surface then pads itself back out with
env(safe-area-inset-*). Each rule is written as a plain fallback declaration
followed by the env() version, so a browser without env() keeps the old
spacing instead of dropping the declaration.

Note: #my-dock lives inside #arena, ABOVE the action area, so it is never at
the physical bottom edge. The bottom inset belongs to whatever IS at the bottom:
#mobile-log on phones, #action-area everywhere else. #my-dock gets the left /
right insets (it spans the width on phones).
"""
from v92_lib import Patch

P = Patch()
print('v92_08_safe_area')
P.rep('<meta name="viewport" content="width=device-width, initial-scale=1.0">',
      '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">', 'viewport-fit=cover')

T, R, B, L = ('env(safe-area-inset-top, 0px)', 'env(safe-area-inset-right, 0px)',
              'env(safe-area-inset-bottom, 0px)', 'env(safe-area-inset-left, 0px)')
def pad(prop, base, inset):
    return f'{prop}: {base}; {prop}: calc({base} + {inset});'

CSS = f"""
/* ══ v92 safe areas (item 8): fallback line first, env() second ══ */
#top-bar {{ {pad('padding-top', '0.5rem', T)} {pad('padding-left', '0.9rem', L)} {pad('padding-right', '0.9rem', R)} }}
#action-area {{ {pad('margin-left', '0.6rem', L)} {pad('margin-right', '0.6rem', R)} {pad('padding-bottom', '0.7rem', B)} }}
#event-log-col {{ {pad('padding-right', '0px', R)} }}
#toast-area {{ {pad('top', '1rem', T)} }}
#av-fab {{ {pad('top', '52px', T)} {pad('right', '10px', R)} }}
.av-strip {{ {pad('top', '62px', T)} {pad('left', '8px', L)} }}
.rules-overlay-header {{ {pad('padding-top', '1.1rem', T)} {pad('padding-left', '1.2rem', L)} {pad('padding-right', '1.2rem', R)} }}
.rules-overlay-body {{ {pad('padding-bottom', '3rem', B)} {pad('padding-left', '1.2rem', L)} {pad('padding-right', '1.2rem', R)} }}
.elo-header {{ {pad('padding-top', '0.8rem', T)} }}
#event-log-overlay-list {{ {pad('padding-bottom', '0.5rem', B)} }}
.modal-overlay, #seat-modal-overlay {{ padding: 1.5rem;
  padding: max(1.5rem, {T}) max(1.5rem, {R}) max(1.5rem, {B}) max(1.5rem, {L}); }}
#auction-reshuffle-banner, .auction-flip-overlay {{ padding: 1rem; padding: max(1rem, {T}) max(1rem, {R}) max(1rem, {B}) max(1rem, {L}); }}
#screen-landing, #screen-lobby, #screen-character {{ {pad('padding-top', '1.5rem', T)} {pad('padding-bottom', '1.5rem', B)} {pad('padding-left', '1.5rem', L)} {pad('padding-right', '1.5rem', R)} }}
#screen-waiting {{ {pad('padding-top', '2rem', T)} {pad('padding-bottom', '2rem', B)} {pad('padding-left', '1.5rem', L)} {pad('padding-right', '1.5rem', R)} }}
#screen-reveal {{ {pad('padding-top', '1.5rem', T)} {pad('padding-bottom', '1.5rem', B)} {pad('padding-left', '1rem', L)} {pad('padding-right', '1rem', R)} }}
#screen-winner {{ {pad('padding-top', '2rem', T)} {pad('padding-bottom', '2rem', B)} }}
#recap-overlay {{ padding-top: 2.5rem !important; padding-top: calc(2.5rem + {T}) !important;
  padding-bottom: 2rem !important; padding-bottom: calc(2rem + {B}) !important; }}
#auction-settings-btn {{ {pad('top', '10px', T)} {pad('right', '12px', R)} }}
@media (max-width: 720px) {{
  #screen-landing {{ {pad('padding-top', '1.6rem', T)} {pad('padding-bottom', '2rem', B)} {pad('padding-left', '1rem', L)} {pad('padding-right', '1rem', R)} }}
  .av-strip {{ {pad('bottom', '4px', B)} {pad('left', '4px', L)} {pad('right', '4px', R)} }}
}}
@media (max-width: 560px) {{
  #action-area {{ padding-bottom: 0.7rem; }}
  #mobile-log {{ {pad('padding-bottom', '0.3rem', B)} {pad('padding-left', '0.9rem', L)} {pad('padding-right', '0.9rem', R)}
    min-height: 1.6rem; min-height: calc(1.6rem + {B}); }}
}}
@media (max-width: 768px) and (orientation: portrait) {{
  #my-dock {{ width: calc(100% - 8px); width: calc(100% - 8px - {L} - {R}); }}
}}
"""
P.rep("\n</style>\n</head>", CSS + "\n</style>\n</head>", 'safe-area block')
P.write()
