// Static checks: every inline <script> compiles, the stylesheet has balanced braces,
// file size is within +-8% of v91, and index.html == coup_v92.html byte for byte.
//   node tools/harness/parse_check.js [baselineBytes=1224420]
const fs = require('fs'); const vm = require('vm'); const crypto = require('crypto');
const html = fs.readFileSync('index.html', 'utf8');
let ok = true;
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
scripts.forEach((src, i) => {
  try { new vm.Script(src, { filename: `inline-script-${i}.js` }); }
  catch (e) { ok = false; console.log(`script ${i}: SYNTAX ERROR ${e.message}`); }
});
console.log(`inline scripts compiled: ${scripts.length}`);
const css = html.slice(html.indexOf('<style>') + 7, html.indexOf('</style>'));
const open = (css.match(/\{/g) || []).length, close = (css.match(/\}/g) || []).length;
console.log(`stylesheet braces: ${open} open / ${close} close ${open === close ? 'balanced' : 'UNBALANCED'}`);
if (open !== close) ok = false;
const base = +(process.argv[2] || 1224420), size = fs.statSync('index.html').size;
const pct = ((size - base) / base * 100);
console.log(`size: ${size} bytes vs v91 ${base} (${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%) ${Math.abs(pct) <= 8 ? 'within +-8%' : 'OUTSIDE +-8%'}`);
if (Math.abs(pct) > 8) ok = false;
const h = f => crypto.createHash('md5').update(fs.readFileSync(f)).digest('hex');
if (fs.existsSync('coup_v92.html')) {
  const same = h('index.html') === h('coup_v92.html');
  console.log(`coup_v92.html ${same ? 'byte-identical to' : 'DIFFERS from'} index.html (${h('index.html')})`);
  if (!same) ok = false;
} else { console.log('coup_v92.html missing'); ok = false; }
console.log(ok ? 'PARSE/SIZE/COPY: PASS' : 'PARSE/SIZE/COPY: FAIL');
process.exit(ok ? 0 : 1);
