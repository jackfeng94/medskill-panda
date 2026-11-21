// Screenshot the README artwork sections: node shoot.js <page.html> <prefix> <scale>
const { chromium } = require('playwright');
(async () => {
  const [,, file, prefix, scale] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1680, height: 1200 }, deviceScaleFactor: +scale || 2 });
  await p.goto('file://' + file); await p.waitForTimeout(400);
  for (const id of ['pipeline', 'slides', 'manuscript', 'charts']) await (await p.$('#' + id)).screenshot({ path: `${prefix}-${id}.png` });
  await b.close();
})();
