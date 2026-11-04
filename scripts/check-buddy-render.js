#!/usr/bin/env node
/* Buddy — visual check of the translation table in a real browser
 *
 * Run: node scripts/check-buddy-render.js
 *
 * The unit tests prove the translation table is structurally sound. This
 * proves what the user actually sees: that no screen displays a raw key
 * like "tiles.people.label" or "form.save", in any of the seven languages.
 *
 * The language is switched the way a user switches it — through the language
 * picker — and the test then checks that the switch actually took, because
 * an earlier version of this script set a localStorage key the app never
 * reads and so silently checked English seven times.
 *
 * Writes screenshots to /workspace/buddy-shots/ for eyeballing.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');

const ROOT = path.resolve(__dirname, '..', 'static', 'buddy');
const SHOTS = '/workspace/buddy-shots';
const PORT = Number(process.env.BUDDY_RENDER_PORT || 8149);

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
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
      });
      res.end(fs.readFileSync(file));
    });
    server.listen(PORT, () => resolve(server));
  });
}

const LANGS = ['en', 'es', 'fr', 'de', 'pt', 'zh', 'fi'];

// Words that must never appear untranslated in a non-English language. These
// are UI chrome, not brand names or content.
const ENGLISH_UI_WORDS = [
  'step', 'clear', 'save', 'cancel', 'add', 'delete', 'edit', 'copy',
  'loading', 'back', 'next', 'skip', 'done', 'close', 'open', 'search',
  'loading…', 'loading...',
];

const problems = [];
let checks = 0;

/* Find English UI words that were never translated.
 *
 * The translation checker works on keys, so a string that is hardcoded in
 * the HTML or the JS is invisible to it - and that is exactly how "Clear"
 * and "Step 1 of 4" stayed English in every other language.
 */
async function findEnglishWords(page, lang, where) {
  return page.evaluate((words) => {
    const out = [];
    document
      .querySelectorAll('button, label, h1, h2, h3, .pin-key, .onboarding-progress-text, .progress-text, .modal-title')
      .forEach((el) => {
        if (el.offsetParent === null) return; // not rendered right now
        const text = (el.textContent || '').trim();
        const low = text.toLowerCase();
        if (words.includes(low)) out.push(`${el.id || el.className || el.tagName} -> "${text}"`);
      });
    return out;
  }, ENGLISH_UI_WORDS);
}

(async () => {
  fs.mkdirSync(SHOTS, { recursive: true });
  const server = await serve();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 900, height: 1100 } });

  await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#lang-btn', { state: 'visible', timeout: 15000 });
  await page.waitForTimeout(400);

  // get past the onboarding wizard once
  const skip = page.locator('[data-skip]').first();
  if (await skip.count() && await skip.isVisible()) {
    await skip.click();
    await page.waitForTimeout(600);
  }

  for (const lang of LANGS) {
    // The language button lives on the home screen header, so come back to
    // home before switching. The other screens have no header at all.
    await page.evaluate(() => {
      const back = document.querySelector('[data-back]');
      if (back) back.click();
      else show('home');
    });
    await page.waitForTimeout(350);

    // switch the language the way a user does
    await page.waitForSelector('#lang-btn', { state: 'visible', timeout: 15000 });
    await page.click('#lang-btn');
    await page.waitForTimeout(250);
    await page.waitForSelector(`[data-lang="${lang}"]`, { state: 'visible', timeout: 15000 });
    await page.click(`[data-lang="${lang}"]`);
    await page.waitForTimeout(500);

    const current = (await page.textContent('#lang-current')) || '';
    checks++;
    const expected = await page.evaluate(
      (l) => (window.TRANSLATIONS ? window.TRANSLATIONS[l].meta.nativeName : ''),
      lang
    );
    if (current.trim() !== expected.trim()) {
      problems.push(`${lang}: language switch did not take (button says "${current.trim()}", expected "${expected.trim()}")`);
    }

    // 1. nothing on screen may look like a raw translation key
    const raw = await page.evaluate(() => {
      const out = [];
      document.querySelectorAll('[data-i18n]').forEach((el) => {
        const text = (el.textContent || '').trim();
        if (/^[a-zA-Z]+(\.[a-zA-Z0-9_]+)+$/.test(text)) out.push(`${el.dataset.i18n} -> ${text}`);
      });
      return out;
    });
    checks++;
    if (raw.length) problems.push(`${lang} home screen shows raw keys: ${raw.join(', ')}`);

    // 2. the five home tiles must all be readable
    const tiles = await page.$$eval('.tile', (els) =>
      els.map((el) => ({
        label: ((el.querySelector('.label') || {}).textContent || '').trim(),
        sub: ((el.querySelector('.sub') || {}).textContent || '').trim(),
      }))
    );
    checks++;
    if (tiles.length !== 5) problems.push(`${lang}: expected 5 tiles, found ${tiles.length}`);
    tiles.forEach((t) => {
      if (!t.label || /^[a-zA-Z]+(\.[a-zA-Z0-9_]+)+$/.test(t.label)) {
        problems.push(`${lang}: tile label is "${t.label}"`);
      }
    });

    // 3. the check-in line must have a real plural, not a leftover "{s}"
    const checkin = await page.textContent('#checkin-status');
    checks++;
    if (/[{}]/.test(checkin || '')) {
      problems.push(`${lang}: check-in line has an unresolved placeholder -> "${checkin}"`);
    }

    // 4. no untranslated English UI words. A hardcoded "Step 1 of 4" or
    //    "Clear" used to sit in the middle of the Chinese and Finnish UI
    //    with nothing to catch it - the translation checker only looks at
    //    keys, and a hardcoded string is not a key.
    if (lang !== 'en') {
      const stray = await findEnglishWords(page, lang, 'home');
      checks++;
      if (stray.length) {
        problems.push(`${lang}: untranslated English UI word(s) on the home screen: ${stray.join(', ')}`);
      }
    }

    // 5. the onboarding wizard - every step, in this language
    await page.evaluate(() => {
      if (typeof initOnboarding === 'function') initOnboarding();
    });
    await page.waitForTimeout(350);
    for (let step = 1; step <= 4; step++) {
      await page.evaluate((n) => {
        if (typeof setOnboardingStep === 'function') setOnboardingStep(n);
      }, step);
      await page.waitForTimeout(250);
      if (lang !== 'en') {
        const stray = await findEnglishWords(page, lang, `onboarding step ${step}`);
        checks++;
        if (stray.length) {
          problems.push(`${lang}: untranslated English UI word(s) in onboarding step ${step}: ${stray.join(', ')}`);
        }
      }
    }
    await page.evaluate(() => {
      const o = document.querySelector('#onboarding');
      if (o) o.classList.add('hidden');
    });
    await page.waitForTimeout(200);

    // 6. the Notes screen - the PIN pad is built in JS, so it needs a visit
    await page.evaluate(() => {
      const b = document.querySelector('[data-go="notes"]');
      if (b) b.click();
    });
    await page.waitForTimeout(500);
    if (lang !== 'en') {
      const stray = await findEnglishWords(page, lang, 'notes');
      checks++;
      if (stray.length) {
        problems.push(`${lang}: untranslated English UI word(s) on the notes screen: ${stray.join(', ')}`);
      }
    }
    await page.evaluate(() => {
      const b = document.querySelector('[data-go="home"]');
      if (b) b.click();
      else show('home');
    });
    await page.waitForTimeout(300);

    // 7. the Add-a-person form must have real labels
    await page.evaluate(() => {
      const tile = document.querySelector('[data-go="people"]');
      if (tile) tile.click();
    });
    await page.waitForTimeout(450);
    await page.evaluate(() => {
      const btn = [...document.querySelectorAll('button')].find((b) =>
        /add a person|add someone|añadir una persona|hinzufügen|adicionar uma pessoa|添加一个人|lisää henkilö/i.test(b.textContent)
      );
      if (btn) btn.click();
    });
    await page.waitForTimeout(450);
    const formFields = await page.evaluate(() => {
      const modal = document.querySelector('#modal');
      if (!modal) return null;
      return [...modal.querySelectorAll('[data-i18n]')].map((el) => ({
        key: el.dataset.i18n,
        text: (el.textContent || '').trim(),
      }));
    });
    checks++;
    if (!formFields) {
      problems.push(`${lang}: the Add-a-person form did not open`);
    } else {
      formFields.forEach((f) => {
        if (/^[a-zA-Z]+(\.[a-zA-Z0-9_]+)+$/.test(f.text)) {
          problems.push(`${lang}: person form shows raw key ${f.key} -> ${f.text}`);
        }
      });
    }

    await page.screenshot({ path: path.join(SHOTS, `render-${lang}.png`) });
    // close the person form and return home for the next language
    await page.evaluate(() => {
      if (typeof closeModal === 'function') closeModal();
      const modal = document.querySelector('#modal');
      if (modal) modal.classList.remove('show');
      show('home');
    });
    await page.waitForTimeout(350);
  }

  await browser.close();
  server.close();

  console.log(`\n  ${checks} render checks run across ${LANGS.length} languages`);
  if (problems.length) {
    console.log(`\n  ${problems.length} PROBLEM(S):`);
    problems.forEach((p) => console.log(`    ! ${p}`));
    console.log('');
    process.exit(1);
  }
  console.log('  No raw keys on screen in any language.');
  console.log(`  Screenshots: ${SHOTS}\n`);
})();
