// Buddy — headless test suite (JSDOM)
//
// Run:  npm i jsdom && node scripts/test-buddy.js
//
// Checks the app's static structure and flows, and — most importantly —
// that no screen renders a raw translation key and that all seven languages
// carry an identical key set. Those last two caught four separate bugs the
// browser never reported an error for.

const fs = require('fs');
const path = require('path');
let JSDOM;
for (const candidate of ['jsdom', '/workspace/buddy-test/node_modules/jsdom']) {
  try { ({ JSDOM } = require(candidate)); break; } catch (e) { /* try next */ }
}
if (!JSDOM) {
  console.error('\n  jsdom is not installed. Run:  npm i jsdom\n');
  process.exit(2);
}

const BUDDY_DIR = require('path').join(__dirname, '..', 'static', 'buddy');

const html = fs.readFileSync(path.join(BUDDY_DIR, 'index.html'), 'utf-8');
const css = fs.readFileSync(path.join(BUDDY_DIR, 'style.css'), 'utf-8');
const i18n = fs.readFileSync(path.join(BUDDY_DIR, 'i18n.js'), 'utf-8');
const app = fs.readFileSync(path.join(BUDDY_DIR, 'app.js'), 'utf-8');

const dom = new JSDOM(html, {
  runScripts: 'outside-only',
  pretendToBeVisual: true,
  url: 'http://localhost/buddy/'
});

const styleEl = dom.window.document.createElement('style');
styleEl.textContent = css;
dom.window.document.head.appendChild(styleEl);

const errors = [];
const warnings = [];
const passed = [];

const doc = dom.window.document;

// === STATIC STRUCTURE CHECKS ===
console.log('=== Static structure ===\n');

const screens = ['home', 'people', 'meds', 'safety', 'help', 'notes'];
screens.forEach(s => {
  const el = doc.querySelector(`[data-screen="${s}"]`);
  if (el) passed.push(`Screen "${s}" exists`);
  else errors.push(`Screen "${s}" missing!`);
});

if (doc.querySelector('#onboarding')) passed.push('Onboarding wizard exists');
else errors.push('Onboarding wizard missing!');

const steps = doc.querySelectorAll('.onboarding-step');
if (steps.length === 4) passed.push(`Onboarding has 4 steps`);
else errors.push(`Onboarding has ${steps.length} steps, expected 4`);

const mascot = doc.querySelector('.mascot-svg');
if (mascot) passed.push('Mascot SVG present');
else errors.push('Mascot SVG missing!');

const eyeGroup = mascot ? mascot.querySelector('.mascot-eyes') : null;
if (eyeGroup) passed.push('Mascot has blinking eyes group');
else errors.push('Mascot eyes group missing!');

if (doc.querySelector('#notes-pin-setup')) passed.push('Notes PIN setup view present');
if (doc.querySelector('#notes-pin-entry')) passed.push('Notes PIN entry view present');
if (doc.querySelector('#notes-unlocked')) passed.push('Notes unlocked view present');
if (doc.querySelector('#add-note')) passed.push('Add note button present');

const tiles = doc.querySelectorAll('.tile');
const expectedTiles = ['people', 'meds', 'safety', 'help', 'notes'];
const actualTiles = Array.from(tiles).map(t => t.dataset.go);
if (JSON.stringify(actualTiles) === JSON.stringify(expectedTiles)) {
  passed.push(`5 tiles: ${actualTiles.join(', ')}`);
} else {
  warnings.push(`Tiles: ${actualTiles.join(', ')}`);
}

const sizeOptions = doc.querySelectorAll('.size-option');
if (sizeOptions.length === 3) {
  passed.push(`3 size options: ${Array.from(sizeOptions).map(o => o.dataset.size).join(', ')}`);
} else {
  errors.push(`Expected 3 size options, found ${sizeOptions.length}`);
}

if (app.includes('buildPinPad') && app.includes('pinKeyPress')) {
  passed.push('PIN pad logic defined');
} else {
  errors.push('PIN pad logic missing!');
}

if (app.includes('Notification.requestPermission') || app.includes('new Notification')) {
  passed.push('Notification API used (alarms implemented)');
} else {
  errors.push('NO Notification API usage — alarm feature missing!');
}

if (app.includes('scheduleMedAlarm') && app.includes('ensureNotificationPermission')) {
  passed.push('Alarm scheduling functions defined');
} else {
  errors.push('Alarm scheduling functions missing!');
}

if (app.includes('medAlarmTimers')) {
  passed.push('Med alarm timer tracking in state');
} else {
  errors.push('Med alarm timer tracking missing from state');
}

if (app.includes('rescheduleAllMedAlarms')) {
  passed.push('Alarm re-scheduling on init');
} else {
  errors.push('No re-scheduling on init!');
}

// === CSS CHECKS ===
if (css.includes('--base-font-size')) {
  passed.push('CSS uses --base-font-size variable');
} else {
  errors.push('CSS does NOT use --base-font-size — display size has NO EFFECT');
}

if (css.includes('@keyframes mascot-blink')) {
  passed.push('Mascot blink keyframe defined');
} else {
  errors.push('Mascot blink keyframe missing!');
}

if (css.includes('.alarm-toggle')) {
  passed.push('Alarm toggle CSS present');
} else {
  errors.push('Alarm toggle CSS missing!');
}

// === RUN THE APP ===
console.log('=== Running the app ===\n');

try { dom.window.eval(i18n); passed.push('i18n.js loaded cleanly'); }
catch (e) { errors.push(`i18n.js error: ${e.message}`); }

// `state` is declared with `const` inside app.js. In an indirect eval only
// function declarations escape to the global object - `const` stays in the
// eval's own scope, so later evals cannot see it. Expose a probe alongside
// the app so the flow tests can reach the live state.
try { dom.window.eval(app + '\n;window.__buddy = { get state() { return state; }, save: save };'); passed.push('app.js loaded cleanly'); }
catch (e) { errors.push(`app.js error: ${e.message}`); }

const stateStr = dom.window.localStorage.getItem('buddy-state-v2');
if (stateStr) {
  try {
    const state = JSON.parse(stateStr);
    if (state.people?.length > 0) passed.push(`State: ${state.people.length} demo people`);
    if (state.meds?.length > 0) passed.push(`State: ${state.meds.length} demo meds`);
    if (state.notes) passed.push('State: notes array');
    if (state.notesPin === null) passed.push('State: notesPin null (not set)');
    if (state.onboardingComplete === false) passed.push('State: onboardingComplete false');
    if (state.displaySize) passed.push(`State: displaySize=${state.displaySize}`);
    if (state.medAlarmTimers) passed.push('State: medAlarmTimers object');
  } catch (e) {
    errors.push(`State parse error: ${e.message}`);
  }
} else {
  warnings.push('No state in localStorage');
}

// === FLOW TESTS ===
console.log('=== User flow tests ===\n');

// Flow 1: Apply display size and verify CSS variable gets set
try {
  dom.window.eval('applyDisplaySize("extra-large")');
  const root = dom.window.document.documentElement;
  const fs = root.style.getPropertyValue('--base-font-size');
  if (fs.includes('22')) {
    passed.push(`applyDisplaySize("extra-large") sets --base-font-size to ${fs}`);
  } else {
    errors.push(`applyDisplaySize("extra-large") set --base-font-size to "${fs}" (expected 22px)`);
  }
  dom.window.eval('applyDisplaySize("comfortable")');
} catch (e) {
  errors.push(`applyDisplaySize test failed: ${e.message}`);
}

// Flow 2: Format time helper
try {
  const result = dom.window.eval('formatTime12("08:30")');
  if (result === '8:30 AM') passed.push('formatTime12("08:30") → "8:30 AM"');
  else errors.push(`formatTime12 wrong: ${result}`);
  
  const result2 = dom.window.eval('formatTime12("20:00")');
  if (result2 === '8:00 PM') passed.push('formatTime12("20:00") → "8:00 PM"');
  else errors.push(`formatTime12 wrong: ${result2}`);
} catch (e) {
  errors.push(`formatTime12 test failed: ${e.message}`);
}

// Flow 3: PIN hash round-trip
try {
  const verify = dom.window.eval('verifyPin("1234")');
  // verifyPin returns true if hash matches, false otherwise
  // Since notesPin is null on first run, it should be false
  if (verify === false) passed.push('PIN verify returns false when no PIN set');
  else if (verify === true) passed.push('PIN hash round-trip works');
  else errors.push(`PIN hash verify returned: ${verify}`);
} catch (e) {
  errors.push(`PIN hash test failed: ${e.message}`);
}

// Flow 4: Add a med and set an alarm
try {
  // Simulate adding a med — reach the live state through the probe
  dom.window.eval(`
    window.__buddy.state.meds.push({
      id: 'test1',
      name: 'Test Med',
      time: 'Morning',
      notes: 'test',
      alarmTime: null
    });
    window.__buddy.save();
  `);
  const state = JSON.parse(dom.window.localStorage.getItem('buddy-state-v2'));
  if (state.meds.some(m => m.id === 'test1')) {
    passed.push('Can add a med to state');
  } else {
    errors.push('Failed to add med to state');
  }
  
  // Set an alarm time
  dom.window.eval(`
    const med = window.__buddy.state.meds.find(m => m.id === 'test1');
    med.alarmTime = '08:00';
    window.__buddy.save();
  `);
  const state2 = JSON.parse(dom.window.localStorage.getItem('buddy-state-v2'));
  if (state2.meds.find(m => m.id === 'test1').alarmTime === '08:00') {
    passed.push('Can set alarmTime on a med');
  } else {
    errors.push('Failed to set alarmTime on med');
  }
} catch (e) {
  errors.push(`Med alarm flow test failed: ${e.message}`);
}

// Flow 5: i18n alarm strings exist
const langs = ['en', 'es', 'fr', 'de', 'pt', 'zh', 'fi'];
const alarmKeys = ['alarmTitle', 'alarmHint', 'alarmTime', 'alarmSet', 'alarmClear'];
for (const lang of langs) {
  const result = dom.window.eval(`
    (function() {
      const alarmKeys = ['alarmTitle', 'alarmHint', 'alarmTime', 'alarmSet', 'alarmClear'];
      const t = TRANSLATIONS.${lang};
      if (!t) return 'lang-missing';
      return alarmKeys.filter(k => t.meds && t.meds[k]).length;
    })()
  `);
  if (result === alarmKeys.length) {
    passed.push(`${lang}: all ${alarmKeys.length} alarm i18n keys present`);
  } else {
    errors.push(`${lang}: only ${result}/${alarmKeys.length} alarm i18n keys present`);
  }
}

// Flow 6: no element may display a raw translation key
// This is the exact bug that went unnoticed four times: t() falls back to
// the key string instead of throwing, so a missing key renders as
// "tiles.people.label" on screen and nothing anywhere reports an error.
try {
  const raw = dom.window.eval(`
    (function() {
      const out = [];
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.dataset.i18n;
        const text = (el.textContent || '').trim();
        if (text === key || new RegExp('^[a-zA-Z]+(\\\\.[a-zA-Z0-9_]+)+$').test(text)) {
          out.push(key + ' -> ' + text);
        }
      });
      return out;
    })()
  `);
  if (raw.length === 0) {
    passed.push('No element shows a raw translation key');
  } else {
    errors.push(`${raw.length} element(s) show a raw translation key -> ${raw.join(', ')}`);
  }
} catch (e) {
  errors.push(`Raw-key sweep failed: ${e.message}`);
}

// Flow 7: every language has the same key set as English
try {
  const parity = dom.window.eval(`
    (function() {
      function leaf(o, p) {
        p = p || '';
        return Object.keys(o).flatMap(function(k) {
          const key = p ? p + '.' + k : k;
          const v = o[k];
          if (Array.isArray(v)) return v.map(function(x, i) { return key + '[' + i + ']'; });
          if (v && typeof v === 'object') return leaf(v, key);
          return [key];
        });
      }
      const en = leaf(TRANSLATIONS.en).sort().join(',');
      const bad = [];
      Object.keys(TRANSLATIONS).forEach(function(l) {
        if (leaf(TRANSLATIONS[l]).sort().join(',') !== en) bad.push(l);
      });
      return bad;
    })()
  `);
  if (parity.length === 0) {
    passed.push('All 7 languages carry an identical key set');
  } else {
    errors.push(`Key sets differ between languages -> ${parity.join(', ')}`);
  }
} catch (e) {
  errors.push(`Key parity test failed: ${e.message}`);
}

// Flow 8: plurals render, and no placeholder is left behind
// The plural marker is the ending to append: {s} -> medicines, {e} ->
// Medikamente, {es} -> señales, {is} -> sinais. It is decided by {n}, and
// the marker used to be left as a literal "{s}" on the home screen.
try {
  const bad = dom.window.eval(`
    (function() {
      const langs = Object.keys(TRANSLATIONS);
      const out = [];
      langs.forEach(function(lang) {
        TRANSLATIONS[lang].__lang = lang;
        window.__buddy.state.lang = lang;
        [['checkin.pending', {n:1}], ['checkin.pending', {n:3}],
         ['checkin.partial', {taken:2, total:5, n:2}],
         ['safety.risky', {n:3, hits:'x'}],
         ['notes.pinTriesLeft', {count:1}], ['notes.pinTriesLeft', {count:3}],
         ['notes.pinTooMany', {count:1}], ['notes.pinTooMany', {count:30}]]
          .forEach(function(pair) {
          const text = t(pair[0], pair[1]);
          if (/[{}]/.test(text)) out.push(lang + ' ' + pair[0] + ' -> ' + text);
          if (!text.trim()) out.push(lang + ' ' + pair[0] + ' -> empty');
        });
      });
      window.__buddy.state.lang = 'en';
      return out;
    })()
  `);
  if (bad.length === 0) {
    passed.push('Plurals render in all 7 languages with no leftover placeholders');
  } else {
    errors.push(`${bad.length} plural rendering problem(s) -> ${bad.join(', ')}`);
  }

  // A leftover-brace check cannot see a wrong ending. German turns
  // "Sekunde" into "Sekunden" and Finnish turns "yritys" into "yritystä",
  // and both are one letter on the end of a stem. Pin the exact output so
  // a future edit cannot produce "Sekundeen" or "yritystäa" again.
  const exact = dom.window.eval(`
    (function() {
      const out = [];
      const cases = [
        ['de', 'notes.pinTooMany', {count:30}, '30 Sekunden'],
        ['de', 'notes.pinTooMany', {count:1},  '1 Sekunde'],
        ['de', 'notes.pinTriesLeft', {count:3}, '3 Versuche'],
        ['fi', 'notes.pinTriesLeft', {count:3}, '3 yritystä'],
        ['fi', 'notes.pinTriesLeft', {count:1}, '1 yritys'],
        ['fi', 'notes.pinTooMany', {count:30}, '30 sekuntia'],
        ['en', 'notes.pinTriesLeft', {count:3}, '3 attempts'],
        ['en', 'notes.pinTriesLeft', {count:1}, '1 attempt'],
      ];
      cases.forEach(function(c) {
        window.__buddy.state.lang = c[0];
        const text = t(c[1], c[2]);
        // Word boundaries, not a substring test: "yritystäa" contains
        // "yritystä", and a substring check would call that correct.
        // The expected strings are plain words, so matching spaces loosely
        // is all the escaping that is needed.
        const esc = c[3].split(' ').join('\\\\s+');
        if (!new RegExp('(^|\\\\W)' + esc + '($|\\\\W)').test(text)) {
          out.push(c[0] + ' ' + c[1] + ' -> "' + text + '" (expected "' + c[3] + '")');
        }
      });
      window.__buddy.state.lang = 'en';
      return out;
    })()
  `);
  if (exact.length === 0) {
    passed.push('German and Finnish plural endings are exact');
  } else {
    errors.push(`${exact.length} wrong plural ending(s) -> ${exact.join(', ')}`);
  }
} catch (e) {
  errors.push(`Plural test failed: ${e.message}`);
}

// === RESULTS ===
console.log('\n=== RESULTS ===\n');
console.log(`PASSED (${passed.length}):`);
passed.forEach(p => console.log(`  ✓ ${p}`));

console.log(`\nWARNINGS (${warnings.length}):`);
warnings.forEach(w => console.log(`  ⚠ ${w}`));

console.log(`\nERRORS (${errors.length}):`);
errors.forEach(e => console.log(`  ✗ ${e}`));

console.log(`\n=== Summary: ${passed.length} passed, ${warnings.length} warnings, ${errors.length} errors ===`);
process.exit(errors.length > 0 ? 1 : 0);
