/* ========== BUDDY APP ==========
 * i18n-aware, demand-validated, vanilla JS. State persists in localStorage.
 * Requires: i18n.js loaded before this file.
 */

const state = {
  people: [],
  meds: [],
  notes: [],           // [{id, title, content, category, createdAt}]
  notesPin: null,      // hashed PIN for notes (XOR-based for MVP)
  notesUnlocked: false, // session-only, not persisted
  takenToday: {},      // { medId: 'Wed Jun 26 2026' }
  emails: [],          // captured upgrade leads
  lang: null,          // null = auto-detect
  visits: [],          // array of date strings
  feedback: [],        // {date, rating: 'easy'|'hard', text}
  onboardingComplete: false,
  displaySize: 'comfortable'  // 'comfortable' | 'large' | 'extra-large'
};

// ========== i18n ==========
const FALLBACK = 'en';

function getLang() {
  if (state.lang && TRANSLATIONS[state.lang]) return state.lang;
  const nav = (navigator.language || 'en').toLowerCase();
  // Try exact match
  if (TRANSLATIONS[nav]) return nav;
  // Try base language
  const base = nav.split('-')[0];
  if (TRANSLATIONS[base]) return base;
  return FALLBACK;
}

function getNested(obj, path) {
  return path.split('.').reduce((acc, k) => (acc != null ? acc[k] : undefined), obj);
}

function t(key, params = {}) {
  const lang = getLang();
  let str = getNested(TRANSLATIONS[lang], key);
  if (str == null) str = getNested(TRANSLATIONS[FALLBACK], key);
  if (str == null) return key;
  if (typeof str !== 'string') return str; // arrays, objects handled by callers

  // Auto-substitute {number} with locale emergency number (911 US, 112 EU, etc.)
  if (str.includes('{number}')) {
    const num = TRANSLATIONS[lang].meta.emergencyNumber
             || TRANSLATIONS[FALLBACK].meta.emergencyNumber
             || '911';
    str = str.replace(/\{number\}/g, num);
  }

  // Interpolate {key} with params
  return str.replace(/\{(\w+)\}/g, (_, k) => {
    if (params[k] === undefined) return `{${k}}`;
    let v = String(params[k]);
    // Plural support: {s} → 's' or '' based on {n}
    if (k === 's' && params.n !== undefined) {
      v = params.n === 1 ? '' : 's';
    }
    return v;
  });
}

function applyI18n() {
  // Text content
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    const params = el.dataset.i18nParams ? safeParse(el.dataset.i18nParams) : {};
    el.textContent = t(key, params);
  });
  // Attribute interpolation (e.g. placeholder)
  document.querySelectorAll('[data-i18n-attr]').forEach(el => {
    el.dataset.i18nAttr.split(';').forEach(pair => {
      const [attr, key] = pair.split(':');
      if (attr && key) el.setAttribute(attr.trim(), t(key));
    });
  });
  // Document title
  const titleEl = document.querySelector('[data-i18n-meta="title"]');
  if (titleEl) {
    const baseTitle = titleEl.textContent.replace(/^Buddy\s*—\s*/, '');
    document.title = `Buddy — ${t('app.brandLine')}`;
  }
  // HTML lang attribute
  const meta = TRANSLATIONS[getLang()].meta;
  document.documentElement.lang = meta.code;
  // Update language button label
  const lc = document.getElementById('lang-current');
  if (lc) lc.textContent = meta.nativeName;
}

function safeParse(json) {
  try { return JSON.parse(json); } catch(e) { return {}; }
}

// ========== STORAGE ==========
const KEY = 'buddy-state-v2'; // bumped: schema now includes lang/visits/feedback

function load() {
  const saved = localStorage.getItem(KEY);
  if (saved) {
    try {
      const data = JSON.parse(saved);
      Object.assign(state, data);
      // Reset session-only flags
      state.notesUnlocked = false;
    } catch (e) { console.warn('Could not load saved data', e); }
  }
  // First-time demo data (only if no onboarding completed and no people/meds yet)
  if (state.people.length === 0 && state.meds.length === 0 && !state.onboardingComplete) {
    state.people = [
      { id: 'p1', name: 'Sarah (Daughter)', phone: '5551234567', relation: 'Family' },
      { id: 'p2', name: 'Dr. Williams', phone: '5559876543', relation: 'Doctor' }
    ];
    state.meds = [
      { id: 'm1', name: 'Blood pressure pill', time: 'Morning', notes: 'Take with food' },
      { id: 'm2', name: 'Vitamin D', time: 'Morning', notes: '' },
      { id: 'm3', name: 'Cholesterol pill', time: 'Evening', notes: '' }
    ];
    save();
  }
}

function save() {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch (e) { console.warn('Could not save', e); }
}

// ========== HELPERS ==========
function $(sel) { return document.querySelector(sel); }
function $$(sel) { return document.querySelectorAll(sel); }

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

function mdBold(s) {
  // Convert **text** to <strong>text</strong>
  return escapeHtml(s).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
}

function toast(msg) {
  const el = $('#toast');
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2200);
}

function today() { return new Date().toDateString(); }

function phoneFormat(p) {
  const d = String(p || '').replace(/\D/g, '');
  if (d.length === 10) return `(${d.slice(0,3)}) ${d.slice(3,6)}-${d.slice(6)}`;
  if (d.length === 11 && d.startsWith('1')) return `(${d.slice(1,4)}) ${d.slice(4,7)}-${d.slice(7)}`;
  return p;
}

// ========== NAV ==========
function show(name) {
  $$('.screen').forEach(s => s.classList.remove('active'));
  const screen = $(`[data-screen="${name}"]`);
  if (screen) screen.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

document.addEventListener('click', (e) => {
  const goBtn = e.target.closest('[data-go]');
  if (goBtn) { show(goBtn.dataset.go); return; }
  const backBtn = e.target.closest('[data-back]');
  if (backBtn) {
    if ($('[data-screen="topic"].active')) show('help');
    else show('home');
    return;
  }
});

// ========== HOME ==========
function renderHome() {
  const d = new Date();
  const locale = TRANSLATIONS[getLang()].meta.dateLocale;
  const opts = { weekday: 'long', month: 'long', day: 'numeric' };
  $('#today-date').textContent = d.toLocaleDateString(locale, opts);

  const hour = d.getHours();
  const greeting = hour < 12 ? t('time.morning') :
                   hour < 18 ? t('time.afternoon') :
                   t('time.evening');
  $('#greeting').textContent = greeting;

  const td = today();
  const taken = state.meds.filter(m => state.takenToday[m.id] === td).length;
  const total = state.meds.length;
  let status;
  if (total === 0) status = t('checkin.empty');
  else if (taken === 0) status = t('checkin.pending', { n: total });
  else if (taken === total) status = t('checkin.done', { total });
  else status = t('checkin.partial', { taken, total });
  $('#checkin-status').textContent = status;
}

// ========== PEOPLE ==========
function renderPeople() {
  const list = $('#people-list');
  if (state.people.length === 0) {
    list.innerHTML = `<li class="hint" style="padding:1rem 0;">${escapeHtml(t('people.empty'))}</li>`;
    return;
  }
  list.innerHTML = state.people.map(p => `
    <li class="list-item" data-id="${p.id}">
      <div class="avatar">${escapeHtml(p.name.charAt(0).toUpperCase())}</div>
      <div class="body">
        <div class="name">${escapeHtml(p.name)}</div>
        <div class="sub">${escapeHtml(p.relation || phoneFormat(p.phone))}</div>
      </div>
      <a class="action" href="tel:${escapeHtml(p.phone)}">${escapeHtml(t('meds.taken').includes('Taken') ? 'Call' : t('form.save').replace('Guardar','Llamar'))}</a>
      <button class="delete" aria-label="${escapeHtml(t('people.delete'))} ${escapeHtml(p.name)}">×</button>
    </li>
  `).join('');

  // Replace action labels properly with "Call" in the right language
  $$('#people-list .action').forEach(a => {
    a.textContent = callLabel();
  });

  list.querySelectorAll('.delete').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const item = e.target.closest('.list-item');
      const id = item.dataset.id;
      const person = state.people.find(p => p.id === id);
      if (confirm(t('people.removeConfirm', { name: person.name }))) {
        state.people = state.people.filter(p => p.id !== id);
        save();
        renderPeople();
        renderSafetyList();
        renderOnboardingLists();
        toast(t('toast.removed'));
      }
    });
  });
}

function callLabel() {
  // Simple call label per language
  const map = { en: 'Call', es: 'Llamar', fr: 'Appeler', de: 'Anrufen', pt: 'Ligar', zh: '拨打', fi: 'Soita' };
  return map[getLang()] || 'Call';
}

// Update the tel: href on emergency buttons to match the locale's number
function updateEmergencyLinks() {
  const num = TRANSLATIONS[getLang()].meta.emergencyNumber || '911';
  document.querySelectorAll('[data-emergency]').forEach(el => {
    el.setAttribute('href', `tel:${num}`);
  });
}

// ========== MEDS ==========
function renderMeds() {
  const td = today();
  const taken = state.meds.filter(m => state.takenToday[m.id] === td).length;
  const total = state.meds.length;
  const pct = total === 0 ? 0 : (taken / total) * 100;

  $('#meds-progress').innerHTML = `
    <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
    <div class="progress-text">${taken}/${total}</div>
  `;

  const list = $('#meds-list');
  if (state.meds.length === 0) {
    list.innerHTML = `<li class="hint" style="padding:1rem 0;">${escapeHtml(t('meds.empty'))}</li>`;
    return;
  }
  list.innerHTML = state.meds.map(m => {
    const isTaken = state.takenToday[m.id] === td;
    return `
      <li class="list-item med-item ${isTaken ? 'taken' : ''}" data-id="${m.id}">
        <button class="check" aria-label="Mark ${escapeHtml(m.name)} as taken"></button>
        <div class="body">
          <div class="name">${escapeHtml(m.name)}</div>
          <div class="sub">${escapeHtml(m.time)}${m.notes ? ' · ' + escapeHtml(m.notes) : ''}</div>
        </div>
        <button class="delete" aria-label="${escapeHtml(t('people.delete'))} ${escapeHtml(m.name)}">×</button>
      </li>
    `;
  }).join('');

  list.querySelectorAll('.check').forEach(el => {
    el.addEventListener('click', (e) => {
      const id = e.target.closest('.list-item').dataset.id;
      if (state.takenToday[id] === td) {
        delete state.takenToday[id];
      } else {
        state.takenToday[id] = td;
        toast(t('meds.taken'));
      }
      save();
      renderMeds();
      renderHome();
    });
  });

  list.querySelectorAll('.delete').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const id = e.target.closest('.list-item').dataset.id;
      const med = state.meds.find(m => m.id === id);
      if (confirm(t('meds.removeConfirm', { name: med.name }))) {
        state.meds = state.meds.filter(m => m.id !== id);
        delete state.takenToday[id];
        save();
        renderMeds();
        renderHome();
        toast(t('toast.removed'));
      }
    });
  });
}

// ========== SAFETY ==========
function renderSafetyList() {
  const list = $('#safety-list');
  if (state.people.length === 0) {
    list.innerHTML = `<li class="hint" style="padding:0.5rem 0;">${escapeHtml(t('safety.emptyTrusted'))}</li>`;
    return;
  }
  list.innerHTML = state.people.slice(0, 5).map(p => `
    <li class="list-item">
      <div class="avatar">${escapeHtml(p.name.charAt(0).toUpperCase())}</div>
      <div class="body">
        <div class="name">${escapeHtml(p.name)}</div>
        <div class="sub">${escapeHtml(p.relation || t('safety.trustedTitle'))}</div>
      </div>
      <a class="action" href="tel:${escapeHtml(p.phone)}">${callLabel()}</a>
    </li>
  `).join('');
}

// ========== SCAM CHECK ==========
const SCAM_PATTERNS = [
  { re: /\b(act now|act fast|urgent|immediately|right away|don'?t delay|24 hours|as soon as possible)\b/i, label: 'urgency' },
  { re: /\b(wire transfer|gift card|bitcoin|crypto|western union|money order|cash app|venmo|zelle)\b/i, label: 'payment' },
  { re: /\b(IRS|Social Security|Medicare|policeman|sheriff|court|dea|fbi|tax authority)\b/i, label: 'authority' },
  { re: /\b(verify your account|confirm your identity|update (your )?payment|suspend(ed)? account|reactivate)\b/i, label: 'verify' },
  { re: /\b(click here|tap (the )?link|open (this|the) link)\b/i, label: 'link' },
  { re: /\b(congratulations|you'?ve won|selected|winner|claim your prize|free gift|lucky)\b/i, label: 'prize' },
  { re: /\b(password|social security number|credit card number|pin number|bank account|routing number)\b/i, label: 'sensitive' },
  { re: /\b(grandma|grandpa|mom|dad|mother|father).*\b(emergency|accident|hospital|arrest|jail)\b/i, label: 'familyEmergency' },
  { re: /\b(arrested|warrant|jail|lawsuit|legal action|consequences)\b/i, label: 'threat' },
  { re: /\b(amazon|apple|microsoft|netflix|geico|bank).*(refund|charge|unauthorized|suspicious|locked)\b/i, label: 'fakeCompany' }
];

function checkScam(text) {
  const trimmed = (text || '').trim();
  if (trimmed.length < 10) {
    return { level: 'neutral', msg: t('safety.tooShort') };
  }
  const hits = [];
  for (const p of SCAM_PATTERNS) if (p.re.test(trimmed)) hits.push(t(`scamPatterns.${p.label}`));

  if (hits.length === 0) {
    return { level: 'ok', msg: t('safety.clean') };
  }

  const joined = hits.join('; ');
  const n = hits.length;
  return {
    level: 'warn',
    msg: t('safety.risky', { n, s: n, hits: joined })
  };
}

// ========== TOPICS ==========
function renderTopics() {
  const div = $('#topics');
  const topics = getNested(TRANSLATIONS[getLang()], 'topics') || getNested(TRANSLATIONS[FALLBACK], 'topics');
  div.innerHTML = Object.entries(topics).map(([id, t0]) => `
    <button class="topic" data-topic="${id}">
      <span class="icon">${topicEmoji(id)}</span>
      <span>${escapeHtml(t0.title)}</span>
    </button>
  `).join('');

  div.querySelectorAll('.topic').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.topic;
      const topic = getNested(TRANSLATIONS[getLang()], `topics.${id}`) || getNested(TRANSLATIONS[FALLBACK], `topics.${id}`);
      const content = $('#topic-content');
      content.innerHTML = `
        <h2>${topicEmoji(id)} ${escapeHtml(topic.title)}</h2>
        ${topic.steps.map((s, i) => `
          <div class="step">
            <span class="num">${i + 1}</span>
            <span>${escapeHtml(s)}</span>
          </div>
        `).join('')}
        <button class="primary block" data-go="help" style="margin-top:1.25rem;" data-i18n="nav.backToHelp">${escapeHtml(t('nav.backToHelp'))}</button>
      `;
      show('topic');
    });
  });
}

function topicEmoji(id) {
  const map = {
    screenshotIphone: '📸', screenshotAndroid: '📸',
    facetime: '📹', duo: '📹',
    sendphoto: '🖼️', wifi: '📶', update: '🔄',
    password: '🔑', textsize: '🔍', ringtone: '🔔'
  };
  return map[id] || '💡';
}

// ========== MODAL ==========
let modalMode = null;

$('#add-person').addEventListener('click', () => openModal('person'));
$('#add-med').addEventListener('click', () => openModal('med'));
$('#modal-cancel').addEventListener('click', closeModal);
$('#modal-save').addEventListener('click', saveModal);

function openModal(mode) {
  modalMode = mode;
  const title = $('#modal-title');
  const body = $('#modal-body');
  if (mode === 'person') {
    title.textContent = t('people.addTitle');
    body.innerHTML = `
      <label class="modal-label">${escapeHtml(t('form.name'))}</label>
      <input type="text" id="m-name" placeholder="${escapeHtml(t('form.placeholderPersonName'))}" autofocus />
      <label class="modal-label">${escapeHtml(t('form.phone'))}</label>
      <input type="tel" id="m-phone" placeholder="${escapeHtml(t('form.placeholderPhone'))}" />
      <label class="modal-label">${escapeHtml(t('form.relation'))}</label>
      <input type="text" id="m-rel" placeholder="${escapeHtml(t('form.placeholderRelation'))}" />
    `;
  } else {
    title.textContent = t('meds.addTitle');
    body.innerHTML = `
      <label class="modal-label">${escapeHtml(t('form.name'))}</label>
      <input type="text" id="m-name" placeholder="${escapeHtml(t('form.placeholderMedName'))}" autofocus />
      <label class="modal-label">${escapeHtml(t('form.medTime'))}</label>
      <input type="text" id="m-time" placeholder="${escapeHtml(t('form.placeholderMedTime'))}" />
      <label class="modal-label">${escapeHtml(t('form.notes'))}</label>
      <input type="text" id="m-rel" placeholder="${escapeHtml(t('form.placeholderNotes'))}" />
    `;
  }
  $('#modal').classList.add('show');
  setTimeout(() => $('#m-name').focus(), 50);
}

function closeModal() {
  $('#modal').classList.remove('show');
  modalMode = null;
}

function saveModal() {
  const name = $('#m-name').value.trim();
  if (!name) {
    alert(t('form.needName'));
    $('#m-name').focus();
    return;
  }
  if (modalMode === 'person') {
    const phone = $('#m-phone').value.trim().replace(/\D/g, '');
    if (!phone) {
      alert(t('form.needPhone'));
      $('#m-phone').focus();
      return;
    }
    state.people.push({
      id: 'p' + Date.now(),
      name,
      phone,
      relation: $('#m-rel').value.trim()
    });
    save();
    renderPeople();
    renderSafetyList();
    renderOnboardingLists();
    toast(t('toast.added'));
  } else if (modalMode === 'med') {
    state.meds.push({
      id: 'm' + Date.now(),
      name,
      time: $('#m-time').value.trim() || 'Anytime',
      notes: $('#m-rel').value.trim()
    });
    save();
    renderMeds();
    renderHome();
    renderOnboardingLists();
    toast(t('toast.added'));
  } else if (modalMode === 'note') {
    const content = $('#n-content').value.trim();
    const title = $('#n-title').value.trim();
    if (!content) {
      alert(t('form.needContent'));
      $('#n-content').focus();
      return;
    }
    const selectedCat = body.querySelector('.category-option.selected');
    const category = selectedCat ? selectedCat.dataset.cat : 'other';
    if (modalEditing) {
      modalEditing.title = title || content.substring(0, 30);
      modalEditing.content = content;
      modalEditing.category = category;
    } else {
      state.notes.push({
        id: 'n' + Date.now(),
        title: title || content.substring(0, 30),
        content,
        category,
        createdAt: new Date().toISOString()
      });
    }
    save();
    renderNotesList();
    modalEditing = null;
    toast(t('toast.saved'));
  }
  closeModal();
}

// ========== SCAM CHECK HANDLER ==========
$('#check-scam').addEventListener('click', () => {
  const text = $('#scam-input').value;
  const result = checkScam(text);
  const out = $('#scam-result');
  out.className = `result show ${result.level}`;
  out.textContent = result.msg;
});

// ========== UPGRADE MODAL ==========
$('#upgrade-btn').addEventListener('click', () => $('#upgrade-modal').classList.add('show'));
$('#upgrade-cancel').addEventListener('click', () => $('#upgrade-modal').classList.remove('show'));
$('#upgrade-save').addEventListener('click', () => {
  const email = $('#upgrade-email').value.trim();
  if (!email || !email.includes('@') || !email.includes('.')) {
    alert(t('upgrade.badEmail'));
    return;
  }
  state.emails = state.emails || [];
  if (!state.emails.includes(email)) state.emails.push(email);
  save();
  $('#upgrade-email').value = '';
  $('#upgrade-modal').classList.remove('show');
  toast(t('upgrade.saved'));
});

// ========== LANGUAGE MODAL ==========
$('#lang-btn').addEventListener('click', () => {
  const list = $('#lang-list');
  list.innerHTML = Object.values(TRANSLATIONS).map(l => `
    <button class="lang-option ${l.meta.code === getLang() ? 'active' : ''}" data-lang="${l.meta.code}">
      <span class="lang-flag">${l.meta.flag}</span>
      <span class="lang-name">${escapeHtml(l.meta.nativeName)}</span>
      ${l.meta.code === getLang() ? '<span class="lang-check">✓</span>' : ''}
    </button>
  `).join('');
  $('#lang-modal').classList.add('show');

  list.querySelectorAll('.lang-option').forEach(btn => {
    btn.addEventListener('click', () => {
      const code = btn.dataset.lang;
      state.lang = code;
      save();
      applyI18n();
      renderHome();
      renderPeople();
      renderMeds();
      renderTopics();
      renderSafetyList();
      updateEmergencyLinks();
      $('#lang-modal').classList.remove('show');
      toast(langNativeName(code));
    });
  });
});

function langNativeName(code) {
  const m = TRANSLATIONS[code];
  return m ? m.meta.nativeName : code;
}

// ========== DEMAND VALIDATION ==========
function trackVisit() {
  const td = today();
  if (!state.visits.includes(td)) {
    state.visits.push(td);
    // Keep last 365 visits max
    if (state.visits.length > 365) state.visits = state.visits.slice(-365);
    save();
  }
}

function maybeShowFeedback() {
  const uniqueDays = state.visits.length;
  // Show after 2+ unique-day visits, only once per 30 days
  if (uniqueDays < 2) return;
  const last = state.feedback.length ? state.feedback[state.feedback.length - 1].date : null;
  const lastDate = last ? new Date(last) : null;
  const daysSince = lastDate ? (Date.now() - lastDate.getTime()) / 86400000 : 999;
  if (daysSince < 30) return;

  $('#feedback-modal').classList.add('show');
}

$('#fb-easy').addEventListener('click', () => {
  state.feedback.push({ date: new Date().toISOString(), rating: 'easy', text: '' });
  save();
  $('#feedback-modal').classList.remove('show');
  toast(t('feedback.easyThanks'));
});

$('#fb-hard').addEventListener('click', () => {
  $('#feedback-detail').style.display = 'block';
});

$('#fb-skip').addEventListener('click', () => {
  $('#feedback-modal').classList.remove('show');
});

$('#fb-send').addEventListener('click', () => {
  const text = $('#feedback-text').value.trim();
  state.feedback.push({ date: new Date().toISOString(), rating: 'hard', text });
  save();
  $('#feedback-text').value = '';
  $('#feedback-detail').style.display = 'none';
  $('#feedback-modal').classList.remove('show');
  toast(t('feedback.sent'));
});

// Close modals on backdrop click
['#modal', '#upgrade-modal', '#lang-modal', '#feedback-modal'].forEach(sel => {
  const el = $(sel);
  if (el) {
    el.addEventListener('click', (e) => {
      if (e.target === el && sel !== '#feedback-modal') el.classList.remove('show');
    });
  }
});

// ========== DISPLAY SIZE ==========
function applyDisplaySize(size) {
  const root = document.documentElement;
  const sizes = { comfortable: 17, large: 19, 'extra-large': 22 };
  root.style.setProperty('--base-font-size', (sizes[size] || 17) + 'px');
  document.body.classList.remove('size-comfortable', 'size-large', 'size-extra-large');
  document.body.classList.add('size-' + (size || 'comfortable'));
  state.displaySize = size || 'comfortable';
}

// ========== ONBOARDING WIZARD ==========
let onboardingStep = 1;
let onboardingChosenSize = null;

function initOnboarding() {
  if (!state.onboardingComplete) {
    // Show wizard on first load
    setTimeout(() => showOnboarding(), 600);
  }
  // Wire up wizard controls
  $$('.onboarding [data-next]').forEach(btn => btn.addEventListener('click', onboardingNext));
  $$('.onboarding [data-prev]').forEach(btn => btn.addEventListener('click', onboardingPrev));
  $$('.onboarding [data-skip]').forEach(btn => btn.addEventListener('click', onboardingSkip));
  $$('.onboarding [data-finish]').forEach(btn => btn.addEventListener('click', onboardingFinish));
  // Add buttons inside wizard reuse existing modal flow
  const addPersonBtn = $('#onboarding-add-person');
  if (addPersonBtn) addPersonBtn.addEventListener('click', () => openModal('person'));
  const addMedBtn = $('#onboarding-add-med');
  if (addMedBtn) addMedBtn.addEventListener('click', () => openModal('med'));
  // Size selection
  $$('.size-option').forEach(opt => {
    opt.addEventListener('click', () => {
      $$('.size-option').forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
      onboardingChosenSize = opt.dataset.size;
    });
  });
  // Re-open button on help screen
  const reopenBtn = $('#reopen-onboarding');
  if (reopenBtn) reopenBtn.addEventListener('click', () => {
    onboardingChosenSize = state.displaySize;
    showOnboarding();
  });
}

function showOnboarding() {
  $('#onboarding').classList.remove('hidden');
  setOnboardingStep(1);
  renderOnboardingLists();
  // Highlight current size if re-opening
  if (onboardingChosenSize) {
    const opt = $(`.size-option[data-size="${onboardingChosenSize}"]`);
    if (opt) opt.classList.add('selected');
  }
}

function hideOnboarding() {
  $('#onboarding').classList.add('hidden');
}

function setOnboardingStep(n) {
  onboardingStep = n;
  $$('.onboarding-step').forEach(s => {
    if (parseInt(s.dataset.step, 10) === n) s.classList.remove('hidden');
    else s.classList.add('hidden');
  });
  const total = 4;
  const pct = (n / total) * 100;
  const fill = $('#onboarding-fill');
  if (fill) fill.style.width = pct + '%';
  const txt = $('#onboarding-progress-text');
  if (txt) txt.textContent = `Step ${n} of ${total}`;
  // Re-render lists for steps 2 & 3
  if (n === 2 || n === 3) renderOnboardingLists();
}

function onboardingNext() {
  if (onboardingStep < 4) setOnboardingStep(onboardingStep + 1);
}
function onboardingPrev() {
  if (onboardingStep > 1) setOnboardingStep(onboardingStep - 1);
}
function onboardingSkip() {
  state.onboardingComplete = true;
  save();
  hideOnboarding();
  toast(t('onboarding.toastSkip'));
}
function onboardingFinish() {
  const size = onboardingChosenSize || state.displaySize || 'comfortable';
  applyDisplaySize(size);
  state.displaySize = size;
  state.onboardingComplete = true;
  save();
  hideOnboarding();
  toast(t('onboarding.toastDone'));
}

function renderOnboardingLists() {
  // People list
  const peopleList = $('#onboarding-people');
  if (peopleList) {
    if (state.people.length === 0) {
      peopleList.innerHTML = `<li class="empty">${escapeHtml(t('onboarding.people.empty'))}</li>`;
    } else {
      peopleList.innerHTML = state.people.map(p => `
        <li>
          <span><strong>${escapeHtml(p.name)}</strong>${p.relation ? ' <small>(' + escapeHtml(p.relation) + ')</small>' : ''}</span>
        </li>
      `).join('');
    }
  }
  // Meds list
  const medsList = $('#onboarding-meds');
  if (medsList) {
    if (state.meds.length === 0) {
      medsList.innerHTML = `<li class="empty">${escapeHtml(t('onboarding.meds.empty'))}</li>`;
    } else {
      medsList.innerHTML = state.meds.map(m => `
        <li>
          <span><strong>${escapeHtml(m.name)}</strong> <small>— ${escapeHtml(m.time || 'Anytime')}</small></span>
        </li>
      `).join('');
    }
  }
}

// ========== NOTES (PIN-PROTECTED) ==========
const NOTE_CATEGORIES = ['password', 'phone', 'address', 'other'];
let notePinEntry = '';

function initNotes() {
  // Re-render notes when navigating to the screen
  const notesScreen = $('[data-screen="notes"]');
  if (notesScreen) {
    const observer = new MutationObserver(() => {
      if (notesScreen.classList.contains('active')) showNotesScreen();
    });
    observer.observe(notesScreen, { attributes: true, attributeFilter: ['class'] });
  }
  // Lock button
  const lockBtn = $('#notes-lock');
  if (lockBtn) lockBtn.addEventListener('click', lockNotes);
  // Add note
  const addNoteBtn = $('#add-note');
  if (addNoteBtn) addNoteBtn.addEventListener('click', () => openNoteModal());
}

function showNotesScreen() {
  const setup = $('#notes-pin-setup');
  const entry = $('#notes-pin-entry');
  const unlocked = $('#notes-unlocked');

  // Hide all
  setup.classList.add('hidden');
  entry.classList.add('hidden');
  unlocked.classList.add('hidden');

  if (!state.notesPin) {
    // First time — set up PIN
    setup.classList.remove('hidden');
    buildPinPad('setup');
  } else if (!state.notesUnlocked) {
    // Returning — enter PIN
    entry.classList.remove('hidden');
    buildPinPad('entry');
    notePinEntry = '';
    renderPinDots('entry', notePinEntry);
    $('#notes-pin-error').classList.add('hidden');
  } else {
    // Unlocked — show notes
    unlocked.classList.remove('hidden');
    renderNotesList();
  }
}

// Simple PIN hashing (XOR with static key — not crypto-secure, fine for MVP demo)
const PIN_KEY = 'buddy-pin-2026';
function hashPin(pin) {
  let result = '';
  for (let i = 0; i < pin.length; i++) {
    result += String.fromCharCode(pin.charCodeAt(i) ^ PIN_KEY.charCodeAt(i % PIN_KEY.length));
  }
  return btoa(result);
}
function verifyPin(pin) {
  return state.notesPin && hashPin(pin) === state.notesPin;
}

function buildPinPad(mode) {
  const container = $(`#notes-pin-pad-${mode}`);
  if (!container) return;
  const keys = ['1','2','3','4','5','6','7','8','9','clear','0','del'];
  container.innerHTML = keys.map(k => {
    if (k === 'clear') return `<button class="pin-key action" data-action="clear" type="button">Clear</button>`;
    if (k === 'del') return `<button class="pin-key action" data-action="del" type="button">⌫</button>`;
    return `<button class="pin-key" data-digit="${k}" type="button">${k}</button>`;
  }).join('');
  container.onclick = (e) => {
    const digit = e.target.dataset.digit;
    const action = e.target.dataset.action;
    if (digit !== undefined) pinKeyPress(digit, mode);
    else if (action === 'del') pinKeyPress('del', mode);
    else if (action === 'clear') pinKeyPress('clear', mode);
  };
}

let setupPin = '';
let setupPinConfirm = '';
let setupStage = 'first'; // 'first' | 'confirm'

function pinKeyPress(key, mode) {
  if (mode === 'setup') {
    if (key === 'del') { setupPin = setupPin.slice(0, -1); renderPinDots('setup', setupPin); return; }
    if (key === 'clear') { setupPin = ''; renderPinDots('setup', setupPin); return; }
    if (setupPin.length < 4) {
      setupPin += key;
      renderPinDots('setup', setupPin);
      if (setupPin.length === 4) {
        if (setupStage === 'first') {
          // Move to confirm
          setTimeout(() => {
            setupStage = 'confirm';
            setupPinConfirm = '';
            // Update label
            const lbl = $('#notes-pin-setup h3');
            if (lbl) lbl.textContent = t('notes.pinConfirmTitle');
            const body = $('#notes-pin-setup p');
            if (body) body.textContent = t('notes.pinConfirmBody');
            renderPinDots('setup', '');
          }, 300);
        } else {
          // Verify match
          if (setupPin === setupPinConfirm) {
            state.notesPin = hashPin(setupPin);
            save();
            state.notesUnlocked = true;
            toast(t('notes.pinSaved'));
            showNotesScreen();
            // Reset
            setupPin = '';
            setupPinConfirm = '';
            setupStage = 'first';
          } else {
            toast(t('notes.pinMismatch'));
            setupPin = '';
            setupPinConfirm = '';
            setupStage = 'first';
            // Reset labels
            const lbl = $('#notes-pin-setup h3');
            if (lbl) lbl.textContent = t('notes.pinSetTitle');
            const body = $('#notes-pin-setup p');
            if (body) body.textContent = t('notes.pinSetBody');
            renderPinDots('setup', '');
          }
        }
      }
    }
  } else if (mode === 'entry') {
    if (key === 'del') { notePinEntry = notePinEntry.slice(0, -1); renderPinDots('entry', notePinEntry); return; }
    if (key === 'clear') { notePinEntry = ''; renderPinDots('entry', notePinEntry); return; }
    if (notePinEntry.length < 4) {
      notePinEntry += key;
      renderPinDots('entry', notePinEntry);
      if (notePinEntry.length === 4) {
        if (verifyPin(notePinEntry)) {
          state.notesUnlocked = true;
          notePinEntry = '';
          $('#notes-pin-error').classList.add('hidden');
          showNotesScreen();
        } else {
          $('#notes-pin-error').classList.remove('hidden');
          notePinEntry = '';
          setTimeout(() => renderPinDots('entry', ''), 300);
        }
      }
    }
  }
}

function renderPinDots(mode, value) {
  const container = $(`#notes-pin-display-${mode}`);
  if (!container) return;
  container.innerHTML = '';
  for (let i = 0; i < 4; i++) {
    const dot = document.createElement('div');
    dot.className = 'pin-dot' + (i < value.length ? ' filled' : '');
    container.appendChild(dot);
  }
}

function lockNotes() {
  state.notesUnlocked = false;
  notePinEntry = '';
  showNotesScreen();
}

function renderNotesList() {
  const list = $('#notes-list');
  if (!list) return;
  if (!state.notes || state.notes.length === 0) {
    list.innerHTML = `
      <li class="notes-empty">
        <div class="big-icon">📝</div>
        <div>${escapeHtml(t('notes.empty'))}</div>
      </li>
    `;
    return;
  }
  list.innerHTML = state.notes.map(n => {
    const cat = NOTE_CATEGORIES.includes(n.category) ? n.category : 'other';
    return `
      <li class="list-item note-item" data-id="${n.id}">
        <div>
          <strong>${escapeHtml(n.title)}</strong>
          <span class="note-category-tag note-category-${cat}">${escapeHtml(t('notes.cat.' + cat))}</span>
          <div class="note-content">${escapeHtml(n.content)}</div>
          <div class="note-actions">
            <button class="copy" data-action="copy" data-id="${n.id}">📋 ${escapeHtml(t('notes.copy'))}</button>
            <button data-action="edit" data-id="${n.id}">✏️ ${escapeHtml(t('notes.edit'))}</button>
            <button class="delete" data-action="delete" data-id="${n.id}">🗑️ ${escapeHtml(t('notes.delete'))}</button>
          </div>
        </div>
      </li>
    `;
  }).join('');
  // Wire up note action buttons
  list.querySelectorAll('button[data-action]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const action = btn.dataset.action;
      const id = btn.dataset.id;
      const note = state.notes.find(n => n.id === id);
      if (!note) return;
      if (action === 'copy') {
        try {
          navigator.clipboard.writeText(note.content).then(() => {
            toast(t('notes.copied'));
          }).catch(() => {
            // Fallback
            const ta = document.createElement('textarea');
            ta.value = note.content;
            document.body.appendChild(ta);
            ta.select();
            try { document.execCommand('copy'); toast(t('notes.copied')); }
            catch (e) { toast(t('notes.copyFailed')); }
            document.body.removeChild(ta);
          });
        } catch (e) { toast(t('notes.copyFailed')); }
      } else if (action === 'edit') {
        openNoteModal(note);
      } else if (action === 'delete') {
        if (confirm(t('notes.confirmDelete'))) {
          state.notes = state.notes.filter(n => n.id !== id);
          save();
          renderNotesList();
          toast(t('notes.deleted'));
        }
      }
    });
  });
}

function openNoteModal(existing) {
  const title = $('#modal-title');
  const body = $('#modal-body');
  const isEdit = !!existing;
  title.textContent = isEdit ? t('notes.editTitle') : t('notes.addTitle');
  const currentCat = existing ? existing.category : 'other';
  body.innerHTML = `
    <label class="modal-label">${escapeHtml(t('form.title'))}</label>
    <input type="text" id="n-title" placeholder="${escapeHtml(t('form.placeholderNoteTitle'))}" value="${existing ? escapeHtml(existing.title) : ''}" autofocus />
    <label class="modal-label">${escapeHtml(t('form.content'))}</label>
    <textarea id="n-content" rows="3" placeholder="${escapeHtml(t('form.placeholderNoteContent'))}" style="width:100%;padding:.6rem;border:1.5px solid var(--border);border-radius:8px;font-family:inherit;font-size:1rem;">${existing ? escapeHtml(existing.content) : ''}</textarea>
    <label class="modal-label">${escapeHtml(t('form.category'))}</label>
    <div class="category-selector" id="n-category">
      ${NOTE_CATEGORIES.map(c => `
        <button type="button" class="category-option ${c === currentCat ? 'selected' : ''}" data-cat="${c}">
          ${escapeHtml(t('notes.cat.' + c))}
        </button>
      `).join('')}
    </div>
  `;
  // Wire category selection
  body.querySelectorAll('.category-option').forEach(btn => {
    btn.addEventListener('click', () => {
      body.querySelectorAll('.category-option').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
    });
  });
  // Override save behavior for note mode
  modalMode = 'note';
  modalEditing = existing || null;
  $('#modal').classList.add('show');
  setTimeout(() => $('#n-title').focus(), 50);
}

let modalEditing = null;

// ========== INIT ==========
load();
applyI18n();
applyDisplaySize(state.displaySize || 'comfortable');
renderHome();
renderPeople();
renderMeds();
renderTopics();
renderSafetyList();
updateEmergencyLinks();
trackVisit();
initOnboarding();
initNotes();

// Re-render check-in status periodically
setInterval(renderHome, 60 * 1000);

// Show feedback prompt after a beat (so first visit isn't interrupted)
setTimeout(maybeShowFeedback, 5000);