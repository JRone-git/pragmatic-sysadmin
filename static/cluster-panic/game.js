(function () {
  const servers = [
    { name: "API NODE", issue: "Disk Full", action: "Purge /tmp", color: "red" },
    { name: "EDGE NODE", issue: "SYN Flood", action: "Enable Firewall", color: "yellow" },
    { name: "WORKER NODE", issue: "Memory Leak", action: "Restart Pod", color: "blue" },
    { name: "CACHE NODE", issue: "Overheating", action: "Boost Fan", color: "orange" }
  ].map((server) => ({ ...server, health: 100, active: true }));

  let selected = 0;
  let incidents = 0;
  let running = false;
  let startedAt = 0;
  let timer;
  let decayTimer;

  const rank = (days) => days > 2 ? "SRE Legend" : days > 1 ? "Senior SRE" : days > 0.25 ? "On-Call Hero" : "Novice";
  const container = document.getElementById("servers-container");

  function render() {
    container.innerHTML = servers.map((server, index) => {
      const selectedClass = index === selected ? "ring-2 ring-cyan-400" : "";
      const healthColor = server.health > 60 ? "green" : server.health > 25 ? "yellow" : "red";
      return `<button data-server="${index}" class="${selectedClass} rounded-lg border border-gray-700 bg-gray-800 p-4 text-left hover:border-cyan-400">
        <div class="mb-3 flex justify-between"><strong class="text-gray-100">${server.name}</strong><span class="text-${healthColor}-400">${Math.max(0, server.health).toFixed(0)}%</span></div>
        <div class="mb-3 h-3 rounded bg-gray-700"><div class="h-3 rounded bg-${healthColor}-500" style="width:${Math.max(0, server.health)}%"></div></div>
        <p class="mb-3 text-sm text-${server.active ? "red" : "gray"}-300">${server.active ? server.issue : "Operational"}</p>
        <span class="rounded bg-gray-700 px-3 py-2 text-xs">${server.active ? server.action : "Healthy"}</span>
      </button>`;
    }).join("");
    document.getElementById("incident-count").textContent = incidents;
  }

  function updateStats() {
    const days = running ? (Date.now() - startedAt) / 86400000 : 0;
    const uptime = servers.reduce((total, server) => total + Math.max(0, server.health), 0) / servers.length;
    document.getElementById("uptime-score").textContent = `${uptime.toFixed(2)}%`;
    document.getElementById("days-survived").textContent = days.toFixed(2);
    document.getElementById("best-rank").textContent = rank(days);
  }

  function repair() {
    const server = servers[selected];
    server.health = Math.min(100, server.health + 35);
    server.active = server.health < 75;
    document.getElementById("game-message").textContent = `${server.name}: ${server.action} complete.`;
    render();
    updateStats();
  }

  function start() {
    running = true;
    startedAt = Date.now();
    document.getElementById("start-screen").classList.add("hidden");
    timer = setInterval(updateStats, 1000);
    decayTimer = setInterval(() => {
      const server = servers[Math.floor(Math.random() * servers.length)];
      server.health -= 5;
      if (server.health < 75) { server.active = true; incidents += 1; }
      render();
      updateStats();
    }, 3500);
  }

  container.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-server]");
    if (!button) return;
    selected = Number(button.dataset.server);
    repair();
  });
  document.getElementById("start-game-btn").addEventListener("click", start);
  document.addEventListener("keydown", (event) => {
    if (event.key >= "1" && event.key <= "4") { selected = Number(event.key) - 1; render(); }
    if (event.key.toLowerCase() === "r") repair();
    if (event.code === "Space" && running) { event.preventDefault(); servers[selected].health = Math.min(100, servers[selected].health + 2); render(); updateStats(); }
  });
  render();
  updateStats();
})();