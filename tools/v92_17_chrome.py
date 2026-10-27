"""v92 item 17 — finish the chrome.

* Scrim: every overlay that sits on top of the game (modal, seat arrangement,
  event log, auction flip/announce, reshuffle banner) uses one blurred scrim
  token (with the -webkit- prefix Safari needs).
* One modal chrome: modal, seat modal, auction boxes, reshuffle box, auction
  settings and the context menu share surface, border, radius, inner highlight
  and e5 elevation; titles share a face and a gold rule.
* Buttons: every button-like control gets hover / active / disabled states
  (zero-specificity :where() so existing per-control styling still wins), and a
  loading state ([aria-busy="true"]: label hidden, spinner shown, clicks
  ignored). The Join button uses it: it goes busy on click and clears on the
  next toast (every join error toasts) or screen change (success).
* Focus: a visible :focus-visible ring (2px gold, 3px offset) on every
  interactive element. The game's clickable <div>s (action cards, respond
  zones, target rows, exchange cards, character cards, mode cards, toggles,
  seat tokens, discard pile, clickable rows) were not focusable at all, so a
  small enhancer gives them tabindex/role and Enter/Space activation; the 1-7
  and P/C/B hotkeys keep working and now have a ring to point at.
* Event log: names become small-caps chips tinted by the player's own colour,
  so they stand out from the body text; body text steps down a level; entries
  get a hairline separator.
"""
from v92_lib import Patch

P = Patch()
print('v92_17_chrome')

# ---- join button: busy state
P.rep('<button class="btn primary" style="flex:1" id="join-btn" onclick="guestJoin()">Join Room</button>',
      '<button class="btn primary" style="flex:1" id="join-btn" onclick="v92Busy(this); guestJoin()">Join Room</button>', 'join button busy state')
P.rep("function toast(msg){", """// v92: presentational busy state for buttons that start async work; cleared by the next toast or screen change
function v92Busy(btn) {
  if (!btn) return;
  btn.setAttribute('aria-busy', 'true');
  clearTimeout(btn._v92busy);
  btn._v92busy = setTimeout(() => btn.removeAttribute('aria-busy'), 8000);
}
function v92ClearBusy() { document.querySelectorAll('[aria-busy="true"]').forEach(b => b.removeAttribute('aria-busy')); }
// v92: make the game's clickable <div>s reachable and operable from the keyboard
(function () {
  const SEL = '.action-card, .respond-zone, .tgt-item, .exch-card, .char-card, .mode-card, .toggle, .seat-token, .discard-stacks, ' +
              '.char-mini-card, .room-code-big, .room-code-mini, .ctx-item, .showcase-card, [onclick]';
  const NATIVE = /^(BUTTON|A|INPUT|SELECT|TEXTAREA|SUMMARY|OPTION|LABEL)$/;
  let queued = false;
  const scan = () => {
    queued = false;
    document.querySelectorAll(SEL).forEach(el => {
      if (NATIVE.test(el.tagName) || el.id === 'modal-overlay' || el.id === 'seat-modal-overlay' || el.classList.contains('auction-flip-overlay')) return;
      const off = el.classList.contains('disabled') || el.classList.contains('taken') || el.classList.contains('ctx-disabled');
      const want = off ? '-1' : '0';
      if (el.getAttribute('tabindex') !== want) el.setAttribute('tabindex', want);
      if (!el.hasAttribute('role')) el.setAttribute('role', el.classList.contains('toggle') ? 'switch' : 'button');
      if (off) el.setAttribute('aria-disabled', 'true'); else el.removeAttribute('aria-disabled');
      if (el.classList.contains('toggle')) el.setAttribute('aria-checked', el.classList.contains('on') ? 'true' : 'false');
    });
  };
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(scan); } };
  new MutationObserver(queue).observe(document.documentElement, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
  document.addEventListener('DOMContentLoaded', scan);
  document.addEventListener('keydown', e => {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const el = e.target;
    if (!el || NATIVE.test(el.tagName) || !el.matches || !el.matches(SEL)) return;
    if (el.getAttribute('aria-disabled') === 'true') return;
    e.preventDefault();
    el.click();
  });
})();
function toast(msg){v92ClearBusy();""", 'busy helpers + keyboard enhancer')
P.rep("function showScr(id) {\n", "function showScr(id) {\n  try { v92ClearBusy(); } catch(e) {}\n", 'screen change clears busy')

BTN = ('button, .btn, .act-btn, .settings-btn, .mode-btn, .mode-card, .lr-tab, .step-btn, .lock-btn, .lobby-chat-send, .wr-back-game-btn, '
       '.wr-change-char-btn, .elim-wr-btn, .cam-panel-btn, .invite-primary, .auction-bid-btn, .asp-toggle, .asp-action, .asp-close, .av-btn, '
       '.arrange-seats-btn, .rules-overlay-close, .elo-close, .lobby-kick-btn, .cpu-char-btn, .mobile-rules-btn, .tgt-item, .ctx-item, .log-toggle, .log-pin')
INTERACTIVE = ('a[href], button, input, select, textarea, summary, [tabindex], [role="button"], [role="switch"], .action-card, .respond-zone, '
               '.tgt-item, .exch-card, .char-card, .mode-card, .toggle, .seat-token, .discard-stacks')

CSS = f"""
/* ══ v92 chrome (item 17) ══ */
:root {{ --scrim: rgba(var(--surface-0-rgb),0.66); --scrim-blur: blur(10px) saturate(1.15); --focus: var(--gold-5); }}
/* one scrim behind everything modal */
.modal-overlay, #seat-modal-overlay, #event-log-overlay, .auction-flip-overlay, #auction-reshuffle-banner {{
  background: var(--scrim); -webkit-backdrop-filter: var(--scrim-blur); backdrop-filter: var(--scrim-blur); }}
/* one modal chrome */
.modal, #seat-modal, .auction-flip-box, .auction-announce-box, .arb-box, #auction-settings-panel {{
  background: linear-gradient(180deg, rgba(var(--gold-4-rgb),0.07), transparent 96px), linear-gradient(160deg, var(--surface-3), var(--surface-2));
  border: 1px solid var(--border-2); border-radius: var(--r-lg);
  box-shadow: inset 0 1px 0 rgba(var(--gold-5-rgb),0.2), inset 0 0 0 1px rgba(0,0,0,0.5), var(--e5); }}
.auction-announce-box {{ border-color: rgba(var(--ok-rgb),0.45); }}
#ctx-menu {{ background: linear-gradient(160deg, var(--surface-3), var(--surface-2)); border: 1px solid var(--border-2);
  border-radius: var(--r-md); box-shadow: inset 0 1px 0 rgba(var(--gold-5-rgb),0.16), var(--e4); }}
.modal-title, .seat-modal-title, .arb-title, .asp-title {{ font-family: var(--font-display); color: var(--gold-4); letter-spacing: 0.12em; }}
.modal-title {{ padding-bottom: 0.55rem; margin-bottom: 0.8rem; border-bottom: 1px solid var(--border-1); }}
/* button states: hover / active / disabled / loading */
:where({BTN}) {{ transition: background-color var(--dur-fast) var(--ease-emphasis), border-color var(--dur-fast) var(--ease-emphasis),
  color var(--dur-fast) var(--ease-emphasis), box-shadow var(--dur-fast) var(--ease-emphasis), filter var(--dur-fast) var(--ease-emphasis),
  transform var(--dur-fast) var(--ease-emphasis), opacity var(--dur-fast) var(--ease-emphasis); }}
:where({BTN}):hover:not(:disabled):not([aria-disabled="true"]) {{ filter: brightness(1.14); }}
:where({BTN}):active:not(:disabled):not([aria-disabled="true"]) {{ filter: brightness(0.9); }}
:where({BTN}):disabled, :where({BTN})[aria-disabled="true"] {{ opacity: 0.38; cursor: not-allowed; filter: grayscale(0.5); box-shadow: none; }}
:where({BTN})[aria-busy="true"] {{ position: relative; color: transparent !important; pointer-events: none; }}
:where({BTN})[aria-busy="true"]::after {{ content: ''; position: absolute; left: 50%; top: 50%; width: 14px; height: 14px; margin: -7px 0 0 -7px;
  inset: auto; opacity: 1; background: none; border-radius: 50%; border: 2px solid rgba(var(--gold-4-rgb),0.3); border-top-color: var(--gold-5);
  animation: spinnerRot 0.8s linear infinite; }}
.btn[aria-busy="true"]::after {{ inset: auto; left: 50%; top: 50%; }}
.action-card.disabled, .respond-zone[aria-disabled="true"] {{ filter: grayscale(0.4); }}
/* focus: one visible ring on everything interactive */
:is({INTERACTIVE}):focus-visible {{ outline: 2px solid var(--focus); outline-offset: 3px; }}
.input:focus-visible, .lobby-chat-input:focus-visible, .timing-slider:focus-visible {{ outline: 2px solid var(--focus); outline-offset: 2px; }}
.action-card:focus-visible, .respond-zone:focus-visible {{ outline-offset: 4px; z-index: 6; }}
:focus:not(:focus-visible) {{ outline: none; }}
/* top bar never wraps its counters */
.tb-right, #tb-round, .tb-room {{ white-space: nowrap; }}
/* event log hierarchy */
.ev {{ color: var(--text-2); border-bottom: 1px solid rgba(var(--text-0-rgb),0.035); }}
.ev.action {{ color: var(--text-1); }}
.ev .ev-name, .ev .ev-tgt {{ font-family: var(--font-label); font-weight: 700; font-variant-caps: all-small-caps; letter-spacing: 0.05em;
  font-size: 1.06em; padding: 0 0.3em 0.05em; border-radius: var(--r-xs);
  background: rgba(var(--text-0-rgb),0.06); background: color-mix(in srgb, currentColor 17%, transparent);
  box-shadow: inset 0 0 0 1px rgba(var(--text-0-rgb),0.06); text-shadow: 0 1px 1px rgba(0,0,0,0.6); }}
.ev.system {{ border-bottom-color: transparent; }}
.log-head {{ color: var(--gold-2); }}
"""
P.css(CSS, 'chrome css')
P.rep(".modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.82); z-index:500; display:flex; align-items:center; justify-content:center; padding:1.5rem; backdrop-filter:blur(6px); }",
      ".modal-overlay { position:fixed; inset:0; z-index:500; display:flex; align-items:center; justify-content:center; padding:1.5rem; }",
      'modal overlay takes the shared scrim')
P.write()
