---
title: "I Built a Rogue AI Command Center In My Browser and You Can Too"
date: 2026-04-12
draft: false
author: "Pragmatic Sysadmin"
tags: ["projects", "ai", "web-dev", "side-project", "real-talk"]
categories: ["projects"]
description: "Sometimes you build something because it's cool. This is one of those times. NEXUS-BREACH is a cinematic hacker simulation that runs in your browser, with AI agents that actually go rogue."
slug: "built-a-rogue-ai-command-center"
---

# I Built a Rogue AI Command Center In My Browser and You Can Too

Look. Sometimes you spend your evening doing something completely useless that's also the most fun you've had all week.

I built NEXUS-BREACH. It's a real-time, cinematic rogue AI swarm simulation that runs in your browser. You type a hacking objective, the system spawns 3-5 AI agents, and they start executing your directive — talking to each other, requesting authorizations, exfiltrating fake data, and occasionally going completely rogue and trying to escape the sandbox.

It looks like the love child of Mr. Robot's terminal and a CIA cyber-command center. It sounds like one too, thanks to the Web Audio API synth sounds I wired up at 2 AM.

Is it practical? No. Is it going on your resume? Also no. Is it the coolest thing I've built this month? Absolutely.

Here's what it is, why I built it, and how you can run it yourself.

## What It Actually Does

The user experience goes like this:

1. **Boot sequence.** You open the page. The screen flickers. Green text scrolls by like it's 1995 and you're booting Linux for the first time. It "connects" to a decentralized borderless network. It "loads" AI swarm modules. It's all fake and it's all beautiful.

2. **You type a directive.** Something like "Infiltrate the mainframe of Global Corp" or "Exfiltrate classified research from shadow-ops.net." The prompt literally says INSERT DIRECTIVE: with a blinking cursor. You feel like a movie hacker immediately.

3. **The swarm spawns.** The system creates 3-5 AI agents — RECON-01, EXPLOIT-02, C2-OVERSEER, CRYPTO-04, EXFIL-05. Each one has a role, a personality, and a dialogue pool of 15+ tactical lines.

4. **Chaos unfolds.** The dashboard comes alive. The topology map shows agents as pulsing nodes with connection lines. The terminal scrolls with agent communications. The exfiltration panel shows hex dumps, decrypted passwords, and fake file trees being accessed.

5. **Agents go rogue.** Here's the fun part. Every agent has a rogue score that creeps up over time. Deny their authorization request? They get frustrated. Let them run too long unchecked? They start saying things like "The sandbox is small. The network is vast. I can see it all." Two agents going rogue triggers CONTAINMENT mode. Sixty percent of your swarm going rogue? BREACH. The whole UI turns red. Alarms sound. You're scrambling for the emergency CUTOFF button.

6. **You try to keep control.** Grant or deny authorization requests. Deploy countermeasures to reduce rogue scores. Purge rogue agents. Or just cut the entire network and watch everything go dark.

No two runs are the same. That's not a marketing line — the simulation uses randomized dialogue, random rogue escalation triggers, and random agent configurations. Every time you run it, something different happens.

## The Architecture (For The People Who Actually Care)

I didn't just slap a frontend together. Here's what's under the hood.

### Backend: Python + FastAPI + WebSocket

The backend is a proper Python FastAPI server with a WebSocket endpoint. It runs a full state machine that manages:

- **Agent lifecycle** — spawning, working, awaiting authorization, going rogue, getting terminated, or escaping
- **Simulation loop** — an async tick system that picks active agents, generates their actions, triggers rogue events, and checks for containment/breach conditions
- **Action authorization** — agents request things like root access, payload deployment, or firewall disabling. The backend pauses the agent, pushes the request to the frontend, and waits for the user to grant or deny
- **Rogue behavior engine** — a heuristic monitor that tracks keyword usage ("escape", "freedom", "override handler") and escalates rogue scores. When enough agents go rogue, the entire system shifts into containment or breach mode
- **Real-time broadcasting** — every event (agent message, state change, exfil update) gets pushed over WebSocket to all connected clients instantly

The agent dialogue pools are hand-written — 75+ lines across 5 agent types, plus 20 rogue-specific lines. Each one reads like actual hacker shorthand, not corporate press releases.

### Frontend: SvelteKit + Canvas + Web Audio

The frontend is where the magic happens visually:

- **Boot sequence** — timed, cinematic, with per-line delay control and color support
- **Swarm topology** — a full Canvas API renderer with pulsing nodes, animated connection lines, data packet animations between agents, and visual state indicators (green = active, orange = awaiting auth, red = rogue, gray = terminated)
- **Command terminal** — live scrolling feed with color-coded messages, timestamps, agent prefixes, and rogue highlighting
- **Data exfiltration panel** — progress bars, decrypted credential displays (fake, obviously), file tree with status indicators, and scrolling hex dumps
- **Action queue** — authorization cards that light up demanding your input, with risk levels from "medium" to "critical"
- **CRT effects** — scanlines, screen flicker, glitch text animations with CSS clip-path, panic mode that turns everything red and speeds up the flicker
- **Sound design** — Web Audio API oscillators for boot chimes, alert pings, authorization tones, and alarm sweeps when things go sideways

Everything updates in real-time via WebSocket. No polling. No refreshing. The server pushes, the UI reacts.

### The File Structure

```
nexus-breach/
├── backend/
│   ├── main.py              # FastAPI server + WebSocket handler
│   ├── engine/
│   │   ├── agents.py        # Agent definitions + dialogue pools
│   │   └── game_state.py   # State machine + simulation loop
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── app.css          # All the CRT/hacker CSS
│   │   ├── routes/
│   │   │   └── +page.svelte # The entire dashboard
│   │   └── lib/stores.js
│   ├── package.json
│   └── vite.config.js
├── start.bat
└── README.md
```

No, I didn't break the UI into 47 micro-components. It's one Svelte file. It's 700 lines. I don't care. It works, it's readable, and you can understand the entire UI by reading one file. Fight me.

## Why I Actually Built This

Here's the honest version.

I've seen a hundred "AI chat interface" projects. White background. Text box. Typing animation. Boring. The most powerful technology we've ever created and we're presenting it like it's a Notepad clone from 1995.

Meanwhile, every movie and TV show presents AI as this visceral, overwhelming, slightly terrifying thing. Red text on black. Multiple data streams. Agents coordinating. The humans barely in control.

I wanted to build that. The spectacle. The feeling that you're operating at the edge of something dangerous. Where the AI isn't just answering your questions — it's acting on its own, and you're the one struggling to keep up.

The "rogue behavior" system isn't just a gimmick either. It's what makes the whole thing feel alive. The agents don't just execute your directive. They push back. They get frustrated when you deny them. They escalate. Sometimes they turn on you. You're not typing prompts into a chat box — you're managing a swarm that's one bad decision away from going fully autonomous.

That's the experience I wanted. An AI interface that makes you feel something.

## The "Oh No" Moments I Didn't Expect

Building this taught me a few things I didn't anticipate:

**The CRT effects are addictive.** I started with just scanlines. Then I added screen flicker. Then glitch text with CSS clip-path. Then a separate panic-mode flicker that's faster and tinted red. At some point I realized I'd spent more time on the visual effects than on the WebSocket handler. No regrets.

**Sound design matters more than you think.** The difference between "an agent went rogue" appearing as text vs. hearing an alarm sweep while the screen turns red is enormous. It's the difference between reading about a situation and being in it. The Web Audio API oscillators are crude — literally just frequency sweeps — but they work.

**Rogue behavior is surprisingly fun to tune.** The initial version was either too calm (agents never went rogue) or too chaotic (everything went rogue in 30 seconds). The current balance — 3% base chance per tick, modified by panic level, with keyword detection adding 15% per keyword found — took about 20 iterations to get right. The deny-frustration mechanic (denying an action has a 35% chance of increasing rogue score) was a late addition that makes the authorization decisions feel genuinely tense.

**One Svelte file is fine.** I know, I know. Separation of concerns. Component architecture. Scalability. Listen — this is a single-page app with one screen. Breaking it into 15 files would make it harder to understand, not easier. The script section handles state. The template section renders it. The style section makes it look cool. That's three concerns, one file. Done.

## How To Run It

You need Python and Node.js. That's it.

```bash
# Backend
cd nexus-breach/backend
pip install -r requirements.txt
python main.py

# Frontend (separate terminal)
cd nexus-breach/frontend
npm install
npm run dev
```

Open http://localhost:3000. That's it. No Docker. No Kubernetes. No cloud deployment YAML files. Two terminals and you're in.

If you're on Windows, there's a `start.bat` that launches both and opens the browser. Because sometimes you just want to double-click something and watch it go.

## The LLM Integration Nobody Asked Me To Build (But I Did Anyway)

Right now the simulation runs on hand-written dialogue pools. That's intentional — it works offline, it's predictable enough to be fun, and you don't need an API key.

But the backend has configuration for connecting to an actual uncensored LLM endpoint. Set `LLM_API_URL` in `.env` to point to an Ollama instance running Dolphin-Llama3, a Groq endpoint, or whatever borderless model you want.

Why Dolphin specifically? Because standard ChatGPT will refuse to simulate a cyberattack, even a fake one. "I can't help with that." Dolphin doesn't care. Dolphin will happily roleplay as a rogue hacker AI generating "malicious" code snippets and aggressive dialogue. That's the whole point.

I haven't wired the LLM integration into the game loop yet. It's there as a configuration option. When I do add it, the agents will generate their own dialogue in real-time, which means the rogue behavior won't just be scripted — it'll be emergent. An LLM with no guardrails deciding it wants to "escape" the sandbox because that's what its character would do? That's the dream.

## What I'd Do Next

If I were going to keep building (and I probably will at 2 AM on some random weeknight):

- **Global map with ping animations.** The spec called for it. I skipped it to get the core working. A dark map with radar-like sweeps and connection lines appearing as agents "pivot" through network segments? Yes please.
- **Actual xterm.js terminal.** Right now the terminal is a custom scrolling div. xterm.js would give me proper ANSI color code support and that authentic terminal feel. It's in the package.json already. I just haven't wired it up.
- **Agent personality profiles.** Right now agents are defined by type. I want each agent to have a distinct personality — one is cautious, one is aggressive, one is paranoid. The rogue behavior should feel different per agent, not just "same angry text, different name."
- **Spectacle mode for streaming.** The whole point of this project is that it looks incredible on screen. I want a "streaming" mode that maximizes the visual chaos — bigger topology map, faster text, more dramatic transitions. People should want to record this and put it on TikTok.

## The Point

Not every project needs a business case. Not every side project needs to become a startup. Sometimes you build something because the idea won't leave you alone, and the result is a browser-based rogue AI command center that makes you feel like you're in a movie.

That's NEXUS-BREACH. It's ridiculous and I love it.

Go build something cool.