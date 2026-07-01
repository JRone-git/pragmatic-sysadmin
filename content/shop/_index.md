---
title: "Shop — Sysadmin Tools & Scripts"
date: 2026-06-30T10:00:00.000Z
description: "Free scripts and paid toolkits for sysadmins. All MIT licensed, all owned by you forever. Tools for server monitoring, SSL checking, backup verification, home labs, and more."
author: "Pragmatic Sysadmin"
---

# Shop

**Production-ready tools for sysadmins.** All MIT licensed, all owned by you forever. No subscriptions, no SaaS, no telemetry. Just scripts and guides you can actually use.

<div style="background:linear-gradient(135deg, #FBF6EE 0%, #FDFAF4 100%);border:2px solid #B7D4BE;border-radius:18px;padding:1.5rem;margin:1.5rem 0;text-align:center;">

<p style="margin:0 0 1rem 0;font-family:'Lora',serif;font-size:1.125rem;color:#2A2520;font-weight:600;">
  ☕ <strong>All paid products sold via Ko-fi</strong> — instant download, no account needed
</p>

<a href="https://ko-fi.com/s/5157a41780" style="display:inline-block;background:#FF5E5B;color:white;padding:0.875rem 2rem;border-radius:999px;font-weight:700;font-size:1rem;text-decoration:none;margin:0.25rem;">🛒 Visit Ko-fi Shop</a>
<a href="https://ko-fi.com/sysadmin_dad" style="display:inline-block;background:transparent;color:#FF5E5B;border:2px solid #FF5E5B;padding:0.75rem 1.75rem;border-radius:999px;font-weight:700;font-size:1rem;text-decoration:none;margin:0.25rem;">☕ Tip Jar</a>

</div>

---

<a id="free-tools"></a>
## 🆓 Free Tools — Start Here

**Grab these first. No email required. No signup. Just scripts.**

These solve one specific problem each. Use them forever, modify them freely. When you outgrow them, the paid toolkits below go deeper.

### 🔒 [SSL Certificate Expiry Checker](/tools/free/ssl-cert-checker/)

**Find certificates about to expire before they break your site**

A simple bash script that checks SSL certificate expiry dates for
one or more domains and alerts you if they're expiring soon.
Exit codes make it perfect for cron + monitoring integration.

```bash
./ssl-cert-checker.sh -f domains.txt
```

[Get the script →](/tools/free/ssl-cert-checker/) · [Download the whole pack](https://pragmaticsysadmin.help/downloads/free-tools-pack.zip)

---

### 🔍 [Log Pattern Search with Context](/tools/free/log-tail-search/)

**Find errors across multiple log files in seconds**

Search multiple log files for patterns with surrounding context lines.
Smart time-range filtering, case-insensitive option, and color output
make debugging much faster than grep + manual context-finding.

```bash
./log-tail-search.sh -p "Failed password" -s 24h -i
```

[Get the script →](/tools/free/log-tail-search/) · [Download the whole pack](https://pragmaticsysadmin.help/downloads/free-tools-pack.zip)

---

### 🔑 [SSH Key Security Auditor](/tools/free/ssh-key-auditor/)

**Find weak keys, suspicious restrictions, and bad permissions**

Audit SSH keys across all user accounts. Reports every authorized
key with type and length, flags weak DSA/short RSA keys, finds
private keys with world-readable permissions.

```bash
sudo ./ssh-key-auditor.sh      # includes /root
```

[Get the script →](/tools/free/ssh-key-auditor/) · [Download the whole pack](https://pragmaticsysadmin.help/downloads/free-tools-pack.zip)

---

### 📊 [Disk Quota Checker](/tools/free/disk-quota-checker/)

**Find who's using the most disk on shared systems**

Find top disk space users on shared /home or any other directory.
Auto-flags users over 10GB as cleanup candidates. Useful for
finding runaway logs, large Docker workloads, or old data.

```bash
sudo ./disk-quota-checker.sh -d /var/www -n 20
```

[Get the script →](/tools/free/disk-quota-checker/) · [Download the whole pack](https://pragmaticsysadmin.help/downloads/free-tools-pack.zip)

---

### 🔄 [Safe Service Restart](/tools/free/service-restart-tamer/)

**Restart services with pre-checks and rollback guidance**

Restart a systemd service safely. Records state before restart,
runs your custom health check before and after, waits for the
service to come back up, and prints recent logs if something fails.

```bash
./service-restart-tamer.sh postgresql --wait 30
```

[Get the script →](/tools/free/service-restart-tamer/) · [Download the whole pack](https://pragmaticsysadmin.help/downloads/free-tools-pack.zip)

---


<a id="paid-toolkits"></a>
## 💎 Paid Toolkits — The Full Solutions

**For when you need more than one script.** Each toolkit bundles multiple scripts + documentation + decision trees, all from a real-world-tested workflow.

### [The 5-Minute Server Health Check Toolkit](/products/health-check-toolkit/) — **$9**

<img src="/images/health-check-toolkit-card.png" alt="The 5-Minute Server Health Check Toolkit" style="width:100%;max-width:320px;border-radius:12px;margin:0.75rem 0;box-shadow:0 4px 14px rgba(95,60,30,0.12);" />

**Catch problems before they page you at 3am**

linux, sysadmin, monitoring, server

[Read full description →](/products/health-check-toolkit/) · [Buy on Ko-fi →](https://ko-fi.com/s/5157a41780)

---


## How it works

**Free tools:**
1. Click any free tool → read the description
2. Copy the script (or download the pack)
3. Use forever — MIT licensed

**Paid toolkits:**
1. Click any paid toolkit → read the full description
2. Click "Buy on Ko-fi" → instant payment, no account needed
3. Receive the download link immediately
4. Use forever — MIT licensed
5. 60-day no-questions refund

## Why these prices are low

- $9-19 feels right for scripts that took real time to write and test
- Low prices = impulse buys = more sales = more word-of-mouth
- You get a working tool, I get to keep making tools. Win-win.

## What you won't find here

- ❌ No monthly subscriptions
- ❌ No SaaS dashboards
- ❌ No telemetry phoning home
- ❌ No "premium" tiers gating basic features
- ❌ No accounts required

You own what you buy. Modify it. Redistribute it. Use it in your team. It's yours.

## Questions?

Email [pragmatic@pragmaticsysadmin.help](mailto:pragmatic@pragmaticsysadmin.help)

Or tip what you want at [https://ko-fi.com/sysadmin_dad](https://ko-fi.com/sysadmin_dad) if you find the free content useful.
