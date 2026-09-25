# BlogForge — Voice-Calibrated Blog Generation for pragmaticsysadmin.help

BlogForge is a 100% free, zero-third-party-dependency automated blog generation, style profiling, and style checking toolchain built specifically for the architecture and voice of **pragmaticsysadmin.help**.

It operates strictly within Python's standard library (`urllib`, `re`, `pathlib`, `json`, `datetime`, `math`, `html.parser`). You do not need to `pip install` anything.

---

## 1. Quick Start

Run the automated self-test to verify the pipeline against your repo files:
```powershell
python -m blogforge selftest
```

Rebuild the voice profile and human-readable style guide from the 43 published posts:
```powershell
python -m blogforge learn
```

View available and ready LLM providers:
```powershell
python -m blogforge providers
```

Discover new post topics from tools built in the repository or gaps in tag coverage:
```powershell
python -m blogforge ideas --from-artifacts
```

Draft a new post using the free local Ollama backend or template outline:
```powershell
# Using your running local Ollama instance (e.g. qwen3.5:9b or llama3.1:8b)
python -m blogforge generate --topic-id password-checker

# Offline deterministic outline (no model required)
python -m blogforge generate --provider template --topic "Automating ZFS snapshots" --section sysadmin
```

Lint any post (or the whole corpus) against the measured voice bounds:
```powershell
python -m blogforge lint content/sysadmin/2026-09-25-my-post.md
python -m blogforge lint --section sysadmin --min-score 70
```

Review and publish safely:
```powershell
# 1. Edit the file until it sounds like you, then mark it reviewed:
python -m blogforge review content/sysadmin/2026-09-25-my-post.md

# 2. Publish it (flips draft: false, updates date):
python -m blogforge review content/sysadmin/2026-09-25-my-post.md --publish

# Or batch-publish all reviewed posts whose scheduled date has arrived:
python -m blogforge publish --due --dry-run
python -m blogforge publish --due
```

Start the zero-dependency Web Studio & Schedule runner:
```powershell
python -m blogforge ui
# or background / headless schedule server:
python -m blogforge ui --no-browser --port 8080
```


---

## 2. Core Components

### `blogforge/voice.py` & `corpus.py`
Parses the existing 43 blog posts across `/content/` to extract a mathematical fingerprint:
- Outer calibration bands (p10/p90) preventing false failures on outlier writing styles.
- Ideal target ranges (p25/p75).
- Metric extraction: word counts, reading time, sentence and paragraph lengths, H2 density, code block frequency, contraction rate, conversational pronoun ratios (`I`, `you`), concrete figures, and house conventions.
- Verbatim corpus examples: extracts genuine openers, section headers, and punchy closers for the style guide.

### `blogforge/linter.py`
Objective style and hygiene validator scoring 0-100:
- **AI Boilerplate**: Flags telltale filler ("delve", "testament", "tapestry", "in conclusion", "furthermore", "it is worth noting", etc.).
- **Fabricated Experiences**: Catches phrases claiming real-world events the AI cannot know ("in our production incident last month", "when my team migrated 500 servers", "I ran this on my cluster").
- **Metric Bounds**: Warns or fails when a draft drifts outside the corpus bands.
- **House Verdict Markers**: Strictly permits the blog's verdict icons (`✅❌⚠️⭐🏆`) while flagging decorative emoji clutter (`🚀🔥💡`).
- **Hugo Structural Hygiene**: Enforces `<!--more-->` placement, Hugo front-matter requirements, inline anchor link validity, and flags duplicate JSON-LD schema (preventing conflicts with `extend_head.html`).

### `blogforge/providers.py`
Zero-dependency HTTP client supporting free LLM backends:
1. **Ollama (Default / Local)**: Queries `http://localhost:11434`. Automatically handles reasoning/thinking models (such as `qwen3.5` and `deepseek-r1`) by setting `think: false` for drafting so token budgets are spent on prose rather than hidden reasoning blocks.
2. **Google Gemini Free Tier**: Set `GEMINI_API_KEY` or `GOOGLE_API_KEY` (defaults to `gemini-3.8-flash`).
3. **Groq Free Tier**: Set `GROQ_API_KEY` (defaults to `llama-3.3-70b-versatile`).
4. **OpenRouter Free Tier**: Set `OPENROUTER_API_KEY` (defaults to `meta-llama/llama-3.3-70b-instruct:free`).
5. **Template**: Offline structural generator that creates a complete, compliant markdown outline without an LLM.

### `blogforge/generator.py` & `prompts.py`
- Selects the top 3 semantically closest posts from the corpus via n-gram shingle retrieval to provide in-context few-shot anchors.
- Emits prompt constraints adhering to the target section (`sysadmin`, `senior-tech`, or `meta`).
- Automatically runs a generate-lint-repair loop: if the first attempt triggers style linter errors, the feedback is fed into a revision pass.

### `blogforge/topics.py`
- Introspects repository artifacts (like interactive tools in `static/tools/*.html`).
- Analyzes section distribution and tag coverage gaps to propose high-value topics.
- Manages `catalog/topics.yaml`.


### `blogforge/server.py` & `blogforge/ui/` (Web Studio)
Zero-dependency browser interface and API server powered exclusively by Python's built-in `http.server`:
- **Live Debounce Linting**: Edits evaluate against the voice profile every 400ms, displaying the calibrated score (0-100), word count, and exact violations (filler phrases, fabricated claims, heading density).
- **Post Management**: Filter and sort posts by section, draft status, and review status.
- **Draft Generator Modal**: Generate drafts instantly via Ollama, template outline, Groq, Gemini, or OpenRouter.
- **Review & Publish Gates**: Review and publish posts directly from the web interface.
- **Topics & Schedule UI**: Review catalog gaps, enqueue generation jobs, and run background tasks.
- **Git Commit & Push**: Inspect git status and stage/commit/push changes directly to remotes.

### `blogforge/scheduler.py`
Background and cron-compatible task queue (`catalog/schedule.yaml`):
- Automates recurring generation, lint audits, and publishing of due reviewed posts.
- Runs embedded inside the web server or as a standalone CLI worker (`python -m blogforge ui`).

---

## 3. Human-in-the-Loop Safeguards (Trust Rails)

To ensure high-quality content and protect the site's reputation:
1. **Draft Lock**: Every generated file is written with `draft: true` and `reviewed: false`.
2. **Publication Gate**: The automated `blogforge publish` tool **refuses** to publish any post with `reviewed: false`. A human must manually inspect the draft and mark it reviewed (`python -m blogforge review <file>`).
3. **Audit Trail**: Every generated draft includes a front-matter provenance block:
   ```yaml
   reviewed: false
   aiAssisted: true
   blogforge:
     provider: ollama
     model: qwen3.5:9b
     generated_at: "2026-09-25T13:00:00Z"
     attempts: 1
     style_score: 92/100
     topic: Topic Name
   ```
4. **Editorial Integrity**: If AI-assisted drafts are published to the site, ensure the footer or homepage disclosures remain truthful and aligned with the author's voice.
