#!/usr/bin/env node
/* Buddy — offline behaviour test
 *
 * Run:
 *   npx playwright install chromium     # once
 *   node scripts/test-buddy-offline.js
 *
 * Buddy is used by people whose phone is becoming difficult to use, which
 * means it has to open with no signal — a lift, a basement flat, a hospital
 * car park. This test proves that claim rather than asserting it:
 *
 *   1. serve static/buddy over HTTP (service workers need a secure context;
 *      http://localhost counts as one)
 *   2. load the page, wait for the service worker to activate and precache
 *   3. cut the network
 *   4. reload and assert the app still rendered and still has its data
 *
 * It also checks the pieces that make the app installable: the manifest is
 * served and parses, the icons resolve, and sw.js is served as JavaScript.
 *
 * Needs Playwright and nothing else:
 *   npm i -g playwright && npx playwright install chromium
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');

const ROOT = path.resolve(__dirname, '..', 'static', 'buddy');
const PORT = 8137;

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.md': 'text/markdown; charset=utf-8',
};

function serve() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const url = new URL(req.url, `http://localhost:${PORT}`);
      let rel = decodeURIComponent(url.pathname);
      if (rel === '/') rel = '/index.html';
      const file = path.join(ROOT, rel);
      if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('not found');
        return;
      }
      res.writeHead(200, {
        'Content-Type': MIME[path.extname(file)] || 'application/octet-stream',
        'Cache-Control': 'no-cache',
        'Service-Worker-Allowed': '/',
      });
      fs.createReadStream(file).pipe(res);
    });
    server.listen(PORT, () => resolve(server));
  });
}

const results = [];
function check(name, ok, detail) {
  results.push({ name, ok, detail });
  console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? '  — ' + detail : ''}`);
}

(async () => {
  const server = await serve();
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  const pageErrors = [];
  page.on('pageerror', (e) => pageErrors.push(e.message));

  const base = `http://localhost:${PORT}`;

  try {
    // ---- 1. first load ------------------------------------------------
    console.log('\n[1] first load (online)');
    await page.goto(`${base}/`, { waitUntil: 'networkidle' });

    const manifestHref = await page.getAttribute('link[rel="manifest"]', 'href');
    check('manifest link present', !!manifestHref, manifestHref);

    const manifestRes = await page.request.get(`${base}/${manifestHref.replace(/^\.\//, '')}`);
    check('manifest served', manifestRes.status() === 200, `status ${manifestRes.status()}`);
    const manifest = await manifestRes.json();
    check('manifest parses', !!manifest.name, manifest.name);
    check('manifest is standalone', manifest.display === 'standalone', manifest.display);

    const swRes = await page.request.get(`${base}/sw.js`);
    check('sw.js served as JavaScript',
      (swRes.headers()['content-type'] || '').includes('javascript'),
      swRes.headers()['content-type']);

    for (const icon of manifest.icons) {
      const res = await page.request.get(`${base}/${icon.src.replace(/^\.\//, '')}`);
      check(`icon ${icon.src} resolves`, res.status() === 200, `status ${res.status()}`);
    }

    // ---- 2. wait for the service worker to take control ---------------
    console.log('\n[2] service worker activates and precaches');
    await page.evaluate(() => navigator.serviceWorker.ready);
    const swState = await page.evaluate(async () => {
      const reg = await navigator.serviceWorker.getRegistration();
      return reg && reg.active ? reg.active.state : 'none';
    });
    check('service worker active', swState === 'activated', swState);

    // give the install handler time to finish writing the shell
    await page.waitForTimeout(1200);
    const cacheInfo = await page.evaluate(async () => {
      const keys = await caches.keys();
      const out = {};
      for (const k of keys) {
        const c = await caches.open(k);
        out[k] = (await c.keys()).map((r) => new URL(r.url).pathname).sort();
      }
      return out;
    });
    const cached = Object.values(cacheInfo).flat();
    check('shell precached', cached.includes('/style.css') && cached.includes('/app.js') && cached.includes('/i18n.js'),
      `${cached.length} entries`);

    // ---- 3. give the app some data to lose if the SW were wrong -------
    await page.evaluate(() => {
      localStorage.setItem('__offline_test__', 'hello');
    });

    // ---- 4. cut the network and reload --------------------------------
    console.log('\n[3] offline reload');
    await context.setOffline(true);
    await page.reload({ waitUntil: 'domcontentloaded' });

    const title = await page.title();
    check('page loads offline', !!title, title);

    const hasApp = await page.evaluate(() => {
      const main = document.getElementById('app');
      return !!(main && main.children.length > 0);
    });
    check('app rendered offline', hasApp);

    const cssApplied = await page.evaluate(() => {
      const el = document.querySelector('.topbar') || document.body;
      return getComputedStyle(el).fontFamily || '';
    });
    check('stylesheet applied offline', cssApplied.length > 0, cssApplied.slice(0, 40));

    const dataKept = await page.evaluate(() => localStorage.getItem('__offline_test__'));
    check('localStorage survives offline reload', dataKept === 'hello', String(dataKept));

    const i18nRan = await page.evaluate(() => {
      const h = document.querySelector('[data-i18n]');
      return !!(h && h.textContent && h.textContent.trim().length > 0);
    });
    check('i18n translations applied offline', i18nRan);

    await context.setOffline(false);
  } catch (err) {
    check('test run completed without throwing', false, err.message);
  }

  await browser.close();
  server.close();

  const failed = results.filter((r) => !r.ok);
  console.log(`\n${results.length - failed.length}/${results.length} checks passed`);
  if (pageErrors.length) {
    console.log('page errors:', pageErrors.slice(0, 5));
  }
  process.exit(failed.length ? 1 : 0);
})();
