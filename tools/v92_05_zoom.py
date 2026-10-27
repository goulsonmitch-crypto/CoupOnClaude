"""v92 item 5 — restore pinch zoom.

* Viewport meta drops maximum-scale=1.0 and user-scalable=no.
* Interactive controls get touch-action: manipulation, which removes the
  double-tap-to-zoom delay on the controls only; pinch zoom stays available
  everywhere.
* With zoom allowed again, iOS Safari would auto-zoom the page whenever an
  input with text under 16px gets focus. Coarse-pointer devices get 16px inputs.
"""
from v92_lib import Patch

P = Patch()
print('v92_05_zoom')
P.rep('<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">',
      '<meta name="viewport" content="width=device-width, initial-scale=1.0">', 'viewport allows pinch zoom')
CSS = """
/* ══ v92 touch (item 5): zoom is allowed; only the controls opt out of double-tap zoom ══ */
button, .btn, input, select, textarea, label, [onclick], [role="button"], .action-card, .respond-zone, .tgt-item,
.exch-card, .char-card, .mode-card, .toggle, .seat-token, .lr-tab, .settings-btn, .discard-stacks, .arena-frame {
  touch-action: manipulation; }
@media (pointer: coarse) {
  input:not([type="range"]):not([type="checkbox"]), select, textarea { font-size: max(16px, 1em); }
}
"""
P.rep("\n</style>\n</head>", CSS + "\n</style>\n</head>", 'touch-action block')
P.write()
