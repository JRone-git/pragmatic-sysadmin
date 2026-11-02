#!/usr/bin/env node
/**
 * Backfill Buddy's translation table so all seven languages match English.
 *
 * Why this exists
 * ---------------
 * Buddy v4 (PIN-protected notes, setup wizard, note form) and v5 (photo
 * contacts, medication alarms) were only ever written in English. The other
 * six languages kept their pre-v4 tables, so every new screen fell back to
 * English. `t()` degrades instead of throwing, so nothing crashed — it just
 * quietly lied.
 *
 * English itself was not clean either. The v4 commit appended a second
 * `notes:`, `form:` and `onboarding:` block to the English object instead of
 * editing the first one. JavaScript takes the last one, so the *original*
 * English blocks became dead code — and the new ones never carried the
 * person/medicine form labels. English users saw literal `form.name` and
 * `form.save` in the "Add a person" dialog.
 *
 * What this does
 * --------------
 *   notes       -> replaced wholesale with the canonical key set
 *   onboarding  -> replaced wholesale with the canonical key set
 *   form        -> MERGED: the old person/medicine labels (already translated
 *                  in every language) plus the new note-form labels
 *   people      -> missing photo keys added, existing ones left alone
 *   meds        -> missing alarm keys added, existing ones left alone
 *
 * Duplicate English blocks are collapsed into one.
 *
 * Usage: node scripts/apply-buddy-i18n.js [--check]
 *   --check   report what would change, write nothing
 */

'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const I18N = path.join(ROOT, 'static', 'buddy', 'i18n.js');
const DATA = path.join(__dirname, 'buddy-i18n-translations.json');

const DRY = process.argv.includes('--check');

// --- canonical key order (matches the English source) ----------------------

const NOTES_ORDER = [
  'title', 'hint',
  'pinSetTitle', 'pinSetBody', 'pinConfirmTitle', 'pinConfirmBody',
  'pinEnterTitle', 'pinEnterBody',
  'pinWarning', 'pinError', 'pinMismatch', 'pinSaved',
  'empty', 'addCta', 'addTitle', 'editTitle',
  'lock', 'copy', 'edit', 'delete',
  'copied', 'copyFailed', 'deleted', 'confirmDelete',
];

const ONBOARDING_ORDER = [
  ['welcome', ['title', 'body', 'steps', 'cta']],
  ['people', ['title', 'body', 'addCta', 'empty']],
  ['meds', ['title', 'body', 'addCta', 'empty']],
  ['size', ['title', 'body', 'comfortable', 'large', 'extraLarge']],
  // flat keys — one entry each. Grouping them into a single array would make
  // the destructuring below swallow six of them.
  ['back', null],
  ['next', null],
  ['skip', null],
  ['finish', null],
  ['reopen', null],
  ['toastSkip', null],
  ['toastDone', null],
];

const FORM_ORDER = [
  // person + medicine form labels (pre-v4, already translated everywhere)
  'name', 'phone', 'relation', 'medTime', 'notes',
  // note form labels (v4, backfilled by this script)
  'title', 'content', 'category',
  // placeholders
  'placeholderPersonName', 'placeholderPhone', 'placeholderRelation',
  'placeholderMedName', 'placeholderMedTime', 'placeholderNotes',
  'placeholderEmail',
  'placeholderNoteTitle', 'placeholderNoteContent',
  // buttons + validation
  'cancel', 'save', 'needName', 'needPhone', 'needContent',
];

// --- helpers ---------------------------------------------------------------

function blockEnd(lines, start) {
  let depth = 0;
  let inStr = false;
  let quote = '';
  let esc = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) {
      if (inStr) {
        if (esc) { esc = false; continue; }
        if (ch === '\\') { esc = true; continue; }
        if (ch === quote) inStr = false;
        continue;
      }
      if (ch === '"' || ch === "'") { inStr = true; quote = ch; continue; }
      if (ch === '{') depth++;
      else if (ch === '}') {
        depth--;
        if (depth === 0) return i;
      }
    }
  }
  throw new Error(`unterminated block starting at line ${start + 1}`);
}

function findBlocks(lines, rstart, rend, section) {
  const hits = [];
  for (let i = rstart; i < rend; i++) {
    if (lines[i] === `    ${section}: {`) hits.push(i);
  }
  return hits;
}

function evalBlock(lines, start, end) {
  const raw = lines.slice(start, end + 1).join('\n');
  const objText = raw.slice(raw.indexOf('{')).replace(/,\s*$/, '');
  return vm.runInNewContext(`(${objText})`);
}

function mergeBlocks(lines, hits) {
  const merged = {};
  for (const h of hits) {
    const end = blockEnd(lines, h);
    Object.assign(merged, evalBlock(lines, h, end));
  }
  return merged;
}

const q = (v) => JSON.stringify(String(v));

function renderFlat(section, values, order) {
  const out = [`    ${section}: {`];
  for (const key of order) {
    if (!(key in values)) {
      throw new Error(`missing ${section}.${key}`);
    }
    out.push(`      ${key}: ${q(values[key])},`);
  }
  out.push('    },');
  return out;
}

function renderNotes(values) {
  const out = ['    notes: {'];
  for (const key of NOTES_ORDER) {
    if (!(key in values)) throw new Error(`missing notes.${key}`);
    out.push(`      ${key}: ${q(values[key])},`);
  }
  out.push('      cat: {');
  for (const sub of ['password', 'phone', 'address', 'other']) {
    if (!values.cat || !(sub in values.cat)) throw new Error(`missing notes.cat.${sub}`);
    out.push(`        ${sub}: ${q(values.cat[sub])},`);
  }
  out.push('      },');
  out.push('    },');
  return out;
}

function renderOnboarding(values) {
  const out = ['    onboarding: {'];
  for (const [key, subkeys] of ONBOARDING_ORDER) {
    if (subkeys) {
      if (!(key in values)) throw new Error(`missing onboarding.${key}`);
      out.push(`      ${key}: {`);
      for (const sub of subkeys) {
        if (!(sub in values[key])) throw new Error(`missing onboarding.${key}.${sub}`);
        out.push(`        ${sub}: ${q(values[key][sub])},`);
      }
      out.push('      },');
    } else {
      if (!(key in values)) throw new Error(`missing onboarding.${key}`);
      out.push(`      ${key}: ${q(values[key])},`);
    }
  }
  out.push('    },');
  return out;
}

function renderMerged(section, values) {
  const out = [`    ${section}: {`];
  for (const [key, value] of Object.entries(values)) {
    out.push(`      ${key}: ${q(value)},`);
  }
  out.push('    },');
  return out;
}

function renderTiles(tiles) {
  const out = ['    tiles: {'];
  // match the file's existing look: values aligned on the colon
  const pad = { people: 'people:', meds: 'meds: ', notes: 'notes:', safety: 'safety:', help: 'help: ' };
  for (const tile of ['people', 'meds', 'notes', 'safety', 'help']) {
    const t = tiles[tile];
    out.push(`      ${pad[tile]} { label: ${q(t.label)}, sub: ${q(t.sub)} },`);
  }
  out.push('    },');
  return out;
}

// --- main ------------------------------------------------------------------

const T = JSON.parse(fs.readFileSync(DATA, 'utf8'));
delete T._comment;

const original = fs.readFileSync(I18N, 'utf8');
let lines = original.split('\n');

// language regions
const langStarts = [];
lines.forEach((ln, i) => {
  const m = /^ {2}([a-z]{2}): \{$/.exec(ln);
  if (m) langStarts.push({ i, code: m[1] });
});
const regions = {};
langStarts.forEach((entry, idx) => {
  const end = idx + 1 < langStarts.length ? langStarts[idx + 1].i : lines.length;
  regions[entry.code] = [entry.i, end];
});

const langs = Object.keys(T);
for (const code of langs) {
  if (!regions[code]) throw new Error(`language ${code} has no block in i18n.js`);
}

const edits = [];
const report = [];

for (const code of langs) {
  const [rstart, rend] = regions[code];
  const trans = T[code];

  // --- notes: replace wholesale -----------------------------------------
  const noteHits = findBlocks(lines, rstart, rend, 'notes');
  if (!noteHits.length) throw new Error(`${code}: no notes block`);
  for (const h of noteHits.slice(0, -1)) {
    edits.push([h, blockEnd(lines, h) + 1, []]);
  }
  const noteLast = noteHits[noteHits.length - 1];
  edits.push([noteLast, blockEnd(lines, noteLast) + 1, renderNotes(trans.notes)]);
  report.push(`${code}: notes -> ${NOTES_ORDER.length + 4} keys`);

  // --- onboarding: replace wholesale ------------------------------------
  const onbHits = findBlocks(lines, rstart, rend, 'onboarding');
  if (!onbHits.length) throw new Error(`${code}: no onboarding block`);
  for (const h of onbHits.slice(0, -1)) {
    edits.push([h, blockEnd(lines, h) + 1, []]);
  }
  const onbLast = onbHits[onbHits.length - 1];
  edits.push([onbLast, blockEnd(lines, onbLast) + 1, renderOnboarding(trans.onboarding)]);
  report.push(`${code}: onboarding -> 24 keys`);

  // --- form: MERGE old + new --------------------------------------------
  const formHits = findBlocks(lines, rstart, rend, 'form');
  if (!formHits.length) throw new Error(`${code}: no form block`);
  const formExisting = mergeBlocks(lines, formHits);
  const formValues = {};
  for (const key of FORM_ORDER) {
    if (key in trans.form) {
      formValues[key] = trans.form[key];
    } else if (key in formExisting) {
      formValues[key] = formExisting[key];
    } else {
      throw new Error(`${code}: no value for form.${key}`);
    }
  }
  for (const h of formHits.slice(0, -1)) {
    edits.push([h, blockEnd(lines, h) + 1, []]);
  }
  const formLast = formHits[formHits.length - 1];
  edits.push([formLast, blockEnd(lines, formLast) + 1, renderFlat('form', formValues, FORM_ORDER)]);
  report.push(`${code}: form -> ${FORM_ORDER.length} keys (was ${Object.keys(formExisting).length})`);

  // --- tiles: MERGE, same story as form ---------------------------------
  // The v4 commit appended a second `tiles:` block to English containing only
  // `notes`. Last-one-wins then wiped people/meds/safety/help out of English
  // entirely, so four of the five home tiles showed raw key names.
  const tileHits = findBlocks(lines, rstart, rend, 'tiles');
  if (!tileHits.length) throw new Error(`${code}: no tiles block`);
  const tileExisting = mergeBlocks(lines, tileHits);
  const tileValues = {};
  for (const tile of ['people', 'meds', 'notes', 'safety', 'help']) {
    const base = tileExisting[tile] || {};
    const over = (trans.tiles && trans.tiles[tile]) || {};
    tileValues[tile] = { label: over.label || base.label, sub: over.sub || base.sub };
    if (!tileValues[tile].label) throw new Error(`${code}: tiles.${tile}.label missing`);
  }
  for (const h of tileHits.slice(0, -1)) {
    edits.push([h, blockEnd(lines, h) + 1, []]);
  }
  const tileLast = tileHits[tileHits.length - 1];
  edits.push([tileLast, blockEnd(lines, tileLast) + 1, renderTiles(tileValues)]);
  report.push(`${code}: tiles -> 5 tiles (was ${Object.keys(tileExisting).length})`);

  // --- toast: add missing keys ------------------------------------------
  const toastHits = findBlocks(lines, rstart, rend, 'toast');
  const toastExisting = mergeBlocks(lines, toastHits);
  const toastValues = Object.assign({}, toastExisting);
  const addedToast = [];
  for (const [key, value] of Object.entries(trans.toast || {})) {
    if (!(key in toastValues)) {
      toastValues[key] = value;
      addedToast.push(key);
    }
  }
  if (addedToast.length) {
    const last = toastHits[toastHits.length - 1];
    edits.push([last, blockEnd(lines, last) + 1, renderMerged('toast', toastValues)]);
    report.push(`${code}: toast + ${addedToast.join(', ')}`);
  }

  // --- people: add missing photo keys -----------------------------------
  const pplHits = findBlocks(lines, rstart, rend, 'people');
  const pplExisting = mergeBlocks(lines, pplHits);
  const pplValues = Object.assign({}, pplExisting);
  const addedPpl = [];
  for (const [key, value] of Object.entries(trans.people)) {
    if (!(key in pplValues)) {
      pplValues[key] = value;
      addedPpl.push(key);
    }
  }
  if (addedPpl.length) {
    const last = pplHits[pplHits.length - 1];
    edits.push([last, blockEnd(lines, last) + 1, renderMerged('people', pplValues)]);
    report.push(`${code}: people + ${addedPpl.join(', ')}`);
  }

  // --- meds: add missing alarm keys --------------------------------------
  const medHits = findBlocks(lines, rstart, rend, 'meds');
  const medExisting = mergeBlocks(lines, medHits);
  const medValues = Object.assign({}, medExisting);
  const addedMed = [];
  for (const [key, value] of Object.entries(trans.meds)) {
    if (!(key in medValues)) {
      medValues[key] = value;
      addedMed.push(key);
    }
  }
  if (addedMed.length) {
    const last = medHits[medHits.length - 1];
    edits.push([last, blockEnd(lines, last) + 1, renderMerged('meds', medValues)]);
    report.push(`${code}: meds + ${addedMed.length} alarm key(s)`);
  }
}

// apply bottom-up
edits.sort((a, b) => b[0] - a[0]);
for (const [start, end, repl] of edits) {
  lines.splice(start, end - start, ...repl);
}

// header comment
const headerOld = ` * 6 languages: English, Spanish, French, German, Portuguese (BR), Chinese (Simplified)`;
const headerNew = ` * 7 languages: English, Spanish, French, German, Portuguese (BR), Chinese (Simplified), Finnish\n * English is the reference: every language must carry exactly the same keys.\n * Verify with: node scripts/check-buddy-i18n.js`;
let out = lines.join('\n');
if (out.includes(headerOld)) {
  out = out.replace(headerOld, headerNew);
} else if (!out.includes(headerNew)) {
  console.warn('! header comment not in the expected shape - check it by hand');
}

if (DRY) {
  console.log('DRY RUN - nothing written. Changes:');
  report.forEach((r) => console.log('  ' + r));
  console.log(`\n${edits.length} block edits`);
  process.exit(0);
}

fs.writeFileSync(I18N, out, 'utf8');
console.log('applied:');
report.forEach((r) => console.log('  ' + r));
console.log(`\n${edits.length} block edits written to ${path.relative(ROOT, I18N)}`);
