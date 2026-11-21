const { chromium } = require('playwright');
(async () => {
  const [,, file, prefix, scale] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: +scale });
  await p.goto('file://' + file); await p.waitForTimeout(300);
  for (const id of ['pipeline', 'cards']) await (await p.$('#' + id)).screenshot({ path: `${prefix}-${id}.png` });
  await b.close();
})();
