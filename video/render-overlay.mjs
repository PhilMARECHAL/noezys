// Rend les frames transparentes de la fenêtre interactive, calées sur la durée du clip.
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const OVERLAY = process.argv[2] || 'overlay-clip1.html';
const OUTDIR = process.argv[3] || 'frames-overlay';
const DUR = parseFloat(process.argv[4] || '8.04');
const FPS = 24;
const N = Math.round(DUR * FPS);

fs.rmSync(OUTDIR, { recursive: true, force: true });
fs.mkdirSync(OUTDIR, { recursive: true });

const browser = await chromium.launch({
  executablePath: '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell',
  args: ['--force-color-profile=srgb'],
});
const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
await page.goto('file://' + path.resolve(OVERLAY));
await page.waitForTimeout(600);

for (let i = 0; i < N; i++) {
  const t = i / FPS;
  await page.evaluate((tt) => window.seek(tt), t);
  await page.screenshot({
    path: path.join(OUTDIR, `f${String(i).padStart(4, '0')}.png`),
    omitBackground: true,
    clip: { x: 0, y: 0, width: 1280, height: 720 },
  });
}
await browser.close();
console.log('frames:', N, 'in', OUTDIR);
