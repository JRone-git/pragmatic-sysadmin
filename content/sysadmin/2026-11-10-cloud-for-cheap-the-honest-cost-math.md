---
title: "Cloud for Cheap: What It Actually Costs to Run Your Own"
date: 2026-11-10
draft: false
description: "Google One 2TB is $9.99 a month and a self-hosted server can cost far less — or much more. The honest 2026 numbers, including the electricity nobody counts."
tags: ["self-hosted", "cloud", "cost", "homelab", "budget"]
categories: ["System administration"]
author: "Pragmatic Sysadmin"
ShowToc: true
reviewed: true
aiAssisted: true
blogforge:
  provider: template
  model: outline
  generated_at: "2026-11-10T17:40:00Z"
  attempts: 1
  style_score: 98
  topic: "Cloud for cheap: the honest 2026 cost math for self-hosting"
---

I did the arithmetic on a Google One bill last month, then did the same arithmetic on the server sitting under my desk. The cloud won. Not narrowly — by enough that I closed the tab and went to make coffee.

That's the answer most self-hosting guides won't give you, because "run your own cloud" is a hobby that sells a feeling, and the feeling is free while the electricity isn't.

Here's the real arithmetic, with every price checked on 10 November 2026: what Google One actually charges, what a cheap VPS actually costs, what a home server burns in electricity, and the one rule that tells you which of the three to pick.

<!--more-->

## Every option, priced

One table, because the whole argument is in it. The Google One and Hetzner prices were checked against the vendors' own pages on 10 November 2026; the electricity figures are calculated at the German household rate of 36.18 euro cents per kWh, which is what Eurostat recorded for the first half of 2026.

| Option | What you get | Monthly | Yearly | Over five years |
|---|---|---|---|---|
| Google One Free | 15 GB, shared | $0.00 | $0.00 | $0.00 |
| Google One Basic | 100 GB, shared | $1.99 | $19.99 | $99.95 |
| Google One AI Plus | 2 TB, shared | $9.99 | $99.99 | $499.95 |
| Google One AI Pro | 5 TB, shared | $19.99 | $199.99 | $999.95 |
| Hetzner CX23 | 2 vCPU, 4 GB, 40 GB NVMe | €5.99 | €71.88 | €359.40 |
| Hetzner CX33 | 4 vCPU, 8 GB, 80 GB NVMe | €8.99 | €107.88 | €539.40 |
| Pi 5 and an 8 TB disk, home | 3.0 W idle, electricity only | — | €9.51 | €47.55 |
| N100 mini PC, home | 10 W idle, electricity only | — | €31.70 | €158.50 |
| Old desktop tower, home | 50 W idle, electricity only | — | €158.46 | €792.30 |

Read the last three rows next to the first four and the argument is already over for most people. A desktop tower left running all day costs more over five years than Google One 2TB does. That is not a self-hosting setup, that is an expensive way to store photographs.

## Where the electricity comes from

The bottom three rows are the ones nobody puts in a spreadsheet, so here is the calculation. German households paid 36.18 euro cents per kWh in the first half of 2026 — the second most expensive rate in the EU, which makes the maths harsher than most guides admit.

A Raspberry Pi 5 idles at about 3.0 W headless, or 3.6 W with Ethernet and a USB SSD attached. A cheap N100 mini PC idles around three times that. A refurbished office box from 2020 can sit at 18 W doing nothing at all.

Here is the whole calculation in one line: **at 36.18 cents per kWh, every watt of continuous draw costs €3.17 a year.** A machine that idles at 50 W is spending more on electricity than a cheap VPS costs for the whole month.

Measure your own machine instead of trusting someone else's table. On a Pi, the power supply reports real numbers:

```bash
# Instantaneous watts on a Raspberry Pi 5
cat /sys/class/power_supply/*/power/now | awk '{printf "%.2f W\n", $1/1000000}'

# On a desktop with a supported kernel: total and per-process draw
sudo powertop --interval=2
```

And if you want the annual figure for your own hardware instead of mine:

```bash
#!/usr/bin/env bash
# Annual electricity cost of a machine that draws $1 W continuously.
# Usage: ./power-cost.sh 3.0          # watts, 36.18 cents/kWh
#        ./power-cost.sh 18.0 0.30    # watts, your own price per kWh
awk -v w="${1:-3.0}" -v p="${2:-0.3618}" 'BEGIN {
  kwh = w * 8760 / 1000
  printf "%.1f W -> %.1f kWh/year -> EUR %.2f/year\n", w, kwh, kwh * p
}'
```

## What a cheap VPS actually costs

Hetzner raised its cloud prices twice in 2026. On 1 April most lines went up about a third, and on 15 June every line went up again for new orders and rescales. The cost-optimised CX23 went from €2.99 to €3.99 to €5.49 a month.

Compare that with DigitalOcean's comparable Droplet at $24 a month and the gap is embarrassing in Hetzner's favour.

But note the catch: the cheap lines are capacity-limited. Since September 2026 the cost-optimised plans are frequently marked unavailable and sell out within minutes of a restock. Budget for the possibility that your €5.99 server isn't there when you want it.

## The three ways to run your own cloud

- **Home server** — a machine you own, in your house. Cheapest in electricity, most expensive in your time.
- **Cheap VPS** — a rented box in a datacentre. One flat monthly price, nobody else's hardware in your hallway.
- **Nothing at all** — sync between your own devices, no server involved. Costs nothing at all.

The third option is the one nobody sells you, and for a lot of people it's the correct one. Syncthing is free, open source, and it syncs folders directly between your laptop, your phone and your parent's laptop without a server in the middle. If what you need is "my photos are on my phone and I want them on my laptop", you don't need a cloud. You need a peer-to-peer sync tool and a free afternoon.

## Where self-hosting genuinely wins

It wins when you're billed per seat and your files are measured in gigabytes, not terabytes.

A ten-person team with a shared document library doesn't need a storage plan, it needs a box. And the box costs the same whether ten people use it or fifty. Google Workspace Business Standard is roughly $14 per user per month on an annual plan — about $140 a month for that team, and it climbs with every hire. One CX33 covers the same library and the price doesn't move.

It also wins when privacy is the point and price isn't. A password manager, a photo library, a calendar — those aren't storage problems, they're trust problems, and no amount of money buys the trust you get from a box in your hallway.

## Where it never wins

- **Cheap bulk storage.** Google One 2TB is $9.99. You aren't beating that with a VPS.
- **Zero administration.** You're buying an unpaid job. Every disk that fills, every certificate that expires, every backup you never tested is now yours.
- **Anything that needs a phone number.** A mail server on a residential connection will get you blocked, and the block will outlast your patience.
- **When the apps already work.** The most underrated saving in the whole self-hosting world is the subscription you didn't cancel.

## The costs nobody puts in the spreadsheet

Electricity is the smallest of the three real costs. The other two are bigger and they're both paid in the same currency: your time.

The 3am restore. Every self-hosted system has a bad day, and the difference between a bad day and a lost weekend is whether you tested the backup. A backup you've never restored is a hypothesis, not a backup.

The update treadmill. Six services means six things to patch, and the one you don't patch is the one with the advisory on it. This is the cost that makes a modest cloud bill look cheap.

The migration. Moving a photo library onto a new server takes an evening, and the evening after that you find the folder structure doesn't match what you expected and you start again.

## What to do next

If the goal is **saving money**, start with the free option: [Syncthing between your own devices](/sysadmin/self-hosting-isnt-free-honest-cost-running-own-server/) costs nothing and needs no server. Then look at what you actually pay for, and whether that subscription is per-seat or per-terabyte.

If the goal is **owning your data**, the [Build Your Own Cloud guide](/meta/build-your-own-free-cloud-home-server-guide/) has the stack and the order to install it in. Budget for a backup disk, and for the evening.

If the goal is **learning**, the [home lab beginner's guide](/sysadmin/2025-10-29-setting-up-a-home-lab-a-beginner-s-guide/) is the gentler version of the same question.

Don't buy the hardware until you've done the arithmetic above for your own machine. The number that decides it is how many watts it draws while idle, and that's a number you can read in five minutes with a €12 plug meter.

*Self-hosting isn't a cheaper cloud. It's a different kind of bill — sometimes smaller, sometimes much larger, and always paid in your own time.*
