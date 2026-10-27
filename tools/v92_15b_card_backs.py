"""v92 item 15 (follow-up) — the auction deck uses the same card back.

The verification screenshots showed the auction deck, its top card and the
face-down dealing card still in v91's plain diagonal stripes while every other
card back now shares the patterned back from item 15. They join it here (the
dealing card's inline background moves to the shared class).
"""
from v92_lib import Patch

P = Patch()
print('v92_15b_card_backs')
P.rep("""            background:repeating-linear-gradient(45deg,var(--surface-3),var(--surface-3) 5px,var(--surface-4) 5px,var(--surface-4) 10px);
            border:1.5px solid rgba(100,80,140,0.55);box-shadow:var(--e3);""",
      """            border:1.5px solid var(--gold-2);box-shadow:var(--e3);""", 'dealing card drops its inline stripes')
P.rep("""        cardArea.innerHTML = `
          <div style="width:${spotW}px;height:${spotH}px;border-radius:var(--r-md);""",
      """        cardArea.innerHTML = `
          <div class="v92-back" style="width:${spotW}px;height:${spotH}px;border-radius:var(--r-md);""", 'dealing card takes the shared back')
P.css("""
/* ══ v92 card backs (item 15b): auction deck joins the shared back ══ */
.auction-deck-card, .auction-card-back, .v92-back {
  background:
    radial-gradient(circle at 50% 50%, rgba(var(--gold-4-rgb),0.30) 0 13%, rgba(var(--gold-4-rgb),0) 14%),
    radial-gradient(circle at 50% 50%, transparent 0 21%, rgba(var(--gold-4-rgb),0.22) 22% 24%, transparent 25%),
    repeating-linear-gradient(45deg, rgba(var(--gold-4-rgb),0.13) 0 1px, transparent 1px 7px),
    repeating-linear-gradient(-45deg, rgba(var(--gold-4-rgb),0.13) 0 1px, transparent 1px 7px),
    linear-gradient(160deg, var(--surface-4), var(--surface-2));
  border-color: var(--gold-2);
  box-shadow: inset 0 0 0 3px var(--surface-1), inset 0 0 0 4px rgba(var(--gold-4-rgb),0.35), var(--e2); }
.auction-deck-card { box-shadow: inset 0 0 0 3px var(--surface-1), inset 0 0 0 4px rgba(var(--gold-4-rgb),0.3), -1px -1px 0 rgba(var(--parchment-rgb),0.25), var(--e1); }
""", 'shared back css')
P.write()
