"""v92 item 16 — rebuild the landing screen and the salon walls.

Layout logic is unchanged (renderHomeWalls still hangs every friend, split
evenly left/right, sized from the viewport height). What changes is the room:
  * Wall: a dark plum wallpaper — fine gold pinstripes, faint stripe bands, a
    generated-noise plaster tooth (inline SVG, not a bitmap), a vignette, and a
    warm spotlight on the centre stage.
  * Picture rail: a bronze moulding across the top of the room with its own
    highlight and shadow.
  * Frames: each portrait gets a metallic moulding (border-box gradient), a
    dark mount with a gold fillet and a bevelled, shadowed opening, a brass
    placard for the name, and a drop shadow that leans with the frame's tilt.
  * Depth: the two side walls are turned away in perspective (rotateY, pivoting
    on their inner edge) and their outer column is dimmer than the inner one, so
    they recede behind the centre content. Hovering a portrait still straightens and lifts
    it above the shading.
  * The role showcase cards widen so "Ambassador" fits, and take the role
    quartet colours.
"""
from urllib.parse import quote
from v92_lib import Patch

P = Patch()
print('v92_16_landing')

P.rep("""      return `<div class="wall-hang" style="--tilt:${tilt}deg">` +
        `<div class="wall-frame2">${portraitImg(k)}</div>` +""",
      """      return `<div class="wall-hang" style="--tilt:${tilt}deg;--sx:${(-tilt * 1.4).toFixed(1)}px">` +
        `<div class="wall-frame2"><div class="wall-window">${portraitImg(k)}</div></div>` +""",
      'wall frames get a mount window + tilt-matched shadow')

NOISE_SVG = ("<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'>"
             "<filter id='p' x='0' y='0'><feTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/>"
             "<feColorMatrix values='0 0 0 0 0.95  0 0 0 0 0.85  0 0 0 0 0.75  0 0 0 0.07 0'/></filter>"
             "<rect width='100%' height='100%' filter='url(#p)'/></svg>")
NOISE = 'url("data:image/svg+xml,' + quote(NOISE_SVG, safe="/:=' ") + '")'

CSS = f"""
/* ══ v92 landing salon (item 16) ══ */
#screen-landing {{ position: relative;
  background:
    radial-gradient(ellipse 40% 58% at 50% 46%, rgba(var(--gold-4-rgb),0.11), transparent 72%),
    radial-gradient(ellipse 120% 95% at 50% 50%, transparent 52%, rgba(0,0,0,0.6) 100%),
    {NOISE},
    repeating-linear-gradient(90deg, rgba(var(--gold-4-rgb),0.028) 0 1px, transparent 1px 36px),
    repeating-linear-gradient(90deg, rgba(var(--text-0-rgb),0.008) 0 18px, transparent 18px 36px),
    linear-gradient(180deg, var(--surface-2) 0%, var(--surface-0) 100%);
  background-size: auto, auto, 220px 220px, auto, auto, auto; }}
/* picture rail */
#screen-landing::before {{ content: ''; position: absolute; left: 0; right: 0; height: 8px; z-index: 0; pointer-events: none;
  top: 12px; top: calc(12px + env(safe-area-inset-top, 0px));
  background: linear-gradient(180deg, var(--gold-3) 0%, var(--gold-2) 30%, var(--gold-1) 65%, var(--rail-0) 100%);
  box-shadow: inset 0 1px 0 rgba(var(--gold-5-rgb),0.55), 0 1px 0 var(--gold-0), 0 5px 10px rgba(0,0,0,0.6); }}
.landing-grid, .landing-center {{ position: relative; z-index: 1; }}
/* side walls recede */
@media (min-width: 1024px) {{
  .home-wall {{ position: relative; padding: 1.4rem 0.4rem 0.6rem; }}
  #home-wall-left {{ transform: perspective(1200px) rotateY(9deg); transform-origin: 100% 50%; }}
  #home-wall-right {{ transform: perspective(1200px) rotateY(-9deg); transform-origin: 0 50%; }}
  /* the outer column sits deeper in the room: dimmer and a touch smaller (no overlay panels) */
  #home-wall-left .wall-hang:nth-child(odd), #home-wall-right .wall-hang:nth-child(even) {{ filter: brightness(0.74) saturate(0.9); }}
  #home-wall-left .wall-hang:nth-child(even), #home-wall-right .wall-hang:nth-child(odd) {{ filter: brightness(0.92); }}
  .wall-hang:hover {{ z-index: 4; filter: none !important; }}
}}
/* frame + mount */
.wall-hang {{ position: relative; gap: 5px; }}
.wall-frame2 {{ position: relative; overflow: visible; border: 4px solid transparent; border-radius: var(--r-xs);
  --mould: linear-gradient(145deg, var(--gold-5) 0%, var(--gold-4) 18%, var(--gold-2) 46%, var(--gold-1) 60%, var(--gold-3) 82%, var(--gold-4) 100%);
  background: linear-gradient(160deg, var(--surface-5), var(--surface-3)) padding-box, var(--mould) border-box;
  box-shadow: 0 0 0 1px var(--gold-0), var(--sx, 0px) 5px 9px rgba(0,0,0,0.5), calc(var(--sx, 0px) * 2) 14px 26px rgba(0,0,0,0.6); }}
.wall-window {{ position: absolute; inset: 5px; overflow: hidden; border-radius: 2px;
  display: flex; align-items: flex-end; justify-content: center;
  background: radial-gradient(ellipse at 50% 30%, var(--surface-4) 0%, var(--surface-1) 90%); }}
.wall-window::after {{ content: ''; position: absolute; inset: 0; pointer-events: none; border-radius: inherit;
  box-shadow: inset 0 0 0 1px rgba(var(--gold-4-rgb),0.5), inset 2px 3px 6px rgba(0,0,0,0.75), inset -1px -1px 2px rgba(var(--parchment-rgb),0.12); }}
.wall-window > img {{ max-width: 100%; max-height: 100%; object-fit: scale-down; }}
.wall-window > .pcrop {{ height: 100%; }}
/* brass placard */
.wall-name2 {{ padding: 1px 7px 2px; border-radius: 2px; border: 1px solid var(--gold-1); color: var(--gold-0);
  background: linear-gradient(180deg, var(--gold-5), var(--gold-4) 40%, var(--gold-3));
  text-shadow: 0 1px 0 rgba(255,244,210,0.55); box-shadow: inset 0 1px 0 rgba(255,248,220,0.5), var(--e1); }}
/* phone strip frames share the moulding */
.home-char-frame {{ border: 3px solid transparent;
  background: radial-gradient(ellipse at 50% 30%, var(--surface-4) 0%, var(--surface-1) 90%) padding-box,
    linear-gradient(145deg, var(--gold-5), var(--gold-2) 50%, var(--gold-4)) border-box;
  box-shadow: 0 0 0 1px var(--gold-0), inset 0 0 0 1px rgba(0,0,0,0.6), var(--e2); }}
/* showcase cards: wide enough for "Ambassador", in role colours */
.showcase-card {{ width: 72px; height: 92px; border-width: 1.5px; box-shadow: inset 0 0 0 2px rgba(0,0,0,0.35), var(--e2); }}
.showcase-card.duke {{ background: linear-gradient(160deg, rgba(var(--duke-rgb),0.45), var(--duke-shade)); }}
.showcase-card.assassin {{ background: linear-gradient(160deg, rgba(150,140,160,0.35), var(--assassin-shade)); }}
.showcase-card.captain {{ background: linear-gradient(160deg, rgba(var(--captain-rgb),0.45), var(--captain-shade)); }}
.showcase-card.ambassador {{ background: linear-gradient(160deg, rgba(var(--ambassador-rgb),0.45), var(--ambassador-shade)); }}
.showcase-card.contessa {{ background: linear-gradient(160deg, rgba(var(--contessa-rgb),0.45), var(--contessa-shade)); }}
@media (max-width: 599px) {{ .showcase-card {{ width: 52px; height: 70px; }} }}
"""
P.css(CSS, 'landing salon css')
P.rep(".wall-frame2 img { max-width: 94%; max-height: 100%; object-fit: contain; }",
      ".wall-frame2 img { max-width: 100%; max-height: 100%; object-fit: scale-down; }", 'wall img never upscales')
P.write()
