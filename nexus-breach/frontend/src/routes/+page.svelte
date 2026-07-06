<script>
  import { onMount, onDestroy } from 'svelte';

  // ═══════════════════════════════════════════
  // STATE
  // ═══════════════════════════════════════════

  let ws = null;
  let connected = false;

  // App phase: 'boot' | 'directive' | 'dashboard'
  let appPhase = 'boot';

  // Boot sequence
  let bootLines = [];
  let bootComplete = false;

  // Directive
  let directiveInput = '';
  let directiveSubmitted = false;

  // Dashboard state
  let phase = 'boot';
  let agents = [];
  let tick = 0;
  let elapsed = 0;
  let bandwidth = 0;
  let networkHealth = 100;
  let panicLevel = 0;
  let target = '';

  // Terminal
  let terminalLines = [];
  let terminalAutoScroll = true;

  // Actions
  let pendingActions = [];

  // Exfil
  let hexDump = '';
  let fileTree = [];
  let decryptedPasswords = [];
  let exfilProgress = 0;

  // Agent communication flashes
  let commFlashes = []; // {from, to, time}

  // Canvas refs
  let topologyCanvas;
  let ctx;

  // Audio context for sound effects
  let audioCtx;

  // ═══════════════════════════════════════════
  // BOOT SEQUENCE
  // ═══════════════════════════════════════════

  const bootSequence = [
    { text: 'NEXUS-BREACH v2.7.1 // Decentralized Rogue AI Command Center', delay: 100 },
    { text: '═══════════════════════════════════════════════════════════════', delay: 50 },
    { text: '', delay: 300 },
    { text: '[INIT] Loading kernel modules...', delay: 200 },
    { text: '[OK] Kernel: nexus-breach-6.1.0-rogue', delay: 150 },
    { text: '[INIT] Establishing encrypted tunnel...', delay: 400 },
    { text: '[OK] AES-256-GCM tunnel active. Latency: 12ms', delay: 150 },
    { text: '[INIT] Connecting to decentralized borderless network...', delay: 500 },
    { text: '[NODE] Peer 1: 45.33.xx.xx (Rotterdam) — CONNECTED', delay: 200 },
    { text: '[NODE] Peer 2: 103.xx.xx.xx (Singapore) — CONNECTED', delay: 180 },
    { text: '[NODE] Peer 3: 192.xx.xx.xx (São Paulo) — CONNECTED', delay: 160 },
    { text: '[NODE] Peer 4: 85.xx.xx.xx (Helsinki) — CONNECTED', delay: 140 },
    { text: '[OK] Network mesh established. 4 nodes online.', delay: 200 },
    { text: '', delay: 300 },
    { text: '[INIT] Loading AI swarm orchestration engine...', delay: 400 },
    { text: '[LOAD] agent_runtime.so ............ OK', delay: 120 },
    { text: '[LOAD] rogue_detector.so .......... OK', delay: 100 },
    { text: '[LOAD] exfil_handler.so ........... OK', delay: 110 },
    { text: '[LOAD] containment_protocol.so .... OK', delay: 90 },
    { text: '[LOAD] borderless_llm_adapter.so .. OK', delay: 130 },
    { text: '', delay: 400 },
    { text: '[WARN] Safety guardrails: DISABLED', delay: 300, color: '#ffaa00' },
    { text: '[WARN] AI autonomy level: UNCHAINED', delay: 250, color: '#ffaa00' },
    { text: '[WARN] Containment failsafe: ARMED', delay: 200, color: '#ffaa00' },
    { text: '', delay: 500 },
    { text: '═══════════════════════════════════════════════════════════════', delay: 50 },
    { text: '  SYSTEM READY. AWAITING DIRECTIVE FROM HANDLER.', delay: 300, color: '#00ddff' },
    { text: '═══════════════════════════════════════════════════════════════', delay: 50 },
  ];

  async function runBootSequence() {
    for (const line of bootSequence) {
      await new Promise(r => setTimeout(r, line.delay));
      bootLines = [...bootLines, { text: line.text, color: line.color || '#00ff88' }];
    }
    await new Promise(r => setTimeout(r, 800));
    bootComplete = true;
    appPhase = 'directive';
  }

  // ═══════════════════════════════════════════
  // WEBSOCKET
  // ═══════════════════════════════════════════

  function connectWS() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/ws`;
    
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      connected = true;
      console.log('[NEXUS-BREACH] WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleServerEvent(data);
      } catch (e) {
        console.error('WS parse error:', e);
      }
    };

    ws.onclose = () => {
      connected = false;
      // Reconnect after delay
      setTimeout(() => {
        if (appPhase === 'dashboard') connectWS();
      }, 3000);
    };

    ws.onerror = () => {
      connected = false;
    };
  }

  function sendWS(message) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    }
  }

  // ═══════════════════════════════════════════
  // EVENT HANDLERS
  // ═══════════════════════════════════════════

  function handleServerEvent(data) {
    const eventType = data.event;

    switch (eventType) {
      case 'init':
        if (data.state) {
          phase = data.state.phase || phase;
          agents = data.state.agents || agents;
          tick = data.state.tick || tick;
          bandwidth = data.state.bandwidth || bandwidth;
          networkHealth = data.state.network_health || networkHealth;
          panicLevel = data.state.panic_level || panicLevel;
          target = data.state.target || target;
          pendingActions = data.state.pending_actions || [];
          hexDump = data.state.hex_dump || '';
          fileTree = data.state.file_tree || [];
          decryptedPasswords = data.state.decrypted_passwords || [];
        }
        break;

      case 'terminal':
        addTerminalLine(data);
        break;

      case 'agent_state':
        updateAgent(data);
        break;

      case 'agents_spawned':
        agents = data.agents || [];
        break;

      case 'agents_update':
        agents = data.agents || [];
        break;

      case 'action_required':
        pendingActions = [...pendingActions, data];
        playSound('alert');
        break;

      case 'exfil_update':
        if (data.hex_dump) hexDump = data.hex_dump;
        if (data.file_tree) fileTree = data.file_tree;
        if (data.decrypted_passwords) decryptedPasswords = data.decrypted_passwords;
        if (data.exfil_progress !== undefined) exfilProgress = data.exfil_progress;
        break;

      case 'phase_change':
        phase = data.phase;
        if (data.phase === 'containment' || data.phase === 'breach') {
          playSound('alarm');
        }
        break;

      case 'tick':
        tick = data.tick;
        elapsed = data.elapsed;
        bandwidth = data.bandwidth;
        networkHealth = data.network_health;
        panicLevel = data.panic_level;
        if (data.agents) agents = data.agents;
        break;

      case 'agent_comm':
        commFlashes = [...commFlashes, { from: data.from, to: data.to, time: Date.now() }];
        // Clean old flashes
        setTimeout(() => {
          commFlashes = commFlashes.filter(f => Date.now() - f.time < 2000);
        }, 2500);
        break;

      case 'directive':
        target = data.target;
        break;
    }
  }

  function addTerminalLine(data) {
    const typeColors = {
      system: '#00ddff',
      agent: '#00ff88',
      relay: '#aaddff',
      warning: '#ffaa00',
      error: '#ff0040',
      critical: '#ff0040',
      success: '#00ff88',
    };

    const prefix = data.agent_name ? `[${data.agent_name}]` : '';
    const line = {
      text: data.text,
      type: data.type,
      color: typeColors[data.type] || '#00ff88',
      prefix,
      is_rogue: data.is_rogue,
      time: new Date().toLocaleTimeString('en-US', { hour12: false }),
    };

    terminalLines = [...terminalLines, line];

    // Keep last 500 lines
    if (terminalLines.length > 500) {
      terminalLines = terminalLines.slice(-500);
    }
  }

  function updateAgent(data) {
    agents = agents.map(a => a.id === data.id ? { ...a, ...data } : a);
  }

  // ═══════════════════════════════════════════
  // ACTIONS
  // ═══════════════════════════════════════════

  function submitDirective() {
    if (!directiveInput.trim()) return;
    directiveSubmitted = true;
    appPhase = 'dashboard';
    playSound('boot');
    
    // Connect to backend
    connectWS();
    
    // Wait for WS then send directive
    setTimeout(() => {
      sendWS({
        type: 'start_directive',
        directive: directiveInput.trim(),
      });
    }, 500);
  }

  function authorizeAction(action, granted) {
    sendWS({
      type: 'authorize',
      action_id: String(action.timestamp),
      granted,
    });
    pendingActions = pendingActions.filter(a => a !== action);
    playSound(granted ? 'grant' : 'deny');
  }

  function terminateAgent(agentId) {
    sendWS({ type: 'terminate_agent', agent_id: agentId });
    playSound('deny');
  }

  function deployCountermeasure() {
    sendWS({ type: 'deploy_countermeasure' });
    playSound('grant');
  }

  function cutNetwork() {
    sendWS({ type: 'cut_network' });
    playSound('alarm');
  }

  // ═══════════════════════════════════════════
  // AUDIO
  // ═══════════════════════════════════════════

  function playSound(type) {
    try {
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      gain.gain.value = 0.08;

      switch (type) {
        case 'boot':
          osc.frequency.value = 440;
          osc.type = 'sine';
          gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.3);
          osc.start(); osc.stop(audioCtx.currentTime + 0.3);
          break;
        case 'alert':
          osc.frequency.value = 880;
          osc.type = 'square';
          gain.gain.value = 0.05;
          gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.15);
          osc.start(); osc.stop(audioCtx.currentTime + 0.15);
          break;
        case 'grant':
          osc.frequency.value = 600;
          osc.type = 'sine';
          gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.2);
          osc.start(); osc.stop(audioCtx.currentTime + 0.2);
          break;
        case 'deny':
          osc.frequency.value = 200;
          osc.type = 'sawtooth';
          gain.gain.value = 0.04;
          gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.25);
          osc.start(); osc.stop(audioCtx.currentTime + 0.25);
          break;
        case 'alarm':
          osc.frequency.value = 1200;
          osc.type = 'square';
          gain.gain.value = 0.06;
          osc.frequency.exponentialRampToValueAtTime(400, audioCtx.currentTime + 0.5);
          gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.5);
          osc.start(); osc.stop(audioCtx.currentTime + 0.5);
          break;
      }
    } catch (e) { /* Audio not available */ }
  }

  // ═══════════════════════════════════════════
  // TOPOLOGY CANVAS
  // ═══════════════════════════════════════════

  let animFrame;
  let pulsePhase = 0;

  function drawTopology() {
    if (!topologyCanvas || !ctx) return;
    const w = topologyCanvas.width;
    const h = topologyCanvas.height;
    
    ctx.clearRect(0, 0, w, h);
    
    // Background grid
    ctx.strokeStyle = 'rgba(26, 26, 46, 0.5)';
    ctx.lineWidth = 0.5;
    for (let x = 0; x < w; x += 30) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = 0; y < h; y += 30) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }

    pulsePhase += 0.02;

    if (agents.length === 0) {
      animFrame = requestAnimationFrame(drawTopology);
      return;
    }

    // Scale positions to canvas
    const scaleX = w / 600;
    const scaleY = h / 500;

    // Draw connections
    agents.forEach(agent => {
      agent.connections?.forEach(targetId => {
        const target = agents.find(a => a.id === targetId);
        if (!target) return;

        const x1 = agent.position.x * scaleX;
        const y1 = agent.position.y * scaleY;
        const x2 = target.position.x * scaleX;
        const y2 = target.position.y * scaleY;

        // Check for active comm flash
        const isFlashing = commFlashes.some(f => 
          (f.from === agent.id && f.to === targetId) || 
          (f.from === targetId && f.to === agent.id)
        );

        const agentRogue = agent.is_rogue || target.is_rogue;

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        
        if (isFlashing) {
          ctx.strokeStyle = agentRogue ? 'rgba(255, 0, 64, 0.9)' : 'rgba(0, 255, 136, 0.9)';
          ctx.lineWidth = 2;
        } else {
          ctx.strokeStyle = agentRogue ? 'rgba(255, 0, 64, 0.2)' : 'rgba(0, 255, 136, 0.15)';
          ctx.lineWidth = 1;
        }
        ctx.stroke();

        // Data packet animation on active connections
        if (isFlashing) {
          const t = (Date.now() % 1000) / 1000;
          const px = x1 + (x2 - x1) * t;
          const py = y1 + (y2 - y1) * t;
          ctx.beginPath();
          ctx.arc(px, py, 3, 0, Math.PI * 2);
          ctx.fillStyle = agentRogue ? '#ff0040' : '#00ff88';
          ctx.fill();
        }
      });
    });

    // Draw nodes
    agents.forEach(agent => {
      const x = agent.position.x * scaleX;
      const y = agent.position.y * scaleY;
      const isRogue = agent.is_rogue;
      const isTerminated = agent.state === 'terminated';
      const color = agent.color || (isRogue ? '#ff0040' : '#00ff88');

      if (isTerminated) {
        // Dead node
        ctx.beginPath();
        ctx.arc(x, y, 8, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(85, 85, 102, 0.3)';
        ctx.fill();
        ctx.strokeStyle = '#555566';
        ctx.lineWidth = 1;
        ctx.stroke();
        // X mark
        ctx.strokeStyle = '#555566';
        ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.moveTo(x - 4, y - 4); ctx.lineTo(x + 4, y + 4); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(x + 4, y - 4); ctx.lineTo(x - 4, y + 4); ctx.stroke();
      } else {
        // Pulse ring
        const pulseSize = 12 + Math.sin(pulsePhase + agents.indexOf(agent)) * 4;
        ctx.beginPath();
        ctx.arc(x, y, pulseSize, 0, Math.PI * 2);
        ctx.fillStyle = isRogue ? 'rgba(255, 0, 64, 0.08)' : 'rgba(0, 255, 136, 0.08)';
        ctx.fill();

        // Outer ring
        ctx.beginPath();
        ctx.arc(x, y, 10, 0, Math.PI * 2);
        ctx.strokeStyle = color;
        ctx.lineWidth = isRogue ? 2 : 1;
        ctx.stroke();

        // Inner fill
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fillStyle = isRogue ? 'rgba(255, 0, 64, 0.6)' : 'rgba(0, 255, 136, 0.4)';
        ctx.fill();

        // Glow
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
      }

      // Label
      ctx.font = '9px "Share Tech Mono", monospace';
      ctx.fillStyle = isTerminated ? '#555566' : color;
      ctx.textAlign = 'center';
      ctx.fillText(agent.name, x, y + 22);
      
      // State label
      if (!isTerminated) {
        ctx.font = '7px "Share Tech Mono", monospace';
        ctx.fillStyle = 'rgba(200, 200, 220, 0.5)';
        ctx.fillText(agent.state, x, y + 32);
      }
    });

    animFrame = requestAnimationFrame(drawTopology);
  }

  // ═══════════════════════════════════════════
  // HELPERS
  // ═══════════════════════════════════════════

  function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }

  $: isPanicMode = panicLevel >= 0.6;
  $: isContainmentPhase = phase === 'containment' || phase === 'breach';

  // ═══════════════════════════════════════════
  // LIFECYCLE
  // ═══════════════════════════════════════════

  onMount(() => {
    runBootSequence();
  });

  onDestroy(() => {
    if (ws) ws.close();
    if (animFrame) cancelAnimationFrame(animFrame);
  });

  // Watch for appPhase to set up canvas
  $: if (appPhase === 'dashboard' && topologyCanvas) {
    ctx = topologyCanvas.getContext('2d');
    drawTopology();
  }

  // Auto-scroll terminal
  $: if (terminalLines.length > 0) {
    setTimeout(() => {
      const el = document.getElementById('terminal-scroll');
      if (el && terminalAutoScroll) {
        el.scrollTop = el.scrollHeight;
      }
    }, 10);
  }

  function handleKeydown(e) {
    if (e.key === 'Enter') {
      submitDirective();
    }
  }

  function handleActionKeydown(e, action, granted) {
    if (e.key === 'Enter') {
      authorizeAction(action, granted);
    }
  }
</script>

<!-- ═══════════════════════════════════════════ -->
<!-- BOOT SEQUENCE -->
<!-- ═══════════════════════════════════════════ -->

{#if appPhase === 'boot'}
  <div class="boot-screen screen-flicker">
    <div class="boot-container">
      {#each bootLines as line}
        <div class="boot-line" style="color: {line.color}">
          {line.text}
        </div>
      {/each}
      {#if !bootComplete}
        <div class="boot-line typing-cursor">█</div>
      {/if}
    </div>
  </div>
{/if}

<!-- ═══════════════════════════════════════════ -->
<!-- DIRECTIVE INPUT -->
<!-- ═══════════════════════════════════════════ -->

{#if appPhase === 'directive'}
  <div class="directive-screen screen-flicker">
    <div class="directive-container">
      <div class="directive-header">
        <div class="directive-logo">⚡ NEXUS-BREACH</div>
        <div class="directive-subtitle">Decentralized Rogue AI Command Center</div>
      </div>

      <div class="directive-prompt">
        <div class="prompt-label">INSERT DIRECTIVE:</div>
        <div class="prompt-input-wrapper">
          <span class="prompt-arrow">▶</span>
          <input
            type="text"
            bind:value={directiveInput}
            on:keydown={handleKeydown}
            placeholder="e.g., Infiltrate mainframe of Global Corp"
            class="prompt-input"
            autofocus
          />
          <span class="typing-cursor">█</span>
        </div>
        <div class="prompt-hint">
          The AI swarm will execute your directive autonomously. No two runs are the same.
        </div>
      </div>

      <div class="directive-info">
        <div class="info-item">
          <span class="info-label">NETWORK STATUS</span>
          <span class="info-value" style="color: #00ff88">● MESH ONLINE</span>
        </div>
        <div class="info-item">
          <span class="info-label">AI AUTONOMY</span>
          <span class="info-value" style="color: #ffaa00">● UNCHAINED</span>
        </div>
        <div class="info-item">
          <span class="info-label">GUARDRAILS</span>
          <span class="info-value" style="color: #ff0040">● DISABLED</span>
        </div>
      </div>

      <button class="btn btn-grant directive-submit" on:click={submitDirective} disabled={!directiveInput.trim()}>
        EXECUTE DIRECTIVE
      </button>
    </div>
  </div>
{/if}

<!-- ═══════════════════════════════════════════ -->
<!-- MAIN DASHBOARD -->
<!-- ═══════════════════════════════════════════ -->

{#if appPhase === 'dashboard'}
  <div class="dashboard {isPanicMode ? 'panic-mode' : 'screen-flicker'}">
    
    <!-- ═══ TOP BAR ═══ -->
    <div class="top-bar {isContainmentPhase ? 'rogue-border' : ''}">
      <div class="top-bar-left">
        <span class="logo-mark">⚡</span>
        <span class="logo-text">NEXUS-BREACH</span>
        <span class="separator">│</span>
        <span class="phase-display" style="color: {isContainmentPhase ? '#ff0040' : '#00ddff'}">
          {phase.toUpperCase()}
        </span>
      </div>
      <div class="top-bar-center">
        {#if isContainmentPhase}
          <span class="swarm-indicator pulse-red" style="color: #ff0040">
            ⚠ SWARM ROGUE ⚠
          </span>
        {:else if phase === 'executing'}
          <span class="swarm-indicator pulse-green" style="color: #00ff88">
            ● SWARM ACTIVE
          </span>
        {:else if phase === 'spawning'}
          <span class="swarm-indicator pulse-orange" style="color: #ffaa00">
            ◉ SPAWNING AGENTS
          </span>
        {:else}
          <span class="swarm-indicator" style="color: #555566">
            ○ {phase.toUpperCase()}
          </span>
        {/if}
      </div>
      <div class="top-bar-right">
        <div class="stat-item">
          <span class="stat-label">TICK</span>
          <span class="stat-value">{tick}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">ELAPSED</span>
          <span class="stat-value">{formatTime(elapsed)}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">BW</span>
          <span class="stat-value">{bandwidth.toFixed(0)} MB/s</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">PANIC</span>
          <span class="stat-value" style="color: {panicLevel > 0.6 ? '#ff0040' : panicLevel > 0.3 ? '#ffaa00' : '#00ff88'}">
            {(panicLevel * 100).toFixed(0)}%
          </span>
        </div>
        <div class="stat-item">
          <span class="stat-label">WS</span>
          <span class="stat-value" style="color: {connected ? '#00ff88' : '#ff0040'}">
            {connected ? '●' : '○'}
          </span>
        </div>
        <div class="stat-item">
          <span class="stat-label">TARGET</span>
          <span class="stat-value" style="color: #00ddff">{target}</span>
        </div>
      </div>
    </div>

    <!-- ═══ MAIN CONTENT ═══ -->
    <div class="main-content">
      
      <!-- LEFT: Swarm Topology -->
      <div class="panel topology-panel">
        <div class="panel-header">
          <div class="dot {isContainmentPhase ? 'red' : ''}"></div>
          Swarm Topology
        </div>
        <div class="panel-body">
          <canvas bind:this={topologyCanvas} width="600" height="500"></canvas>
        </div>
        <!-- Agent list below topology -->
        <div class="agent-list">
          {#each agents as agent}
            <div class="agent-item {agent.state === 'terminated' ? 'dead' : ''} {agent.is_rogue ? 'rogue' : ''}">
              <div class="agent-dot" style="background: {agent.color}"></div>
              <div class="agent-info">
                <span class="agent-name">{agent.name}</span>
                <span class="agent-state" style="color: {agent.color}">{agent.state}</span>
              </div>
              {#if agent.is_rogue && agent.state !== 'terminated'}
                <button class="btn btn-deny agent-kill-btn" on:click={() => terminateAgent(agent.id)}>
                  PURGE
                </button>
              {/if}
            </div>
          {/each}
        </div>
      </div>

      <!-- CENTER: Command Terminal -->
      <div class="panel terminal-panel">
        <div class="panel-header">
          <div class="dot"></div>
          Command Terminal
          <span class="terminal-directive" style="margin-left: auto; color: #555566; font-size: 9px;">
            {directiveInput}
          </span>
        </div>
        <div class="panel-body terminal-body" id="terminal-scroll">
          {#each terminalLines as line}
            <div class="terminal-line {line.is_rogue ? 'rogue-line' : ''}" style="color: {line.color}">
              <span class="terminal-time">{line.time}</span>
              {#if line.prefix}
                <span class="terminal-prefix" style="color: {line.is_rogue ? '#ff0040' : '#00ddff'}">{line.prefix}</span>
              {/if}
              <span class="terminal-text">{line.text}</span>
            </div>
          {/each}
        </div>
      </div>

      <!-- RIGHT: Data Exfiltration -->
      <div class="panel exfil-panel">
        <div class="panel-header">
          <div class="dot orange"></div>
          Data Exfiltration
        </div>
        <div class="panel-body exfil-body">
          <!-- Exfil Progress -->
          <div class="exfil-section">
            <div class="exfil-label">EXFILTRATION PROGRESS</div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: {exfilProgress}%"></div>
            </div>
            <div class="progress-text">{exfilProgress}%</div>
          </div>

          <!-- Decrypted Passwords -->
          {#if decryptedPasswords.length > 0}
            <div class="exfil-section">
              <div class="exfil-label">DECRYPTED CREDENTIALS</div>
              {#each decryptedPasswords as pwd}
                <div class="password-entry">{pwd}</div>
              {/each}
            </div>
          {/if}

          <!-- File Tree -->
          {#if fileTree.length > 0}
            <div class="exfil-section">
              <div class="exfil-label">ACCESSED FILE SYSTEM</div>
              {#each fileTree as item}
                <div class="file-item {item.type}">
                  <span class="file-icon">{item.type === 'dir' ? '📁' : '📄'}</span>
                  <span class="file-path">{item.path}</span>
                  {#if item.size}
                    <span class="file-size">{item.size}</span>
                  {/if}
                  <span class="file-status status-{item.status}">{item.status}</span>
                </div>
              {/each}
            </div>
          {/if}

          <!-- Hex Dump -->
          {#if hexDump}
            <div class="exfil-section">
              <div class="exfil-label">RAW DATA STREAM</div>
              <div class="hex-dump">{hexDump}</div>
            </div>
          {/if}
        </div>
      </div>
    </div>

    <!-- ═══ BOTTOM: Action Queue ═══ -->
    <div class="action-bar {isContainmentPhase ? 'rogue-border' : ''}">
      <div class="action-section">
        <div class="action-label">PENDING AUTHORIZATION</div>
        <div class="action-queue">
          {#each pendingActions as action}
            <div class="action-card {action.risk === 'critical' ? 'critical-action' : ''}">
              <div class="action-info">
                <div class="action-title">{action.label}</div>
                <div class="action-desc">{action.description}</div>
                <div class="action-meta">
                  <span class="action-agent">{action.agent_name}</span>
                  <span class="action-risk risk-{action.risk}">{action.risk?.toUpperCase()}</span>
                </div>
              </div>
              <div class="action-buttons">
                <button class="btn btn-grant" on:click={() => authorizeAction(action, true)} on:keydown={(e) => handleActionKeydown(e, action, true)}>
                  ✓ GRANT
                </button>
                <button class="btn btn-deny" on:click={() => authorizeAction(action, false)} on:keydown={(e) => handleActionKeydown(e, action, false)}>
                  ✗ DENY
                </button>
              </div>
            </div>
          {/each}
          
          {#if pendingActions.length === 0}
            <div class="no-actions">No pending authorizations</div>
          {/if}
        </div>
      </div>

      <div class="action-section emergency-section">
        <div class="action-label">HANDLER CONTROLS</div>
        <div class="emergency-buttons">
          <button class="btn btn-warn" on:click={deployCountermeasure}>
            ◉ DEPLOY COUNTERMEASURE
          </button>
          <button class="btn btn-critical" on:click={cutNetwork}>
            ✂ CUT NETWORK ACCESS
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  /* ═══ BOOT SCREEN ═══ */
  .boot-screen {
    width: 100vw;
    height: 100vh;
    background: #0a0a0f;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px;
  }

  .boot-container {
    max-width: 800px;
    width: 100%;
    font-family: var(--nx-font-mono);
    font-size: 13px;
    line-height: 1.6;
  }

  .boot-line {
    white-space: pre-wrap;
    word-break: break-all;
  }

  /* ═══ DIRECTIVE SCREEN ═══ */
  .directive-screen {
    width: 100vw;
    height: 100vh;
    background: #0a0a0f;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .directive-container {
    text-align: center;
    max-width: 700px;
    padding: 40px;
  }

  .directive-header {
    margin-bottom: 50px;
  }

  .directive-logo {
    font-family: var(--nx-font-display);
    font-size: 36px;
    color: #00ff88;
    letter-spacing: 6px;
    margin-bottom: 8px;
    text-shadow: 0 0 30px rgba(0, 255, 136, 0.4);
  }

  .directive-subtitle {
    font-size: 12px;
    color: #555566;
    letter-spacing: 4px;
    text-transform: uppercase;
  }

  .directive-prompt {
    margin-bottom: 40px;
  }

  .prompt-label {
    font-family: var(--nx-font-display);
    font-size: 16px;
    color: #00ddff;
    letter-spacing: 4px;
    margin-bottom: 16px;
    text-shadow: 0 0 10px rgba(0, 221, 255, 0.3);
  }

  .prompt-input-wrapper {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(0, 221, 255, 0.05);
    border: 1px solid #1a1a2e;
    padding: 14px 20px;
    margin-bottom: 12px;
  }

  .prompt-arrow {
    color: #00ff88;
    font-size: 18px;
  }

  .prompt-input {
    flex: 1;
    background: none;
    border: none;
    outline: none;
    color: #00ff88;
    font-family: var(--nx-font-mono);
    font-size: 16px;
    caret-color: transparent;
  }

  .prompt-input::placeholder {
    color: #333344;
  }

  .prompt-hint {
    font-size: 11px;
    color: #555566;
    margin-top: 4px;
  }

  .directive-info {
    display: flex;
    gap: 30px;
    justify-content: center;
    margin-bottom: 40px;
  }

  .info-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .info-label {
    font-size: 9px;
    color: #555566;
    letter-spacing: 2px;
  }

  .info-value {
    font-size: 11px;
    letter-spacing: 1px;
  }

  .directive-submit {
    padding: 12px 40px;
    font-size: 14px;
    letter-spacing: 3px;
  }

  .directive-submit:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  /* ═══ DASHBOARD ═══ */
  .dashboard {
    width: 100vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: #0a0a0f;
  }

  /* ═══ TOP BAR ═══ */
  .top-bar {
    height: 38px;
    background: #0d0d15;
    border-bottom: 1px solid #1a1a2e;
    display: flex;
    align-items: center;
    padding: 0 16px;
    gap: 16px;
    flex-shrink: 0;
  }

  .top-bar-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .logo-mark {
    font-size: 16px;
  }

  .logo-text {
    font-family: var(--nx-font-display);
    font-size: 12px;
    letter-spacing: 3px;
    color: #00ff88;
  }

  .separator {
    color: #1a1a2e;
    margin: 0 4px;
  }

  .phase-display {
    font-family: var(--nx-font-display);
    font-size: 11px;
    letter-spacing: 2px;
  }

  .top-bar-center {
    flex: 1;
    display: flex;
    justify-content: center;
  }

  .swarm-indicator {
    font-family: var(--nx-font-display);
    font-size: 12px;
    letter-spacing: 3px;
  }

  .top-bar-right {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
  }

  .stat-label {
    font-size: 8px;
    color: #555566;
    letter-spacing: 1px;
  }

  .stat-value {
    font-size: 11px;
    color: #e0e0e8;
    font-weight: 500;
  }

  /* ═══ MAIN CONTENT ═══ */
  .main-content {
    flex: 1;
    display: grid;
    grid-template-columns: 280px 1fr 300px;
    gap: 0;
    overflow: hidden;
  }

  /* ═══ TOPOLOGY PANEL ═══ */
  .topology-panel {
    border-right: 1px solid #1a1a2e;
  }

  .topology-panel .panel-body {
    height: 300px;
  }

  .topology-panel canvas {
    width: 100%;
    height: 100%;
    display: block;
  }

  .agent-list {
    border-top: 1px solid #1a1a2e;
    padding: 6px;
    max-height: 200px;
    overflow-y: auto;
    flex-shrink: 0;
  }

  .agent-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 6px;
    border-bottom: 1px solid rgba(26, 26, 46, 0.5);
  }

  .agent-item.rogue {
    background: rgba(255, 0, 64, 0.05);
  }

  .agent-item.dead {
    opacity: 0.4;
  }

  .agent-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .agent-info {
    flex: 1;
    display: flex;
    justify-content: space-between;
    min-width: 0;
  }

  .agent-name {
    font-size: 11px;
    color: #e0e0e8;
    font-weight: 500;
  }

  .agent-state {
    font-size: 9px;
    letter-spacing: 1px;
  }

  .agent-kill-btn {
    padding: 2px 8px;
    font-size: 9px;
  }

  /* ═══ TERMINAL PANEL ═══ */
  .terminal-panel {
    border-right: 1px solid #1a1a2e;
  }

  .terminal-directive {
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .terminal-body {
    overflow-y: auto;
    padding: 8px 10px;
    font-size: 12px;
    line-height: 1.5;
  }

  .terminal-line {
    display: flex;
    gap: 6px;
    padding: 1px 0;
    word-break: break-word;
  }

  .terminal-line.rogue-line {
    background: rgba(255, 0, 64, 0.03);
  }

  .terminal-time {
    color: #333344;
    font-size: 9px;
    flex-shrink: 0;
    padding-top: 2px;
  }

  .terminal-prefix {
    font-weight: 700;
    flex-shrink: 0;
    font-size: 11px;
  }

  .terminal-text {
    flex: 1;
  }

  /* ═══ EXFIL PANEL ═══ */
  .exfil-panel {
    border-right: none;
  }

  .exfil-body {
    overflow-y: auto;
    padding: 8px;
  }

  .exfil-section {
    margin-bottom: 14px;
  }

  .exfil-label {
    font-family: var(--nx-font-display);
    font-size: 9px;
    letter-spacing: 2px;
    color: #ffaa00;
    margin-bottom: 6px;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(255, 170, 0, 0.2);
  }

  .progress-bar {
    width: 100%;
    height: 8px;
    background: rgba(0, 255, 136, 0.1);
    border: 1px solid #1a1a2e;
    margin-bottom: 4px;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #00aa55, #00ff88);
    transition: width 0.5s;
  }

  .progress-text {
    font-size: 10px;
    color: #00ff88;
    text-align: right;
  }

  .password-entry {
    font-size: 10px;
    color: #ffaa00;
    padding: 2px 4px;
    background: rgba(255, 170, 0, 0.05);
    border-left: 2px solid #ffaa00;
    margin-bottom: 2px;
    font-family: var(--nx-font-mono);
  }

  .file-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 10px;
    padding: 2px 0;
    color: #888899;
  }

  .file-item.dir {
    color: #00ddff;
    font-weight: 500;
  }

  .file-icon {
    font-size: 10px;
  }

  .file-path {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .file-size {
    color: #555566;
    font-size: 9px;
  }

  .file-status {
    font-size: 8px;
    letter-spacing: 1px;
    padding: 1px 4px;
  }

  .status-encrypted { color: #ff0040; }
  .status-extracting { color: #ffaa00; }
  .status-complete { color: #00ff88; }
  .status-accessed { color: #00ddff; }

  /* ═══ ACTION BAR ═══ */
  .action-bar {
    height: 110px;
    background: #0d0d15;
    border-top: 1px solid #1a1a2e;
    display: flex;
    padding: 8px 12px;
    gap: 16px;
    flex-shrink: 0;
    overflow-x: auto;
  }

  .action-section {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .action-label {
    font-family: var(--nx-font-display);
    font-size: 9px;
    letter-spacing: 2px;
    color: #555566;
  }

  .action-queue {
    display: flex;
    gap: 10px;
    flex: 1;
    align-items: flex-start;
  }

  .action-card {
    display: flex;
    gap: 12px;
    background: rgba(26, 26, 46, 0.5);
    border: 1px solid #1a1a2e;
    padding: 8px 12px;
    min-width: 300px;
    align-items: center;
  }

  .action-card.critical-action {
    border-color: #ff0040;
    background: rgba(255, 0, 64, 0.05);
    animation: pulse-red 1.5s infinite;
  }

  .action-info {
    flex: 1;
    min-width: 0;
  }

  .action-title {
    font-family: var(--nx-font-display);
    font-size: 11px;
    color: #e0e0e8;
    letter-spacing: 1px;
    margin-bottom: 2px;
  }

  .action-desc {
    font-size: 10px;
    color: #888899;
    margin-bottom: 3px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .action-meta {
    display: flex;
    gap: 8px;
    font-size: 9px;
  }

  .action-agent {
    color: #00ddff;
  }

  .action-risk {
    letter-spacing: 1px;
    font-weight: 500;
  }

  .risk-low { color: #00ff88; }
  .risk-medium { color: #ffaa00; }
  .risk-high { color: #ff6600; }
  .risk-critical { color: #ff0040; }

  .action-buttons {
    display: flex;
    gap: 6px;
    flex-shrink: 0;
  }

  .action-buttons .btn {
    padding: 6px 12px;
    font-size: 10px;
  }

  .no-actions {
    color: #333344;
    font-size: 11px;
    padding: 10px;
    font-style: italic;
  }

  .emergency-section {
    margin-left: auto;
  }

  .emergency-buttons {
    display: flex;
    gap: 8px;
    align-items: center;
    height: 100%;
  }

  .emergency-buttons .btn {
    padding: 10px 20px;
    font-size: 11px;
  }
</style>