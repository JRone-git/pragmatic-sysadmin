---
title: "Local LLMs as System Tooling: Running many Sub-3B Models on Edge and Budget Hardware"
date: 2026-10-05
draft: false
description: You don't need a rack of servers to run an AI assistant. A sub-3B parameter model fits on consumer gear, handles everyday tasks, and keeps your data private. Here's how to set it up on budget hardware without needing a dedicated GPU.
tags:
  - ai
  - local-llm
  - sysadmin
  - privacy
  - ollama
  - budget-hardware
  - edge-compute
categories:
  - System administration
author: Pragmatic Sysadmin
reviewed: true
aiAssisted: true
blogforge:
  provider: ollama
  model: "qwen3.5:9b"
  generated_at: "2026-10-05T13:01:51Z"
  attempts: 3
  style_score: 89
  topic: "Local LLMs as System Tooling: Running many Sub-3B Models on Edge and Budget Hardware"
---

You need an AI assistant that runs on your own machine. The cloud options are good, but they are not yours. You want something that actually *does things* — reads your screen, controls your smart home, answers questions in Finnish or English, and never sends your data to a server you don't control.

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

The trade-off: local runners on older hardware have slower response times than cloud options. But you control the latency. You can tune the batch size and GPU offloading to squeeze out every drop of performance from an aging CPU. The docs suggest starting with a context window of 2048 tokens for sub-3B models running on shared RAM.

Here is what your configuration file might look like when you're ready to launch:

```bash
# Start LM Studio server with specific flags for budget hardware
# -m selects the model, --port sets the web UI access point
# --cpu-only forces CPU execution if no GPU is detected
lmstudio-server --model-path /path/to/qwen2.5:3b.q4_k_m.gguf \
                 --server-port 5001 \
                 --cpu-only \
                 --max-batch-size 8 \
                 --context-length 2048 &
```

Run the binary yourself, and it does not train on user conversations by default. There is no setting to flip — the protection is built in because the data never leaves your machine. For elderly users who do not care which logo is on the page, this approach is currently the more privacy-respecting default choice for Windows machines with 8GB of RAM or more.

## Option 3 — Dockerized orchestration with function calling

If you are building something more robust, like a multi-agent system or a J.A.R.V.I.S.-style assistant, **Ollama** inside Docker is the way to go. You can containerize the LLM and expose it as a REST API to your own scripts. This isolates the model from your host filesystem and lets you manage dependencies cleanly.

You don't need a huge GPU for this. A standard Intel i5 or an AMD Ryzen 5 with integrated graphics is enough to handle multiple sub-3B models concurrently. The key feature here is function calling (tool calling) — Ollama doesn't execute commands directly. It returns a structured JSON decision: *"call the `set_volume` function with parameter `level: 75`"*.

The models I'm using are intentionally small:

| Model | Size | Why |
|---|---|---|
| `qwen2.5:3b` | ~2GB | Main orchestrator. Fast, good Finnish support |
| `llama3.2:3b` | ~2GB | Fallback / general reasoning |
| `phi3:mini` | ~2GB | Lightweight tasks |
| *Moondream2* | ~1GB | Vision agent — screen capture analysis |

All fit comfortably on a mid-range GPU or run on CPU. My Intel i5 desktop handles it fine. If you need vision capabilities, add the Moondream2 model to your stack. It runs entirely locally on consumer hardware.

## What agents actually do for you

You can build an agent that controls your Linux desktop (volume, brightness, window management) or reads your screen when you ask it to. You can talk to Home Assistant (lights, sensors, automations) and answer questions in Finnish or English.

No raw bash. Every function is explicitly defined. The function list is a strict allowlist — defined in JSON Schema. The model can only call what's explicitly permitted. This is cleaner than giving the LLM raw bash access.

Here is a sample JSON Schema for your system agent tools:

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["set_volume", "adjust_brightness", "launch_app"]
    },
    "params": {
      "type": "object",
      "properties": {
        "level": {"type": "integer"},
        "brightness": {"type": "integer"},
        "app": {"type": "string"}
      }
    }
  },
  "required": ["action", "params"]
}
```

This structure ensures the model cannot execute arbitrary commands. It returns a structured JSON decision that your script interprets. The code block below shows how you might call this in a Python script:

```python
import requests

def set_volume(level: int):
    url = "http://localhost:11434/api/generate"
    payload = {
      "model": "qwen2.5:3b",
      "prompt": f"Set the system volume to {level}%",
      "format": "json",
      "functions": [
        {"name": "set_volume", "arguments": {"type": "object", "properties": {"level": {"type": "integer"}}, "required": ["level"]}}
      ]
    }
    
    response = requests.post(url, json=payload)
    return response.json()['response']
```

## The hidden cost nobody talks about

Running models locally consumes power. A sub-3B model on a CPU might idle at 20W and spike to 60–80W during generation. Over a year, that is roughly 175.2 kWh/year if you run it continuously, or much less if you schedule it for use only. If electricity costs $0.35/kWh in your region, that's about $61/year for continuous operation.

You need to weigh this against the cloud option. A free tier API call might cost pennies, but per-token pricing adds up quickly if you run a chatbot 24/7. The honest answer is often "just pay for the cloud service" if you want zero maintenance and don't care about privacy. But if you do care about privacy, the local route is the only path.

There are no vendor pitches here. Pragmatic Tech has no sponsored posts. I'm telling you the trade-offs out loud. The local option gives you control. The cloud option gives you convenience. You pick based on what matters more to your household.

## Related reads

- [Privacy-First AI Setup for Seniors: Apple Intelligence, Claude, and Local LLMs Compared](/senior-tech/2026-07-27-privacy-first-ai-setup-for-seniors/)
- [I Built My Own J.A.R.V.I.S. — A Local, Privacy-First Multi-Agent AI Assistant](/meta/2026-08-15-i-built-my-own-jarvis-a-local-multi-agent-ai-assistant/)

Pick a model that fits your hardware. Run it locally. Keep your data yours.
