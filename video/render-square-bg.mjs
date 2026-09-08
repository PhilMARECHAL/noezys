import { chromium } from 'playwright';
import path from 'path';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell', args:['--force-color-profile=srgb'] });
const p = await b.newPage({ viewport:{ width:1080, height:1080 }, deviceScaleFactor:1 });
await p.goto('file://' + path.resolve('square-bg.html'));
await p.waitForTimeout(500);
await p.screenshot({ path:'hf-shots/square-bg.png' });
await b.close(); console.log('bg done');
