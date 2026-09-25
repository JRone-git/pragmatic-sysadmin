# bashbuddy

> Your terminal AI companion — for sysadmins, devs, and anyone who lives in the command line.

**bashbuddy** is a single bash script that turns any AI API into a smart, interactive terminal assistant. Paste errors, write scripts, translate natural language to bash, review code — all from your terminal.

MIT licensed. No tracking. No telemetry. Runs offline with local models.

---

## Features

- **Chat mode** — interactive REPL with conversation history
- `/explain` — paste an error → plain-English explanation
- `/review` — review a bash script for bugs, security, and style
- `/translate` — "show me disk space" → `df -h`
- `/fix` — paste a bad command → explain what's wrong and fix it
- **Streaming output** — responses stream token-by-token
- **Conversation history** — remembers context across sessions
- **Any backend** — OpenAI, OpenRouter, Groq, LM Studio, Ollama, or any OpenAI-compatible API

---

## Install

```bash
# One-line install (curl to your ~/bin)
curl -fsSL https://raw.githubusercontent.com/pragmatic-sysadmin/bashbuddy/main/bashbuddy -o ~/bin/bashbuddy
chmod +x ~/bin/bashbuddy

# Or clone
git clone https://github.com/pragmatic-sysadmin/bashbuddy.git
cd bashbuddy
./bashbuddy --setup
```

Requirements: `bash`, `curl`, `jq`

---

## Setup

```bash
bashbuddy --setup
```

Choose your backend:
1. **OpenRouter** (recommended) — unified API for Claude, Gemini, Llama, and 100+ models. Free tier available.
2. **OpenAI** — direct, reliable
3. **Groq** — extremely fast, generous free tier
4. **LM Studio** — run open-source models locally, fully offline
5. **Ollama** — run open-source models locally, fully offline
6. **Custom URL** — any OpenAI-compatible endpoint

Your API key is saved to `~/.config/bashbuddy/config`. You only set it once.

---

## Usage

```bash
# Interactive chat
bashbuddy

# One-shot questions
bashbuddy "show me the largest files in /var/log"
bashbuddy "explain this error: permission denied"
bashbuddy "write a script to find duplicate photos"

# Explain a pasted error (from file)
bashbuddy --explain < error.log

# Review a script
bashbuddy --review deploy.sh

# Natural language to bash
bashbuddy --translate "show me disk usage sorted by size"

# Fix a bad command
bashbuddy --fix "rm -rf / tmp"

# Disable streaming
bashbuddy --no-stream "explain this code"
```

### Interactive commands

| Command | What it does |
|---|---|
| `/explain` | Paste an error → plain-English explanation |
| `/review` | Review a bash script for bugs |
| `/translate` | Natural language → bash command |
| `/fix` | Explain a bad command and fix it |
| `/model` | Switch to a different model |
| `/setup` | Re-run the API key setup |
| `/clear` | Clear conversation history |
| `/help` | Show all commands |
| `/exit` | Quit |

---

## Configuration

Config file: `~/.config/bashbuddy/config`

```bash
API_KEY="sk-or-..."
BASE_URL="https://openrouter.ai/api/v1"
MODEL="anthropic/claude-3.5-haiku"
```

Environment variables (override config file):
- `BASHBUDDY_CONFIG` — custom config file path
- `BASHBUDDY_HISTORY` — custom history file path

---

## License

MIT — use it, modify it, ship it, no strings attached.

https://github.com/pragmatic-sysadmin/bashbuddy
