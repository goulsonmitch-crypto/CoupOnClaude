// Effective on-screen scale of all 20 crew portraits in every context they appear in, at the
// largest sizes the layout produces (2-player table = biggest arena frames).
//   BASE=http://localhost:8092/index.html node tools/harness/portraits.js
// scale = (rendered image px) / (intrinsic image px), including object-fit and every ancestor transform.
const fs = require('fs');
const { launch, newPage, load, startSolo, waitMyTurn, sleep } = require('./common');

const VPS = [
  { name: 'desktop-1920', width: 1920, height: 1080 },
  { name: 'laptop-1440', width: 1440, height: 900 },
  { name: 'ipad-1024', width: 1024, height: 768, mobile: true },
  { name: 'iphone14-390', width: 390, height: 844, mobile: true },
];

function measureAll() {
  const scaleOf = el => {
    let s = 1;
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.transform && cs.transform !== 'none') { const m = new DOMMatrixReadOnly(cs.transform); s *= Math.sqrt(m.a * m.a + m.b * m.b); }
      if (cs.scale && cs.scale !== 'none') s *= parseFloat(cs.scale.split(' ')[0]);
    }
    return s;
  };
  const res = [];
  document.querySelectorAll('img[src^="data:image/webp"]').forEach(img => {
    if (!img.naturalWidth) return;
    const r = img.getBoundingClientRect();
    if (r.width < 1) return;
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
    const key = Object.keys(CHARACTER_IMAGES).find(k => CHARACTER_IMAGES[k] === img.getAttribute('src')) || '?';
    const ctx = img.closest('.af-portrait') ? 'arena-frame' : img.closest('.me-chip') ? 'my-dock' : img.closest('.win-frame') ? 'winner'
      : img.closest('.wall-frame2') ? 'salon-wall' : img.closest('.char-avatar') ? 'char-pick' : img.closest('.pit-chip') ? 'pit' : img.closest('.lobby-avatar') ? 'lobby' : 'other';
    res.push({ key, ctx, scale: +s.toFixed(3), nw, nh });
  });
  return res;
}

(async () => {
  const BASE = process.env.BASE || 'http://localhost:8092/index.html';
  const OUT = process.env.OUT || 'tools/harness/portraits_result.json';
  const browser = await launch();
  const crewOut = {};
  const record = (vp, rows) => rows.forEach(r => {
    if (r.key === '?') return;
    const k = crewOut[r.key] = crewOut[r.key] || { nw: r.nw, nh: r.nh, max: 0, where: '' , ctx: {} };
    const ck = `${vp}/${r.ctx}`;
    k.ctx[ck] = Math.max(k.ctx[ck] || 0, r.scale);
    if (r.scale > k.max) { k.max = r.scale; k.where = ck; }
  });
  for (const vp of VPS) {
    const { ctx, page } = await newPage(browser, vp);
    await load(page, BASE);
    await sleep(300);
    record(vp.name, await page.evaluate(measureAll));                 // salon walls
    await page.evaluate(() => startSoloFlow()); await sleep(400);
    record(vp.name, await page.evaluate(measureAll));                 // character grid
    await startSolo(page, 'standard', 1);
    await waitMyTurn(page, 30000);
    await sleep(2500);
    const crew = await page.evaluate(() => Object.keys(CREW_NAMES));
    for (const key of crew) {
      await page.evaluate(key => {
        const opp = G.players.find(p => p.id !== ME); opp.character = key; opp.characterVariant = null;
        const me = G.players.find(p => p.id === ME); me.character = key; me.characterVariant = null;
        renderGame();
      }, key);
      await sleep(120);
      record(vp.name, await page.evaluate(measureAll));
      await page.evaluate(key => {   // the winner tableau, rendered exactly as showWinner() does
        const me = G.players.find(p => p.id === ME);
        document.getElementById('winner-portrait').innerHTML = `<div class="win-frame"><div class="win-crown">👑</div><div class="win-port">${charImgHtml(me)}</div></div>`;
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
        document.getElementById('screen-winner').classList.add('active');
      }, key);
      await sleep(900);   // let winFrameIn finish
      record(vp.name, (await page.evaluate(measureAll)).filter(r => r.ctx === 'winner'));
      await page.evaluate(() => { document.querySelectorAll('.screen').forEach(s => s.classList.remove('active')); document.getElementById('screen-game').classList.add('active'); });
    }
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync(OUT, JSON.stringify(crewOut, null, 2));
  const keys = Object.keys(crewOut).sort((a, b) => crewOut[b].max - crewOut[a].max);
  for (const k of keys) console.log(`${k.padEnd(10)} ${String(crewOut[k].nw + 'x' + crewOut[k].nh).padEnd(8)} max ${crewOut[k].max.toFixed(3)}x  @ ${crewOut[k].where}`);
  const over = keys.filter(k => crewOut[k].max > 1.0005);
  console.log(over.length ? `OVER 1.0x: ${over.join(', ')}` : 'ALL PORTRAITS <= 1.0x');
  process.exit(over.length && !process.argv.includes('--report-only') ? 1 : 0);
})();
