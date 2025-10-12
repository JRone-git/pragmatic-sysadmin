---
title: "Maths Game"
description: "Practice maths from simple addition to more complex problems."
draft: false
---

# Maths Game

Solve the problem and tap your answer:

<div id="maths-game"></div>

<script>
function randomInt(a, b) { return Math.floor(Math.random() * (b - a + 1)) + a; }
let score = 0, total = 0;
function nextQuestion() {
  const a = randomInt(1, 10), b = randomInt(1, 10);
  const answer = a + b;
  const options = [answer, answer + randomInt(1, 3), answer - randomInt(1, 2)].sort(() => Math.random() - 0.5);
  document.getElementById('maths-game').innerHTML = `
    <h3>${a} + ${b} = ?</h3>
    <div>${options.map(opt => `<button style='font-size:1.2em;margin:0.5em;' onclick='checkMath(${opt},${answer})'>${opt}</button>`).join('')}</div>
    <div id='math-feedback'></div>
    <div>Score: ${score}/${total}</div>
  `;
}
window.checkMath = function(opt, answer) {
  total++;
  if (opt === answer) {
    score++;
    document.getElementById('math-feedback').innerHTML = '<span style="color:green;">Correct!</span>';
  } else {
    document.getElementById('math-feedback').innerHTML = '<span style="color:red;">Try again!</span>';
    return;
  }
  setTimeout(nextQuestion, 800);
};
nextQuestion();
</script>
