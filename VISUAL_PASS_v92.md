# COUP v92 — Visual Pass

`index.html` (and its byte-identical twin `coup_v92.html`) now reads **VERSION 92 · LIVE AT THE TABLE**.
This was a presentation-only pass over the v91 build (`27ea1a3`). Game rules, action resolution,
challenge/block logic, modes, the timer system, turn flow, CPU AI, Firebase, the crypto layer and WebRTC
signalling are untouched. With the seeded harness, a v91 and a v92 game played under the same conditions
reach the same turn count and the same winner (checked at 360×640, where both builds play an identical 32-turn game).

## Verification: all green

| Check | Result |
|---|---|
| Asset integrity (`tools/verify_assets.py`) | **All 32/32 WebP md5s unchanged** (combined `160339442b6912e30b2c083ee57b219d`). Checked after every one of the 25 patch scripts and on `coup_v92.html`. |
| Reproducible build (`tools/run_all.sh`) | Replaying all 25 scripts in order against the v91 file produces a file **byte-identical** to the committed `index.html`. |
| File parses (`tools/harness/parse_check.js`) | 3 inline scripts compile; stylesheet braces balanced (1327/1327). |
| File weight | 1,224,420 → 1,289,758 bytes (**+5.34%**, inside ±8%). |
| `coup_v92.html` | Byte-identical to `index.html` (md5 `f9964a53a910f38fba92fa2f91d4df08`). |
| Screenshots | 9 screens × 5 viewports captured **before and after** (45 pairs below). **0 pageerror, 0 console errors** at every viewport. v91 logged 18 console errors per viewport; that was a pre-existing SVG bug, fixed here. |
| Full CPU game, end to end, at all 5 viewports (`cpu_game.js`) | **5/5 complete** (deal → turns → reveal → winner), 0 pageerror, 0 console errors. |
| No text under 11px (`checks.js`, 10 states × 5 viewports) | **0 violations.** Smallest computed size: v91 **6.08px** → v92 **11.24px**. v91 had 813 sub-11px text-node violations. |
| No overflow (same 50 states) | **0 violations** (v91: 7) |
| No portrait above 1.0× (`portraits.js`, all 20 crew × 6 contexts × 4 viewports at the largest frame sizes) | **0 violations**. The worst case is Nachum at 0.922×, a 277px-tall source (table below). |
| Action-area height constant between turns | **One height per viewport for the whole game**: 185px on desktop/iPad, 205px on iPhone, 189px on 360×640. v91 swung 69→177px on desktop and 69→258px on iPhone. |
| `:focus-visible` ring on every interactive element | **567/567 pass** (v91: 204 of 517 failed, mostly unfocusable clickable divs). |
| Reduced motion (`motion.js`) | Under `prefers-reduced-motion: reduce`, nothing runs longer than 10ms or loops, and the active-turn frame still shows its full gold ring and glow. |
| GPU layers (`motion.js`) | No keyframe animates top/left/width/height. With the table settled, `will-change` is held only by the live state layer, so nothing leaks. |

Browser: Playwright 1.63 + its bundled Chromium (pre-installed, so no install or apt fallback was needed),
served over `python3 -m http.server` (localhost = secure context).

## Measured numbers, before → after

| Metric | v91 | v92 |
|---|---|---|
| Hex colour literals | 542 in the file (24 were `:root` definitions, 518 outside) | **0 outside `:root`.** 168 values now exist only as token definitions. |
| `:root` tokens | 25 (the brief said 26; there are 25) | 208 design + illustration + character tokens |
| `rgba()` literals on the main families | 440 total | 325 moved to `rgba(var(--x-rgb), a)` channel tokens |
| `box-shadow` declarations | 102 one-offs | 41 use the elevation scale (`--e1…--e5`, `--e-up`). 58 are pure state (glow/ring/inset) and stay as layers next to the token. 3 are `none`/`inherit`. |
| `border-radius` declarations | 142, ~20 distinct values | all on 5 tokens (`--r-xs/sm/md/lg/pill`); the 14 `50%` circles stay circles |
| `font-family` declarations | 125 literals | 123 on family tokens + 2 `inherit` |
| `font-size` declarations | 353 (143 below 11px; the smallest was 0.34rem = 5.4px) | all on a 1.125 modular scale, floor 11.24px; 8 `em` sizes and 1 `clamp()` floored |
| `font-variant-numeric` / smoothing / `font-feature-settings` | 0 / 0 / 0 | tabular lining numerals on every live number; antialiasing + kerning hints |
| `vh` units | **3** plain `vh` + 1 `dvh` (the brief said 23; the measured count is 3) | 4 `dvh`/`svh`, each with a `vh` fallback line |
| `env(safe-area-inset-*)` | 0 | 60 uses, each after a plain fallback declaration |
| Width breakpoints | 8 widths (380/560/640/720/768/900/1000/1150), 2 syntaxes | 4 named: phone ≤599 · tablet 600–1023 · desktop ≥1024 · wide ≥1280 (reserved), in one syntax |
| `prefers-reduced-motion` | 0 | 1 block, kept as the last rule |
| `will-change` | 1 (never removed) | scoped to state classes and transient flyers, plus a start/end lifecycle for one-shot entrances |
| `cubic-bezier` | 15 uses, 7 distinct | 4 (the four easing tokens) |
| Transitions | 54 declarations, ad-hoc timings | 58 items on `--ease-emphasis`, 1 on `--ease-enter`, 3 clock-synced kept linear/exact |
| `backdrop-filter` | 4 | one shared scrim token (plus the `-webkit-` prefix) behind every modal surface |
| `:focus-visible` / `outline-offset` | 0 / 0 | 7 / 3 rules, covering every interactive element |
| Keyframes | 47 | 47 (4 orphaned box-shadow pulses removed, 4 compositor-only replacements added) |

## What changed, item by item

Each item is one patch script in `tools/`. Each script asserts every anchor (it crashes on 0 or more than 1
match) and writes once at the end. Every script runs through `tools/v92_lib.py`, which swaps all 32 base64 blobs
for opaque placeholders before any edit and swaps them back afterwards, asserting each returns exactly once.
No edit can touch image data.

**1. Colour system** — `v92_01_tokens.py`. `:root` became a real scale: surface 0–5, gold 0–5 (ink #14100a →
highlight #f0c966; the five unrelated golds `#d4a843 #f0c966 #7a6020 #7a5a30 #5a4515` are now steps 4/5/2/2/1),
text 0–3, border 0–2, a base/tint/shade/glow quartet for Duke, Assassin, Captain, Ambassador and Contessa,
status, felt/rail, and `-rgb` channel tokens. Literals within ~3% of each other (max channel delta 8) collapse
to one token. Examples: `#1a1424 #1a1628 → surface-3`; `#221c30 #201c30 #1e1830 #241c2e → surface-4`;
`#e88 → contessa-tint`. All 603 `var(--old-name)` references were renamed to the new scale. Nothing moves.

**2. Elevation & radius** — `v92_02_elevation.py`. `--e0` (flush) to `--e5` (modal), two layers each (a contact
shadow plus an ambient one), plus `--e-up` for bottom-docked surfaces. Each shadow's black drop layers become the
token matching their depth; coloured glows, rings and insets stay as state layers. Radii are quantised to
3/6/9/14/999px.

**3. Type** — `v92_03_type.py`. A 1.125 modular scale (`--fs-xs` 11.24px … `--fs-11xl`) with family tokens.
Every live counter uses `tabular-nums lining-nums`: coins, timer digits, round, deck/discard counts, auction
counters and stats. Cinzel has no tabular figures, so badges set in it switch to Crimson Pro's tabular figures
(verified: "1111" and "8888" are equal width). The document gets antialiasing, kerning and ligature hints.
Display tracking tightens as size grows (≥2.5rem caps at 0.14em, 1.5–2.5rem at 0.16em, 1–1.5rem at 0.18em).

**4. Sub-11px text** — `v92_04_legibility.py`, `v92_04b_legibility_fit.py`, `v92_04c_clamp_floor.py`. All 143
sub-11px sizes rise to 11.24px. Tight labels (centre labels, card names, nameplate tags, placards, badges) switch
from Cinzel to a label face: **Source Sans 3** semibold with real small caps (verified: "Ambassador" sets
53.8px in small caps vs 75.5px in capitals) and wider tracking. Where nothing fits, text becomes icon + `title`:
dead cards inside opponents' 34px frames drop the name strip (portrait + title remain), and phone showcase cards
show the emoji with a title. "(CPU)" became its own span, so phones can drop it while the plate's title keeps
the full name.

**5. Pinch zoom** — `v92_05_zoom.py`. The viewport meta drops `maximum-scale`/`user-scalable`. Controls get
`touch-action: manipulation`. Coarse-pointer inputs are 16px so iOS doesn't auto-zoom on focus.

**6. Portrait blur** — `v92_06_portraits.py`. `CHAR_NUDGE`'s `scale(1.04–1.30)` transforms are gone.
`CHAR_FRAMING` keeps the same art direction (zoom plus offset), and `portraitImg()` achieves it by cropping:
an aspect box `zoom × the source's aspect` holds the image with `object-fit: cover` anchored at the top, and
the box's `max-height = nh / zoom` px caps the picture at 1.0× however large the frame gets. All portrait
`<img>`s get `image-rendering: auto`; `contain` becomes `scale-down` everywhere. Same-seat before/after
screenshots of all seven show identical framing. The one used everywhere: arena frames, dock, winner, salon
walls, camera-off tiles.

Effective scale, the largest value per context (CSS px; 2-player table, so the frames are as big as they get):

| crew | source | reframed | arena frame | my dock | winner | salon wall | picker | **max** | at DPR 2 / 3 |
|---|---|---|---|---|---|---|---|---|---|
| nachum | 218×277 | yes | 0.922 | 0.445 | 0.835 | 0.485 | 0.289 | **0.922×** | 1.84 / 2.77 |
| dov | 375×338 | yes | 0.877 | 0.424 | 0.795 | 0.461 | 0.192 | **0.877×** | 1.75 / 2.63 |
| binny | 420×360 | yes | 0.838 | 0.405 | 0.760 | 0.440 | 0.171 | **0.838×** | 1.68 / 2.51 |
| evan | 439×360 | yes | 0.838 | 0.405 | 0.759 | 0.441 | 0.164 | **0.838×** | 1.68 / 2.51 |
| eddie | 215×360 | yes | 0.772 | 0.372 | 0.702 | 0.409 | 0.222 | **0.772×** | 1.54 / 2.32 |
| yossi | 206×360 | yes | 0.733 | 0.354 | 0.665 | 0.388 | 0.222 | **0.733×** | 1.47 / 2.20 |
| bevman | 294×360 | yes | 0.670 | 0.323 | 0.605 | 0.353 | 0.222 | **0.670×** | 1.34 / 2.01 |
| jake | 279×360 |  | 0.644 | 0.311 | 0.583 | 0.340 | 0.222 | **0.644×** | 1.29 / 1.93 |
| ben | 226×360 |  | 0.644 | 0.310 | 0.583 | 0.340 | 0.222 | **0.644×** | 1.29 / 1.93 |
| josh | 250×360 |  | 0.644 | 0.311 | 0.583 | 0.340 | 0.222 | **0.644×** | 1.29 / 1.93 |
| jonnySoul | 259×360 |  | 0.644 | 0.311 | 0.583 | 0.339 | 0.222 | **0.644×** | 1.29 / 1.93 |
| zach | 267×360 |  | 0.644 | 0.311 | 0.583 | 0.337 | 0.222 | **0.644×** | 1.29 / 1.93 |
| joey | 223×360 |  | 0.644 | 0.309 | 0.583 | 0.337 | 0.222 | **0.644×** | 1.29 / 1.93 |
| eden | 278×360 |  | 0.644 | 0.309 | 0.583 | 0.338 | 0.222 | **0.644×** | 1.29 / 1.93 |
| aquaman | 196×360 |  | 0.643 | 0.311 | 0.582 | 0.337 | 0.222 | **0.643×** | 1.29 / 1.93 |
| noah | 238×360 |  | 0.643 | 0.311 | 0.583 | 0.340 | 0.222 | **0.643×** | 1.29 / 1.93 |
| aaron | 241×360 |  | 0.643 | 0.311 | 0.583 | 0.337 | 0.222 | **0.643×** | 1.29 / 1.93 |
| eli | 266×360 |  | 0.643 | 0.311 | 0.583 | 0.337 | 0.222 | **0.643×** | 1.29 / 1.93 |
| jasper | 300×360 |  | 0.643 | 0.310 | 0.583 | 0.339 | 0.222 | **0.643×** | 1.29 / 1.93 |
| baby | 179×360 |  | 0.642 | 0.311 | 0.581 | 0.337 | 0.222 | **0.642×** | 1.28 / 1.93 |
An honest reading of these numbers:

- **In CSS pixels the seven were already ≤1.0× in v91.** The v91 harness measured 0.921× for Nachum and
  0.838× for Binny and Evan, because the frames are smaller than the 277–439px sources.
- **For a fixed frame size, crop-to-zoom and scale-to-zoom end at the same final magnification.** What
  v92 removes is the extra transform resample, and it adds a hard cap so a larger future frame can't push
  any portrait past 1.0×.
- **On retina screens every portrait is upsampled in device pixels** (the right-hand column: 1.3–2.8×).
  That's a property of 360px-tall sources, not of the CSS. It only goes away with higher-resolution
  re-exports, which are out of scope (no source photos in the repo).

**7. Dynamic viewport units** — `v92_07_dvh.py`. The 3 `vh` + 1 `dvh` become `dvh` (screens, confetti) or `svh`
(the seat modal and the faces strip, which must never clip), each after a `vh` fallback line.

**8. Safe areas** — `v92_08_safe_area.py`. `viewport-fit=cover`, then `env()` padding on the top bar, the action
area, `#mobile-log`, the phone faces strip, the toast area, the camera FAB, the rules overlay, the event-log
overlay, every modal scrim and every screen's edges. `#my-dock` sits inside the arena *above* the action area,
so it never touches the physical bottom: it gets the side insets, and the bottom inset goes to whatever is
actually at the bottom.

**9. Breakpoints** — `v92_09_breakpoints.py`, `v92_09b_action_area.py`, `v92_09c_phone_fit.py`.
- **Four named breakpoints in one syntax**, with a `BP` constant so the JS frame sizer uses the same numbers.
  The sizer now measures the arena's real width, since the event-log column isn't table space.
- **iPad portrait was the dead zone.** v91 gave it the phone CSS but sized the frames as desktop, so the outer
  frames hung off-screen (visible in the screenshots). Tablet now has its own layout block.
- **The action area has one fixed height per breakpoint.** The "must Coup" and Double Contessa notes became
  pills floating over the cards, and phones lay the actions out as a centred 4-up grid.
- **9c fixes v91 bugs the 360×640 captures exposed.** `#table-center` (absolute, `left:50%`) was capped at half
  the arena's width (180px), so the centre zone wrapped under the frames. The landing logo, the character
  picker's title row and the winner portrait were clipped by flex centring, and the settings modal could
  overflow a 640px screen.

**10. Reduced motion** — `v92_10_reduced_motion.py`. One block, kept as the last rule:
- All durations collapse to 0.01s and run once, but delays are kept, so banners and toasts still stay up for
  their reading time.
- Every looping state is shown still: the active frame keeps its bright ring and glow, the dock its glow, hot
  coins stay red, the live auction slot stays lit, target previews keep their ring, the recording dot stays
  solid.
- Signals that existed only as motion (the BLUFF/HONEST stamp, the challenge border flash) become a still held
  for the same duration via `steps(1, end)`.

**11. GPU layers** — `v92_11_gpu.py`.
- **Three layout/repaint costs removed.** The card-loss slide moved from `left`/`top` to `transform`, and so did
  the toggle knob. The five box-shadow pulses (active frame, dock, target preview, hit flash, live auction slot)
  became a pre-painted glow layer whose opacity animates, which is compositor-only.
- **`will-change` follows the animation's life.** It is scoped to the state class, set on transient flyers
  (which are then removed), and set on `animationstart` / cleared on `animationend` for one-shot entrances.
- **Coin flights work again.** They had silently not run since v74 (`_findPlayerCoinEl` looked for
  `.seat-coins`, which the arena no longer renders); they now find `.af-coins`/`.me-coins`.

**12. Easing & duration** — `v92_12_easing.py`. Four easing tokens: `--ease-enter` (0.22,1,0.36,1),
`--ease-exit` (0.55,0,1,0.45), `--ease-spring` (0.2,1.4,0.4,1), `--ease-emphasis` (0.4,0,0.2,1). Three
durations: 150/250/450ms. They apply to every transition (CSS, inline and JS-assigned) and to one-shot
entrances and exits. Loops keep `ease-in-out`.

**13. Arena table** — `v92_13_table.py`. The table is built in layers, all CSS, with no new bitmap:
- a bronze rail as the outer trapezoid;
- the felt as an inset trapezoid, stacking generated fractal-noise nap (inline-SVG `feTurbulence`), a fine
  crosshatch weave, a centre bloom, an edge vignette and the felt gradient;
- a **real inner shadow**: a rail-shaped evenodd ring, blurred and clipped to the felt, so the slanted sides
  are shaded too (v91's inset shadow followed the rectangle);
- a gold trim hairline where rail meets felt;
- a near rail with a specular line, a sheen and a contact shadow.

Felt and rail colours are variables, so the DC theme recolours the same layers.

**14. Hung frames** — `v92_14_frames.py`.
- **Tilt:** each seat gets a stable random tilt (1.2–2.5°, random sign, hashed from player + character so
  re-renders don't wobble). Frames pivot like a picture on a nail.
- **Moulding:** a metallic border-box gradient lit from the top-left, with an inner lip and bevel.
- **Shadows:** a two-layer drop shadow offset along the frame's own lean, plus an upright wall contact shadow
  behind it.
- **States:** the active turn straightens, lifts and keeps its glow pulse; eliminated stays grayscale with its
  stamp. Phones use half the tilt.

**15. Nameplates & table centre** — `v92_15_plates_center.py`, `v92_15b_card_backs.py`.
- **Brass plaques:** brushed gradient, bevelled edge, inset rim, two screw heads, letterpress text.
- **Treasury coins:** milled rim, groove, specular rim-light and visible edge thickness.
- **One patterned card back everywhere:** gold lattice, inset frame, medallion. The deck shows its thickness
  (up to 6 layers, 2px apart, with page edges).
- **Discard stacks:** rebuilt at **62×86 desktop / 46×64 phone** (42×58 on ≤700px-tall phones). Every layer
  carries the role colour, the offset layers each cast their own shadow, and the role name sits on a ribbon in
  the label face. v91's stack container also carried `.seat-card` (`overflow:hidden`), which clipped the offset
  layers and the ×N badge; that's neutralised.

**16. Landing & salon** — `v92_16_landing.py`, `v92_16b_landing_fit.py`. The layout logic is unchanged: every
friend still hangs on the walls, split evenly between the sides.
- **The room:** plum wallpaper (pinstripes, faint bands, generated plaster tooth, vignette, centre spotlight)
  and a bronze picture rail.
- **The frames:** each portrait gets a moulding, a dark mount with a gold fillet and a bevelled opening, a brass
  placard, and a shadow that leans with its tilt.
- **Depth:** the side walls turn away in perspective (16b fixed the rotation sign: the outer columns now measure
  smaller, 97px vs 101px, as they should) and their outer column is dimmer.
- **Showcase cards** widen to 72px so "Ambassador" fits, and use the role colours.

**17. Chrome** — `v92_17_chrome.py`.
- **One blurred scrim token** behind every modal surface, and **one modal chrome** (modal, seat modal,
  auction boxes, reshuffle box, auction settings, context menu) with shared title styling.
- **Button states:** hover, active, disabled and loading (`[aria-busy]`) on every button-like control.
- **A 2px gold `:focus-visible` ring** with offset on every interactive element. A small enhancer gives the
  game's clickable `<div>`s (action cards, respond zones, targets, exchange cards, character/mode cards,
  toggles, seat tokens, the discard pile, clickable rows) `tabindex`, `role` and Enter/Space activation, so
  1–7 and P/C/B have a visible ring to point at.
- **Event log:** names and targets are small-caps chips tinted with the player's own colour, the body text
  steps down a level, and entries get hairline separators.

**18–19. Version constant** — `v92_18_version.py`. `const GAME_VERSION = '92'` is declared once, in the first
`<head>` script. The tagline is written from it, synchronously, so there's no empty paint, and
`captureFrozenState()` exports `'v' + GAME_VERSION` instead of the hard-coded `'v63'`. Verified: tagline
`VERSION 92 · LIVE AT THE TABLE`, export `v92`.

**Other fix** — `v92_19b_svg_fixes.py`. The auction spotlight drew `<rect width="${spotW-3}">` before its
container was laid out, which caused the 18 console errors per viewport in v91; the size is now clamped at 0.
`var()` in SVG presentation attributes moved into `style` declarations so other engines resolve it too.

## Judgment calls I made on my own

1. **Illustration hex is tokenised too, but into its own palette.** The brief said "all 542". About 275 of them
   are paint inside SVG drawings: the five role portraits, plus the legacy-roster art, which is dormant because
   every character has a WebP. Skin tones aren't design tokens, so they became an `--ill-*` palette (68 tokens
   after ≤3% collapsing). Art colours that match a design token use the design token. SVG `fill=`/`stroke=`
   attributes became `style` declarations so `var()` resolves. Rabbi Akiva's skin-swap now targets the token
   string.
2. **The 32 per-character log colours became `--char-*` tokens**, not role colours. They're identity, not
   chrome.
3. **`--text-3` was raised from `#3d3545` to `#645a70`** (about 1.6:1 → 3.1:1 on the page background). The
   old faint text was close to invisible, and readability won.
4. **Elevation is assigned by blur depth.** Glows, rings and insets were left as state layers next to the
   token, since they describe state, not height.
5. **Radius steps are 3/6/9/14px.** Former 4px buttons became 6px, so buttons, cards and frames share one
   family.
6. **The label face is Source Sans 3** (Google Fonts, real `smcp`). Using it only for tight labels keeps
   Cinzel as the brand face everywhere it can still be read.
7. **The breakpoint numbers are mine:** 599 / 1023 / 1280. iPad landscape (1024) counts as desktop and now
   gets the salon walls; "wide" is defined but currently only used by the walls' fit band.
8. **The action area is a fixed height** sized for the tallest content (a full hand of seven actions). The
   table is slightly shorter while you wait, but it no longer jumps every turn.
9. **The bottom safe-area inset goes to `#mobile-log`/`#action-area`, not `#my-dock`**, because the dock is
   not at the physical bottom edge.
10. **Coin flights are restored.** This is a visible behaviour change (coins arc between seats again), but it
    is presentational: the counter tick was made to skip structured labels, and `renderGame` still paints the
    totals.
11. **Pre-existing layout bugs were fixed.** The ones the verification run surfaced: centre-zone half width,
    flex-centring clipping, the overflowing settings modal, discard-stack clipping, the iPad-portrait arc and
    the negative SVG rect. They're visual defects, so they're in scope.
12. **Loading state is wired only on Join.** The CSS state exists for every button, but Join is the only
    button that starts asynchronous work. The busy state clears on the next toast (every join error toasts)
    or on a screen change; `guestJoin()` itself is untouched.
13. **The brief's counts were corrected to what's actually in the file:** 3 `vh` (not 23), 102 shadows (not
    105), 125 font-family declarations (not 104), 25 root tokens (not 26), 8 widths (not 9), and 54
    transition declarations / 62 transition items (not 57).

## Deliberately not done, and why

- **The timer bar's `width` tick** stays a width change, because the timer system writes it. It is now a
  `contain: layout paint` boundary, so it never relayouts the action area.
- **Three clock-synced animations keep their exact linear timing:** the 1s timer bar, the 0.9s auction
  ring and the 1s bluff-rate fill. They have to line up with a countdown.
- **The event-log column's collapse (`width` transition)** and **the lobby-only Double Contessa panel glow
  (box-shadow)** were left alone. They're rare, user-triggered or off-table, and converting them would mean
  restructuring lobby markup for no gameplay benefit.
- **The challenge arc on `<canvas>`** is not affected by reduced motion. It's 1.8s, carries who-challenged-whom
  information, and a CSS block can't reach canvas drawing.
- **Portrait re-exports** were not attempted, as instructed. See the honest reading above the portrait table.
- **`coup_v55.html`** (a stale older copy already in the repo) was left untouched. `coup_v92.html` was added
  next to `index.html`.
- **Not tested on real iOS Safari or Android hardware.** Headless Chromium reports 0 for every `env()` inset,
  so the safe-area rules are verified by construction (fallback first, then `env()`), not by a device.

## Re-running everything

```bash
python3 -m http.server 8092 &                                  # serve the repo root
tools/run_all.sh                                               # rebuild v92 from v91, assets checked after every step
python3 tools/verify_assets.py index.html coup_v92.html        # 32/32 md5s
node tools/harness/parse_check.js                              # scripts compile, size ±8%, copy identical
BASE=http://localhost:8092/index.html node tools/harness/checks.js      # font / overflow / portrait / focus
BASE=http://localhost:8092/index.html node tools/harness/cpu_game.js    # 5 full CPU games, errors, action-area height
BASE=http://localhost:8092/index.html node tools/harness/portraits.js   # all 20 crew ≤ 1.0×
BASE=http://localhost:8092/index.html node tools/harness/motion.js      # reduced motion + layer leaks
BASE=... OUT=dir node tools/harness/shoot.js                   # 9 screens × 5 viewports
python3 tools/harness/pairs.py <shots-dir> docs/v92_shots      # side-by-side pairs
```

The v91 results these numbers are compared against are in `tools/harness/baseline_v91/`.

## Before / after (v91 left, v92 right)

Captured with the seeded harness. The CPUs' characters can differ between the two runs because each build
consumes the seeded RNG differently before the game starts.

### Desktop 1920×1080

**landing**

![desktop-1920 landing: v91 left, v92 right](docs/v92_shots/desktop-1920__landing.jpg)

**character**

![desktop-1920 character: v91 left, v92 right](docs/v92_shots/desktop-1920__character.jpg)

**lobby**

![desktop-1920 lobby: v91 left, v92 right](docs/v92_shots/desktop-1920__lobby.jpg)

**waiting**

![desktop-1920 waiting: v91 left, v92 right](docs/v92_shots/desktop-1920__waiting.jpg)

**game**

![desktop-1920 game: v91 left, v92 right](docs/v92_shots/desktop-1920__game.jpg)

**modal**

![desktop-1920 modal: v91 left, v92 right](docs/v92_shots/desktop-1920__modal.jpg)

**auction**

![desktop-1920 auction: v91 left, v92 right](docs/v92_shots/desktop-1920__auction.jpg)

**reveal**

![desktop-1920 reveal: v91 left, v92 right](docs/v92_shots/desktop-1920__reveal.jpg)

**winner**

![desktop-1920 winner: v91 left, v92 right](docs/v92_shots/desktop-1920__winner.jpg)

### Laptop 1440×900

**landing**

![laptop-1440 landing: v91 left, v92 right](docs/v92_shots/laptop-1440__landing.jpg)

**character**

![laptop-1440 character: v91 left, v92 right](docs/v92_shots/laptop-1440__character.jpg)

**lobby**

![laptop-1440 lobby: v91 left, v92 right](docs/v92_shots/laptop-1440__lobby.jpg)

**waiting**

![laptop-1440 waiting: v91 left, v92 right](docs/v92_shots/laptop-1440__waiting.jpg)

**game**

![laptop-1440 game: v91 left, v92 right](docs/v92_shots/laptop-1440__game.jpg)

**modal**

![laptop-1440 modal: v91 left, v92 right](docs/v92_shots/laptop-1440__modal.jpg)

**auction**

![laptop-1440 auction: v91 left, v92 right](docs/v92_shots/laptop-1440__auction.jpg)

**reveal**

![laptop-1440 reveal: v91 left, v92 right](docs/v92_shots/laptop-1440__reveal.jpg)

**winner**

![laptop-1440 winner: v91 left, v92 right](docs/v92_shots/laptop-1440__winner.jpg)

### iPad 1024×768

**landing**

![ipad-1024 landing: v91 left, v92 right](docs/v92_shots/ipad-1024__landing.jpg)

**character**

![ipad-1024 character: v91 left, v92 right](docs/v92_shots/ipad-1024__character.jpg)

**lobby**

![ipad-1024 lobby: v91 left, v92 right](docs/v92_shots/ipad-1024__lobby.jpg)

**waiting**

![ipad-1024 waiting: v91 left, v92 right](docs/v92_shots/ipad-1024__waiting.jpg)

**game**

![ipad-1024 game: v91 left, v92 right](docs/v92_shots/ipad-1024__game.jpg)

**modal**

![ipad-1024 modal: v91 left, v92 right](docs/v92_shots/ipad-1024__modal.jpg)

**auction**

![ipad-1024 auction: v91 left, v92 right](docs/v92_shots/ipad-1024__auction.jpg)

**reveal**

![ipad-1024 reveal: v91 left, v92 right](docs/v92_shots/ipad-1024__reveal.jpg)

**winner**

![ipad-1024 winner: v91 left, v92 right](docs/v92_shots/ipad-1024__winner.jpg)

### iPhone 14 390×844

**landing**

![iphone14-390 landing: v91 left, v92 right](docs/v92_shots/iphone14-390__landing.jpg)

**character**

![iphone14-390 character: v91 left, v92 right](docs/v92_shots/iphone14-390__character.jpg)

**lobby**

![iphone14-390 lobby: v91 left, v92 right](docs/v92_shots/iphone14-390__lobby.jpg)

**waiting**

![iphone14-390 waiting: v91 left, v92 right](docs/v92_shots/iphone14-390__waiting.jpg)

**game**

![iphone14-390 game: v91 left, v92 right](docs/v92_shots/iphone14-390__game.jpg)

**modal**

![iphone14-390 modal: v91 left, v92 right](docs/v92_shots/iphone14-390__modal.jpg)

**auction**

![iphone14-390 auction: v91 left, v92 right](docs/v92_shots/iphone14-390__auction.jpg)

**reveal**

![iphone14-390 reveal: v91 left, v92 right](docs/v92_shots/iphone14-390__reveal.jpg)

**winner**

![iphone14-390 winner: v91 left, v92 right](docs/v92_shots/iphone14-390__winner.jpg)

### Small Android 360×640

**landing**

![android-360 landing: v91 left, v92 right](docs/v92_shots/android-360__landing.jpg)

**character**

![android-360 character: v91 left, v92 right](docs/v92_shots/android-360__character.jpg)

**lobby**

![android-360 lobby: v91 left, v92 right](docs/v92_shots/android-360__lobby.jpg)

**waiting**

![android-360 waiting: v91 left, v92 right](docs/v92_shots/android-360__waiting.jpg)

**game**

![android-360 game: v91 left, v92 right](docs/v92_shots/android-360__game.jpg)

**modal**

![android-360 modal: v91 left, v92 right](docs/v92_shots/android-360__modal.jpg)

**auction**

![android-360 auction: v91 left, v92 right](docs/v92_shots/android-360__auction.jpg)

**reveal**

![android-360 reveal: v91 left, v92 right](docs/v92_shots/android-360__reveal.jpg)

**winner**

![android-360 winner: v91 left, v92 right](docs/v92_shots/android-360__winner.jpg)
