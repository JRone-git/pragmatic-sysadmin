---
title: "I Built a Tool That Explains Any Command or Error in Plain Language"
date: 2026-08-04
author: Pragmatic Sysadmin
description: "The most common sysadmin task isn't running commands — it's explaining commands. I built a free tool that translates technical jargon into plain language for sysadmins, family caregivers, or total beginners."
draft: false
tags: ["tools", "ai", "bash", "plain-english", "explanation"]
slug: plain-english-explain-any-command-error-concept
topics: ["tools", "ai"]
resources:
  - name: plain-english
    url: /tools/plain-english.html
    description: Try Plain English — free, no account needed
---

Every sysadmin has the same job, really. It's not "manage servers." It's not "configure networks." It's: **explain technical things to non-technical people.**

My dad calls me. Something's wrong with his computer. He says: "It says something about DNS and the connection isn't private."

What do I actually need to tell him?

I could say: "Your router's DNS resolution is failing because the ISP's nameserver at 8.8.8.8 isn't responding, causing an SSL handshake failure due to certificate verification timing out."

That's accurate. It's also useless.

What I actually say: "Your internet is having a momentary hiccup. Turn the router off and on, wait 30 seconds, try again."

Same fix. Better explanation.

That's the gap I tried to fill with [Plain English](/tools/plain-english.html).

<!--more-->

## What It Is

A free, browser-based tool. Paste a bash command, an error message, a config file, or a technical concept — and it explains it in plain language.

The twist: you pick who you're explaining it *to*.

- **Sysadmin / Dev** — technical precision, appropriate jargon, cite error codes
- **Family Member** — warm, simple, everyday analogies, reassuring
- **Total Beginner** — zero jargon, treat them like they just opened a computer for the first time

Same command, three explanations. All of them correct. None of them condescending.

## Examples

**Input:** `sudo rm -rf /var/cache`

> **For a sysadmin:** This recursively deletes `/var/cache` with root privileges. It removes cached package files, build artifacts, and temporary data. Generally safe on Debian/Ubuntu since `/var/cache` is regenerated on next package install, but will temporarily break any in-progress builds or downloads.
>
> **For a family member:** Your helper ran a command to delete temporary files that your computer saves so things load faster. It's safe — your computer will make new ones automatically. It's the digital equivalent of clearing out old junk mail.
>
> **For a total beginner:** Someone typed a command that tells the computer to permanently delete a folder of saved temporary files. The computer will not ask "are you sure?" It will just do it. These files are like scratch paper — useful, but not important. It's fine to delete them.

---

**Input:** `HTTP 502 Bad Gateway`

> **For a sysadmin:** The upstream application server (behind Nginx/Apache) either crashed, is overloaded, or refused the connection. Check upstream logs, verify the service is running, inspect the proxy timeout settings. Common after deployments or during traffic spikes.
>
> **For a family member:** The website you're trying to visit is having a momentary problem — the "middle person" server (which helps direct your request) couldn't get an answer from the main server. Usually fixes itself in a few minutes. Try refreshing.
>
> **For a total beginner:** Imagine you call a company and the receptionist says "hold on" — then never comes back. That's what this error means. The website is still there, but it's not answering right now. Wait a minute and try again.

---

**Input:** `What is a systemd service?`

> **For a sysadmin:** A systemd unit that runs as a daemon (background process) managed by the init system. Defined by a `.service` file under `/etc/systemd/system/`. Controlled via `systemctl start/stop/restart/enable/disable`. Dependencies expressed via `After=`/`Requires=` directives.
>
> **For a family member:** It's like an app on your phone — except it's always running in the background on the computer, even when you're not using it. It starts automatically when the computer turns on and keeps working even if something crashes. Things like WiFi, printing, and keeping time are all handled this way.
>
> **For a total beginner:** Imagine a helpful robot inside your computer that wakes up every time the computer starts, makes sure all the important things (like internet, printing, sound) are running, and restarts them if they stop. You don't see it, but it's always working.

## Why It Matters More Than You'd Think

I've been thinking about why this is hard to do well.

The reason isn't intelligence. It's **audience calibration**. When you're deep in technical work, it's genuinely difficult to remember what you didn't know. The command is obvious to you. The error code is self-explanatory.

But your dad doesn't have 20 years of muscle memory for this stuff. And your client doesn't know what "elevated privileges" means.

The tool doesn't do anything you couldn't do yourself. It just forces you to pick an audience before you start explaining. That single choice — "who am I talking to?" — changes everything about how you communicate.

## How It Works

It uses AI (your own API key, stored only in your browser) to generate the explanations. The prompt templates are tuned for each audience — the sysadmin version prioritizes precision; the beginner version prioritizes analogy and reassurance.

No accounts. No server. Your API key never leaves your browser. If you don't have an API key, [get one from OpenRouter](https://openrouter.ai/keys) — there's a free tier that works fine for this.

## The Real Use Case

Honestly, I built this for myself.

Every time I have to explain something to my mom, I spend 10 minutes re-calibrating my brain from "senior sysadmin mode" to "person who just wants their printer to work."

This tool doesn't replace that judgment. But it gives me a starting point — a first draft of an explanation — that I can then adjust.

Sometimes I just paste my own command and read the beginner explanation, just to see if I've actually understood what I'm running.

---

**Try it:** [pragmaticsysadmin.help/tools/plain-english.html](/tools/plain-english.html) — free, no account, uses your own API key.

If you find it useful, the [5-Minute Server Health Check Toolkit](https://pragmaticsysadmin.help/products/health-check-toolkit/) funds the server costs and the time it takes to build things like this.
