"""v92 item 13 — give the Arena table real depth.

v91: #arena-table-top was a flat two-stop felt gradient clipped to a trapezoid,
with a 12px strip on top. Its inset box-shadow followed the RECTANGLE, so the
slanted sides never got any shading.

Now the table is built in layers, all CSS, no new bitmap (asset count stays 32):
  #arena-table-top   the rail: outer trapezoid, leather/bronze gradient
  .tbl-felt          the felt: inner trapezoid, inset so a rail shows on all sides.
                     Background stack (top -> bottom): generated fractal noise
                     (inline SVG feTurbulence, ~5% alpha) for nap, a fine
                     crosshatch weave, a soft centre bloom, an edge vignette, and
                     the felt gradient.
  .tbl-shade/.tbl-ring  a genuine inner shadow: a dark ring shaped exactly like
                     the rail (evenodd polygon), blurred, then clipped to the felt,
                     so the shadow follows the slanted edges too.
  .tbl-trim          a crisp gold hairline where rail meets felt.
  #arena-table-edge  the near rail, now with a specular highlight along its top
                     edge and a sheen in the middle, casting a contact shadow
                     onto the felt.
Felt and rail colours are variables, so the DC theme (and the dormant blue /
crimson table colours) recolour the same layers instead of replacing them.
"""
from urllib.parse import quote
from v92_lib import Patch

P = Patch()
print('v92_13_table')

P.rep('<div id="arena-table"><div id="arena-table-top"></div><div id="arena-table-edge"></div></div>',
      '<div id="arena-table"><div id="arena-table-top"><div class="tbl-felt"><div class="tbl-shade"><div class="tbl-ring"></div></div>'
      '<div class="tbl-trim"></div></div></div><div id="arena-table-edge"></div></div>', 'table markup layers')

NOISE_SVG = ("<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'>"
             "<filter id='n' x='0' y='0'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/>"
             "<feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.11 0'/></filter>"
             "<rect width='100%' height='100%' filter='url(#n)'/></svg>")
NOISE = 'url("data:image/svg+xml,' + quote(NOISE_SVG, safe="/:=' ") + '")'

OUTER = '14% 0, 86% 0, 101% 101%, -1% 101%'
FELT = '14.95% 3%, 85.05% 3%, 99.6% 101%, 0.4% 101%'
TRIM_IN = '15.25% 3.6%, 84.75% 3.6%, 99.3% 101%, 0.7% 101%'
OLD = """#arena-table { position:absolute; left:0; right:0; bottom:0; top:24%; pointer-events:none; }
#arena-table-top { position:absolute; inset:0;
  clip-path: polygon(14% 0, 86% 0, 101% 101%, -1% 101%);
  background: linear-gradient(180deg, var(--felt-0) 0%, var(--felt-1) 45%, var(--felt-2) 100%);
  box-shadow: inset 0 30px 60px rgba(0,0,0,0.55); }
#arena-table-top::before { content:''; position:absolute; inset:0;
  clip-path: polygon(14.6% 1.5%, 85.4% 1.5%, 99.6% 99%, 0.4% 99%);
  box-shadow: inset 0 0 0 2px rgba(var(--gold-4-rgb),0.14); }
#arena-table-edge { position:absolute; left:14%; right:14%; top:-10px; height:12px;
  background: linear-gradient(180deg, var(--gold-1), var(--rail-0));
  transform: perspective(300px) rotateX(30deg); border-radius: var(--r-xs) var(--r-xs) 0 0;
  box-shadow: var(--e-up); }"""
NEW = f"""#arena-table {{ position:absolute; left:0; right:0; bottom:0; top:24%; pointer-events:none; contain: layout paint;
  --felt-a: var(--felt-0); --felt-b: var(--felt-1); --felt-c: var(--felt-2); --felt-tint: transparent;
  --rail-a: var(--gold-1); --rail-b: var(--rail-0); }}
/* rail: the outer trapezoid */
#arena-table-top {{ position:absolute; inset:0; clip-path: polygon({OUTER});
  background:
    linear-gradient(180deg, rgba(var(--parchment-rgb),0.10) 0, transparent 2.5%),
    linear-gradient(180deg, var(--rail-a) 0%, var(--rail-b) 55%, var(--rail-b) 100%); }}
/* felt: inner trapezoid, layered nap + weave + bloom + vignette */
.tbl-felt {{ position:absolute; inset:0; clip-path: polygon({FELT});
  background:
    {NOISE},
    repeating-linear-gradient(45deg, rgba(var(--text-0-rgb),0.022) 0 1px, transparent 1px 3px),
    repeating-linear-gradient(-45deg, rgba(0,0,0,0.06) 0 1px, transparent 1px 3px),
    radial-gradient(ellipse 46% 40% at 50% 46%, rgba(var(--parchment-rgb),0.09), transparent 72%),
    radial-gradient(ellipse 78% 92% at 50% 40%, transparent 48%, rgba(0,0,0,0.5) 100%),
    linear-gradient(var(--felt-tint), var(--felt-tint)),
    linear-gradient(180deg, var(--felt-a) 0%, var(--felt-b) 45%, var(--felt-c) 100%);
  background-size: 160px 160px, auto, auto, auto, auto, auto, auto; }}
/* inner shadow: a rail-shaped ring, blurred, clipped to the felt */
.tbl-shade {{ position:absolute; inset:-2%; filter: blur(14px); }}
.tbl-ring {{ position:absolute; inset:2%; background: rgba(0,0,0,0.92);
  clip-path: polygon(evenodd, {OUTER}, 14% 0, {FELT}, 14.95% 3%); }}
.tbl-trim {{ position:absolute; inset:0; background: rgba(var(--gold-4-rgb),0.34);
  clip-path: polygon(evenodd, {FELT}, 14.95% 3%, {TRIM_IN}, 15.25% 3.6%); }}
/* near rail: bronze with a specular line and a sheen, casting onto the felt */
#arena-table-edge {{ position:absolute; left:14%; right:14%; top:-11px; height:14px;
  background:
    linear-gradient(180deg, rgba(255,246,222,0.85) 0, rgba(255,246,222,0.28) 1.5px, transparent 3.5px),
    radial-gradient(ellipse 34% 160% at 50% 0%, rgba(var(--gold-5-rgb),0.42), transparent 70%),
    linear-gradient(180deg, var(--gold-2) 0%, var(--rail-a) 38%, var(--rail-b) 100%);
  transform: perspective(300px) rotateX(30deg); border-radius: var(--r-xs) var(--r-xs) 0 0;
  box-shadow: 0 -1px 0 rgba(0,0,0,0.55), 0 4px 7px rgba(0,0,0,0.55), var(--e-up); }}"""
P.rep(OLD, NEW, 'layered table')

P.rep(".dc-theme #arena-table-top { background: linear-gradient(180deg, var(--felt-dc-0) 0%, var(--felt-dc-1) 40%, var(--felt-dc-2) 100%); box-shadow: inset 0 0 40px rgba(var(--contessa-rgb),0.18); }",
      ".dc-theme #arena-table { --felt-a: var(--felt-dc-0); --felt-b: var(--felt-dc-1); --felt-c: var(--felt-dc-2); --felt-tint: rgba(var(--contessa-rgb),0.10); --rail-a: var(--rail-dc-0); --rail-b: var(--rail-dc-1); }",
      'dc felt via variables')
P.rep(".table-color-blue #arena-table-top { background: linear-gradient(180deg, var(--felt-blue-0) 0%, var(--felt-blue-1) 40%, var(--felt-blue-2) 100%); }",
      ".table-color-blue #arena-table { --felt-a: var(--felt-blue-0); --felt-b: var(--felt-blue-1); --felt-c: var(--felt-blue-2); --rail-a: var(--rail-blue-0); --rail-b: var(--rail-blue-1); }",
      'blue felt via variables')
P.rep(".table-color-blue #arena-table-edge { background: linear-gradient(180deg, var(--rail-blue-0), var(--rail-blue-1)); }\n", "", 'blue edge now inherits rail vars')
P.rep(".table-color-crimson #arena-table-top { background: linear-gradient(180deg, var(--felt-red-0) 0%, var(--felt-red-1) 40%, var(--felt-red-2) 100%); }",
      ".table-color-crimson #arena-table { --felt-a: var(--felt-red-0); --felt-b: var(--felt-red-1); --felt-c: var(--felt-red-2); --rail-a: var(--rail-red-0); --rail-b: var(--rail-red-1); }",
      'crimson felt via variables')
P.rep(".table-color-crimson #arena-table-edge { background: linear-gradient(180deg, var(--rail-red-0), var(--rail-red-1)); }\n", "", 'crimson edge now inherits rail vars')
P.rep(".dc-theme #arena-table-edge { background: linear-gradient(180deg, var(--rail-dc-0), var(--rail-dc-1)); }\n", "", 'dc edge now inherits rail vars')
P.write()
