"""v92 item 10 — reduced-motion path.

One @media (prefers-reduced-motion: reduce) block, kept as the LAST rule in the
stylesheet (later v92 scripts insert above its marker):
  * every animation and transition collapses to 0.01s and runs once;
  * animation DELAYS are kept, so a banner/toast still stays up for its reading
    time and then disappears (no slide, no fade);
  * every looping animation that communicated a state is replaced by the static
    end state of that state: the active-turn frame keeps its bright gold ring,
    my-turn dock keeps its glow, hot coins stay red, the live auction slot stays
    lit, target previews keep a red ring, the recording dot stays solid;
  * signals that were ONLY an animation (verdict stamp, challenge border flash)
    become a still image held for the same duration via steps(1, end), so the
    information survives without motion.
"""
from v92_lib import Patch

P = Patch()
print('v92_10_reduced_motion')

CSS = """
/* ══ v92 reduced motion (item 10) — keep this block LAST in the stylesheet ══ */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01s !important; animation-iteration-count: 1 !important;
    transition-duration: 0.01s !important; transition-delay: 0s !important; scroll-behavior: auto !important; }
  .flash-banner, .flash-banner.long, .toast { animation-duration: 0.01s !important; }
  /* states that were told by a loop, shown still */
  .arena-frame.active-turn .af-body { border-color: var(--gold-5);
    box-shadow: 0 0 0 1px var(--gold-0), 0 0 0 3px rgba(var(--gold-5-rgb),1), 0 0 24px rgba(var(--gold-5-rgb),0.6), inset 0 0 22px rgba(0,0,0,0.75), var(--e3) !important; }
  .arena-frame.active-turn::before, .arena-me.my-turn-glow::before { opacity: 1 !important; }
  .arena-me.my-turn-glow { box-shadow: 0 0 26px rgba(var(--gold-4-rgb),0.55), var(--e-up) !important; }
  .seat.target-preview.arena-frame .af-body { box-shadow: 0 0 0 4px rgba(var(--danger-rgb),0.8), var(--e3) !important; }
  .auction-hist-slot.live-slot, .aph-tile.live { box-shadow: 0 0 12px rgba(var(--gold-4-rgb),0.5) !important; }
  .dc-theme .panel, .dc-theme .waiting-panel { box-shadow: 0 0 18px rgba(var(--contessa-rgb),0.25) !important; }
  .af-coins.hot, .af-coins.maxed, .me-coins.hot { transform: none !important; }
  .av-dot, #tb-paused, .blitz-timer-urgent, .pit-waitface { opacity: 1 !important; }
  .choosing-spinner, .seat-crown, .win-crown, .w-trophy, #landscape-overlay .lo-icon, .dc-rose { animation: none !important; }
  .confetti-piece { display: none !important; }
  /* signals that existed only as motion become a still held for the same time */
  .verdict-stamp.show { animation: v92StampStill 2.2s steps(1, end) forwards !important; }
  .border-pulse-anim { animation: v92BorderStill 1.2s steps(1, end) forwards !important; }
  @keyframes v92StampStill { 0% { transform: translate(-50%,-50%) rotate(-8deg) scale(1); opacity: 1; } 100% { opacity: 0; } }
  @keyframes v92BorderStill { 0% { box-shadow: inset 0 0 0 6px rgba(var(--danger-rgb),0.85); } 100% { box-shadow: none; } }
}
/* ══ end v92 reduced motion ══ */
"""
P.rep("\n</style>\n</head>", CSS + "\n</style>\n</head>", 'reduced-motion block (last rule)')
P.write()
