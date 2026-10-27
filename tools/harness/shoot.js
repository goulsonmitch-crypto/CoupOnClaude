// Screenshot every screen at every viewport.
//   BASE=http://localhost:8092/index.html OUT=tools/shots/after node tools/harness/shoot.js
const fs = require('fs');
const path = require('path');
const { VIEWPORTS, SCREENS, launch, newPage, load, gotoScreen } = require('./common');

(async () => {
  const BASE = process.env.BASE || 'http://localhost:8092/index.html';
  const OUT = process.env.OUT || 'tools/shots/after';
  const only = process.env.VP ? process.env.VP.split(',') : null;
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await launch();
  const report = {};
  for (const vp of VIEWPORTS) {
    if (only && !only.includes(vp.name)) continue;
    const { ctx, page } = await newPage(browser, vp);
    await load(page, BASE);
    for (const sc of SCREENS) {
      try {
        await gotoScreen(page, sc);
        await page.screenshot({ path: path.join(OUT, `${vp.name}__${sc}.jpg`), type: 'jpeg', quality: 72 });
        process.stdout.write(`  ${vp.name} ${sc} ok\n`);
      } catch (e) {
        process.stdout.write(`  ${vp.name} ${sc} FAILED ${e.message}\n`);
      }
    }
    const inPage = await page.evaluate(() => window.__errors || []);
    report[vp.name] = { pageerrors: page.__log.pageerrors, consoleErrors: page.__log.consoleErrors, windowErrors: inPage };
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(OUT, 'errors.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
})();
