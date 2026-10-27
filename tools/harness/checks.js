// Programmatic assertions for the v92 visual pass, run at all five viewports on every screen.
//   BASE=http://localhost:8092/index.html node tools/harness/checks.js  [--report-only]
// Checks (each produces a list of violations):
//   font      — every visible, non-empty text node computes to >= 11px
//   overflow  — no horizontal page scroll; no visible element pokes outside the viewport
//               (unless it sits in a horizontal scroller or is clipped by an on-screen ancestor);
//               no text silently clipped by overflow:hidden without an ellipsis
//   portrait  — no character portrait renders above 1.0x its intrinsic pixel size
//   focus     — every visible interactive element is keyboard-focusable and shows a
//               non-zero :focus-visible outline
const fs = require('fs');
const { VIEWPORTS, launch, newPage, load, gotoScreen, sleep } = require('./common');

const CHECK_SCREENS = ['landing', 'rules', 'character', 'lobby', 'waiting', 'game', 'modal', 'auction', 'reveal', 'winner'];

async function enter(page, sc) {
  if (sc === 'rules') {
    await page.evaluate(() => { try { goHome(); } catch (e) {} openRulesOverlay(); });
    await sleep(700); return;
  }
  if (sc === 'character') await page.evaluate(() => { try { closeRulesOverlay(); } catch (e) {} });
  await gotoScreen(page, sc);
}

// Runs in the page. Returns { minFont, font:[], overflow:[], portrait:[], focusables:[] }
function measure() {
  const out = { minFont: null, minFontAt: '', font: [], overflow: [], portrait: [], focusables: [] };
  const W = innerWidth, H = innerHeight;
  const path = el => {
    const p = [];
    for (let e = el; e && e !== document.body && p.length < 4; e = e.parentElement)
      p.unshift(e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.classList.length ? '.' + [...e.classList].slice(0, 2).join('.') : ''));
    return p.join(' > ');
  };
  const hiddenByAncestor = el => {
    for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) return true;
      if (e.id === 'av-pool' || e.id === 'flash-area' || e.id === 'toast-area') return true;
      if (e.classList.contains('rules-overlay') && !e.classList.contains('open')) return true;
      if (e.classList.contains('ac-flying') || e.classList.contains('flying-card') || e.classList.contains('flying-coin') || e.classList.contains('confetti-piece')) return true;
    }
    return false;
  };
  // ---- fonts
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  for (let n = tw.nextNode(); n; n = tw.nextNode()) {
    if (!n.nodeValue.trim()) continue;
    const el = n.parentElement;
    if (!el || seen.has(el)) continue;
    seen.add(el);
    if (['SCRIPT', 'STYLE', 'TITLE', 'OPTION'].includes(el.tagName)) continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    if (hiddenByAncestor(el)) continue;
    const fsz = parseFloat(getComputedStyle(el).fontSize);
    if (out.minFont === null || fsz < out.minFont) { out.minFont = fsz; out.minFontAt = path(el) + ' "' + n.nodeValue.trim().slice(0, 24) + '"'; }
    if (fsz < 11 - 0.01) out.font.push(`${fsz.toFixed(2)}px ${path(el)} "${n.nodeValue.trim().slice(0, 30)}"`);
  }
  // ---- overflow
  if (document.documentElement.scrollWidth > W + 1) out.overflow.push(`page scrollWidth ${document.documentElement.scrollWidth} > ${W}`);
  const act = document.querySelector('.screen.active');
  if (act && act.scrollWidth > act.clientWidth + 1 && getComputedStyle(act).overflowX !== 'hidden')
    out.overflow.push(`screen ${act.id} scrollWidth ${act.scrollWidth} > ${act.clientWidth}`);
  const roots = [act, document.querySelector('.modal-overlay:not(.hidden)'), document.querySelector('.rules-overlay.open')].filter(Boolean);
  const all = new Set(); roots.forEach(r => r.querySelectorAll('*').forEach(e => all.add(e)));
  for (const el of all) {
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) continue;
    if (hiddenByAncestor(el)) continue;
    const cs = getComputedStyle(el);
    if (cs.position === 'fixed' && (r.right < 0 || r.left > W)) continue;
    if (r.left < -1 || r.right > W + 1) {
      // allowed when an ancestor clips it and that ancestor is on-screen, or it lives in a horizontal scroller
      let ok = false;
      for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
        const acs = getComputedStyle(a);
        if (/(auto|scroll)/.test(acs.overflowX)) { ok = true; break; }
        if (acs.overflowX !== 'visible' || acs.overflow === 'hidden' || acs.clipPath !== 'none') {
          const ar = a.getBoundingClientRect();
          if (ar.left >= -1 && ar.right <= W + 1) { ok = true; break; }
        }
      }
      if (!ok) out.overflow.push(`outside viewport [${Math.round(r.left)},${Math.round(r.right)}] ${path(el)}`);
    }
    // silent text clipping
    const hasText = [...el.childNodes].some(c => c.nodeType === 3 && c.nodeValue.trim());
    if (hasText && (cs.overflowX === 'hidden' || cs.overflow === 'hidden') && cs.textOverflow !== 'ellipsis'
        && el.scrollWidth > el.clientWidth + 2 && el.tagName !== 'INPUT') {
      out.overflow.push(`text clipped ${el.scrollWidth}>${el.clientWidth} ${path(el)} "${el.textContent.trim().slice(0, 24)}"`);
    }
  }
  // ---- portraits
  const scaleOf = el => {
    let s = 1;
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.transform && cs.transform !== 'none') {
        const m = new DOMMatrixReadOnly(cs.transform);
        s *= Math.sqrt(m.a * m.a + m.b * m.b);
      }
      if (cs.scale && cs.scale !== 'none') s *= parseFloat(cs.scale.split(' ')[0]);
      if (cs.zoom && cs.zoom !== '1' && cs.zoom !== 'normal') s *= parseFloat(cs.zoom);
    }
    return s;
  };
  document.querySelectorAll('img[src^="data:image/webp"]').forEach(img => {
    if (!img.naturalWidth) return;
    const r = img.getBoundingClientRect();
    if (r.width < 1 || hiddenByAncestor(img)) return;
    const cs = getComputedStyle(img);
    const bw = img.clientWidth, bh = img.clientHeight, nw = img.naturalWidth, nh = img.naturalHeight;
    let s;
    switch (cs.objectFit) {
      case 'cover': s = Math.max(bw / nw, bh / nh); break;
      case 'contain': s = Math.min(bw / nw, bh / nh); break;
      case 'scale-down': s = Math.min(1, Math.min(bw / nw, bh / nh)); break;
      case 'none': s = 1; break;
      default: s = Math.max(bw / nw, bh / nh);
    }
    s *= scaleOf(img);
    const key = Object.keys(window.CHARACTER_IMAGES || {}).find(k => CHARACTER_IMAGES[k] === img.getAttribute('src')) || '?';
    out.portrait.push({ key, scale: +s.toFixed(3), ctx: path(img), nw, nh, box: `${bw}x${bh}` });
  });
  // ---- focusables
  const sel = 'button, a[href], input, select, textarea, [onclick], [tabindex], .action-card, .respond-zone, .exch-card, .tgt-item, .char-card, .mode-card, .toggle';
  const cands = new Set();
  roots.forEach(r => r.querySelectorAll(sel).forEach(e => cands.add(e)));
  document.querySelectorAll('#top-bar button, .modal-overlay:not(.hidden) *').forEach(e => { if (e.matches(sel)) cands.add(e); });
  const list = [];
  cands.forEach(e => {
    const r = e.getBoundingClientRect();
    if (r.width < 1 || r.height < 1 || hiddenByAncestor(e)) return;
    if (e.matches('input[type=range]') && false) return;
    if (e.disabled) return;
    if (!e.id) e.id = '__f' + Math.random().toString(36).slice(2, 8);
    list.push(e.id);
  });
  out.focusables = list;
  return out;
}

async function focusRings(page, ids) {
  const bad = [];
  await page.keyboard.press('Shift'); // mark the session as keyboard-driven so :focus-visible applies
  for (const id of ids) {
    const res = await page.evaluate(id => {
      const e = document.getElementById(id);
      if (!e) return null;
      const desc = e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.split(' ').slice(0, 2).join('.') : '') + ' "' + (e.textContent || '').trim().slice(0, 18) + '"';
      e.focus({ preventScroll: true });
      if (document.activeElement !== e) return { ok: false, why: 'not focusable', desc };
      const cs = getComputedStyle(e);
      const w = parseFloat(cs.outlineWidth) || 0;
      const vis = e.matches(':focus-visible');
      const ok = vis && cs.outlineStyle !== 'none' && w > 0;
      e.blur();
      return { ok, why: ok ? '' : `focus-visible=${vis} outline=${cs.outlineStyle} ${w}px`, desc };
    }, id);
    if (res && !res.ok) bad.push(`${res.why} ${res.desc}`);
  }
  return bad;
}

(async () => {
  const BASE = process.env.BASE || 'http://localhost:8092/index.html';
  const OUT = process.env.OUT || 'tools/harness/checks_result.json';
  const only = process.env.VP ? process.env.VP.split(',') : null;
  const browser = await launch();
  const result = {};
  let failures = 0;
  for (const vp of VIEWPORTS) {
    if (only && !only.includes(vp.name)) continue;
    const { ctx, page } = await newPage(browser, vp);
    await load(page, BASE);
    result[vp.name] = {};
    for (const sc of CHECK_SCREENS) {
      await enter(page, sc);
      const m = await page.evaluate(measure);
      const focus = await focusRings(page, m.focusables);
      const portraitOver = m.portrait.filter(p => p.scale > 1.0005).map(p => `${p.key} ${p.scale}x ${p.box} ${p.ctx}`);
      const r = { minFont: m.minFont, minFontAt: m.minFontAt, font: m.font, overflow: m.overflow, portraitOver, focus, portraits: m.portrait, focusableCount: m.focusables.length };
      result[vp.name][sc] = r;
      const n = m.font.length + m.overflow.length + portraitOver.length + focus.length;
      failures += n;
      console.log(`${vp.name.padEnd(13)} ${sc.padEnd(10)} minFont=${m.minFont}px font:${m.font.length} overflow:${m.overflow.length} portrait>1:${portraitOver.length} focus:${focus.length}/${m.focusables.length}`);
    }
    result[vp.name].__errors = { pageerrors: page.__log.pageerrors, consoleErrors: page.__log.consoleErrors };
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync(OUT, JSON.stringify(result, null, 2));
  console.log(`TOTAL VIOLATIONS: ${failures}`);
  process.exit(failures && !process.argv.includes('--report-only') ? 1 : 0);
})();
