---
title: "I Built My Own J.A.R.V.I.S. — A Local, Privacy-First Multi-Agent AI Assistant"
date: 2026-08-15
author: Pragmatic Sysadmin
description: "I designed and started building a fully local, multi-agent AI system that runs on my Linux desktop. Ollama as the brain, Docker containers for each agent, function calling for orchestration, and nothing leaves my network. Here's the architecture."
draft: false
tags: ["ai", "self-hosted", "linux", "home-lab", "ollama", "privacy", "agents"]
slug: i-built-my-own-jarvis-local-multi-agent-ai-assistant
topics: ["ai", "self-hosted", "linux"]
resources:
  - name: ollama
    url: https://ollama.com
    description: Ollama — run LLMs locally
  - name: home-assistant
    url: https://www.home-assistant.io
    description: Home Assistant — smart home platform
---

I wanted a personal AI assistant. Not a chatbot. Not a copilot. Something that actually *does things* — controls my desktop, reads my screen, talks to my smart home, answers questions in Finnish or English, and never, ever sends my data to a server I don't control.

The cloud options are good. They're not *mine*.

So I started building one.

This post is the architecture document for that project. It's a work in progress — the docker-compose is ready, the Ollama instance is running, and the first agent is next. I'm writing this because the design decisions are interesting, and because someone else might want to build the same thing.

<!--more-->

## What J.A.R.V.I.S. Is (And Isn't)

This isn't a Jarvis like Tony Stark's. It's closer to a privacy-respecting home automation brain — or what you'd get if you crossed a really good CLI assistant with a smart home hub and gave it eyes.

The core idea: a lightweight orchestrator (Ollama) decides *what to do*. Specialized agents handle *how to do it*. Each agent runs in its own Docker container. Everything stays on my local network.

What it does:
- Controls my Linux desktop (volume, brightness, window management)
- Reads my screen when I ask it to
- Talks to Home Assistant (lights, sensors, automations)
- Answers questions, explains code, translates Finnish ↔ English
- Runs entirely locally on consumer hardware

What it doesn't do: send my commands, my screen contents, or my voice to OpenAI, Google, or anyone else.

## The Architecture

```
                      ┌─────────────────────────────────┐
                      │     Input / Output Layer         │
                      │  (Whisper STT · Piper TTS)     │
                      └──────────────┬──────────────────┘
                                     │
                                     v
                      ┌─────────────────────────────────┐
                      │        OLLAMA (The Brain)       │
                      │   qwen2.5:3b · Function Calling  │
                      │   Response time: < 200ms         │
                      └──────────────┬──────────────────┘
                                     │
         ┌────────────────────────────┼────────────────────────────┐
         │ HTTP/REST                  │ HTTP/REST                  │ HTTP/REST
         v                            v                            v
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────────┐
│   System Agent      │  │   Vision Agent     │  │   Home Assistant Agent  │
│  (Linux / DBus)    │  │  (Screen capture)  │  │  (Smart home control)   │
│ · Volume / Brightness│  │ · maim / grim      │  │ · Lights, sensors       │
│ · Window management │  │ · Moondream2 VLM   │  │ · WebSocket API         │
│ · Process control   │  │ · Screen analysis  │  │ · Automations           │
└─────────────────────┘  └─────────────────────┘  └─────────────────────────┘
```

Each agent is a **FastAPI service** inside a Docker container. They don't know about each other. They just expose a clean REST interface and wait for instructions from Ollama.

## Why Ollama as the Brain?

Ollama runs small, capable LLMs locally. The key feature here is **function calling** (tool calling) — Ollama doesn't execute commands directly. It returns a structured JSON decision: *"call the `set_volume` function with parameter `level: 75`"*.

This is cleaner than giving the LLM raw bash access. The function list is a strict allowlist — defined in JSON Schema. The model can only call what's explicitly permitted. No `rm -rf /`, no matter how creatively phrased.

The models I'm using are intentionally small:

| Model | Size | Why |
|---|---|---|
| `qwen2.5:3b` | ~2GB | Main orchestrator. Fast, good Finnish support |
| `llama3.2:3b` | ~2GB | Fallback / general reasoning |
| `phi3:mini` | ~2GB | Lightweight tasks |
| *Moondream2* | ~1GB | Vision agent — screen capture analysis |

All fit comfortably on a mid-range GPU or run on CPU. My Intel i5 desktop handles it fine.

## The Agents

### System Agent — Linux Desktop Control

Controls the running Linux session via `wmctrl`, `xdotool`, `playerctl`, and DBus. Things it can do:

- Set volume (`pamixer`)
- Adjust brightness (`xbacklight` or `brightnessctl`)
- Launch applications (`gtk-launch` or `xdg-open`)
- Get active window info
- Control music playback (`playerctl`)
- Read system stats (CPU, memory, disk)

No raw bash. Every function is explicitly defined.

### Vision Agent — "The Eyes"

Takes a screenshot (`maim` or `grim`) or reads a camera stream, then runs the image through a lightweight VLM (Moondream2). Can answer: *"What window is in the foreground?"*, *"Did that build succeed?"*, *"What's on my second monitor right now?"*

### Home Assistant Agent

Talks to my Home Assistant instance over its WebSocket API. Lights, switches, climate, sensors — all accessible. I can say: *"Turn off the office lights, but only if nobody's in there"* and it checks the occupancy sensor before acting.

### Media & Data Agent

Pulls in external data when needed: weather forecasts, electricity prices (relevant in Finland), InfluxDB logs, or web searches via a headless browser.

## The Safety Layer

Giving an AI system control over your desktop is a significant trust boundary. I'm implementing **human-in-the-loop** for sensitive operations:

For destructive or significant actions, the system doesn't just execute. It:
1. Shows a desktop notification with the proposed action
2. Waits for confirmation (click or hotkey)
3. Executes only on explicit approval

This isn't paranoid — it's sensible. The function allowlist prevents most problems at the model level. The confirmation prompt handles the remaining edge cases.

## The Docker Compose

This is where it lives:

```yaml
version: '3.8'

services:
  # The Brain
  ollama:
    image: ollama/ollama:latest
    container_name: jarvis-ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    # GPU passthrough if you have one:
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: all
    #           capabilities: [gpu]

  # The Orchestrator
  jarvis-core:
    build: ./core
    container_name: jarvis-core
    restart: unless-stopped
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - DEFAULT_MODEL=qwen2.5:3b
    ports:
      - "8000:8000"
    depends_on:
      - ollama

  # Linux System Agent
  agent-system:
    build: ./agents/system
    container_name: jarvis-agent-system
    restart: unless-stopped
    network_mode: host   # Needs access to host D-Bus / display

volumes:
  ollama_data:
```

## Voice I/O

For voice input, I'm using **Faster-Whisper** (or `whisper.cpp` for CPU-only) — push-to-talk on a hotkey. For output, **Piper TTS** — fast, local, and surprisingly natural Finnish voices available.

The pipeline: hotkey → Whisper → Ollama → function call or text → Piper TTS → speaker. Total latency target: under 1 second end-to-end.

## Why Not Just Use Home Assistant's Built-in Assist?

Home Assistant has an Assist feature withwyoming-satellite and OpenAI-compatible endpoints. That's actually the longer-term plan — integrate as an Assist pipeline so it works with HA's voice push button.

But building the agents standalone first means they work independently of HA, and can be composed in other ways later. Modular by design.

## What's Next

1. **This week:** Get Ollama running with `qwen2.5:3b`, test function calling with a Python script
2. **Next:** Build the first agent (System Agent) — volume and brightness control as a proof of concept
3. **After that:** Voice pipeline (Whisper + Piper), then Home Assistant integration

I'll post updates as the build progresses. The code will be on GitHub when it's worth sharing.

---

*Building your own tools is the whole point of this site. If you're interested in self-hosted AI, the Ollama docs are a good starting point: [ollama.com](https://ollama.com). And if you want something more polished out of the box, Home Assistant's Assist feature is worth exploring.*
