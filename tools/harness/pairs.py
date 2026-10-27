import sys, os
from PIL import Image, ImageDraw
S = sys.argv[1]; OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
VPS = ['desktop-1920', 'laptop-1440', 'ipad-1024', 'iphone14-390', 'android-360']
SCR = ['landing', 'character', 'lobby', 'waiting', 'game', 'modal', 'auction', 'reveal', 'winner']
for vp in VPS:
    for sc in SCR:
        a = Image.open(f'{S}/before/{vp}__{sc}.jpg').convert('RGB'); b = Image.open(f'{S}/after/{vp}__{sc}.jpg').convert('RGB')
        w, h = a.size; scale = min(1.0, 900 / w) if w > 600 else min(1.0, 700 / h)
        a = a.resize((int(w*scale), int(h*scale))); b = b.resize((int(w*scale), int(h*scale)))
        W = Image.new('RGB', (a.width*2 + 12, a.height + 28), (20, 16, 24))
        W.paste(a, (0, 28)); W.paste(b, (a.width + 12, 28))
        d = ImageDraw.Draw(W); d.text((8, 7), f'v91 BEFORE  {vp} / {sc}', fill=(200, 180, 120)); d.text((a.width + 20, 7), 'v92 AFTER', fill=(240, 200, 100))
        W.save(f'{OUT}/{vp}__{sc}.jpg', quality=78)
print('pairs written')
