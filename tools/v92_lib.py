"""Shared helpers for the v92 patch scripts.

Every script follows the same shape: read index.html once, make a series of
asserted replacements in memory, and write once at the very end. A failed
assertion raises before anything is written, so a bad anchor changes nothing.

Base64 image blobs are swapped for opaque placeholders before any edit and
swapped back before writing (shield/unshield), so no regex pass can ever touch
image data. unshield() asserts every placeholder comes back exactly once.
"""
import io
import re

PATH = 'index.html'
B64 = re.compile(r'data:image/webp;base64,[A-Za-z0-9+/=]+')


class Patch:
    def __init__(self, path=PATH):
        self.path = path
        self.raw = io.open(path, encoding='utf-8').read()
        self.orig = len(self.raw)
        self.blobs = B64.findall(self.raw)
        self.n = 0
        self.src = B64.sub(self._ph, self.raw)

    def _ph(self, m):
        tok = f'@@B64_{self.n:03d}@@'
        self.n += 1
        return tok

    # exact-anchor replacement: must match exactly `count` times
    def rep(self, old, new, tag, count=1):
        assert old in self.src, f'MISSING: {tag}'
        got = self.src.count(old)
        assert got == count, f'EXPECTED {count} GOT {got}: {tag}'
        self.src = self.src.replace(old, new)
        print(f'  ok: {tag}')

    # regex replacement inside [start_anchor, end_anchor) with an asserted hit count
    def sub(self, pattern, repl, tag, count=None, region=None, flags=0):
        a, b = self.region(region) if region else (0, len(self.src))
        seg = self.src[a:b]
        new, n = re.subn(pattern, repl, seg, flags=flags)
        if count is not None:
            assert n == count, f'EXPECTED {count} GOT {n}: {tag}'
        else:
            assert n > 0, f'MISSING: {tag}'
        self.src = self.src[:a] + new + self.src[b:]
        print(f'  ok: {tag} ({n})')
        return n

    def region(self, name):
        s = self.src
        if name == 'css':
            a = s.index('<style>') + len('<style>'); b = s.index('</style>')
        elif name == 'markup':
            a = s.index('</style>'); b = s.index('<script>\n// ════════════════════════════════════════\n// DATA')
        elif name == 'js':
            a = s.index('<script>\n// ════════════════════════════════════════\n// DATA'); b = s.rindex('</script>')
        elif name == 'legacy-svg':
            a = s.index('const CHARACTERS = {'); b = s.index('// ══ THE CREW')
        elif name == 'role-svg':
            a = s.index('const PORTRAIT_SVG = {'); b = s.index('function portraitFor')
        elif isinstance(name, tuple):
            a = s.index(name[0]); b = s.index(name[1], a)
        else:
            raise KeyError(name)
        return a, b

    def write(self):
        out = self.src
        for i, blob in enumerate(self.blobs):
            tok = f'@@B64_{i:03d}@@'
            assert out.count(tok) == 1, f'PLACEHOLDER {tok} count {out.count(tok)}'
            out = out.replace(tok, blob)
        assert '@@B64_' not in out, 'stray placeholder'
        assert B64.findall(out) == self.blobs, 'asset list changed'
        io.open(self.path, 'w', encoding='utf-8').write(out)
        print(f'DONE {self.orig} -> {len(out)}')
