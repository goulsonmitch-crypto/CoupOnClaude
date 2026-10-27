"""v92 item 11 — GPU-promote the animated layers.

No CSS keyframe animated top/left/width/height, but three things forced layout
or full repaints every frame:
  * the card-loss slide (animateCardLoss) transitioned `left`/`top`;
  * the settings toggle knob transitioned `left`;
  * the state pulses (active-turn frame, my-turn dock, target preview, frame
    hit flash, live auction slot) animated box-shadow, i.e. repainted a large
    blurred shadow 60 times a second for as long as the state lasted.
Now:
  * the card-loss slide and toggle knob move with transform only;
  * each pulse is a static ring plus a pre-painted glow layer (::before) whose
    OPACITY animates — compositor-only — with will-change scoped to the state
    class, so the promotion disappears the moment the state does;
  * transient flyers (flying cards/coins/action cards, confetti, verdict stamp,
    banners, toasts) carry will-change and are removed from the DOM after;
  * persistent elements with one-shot entrances (modal, claim bubble, intro
    bubble, winner frame, auction cards, log rows) are promoted on animationstart
    and demoted on animationend, so nothing holds compositor memory after;
  * the timer track is a layout/paint containment boundary, so its 4Hz width
    tick never relayouts the action area.
Also: coin flights have been silently dead since v74 — _findPlayerCoinEl looked
for .seat-coins, which the arena no longer renders. It now finds .af-coins /
.me-coins, so coins arc between seats again (transform-only keyframes). The
counter tick skips elements that contain markup (the dock's coin line holds a
nested span the tick would have wiped); renderGame paints the final value.
"""
from v92_lib import Patch

P = Patch()
print('v92_11_gpu')

# ---- card-loss slide: transform, not left/top
P.rep("""  requestAnimationFrame(() => {
    fly.style.transition = 'left 0.55s cubic-bezier(.3,.7,.4,1), top 0.55s cubic-bezier(.3,.7,.4,1), opacity 0.3s ease 0.4s, transform 0.55s ease';
    fly.style.left = tx + 'px'; fly.style.top = ty + 'px';
    fly.style.transform = 'scale(0.8)'; fly.style.opacity = '0.7';
    setTimeout(() => fly.remove(), 900);
  });""",
"""  fly.style.willChange = 'transform, opacity';
  requestAnimationFrame(() => {
    fly.style.transition = 'transform 0.55s var(--ease-enter), opacity 0.3s var(--ease-exit) 0.4s';
    fly.style.transform = `translate(${tx - sR.left}px, ${ty - sR.top}px) scale(0.8)`; fly.style.opacity = '0.7';
    setTimeout(() => fly.remove(), 900);
  });""", 'card-loss slide uses transform')

# ---- coin flights: find the arena's coin labels again
P.rep("      return s.querySelector('.seat-coins') || s.querySelector('.opp-coins') || null;",
      "      return s.querySelector('.seat-coins') || s.querySelector('.opp-coins') || s.querySelector('.af-coins') || s.querySelector('.me-coins') || null;",
      'coin flights target .af-coins / .me-coins')
P.rep("function _tickCoinEl(el, delta) {\n", "function _tickCoinEl(el, delta) {\n  if (el.children && el.children.length) return;   // v92: never wipe nested markup; renderGame paints the total\n",
      'coin tick leaves structured labels alone')

# ---- toggle knob
P.rep(".toggle.on::after { left:21px; background:var(--gold-4); }",
      ".toggle.on::after { transform:translateX(18px); background:var(--gold-4); }", 'toggle knob uses transform')

# ---- promote one-shot entrances only while they run
P.rep("function toast(msg){", """// v92: promote one-shot entrance animations for exactly as long as they run
(function () {
  const ENTER = new Set(['modIn', 'claimBubbleIn', 'bubbleIn', 'winFrameIn', 'auctionCardIn', 'auctionCardOut', 'evIn', 'fadeIn', 'pitCardIn', 'cardFlipIn']);
  document.addEventListener('animationstart', e => { if (ENTER.has(e.animationName) && e.target.style) e.target.style.willChange = 'transform, opacity'; }, true);
  const done = e => { if (ENTER.has(e.animationName) && e.target.style) e.target.style.willChange = 'auto'; };
  document.addEventListener('animationend', done, true);
  document.addEventListener('animationcancel', done, true);
})();
function toast(msg){""", 'animation-scoped will-change')

# ---- pulses: static ring + opacity glow layer
P.rep(".arena-frame.active-turn .af-body { animation: framePulse 1.8s ease-in-out infinite; border-color:var(--gold-5); }",
      ".arena-frame.active-turn .af-body { border-color:var(--gold-5);\n"
      "  box-shadow: 0 0 0 1px var(--gold-0), 0 0 0 3px rgba(var(--gold-5-rgb),0.9), inset 0 0 22px rgba(0,0,0,0.75), var(--e3); }",
      'active frame: static ring (glow moves to a layer)')
P.rep(".arena-me.my-turn-glow { animation: dockPulse 2s ease-in-out infinite; border-color: var(--gold-4); }",
      ".arena-me.my-turn-glow { border-color: var(--gold-4); }", 'dock: glow moves to a layer')
P.rep(".arena-frame.targeted .af-body { animation: targetedFlash 0.5s ease 3; }", "", 'frame hit flash moves to a layer')
P.rep(".seat.target-preview.arena-frame .af-body { animation: targetPulse 1s ease-in-out infinite; }",
      ".seat.target-preview.arena-frame .af-body { box-shadow: 0 0 0 1px var(--gold-0), 0 0 0 3px rgba(var(--danger-rgb),0.75), inset 0 0 22px rgba(0,0,0,0.75), var(--e3); }",
      'target preview: static red ring')
P.rep(".auction-hist-slot.live-slot { border:1px solid var(--gold-4); background:rgba(var(--gold-4-rgb),0.08); box-shadow:0 0 8px rgba(var(--gold-4-rgb),0.25); animation:auctionLivePulse 1.4s ease-in-out infinite; }",
      ".auction-hist-slot.live-slot { position:relative; border:1px solid var(--gold-4); background:rgba(var(--gold-4-rgb),0.08); box-shadow:0 0 8px rgba(var(--gold-4-rgb),0.25); }",
      'live auction slot: static ring')
P.rep("  .aph-tile.live { background:rgba(var(--gold-4-rgb),0.08); border:1px solid var(--gold-4); box-shadow:0 0 10px rgba(var(--gold-4-rgb),0.4); animation:auctionLivePulse 1.4s ease-in-out infinite; }",
      "  .aph-tile.live { position:relative; background:rgba(var(--gold-4-rgb),0.08); border:1px solid var(--gold-4); box-shadow:0 0 10px rgba(var(--gold-4-rgb),0.4); }",
      'phone live auction tile: static ring')

CSS = """
/* ══ v92 GPU layers (item 11) ══ */
/* pulses: the glow is painted once; only its opacity animates (compositor-only) */
.arena-frame::before, .arena-me::before, .auction-hist-slot.live-slot::after, .aph-tile.live::after {
  content: ''; position: absolute; pointer-events: none; opacity: 0; border-radius: inherit; }
.arena-frame::before { inset: -3px -3px 26px -3px; z-index: -1; border-radius: var(--r-md); }
.arena-me { position: relative; isolation: isolate; }
.arena-me::before { inset: -1px; z-index: -1; box-shadow: 0 0 30px rgba(var(--gold-4-rgb),0.65); }
.arena-frame.active-turn::before { box-shadow: 0 0 30px rgba(var(--gold-5-rgb),0.7), 0 0 0 2px rgba(var(--gold-5-rgb),0.55);
  will-change: opacity; animation: v92Glow 1.8s ease-in-out infinite; }
.arena-me.my-turn-glow::before { will-change: opacity; animation: v92Glow 2s ease-in-out infinite; }
.seat.target-preview.arena-frame::before { box-shadow: 0 0 0 4px rgba(var(--danger-rgb),0.85), 0 0 22px rgba(var(--danger-rgb),0.55);
  will-change: opacity; animation: v92Glow 1s ease-in-out infinite; }
.arena-frame.targeted::before { box-shadow: 0 0 26px rgba(var(--danger-rgb),0.8), 0 0 0 3px rgba(var(--danger-rgb),0.8);
  will-change: opacity; animation: v92Flash 0.5s ease 3; }
.auction-hist-slot.live-slot::after, .aph-tile.live::after { inset: -1px; box-shadow: 0 0 14px rgba(var(--gold-4-rgb),0.55);
  will-change: opacity; animation: v92Glow 1.4s ease-in-out infinite; }
@keyframes v92Glow { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }
@keyframes v92Flash { 0%, 100% { opacity: 0; } 50% { opacity: 1; } }
/* transient flyers: promoted for their whole (short) life, then removed from the DOM */
.flying-card, .flying-coin, .ac-flying, .confetti-piece, .verdict-stamp.show, .flash-banner, .toast { will-change: transform, opacity; }
.pit-card { will-change: transform; }
/* the timer bar ticks its width; keep that layout inside the track */
.timer-track { contain: layout paint; }
"""
P.css(CSS, 'GPU layer css')
P.write()
