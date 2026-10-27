#!/usr/bin/env bash
# Rebuild the v92 index.html from the v91 file by replaying every patch script in order.
#   tools/run_all.sh [v91-commit]        (default 27ea1a3 = "v91: solo picker flow ...")
# Each script asserts its anchors and writes only at the end; verify_assets.py runs
# after every step and stops the chain if a single image md5 changes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${1:-27ea1a3}"
WORK="$(mktemp -d)"
git -C "$ROOT" show "$BASE:index.html" > "$WORK/index.html"
cd "$WORK"
STEPS=(
  v92_01_tokens v92_02_elevation v92_03_type v92_04_legibility v92_04b_legibility_fit
  v92_05_zoom v92_06_portraits v92_07_dvh v92_08_safe_area v92_09_breakpoints v92_09b_action_area
  v92_10_reduced_motion v92_11_gpu v92_12_easing v92_13_table v92_14_frames v92_15_plates_center
  v92_16_landing v92_17_chrome v92_04c_clamp_floor v92_18_version v92_19b_svg_fixes
  v92_09c_phone_fit v92_16b_landing_fit v92_15b_card_backs
)
for s in "${STEPS[@]}"; do
  echo "== $s"
  python3 "$ROOT/tools/$s.py" | tail -1
  python3 "$ROOT/tools/verify_assets.py" "$WORK/index.html"
done
if cmp -s "$WORK/index.html" "$ROOT/index.html"; then echo "REBUILD IS BYTE-IDENTICAL TO index.html"; else echo "REBUILD DIFFERS FROM index.html"; exit 1; fi
rm -rf "$WORK"
