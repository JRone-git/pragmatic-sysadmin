---
title: "Reading Game (Finnish)"
description: "Learn Finnish words with pictures! Tap the right word for each image."
draft: false
---


# Lukupeli (Suomi)

Valitse oikea sana kuvan perusteella. Sanojen tavutus auttaa lukemaan!

<div id="reading-game"></div>

<script>
const items = [
  {img: 'https://cdn.pixabay.com/photo/2017/01/06/19/15/cat-1951307_1280.jpg', word: 'kissa', syllables: 'kis-sa', options: ['kissa', 'koira', 'auto']},
  {img: 'https://cdn.pixabay.com/photo/2016/02/19/10/00/dog-1207816_1280.jpg', word: 'koira', syllables: 'koi-ra', options: ['kissa', 'koira', 'pallo']},
  {img: 'https://cdn.pixabay.com/photo/2012/05/29/00/43/car-49278_1280.jpg', word: 'auto', syllables: 'au-to', options: ['koira', 'auto', 'kissa']},
  {img: 'https://cdn.pixabay.com/photo/2016/03/27/21/16/ball-1283760_1280.jpg', word: 'pallo', syllables: 'pal-lo', options: ['pallo', 'kissa', 'koira']},
  {img: 'https://cdn.pixabay.com/photo/2014/12/21/23/28/snow-577412_1280.jpg', word: 'lumi', syllables: 'lu-mi', options: ['lumi', 'auto', 'koira']}
];
let score = 0;
let current = 0;
function showItem() {
  if (current >= items.length) {
    document.getElementById('reading-game').innerHTML = `<h3>Peli loppui! Pisteet: ${score}/${items.length}</h3>`;
    return;
  }
  const item = items[current];
  document.getElementById('reading-game').innerHTML = `
    <img src="${item.img}" alt="pic" style="max-width:220px;display:block;margin-bottom:1em;border-radius:12px;box-shadow:0 0 10px #ccc;" />
    <div style='font-size:1.3em;margin-bottom:1em;'>Tavutus: <b>${item.syllables}</b></div>
    <div>
      ${item.options.map(opt => `<button style='font-size:2em;margin:0.7em;padding:0.7em 2em;border-radius:1em;background:#f7c873;color:#222;border:2px solid #f7c873;box-shadow:0 2px 6px #ccc;' onclick='checkWord("${opt}")'>${opt}</button>`).join('')}
    </div>
    <div id='feedback'></div>
    <div style='margin-top:1em;'>Pisteet: ${score}/${items.length}</div>
  `;
}
window.checkWord = function(word) {
  const item = items[current];
  if (word === item.word) {
    score++;
    document.getElementById('feedback').innerHTML = '<span style="color:green;font-size:1.3em;">Oikein!</span>';
  } else {
    document.getElementById('feedback').innerHTML = '<span style="color:red;font-size:1.3em;">Yritä uudelleen!</span>';
    return;
  }
  setTimeout(() => { current++; showItem(); }, 1000);
};
showItem();
</script>
