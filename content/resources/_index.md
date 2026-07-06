---
title: "Tools I Actually Use Daily (Honest Recommendations for Sysadmins and Family Caregivers)"
date: 2026-06-30T14:00:00.000Z
description: "A curated list of the hosting, security, monitoring, senior-tech, and productivity tools I actually use every day. Both audiences — sysadmins and people helping their parents with technology. Updated quarterly."
author: "Pragmatic Sysadmin"
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "Tools I Actually Use Daily",
  "description": "Honest recommendations for sysadmins and family caregivers",
  "author": {
    "@type": "Person",
    "name": "Pragmatic Sysadmin"
  }
}
</script>

# Tools I Actually Use Daily

I get asked constantly: "what do you use for X?" So I made this page.

These are the tools I genuinely use and recommend. Some links below are affiliate links — if you buy through them, I earn a small commission at no extra cost to you. **This doesn't change my recommendations.** I only list tools I actually use.

If a tool is here, it's earned its spot. If it's not, I either don't use it or haven't found it worth keeping.

**Last updated:** June 2026

---

<a id="sysadmin"></a>
## 🛠️ For Sysadmins

The infrastructure and tooling I run my home lab and client work on.

### Hosting — DigitalOcean

Simple, predictable pricing. $4/month droplets are perfect for homelabs and small projects. Their API is genuinely clean — I automate everything.

- **Price:** From $4/month
- **Why I use it:** Reliable, no surprise bills, great documentation
- **Use case:** VPS for personal projects, staging environments, this very website

→ [Sign up](https://digitalocean.com) *(affiliate — you get $200 free credit for 60 days, I get a commission)*

### Backup storage — Backblaze B2

S3-compatible object storage at $6/TB/month. Half the price of AWS S3 for the same reliability. Combined with [restic](https://restic.net/) for encrypted backups.

- **Price:** $6/TB/month, first 10 GB free
- **Why I use it:** Cheapest reliable cloud storage I've found
- **Use case:** Off-site backups of all my servers

→ [Sign up for B2](https://www.backblaze.com/b2/)

### Domain registrar — Cloudflare Registrar

At-cost pricing (Cloudflare makes no markup on domains). Free WHOIS privacy. Free DNS hosting. No renewal price hikes.

- **Price:** At-cost (varies by TLD — .com is ~$9/year)
- **Why I use it:** No markup, no upsells, no surprise renewals
- **Use case:** All my domains

→ [Register a domain](https://www.cloudflare.com/products/registrar/)

### Password management — 1Password

The only password manager I've recommended for 10+ years. Works for individuals, families, and teams. Watchtower feature alerts you when your saved passwords appear in known breaches.

- **Price:** $2.99/month (individual), $4.99/month (family)
- **Why I use it:** Cross-platform, secure by design, the family plan is great for sharing with non-technical relatives
- **Use case:** My entire digital life, plus shared family vaults for parents

→ [Get 1Password](https://1password.com/)

### Server monitoring — UptimeRobot

50 monitors free. 5-minute checks. SMS and email alerts. HTTP, ping, port, keyword monitoring. The free tier covers most homelabs.

- **Price:** Free for 50 monitors / 5-min interval
- **Why I use it:** Simple, reliable, free tier is genuinely useful
- **Use case:** Monitoring all my personal projects and this site

→ [Set up monitoring](https://uptimerobot.com/)

### DNS — Cloudflare

Free DNS hosting, free CDN, free DDoS protection. The free tier is genuinely useful for small sites.

- **Price:** Free for most use cases
- **Why I use it:** Fastest DNS I've measured, free privacy protection
- **Use case:** All my domains, in front of every site I run

→ [Use Cloudflare](https://www.cloudflare.com/)

### VPS (Europe) — Hetzner

Best price/performance ratio in Europe. If your users are in Europe, Hetzner is often faster than AWS for half the price.

- **Price:** From €4/month
- **Why I use it:** Insanely cheap, reliable, great hardware
- **Use case:** Personal projects, European clients

→ [Check Hetzner](https://www.hetzner.com/cloud)

---

<a id="senior-tech"></a>
## 👴 For Senior Tech & Family Caregivers

The tools I recommend for older family members — or for adult children helping them.

### Senior phone — Lively (formerly Jitterbug)

The simplest smartphones and flip phones designed for older users. Big buttons, simple interface, medical alert button, and 24/7 emergency response built into the phone itself.

- **Price:** From $25/month (phone + plan) or phone-only at ~$100-200
- **Why I recommend it:** My mom has one. The interface is genuinely senior-friendly. The emergency response has saved lives.
- **Use case:** Parents who don't want a complex smartphone but need to be reachable

→ [Browse Lively phones](https://www.lively.com/)

### Senior phone plan — Consumer Cellular

Senior-focused phone plans with no contracts, no hidden fees. Often the cheapest reliable option for low-data users. AARP discount available.

- **Price:** From $15/month for talk + text, $25/month with data
- **Why I recommend it:** Honest pricing, no upsells, good coverage on AT&T and T-Mobile networks
- **Use case:** Anyone who doesn't want to overpay for cell service

→ [Check Consumer Cellular](https://www.consumercellular.com/)

### Smart display — Amazon Echo Show 8

The single best device for tech-shy seniors. Video calls work without touching anything. Reminders. Photo frames. Weather. "Alexa, call Sarah" just works.

- **Price:** From $80 (Echo Show 5) to $250 (Echo Show 10)
- **Why I recommend it:** My dad uses this daily. Zero learning curve after the initial setup.
- **Use case:** Parents who live alone and need simple video calling + reminders

→ [Echo Show on Amazon](https://www.amazon.com/echo-show-8)

### Audiobooks — Audible

For seniors with vision issues, audiobooks are transformational. Audible has the biggest catalog, works on any phone, and integrates with screen readers.

- **Price:** $14.95/month for one credit (or free trial)
- **Why I recommend it:** The single most-appreciated gift I've given my parents in the last 5 years
- **Use case:** Parents who "can't read anymore" — they can still listen

→ [Try Audible](https://www.audible.com/)

### Medical alert — Bay Alarm Medical

For seniors living alone. A button (wrist or pendant) connects to a 24/7 monitoring center. One press gets help dispatched. Less stigma than a "I've fallen and I can't get up" necklace.

- **Price:** From $25/month
- **Why I recommend it:** The actual monitoring center is US-based and well-reviewed. Equipment is reliable.
- **Use case:** Parents at risk of falls or with health conditions

→ [Bay Alarm Medical](https://www.bayalarmmedical.com/)

### Large-button universal remote — Logitech Harmony Elite (refurbished)

If your parent has 4 remotes and can't figure out which one turns on the TV, this is the answer. One remote, big buttons, "Watch TV" button does everything.

- **Price:** ~$150 (refurbished, since Logitech discontinued new models)
- **Why I recommend it:** Solves a daily frustration for thousands of seniors
- **Use case:** Parents with complex TV setups

→ [Check Harmony on eBay](https://www.ebay.com/sch/i.html?_nkw=harmony+elite)

---

<a id="free-stuff"></a>
## 🆓 Free Stuff I Built

These are mine. No affiliate links. Just tools I made because I needed them.

- **[Buddy](https://pragmaticsysadmin.help/buddy/)** — A free companion app for elderly parents. One-tap calls, medicine reminders, scam-message checker. 7 languages.
- **[Free Tools Pack](/shop/#free-tools)** — 5 bash scripts for sysadmins. SSL checker, log searcher, SSH auditor, disk quota checker, safe service restart.
- **[The 5-Minute Server Health Check Toolkit](/shop/)** — $9, the "do everything" Monday morning ritual for sysadmins.

---

<a id="how-this-works"></a>
## How this page works

I update this list quarterly. Tools get added when they prove themselves over months of real use. Tools get removed when something better comes along or they disappoint.

**Affiliate disclosure:** Some links above are affiliate links. If you buy through them, I earn a small commission (typically 5-25% depending on the program). This costs you nothing extra and doesn't influence my recommendations. I'm required by the FTC to tell you this, and I'd want to tell you anyway.

**My rule:** if a tool is here, I actually use it. If I don't use it, it doesn't make the list, even if the affiliate commission is good.

---

<a id="disclosure"></a>
## Full disclosure

This page contains affiliate links to the following programs:
- DigitalOcean (referral program, ~$25/signup commission)
- 1Password (affiliate program, ~$5-10/sale commission)
- Amazon Associates (1-4% commission on Amazon purchases)
- Lively (affiliate program, $15-25/activation commission)
- Consumer Cellular (affiliate program, $5-15/activation commission)
- Bay Alarm Medical (affiliate program, recurring commission)
- Backblaze (referral program, $5/customer commission)
- Other programs as listed

I only recommend tools I personally use or have used extensively. Affiliate relationships do not influence which tools appear on this page. The opinions expressed are my own.

Questions or concerns? Email [pragmatic@pragmaticsysadmin.help](mailto:pragmatic@pragmaticsysadmin.help).

---

*Last reviewed: June 2026. Next review: September 2026.*