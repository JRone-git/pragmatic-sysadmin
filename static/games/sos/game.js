(function () {
  const el = (id) => document.getElementById(id);
  let path = [];

  function render(id, push = true) {
    const node = window.SOS_TREE.nodes[id];
    if (push) path.push(id);
    const box = el("node");
    if (node.type === "q") {
      box.innerHTML = `<h2 class="q">${node.text}</h2>
        <div class="choices">${node.options
          .map(
            (o, i) =>
              `<button class="psa-btn choice" data-next="${o.next}">${i + 1} · ${o.label}</button>`
          )
          .join("")}</div>`;
      box.querySelectorAll(".choice").forEach((b) =>
        b.addEventListener("click", () => render(b.dataset.next))
      );
    } else {
      box.innerHTML = `
        <h2>${node.title}</h2>
        <p class="likely"><strong>Most likely:</strong> ${node.likely}</p>
        <ol class="steps">${node.steps.map((x) => `<li>${x}</li>`).join("")}</ol>
        <p><a class="psa-link" href="${node.guide}">Read the full guide →</a></p>
        ${PSA.cta(node.product, "Get the Tech Confidence Checklist (€9)")}`;
      PSA.track("sos_outcome", { outcome: id, depth: path.length });
    }
    el("back").hidden = path.length <= 1;
  }

  function back() {
    if (path.length <= 1) return;
    path.pop();
    render(path[path.length - 1], false);
  }

  document.addEventListener("DOMContentLoaded", () => {
    el("start").addEventListener("click", () => {
      el("intro").hidden = true;
      el("game").hidden = false;
      PSA.track("sos_start");
      render(window.SOS_TREE.start);
    });
    el("back").addEventListener("click", back);

    document.addEventListener("click", (e) => {
      const a = e.target.closest("[data-cta]");
      if (a) PSA.track("cta_click", { slug: a.dataset.cta });
    });

    const sizeBtn = el("size-toggle");
    sizeBtn.addEventListener("click", () => {
      const isLarge = document.documentElement.dataset.size === "xlarge";
      document.documentElement.dataset.size = isLarge ? "" : "xlarge";
      sizeBtn.textContent = isLarge ? "Larger text" : "Standard text";
    });
  });
})();