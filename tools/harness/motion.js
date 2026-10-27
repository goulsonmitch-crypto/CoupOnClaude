// Motion checks for items 10-11.
//   BASE=http://localhost:8092/index.html node tools/harness/motion.js
// 1. prefers-reduced-motion: reduce -> every running CSS animation/transition is <= 10ms
//    (delays may remain), and the active-turn frame / my-turn dock still look active.
// 2. Normal motion -> after the table settles, will-change is only held by elements in an
//    active animated state (no compositor-layer leaks), and no animation targets layout
//    properties (top/left/width/height).
const fs = require('fs');
const { launch, sleep, load, startSolo, waitMyTurn } = require('./common');

(async () => {
  const BASE = process.env.BASE || 'http://localhost:8092/index.html';
  const browser = await launch();
  const out = {};
  let bad = 0;

  // ---- reduced motion
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce', ignoreHTTPSErrors: true });
    await ctx.addInitScript(() => { try { localStorage.setItem('coup_settings', JSON.stringify({ voice: false, sound: false, fastCPU: true, tempo: 'fast', noTimeLimit: true })); } catch (e) {} });
    const page = await ctx.newPage();
    await load(page, BASE);
    await startSolo(page, 'standard', 3);
    await waitMyTurn(page);
    await sleep(1500);
    const r = await page.evaluate(() => {
      // make an opponent the active seat so the active-turn frame is on screen
      G.currentTurn = 1; G.phase = 'action'; renderGame();
      const anims = document.getAnimations().map(a => {
        const t = a.effect && a.effect.getTiming ? a.effect.getTiming() : {};
        return { name: a.animationName || a.transitionProperty || a.constructor.name, duration: +t.duration || 0, iterations: t.iterations };
      });
      const long = anims.filter(a => a.duration > 10 || a.iterations === Infinity);
      const fr = document.querySelector('.arena-frame.active-turn .af-body');
      const glow = document.querySelector('.arena-frame.active-turn');
      return {
        animations: anims.length, longOrInfinite: long,
        activeFrameRing: fr ? getComputedStyle(fr).boxShadow.includes('240, 201, 102') : false,
        activeGlowOpacity: glow ? getComputedStyle(glow, '::before').opacity : null,
      };
    });
    out.reducedMotion = r;
    const ok = r.longOrInfinite.length === 0 && r.activeFrameRing && r.activeGlowOpacity === '1';
    if (!ok) bad++;
    console.log(`reduced-motion: ${ok ? 'PASS' : 'FAIL'} animations=${r.animations} long/infinite=${r.longOrInfinite.length} activeRing=${r.activeFrameRing} glowOpacity=${r.activeGlowOpacity}`);
    await ctx.close();
  }

  // ---- normal motion: layers + layout-free animation
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, ignoreHTTPSErrors: true });
    await ctx.addInitScript(() => { try { localStorage.setItem('coup_settings', JSON.stringify({ voice: false, sound: false, fastCPU: true, tempo: 'fast', noTimeLimit: true })); } catch (e) {} });
    const page = await ctx.newPage();
    await load(page, BASE);
    await startSolo(page, 'standard', 3);
    await waitMyTurn(page);
    await sleep(3500);
    const r = await page.evaluate(() => {
      const holders = [];
      document.querySelectorAll('*').forEach(el => {
        for (const pseudo of [null, '::before', '::after']) {
          const wc = getComputedStyle(el, pseudo).willChange;
          if (wc && wc !== 'auto') holders.push((el.id ? '#' + el.id : el.className && typeof el.className === 'string' ? '.' + el.className.split(' ').join('.') : el.tagName) + (pseudo || '') + ' => ' + wc);
        }
      });
      const LAYOUT = /^(top|left|right|bottom|width|height|margin|padding)/;
      const layoutAnims = [];
      for (const sheet of document.styleSheets) {
        let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
        for (const rule of rules) {
          if (rule.type === CSSRule.KEYFRAMES_RULE) for (const kf of rule.cssRules) for (let i = 0; i < kf.style.length; i++) if (LAYOUT.test(kf.style[i])) layoutAnims.push(rule.name + ':' + kf.style[i]);
        }
      }
      return { holders, layoutAnims: [...new Set(layoutAnims)] };
    });
    // allowed: state-scoped pulse layers, the floating pit card, transient flyers
    const allowed = /(active-turn|my-turn-glow|target-preview|targeted|live-slot|live|pit-card|flying|ac-flying|confetti|verdict|flash-banner|toast)/;
    const leaks = r.holders.filter(h => !allowed.test(h));
    out.layers = { holders: r.holders, leaks, layoutKeyframes: r.layoutAnims };
    const ok = leaks.length === 0 && r.layoutAnims.length === 0;
    if (!ok) bad++;
    console.log(`layers: ${ok ? 'PASS' : 'FAIL'} will-change holders=${r.holders.length} leaks=${leaks.length} layout-keyframes=${r.layoutAnims.length}`);
    if (leaks.length) console.log('  leaks:', leaks.slice(0, 10));
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync(process.env.OUT || 'tools/harness/motion_result.json', JSON.stringify(out, null, 2));
  process.exit(bad && !process.argv.includes('--report-only') ? 1 : 0);
})();
