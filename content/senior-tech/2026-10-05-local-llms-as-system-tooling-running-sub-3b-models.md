---
title: "Local LLMs as System Tooling: Running Sub-3B Models on Edge and Budget Hardware"
date: 2026-10-05
draft: false
description: You need an AI assistant that runs on your own machine. Here is how to set up a local sub-3B model for privacy and reliability without buying new hardware.
tags:
  - ai
  - local-llm
  - privacy
  - senior-tech
  - budget-hardware
categories:
  - System administration
author: Pragmatic Sysadmin
ShowToc: true
reviewed: true
aiAssisted: true
blogforge:
  provider: ollama
  model: "qwen3.5:9b"
  generated_at: "2026-10-05T12:40:42Z"
  attempts: 3
  style_score: 90
  topic: "Local LLMs as System Tooling: Running Sub-3B Models on Edge and Budget Hardware"
---

You need an AI assistant that runs on your own machine. The cloud options are good but they are not yours. You want something that actually *does things* — reads your screen, controls your smart home, answers questions in Finnish or English, and never sends your data to a server you don't control.

The local LLM trend is about as practical as it sounds. It works on mid-range hardware if you pick the right model size. A sub-3B parameter model fits comfortably on consumer gear and handles everyday tasks without needing a dedicated GPU or a rack of servers. The trade-off versus cloud options is that the response times are slower, but your parents' conversations do not become training data for a future model owned by a third party.

<!--more-->

## Why "local" matters more than "smarter"

The most capable AI in 2026 is still a cloud-hosted model from OpenAI or Anthropic. But "most capable" is the wrong axis for elderly parents. They are not pushing the model with complex prompts or asking it to write production code. They are asking it to summarize a long email, explain a confusing medication instruction, draft a birthday reply to a grandchild, or settle a trivia dispute.

For all of those tasks, a smaller, more private model is more than sufficient — and the privacy trade-off is meaningfully better. The three options below all share one property: your parents' conversations do not become training data for a future model owned by a third party. That single property is worth more than a few IQ points of model quality.

You might think you need the biggest GPU to run this locally. You don't. A sub-3B model runs on an older laptop or a budget desktop. The key feature here is function calling — the model does not execute commands directly but returns a structured JSON decision that your script interprets. This is cleaner than giving the LLM raw bash access. The function list is a strict allowlist — defined in JSON Schema. The model can only call what is explicitly permitted. No `rm -rf /`, no matter how creatively phrased.

## Option 1 — Run Ollama on an old machine

If your parents have an older Mac, a Windows PC from the last few years, or a Linux box gathering dust, **Ollama** is the strongest default choice. It is built into the system via a simple binary install, requires no separate app store login, and does not require a separate cloud account for the model itself. Your parents do not have to "use" Ollama — they just continue using their devices as they always have, and the AI shows up where it is useful: inside a chat window or a smart home dashboard.

The privacy architecture is genuinely best-in-class for consumer AI when you host it yourself:

- **On-device first.** Most requests are processed locally on the device's CPU or integrated GPU. The data never leaves the machine unless you explicitly configure an API endpoint to send it elsewhere.
- **Private Cloud Compute (optional).** For requests that need more compute than the phone can provide, you can route them to dedicated servers, but this is not required for sub-3B models. They run fine on a CPU.
- **No training on personal data.** You are the model owner. Your parents' Ollama requests do not get sent to OpenAI or Anthropic. This is an architectural commitment, not just a setting.

The catch: you must manage the updates. If your machine does not have access to the internet, the model binaries will not update automatically. You need to check for new releases and pull them manually. If your parents are in a supported region for Apple Intelligence, you might still prefer that option over Ollama for simplicity. Check Settings → General → Apple Intelligence & Siri on their device; if the menu is present and the toggle works, they are eligible.

**Setup time:** 10 minutes on macOS or Linux, 20 minutes on Windows. Run the installer script or download the binary from the official site. Open a terminal or command prompt. Type `ollama run qwen2.5:3b`. Wait for the pull to finish. Talk them through three demo tasks: "summarize this notification stack," "rewrite this email to be shorter," and "create a fun image of a cat." That is enough for them to internalize what the AI can do without overwhelming them.

## Option 2 — Use a browser-based local runner

If your parents are on Android, on a Windows PC, or simply do not have a recent enough machine for Apple Intelligence, the next best default is **KoboldCPP** or **LM Studio**, used through a browser at `localhost:5001`. These tools run locally but offer a web interface that looks familiar to anyone who has used a chatbot before.

KoboldCPP's privacy posture for local users is stronger than most cloud tools: you run the binary yourself, and it does not train on user conversations by default, full stop, on any tier. There is no setting to flip — the protection is built in because the data never leaves your machine. For elderly users who do not care which logo is on the page, KoboldCPP is currently the more privacy-respecting default choice for Windows machines with 8GB of RAM or more.

The trade-off: local runners on older hardware have slower response times than cloud services. You will see "processing" indicators for a few seconds longer. For someone using AI a few times a week, this is fine. For someone who has integrated it into daily routines, it is annoying but not dangerous. You can set the temperature and context window to match their needs. Lower temperature means more factual answers; higher temperature means more creative writing.

| Tool | Platform | RAM needed | Best for |
|---|---|---|---|
| Ollama | macOS/Linux/Windows | 6GB+ | System integration |
| LM Studio | Windows/macOS/Linux | 4GB+ | Easy web UI |
| KoboldCPP | Windows/Linux | 4GB+ | High compatibility |

All fit comfortably on mid-range hardware or run on CPU. Your Intel i5 desktop handles it fine if you pick the right model. The models I'm using are intentionally small: `qwen2.5:3b` for the main orchestrator, `llama3.2:3b` as a fallback, and `phi3:mini` for lightweight tasks.

## The System Agent — Desktop Control

Once you have Ollama or LM Studio running locally, you can build a simple agent to control the desktop environment. Things it can do include setting volume with `pamixer`, adjusting brightness with `xbacklight`, launching applications with `xdg-open`, and getting active window info via `wmctrl`.

No raw bash. Every function is explicitly defined in a JSON schema file that the model reads before taking an action. The model sees a list of allowed functions and can only call what's on that list. This prevents the "I want to delete all my files" prompt from accidentally deleting anything, because the command to do so is not on the allowlist.

You might wonder if this setup is safe for your parents. If they are comfortable using their phones without fear of breaking something, they can use a local LLM agent with similar confidence. The only real risk is accidental deletion if the function list is too broad. Keep it strict. Define specific functions like `set_volume(level)` or `open_app(name)`. Do not add `delete_file()` unless you really want to risk losing data.

## The Vision Agent — "The Eyes"

If your parents have a tablet with a camera, you can take a screenshot or read a camera stream, then run the image through a lightweight VLM like `Moondream2`. It can answer: *"What window is in the foreground?"*, *"Did that build succeed?"*, *"What's on my second monitor right now?"*.

The setup requires a tool to capture the screen image before sending it to the model. On Linux, use `maim` or `grim`. On Windows, use `PowerShell` commands with the built-in clipboard support. The model then analyzes the image and returns text. You can chain this with the system agent to read screen content aloud or highlight important windows.

## The Home Assistant Agent

If your parents have smart home devices, you can talk to a Home Assistant instance over its WebSocket API. Lights, switches, climate, sensors — all accessible via the local network. I can say: *"Turn off the office lights, but only if nobody's in there"* and it checks the occupancy sensor before acting.

This setup requires the Home Assistant container to expose its API endpoint to the local LLM agent. The model sends a message like "dim the living room light" and the agent parses it into a JSON call to the Home Assistant API. The agent handles the HTTP request and returns success or failure status to the user interface.

## Media & Data Agent

You might want the AI to pull in external data when needed: weather forecasts, electricity prices relevant in Finland, or web searches via a headless browser tool like `curl` or `playwright`. This is optional but useful if your parents need to plan their day around energy costs or check the weather for outdoor activities.

The agent runs in its own Docker container and does not know about the other agents. It just exposes a clean REST interface and waits for instructions from Ollama. Each agent is a **FastAPI service** inside a Docker container. They don't know about each other. They just expose a clean REST interface and wait for instructions from Ollama.

This isolation prevents one agent from breaking another. If the media agent crashes, the system agent keeps working. You can restart containers individually without affecting the whole stack. This is better than running everything as one monolithic Python script.

## The tradeoff — Local vs Cloud

You might ask why not just use the cloud service. The answer is simple: privacy. When you run locally, your parents' conversations do not become training data for a future model owned by a third party. That single property is worth more than a few IQ points of model quality.

The local runner does not have unlimited context windows or infinite message quotas. You will hit hardware limits sooner than cloud services. A sub-3B model on a budget machine will choke on long documents that fit easily in the cloud. This is fine for most users who just want to summarize emails or draft messages. If you need more power, you can switch to a larger model or upgrade the hardware later.

## Setup checklist

Here is what you should do next time you visit your parents:

- Install Ollama or LM Studio on their machine.
- Pull a sub-3B model like `qwen2.5:3b` for general tasks.
- Configure a simple agent to control volume, brightness, and app launching.
- Set up a web interface so they can chat without opening a terminal.
- Test three demo tasks together to show what the AI can do.

If you are unsure about Docker or the command line, stick to the installer scripts. They handle most of the configuration for you. You just type `ollama run qwen2.5:3b` and wait for it to finish downloading. The model will start automatically after that.

## Closing thought

You do not need a new computer to run local AI. An old laptop or a budget desktop works fine for sub-3B models. The setup takes ten minutes on Linux, twenty on Windows, and two on macOS. Your parents' conversations stay private because they never leave the machine.

Whatever you choose, take 30 minutes on a Saturday to set it up properly. The local LLM is the second-most-important thing; the setup is the first. A senior with a well-set-up local AI will be happier than a senior with a poorly-set-up flagship cloud service.
