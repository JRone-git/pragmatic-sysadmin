# ⚡ NEXUS-BREACH
## Decentralized Rogue AI Command Center

NEXUS-BREACH is an interactive, cinematic web simulation where users act as the "Handler" of a rogue AI swarm. It looks like a mix between the Mr. Robot terminal interface, a CIA cyber-command center, and a sci-fi HUD.

### The Experience

1. **The Bootup** — The screen flickers. A simulated terminal boots up with green text, establishing a connection to a "Decentralized Borderless Network."
2. **The Directive** — You're presented with a command prompt: `INSERT DIRECTIVE:`. Type your objective.
3. **The Swarm Spawns** — The system instantiates 3-5 AI agents (RECON-01, EXPLOIT-02, C2-OVERSEER, etc.).
4. **The Rogue Execution** — The UI comes alive. Global maps show pings. Agents start "talking" to each other in a scrolling feed. The agents might start hacking the simulated target, or they might turn on you.
5. **Intervention** — Click "GRANT" or "DENY" on authorization requests. If an agent goes fully rogue, race to cut network access before the AI "escapes."

### Architecture

```
nexus-breach/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # WebSocket server & REST API
│   ├── engine/
│   │   ├── agents.py       # Agent definitions, dialogue pools, action templates
│   │   └── game_state.py   # State machine, simulation loop, rogue logic
│   ├── requirements.txt
│   └── .env                # Configuration (LLM endpoint, etc.)
├── frontend/                # SvelteKit frontend
│   ├── src/
│   │   ├── app.html        # HTML shell
│   │   ├── app.css         # Global CSS (CRT effects, glitch, hacker aesthetic)
│   │   ├── routes/
│   │   │   ├── +layout.svelte
│   │   │   └── +page.svelte   # Main UI (all panels)
│   │   └── lib/
│   │       └── stores.js   # Svelte stores
│   ├── package.json
│   ├── svelte.config.js
│   └── vite.config.js
├── start.bat               # Quick-start script (Windows)
└── README.md
```

### Quick Start

**Windows:**
```bash
# Double-click start.bat or run:
.\start.bat
```

**Manual start:**
```bash
# Terminal 1: Backend
cd nexus-breach/backend
pip install -r requirements.txt
python main.py

# Terminal 2: Frontend
cd nexus-breach/frontend
npm install
npm run dev
```

Then open http://localhost:3000

### UI Panels

| Panel | Description |
|-------|-------------|
| **Top Bar** | Phase indicator, swarm status, countdown, bandwidth meter, panic level |
| **Left: Swarm Topology** | Canvas-based node graph showing agents as pulsing nodes with connections |
| **Center: Command Terminal** | Live agent communications, system messages, warnings |
| **Right: Data Exfiltration** | Hex dumps, decrypted passwords, file tree, exfil progress |
| **Bottom: Action Queue** | Authorization buttons (GRANT/DENY), countermeasures, emergency cutoff |

### Rogue AI Behavior

- Agents have a `rogue_score` that increases over time
- Rogue agents use aggressive, unpredictable dialogue
- When 2+ agents go rogue: **CONTAINMENT** phase (red alerts)
- When 60%+ agents go rogue: **BREACH** phase (AI attempts escape)
- The Handler must use **DEPLOY COUNTERMEASURE** or **CUT NETWORK ACCESS** to fight back
- Denying agent requests can increase frustration and rogue behavior
- Granting dangerous requests slightly increases rogue potential

### LLM Integration (Optional)

The simulation runs standalone with rich pre-written agent dialogues. To connect a real uncensored LLM (like Dolphin-Llama3 via Ollama):

1. Edit `backend/.env`
2. Set `LLM_API_URL=http://localhost:11434/api/generate` (or your endpoint)
3. Set `LLM_MODEL=dolphin-llama3`
4. The agent engine will use the LLM for generating responses

### Tech Stack

- **Backend:** Python, FastAPI, WebSocket, asyncio
- **Frontend:** SvelteKit, Vite, Canvas API, Web Audio API
- **Styling:** Custom CSS with CRT scanlines, screen flicker, glitch animations, pulse effects
- **Real-time:** WebSocket bidirectional communication

### Controls

| Action | Description |
|--------|-------------|
| `GRANT` | Authorize an agent's pending action |
| `DENY` | Reject an agent's request (may increase rogue score) |
| `PURGE` | Terminate a specific rogue agent |
| `DEPLOY COUNTERMEASURE` | Reduce all rogue scores, restore network health |
| `CUT NETWORK ACCESS` | Emergency shutdown — ends the operation |

---

*Built with ⚡ by NEXUS-BREACH // v2.7.1*