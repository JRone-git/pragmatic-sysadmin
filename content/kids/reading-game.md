---
title: "Reading Game (Finnish)"
description: "Learn Finnish words with pictures! Tap the right word for each image."
draft: false
---



# Lukupeli / Reading Game

<div id="reading-game"></div>

<script>
// Reliable images for kissa, koira, auto, pallo, lumi (Finnish and English)
const images = {
  kissa: '/images/kids/kissa.svg',
  koira: '/images/kids/koira.svg',
  auto: '/images/kids/auto.svg',
  pallo: '/images/kids/pallo.svg',
  lumi: '/images/kids/lumi.svg',
  koira_en: '/images/kids/koira.svg',
  cat: '/images/kids/kissa.svg',
  car: '/images/kids/auto.svg',
  ball: '/images/kids/pallo.svg',
  snow: '/images/kids/lumi.svg'
};

const items_fi = [
  {img: images.kissa, word: 'kissa', syllables: 'kis-sa', options: ['kissa', 'koira', 'auto']},
  {img: images.koira, word: 'koira', syllables: 'koi-ra', options: ['kissa', 'koira', 'pallo']},
  {img: images.auto, word: 'auto', syllables: 'au-to', options: ['koira', 'auto', 'kissa']},
  {img: images.pallo, word: 'pallo', syllables: 'pal-lo', options: ['pallo', 'kissa', 'koira']},
  {img: images.lumi, word: 'lumi', syllables: 'lu-mi', options: ['lumi', 'auto', 'koira']}
];
const items_en = [
  {img: images.cat, word: 'cat', syllables: 'cat', options: ['cat', 'dog', 'car']},
  {img: images.koira_en, word: 'dog', syllables: 'dog', options: ['cat', 'dog', 'ball']},
  {img: images.car, word: 'car', syllables: 'car', options: ['dog', 'car', 'cat']},
  {img: images.ball, word: 'ball', syllables: 'ball', options: ['ball', 'cat', 'dog']},
  {img: images.snow, word: 'snow', syllables: 'snow', options: ['snow', 'car', 'dog']}
];

let lang = 'fi';
let nickname = '';
let score = 0;
let current = 0;
let leaderboard = JSON.parse(localStorage.getItem('kids_leaderboard') || '[]');

function startGame() {
  score = 0; current = 0;
  showItem();
}

function showStart() {
  document.getElementById('reading-game').innerHTML = `
    <div style='margin-bottom:1em;'>
      <label for='nickname'><b>Valitse nimimerkki / Choose nickname:</b></label>
      <input id='nickname' type='text' maxlength='12' style='font-size:1.2em;padding:0.3em;' />
    </div>
    <div style='margin-bottom:1em;'>
      <label><b>Kieli / Language:</b></label>
      <button onclick='setLang("fi")' style='font-size:1.2em;margin-right:1em;'>Suomi</button>
      <button onclick='setLang("en")' style='font-size:1.2em;'>English</button>
    </div>
    <button onclick='beginGame()' style='font-size:1.5em;padding:0.5em 2em;background:#7ed957;color:#222;border-radius:1em;border:2px solid #7ed957;'>Aloita / Start</button>
    <div style='margin-top:2em;'>
      <b>Leaderboard:</b>
      <ul id='lb'></ul>
    </div>
  `;
  showLeaderboard();
  document.getElementById('nickname').addEventListener('input', e => nickname = e.target.value);
}

function setLang(l) { lang = l; }
function beginGame() { if (!nickname) nickname = 'Pelaaja'; startGame(); }

function showLeaderboard() {
  const lb = leaderboard.sort((a,b) => b.score - a.score).slice(0,5);
  document.getElementById('lb').innerHTML = lb.map(e => `<li>${e.name}: ${e.score}</li>`).join('');
}

function showItem() {
  const items = lang === 'fi' ? items_fi : items_en;
  if (current >= items.length) {
    leaderboard.push({name: nickname, score});
    localStorage.setItem('kids_leaderboard', JSON.stringify(leaderboard));
    document.getElementById('reading-game').innerHTML = `<h3>${lang==='fi' ? 'Peli loppui!' : 'Game Over!'} ${lang==='fi' ? 'Pisteet' : 'Score'}: ${score}/${items.length}</h3><button onclick='showStart()' style='font-size:1.2em;padding:0.5em 2em;background:#7ed957;color:#222;border-radius:1em;border:2px solid #7ed957;'>${lang==='fi' ? 'Uudestaan' : 'Restart'}</button><div style='margin-top:2em;'><b>Leaderboard:</b><ul id='lb'></ul></div>`;
    showLeaderboard();
    return;
  }
  const item = items[current];
  document.getElementById('reading-game').innerHTML = `
    <div style='margin-bottom:1em;font-size:1.2em;'>${lang==='fi' ? 'Nimimerkki' : 'Nickname'}: <b>${nickname}</b></div>
    <img src="${item.img}" alt="pic" style="max-width:220px;display:block;margin-bottom:1em;border-radius:12px;box-shadow:0 0 10px #ccc;" />
    <div style='font-size:1.3em;margin-bottom:1em;'>${lang==='fi' ? 'Tavutus' : 'Syllables'}: <b>${item.syllables}</b></div>
    <div>
      ${item.options.map(opt => `<button style='font-size:2em;margin:0.7em;padding:0.7em 2em;border-radius:1em;background:#f7c873;color:#222;border:2px solid #f7c873;box-shadow:0 2px 6px #ccc;' onclick='checkWord("${opt}")'>${opt}</button>`).join('')}
    </div>
    <div id='feedback'></div>
    <div style='margin-top:1em;'>${lang==='fi' ? 'Pisteet' : 'Score'}: ${score}/${items.length}</div>
  `;
}
window.checkWord = function(word) {
  const items = lang === 'fi' ? items_fi : items_en;
  const item = items[current];
  if (word === item.word) {
    score++;
    document.getElementById('feedback').innerHTML = `<span style="color:green;font-size:1.3em;">${lang==='fi' ? 'Oikein!' : 'Correct!'}</span>`;
  } else {
    document.getElementById('feedback').innerHTML = `<span style="color:red;font-size:1.3em;">${lang==='fi' ? 'Yritä uudelleen!' : 'Try again!'}</span>`;
    return;
  }
  setTimeout(() => { current++; showItem(); }, 1000);
};
showStart();
</script>
