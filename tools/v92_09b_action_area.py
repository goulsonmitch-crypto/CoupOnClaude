"""v92 item 9 (follow-up) — the action area keeps one height for the whole game.

v91 measured (cpu_game harness): #action-area was 69px while waiting and 177px
on your turn on desktop (69 -> 258px on an iPhone, where the 5-7 cards wrapped),
so the whole table jumped every turn.

* #act-btns has a fixed height per breakpoint (--act-h), sized for the tallest
  content it ever holds (a full hand of action cards); waiting / responding /
  resolving states centre inside the same box.
* The phase label is a single line (ellipsis), so it can't add a row.
* The "10+ coins — must Coup" / Double Contessa notes become a pill floating
  over the top edge of the cards instead of a new line under them.
* Desktop action cards widen to 90px so the raised 11px Cinzel names fit
  ("ASSASSINATE" is 78px wide). Phones lay the cards out as a centred 4-up wrap
  (two rows max for all seven actions) with names in the label face; touch
  devices hide the 1-7 hotkey hints.
"""
from v92_lib import Patch

P = Patch()
print('v92_09b_action_area')

P.rep("if (mustCoup) { const n = document.createElement('div'); n.style.cssText='font-size:var(--fs-xs);color:var(--danger);width:100%;text-align:center;padding-top:0.2rem;'; n.textContent=t('must_coup'); container.appendChild(n); }",
      "if (mustCoup) { const n = document.createElement('div'); n.className='act-note act-note-danger'; n.textContent=t('must_coup'); container.appendChild(n); }",
      'must-coup note -> pill')
P.rep("if (dcLocked) { const n = document.createElement('div'); n.style.cssText='font-size:var(--fs-xs);color:var(--duke-tint);width:100%;text-align:center;padding-top:0.3rem;'; n.textContent='🌹🌹 Double Contessa — no Income / Foreign Aid'; container.appendChild(n); }",
      "if (dcLocked) { const n = document.createElement('div'); n.className='act-note act-note-duke'; n.textContent='🌹🌹 Double Contessa — no Income / Foreign Aid'; container.appendChild(n); }",
      'dc note -> pill')

CSS = """
/* ══ v92 action area (item 9b): one height for every phase ══ */
:root { --act-h: 114px; }
#act-btns { position: relative; height: var(--act-h); align-items: center; align-content: center; }
.phase-label { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; height: 1.5em; line-height: 1.5em; min-height: 0; }
.timer-row { height: 18px; }
.action-card { width: 90px; }
.action-card .ac-name { letter-spacing: 0.03em; padding: 0 3px; }
.act-note { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); z-index: 7; pointer-events: none;
  padding: 2px 10px; border-radius: var(--r-pill); font-size: var(--fs-xs); white-space: nowrap;
  background: var(--surface-2); border: 1px solid currentColor; box-shadow: var(--e2); }
.act-note-danger { color: var(--danger); }
.act-note-duke { color: var(--duke-tint); }
@media (pointer: coarse) { .action-card .ac-key { display: none; } }
@media (min-width: 600px) and (max-width: 1023px) {
  :root { --act-h: 108px; }
  .action-card { width: 80px; }
  .action-card .ac-name { font-family: var(--font-label); letter-spacing: 0.02em; }
}
@media (max-width: 599px) {
  :root { --act-h: 134px; }
  .action-fan { width: 100%; gap: 6px; padding-top: 0; align-items: stretch; }
  .action-card { flex: 0 0 calc(25% - 4.5px); width: auto; height: 64px; gap: 1px; transform: none;
    border-radius: var(--r-sm); }
  .action-card:hover:not(.disabled) { transform: translateY(-3px); }
  .action-card:active:not(.disabled) { transform: translateY(-1px); }
  .action-card .ac-emoji { font-size: var(--fs-lg); }
  .action-card .ac-name { font-family: var(--font-label); letter-spacing: 0.02em; line-height: 1.05; }
  .respond-zones { gap: 6px; }
  .respond-zone { min-width: 0; flex: 1 1 calc(50% - 6px); padding: 0.55rem 0.5rem; }
}
"""
P.rep("\n</style>\n</head>", CSS + "\n</style>\n</head>", 'action area block')
P.write()
