#!/usr/bin/env node
/* Buddy — Notes flow test (Playwright)
 *
 * Run:
 *   npm i -g playwright && npx playwright install chromium
 *   node scripts/test-buddy-notes.js
 *
 * The Notes feature had never worked, and nothing reported it. Three
 * separate bugs stacked up:
 *
 *   1. There was no generic `.hidden` rule in style.css - only
 *      `.onboarding.hidden`, `.onboarding-step.hidden`, `.pin-error.hidden`
 *      and `.photo-clear.hidden`. The three notes panels (PIN setup, PIN
 *      entry, notes list) carry a bare class="hidden", so all three
 *      rendered stacked on top of each other at the same time.
 *
 *   2. saveModal() read $('#m-name').value before looking at modalMode.
 *      The note form has #n-title and #n-content, not #m-name, so saving
 *      a note threw "Cannot read properties of null" every time.
 *
 *   3. The PIN could never be set. The confirm stage appended to setupPin
 *      instead of setupPinConfirm, so setupPinConfirm stayed empty, the
 *      comparison could never match, and the length guard blocked the
 *      second entry. The notes list was unreachable.
 *
 * Every one of them was invisible to the unit tests, which check structure
 * and translations rather than what a person can actually do. This drives
 * the real thing.
 *
 * Needs Playwright and nothing else.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');

const ROOT = path.resolve(__dirname, '..', 'static', 'buddy');
const PORT = Number(process.env.BUDDY_NOTES_PORT || 8157);

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.png': 'image/png',
  '.webmanifest': 'application/manifest+json',
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

const problems = [];
let passed = 0;

function ok(condition, message) {
  if (condition) {
    passed++;
    console.log(`  PASS  ${message}`);
  } else {
    problems.push(message);
    console.log(`  FAIL  ${message}`);
  }
}

(async () => {
  const server = await serve();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 900, height: 1100 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(`PAGEERROR: ${e.message}`));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(`CONSOLE: ${m.text()}`); });
  // One handler for every confirm() in the app.
  page.on('dialog', (d) => d.accept());

  const type = async (pad, digits) => {
    for (const d of digits) {
      await page.evaluate(([p, key]) => {
        const b = [...document.querySelectorAll(`#notes-pin-pad-${p} button`)]
          .find((x) => x.textContent.trim() === key);
        if (b) b.click();
      }, [pad, d]);
      await page.waitForTimeout(110);
    }
  };

  const visibleViews = () => page.evaluate(() =>
    ['setup', 'entry', 'unlocked']
      .filter((s) => {
        const e = document.querySelector(`#notes-pin-${s}`);
        return e && !e.classList.contains('hidden');
      })
      .join(',')
  );

  await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(800);
  const skip = page.locator('[data-skip]').first();
  if (await skip.count() && await skip.isVisible()) {
    await skip.click();
    await page.waitForTimeout(500);
  }

  console.log('\n  PIN setup');
  await page.evaluate(() => document.querySelector('[data-go="notes"]').click());
  await page.waitForTimeout(500);
  ok(await page.isVisible('#notes-pin-setup'), 'PIN setup view shown on first visit');
  ok((await visibleViews()) === 'setup', 'only one notes panel is visible at a time');

  await type('setup', ['1', '2', '3', '4']);
  await page.waitForTimeout(600);
  ok((await visibleViews()) === 'setup', 'still only the setup panel after 4 digits');
  const prompt = (await page.textContent('#notes-pin-setup h3')).trim();
  ok(/again/i.test(prompt), `setup switches to the confirm prompt (got "${prompt}")`);

  // a mismatched second entry must bounce back to the first stage
  await type('setup', ['9', '9', '9', '9']);
  await page.waitForTimeout(700);
  ok((await visibleViews()) === 'setup', 'a mismatched PIN keeps the setup panel up');
  const backToStart = (await page.textContent('#notes-pin-setup h3')).trim();
  ok(!/again/i.test(backToStart), `mismatch resets the prompt (got "${backToStart}")`);

  // now a matching pair
  await type('setup', ['1', '2', '3', '4']);
  await page.waitForTimeout(600);
  await type('setup', ['1', '2', '3', '4']);
  await page.waitForTimeout(700);
  ok(await page.isVisible('#notes-unlocked'), 'matching PIN unlocks the notes');
  ok(!(await page.isVisible('#notes-pin-setup')), 'PIN setup panel hidden afterwards');

  console.log('\n  Adding a note');
  await page.click('#add-note');
  await page.waitForTimeout(400);
  ok(await page.isVisible('#modal'), 'the note form opens');
  await page.fill('#n-title', 'Wifi password');
  await page.fill('#n-content', 'hunter2');
  await page.evaluate(() =>
    document.querySelector('#n-category .category-option[data-cat="password"]').click()
  );
  await page.click('#modal-save');
  await page.waitForTimeout(700);
  ok(!(await page.isVisible('#modal')), 'the form closes after saving');
  const list = await page.textContent('#notes-list');
  ok(/Wifi password/.test(list), 'the note appears in the list');
  ok(/Password/.test(list), 'the category label is rendered');

  console.log('\n  Editing a note');
  await page.evaluate(() => document.querySelector('#notes-list button[data-action="edit"]').click());
  await page.waitForTimeout(400);
  ok(await page.isVisible('#modal'), 'the edit form opens');
  ok((await page.inputValue('#n-title')) === 'Wifi password', 'the edit form prefills the title');
  await page.fill('#n-title', 'Wifi password (main router)');
  await page.click('#modal-save');
  await page.waitForTimeout(600);
  ok(/main router/.test(await page.textContent('#notes-list')), 'the edit is saved');

  console.log('\n  Lock and unlock');
  await page.click('#notes-lock');
  await page.waitForTimeout(500);
  ok(await page.isVisible('#notes-pin-entry'), 'locking shows the PIN entry panel');
  ok(!(await page.isVisible('#notes-unlocked')), 'the notes are hidden while locked');
  await type('entry', ['9', '9', '9', '9']);
  await page.waitForTimeout(500);
  ok(
    await page.evaluate(() => {
      const e = document.querySelector('#notes-pin-error');
      return !!e && !e.classList.contains('hidden');
    }),
    'a wrong PIN shows an error'
  );
  ok(!(await page.isVisible('#notes-unlocked')), 'still locked after a wrong PIN');
  await type('entry', ['1', '2', '3', '4']);
  await page.waitForTimeout(600);
  ok(await page.isVisible('#notes-unlocked'), 'the right PIN unlocks the notes');
  ok(/Wifi password/.test(await page.textContent('#notes-list')), 'the notes are still there');

  console.log('\n  The PIN is never persisted as unlocked');
  ok(
    await page.evaluate(() => {
      const raw = localStorage.getItem('buddy-state-v2');
      if (!raw) return true;
      return !('notesUnlocked' in JSON.parse(raw));
    }),
    'notesUnlocked is not written to localStorage'
  );

  console.log('\n  Keyboard entry');
  await page.click('#notes-lock');
  await page.waitForTimeout(500);
  await page.keyboard.type('1234', { delay: 90 });
  await page.waitForTimeout(700);
  ok(await page.isVisible('#notes-unlocked'), 'typing on a physical keyboard unlocks the notes');

  console.log('\n  Changing the PIN');
  await page.click('#notes-change-pin');
  await page.waitForTimeout(500);
  ok(await page.isVisible('#notes-pin-setup'), 'the change-PIN flow shows the setup panel');
  ok(
    /new PIN/i.test(await page.textContent('#notes-pin-setup h3')),
    'the setup panel asks for a new PIN'
  );
  await type('setup', ['5', '6', '7', '8']);
  await page.waitForTimeout(600);
  await type('setup', ['5', '6', '7', '8']);
  await page.waitForTimeout(800);
  ok(await page.isVisible('#notes-unlocked'), 'the new PIN unlocks the notes');
  await page.click('#notes-lock');
  await page.waitForTimeout(500);
  await type('entry', ['1', '2', '3', '4']);
  await page.waitForTimeout(600);
  ok(!(await page.isVisible('#notes-unlocked')), 'the old PIN no longer works');
  await type('entry', ['5', '6', '7', '8']);
  await page.waitForTimeout(600);
  ok(await page.isVisible('#notes-unlocked'), 'the new PIN works');

  console.log('\n  Wrong PINs are counted');
  // A note to lose when the PIN is reset.
  await page.click('#add-note');
  await page.waitForTimeout(400);
  await page.fill('#n-title', 'Router admin password');
  await page.fill('#n-content', 'letmein');
  await page.click('#modal-save');
  await page.waitForTimeout(700);
  await page.click('#notes-lock');
  await page.waitForTimeout(500);
  for (let i = 0; i < 2; i++) {
    await type('entry', ['9', '9', '9', '9']);
    await page.waitForTimeout(500);
  }
  const errText = await page.textContent('#notes-pin-error');
  ok(/2|left/i.test(errText), `the error says how many tries are left (got "${errText.trim()}")`);

  console.log('\n  Too many wrong tries');
  // Two were already used above, so three more reaches the limit of five.
  for (let i = 0; i < 3; i++) {
    await type('entry', ['9', '9', '9', '9']);
    await page.waitForTimeout(450);
  }
  const lockedMsg = await page.textContent('#notes-pin-error').catch(() => '');
  ok(/wait/i.test(lockedMsg), `too many tries causes a pause (got "${lockedMsg.trim()}")`);
  await type('entry', ['1', '2', '3', '4']);
  await page.waitForTimeout(500);
  ok(!(await page.isVisible('#notes-unlocked')), 'the keypad does nothing during the pause');

  console.log('\n  Deleting a note');
  await page.evaluate(() => document.querySelector('#notes-list button[data-action="delete"]').click());
  await page.waitForTimeout(700);
  ok(!/Wifi password/.test(await page.textContent('#notes-list')), 'the note is deleted');

  console.log('\n  Forgetting the PIN');
  const before = await page.evaluate(() => {
    const s = JSON.parse(localStorage.getItem('buddy-state-v2') || '{}');
    return { meds: (s.meds || []).length, people: (s.people || []).length, notes: (s.notes || []).length };
  });
  ok(before.notes > 0, 'there is a note to lose');
  await page.click('#notes-pin-forgot');
  await page.waitForTimeout(800);
  ok(await page.isVisible('#notes-pin-setup'), 'forgetting the PIN returns to the setup panel');
  const after = await page.evaluate(() => {
    const s = JSON.parse(localStorage.getItem('buddy-state-v2') || '{}');
    return { meds: (s.meds || []).length, people: (s.people || []).length, notes: (s.notes || []).length, pin: s.notesPin };
  });
  ok(!after.pin, 'the PIN is cleared');
  ok(after.notes === 0, 'the notes are deleted - they cannot be recovered without the PIN');
  ok(after.meds === before.meds, 'the medicines are kept');
  ok(after.people === before.people, 'the contacts are kept');
  ok(
    !/Router admin password/.test(await page.textContent('#notes-list')),
    'the old notes are gone from the page too'
  );

  console.log('\n  The other forms still work');
  await page.evaluate(() => document.querySelector('[data-go="people"]').click());
  await page.waitForTimeout(500);
  await page.evaluate(() => {
    const b = [...document.querySelectorAll('[data-screen="people"] button')].find((x) =>
      /add a person/i.test(x.textContent)
    );
    if (b) b.click();
  });
  await page.waitForTimeout(500);
  await page.fill('#m-name', 'Test Person');
  await page.fill('#m-phone', '5551234567');
  await page.click('#modal-save');
  await page.waitForTimeout(700);
  ok(
    !(await page.isVisible('#modal')),
    'the person form saves (saveModal still reads #m-name for people)'
  );
  ok(/Test Person/.test(await page.textContent('[data-screen="people"]')), 'the person is listed');

  console.log('\n  No errors');
  ok(errors.length === 0, `no page errors (${errors.length})`);
  if (errors.length) errors.forEach((e) => console.log(`        ${e}`));

  await browser.close();
  server.close();

  console.log(`\n  ${passed} passed, ${problems.length} problem(s)\n`);
  if (problems.length) {
    problems.forEach((p) => console.log(`    ! ${p}`));
    console.log('');
    process.exit(1);
  }
})();
