/* Renders pub.html (FR or EN) frame-by-frame, then encodes to MP4.
   Usage: node render-pub.mjs fr|en [fps] */
import { chromium } from 'playwright-core';
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.dirname(fileURLToPath(import.meta.url));
const LANG = process.argv[2] || 'fr';
const FPS = Number(process.argv[3]) || 30;
const DURATION = 30;
const FRAMES = FPS * DURATION;
const framesDir = path.join(DIR, 'frames');

fs.rmSync(framesDir, { recursive: true, force: true });
fs.mkdirSync(framesDir, { recursive: true });

const exe = [
  '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell',
  '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
].find(p => fs.existsSync(p));

const browser = await chromium.launch({ executablePath: exe, args: ['--force-color-profile=srgb', '--disable-lcd-text', '--hide-scrollbars'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto('file://' + path.join(DIR, 'pub.html') + '?lang=' + LANG);
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(500);

const t0 = Date.now();
for (let i = 0; i < FRAMES; i++) {
  await page.evaluate(t => window.seek(t), i / FPS);
  await page.screenshot({ path: path.join(framesDir, `f${String(i).padStart(4, '0')}.png`) });
  if (i % 120 === 0) console.log(`[${LANG}] frame ${i}/${FRAMES}`);
}
await browser.close();

const out = path.join(DIR, `noezys-pub-${LANG}.mp4`);
execSync(
  `ffmpeg -y -loglevel error -framerate ${FPS} -i ${framesDir}/f%04d.png ` +
  `-c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart ${out}`,
  { stdio: 'inherit' }
);
console.log(`done → ${out} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
