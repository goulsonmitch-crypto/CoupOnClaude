"""v92 item 6 — stop compounding portrait blur.

CHAR_NUDGE used transform: scale(1.04-1.30) on seven portraits whose sources are
only 206-439px wide / 277-360px tall. Those seven were magnified on top of
whatever the frame and the display's pixel ratio already did.

Now: CHAR_FRAMING keeps the same art direction (zoom + offset) but achieves it
by cropping. portraitImg() wraps those seven in a .pcrop box whose aspect is the
source's aspect widened by `zoom`; inside it the image is object-fit: cover with
object-position at the top, so the zoom comes from trimming the bottom of the
picture rather than from scaling it. The box's max-height is nh / zoom px,
which caps the image at exactly 1.0x its intrinsic size however large the frame
gets. Offsets are plain translations (no scale). Every portrait <img> also gets
image-rendering: auto explicitly and object-fit: scale-down wherever it used to
be contain, so nothing is ever drawn above 1.0x.
"""
from v92_lib import Patch

P = Patch()
print('v92_06_portraits')

P.rep("""const CHAR_NUDGE = {
  eddie:  'translate(4%, 12%) scale(1.20)',    // right, and down a touch
  nachum: 'translate(5%, 6%) scale(1.10)',     // right, and down a touch
  bevman: 'translate(0, 6%) scale(1.04)',      // down a tad
  yossi:  'translate(0, 12%) scale(1.14)',
  dov:    'translate(0, 0%) scale(1.28)',      // face fills the frame, sits mid
  binny:  'translate(0, 0%) scale(1.30)',
  evan:   'translate(0, 0%) scale(1.30)',
};
function charImgHtml(p) {
  let fStyle = p.characterVariant ? variantFilter(p.characterVariant, p.character) : '';
  if (p.character && CHAR_NUDGE[p.character]) fStyle += (fStyle && !fStyle.endsWith(';') ? ';' : '') + 'transform:' + CHAR_NUDGE[p.character] + ';';
  if (p.character && CHARACTER_IMAGES[p.character])
    return `<img src="${CHARACTER_IMAGES[p.character]}" style="${fStyle}" alt="">`;""",
"""// v92: framing is done by CROPPING, never by magnifying. zoom = how much tighter than a
// full-height fit; x/y = offset as a % of the crop box (+y moves the face down).
const CHAR_FRAMING = {
  eddie:  { zoom: 1.20, x: 4, y: 12 },   // right, and down a touch
  nachum: { zoom: 1.10, x: 5, y: 6 },    // right, and down a touch
  bevman: { zoom: 1.04, x: 0, y: 6 },    // down a tad
  yossi:  { zoom: 1.14, x: 0, y: 12 },
  dov:    { zoom: 1.28, x: 0, y: 0 },    // face fills the frame, sits mid
  binny:  { zoom: 1.30, x: 0, y: 0 },
  evan:   { zoom: 1.30, x: 0, y: 0 },
};
// Intrinsic pixel size of each framed source (measured from the embedded WebP).
const PORTRAIT_PX = {
  eddie: [215, 360], nachum: [218, 277], bevman: [294, 360], yossi: [206, 360],
  dov: [375, 338], binny: [420, 360], evan: [439, 360],
};
// The crop box has the source's aspect widened by `zoom`; object-fit:cover inside it trims
// the bottom of the picture. max-height = nh/zoom keeps the picture at <= 1.0x its own pixels.
function portraitImg(key, extraStyle) {
  const src = CHARACTER_IMAGES[key];
  if (!src) return '';
  const st = extraStyle ? ` style="${extraStyle}"` : '';
  const fr = CHAR_FRAMING[key], px = PORTRAIT_PX[key];
  if (!fr || !px) return `<img class="pimg" src="${src}"${st} alt="">`;
  const [nw, nh] = px;
  const box = `aspect-ratio:${(fr.zoom * nw).toFixed(1)}/${nh};max-height:${Math.floor(nh / fr.zoom)}px;--pdx:${fr.x}%;--pdy:${fr.y}%`;
  return `<span class="pcrop" style="${box}"><img class="pimg" src="${src}"${st} alt=""></span>`;
}
function charImgHtml(p) {
  let fStyle = p.characterVariant ? variantFilter(p.characterVariant, p.character) : '';
  if (p.character && CHARACTER_IMAGES[p.character])
    return portraitImg(p.character, fStyle);""", 'CHAR_NUDGE -> CHAR_FRAMING + portraitImg()')

FACE_OLD = """`<img src="${CHARACTER_IMAGES[en.charKey]}" ${CHAR_NUDGE[en.charKey] ? `style="transform:${CHAR_NUDGE[en.charKey]}"` : ''} alt="">`"""
P.rep(FACE_OLD, "portraitImg(en.charKey)", 'camera-off tiles use portraitImg', count=2)
P.rep("""      const nud = CHAR_NUDGE[k] ? `style="transform:${CHAR_NUDGE[k]}"` : '';
""", "", 'salon walls: drop transform nudge')
P.rep("""`<div class="wall-frame2"><img src="${CHARACTER_IMAGES[k]}" ${nud} alt=""></div>`""",
      """`<div class="wall-frame2">${portraitImg(k)}</div>`""", 'salon walls use portraitImg')
assert 'CHAR_NUDGE' not in P.src

# winner tableau: an inner clipping well, so the crop can never spill past the frame while
# the frame itself stays overflow:visible for the crown
P.rep("""`<div class="win-frame"><div class="win-crown">👑</div>${charImgHtml(wpl)}</div>`""",
      """`<div class="win-frame"><div class="win-crown">👑</div><div class="win-port">${charImgHtml(wpl)}</div></div>`""",
      'winner portrait well')

# contain -> scale-down so a large box never upsamples a small source
P.rep("""return `<img src="${CHARACTER_IMAGES[charKey]}" style="width:100%;height:100%;object-fit:contain;display:block;${filter}">`;""",
      """return `<img src="${CHARACTER_IMAGES[charKey]}" style="width:100%;height:100%;object-fit:scale-down;object-position:50% 100%;display:block;${filter}">`;""",
      'getCharacterSvg img never upscales')
P.rep("""avatarInner = `<img src="${CHARACTER_IMAGES[p.character]}" style="width:100%;height:100%;object-fit:contain;display:block;">`;""",
      """avatarInner = `<img src="${CHARACTER_IMAGES[p.character]}" style="width:100%;height:100%;object-fit:scale-down;object-position:50% 100%;display:block;">`;""",
      'seat-token img never upscales')
P.sub(r'(style="width:\d+px;height:\d+px;)object-fit:contain;', r'\1object-fit:scale-down;', 'claim-banner portraits never upscale', count=2)
P.rep(".char-avatar img { width: 100%; height: 100%; object-fit: contain; display: block; }",
      ".char-avatar img { width: 100%; height: 100%; object-fit: scale-down; object-position: 50% 100%; display: block; }", 'char grid')
P.rep(".win-frame img { width:100%; height:210px; object-fit:contain; display:block; padding-top:8px; }",
      ".win-port { position:relative; height:218px; padding-top:8px; overflow:hidden; border-radius:inherit;\n"
      "  display:flex; align-items:flex-end; justify-content:center; }\n"
      ".win-port > img { max-width:100%; max-height:100%; object-fit:scale-down; display:block; }", 'winner well css')

P.rep(".arena-frame.av-live .af-portrait > img { visibility:hidden; }",
      ".arena-frame.av-live .af-portrait > img, .arena-frame.av-live .af-portrait > .pcrop { visibility:hidden; }", 'live video hides cropped portrait too')
P.rep(".arena-me.av-live-me .me-chip > img { visibility:hidden; }",
      ".arena-me.av-live-me .me-chip > img, .arena-me.av-live-me .me-chip > .pcrop { visibility:hidden; }", 'live self video hides cropped portrait too')

CSS = """
/* ══ v92 portraits (item 6): crop, never magnify ══ */
img { image-rendering: auto; }
.pcrop { position: relative; display: block; flex: 0 0 auto; height: 100%; overflow: hidden;
  transform: translate(var(--pdx, 0), var(--pdy, 0)); }
.pcrop > img.pimg { display: block; width: 100%; height: 100%; max-width: none; max-height: none;
  object-fit: cover; object-position: 50% 0%; transform: none; }
.af-portrait > .pcrop > img.pimg { filter: drop-shadow(0 5px 9px rgba(0,0,0,0.7)); }
.face-ph > .pcrop, .wall-frame2 > .pcrop, .me-chip > .pcrop, .pit-chip > .pcrop, .pit-waitface > .pcrop { height: 100%; }
"""
P.rep("\n</style>\n</head>", CSS + "\n</style>\n</head>", 'pcrop css')
P.write()
