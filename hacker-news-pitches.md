# Hacker News Pitches

---

## HN #1 — Buddy (personal story + open source tool)

**Title:**
> I built a free companion app for my dad with dementia when every other app was too complex

**Body:**

My dad called me at 2 AM. He had dementia and couldn't remember if he'd taken his pills or what day it was.

I looked at the App Store. 47 medication reminder apps. Every single one required: user accounts, push notification permissions, onboarding flows, cloud sync, subscription upsells.

None of them was: open the app, tap green when you've taken your pill, done.

So I built Buddy. Five tiles on a home screen. No accounts. No server. Everything lives in the browser. Works offline. In 7 languages.

The design insight was simple: people with cognitive decline don't have problems with complexity in the traditional sense. They have problems with *decision load*. Every screen that asks "what do you want to do?" is a failure waiting to happen.

One screen, one job. That's it.

It's MIT licensed. Here's the story and what I learned: [pragmaticsysadmin.help/meta/why-i-built-buddy-free-app-dad-sick/]

Try it: [pragmaticsysadmin.help/buddy/]

---

## HN #2 — bashbuddy (show hn)

**Title:**
> Show HN: bashbuddy — a terminal AI companion in 300 lines of pure bash

**Body:**

[billguisness]

I've been a sysadmin for 15 years. The most common task isn't running commands — it's explaining commands. To clients, family members, junior engineers.

bashbuddy is a single bash script that turns any AI API into an interactive terminal assistant.

The pitch isn't "it's cool." The pitch is: it's a real tool I use every day. When I'm staring at a segfault at midnight and can't remember what `ulimit` does, I can just ask.

One-line install. Works offline with LM Studio or Ollama. No npm. No framework. MIT licensed.

**The twist:** It explains things differently depending on your audience. Same command, explained for a sysadmin vs a family member vs a total beginner.

Source: [github.com](https://github.com/JRone-git/pragmatic-sysadmin/tree/main/bashbuddy)
Write-up: [pragmaticsysadmin.help](https://pragmaticsysadmin.help/sysadmin/bashbuddy-300-lines-bash-terminal-ai-companion/)

---

## HN #3 — Prism Engine (show hn)

**Title:**
> Show HN: Prism Engine — visualize Docker Compose configs as interactive 3D topology maps

**Body:**

[username]

I wanted a way to look at a Docker Compose file and actually *see* the infrastructure — not just parse YAML.

Prism Engine: paste your config, get a rotatable 3D scene with nodes colored by risk level. Click any node for a plain-English explanation of what it does and what to harden.

Risk is inferred from image names and port exposure. Postgres exposed to the internet = red. Nginx reverse proxy = yellow. Redis cache = green.

Free, no account, works offline after load.

[bunch of screenshots would go here]

Try it: [pragmaticsysadmin.help/tools/prism-engine.html](https://pragmaticsysadmin.help/tools/prism-engine.html)

---

## Posting Strategy

| Post | Platform | Timing | Order |
|---|---|---|---|
| Buddy story | r/sysadmin | Mon-Thu morning (your timezone) | Post 1st |
| bashbuddy | HN + r/sysadmin | Wed-Thu afternoon US time | Post 2nd (24hr after) |
| Prism Engine | r/selfhosted + r/homelab | Fri or Sat | Post 3rd |

**Rule:** Post once per platform per 48 hours. Stagger them so you're not spamming.

**HN submission URL:** https://news.ycombinator.com/submit

**Tip:** Add a comment within the first 30 minutes of posting on HN. Ask a question. Engage with the first 5 comments. That dramatically affects your ranking.
