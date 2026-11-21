const { chromium } = require('playwright');
(async () => {
  const [,, file, prefix, n] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await p.goto('file://' + file); await p.addStyleTag({content: '#tools{display:none!important}'}); await p.waitForTimeout(1500);
  for (let i = 1; i <= +n; i++) {
    await p.mouse.move(1900, 10);
    await p.screenshot({ path: `${prefix}-${i}.png` });
    await p.keyboard.press('ArrowRight'); await p.waitForTimeout(1700);
  }
  await b.close();
})();
