// Shared Playwright helpers for the v92 visual-pass harnesses.
// Serve the build under test with:  python3 -m http.server <port> --directory <dir>
// then point BASE at it, e.g. BASE=http://localhost:8092/index.html
const { chromium } = require('playwright');

const VIEWPORTS = [
  { name: 'desktop-1920', width: 1920, height: 1080, mobile: false },
  { name: 'laptop-1440', width: 1440, height: 900, mobile: false },
  { name: 'ipad-1024', width: 1024, height: 768, mobile: true },
  { name: 'iphone14-390', width: 390, height: 844, mobile: true },
  { name: 'android-360', width: 360, height: 640, mobile: true },
];

// Deterministic Math.random + quiet audio so before/after runs deal the same hands.
const INIT = `
(() => {
  let s = 0x9e3779b9 ^ (window.__SEED || 1913);
  Math.random = function () {
    s |= 0; s = (s + 0x6D2B79F5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  try {
    localStorage.setItem('coup_settings', JSON.stringify({
      voice: false, sound: false, fastCPU: true, tempo: 'fast', noTimeLimit: true, cpuDifficulty: 'hard'
    }));
  } catch (e) {}
  window.__errors = [];
  window.addEventListener('error', e => window.__errors.push(String(e.message || e)));
  window.addEventListener('unhandledrejection', e => window.__errors.push('rejection: ' + String(e.reason)));
})();
`;

async function launch() {
  const opts = { args: ['--autoplay-policy=no-user-gesture-required', '--use-fake-ui-for-media-stream'] };
  if (process.env.HTTPS_PROXY) opts.proxy = { server: process.env.HTTPS_PROXY, bypass: 'localhost,127.0.0.1' };
  return chromium.launch(opts);
}

async function newPage(browser, vp, seed = 1913) {
  const ctx = await browser.newContext({
    viewport: { width: vp.width, height: vp.height },
    deviceScaleFactor: 1,
    isMobile: !!vp.mobile && vp.width < 800,
    hasTouch: !!vp.mobile,
    ignoreHTTPSErrors: true,
  });
  await ctx.addInitScript(`window.__SEED=${seed};` + INIT);
  const page = await ctx.newPage();
  page.__log = { pageerrors: [], consoleErrors: [] };
  page.on('pageerror', e => page.__log.pageerrors.push(String(e && e.message || e)));
  page.on('console', m => {
    if (m.type() !== 'error') return;
    const t = m.text();
    // Network noise from the sandbox (Firebase long-poll, favicon) is not a page bug.
    if (/favicon|net::ERR_|Failed to load resource/i.test(t)) return;
    page.__log.consoleErrors.push(t);
  });
  return { ctx, page };
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function load(page, base) {
  await page.goto(base, { waitUntil: 'load', timeout: 60000 });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await sleep(600);
}

// Put the build into each of the nine states. Uses only the game's own public entry points.
async function gotoScreen(page, screen) {
  switch (screen) {
    case 'landing':
      await page.evaluate(() => { try { goHome(); } catch (e) {} });
      await sleep(500); return;
    case 'character':
      await page.evaluate(() => startSoloFlow());
      await sleep(500); return;
    case 'lobby':
      await page.evaluate(() => { soloCpuCount = 3; selectedGameMode = 'standard'; soloWaitingChar = 'eden'; soloWaitingCpuChars = []; enterSoloWaiting(); });
      await sleep(500); return;
    case 'waiting':
      await page.evaluate(() => showScr('waiting'));
      await sleep(500); return;
    case 'game':
      await startSolo(page, 'standard', 3);
      await waitMyTurn(page);
      await sleep(2600); return;
    case 'modal':
      await page.evaluate(() => openSettings());
      await sleep(600); return;
    case 'auction':
      await page.evaluate(() => { try { goHome(); } catch (e) {} });
      await startSolo(page, 'auction', 3);
      await sleep(2200); return;
    case 'reveal':
      await page.evaluate(() => { try { goHome(); } catch (e) {} });
      await startSolo(page, 'standard', 3);
      await waitMyTurn(page);
      await page.evaluate(() => {
        G.players.forEach(p => { if (p.isCPU) { p.cards.forEach(c => c.alive = false); p.eliminated = true; } });
        renderGame();
        const me = G.players.find(p => p.id === ME);
        showWinner(me.displayName || me.name, me.id);
      });
      await sleep(4600);
      await clearTransient(page); return;
    case 'winner':
      await page.evaluate(() => { revealToWinner(); try { closeRecapOverlay(); } catch (e) {} });
      await sleep(1400);
      await clearTransient(page); return;
  }
}

// Flash banners / confetti are timed overlays; strip them so before/after frames compare like for like.
async function clearTransient(page) {
  await page.evaluate(() => {
    const fa = document.getElementById('flash-area'); if (fa) fa.innerHTML = '';
    document.querySelectorAll('.confetti-piece,.verdict-stamp').forEach(e => e.remove());
  });
  await sleep(150);
}

async function startSolo(page, mode, cpus) {
  await page.evaluate(([mode, cpus]) => {
    selectedGameMode = mode; soloCpuCount = cpus; soloWaitingChar = 'eden'; soloWaitingCpuChars = [];
    enterSoloWaiting();
    startSoloFromWaiting();
  }, [mode, cpus]);
}

async function waitMyTurn(page, timeout = 45000) {
  try {
    await page.waitForSelector('.action-card:not(.disabled)', { timeout });
  } catch (e) { /* screenshot whatever state we reached */ }
}

const SCREENS = ['landing', 'character', 'lobby', 'waiting', 'game', 'modal', 'auction', 'reveal', 'winner'];

module.exports = { VIEWPORTS, SCREENS, launch, newPage, load, gotoScreen, startSolo, waitMyTurn, sleep, clearTransient };
