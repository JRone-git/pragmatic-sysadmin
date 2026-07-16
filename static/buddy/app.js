/* ========== BUDDY APP ==========
 * i18n-aware, demand-validated, vanilla JS. State persists in localStorage.
 * Requires: i18n.js loaded before this file.
 * v4: Notes, medicine alarm toggles, onboarding flow
 */

const state = {
  people: [],
  meds: [],
  takenToday: {},      // { medId: 'Wed Jun 26 2026' }
  notes: [],           // { id, text, alarm: bool, alarmTime: 'HH:MM'|'', created: ISO }
  emails: [],          // captured upgrade leads
  lang: null,          // null = auto-detect
  visits: [],          // array of date strings
  feedback: [],        // {date, rating: 'easy'|'hard', text}
  onboarded: false     // true = skip onboarding
};

// ========== i18n ==========
const FALLBACK = 'en';

function getLang() {
  if (state.lang && TRANSLATIONS[state.lang]) return state.lang;
  const nav = (navigator.language || 'en').toLowerCase();
  if (TRANSLATIONS[nav]) return nav;
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
  if (typeof str !== 'string') return str;

  if (str.includes('{number}')) {
    const num = TRANSLATIONS[lang].meta.emergencyNumber
             || TRANSLATIONS[FALLBACK].meta.emergencyNumber
             || '911';
    str = str.replace(/\{number\}/g, num);
  }

  return str.replace(/\{(\w+)\}/g, (_, k) => {
    if (params[k] === undefined) return `{${k}}`;
    let v = String(params[k]);
    if (k === 's' && params.n !== undefined) {
      v = params.n === 1 ? '' : 's';
    }
    return v;
  });
}

function applyI18n() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    const params = el.dataset.i18nParams ? safeParse(el.dataset.i18nParams) : {};
    el.textContent = t(key, params);
  });
  document.querySelectorAll('[data-i18n-attr]').forEach(el => {
    el.dataset.i18nAttr.split(';').forEach(pair => {
      const [attr, key] = pair.split(':');
      if (attr && key) el.setAttribute(attr.trim(), t(key));
    });
  });
  document.title = `Buddy — ${t('app.brandLine')}`;
  const meta = TRANSLATIONS[getLang()].meta;
  document.documentElement.lang = meta.code;
  const lc = document.getElementById('lang-current');
  if (lc) lc.textContent = meta.nativeName;
}

function safeParse(json) {
  try { return JSON.parse(json); } catch(e) { return {}; }
}

// ========== STORAGE ==========
const KEY = 'buddy-state-v3'; // v3: adds notes, onboarded, med alarms

function load() {
  const saved = localStorage.getItem(KEY);
  if (saved) {
    try {
      const data = JSON.parse(saved);
      Object.assign(state, data);
      // Migrate v2 → v3: ensure notes/onboarded exist
      if (!Array.isArray(state.notes)) state.notes = [];
      if (state.meds) state.meds.forEach(m => { if (m.alarm === undefined) m.alarm = false; });
    } catch (e) { console.warn('Could not load saved data', e); }
  }
  // First-time setup (only if no state at all)
  if (state.people.length === 0 && state.meds.length === 0 && !state.onboarded) {
    state.people = [
      { id: 'p1', name: 'Sarah (Daughter)', phone: '5551234567', relation: 'Family' },
      { id: 'p2', name: 'Dr. Williams', phone: '5559876543', relation: 'Doctor' }
    ];
    state.meds = [
      { id: 'm1', name: 'Blood pressure pill', time: 'Morning', notes: 'Take with food', alarm: true },
      { id: 'm2', name: 'Vitamin D', time: 'Morning', notes: '', alarm: false },
      { id: 'm3', name: 'Cholesterol pill', time: 'Evening', notes: '', alarm: true }
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

function timeToMinutes(timeStr) {
  // Parse "08:30" → 510, "Morning" → 480, "Evening" → 1140, etc.
  if (!timeStr) return -1;
  const m = timeStr.match(/^(\d{1,2}):(\d{2})$/);
  if (m) return parseInt(m[1]) * 60 + parseInt(m[2]);
  const lower = timeStr.toLowerCase();
  if (lower.includes('morning') || lower.includes('aamu')) return 480;
  if (lower.includes('noon') || lower.includes('keskipäivä')) return 720;
  if (lower.includes('afternoon') || lower.includes('iltapäivä')) return 840;
  if (lower.includes('evening') || lower.includes('ilta')) return 1080;
  if (lower.includes('night') || lower.includes('yö') || lower.includes('bedtime') || lower.includes('nukkumaan')) return 1320;
  return -1;
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
      <a class="action" href="tel:${escapeHtml(p.phone)}">${escapeHtml(callLabel())}</a>
      <button class="delete" aria-label="${escapeHtml(t('people.delete'))} ${escapeHtml(p.name)}">×</button>
    </li>
  `).join('');

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
        toast(t('toast.removed'));
      }
    });
  });
}

function callLabel() {
  const map = { en: 'Call', es: 'Llamar', fr: 'Appeler', de: 'Anrufen', pt: 'Ligar', zh: '拨打', fi: 'Soita' };
  return map[getLang()] || 'Call';
}

function updateEmergencyLinks() {
  const num = TRANSLATIONS[getLang()].meta.emergencyNumber || '911';
  document.querySelectorAll('[data-emergency]').forEach(el => {
    el.setAttribute('href', `tel:${num}`);
  });
}

// ========== MEDS (with alarm toggles) ==========
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
    const alarmOn = m.alarm;
    return `
      <li class="list-item med-item ${isTaken ? 'taken' : ''}" data-id="${m.id}">
        <button class="check" aria-label="Mark ${escapeHtml(m.name)} as taken"></button>
        <div class="body">
          <div class="name">${escapeHtml(m.name)}</div>
          <div class="sub">${escapeHtml(m.time)}${m.notes ? ' · ' + escapeHtml(m.notes) : ''}</div>
        </div>
        <div class="alarm-toggle" data-med-id="${m.id}">
          <span class="alarm-icon ${alarmOn ? '' : 'off'}">${alarmOn ? '🔔' : '🔕'}</span>
          <div class="toggle-track ${alarmOn ? 'on' : ''}" role="switch" aria-checked="${alarmOn}" aria-label="${escapeHtml(t('meds.alarm'))}" tabindex="0">
            <div class="toggle-thumb"></div>
          </div>
        </div>
        <button class="delete" aria-label="${escapeHtml(t('people.delete'))} ${escapeHtml(m.name)}">×</button>
      </li>
    `;
  }).join('');

  // Check-off buttons
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

  // Alarm toggles
  list.querySelectorAll('.toggle-track').forEach(el => {
    function toggleAlarm() {
      const id = el.closest('.alarm-toggle').dataset.medId;
      const med = state.meds.find(m => m.id === id);
      if (!med) return;
      med.alarm = !med.alarm;
      if (med.alarm) {
        requestNotificationPermission();
      }
      save();
      renderMeds();
    }
    el.addEventListener('click', toggleAlarm);
    el.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleAlarm(); } });
  });

  // Delete buttons
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

// ========== NOTES ==========
function renderNotes() {
  const list = $('#notes-list');
  if (state.notes.length === 0) {
    list.innerHTML = `<li class="hint" style="padding:1rem 0;">${escapeHtml(t('notes.empty'))}</li>`;
    return;
  }
  // Show newest first
  const sorted = [...state.notes].reverse();
  list.innerHTML = sorted.map(n => {
    const date = new Date(n.created);
    const locale = TRANSLATIONS[getLang()].meta.dateLocale;
    const dateStr = date.toLocaleDateString(locale, { month: 'short', day: 'numeric' });
    return `
      <li class="list-item note-item" data-id="${n.id}">
        <div class="note-body">
          <div class="note-text">${escapeHtml(n.text)}</div>
          <div class="note-meta">
            <span class="note-time">${escapeHtml(dateStr)}</span>
            ${n.alarm && n.alarmTime ? `<span class="note-alarm-badge">🔔 ${escapeHtml(n.alarmTime)}</span>` : ''}
            ${!n.alarm ? `<span class="note-alarm-badge off">🔕 ${escapeHtml(t('notes.noAlarm'))}</span>` : ''}
          </div>
        </div>
        <button class="delete" aria-label="${escapeHtml(t('notes.delete'))}">×</button>
      </li>
    `;
  }).join('');

  list.querySelectorAll('.delete').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const id = e.target.closest('.list-item').dataset.id;
      if (confirm(t('notes.removeConfirm'))) {
        state.notes = state.notes.filter(n => n.id !== id);
        save();
        renderNotes();
        toast(t('toast.removed'));
      }
    });
  });
}

$('#add-note').addEventListener('click', () => openModal('note'));

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
        <button class="primary block" data-go="help" style="margin-top:1.25rem;">${escapeHtml(t('nav.backToHelp'))}</button>
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

// ========== MODAL (person / med / note) ==========
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
  } else if (mode === 'med') {
    title.textContent = t('meds.addTitle');
    body.innerHTML = `
      <label class="modal-label">${escapeHtml(t('form.name'))}</label>
      <input type="text" id="m-name" placeholder="${escapeHtml(t('form.placeholderMedName'))}" autofocus />
      <label class="modal-label">${escapeHtml(t('form.medTime'))}</label>
      <input type="text" id="m-time" placeholder="${escapeHtml(t('form.placeholderMedTime'))}" />
      <label class="modal-label">${escapeHtml(t('form.notes'))}</label>
      <input type="text" id="m-rel" placeholder="${escapeHtml(t('form.placeholderNotes'))}" />
    `;
  } else if (mode === 'note') {
    title.textContent = t('notes.addTitle');
    body.innerHTML = `
      <label class="modal-label">${escapeHtml(t('notes.noteText'))}</label>
      <textarea id="m-note-text" placeholder="${escapeHtml(t('notes.placeholderNote'))}" rows="3" style="min-height:80px;"></textarea>
      <label class="modal-label">${escapeHtml(t('notes.alarmTime'))}</label>
      <input type="time" id="m-alarm-time" style="max-width:200px;" />
      <p style="font-size:0.85rem;color:var(--text-muted);margin:0.25rem 0 0;">${escapeHtml(t('notes.alarmHint'))}</p>
    `;
  }
  $('#modal').classList.add('show');
  setTimeout(() => {
    const first = $('#modal-content input, #modal-content textarea');
    if (first) first.focus();
  }, 50);
}

function closeModal() {
  $('#modal').classList.remove('show');
  modalMode = null;
}

function saveModal() {
  if (modalMode === 'note') {
    const text = $('#m-note-text').value.trim();
    if (!text) {
      alert(t('form.needName'));
      $('#m-note-text').focus();
      return;
    }
    const alarmTime = $('#m-alarm-time').value; // "HH:MM" or ""
    const hasAlarm = !!alarmTime;
    if (hasAlarm) requestNotificationPermission();
    state.notes.push({
      id: 'n' + Date.now(),
      text,
      alarm: hasAlarm,
      alarmTime,
      created: new Date().toISOString()
    });
    save();
    renderNotes();
    toast(t('toast.added'));
    closeModal();
    return;
  }

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
    toast(t('toast.added'));
  } else if (modalMode === 'med') {
    state.meds.push({
      id: 'm' + Date.now(),
      name,
      time: $('#m-time').value.trim() || 'Anytime',
      notes: $('#m-rel').value.trim(),
      alarm: false
    });
    save();
    renderMeds();
    renderHome();
    toast(t('toast.added'));
  }
  closeModal();
}

// ========== NOTIFICATION / ALARM SYSTEM ==========
let alarmTimerId = null;
let lastAlarmMinute = -1;

function requestNotificationPermission() {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
  }
}

function checkAlarms() {
  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();
  if (currentMinutes === lastAlarmMinute) return; // already fired this minute
  lastAlarmMinute = currentMinutes;

  const locale = TRANSLATIONS[getLang()].meta.dateLocale;
  const timeStr = now.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' });

  // Check medicine alarms
  state.meds.forEach(m => {
    if (!m.alarm) return;
    const medMinutes = timeToMinutes(m.time);
    if (medMinutes === currentMinutes) {
      fireNotification(t('meds.alarmNotify', { name: m.name, time: timeStr }), m.name);
    }
  });

  // Check note alarms
  state.notes.forEach(n => {
    if (!n.alarm || !n.alarmTime) return;
    const [h, min] = n.alarmTime.split(':').map(Number);
    if (h * 60 + min === currentMinutes) {
      fireNotification(t('notes.alarmNotify', { text: n.text.substring(0, 60), time: timeStr }), n.text.substring(0, 30));
    }
  });
}

function fireNotification(body, tag) {
  // Browser notification
  if ('Notification' in window && Notification.permission === 'granted') {
    try {
      new Notification('Buddy', { body, icon: '/buddy/favicon.svg', tag: 'buddy-' + tag, requireInteraction: false });
    } catch(e) { /* notification failed silently */ }
  }
  // Also show in-app toast
  toast('🔔 ' + body);
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
      renderNotes();
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
    if (state.visits.length > 365) state.visits = state.visits.slice(-365);
    save();
  }
}

function maybeShowFeedback() {
  const uniqueDays = state.visits.length;
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
['#modal', '#upgrade-modal', '#lang-modal', '#feedback-modal', '#onboarding-modal'].forEach(sel => {
  const el = $(sel);
  if (el) {
    el.addEventListener('click', (e) => {
      if (e.target === el && sel !== '#feedback-modal') el.classList.remove('show');
    });
  }
});

// ========== ONBOARDING ==========
const ONBOARDING_STEPS = [
  { icon: '👋', getTitle: () => t('onboarding.welcomeTitle'), getText: () => t('onboarding.welcomeText') },
  { icon: '👥', getTitle: () => t('onboarding.peopleTitle'), getText: () => t('onboarding.peopleText') },
  { icon: '💊', getTitle: () => t('onboarding.medsTitle'), getText: () => t('onboarding.medsText') },
  { icon: '🛡️', getTitle: () => t('onboarding.safetyTitle'), getText: () => t('onboarding.safetyText') }
];

let onboardingStep = 0;

function maybeShowOnboarding() {
  if (state.onboarded) return;
  // Only show if there's no existing data (truly first visit)
  if (state.people.length > 0 && state.visits.length > 1) {
    state.onboarded = true;
    save();
    return;
  }
  renderOnboardingStep();
  $('#onboarding-modal').classList.add('show');
  requestNotificationPermission();
}

function renderOnboardingStep() {
  const step = ONBOARDING_STEPS[onboardingStep];
  const total = ONBOARDING_STEPS.length;
  const isLast = onboardingStep === total - 1;

  const stepsEl = $('#onboarding-steps');
  stepsEl.innerHTML = `
    <div class="onboarding-step active">
      <div class="onboarding-icon">${step.icon}</div>
      <h3>${escapeHtml(step.getTitle())}</h3>
      <p>${escapeHtml(step.getText())}</p>
    </div>
  `;

  // Dots
  const dotsEl = $('#onboarding-dots');
  dotsEl.innerHTML = ONBOARDING_STEPS.map((_, i) =>
    `<div class="onboarding-dot ${i === onboardingStep ? 'active' : ''}"></div>`
  ).join('');

  // Button text
  const nextBtn = $('#onboarding-next');
  nextBtn.textContent = isLast ? t('onboarding.done') : t('onboarding.next');
}

$('#onboarding-next').addEventListener('click', () => {
  onboardingStep++;
  if (onboardingStep >= ONBOARDING_STEPS.length) {
    state.onboarded = true;
    save();
    $('#onboarding-modal').classList.remove('show');
    return;
  }
  renderOnboardingStep();
});

$('#onboarding-skip').addEventListener('click', () => {
  state.onboarded = true;
  save();
  $('#onboarding-modal').classList.remove('show');
});

// ========== INIT ==========
load();
applyI18n();
renderHome();
renderPeople();
renderMeds();
renderNotes();
renderTopics();
renderSafetyList();
updateEmergencyLinks();
trackVisit();

// Check alarms every 30 seconds
alarmTimerId = setInterval(checkAlarms, 30000);
// Also check once on load (in case an alarm was missed while tab was closed)
setTimeout(checkAlarms, 2000);

// Re-render check-in status periodically
setInterval(renderHome, 60 * 1000);

// Show onboarding for first-time users (delay so page renders first)
setTimeout(maybeShowOnboarding, 800);

// Show feedback prompt after a beat
setTimeout(maybeShowFeedback, 5000);