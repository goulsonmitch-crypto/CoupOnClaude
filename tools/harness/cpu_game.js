// Play complete solo games against CPUs at every viewport, start to winner screen.
//   BASE=http://localhost:8092/index.html node tools/harness/cpu_game.js
// The human seat is driven like a player would: Income until 7 coins, then Coup; Pass on every
// response window; first option in any modal. Asserts zero pageerror / console errors, and that
// #action-area keeps one height for the whole game (no layout jump between turns).
const fs = require('fs');
const { VIEWPORTS, launch, newPage, load, startSolo, sleep } = require('./common');

async function drive(page) {
  return page.evaluate(() => {
    const scr = document.querySelector('.screen.active')?.id;
    const out = { scr, did: '', aa: null };
    const aa = document.getElementById('action-area');
    if (scr === 'screen-game' && aa) out.aa = Math.round(aa.getBoundingClientRect().height);
    const mo = document.getElementById('modal-overlay');
    if (mo && !mo.classList.contains('hidden')) {
      const tgt = mo.querySelector('.tgt-item'); if (tgt) { tgt.click(); out.did = 'modal-tgt'; return out; }
      const conf = mo.querySelector('#modal-actions .btn.primary');
      const pick = mo.querySelector('.exch-card:not(.selected):not(.kept):not(.ordered)');
      if (conf && conf.disabled && pick) { pick.click(); out.did = 'exch-pick'; return out; }
      const btns = [...mo.querySelectorAll('#modal-actions .btn')].filter(b => !b.disabled);
      const acc = btns.find(b => /accept|keep playing|close|done|ok/i.test(b.textContent)) || btns[btns.length - 1];
      if (acc) { acc.click(); out.did = 'modal-btn:' + acc.textContent.trim(); }
      return out;
    }
    if (scr === 'screen-reveal' || scr === 'screen-winner') return out;
    const coup = document.querySelector('.action-card.ac-coup:not(.disabled)');
    const inc = document.querySelector('.action-card.ac-income:not(.disabled)');
    const any = document.querySelector('.action-card:not(.disabled)');
    const c = coup || inc || any;
    if (c && !window.__lastClick || (c && Date.now() - window.__lastClick > 900)) {
      if (c) { window.__lastClick = Date.now(); c.click(); out.did = 'action:' + c.className; return out; }
    }
    const pass = document.querySelector('.respond-zone.rz-pass');
    if (pass) { pass.click(); out.did = 'pass'; }
    return out;
  });
}

async function playOne(browser, vp, BASE, seed) {
  const { ctx, page } = await newPage(browser, vp, seed);
  await load(page, BASE);
  await startSolo(page, 'standard', 3);
  const heights = new Map();
  const t0 = Date.now();
  let last = '', winner = false, steps = 0;
  while (Date.now() - t0 < 12 * 60 * 1000) {
    const st = await drive(page);
    steps++;
    if (st.aa != null) heights.set(st.aa, (heights.get(st.aa) || 0) + 1);
    if (st.scr === 'screen-reveal') {
      await sleep(1500);
      await page.evaluate(() => revealToWinner());
      await sleep(1500);
      await page.evaluate(() => { try { closeRecapOverlay(); } catch (e) {} });
      winner = (await page.evaluate(() => document.querySelector('.screen.active')?.id)) === 'screen-winner';
      break;
    }
    if (st.scr === 'screen-winner') { winner = true; break; }
    last = st.did || last;
    await sleep(250);
  }
  const info = await page.evaluate(() => ({
    winner: document.getElementById('winner-name')?.textContent, turns: G && G.turnsTaken, errs: window.__errors,
  }));
  const r = {
    viewport: vp.name, completed: winner, seconds: Math.round((Date.now() - t0) / 1000), steps,
    winnerName: info.winner, turns: info.turns,
    actionAreaHeights: Object.fromEntries(heights),
    pageerrors: page.__log.pageerrors, consoleErrors: page.__log.consoleErrors, windowErrors: info.errs,
  };
  await ctx.close();
  return r;
}

(async () => {
  const BASE = process.env.BASE || 'http://localhost:8092/index.html';
  const OUT = process.env.OUT || 'tools/harness/cpu_game_result.json';
  const only = process.env.VP ? process.env.VP.split(',') : null;
  const browser = await launch();
  const vps = VIEWPORTS.filter(v => !only || only.includes(v.name));
  const results = await Promise.all(vps.map((vp, i) => playOne(browser, vp, BASE, 4242 + i)));
  await browser.close();
  fs.writeFileSync(OUT, JSON.stringify(results, null, 2));
  let bad = 0;
  for (const r of results) {
    const hs = Object.keys(r.actionAreaHeights);
    const ok = r.completed && !r.pageerrors.length && !r.consoleErrors.length && !(r.windowErrors || []).length && hs.length === 1;
    if (!ok) bad++;
    console.log(`${r.viewport.padEnd(13)} ${ok ? 'PASS' : 'FAIL'} completed=${r.completed} ${r.seconds}s turns=${r.turns} winner="${r.winnerName}" pageerrors=${r.pageerrors.length} console=${r.consoleErrors.length} actionAreaHeights=${JSON.stringify(r.actionAreaHeights)}`);
    if (r.consoleErrors.length) console.log('   console:', [...new Set(r.consoleErrors)].slice(0, 5));
    if (r.pageerrors.length) console.log('   pageerror:', [...new Set(r.pageerrors)].slice(0, 5));
  }
  process.exit(bad && !process.argv.includes('--report-only') ? 1 : 0);
})();
