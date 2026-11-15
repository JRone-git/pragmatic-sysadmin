(function () {
  const ROUND = 8;
  const el = (id) => document.getElementById(id);
  let s = {};

  const shuffle = (a) => {
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  };
  const fmt = (t) => t.replace(/\[\[(.+?)\]\]/g, "<mark>$1</mark>");

  function start() {
    s = {
      queue: shuffle([...window.PHISHING_DECK]).slice(0, ROUND),
      i: 0,
      score: 0,
      streak: 0,
      best: 0,
      done: false
    };
    el("intro").hidden = true;
    el("summary").hidden = true;
    el("game").hidden = false;
    PSA.track("phishing_start");
    render();
  }

  function render() {
    const item = s.queue[s.i];
    s.done = false;
    el("progress").textContent = `Email ${s.i + 1} of ${s.queue.length}`;
    el("bar").style.width = `${(s.i / s.queue.length) * 100}%`;
    el("from").textContent = item.from;
    el("subject").textContent = item.subject;
    el("body").innerHTML = fmt(item.body);
    el("feedback").hidden = true;
    el("feedback").innerHTML = "";
    el("choices").hidden = false;
    el("next").hidden = true;
    document.querySelectorAll(".choice").forEach((b) => (b.disabled = false));
  }

  function answer(guess) {
    if (s.done) return;
    s.done = true;
    const item = s.queue[s.i];
    const correct = guess === item.verdict;
    if (correct) {
      s.streak++;
      s.score += 10 + Math.min(s.streak, 5) * 2;
      s.best = Math.max(s.best, s.streak);
    } else {
      s.streak = 0;
    }

    document.querySelectorAll(".choice").forEach((b) => (b.disabled = true));
    el("choices").hidden = true;
    const fb = el("feedback");
    fb.hidden = false;
    fb.innerHTML = `
      <p class="verdict ${correct ? "ok" : "bad"}">
        ${correct ? "✔ Correct" : "✘ Not quite"} — this is
        <strong>${item.verdict === "phishing" ? "phishing" : "legitimate"}</strong>.
      </p>
      <ul class="flags">${item.flags.map((f) => `<li>${f}</li>`).join("")}</ul>
      <p class="explain">${item.explain}</p>`;
    el("next").hidden = false;
    el("next").focus();
    el("score").textContent = s.score;
  }

  function next() {
    s.i++;
    if (s.i >= s.queue.length) return finish();
    render();
  }

  function finish() {
    el("game").hidden = true;
    const sum = el("summary");
    sum.hidden = false;
    const pct = s.score / (s.queue.length * 12);
    const badge =
      pct > 0.85 ? "Sharp-eyed Spotter" : pct > 0.6 ? "Careful Checker" : "Keep Practicing";
    el("badge").textContent = badge;
    el("finalScore").textContent = s.score;
    el("bestStreak").textContent = s.best;
    el("ctaSlot").innerHTML = PSA.cta(
      "scam-safety-guide",
      "Get the one-page Scam Safety Guide (€9)"
    );
    el("ctaSlot").insertAdjacentHTML(
      "beforeend",
      '<p style="font-size:0.9rem;color:var(--muted);margin-top:1rem;">New games? <a href="/newsletter/" class="psa-link">Join the newsletter</a>.</p>'
    );
    PSA.save({ phishing: { score: s.score, badge, at: Date.now() } });
    PSA.track("phishing_complete", { score: s.score, badge });
  }

  document.addEventListener("DOMContentLoaded", () => {
    el("start").addEventListener("click", start);
    el("next").addEventListener("click", next);
    el("restart").addEventListener("click", start);
    document.querySelectorAll(".choice").forEach((b) =>
      b.addEventListener("click", () => answer(b.dataset.guess))
    );
    document.addEventListener("keydown", (e) => {
      if (el("game").hidden) return;
      if (e.key === "1") answer("safe");
      if (e.key === "2") answer("phishing");
      if (e.key === "Enter" && !el("next").hidden) next();
    });
    document.querySelectorAll("[data-cta]").forEach((a) =>
      a.addEventListener("click", () =>
        PSA.track("cta_click", { slug: a.dataset.cta })
      )
    );

    const sizeBtn = el("size-toggle");
    sizeBtn.addEventListener("click", () => {
      const isLarge = document.documentElement.dataset.size === "xlarge";
      document.documentElement.dataset.size = isLarge ? "" : "xlarge";
      sizeBtn.textContent = isLarge ? "Larger text" : "Standard text";
    });
  });
})();