# Reddit Pitches

---

## r/sysadmin — "I Built an App for My Dad with Dementia — It's Free and No Account Needed"

**Title:**
> I built a free, no-account companion app for my dad when dementia made his phone unusable

**Body:**

My dad called me at 2 AM. He couldn't remember if he'd taken his pills. He didn't know what day it was.

I drove up that morning and watched him stare at his phone like it was a foreign object — and he'd been using it for 10 years.

That's when I built Buddy. Five tiles: People (tap a face to call), Medicines (tap green when taken), Safety, Notes, Help. No account. No data on a server. Works offline. In 7 languages.

The design principle was simple: one screen, one job. No hamburger menus. No settings labyrinth.

I gave it away for free. Here's what I learned about designing for people with cognitive decline: [pragmaticsysadmin.help/meta/why-i-built-buddy-free-app-dad-sick/]

Try it: [pragmaticsysadmin.help/buddy/] — no account, works on any phone.

AMA about building for elderly users with dementia.

---

**Tags to include:** Discussion, Tools

---

## r/sysadmin — "bashbuddy — 300 Lines of Pure Bash That Turns Any AI Into a Terminal Companion"

**Title:**
> I built a terminal AI companion in 300 lines of pure bash (MIT licensed, no npm)

**Body:**

Every time I run a command that fails, I spend 20 minutes figuring out why — then realize the answer was obvious in retrospect.

bashbuddy is a single bash script that turns any AI API into an interactive terminal assistant:

```bash
bashbuddy                         # Interactive chat
bashbuddy --explain < error.log   # Explain a pasted error
bashbuddy --review script.sh      # Bug + security review
bashbuddy "show me disk usage"   # Natural language -> bash
```

Works with OpenAI, OpenRouter, Groq, LM Studio (offline), Ollama (offline). One-line install.

The whole thing is one file. 300 lines. MIT licensed. No npm, no Python, no dependencies beyond curl and jq.

**Source:** [github.com/JRone-git/pragmatic-sysadmin/tree/main/bashbuddy]
**Write-up:** [pragmaticsysadmin.help/sysadmin/bashbuddy-300-lines-bash-terminal-ai-companion/]

Happy to answer questions about the design choices.

---

**Tags:** Tools, Discussion

---

## r/homelab or r/selfhosted — "Prism Engine — Visualize Your Docker Compose as a 3D Topology"

**Title:**
> I made a free browser tool that renders your Docker Compose config as a 3D infrastructure map (click nodes for risk analysis)

**Body:**

Wanted to visualize infrastructure configs in a way that actually shows the topology, not just YAML.

Prism Engine: paste your Docker Compose, K8s manifest, or just describe your stack — it renders it as a 3D scene you can rotate, zoom, and click through.

- Nodes colored by risk level (green/yellow/orange/red)
- Click any node to see: what it does, why it's that risk level, and what to do about it
- Auto-infers risk from image names (postgres exposed = critical, nginx = high, redis = medium)
- Demo loads automatically — no signup, works offline after first load

Free, no account: [pragmaticsysadmin.help/tools/prism-engine.html]

Written in vanilla JS + Three.js. Paste config → see your infra.

---

**Tags:** Selfhosted, Tools, Discussion
