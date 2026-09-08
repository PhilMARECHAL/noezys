import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
const DUR = 4.5, FPS = 24, N = Math.round(DUR * FPS);
const OUT = 'frames-endcard';
fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell', args: ['--force-color-profile=srgb'] });
const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
await p.goto('file://' + path.resolve('endcard.html'));
await p.waitForTimeout(500);
for (let i = 0; i < N; i++) { await p.evaluate(t => window.seek(t), i / FPS); await p.screenshot({ path: path.join(OUT, `f${String(i).padStart(4,'0')}.png`) }); }
await b.close(); console.log('endcard frames', N);
