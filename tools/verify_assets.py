#!/usr/bin/env python3
"""Asset integrity guard for index.html.

Extracts every data:image/webp;base64,... blob, md5s each one, and either
records a baseline (--baseline) or compares against tools/asset_baseline.json.
Exit code 1 on any mismatch so patch pipelines stop hard.
"""
import hashlib, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASELINE = os.path.join(HERE, 'asset_baseline.json')
PAT = re.compile(r'data:image/webp;base64,([A-Za-z0-9+/=]+)')

def scan(path):
    src = io.open(path, encoding='utf-8').read()
    blobs = PAT.findall(src)
    md5s = [hashlib.md5(b.encode('ascii')).hexdigest() for b in blobs]
    return {
        'file': os.path.relpath(path, ROOT),
        'count': len(md5s),
        'total_b64_bytes': sum(len(b) for b in blobs),
        'md5s': md5s,
        'combined': hashlib.md5(''.join(md5s).encode()).hexdigest(),
    }

def main():
    args = sys.argv[1:]
    make = '--baseline' in args
    files = [a for a in args if not a.startswith('--')] or [os.path.join(ROOT, 'index.html')]
    rc = 0
    for f in files:
        cur = scan(f)
        if make:
            json.dump(cur, io.open(BASELINE, 'w'), indent=2)
            print(f'baseline written: {cur["count"]} assets, {cur["total_b64_bytes"]} b64 bytes, combined {cur["combined"]}')
            continue
        base = json.load(io.open(BASELINE))
        ok = cur['md5s'] == base['md5s']
        if ok:
            print(f'{cur["file"]}: ALL {cur["count"]}/{base["count"]} ASSETS MATCH (combined {cur["combined"]})')
        else:
            rc = 1
            print(f'{cur["file"]}: ASSET MISMATCH count {cur["count"]} vs baseline {base["count"]}')
            for i, (a, b) in enumerate(zip(cur['md5s'], base['md5s'])):
                if a != b:
                    print(f'  #{i}: {a} != {b}')
    sys.exit(rc)

if __name__ == '__main__':
    main()
