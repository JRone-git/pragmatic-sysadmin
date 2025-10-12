---
title: "Reading Game (Finnish)"
description: "Learn Finnish words with pictures! Tap the right word for each image."
draft: false
---

# Reading Game (Finnish)

Tap the correct Finnish word for each picture:

<div id="reading-game"></div>

<script>
const items = [
  {img: 'https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg', word: 'kissa', options: ['kissa', 'koira', 'auto']},
  {img: 'https://upload.wikimedia.org/wikipedia/commons/6/6e/Golde33443.jpg', word: 'koira', options: ['kissa', 'koira', 'pallo']},
  {img: 'https://upload.wikimedia.org/wikipedia/commons/3/3e/Car.jpg', word: 'auto', options: ['koira', 'auto', 'kissa']}
];
let score = 0;
let current = 0;
function showItem() {
  if (current >= items.length) {
    document.getElementById('reading-game').innerHTML = `<h3>Game Over! Score: ${score}/${items.length}</h3>`;
    return;
  }
  const item = items[current];
  document.getElementById('reading-game').innerHTML = `
    <img src="${item.img}" alt="pic" style="max-width:200px;display:block;margin-bottom:1em;" />
    <div>
      ${item.options.map(opt => `<button style='font-size:1.2em;margin:0.5em;' onclick='checkWord("${opt}")'>${opt}</button>`).join('')}
    </div>
    <div id='feedback'></div>
  `;
}
window.checkWord = function(word) {
  const item = items[current];
  if (word === item.word) {
    score++;
    document.getElementById('feedback').innerHTML = '<span style="color:green;">Correct!</span>';
  } else {
    document.getElementById('feedback').innerHTML = '<span style="color:red;">Try again!</span>';
    return;
  }
  setTimeout(() => { current++; showItem(); }, 800);
};
showItem();
</script>
