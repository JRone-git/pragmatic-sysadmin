#!/usr/bin/env node
/* Buddy — translation completeness checker
 *
 * Run:  node scripts/check-buddy-i18n.js
 *
 * Buddy's whole promise is that it works for a parent who does not speak
 * English. That promise is only as good as the translation table, and the
 * table is a 90 KB hand-edited JavaScript object that nothing in the build
 * pipeline validates.
 *
 * It has gone wrong four times now:
 *
 *   1. A missing comma after `people.removeConfirm` — in every language.
 *      The whole file failed to parse, `TRANSLATIONS` was never defined,
 *      and every language silently fell back to English. The app still
 *      "worked", so nothing looked broken. It was broken.
 *
 *   2. When the English block was restructured for v4 (notes, onboarding,
 *      forms) and v5 (photo contacts, medication alarms), the other six
 *      languages were not updated to match. Their keys were still the old
 *      flat style, so every new feature rendered in English for every
 *      language except English.
 *
 *   3. The v4 work APPENDED a second `notes:`, `form:` and `onboarding:`
 *      block to the English object instead of editing the first one.
 *      JavaScript takes the last one, so the original English blocks became
 *      dead code — and the new `form:` block never carried the person and
 *      medicine form labels. English users saw a literal "form.name" and
 *      "form.save" in the Add-a-person dialog.
 *
 *   4. Same trick with `tiles:`. The second English tiles block held only
 *      `notes`, which wiped people/meds/safety/help out of English
 *      entirely. Four of the five home tiles showed "tiles.people.label"
 *      to every English user.
 *
 * `t()` falls back to the raw key string rather than throwing, so none of
 * these produced an error. They produced a UI that looked like it had been
 * written by a machine. That is why the checks below are as blunt as they are.
 *
 * What this checks:
 *
 *   - the file must parse at all
 *   - no duplicate object keys anywhere (this is the bug class above; the
 *     evaluated object hides duplicates, so the raw source has to be scanned)
 *   - English must cover EVERY key the app asks for — English is the
 *     fallback, so a gap there is visible to every user of every language
 *   - every other language must carry exactly English's key set
 *   - no value may be empty or whitespace
 *   - the header comment must state the right number of languages
 *
 * Exit code 0 = clean, 1 = problems found.
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const BUDDY = path.join(ROOT, 'static', 'buddy');

const problems = [];
const notes = [];

function fail(msg) { problems.push(msg); }
function note(msg) { notes.push(msg); }

/* ---- 1. does it even parse? ------------------------------------------ */

const src = fs.readFileSync(path.join(BUDDY, 'i18n.js'), 'utf8');
const ctx = { window: {} };
vm.createContext(ctx);
try {
  vm.runInContext(src, ctx);
} catch (err) {
  console.error(`\n  i18n.js FAILED TO PARSE: ${err.message}`);
  console.error('  Every language is falling back to English. This is the');
  console.error('  worst kind of bug here: nothing looks broken.\n');
  process.exit(1);
}

const T = ctx.window.TRANSLATIONS;
if (!T) {
  console.error('\n  i18n.js parsed but did not define window.TRANSLATIONS\n');
  process.exit(1);
}

/* ---- 2. duplicate keys in the RAW source ------------------------------- */
/* Evaluating the file silently resolves duplicate keys, last-one-wins. The
 * only way to see the bug is to read the source. */

function scanDuplicates(text) {
  const lines = text.split('\n');
  const found = [];
  let lang = null;
  let section = null;
  const seenSections = {};
  const seenKeys = {};

  lines.forEach((ln, i) => {
    let m = /^ {2}([a-z]{2}): \{$/.exec(ln);
    if (m) {
      lang = m[1];
      section = null;
      for (const k of Object.keys(seenSections)) delete seenSections[k];
      for (const k of Object.keys(seenKeys)) delete seenKeys[k];
      return;
    }
    m = /^ {4}([A-Za-z_]\w*): \{$/.exec(ln);
    if (m) {
      section = m[1];
      if (seenSections[section] !== undefined) {
        found.push(`${lang}.${section} — second definition at line ${i + 1} (first at line ${seenSections[section]}). The first one is dead code.`);
      } else {
        seenSections[section] = i + 1;
      }
      for (const k of Object.keys(seenKeys)) delete seenKeys[k];
      return;
    }
    m = /^ {6}([A-Za-z_]\w*):/.exec(ln);
    if (m && section) {
      const key = m[1];
      if (seenKeys[key] !== undefined) {
        found.push(`${lang}.${section}.${key} — defined twice (lines ${seenKeys[key]} and ${i + 1}).`);
      } else {
        seenKeys[key] = i + 1;
      }
    }
  });
  return found;
}

const duplicates = scanDuplicates(src);
for (const d of duplicates) {
  fail(`duplicate key: ${d}`);
}

/* ---- 3. flatten -------------------------------------------------------- */

function flatten(obj, prefix = '') {
  const out = new Map();
  for (const [k, v] of Object.entries(obj || {})) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (Array.isArray(v)) {
      // Step-by-step guides are arrays of strings. Compare them element by
      // element, otherwise a language could keep an English array and still
      // look complete.
      v.forEach((item, i) => out.set(`${key}[${i}]`, item));
    } else if (v && typeof v === 'object') {
      for (const [ik, iv] of flatten(v, key)) out.set(ik, iv);
    } else {
      out.set(key, v);
    }
  }
  return out;
}

/* ---- 4. what does the app actually ask for? ---------------------------- */

const app = fs.readFileSync(path.join(BUDDY, 'app.js'), 'utf8');
const html = fs.readFileSync(path.join(BUDDY, 'index.html'), 'utf8');

const requested = new Set();
let m;

// t('some.key') and t("some.key")
const callRe = /\bt\(\s*['"]([a-zA-Z0-9_.]+)['"]/g;
while ((m = callRe.exec(app)) !== null) requested.add(m[1]);

// Dynamic prefixes: t('notes.cat.' + cat) only names the prefix, so the
// concrete keys have to be expanded from the list the app actually uses.
const DYNAMIC_PREFIXES = {
  'notes.cat.': () => {
    const cm = app.match(/const NOTE_CATEGORIES\s*=\s*\[([^\]]*)\]/);
    if (!cm) return [];
    return cm[1]
      .split(',')
      .map((s) => s.trim().replace(/^['"]|['"]$/g, ''))
      .filter(Boolean)
      .map((c) => `notes.cat.${c}`);
  },
};
for (const key of [...requested]) {
  if (!key.endsWith('.')) continue;
  const expand = DYNAMIC_PREFIXES[key];
  if (!expand) {
    fail(`app.js builds the translation key "${key}" dynamically and the checker cannot tell which keys that means - add it to DYNAMIC_PREFIXES in this script`);
    continue;
  }
  requested.delete(key);
  expand().forEach((k) => requested.add(k));
}

// data-i18n="some.key"
const attrRe = /data-i18n="([a-zA-Z0-9_.]+)"/g;
while ((m = attrRe.exec(html)) !== null) requested.add(m[1]);

// data-i18n-attr="placeholder:some.key"
const attrAttrRe = /data-i18n-attr="[^"]*?([a-zA-Z0-9_.]+)"/g;
while ((m = attrAttrRe.exec(html)) !== null) requested.add(m[1]);

// t(`scamPatterns.${p.label}`) — the labels are a fixed list in app.js
const scamBlock = app.match(/const SCAM_PATTERNS\s*=\s*\[([\s\S]*?)\n\];/);
if (scamBlock) {
  const labelRe = /label:\s*'([^']+)'/g;
  let sm;
  while ((sm = labelRe.exec(scamBlock[1])) !== null) requested.add(`scamPatterns.${sm[1]}`);
}

// read straight off the meta object rather than through t()
for (const k of ['name', 'nativeName', 'code', 'flag', 'dateLocale', 'emergencyNumber']) {
  requested.add(`meta.${k}`);
}

/* ---- 5. compare -------------------------------------------------------- */

const langs = Object.keys(T);
const en = flatten(T.en);

console.log(`\n  languages : ${langs.join(', ')} (${langs.length})`);
console.log(`  en keys   : ${en.size}`);
console.log(`  requested : ${requested.size} distinct keys`);

// English is the fallback for every other language, so a gap here is visible
// to everybody. This is the check that catches "form.name" showing up raw.
const enMissing = [...requested].filter((k) => !en.has(k)).sort();
if (enMissing.length) {
  fail(`English is missing ${enMissing.length} key(s) the app needs — these render as the raw key for every user of every language -> ${enMissing.join(', ')}`);
}

const required = [...requested].filter((k) => en.has(k));
console.log('');

for (const lang of langs) {
  const loc = flatten(T[lang]);
  const missing = required.filter((k) => !loc.has(k));
  const extra = [...loc.keys()].filter((k) => !en.has(k));
  const empty = [...loc.entries()]
    .filter(([, v]) => typeof v === 'string' && !v.trim())
    .map(([k]) => k);

  if (!missing.length && !extra.length && !empty.length) {
    console.log(`  ${lang}: complete (${loc.size} keys)`);
    continue;
  }
  console.log(`  ${lang}: ${missing.length} missing, ${extra.length} extra, ${empty.length} empty`);
  if (missing.length) {
    fail(`${lang}: ${missing.length} key(s) the app needs are missing -> ${missing.join(', ')}`);
  }
  if (extra.length) {
    note(`${lang}: ${extra.length} key(s) English does not have -> ${extra.join(', ')}`);
  }
  if (empty.length) {
    fail(`${lang}: ${empty.length} empty value(s) -> ${empty.join(', ')}`);
  }
}

/* ---- 6. header comment must not lie ------------------------------------ */

const header = src.slice(0, src.indexOf('*/'));
const claimed = header.match(/(\d+)\s+languages?/i);
if (claimed && Number(claimed[1]) !== langs.length) {
  fail(`i18n.js header says "${claimed[1]} languages" but the file defines ${langs.length} (${langs.join(', ')})`);
}

/* ---- 7. every language needs a name ------------------------------------ */

for (const lang of langs) {
  const name = T[lang] && T[lang].meta && T[lang].meta.name;
  if (!name) fail(`${lang}: missing meta.name (shown in the language picker)`);
}

/* ---- report ------------------------------------------------------------ */

if (notes.length) {
  console.log('\n  notes (not failures):');
  for (const n of notes) console.log(`    - ${n}`);
}

if (problems.length) {
  console.log(`\n  ${problems.length} PROBLEM(S):`);
  for (const p of problems) console.log(`    ! ${p}`);
  console.log('');
  process.exit(1);
}

console.log('\n  Buddy translations complete for every language.');
console.log(`  ${langs.length} languages x ${en.size} keys, no duplicates, no gaps.\n`);
