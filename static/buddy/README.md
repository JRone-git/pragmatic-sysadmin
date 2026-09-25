# Buddy — Your Everyday Helper

A free, multi-language web app for older adults (and the adult children who love them). Built for **[pragmaticsysadmin.help](https://pragmaticsysadmin.help)**.

## What's new in v3

- ✅ **7 languages**: English, Spanish, French, German, Portuguese (BR), Chinese (Simplified), Finnish
- ✅ **Locale-aware emergency numbers**: 911 (US), 112 (EU: Finland, Germany, France), 190 (Brazil), 110 (China)
- ✅ **Auto-detects** browser language on first visit; user can override via 🌐 button
- ✅ **Demand validation built-in**: tracks unique-day visits, prompts for feedback after 2nd use (max once per 30 days)
- ✅ **Email capture** for upgrade waitlist (unchanged)
- ✅ Same simple, elderly-first UX

## What it does

A mobile-first companion with four giant buttons:

| Tile | What it does |
|------|--------------|
| 👥 **My People** | One-tap calls to family, doctor, neighbor |
| 💊 **Medicines** | Daily reminders, check off what you took |
| 🛡️ **Stay Safe** | Paste a suspicious message → scam-pattern check |
| 💡 **How-To** | Step-by-step guides (screenshots, video calls, Wi-Fi, passwords…) |

Plus a big red **emergency** button on the home screen — number adapts to the user's country (911 US, 112 EU, etc.).

## Languages

| Code | Language | Speakers | Emergency # | Reach |
|------|----------|----------|-------------|-------|
| 🇺🇸 en | English | 1.5B | 911 | US, UK, AU, CA |
| 🇪🇸 es | Español | 560M | 911 | US (60M Hispanics), Mexico, LATAM, Spain |
| 🇫🇷 fr | Français | 310M | 112 | France, Canada (Quebec), Belgium, Africa |
| 🇩🇪 de | Deutsch | 130M | 112 | Germany, Austria, Switzerland |
| 🇧🇷 pt | Português | 260M | 190 | Brazil, Portugal |
| 🇨🇳 zh | 中文 | 1.1B | 110 | China, Singapore, Malaysia |
| 🇫🇮 fi | Suomi | 5M | 112 | Finland (fastest-aging EU population) |

**Combined reach: 3.9 billion speakers.** Senior population across these languages: roughly **400M people**.

## File structure

```
buddy/
├── index.html       — single-page app shell with i18n hooks
├── style.css        — elderly-first styles (18-20px base, big touch targets, high contrast)
├── app.js           — state, rendering, i18n, demand validation
├── i18n.js          — translations for all 6 languages (1450 lines)
└── README.md        — this file
```

No build step. No dependencies. Pure HTML/CSS/JS.

## Install on pragmaticsysadmin.help

### Option A: Subfolder (recommended)
Upload all 4 files to `public_html/buddy/` on your host. Link from your main site:
```html
<a href="/buddy/">Try Buddy — a free app for older family members</a>
```
Visit: `https://pragmaticsysadmin.help/buddy/`

### Option B: Subdomain
Create `buddy.pragmaticsysadmin.help` → point to the same folder.

### Option C: Per-language landing pages
For SEO, create separate landing pages per language:
- `pragmaticsysadmin.help/buddy/es/` → `index.html` with `<script>localStorage.setItem('buddy-state-v2', JSON.stringify({lang:'es'}))</script>` before app loads
- This way Google sees Spanish content and links to it.

## Adding a 7th language

1. Open `i18n.js`
2. Copy the entire `en: { ... }` block
3. Rename to your language code (e.g., `it`, `ja`, `ko`, `ar`, `hi`, `nl`, `pl`)
4. Translate every value (UI strings, topic titles, all step arrays)
5. Update `meta.dateLocale` (e.g., `"ja-JP"`)
6. Add a flag emoji to `meta.flag`
7. Save → reload → language appears in picker

**Translation tip**: AI translation is fine for v1, but get a native speaker to review before marketing in that language. Bad translations are worse than English for the elderly audience.

For RTL languages (Arabic, Hebrew): add `dir="rtl"` to `<html>` when those languages are active. Also consider logical CSS properties if you expand.

## Validate demand FIRST, monetize LATER

This is the right approach. Here's what the app already measures:

### Built-in signals (no setup required)
1. **Email captures** — saved to `state.emails[]` in localStorage. Pull from dev tools: `JSON.parse(localStorage.getItem('buddy-state-v2')).emails`
2. **Visit frequency** — `state.visits[]` array of unique day strings. Use this to measure stickiness.
3. **Feedback** — `state.feedback[]` with `{date, rating, text}`. Real signal from real users.

### Server-side tracking (add later when worth it)

For multi-device tracking, add a tiny Cloudflare Worker or similar:
```js
// On every page load, fire-and-forget a beacon
const beacon = navigator.sendBeacon.bind(navigator);
beacon('/api/track', JSON.stringify({
  lang: state.lang,
  visits: state.visits.length,
  people: state.people.length,
  meds: state.meds.length,
  hasEmail: state.emails.length > 0,
  feedback: state.feedback.map(f => f.rating),
  ua: navigator.userAgent.slice(0, 80)
}));
```

Or simpler: drop in **Plausible Analytics** (privacy-friendly, no cookies, GDPR-safe). It's free for sites under 10k views/mo.

### Decision thresholds for monetization

| Signal | Threshold | Action |
|--------|-----------|--------|
| Email captures | 100 | Add Stripe for $7/mo tier |
| Daily unique visitors | 50 | Add affiliate links (phones for seniors) |
| Repeat-visit rate >40% | — | Safe to invest in family dashboard feature |
| Feedback "hard" >30% | — | UX fix sprint before any monetization |

## Soft monetization options (work even while free)

Don't wait for a paid tier — these start earning immediately:

1. **Affiliate links** (in the upgrade banner or footer)
   - Jitterbug / Lively smartphones (~$20-40 per sale)
   - Consumer Cellular / Mint Mobile plans ($5-25 per signup)
   - Hearing-aid compatible phones
   - Large-print phone cases on Amazon

2. **"Buy Me a Coffee" or Ko-fi** button in the footer
   - Senior users won't use it, but their adult children will when they share the app
   - Honest framing: "Help keep Buddy free for seniors"

3. **Setup service** ($29 one-time)
   - Adult children pay you to do a 30-min video call and enter their parent's contacts/meds
   - Highest-margin product, scales with your time
   - Sell via Fiverr, TaskRabbit, or directly on your site

4. **B2B white-label** (later)
   - Senior living facilities pay $50-200/mo per facility
   - Don't pursue this until you have 1000+ free users as proof

## When to add a paid tier

The trigger is **demand exceeds free-tier capacity**:
- Users asking for more contacts → unlock unlimited contacts in Pro
- Users asking for family dashboard → build sync + dashboard
- Users asking for AI scam check → swap pattern matching for Claude API
- Users wanting cross-device sync → build backend

**Don't add payments before you have a clear "I would pay for this" signal.**

## Marketing plan (drives usage)

### SEO — one post per language per topic
Each language opens new keyword territory. Quick wins:
- 🇺🇸 "how to help parents with technology"
- 🇪🇸 "cómo ayudar a mis padres con la tecnología"
- 🇫🇷 "comment aider mes parents avec la technologie"
- 🇩🇪 "wie kann ich meinen Eltern Technik beibringen"
- 🇧🇷 "como ajudar meus pais com tecnologia"
- 🇨🇳 "如何教父母使用智能手机"

Write 2-3 posts per language, each linking to Buddy. That's 12-18 posts = months of content.

### Reddit (free, high-converting)
- 🇺🇸 r/agingparents, r/CaregiverSupport, r/digitalminimalism, r/sysadmin
- 🇪🇸 r/ConsejosLegales, r/Mexico, r/es
- 🇫🇷 r/france, r/Quebec
- 🇩🇪 r/de, r/Fragezeichen
- 🇧🇷 r/desabafos, r/brasil
- 🇨🇳 r/China_irl (English-language Chinese subreddit)

Genuinely help first. Mention Buddy once.

### YouTube (long-tail SEO)
- "How to set up Buddy for your mom"
- "5 scams targeting seniors in 2026"
- One per language if you want (use your own voice for native)

### Partnerships
- Senior centers (free setup workshops)
- AARP local chapters
- Church groups
- Local estate attorneys (referral fee)
- Caregiver support groups

## Privacy & trust (critical for this audience)

State prominently on the site:
- "We don't sell your data. Ever."
- "All your contacts and medicines stay on your phone."
- "No ads. No tracking pixels."
- "Family dashboard requires explicit consent."
- "You can delete everything with one tap."

This is your biggest competitive moat against VC-funded competitors.

## Tech

- Vanilla HTML / CSS / JavaScript
- `localStorage` for state persistence
- Mobile-first responsive (tested iPhone Safari, Android Chrome)
- WCAG AA accessibility (18px+ base, 48px+ targets, 4.5:1 contrast)
- Works offline once loaded

## License

Your call. Keep it private to protect your marketing position. Open-source later if you want a community around it.

---

**Next step**: drop these 4 files in `/public_html/buddy/` on your host. Write your first SEO post in your strongest language linking to it. Watch the `state.emails[]` count grow. When it crosses 100, add Stripe.