"""v92 item 14 — the frames read as hung portraits.

* Tilt: the alternating +-0.6deg (too small to read as intent) is replaced by a
  per-seat tilt of 1.2-2.5deg with a random sign, derived from a hash of the
  seat (player id + character) so it is random per seat but stable across
  re-renders. Frames pivot just below the top, like a picture on a nail.
  Phones use half the tilt (the frames are small and packed in one row).
* Moulding: the 3px flat border becomes a 4px metallic moulding (a border-box
  gradient lit from the top-left) with an inner dark lip and a fine gold bevel
  line on the inside edge.
* Drop shadow: offset along the frame's own lean (--sx follows the tilt), two
  layers (contact + ambient) matching the e3 elevation.
* Wall contact shadow: a soft shadow behind each frame, counter-rotated so it
  stays upright on the (unrotated) wall while the frame tilts in front of it.
* Active turn still straightens and lifts the frame and keeps its gold glow
  pulse (item 11 layer); eliminated frames keep the grayscale + stamp.
"""
from v92_lib import Patch

P = Patch()
print('v92_14_frames')

P.rep("""    fr.className = 'seat arena-frame' + (isTurn ? ' active-turn' : '') + (p.eliminated ? ' eliminated' : '');
    fr.setAttribute('data-pid', p.id);""",
"""    fr.className = 'seat arena-frame' + (isTurn ? ' active-turn' : '') + (p.eliminated ? ' eliminated' : '');
    fr.setAttribute('data-pid', p.id);
    // v92: each seat hangs at its own angle — random per seat, stable across re-renders
    const _fh = [...(String(p.id) + '|' + (p.character || ''))].reduce((a, ch) => (Math.imul(a, 31) + ch.charCodeAt(0)) >>> 0, 2166136261);
    const _tilt = (((_fh >>> 11) & 1) ? 1 : -1) * (1.2 + ((_fh % 1000) / 1000) * 1.3);
    fr.style.setProperty('--tilt', _tilt.toFixed(2) + 'deg');
    fr.style.setProperty('--drop', (2 + ((_fh >>> 4) % 9)) + 'px');
    fr.style.setProperty('--sx', (-_tilt * 1.6).toFixed(1) + 'px');""", 'per-seat tilt variables')

P.rep(""".arena-frame:nth-child(odd)  { transform: translateY(10px) rotate(-0.6deg); }
.arena-frame:nth-child(even) { transform: translateY(2px)  rotate(0.6deg); }
.af-body { position:relative; border-radius:var(--r-sm); overflow:hidden;
  background: radial-gradient(ellipse at 50% 30%, var(--surface-4) 0%, var(--surface-1) 90%);
  border: 3px solid var(--gold-2);
  box-shadow: 0 0 0 1px var(--gold-0), 0 0 0 3px rgba(var(--gold-4-rgb),0.55), 0 0 0 4px var(--gold-0), inset 0 0 22px rgba(0,0,0,0.75), var(--e3); }""",
""".arena-frame { --tilt: 0deg; --drop: 4px; --sx: 0px; isolation: isolate; transform-origin: 50% 32%;
  transform: translateY(var(--drop)) rotate(var(--tilt)); }
/* wall contact shadow: stays upright behind the tilted frame */
.arena-frame::after { content: ''; position: absolute; z-index: -2; left: 7%; right: 7%; top: 10px; bottom: 30px;
  border-radius: var(--r-md); pointer-events: none;
  box-shadow: 0 14px 26px 1px rgba(0,0,0,0.5), 0 4px 10px rgba(0,0,0,0.4);
  transform: translate(calc(var(--sx) * -0.5), 6px) rotate(calc(var(--tilt) * -1)); }
.af-body { position:relative; border-radius:var(--r-sm); overflow:hidden;
  --mould: linear-gradient(145deg, var(--gold-5) 0%, var(--gold-4) 18%, var(--gold-2) 46%, var(--gold-1) 60%, var(--gold-3) 82%, var(--gold-4) 100%);
  border: 4px solid transparent;
  background: radial-gradient(ellipse at 50% 30%, var(--surface-4) 0%, var(--surface-1) 90%) padding-box, var(--mould) border-box;
  box-shadow: 0 0 0 1px var(--gold-0),
    inset 0 0 0 1px rgba(0,0,0,0.75), inset 0 0 0 2px rgba(var(--gold-5-rgb),0.22), inset 0 0 22px rgba(0,0,0,0.75),
    var(--sx) 5px 9px rgba(0,0,0,0.48), calc(var(--sx) * 2) 14px 30px rgba(0,0,0,0.58); }""", 'moulding + tilt-matched shadow')

P.rep(""".arena-frame.active-turn .af-body { border-color:var(--gold-5);
  box-shadow: 0 0 0 1px var(--gold-0), 0 0 0 3px rgba(var(--gold-5-rgb),0.9), inset 0 0 22px rgba(0,0,0,0.75), var(--e3); }
.arena-frame.active-turn { transform: translateY(-6px) scale(1.04) !important; }""",
""".arena-frame.active-turn .af-body {
  --mould: linear-gradient(145deg, var(--text-0) 0%, var(--gold-5) 22%, var(--gold-4) 50%, var(--gold-3) 70%, var(--gold-5) 100%);
  box-shadow: 0 0 0 1px var(--gold-0), 0 0 0 3px rgba(var(--gold-5-rgb),0.9),
    inset 0 0 0 1px rgba(0,0,0,0.75), inset 0 0 22px rgba(0,0,0,0.75), 0 8px 14px rgba(0,0,0,0.5), 0 18px 36px rgba(0,0,0,0.6); }
.arena-frame.active-turn { transform: translateY(-6px) rotate(0deg) scale(1.04) !important; }
.arena-frame.active-turn::after { transform: translate(0, 10px); }""", 'active frame straightens, keeps ring')

P.rep(".seat.target-preview.arena-frame .af-body { box-shadow: 0 0 0 1px var(--gold-0), 0 0 0 3px rgba(var(--danger-rgb),0.75), inset 0 0 22px rgba(0,0,0,0.75), var(--e3); }",
      ".seat.target-preview.arena-frame .af-body { box-shadow: 0 0 0 1px var(--gold-0), 0 0 0 3px rgba(var(--danger-rgb),0.75), inset 0 0 0 1px rgba(0,0,0,0.75), inset 0 0 22px rgba(0,0,0,0.75), var(--sx) 5px 9px rgba(0,0,0,0.48), calc(var(--sx) * 2) 14px 30px rgba(0,0,0,0.58); }",
      'target preview keeps the frame shadow')
P.rep("  .arena-frame:nth-child(odd), .arena-frame:nth-child(even) { transform:none; }\n  .arena-frame.active-turn { transform: translateY(-4px) scale(1.04) !important; }",
      "  .arena-frame { transform: translateY(calc(var(--drop) * 0.5)) rotate(calc(var(--tilt) * 0.5)); }\n"
      "  .af-body { border-width: 3px; }\n"
      "  .arena-frame.active-turn { transform: translateY(-4px) rotate(0deg) scale(1.04) !important; }", 'phone: half tilt')
# the box-shadow pulses this replaced in item 11 are no longer referenced
for kf in ('framePulse', 'dockPulse', 'targetPulse', 'auctionLivePulse'):
    import re
    m = re.search(r'@keyframes ' + kf + r' \{(?:[^{}]*\{[^{}]*\})*[^{}]*\}\n?', P.src)
    assert m, kf
    assert P.src.count(kf) == 1, f'{kf} still referenced'
    P.src = P.src[:m.start()] + P.src[m.end():]
    print(f'  ok: removed orphaned @keyframes {kf}')
P.write()
