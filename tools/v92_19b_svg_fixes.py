"""v92 follow-up — SVG correctness found by the verification harness.

* Pre-existing (v91): the auction spotlight drew <rect width="${spotW-3}">
  while its container had not been laid out yet (spotW = 0), so every auction
  logged 'Error: <rect> attribute width: A negative value is not valid ("-3")'
  (18 console errors per viewport in the v91 baseline). The rect size is now
  clamped at 0.
* var() inside SVG presentation attributes (stroke="var(..)") is resolved by
  Chromium but is not guaranteed elsewhere; the three that exist (two auction
  ring strokes, one spotlight stroke) move into style declarations, where
  var() is always valid.
* The face-down auction card's inline entrance used the enter curve as a raw
  cubic-bezier; it now uses the motion tokens like every other entrance.
"""
from v92_lib import Patch

P = Patch()
print('v92_19b_svg_fixes')
P.rep('<rect x="1.5" y="1.5" width="${spotW-3}" height="${spotH-3}" rx="10" ry="10"\n            fill="url(#spot-grad)" stroke="rgba(var(--gold-4-rgb),0.55)" stroke-width="2"/>',
      '<rect x="1.5" y="1.5" width="${Math.max(0, spotW-3)}" height="${Math.max(0, spotH-3)}" rx="10" ry="10"\n            fill="url(#spot-grad)" stroke-width="2" style="stroke:rgba(var(--gold-4-rgb),0.55)"/>',
      'spotlight rect: no negative size; stroke via style')
P.rep('<circle cx="38" cy="38" r="31" fill="none" stroke="var(--surface-4)" stroke-width="5"/>',
      '<circle cx="38" cy="38" r="31" fill="none" stroke-width="5" style="stroke:var(--surface-4)"/>', 'ring track stroke via style')
P.rep('<circle id="auction-ring" cx="38" cy="38" r="31" fill="none" stroke="var(--gold-4)" stroke-width="5"\n            stroke-dasharray="194.8" stroke-dashoffset="0" style="transition:',
      '<circle id="auction-ring" cx="38" cy="38" r="31" fill="none" stroke-width="5"\n            stroke-dasharray="194.8" stroke-dashoffset="0" style="stroke:var(--gold-4);transition:', 'ring stroke via style')
P.rep("animation:auctionCardIn 0.5s cubic-bezier(0.22,1,0.36,1) both", "animation:auctionCardIn var(--dur-slow) var(--ease-enter) both",
      'face-down auction card uses motion tokens')
import re
assert not re.search(r'(fill|stroke|stop-color)="[^"]*var\(', P.src)
assert not re.search(r'cubic-bezier\((?!0\.22, 1, 0\.36, 1\)|0\.55, 0, 1, 0\.45\)|0\.2, 1\.4, 0\.4, 1\)|0\.4, 0, 0\.2, 1\))', P.src)
P.write()
