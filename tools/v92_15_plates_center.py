"""v92 item 15 — engrave the nameplates and the table centre.

* .af-plate becomes a brass plaque: brushed-metal gradient, bevelled top edge,
  an inset rim, two screw heads, and letterpress (engraved) text.
* Treasury coins get a milled rim, an inner groove, a specular rim-light and a
  visible edge thickness, so the pile reads as coins, not flat dots.
* Card backs (deck, face-down seat cards, face-down flights) share one
  patterned back: a gold diamond lattice on plum, an inset frame line and a
  centre medallion. The deck shows its thickness: up to 6 layers stacked 2px
  apart (was 4 layers 4px apart at 55% opacity), each with a pale page edge.
* Discard stacks are rebuilt larger — 62x86 on desktop, 46x64 on phones — with
  the role colour on every layer, offset layers each casting their own shadow
  (so three cards look like three cards) and the role name on a ribbon across
  the top card in the label face.
"""
from v92_lib import Patch

P = Patch()
print('v92_15_plates_center')

# ---- deck: thinner, more layers
P.rep("""  const deckLayers = Math.min(4, deckSize);
  let deckCards = '';
  for (let i = 0; i < deckLayers; i++) deckCards += `<div class="deck-card" style="top:${i*4}px;left:${i*3}px;z-index:${i}"></div>`;
  const deckH = 68 + (deckLayers-1)*4, deckW = 50 + (deckLayers-1)*3;""",
"""  // v92: the stack shows its thickness — one layer per ~2.5 cards, 2px apart
  const deckLayers = deckSize ? Math.min(6, Math.max(1, Math.ceil(deckSize / 2.5))) : 0;
  let deckCards = '';
  for (let i = 0; i < deckLayers; i++) deckCards += `<div class="deck-card${i === deckLayers - 1 ? ' deck-top' : ''}" style="top:${i*2}px;left:${i*1.5}px;z-index:${i}"></div>`;
  const deckH = 68 + Math.max(0, deckLayers-1)*2, deckW = 50 + Math.max(0, deckLayers-1)*1.5;""", 'deck layers 2px apart, up to 6')

# ---- discard stacks: name ribbon + larger offsets
P.rep("""    for (let i = Math.min(n, 3) - 1; i >= 1; i--)
      inner += `<div class="disc-layer ${role}" style="transform:translate(${i*3}px,${-i*3}px);z-index:${10-i}"></div>`;
    inner += `<div class="disc-top ${role}" style="z-index:20">${portraitFor(role,'small')}</div>`;""",
"""    for (let i = Math.min(n, 3) - 1; i >= 1; i--)
      inner += `<div class="disc-layer ${role}" style="transform:translate(${i*4}px,${-i*4}px);z-index:${10-i}"></div>`;
    inner += `<div class="disc-top ${role}" style="z-index:20">${portraitFor(role,'small')}<div class="disc-name">${d.name||role}</div></div>`;""",
      'discard stack ribbon + offsets')

CSS = """
/* ══ v92 nameplates + table centre (item 15) ══ */
/* brass plaque */
.af-plate { position: relative; margin-top: 6px; padding: 3px 12px; border-radius: var(--r-xs); border: 1px solid var(--gold-1);
  background:
    linear-gradient(180deg, rgba(255,250,232,0.6) 0, rgba(255,250,232,0) 2px),
    repeating-linear-gradient(90deg, rgba(255,255,255,0.05) 0 1px, rgba(0,0,0,0.035) 1px 3px),
    linear-gradient(180deg, var(--gold-5) 0%, var(--gold-4) 34%, var(--gold-3) 72%, var(--gold-2) 100%);
  box-shadow: inset 0 1px 0 rgba(255,248,220,0.55), inset 0 -1px 0 rgba(0,0,0,0.35), inset 0 0 0 2px rgba(var(--gold-5-rgb),0.18),
    0 1px 0 var(--gold-0), var(--e2); }
.af-plate::before, .af-plate::after { content: ''; position: absolute; top: 50%; width: 5px; height: 5px; margin-top: -2.5px; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, var(--gold-5) 0, var(--gold-3) 45%, var(--gold-1) 100%);
  box-shadow: inset 0 0 0 0.5px rgba(0,0,0,0.55), 0 1px 0 rgba(255,248,220,0.4); }
.af-plate::before { left: 4px; } .af-plate::after { right: 4px; }
.af-name, .af-coins, .af-plate .af-cpu { color: var(--gold-0); text-shadow: 0 1px 0 rgba(255,244,210,0.6), 0 -1px 0 rgba(0,0,0,0.28); }
.af-coins.hot { text-shadow: 0 1px 0 rgba(255,244,210,0.6), 0 0 6px rgba(255,220,120,0.9); }
@media (max-width: 599px) {
  .af-plate { padding: 1px 4px; margin-top: 4px; }
  .af-plate::before, .af-plate::after { display: none; }
}
/* treasury: milled coins with a rim-light and an edge */
.t-pile { height: 46px; }
.t-coin { width: 22px; height: 18px; border: 1px solid var(--gold-1);
  background:
    radial-gradient(ellipse at 50% 50%, transparent 52%, rgba(0,0,0,0.28) 55%, rgba(255,240,200,0.25) 60%, transparent 64%),
    radial-gradient(ellipse at 34% 26%, rgba(255,250,225,0.95) 0, rgba(255,250,225,0) 30%),
    radial-gradient(ellipse at 50% 55%, var(--gold-5) 0%, var(--gold-4) 46%, var(--gold-3) 66%, var(--gold-2) 100%);
  box-shadow: inset 0 -2px 2px rgba(0,0,0,0.3), inset 0 1px 1px rgba(255,245,210,0.7),
    0 1px 0 var(--gold-3), 0 2px 0 var(--gold-2), 0 3px 0 var(--gold-1), 0 4px 5px rgba(0,0,0,0.55); }
/* one patterned card back everywhere */
.deck-card, .seat-card.face-down, .flying-card.face-down-fly {
  background:
    radial-gradient(circle at 50% 50%, rgba(var(--gold-4-rgb),0.30) 0 15%, rgba(var(--gold-4-rgb),0) 16%),
    radial-gradient(circle at 50% 50%, transparent 0 24%, rgba(var(--gold-4-rgb),0.22) 25% 27%, transparent 28%),
    repeating-linear-gradient(45deg, rgba(var(--gold-4-rgb),0.13) 0 1px, transparent 1px 6px),
    repeating-linear-gradient(-45deg, rgba(var(--gold-4-rgb),0.13) 0 1px, transparent 1px 6px),
    linear-gradient(160deg, var(--surface-4), var(--surface-2));
  border-color: var(--gold-2);
  box-shadow: inset 0 0 0 2px var(--surface-1), inset 0 0 0 3px rgba(var(--gold-4-rgb),0.35), var(--e1); }
.seat-card.face-down::after, .flying-card.face-down-fly .card-back-mark { color: var(--gold-4); opacity: 0.8; text-shadow: 0 1px 2px var(--ink); }
.deck-card { opacity: 1; color: transparent; border: 1.5px solid var(--gold-2);
  box-shadow: inset 0 0 0 2px var(--surface-1), inset 0 0 0 3px rgba(var(--gold-4-rgb),0.3), -1px -1px 0 rgba(var(--parchment-rgb),0.28), var(--e1); }
.deck-card.deck-top { box-shadow: inset 0 0 0 2px var(--surface-1), inset 0 0 0 3px rgba(var(--gold-4-rgb),0.4), -1px -1px 0 rgba(var(--parchment-rgb),0.32), var(--e2); }
.deck-card.deck-top::after { content: '⚜'; color: var(--gold-4); font-size: var(--fs-lg); text-shadow: 0 1px 2px var(--ink); }
/* discard stacks: three cards look like three cards */
.discard-stacks { gap: 18px; min-height: 96px; padding: 8px 14px 10px 4px; }
.disc-stack { width: 62px; height: 86px; }
/* the stack container also carries .seat-card (overflow:hidden, border, padding), which clipped
   the offset layers and the xN badge in v91 — neutralise it so the stack can show its depth */
.disc-stack.seat-card { overflow: visible; border: 0; background: none; box-shadow: none; padding: 0; }
.disc-top { overflow: visible; }
.disc-top .portrait-wrap { overflow: hidden; border-radius: var(--r-xs); }
.disc-layer, .disc-top { border-width: 2px; border-radius: var(--r-sm); }
.disc-layer { opacity: 1; filter: brightness(0.62); box-shadow: 2px 3px 6px rgba(0,0,0,0.55); }
.disc-top { box-shadow: 3px 5px 10px rgba(0,0,0,0.6), 1px 1px 2px rgba(0,0,0,0.5); flex-direction: column; justify-content: flex-start; padding-top: 6px; }
.disc-top .portrait-wrap { transform: scale(0.95); }
.disc-name { position: absolute; left: -1px; right: -1px; bottom: 5px; padding: 2px 0 3px; text-align: center; white-space: nowrap;
  font-family: var(--font-label); font-weight: 700; font-variant-caps: all-small-caps; font-size: var(--fs-xs); letter-spacing: 0.04em;
  color: var(--text-0); background: linear-gradient(90deg, rgba(0,0,0,0.25), rgba(0,0,0,0.72) 20% 80%, rgba(0,0,0,0.25));
  text-shadow: 0 1px 2px var(--ink); }
.disc-layer.duke, .disc-top.duke { border-color: var(--duke); background: linear-gradient(160deg, rgba(var(--duke-rgb),0.55), var(--duke-shade)); }
.disc-layer.assassin, .disc-top.assassin { border-color: var(--assassin); background: linear-gradient(160deg, rgba(150,140,160,0.5), var(--assassin-shade)); }
.disc-layer.captain, .disc-top.captain { border-color: var(--captain); background: linear-gradient(160deg, rgba(var(--captain-rgb),0.55), var(--captain-shade)); }
.disc-layer.ambassador, .disc-top.ambassador { border-color: var(--ambassador); background: linear-gradient(160deg, rgba(var(--ambassador-rgb),0.55), var(--ambassador-shade)); }
.disc-layer.contessa, .disc-top.contessa { border-color: var(--contessa); background: linear-gradient(160deg, rgba(var(--contessa-rgb),0.55), var(--contessa-shade)); }
.disc-badge { bottom: -8px; right: -9px; z-index: 40; }
@media (max-width: 599px) {
  .discard-stacks { gap: 12px; min-height: 72px; padding: 6px 10px 8px 2px; }
  .disc-stack { width: 46px; height: 64px; }
  .disc-top { padding-top: 3px; }
  .disc-top .portrait-wrap { transform: scale(0.7); }
  .disc-name { left: -5px; right: -5px; bottom: 3px; letter-spacing: 0; }
  .disc-layer { box-shadow: 1px 2px 4px rgba(0,0,0,0.55); }
}
"""
P.css(CSS, 'plates + centre css')
# the phone rule shrinking the old 34x48 stacks would now fight the new phone size
P.rep("  .disc-stack { width:34px; height:48px; }\n", "", 'drop the v91 phone stack size')
P.write()
