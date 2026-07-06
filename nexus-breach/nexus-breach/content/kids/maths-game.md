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

// Game state
let score = 0, total = 0, streak = 0, multiplier = 1;
let difficulty = 'easy'; // easy | medium | hard
let timerId = null, timeLeft = 0;
const bestKey = 'kids_maths_best';

const ranges = {
  easy: {min:1, max:10, time:12},
  medium: {min:5, max:20, time:9},
  hard: {min:10, max:50, time:6}
};

function setDifficulty(d) {
  difficulty = d;
  showStart();
}

function showStart() {
  const best = localStorage.getItem(bestKey) || 0;
  document.getElementById('maths-game').innerHTML = `
    <div style='margin-bottom:1em;'>
      <button onclick="setDifficulty('easy')" style='margin-right:.5em;'>Easy</button>
      <button onclick="setDifficulty('medium')" style='margin-right:.5em;'>Medium</button>
      <button onclick="setDifficulty('hard')">Hard</button>
    </div>
    <div style='margin-bottom:1em;'>Difficulty: <b>${difficulty}</b></div>
    <div style='margin-bottom:1em;'>Best score: <b>${best}</b></div>
    <button onclick='startGame()' style='font-size:1.2em;padding:.5em 1em;'>Start</button>
    <div id='math-controls' style='margin-top:1em;'></div>
  `;
}

function startGame() {
  score = 0; total = 0; streak = 0; multiplier = 1;
  nextQuestion();
}

function nextQuestion() {
  clearTimeout(timerId);
  const r = ranges[difficulty];
  const a = randomInt(r.min, r.max), b = randomInt(r.min, r.max);
  const answer = a + b;
  // generate distractors with variety
  const opts = new Set([answer]);
  while (opts.size < 3) {
    const delta = randomInt(1, Math.max(2, Math.floor(answer * 0.2)));
    const sign = Math.random() < 0.5 ? -1 : 1;
    opts.add(Math.max(0, answer + sign * delta));
  }
  const options = Array.from(opts).sort(() => Math.random() - 0.5);

  timeLeft = r.time;
  document.getElementById('maths-game').innerHTML = `
    <div style='display:flex;justify-content:space-between;align-items:center;'><div>Score: <b>${score}</b> (Best: <b>${localStorage.getItem(bestKey)||0}</b>)</div><div>Streak: <b id="streak">${streak}</b> x<b id="mult">${multiplier}</b></div></div>
    <h3 style='font-size:1.6em;'>${a} + ${b} = ?</h3>
    <div>${options.map(opt => `<button class='math-btn' style='font-size:1.2em;margin:0.5em;padding:.6em 1em;' onclick='checkMath(${opt},${answer})'>${opt}</button>`).join('')}</div>
    <div id='math-feedback' style='min-height:1.5em;margin-top:.8em;'></div>
    <div style='margin-top:0.5em;'>Time left: <span id='time'>${timeLeft}</span>s</div>
  `;

  // start countdown
  timerId = setInterval(() => {
    timeLeft--;
    const el = document.getElementById('time');
    if (el) el.textContent = timeLeft;
    if (timeLeft <= 0) {
      clearInterval(timerId);
      total++;
      streak = 0; multiplier = 1;
      document.getElementById('math-feedback').innerHTML = `<span style="color:orange;">Time's up! The answer was <b>${answer}</b></span>`;
      setTimeout(nextQuestion, 1200);
    }
  }, 1000);
}

window.checkMath = function(opt, answer) {
  clearInterval(timerId);
  total++;
  if (opt === answer) {
    streak++;
    multiplier = 1 + Math.floor(streak / 3);
    score += multiplier;
    document.getElementById('math-feedback').innerHTML = `<span style="color:green;">Correct! +${multiplier}</span>`;
  } else {
    streak = 0; multiplier = 1;
    document.getElementById('math-feedback').innerHTML = `<span style="color:red;">Wrong — answer was <b>${answer}</b></span>`;
  }
  const best = parseInt(localStorage.getItem(bestKey) || '0', 10);
  let isNewBest = false;
  if (score > best) { localStorage.setItem(bestKey, score); isNewBest = true; }
  // celebratory confetti on milestones
  if (streak >= 5) launchConfetti();
  if (isNewBest) launchConfetti();
  // brief pause then next
  setTimeout(nextQuestion, 900);
};

// lightweight confetti (same implementation as reading-game)
function launchConfetti() {
  const container = document.createElement('div');
  container.style.position = 'fixed';
  container.style.left = 0;
  container.style.top = 0;
  container.style.width = '100%';
  container.style.height = '100%';
  container.style.pointerEvents = 'none';
  container.style.overflow = 'hidden';
  document.body.appendChild(container);
  const colours = ['#ff5e5b','#ffca3a','#8ac926','#1982c4','#6a4c93'];
  const count = 30;
  for (let i=0;i<count;i++) {
    const el = document.createElement('div');
    const size = Math.random()*10+6;
    el.style.position = 'absolute';
    el.style.width = size+'px';
    el.style.height = (size*0.6)+'px';
    el.style.background = colours[Math.floor(Math.random()*colours.length)];
    el.style.left = (Math.random()*100)+'%';
    el.style.top = '-10%';
    el.style.opacity = '0.95';
    el.style.transform = `rotate(${Math.random()*360}deg)`;
    el.style.borderRadius = '2px';
    el.style.transition = 'transform 1.6s linear, top 1.6s cubic-bezier(.17,.67,.83,.67), opacity 0.5s linear 1.6s';
    container.appendChild(el);
    setTimeout(() => {
      el.style.top = (60 + Math.random()*40)+'%';
      el.style.transform = `rotate(${Math.random()*720}deg) translateX(${(Math.random()-0.5)*200}px)`;
    }, 20 + Math.random()*200);
  }
  setTimeout(() => { container.style.transition='opacity .5s'; container.style.opacity='0'; setTimeout(()=>container.remove(),600); }, 2200);
}

// initialize
showStart();
</script>
