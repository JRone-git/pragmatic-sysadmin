---
title: "The 5-Minute Server Health Check Toolkit — $9"
date: 2026-06-28T18:00:00.000Z
description: "A complete weekly server health check system for Linux sysadmins. Three bash scripts, a one-page printable checklist, and a 'what to do when something's red' decision tree. $9 one-time, no subscription, no SaaS — you own the scripts forever."
author: "Pragmatic Sysadmin"
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "The 5-Minute Server Health Check Toolkit",
  "description": "A complete weekly server health check system for Linux sysadmins. Three production-ready bash scripts, a printable weekly checklist, and a decision tree for every warning.",
  "brand": {
    "@type": "Brand",
    "name": "Pragmatic Sysadmin"
  },
  "offers": {
    "@type": "Offer",
    "price": "9.00",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock"
  }
}
</script>

# The 5-Minute Server Health Check Toolkit

**Catch problems before they page you at 3am. $9, one-time, you own it forever.**

A complete weekly health check system for Linux servers. Three production-ready bash scripts, a printable weekly checklist, and a decision tree for every warning the scripts can throw at you.

Based on the popular blog post [The 5-Minute Server Health Check That Could Save Your Career](https://pragmaticsysadmin.help/posts/the-5-minute-server-health-check-that-could-save-your-career/), expanded into a tool you can actually use every Monday.

<div style="text-align:center;margin:2rem 0;">
  <a href="#buy" style="display:inline-block;background:#2D6A4F;color:white;padding:1.125rem 2rem;border-radius:999px;font-weight:700;font-size:1.125rem;text-decoration:none;box-shadow:0 4px 14px rgba(45,106,79,0.25);">⬇️ Get the Toolkit — $9</a>
</div>

---

## What's in the box

```
health-check-toolkit/
├── quick-health-check.sh   ← main script, run this weekly
├── disk-analyzer.sh        ← when disk is filling up, find what's eating it
├── log-watcher.sh          ← alert when error patterns spike
├── weekly-checklist.md     ← one-page printable checklist
├── what-to-do-when-red.md  ← decision tree for every red flag
└── README.md               ← 60-second setup + cron examples
```

**3 bash scripts** that you can run today on any Linux box. **No dependencies to install.** No frameworks. No SaaS subscription. No telemetry phoning home. You own the scripts, you read the code, you modify them if you want.

**The weekly checklist** is a single markdown file formatted to print on one page. Tape it next to your monitor. Run it every Monday at 8am.

**The "what to do when red" decision tree** walks you through every warning the scripts can throw. Disk at 90%? Memory leak? Load average spike? Service failed? Each has a documented path to resolution.

---

## What the main script checks

Run `./quick-health-check.sh` and you get a complete health snapshot in under 5 seconds:

- **Disk space** — usage %, free space, top 5 largest directories under any path you choose
- **Memory** — usage %, swap activity, OOM detection
- **CPU load** — vs your actual CPU count, top 5 consumers
- **Recent errors** — error count in syslog/messages over the last hour
- **Network** — connectivity to 1.1.1.1 and 8.8.8.8, listening sockets
- **Uptime** — days up, with warning at 90+ days
- **Failed systemd units** — count of services that won't start

Run it with `--json` for monitoring integration. Run it with `--quiet` to only see problems.

**Sample output:**

```
Server Health Check — web-prod-01
Sun Jun 28 08:00:01 UTC 2026  ·  Uptime: up 12 days, 4 hours

Disk Space
  ✓ Disk usage (/): 47%  (235G free of 450G)
  Top 5 largest dirs in /:
    180G   /var
     45G   /usr
     12G   /home
     ...

Memory
  ✓ Memory usage: 62%  (15820MB / 24000MB)
  ✓ Swap usage: 8%  Normal

CPU & Load
  ✓ Load average (1m): 0.8  Normal
  Top 5 CPU consumers:
    12345 www-data   12%  php-fpm
    ...

========================================
All checks passed
```

Exit codes: `0` = clean, `1` = warnings, `2` = critical. Use in cron + monitoring with confidence.

---

## What it's not

- ❌ Not a SaaS. Nothing phones home. No accounts.
- ❌ Not an agent. Nothing installs as a daemon.
- ❌ Not an enterprise monitoring platform. If you want Datadog, buy Datadog.
- ❌ Not magic. It's a 5-minute check, not a full APM solution.
- ❌ Not Windows-compatible. Linux only.

---

## Who this is for

- **Solo sysadmins** managing 5-50 servers who need a weekly check that doesn't take all morning
- **Small IT teams** that want a shared baseline checklist
- **Junior sysadmins** learning what to look for on a Linux server
- **Anyone running a homelab** with services that matter to them

If you have a real monitoring platform already, this toolkit is for the Mondays when you want a human-readable sanity check. If you don't have monitoring at all, this toolkit is your Monday morning ritual until you do.

---

## How to get it

**Price: $9 USD, one-time.**

You'll get:
- Instant download of `health-check-toolkit.zip` (12 KB, all 6 files)
- Free updates for life (subscribe at the same link, get notified)
- A 60-day no-questions refund if it doesn't help

<a id="buy"></a>

<div style="text-align:center;margin:2rem 0;padding:2rem;background:#FDFAF4;border:2px solid #B7D4BE;border-radius:18px;">
  <h3 style="margin-bottom:0.5rem;">Ready to buy?</h3>
  <p style="margin-bottom:1.5rem;">Pay $9 via Ko-fi, get the zip instantly. No account needed.</p>

  <!-- REPLACE THIS LINK WITH YOUR KO-FI SHOP URL AFTER SETUP -->
  <a href="https://ko-fi.com/pragmatic_sysadmin/shop" style="display:inline-block;background:#FF5E5B;color:white;padding:1.125rem 2.5rem;border-radius:999px;font-weight:700;font-size:1.1875rem;text-decoration:none;box-shadow:0 4px 14px rgba(255,94,91,0.25);">☕ Buy on Ko-fi — $9</a>

  <p style="margin-top:1.5rem;font-size:0.9375rem;">Or tip what you want: <a href="https://ko-fi.com/pragmatic_sysadmin">ko-fi.com/pragmatic_sysadmin</a></p>
</div>

---

## Frequently asked questions

**Q: Does this work on macOS?**
A: No — it's Linux only. The scripts assume `/proc`, `systemctl`, `ss`, and standard Linux tools. macOS doesn't have these.

**Q: Do I need root access?**
A: For the basic checks (disk, memory, CPU, logs), no. For the systemd unit check, yes. The scripts gracefully degrade when run as non-root.

**Q: Can I modify the scripts?**
A: That's the whole point. They're yours. MIT licensed. Rename them, tweak the thresholds, add checks — whatever helps.

**Q: Will this work in my monitoring platform (Nagios, Zabbix, Datadog)?**
A: Yes — the `--json` output flag gives you machine-readable results. Exit codes tell you severity (0/1/2). Wrap it in whatever you already use.

**Q: How is this different from the blog post?**
A: The blog post is the philosophy and the high-level steps. The toolkit is the implementation — three runnable scripts, a printable checklist, and a decision tree for every warning. The blog post gets you 30% of the way there; the toolkit gets you 100%.

**Q: Can I get a refund?**
A: Yes, 60-day no-questions refund. Email pragmatic@pragmaticsysadmin.help.

---

## What people are saying

> "I run this every Monday now. Caught a runaway log file before it filled the disk. Saved me a Saturday of cleanup work."
> — *placeholder testimonial, will be replaced when real ones come in*

---

## License & support

MIT licensed — use, modify, redistribute. If it saves your bacon, [buy me a coffee](https://ko-fi.com/pragmatic_sysadmin) or [drop me a testimonial](mailto:pragmatic@pragmaticsysadmin.help).

Bug reports: pragmatic@pragmaticsysadmin.help

---

*Part of the [Pragmatic Sysadmin](https://pragmaticsysadmin.help) tool library — built to make sysadins sleep better at night.*