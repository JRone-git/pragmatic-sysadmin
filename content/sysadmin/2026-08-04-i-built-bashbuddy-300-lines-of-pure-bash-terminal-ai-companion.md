---
title: "I Built a Terminal AI Companion in 300 Lines of Pure Bash — And It's MIT Licensed"
date: 2026-08-04
author: Pragmatic Sysadmin
description: "bashbuddy is a single bash script that turns any AI API into a smart terminal assistant. Paste errors, write scripts, review code — all without leaving your terminal. Free and open source."
draft: false
tags: ["bash", "ai", "cli", "tools", "open-source", "productivity"]
slug: bashbuddy-300-lines-bash-terminal-ai-companion
topics: ["tools", "bash", "ai"]
resources:
  - name: bashbuddy
    url: /bashbuddy/
    description: Try bashbuddy — MIT licensed, single bash script
  - name: bashbuddy-github
    url: https://github.com/JRone-git/pragmatic-sysadmin/tree/main/bashbuddy
    description: Source code on GitHub
---

I write a lot of bash scripts. Most of them work. Some of them don't — and when they don't, I spend 20 minutes staring at an error message that, in retrospect, was actually pretty obvious.

I figured: what if I could just ask an AI, from my terminal, what went wrong?

That's bashbuddy. 300 lines of pure bash. No npm. No Python. No dependencies beyond `curl` and `jq`. MIT licensed, free forever.

<!--more-->

## What It Does

```bash
# Interactive chat mode — like having a senior engineer at your desk
bashbuddy

# Explain a pasted error
bashbuddy --explain < error.log

# Review a script for bugs before you run it
bashbuddy --review deploy.sh

# Natural language to bash command
bashbuddy --translate "show me disk usage sorted by size"

# Fix a bad command
bashbuddy --fix "rm -rf /"
```

That's it. No Electron app. No Python framework. It's literally a bash script you pipe things to.

## The Interactive Mode

Run `bashbuddy` with no arguments and you get a REPL:

```
  bashbuddy v1.0.0 | Ctrl+D to quit | /help for commands

bb > why is my Nginx reverse proxy returning 502?

Your Nginx is returning a 502 Bad Gateway error, which means...

    [explanation with context and fix]

bb > write a script to find files modified in the last 24 hours

Here's a script that does that...

    #!/bin/bash
    find /path -type f -mtime -1 ...
```

The REPL remembers your conversation history across sessions. It knows what OS you're on, what shell, what directory you're in. Context-sensitive help, basically.

## Special Commands

| Command | What it does |
|---|---|
| `/explain` | Paste an error → plain-English explanation |
| `/review` | Review a bash script for bugs, security, and style |
| `/translate` | "show me disk space" → `df -h` |
| `/fix` | Paste a bad command → explain what's wrong + fix it |
| `/model` | Switch to a different AI model |
| `/clear` | Clear conversation history |

## Works With Any AI Backend

I didn't want to lock anyone into a specific provider. bashbuddy works with:

- **OpenRouter** — 100+ models, one API (my recommendation: Claude Haiku for speed)
- **OpenAI** — direct, reliable
- **Groq** — extremely fast, generous free tier
- **LM Studio** — run open-source models locally, fully offline
- **Ollama** — run open-source models locally, fully offline
- **Any OpenAI-compatible API** — bring your own endpoint

The setup wizard detects LM Studio and Ollama automatically if they're running locally:

```bash
$ bashbuddy --setup
Choose backend [1]: 4   # LM Studio
Detected model: llama-3.2-3b-instruct
Config saved. Done.
```

## One-Line Install

```bash
curl -fsSL https://raw.githubusercontent.com/JRone-git/pragmatic-sysadmin/main/bashbuddy/bashbuddy \
  -o ~/bin/bashbuddy && chmod +x ~/bin/bashbuddy

bashbuddy --setup
```

Requires: `bash`, `curl`, `jq` — already on most systems.

## What 300 Lines Gets You

I wrote it to be readable, not clever. The entire source is one file. Here's the rough architecture:

```
Config loading          ~40 lines  (env vars, XDG paths, API key)
Dependency check        ~10 lines  (curl, jq)
Setup wizard            ~60 lines  (backend detection, auto-detect local models)
System prompt builder   ~20 lines  (OS, shell, hostname, working dir)
API caller              ~40 lines  (curl, error parsing, HTTP code hints)
Message builder         ~50 lines  (history loading, JSON assembly with jq)
Streaming output        ~40 lines  (SSE parsing, token-by-token rendering)
Interactive REPL        ~60 lines  (input loop, built-in commands)
CLI parser              ~20 lines  (--explain, --review, etc.)
```

No external libraries. No package manager. You can read the whole thing in 10 minutes.

## What It Doesn't Do

Honest limitations:

- **No background jobs** — it's synchronous, it blocks while waiting for the API
- **No code execution** — it explains and suggests, doesn't run your code for you (though the `$RUN:` directive lets it offer commands for you to run manually)
- **No multi-model conversations** — each session uses one model
- **No plugins** — it's intentionally small

If you need more, use a full CLI tool. bashbuddy is for the 90% case: "what does this error mean?" and "write me a quick one-liner."

## The $RUN Directive

One thing I'm proud of: if bashbuddy suggests a command to run, it doesn't just dump it in the response. It uses a `$RUN:` prefix and waits for confirmation:

```
bb > find all large log files

That command would be:

    $RUN: find /var/log -name "*.log" -size +100M -exec ls -lh {} \;

Run this command? [y/N]
```

This is intentional. It's a CLI tool. You should always know what's about to run.

## Why MIT Instead of GPL?

Because I want this to live in `/usr/local/bin` on servers, in Docker containers, in dotfile repos, everywhere. GPL would require anyone who modifies it to open-source their changes. MIT says: use it however you want, modify it, ship it, no strings attached.

The worst thing a developer tool can be is a walled garden.

## The Code Is On GitHub

All of it. MIT licensed. Issues welcome, PRs doubly so.

**Source:** [github.com/JRone-git/pragmatic-sysadmin/tree/main/bashbuddy](https://github.com/JRone-git/pragmatic-sysadmin/tree/main/bashbuddy)

If you want to follow the development, the Buddy companion app (the elderly-friendly phone app) is in the same repo: [pragmaticsysadmin.help/buddy](/buddy/) — also MIT licensed, also free forever.
