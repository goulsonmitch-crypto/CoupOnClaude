"""v92 item 16 (follow-up) — side walls turn AWAY, and the room fits at 1024.

Measured after item 16: the outer column of each wall rendered LARGER than the
inner one (106px vs 104px at 1024 wide), i.e. rotateY was swinging the outer
edge toward the viewer. The signs are flipped so the outer edge recedes. In the
desktop band below the wide breakpoint (1024-1279px) the logo alone was 526px
wide, pushing the walls off the screen edges; it scales down there.
"""
from v92_lib import Patch

P = Patch()
print('v92_16b_landing_fit')
P.rep("  #home-wall-left {{ transform: perspective(1200px) rotateY(9deg); transform-origin: 100% 50%; }}".replace('{{', '{').replace('}}', '}'),
      "  #home-wall-left { transform: perspective(1200px) rotateY(-9deg); transform-origin: 100% 50%; }", 'left wall recedes')
P.rep("  #home-wall-right {{ transform: perspective(1200px) rotateY(-9deg); transform-origin: 0 50%; }}".replace('{{', '{').replace('}}', '}'),
      "  #home-wall-right { transform: perspective(1200px) rotateY(9deg); transform-origin: 0 50%; }", 'right wall recedes')
P.css("""
@media (min-width: 1024px) and (max-width: 1279px) {
  .logo-main { font-size: clamp(4.2rem, 9vw, 6.5rem); }
  .landing-grid { gap: 1.4rem; }
}
""", 'desktop-band logo size')
P.write()
