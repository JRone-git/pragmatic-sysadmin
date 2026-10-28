---
title: "Tech in a Busy Household: Balancing Home Networks, Gaming Rigs, and DIY Tinkering"
date: 2026-10-28
author: "Pragmatic Sysadmin"
description: "A practical guide to running a home network with gaming PCs, smart home, kids' devices, and your own homelab projects in it. Segmentation, QoS, IP management, and a tinkering budget that keeps the family online."
draft: false
tags: ["networking", "homelab", "gaming", "wifi", "router", "qos", "home-lab"]
slug: tech-in-a-busy-household-networks-gaming-rigs-diy-tinkering
topics: ["networking", "homelab"]
---

My home network serves four separate humans, two cats, a Nintendo Switch, three streaming devices, a NAS, a homelab in the closet, and an unreasonable number of Raspberry Pis.

It also serves a PlayStation 5 that's downloading a 90GB game update at 9 PM, while my wife is on a work call from the kitchen, while I'm restarting a service I broke twenty minutes ago.

None of these things are hard individually. All of them at once is how you end up with a router you want to throw out of a window.

This is how I keep it all working.

<!--more-->

## Start With the Actual Problem

The failure isn't "the internet is slow." It's four specific problems, and they need four different fixes:

| Symptom | Real cause | Fix |
|---|---|---|
| "The game lags at 8 PM" | Everyone's device competing for the same pipe | **QoS / traffic prioritisation** |
| "The kids got onto the NAS" | Flat network, everything can reach everything | **Segmentation (VLANs)** |
| "The camera moved to a new IP" | DHCP lease changed | **DHCP reservations** |
| "My project broke the internet" | Experimenting on the production network | **A tinkering budget + a lab setup** |

Most router admin pages get buried because people try to fix symptom #2 with a fix for symptom #1. QoS won't stop the kids reaching the NAS. VLANs won't fix lag. You need all four.

---

## 1. Segmentation: Split the Flat Network

**The default home network treats every device the same.** Your NAS, the smart fridge, the kids' Xbox, your work laptop, and a guest's phone can all reach each other, any time, with no credentials.

That stops being theoretical the moment a smart TV gets compromised through some random CVE. Then it's on your NAS, and your NAS has your photos and your backups.

### The segmentation I'd actually build

| Network | Devices | Rules |
|---|---|---|
| **Trusted** | Your phone, laptop, NAS | Full access to everything |
| **IoT** | Smart bulbs, cameras, plugs, TV | Internet only. Can reach the DNS server. Nothing else. |
| **Kids** | Consoles, tablets, their PCs | Internet + local game traffic. **Cannot reach the NAS, the homelab, or the printers.** |
| **Guest** | Visitor phones, IoT guests | Internet only, client isolation on, can't see the local network at all |
| **Work** | Work laptop, if you work from home | Internet + whatever you need. Kept separate so a work compromise doesn't reach your homelab. |

Five networks, five SSIDs, one router that understands VLANs. Everything on its own subnet.

**Why this matters in practice:**
- Your kid's console can't see your NAS, so a pirated game on the Xbox can't try to browse your photos
- The smart TV can't reach your laptop, so the last TV that got a worm can't try to spread
- A guest on the guest Wi-Fi is completely isolated — no seeing the printer, no reaching the router
- If one of your own devices gets infected, the blast radius is one VLAN instead of the whole house

### Doing this without spending a fortune

**Budget option (€40–80):** A good consumer router with multiple SSIDs and basic VLAN support. The **TP-Link Archer AX55** (~€70) or **Tenda AX6** (~€60) let you create separate SSIDs with client isolation. Not true VLANs, but on a flat network it's about 80% of the benefit for 10% of the effort.

**Mid option (€120–180):** **TP-Link Omada** — the **ER605** router (~€150) plus an **Omada AC1200 access point** (~€80). Full 802.1Q VLAN support, proper guest isolation, a real QoS engine, and a management UI that doesn't make you want to cry. This is the sweet spot for most households and it's what I'd recommend.

**Enthusiast option (€250–400):** **UniFi** — the **Dream Machine** (~€350) or a **CloudKey Gen2** plus a **U6-Pro** access point. Best-in-class QoS, best-in-class UI, excellent VLAN support.

**Free option:** If you've got a spare router or an old PC, **OpenWrt** or **OPNsense** on it. Free software, full control, steep learning curve. Great if you're the type who enjoys configuring routers. Not great if you want it working in ten minutes.

### The one thing everyone forgets: the IoT network needs DNS

Most "IoT isolation" guides cut IoT off from the internet entirely. Then your smart bulbs can't resolve `ntp.pool.org` and drift out of sync, or your camera can't find the time and timestamps everything as 1970.

Give the IoT network access to **one** thing: your DNS resolver (Pi-hole or AdGuard Home). Everything else: blocked.

---

## 2. QoS: Making the Pipe Fair

Here's the maths that explains most evening lag:

| Activity | Bandwidth needed |
|---|---|
| 4K Netflix / YouTube | ~25 Mbps down |
| HD video call (1080p) | ~4 Mbps down, ~4 Mbps up |
| Game download (Steam/PS5) | 50–150 Mbps sustained |
| Gameplay | 1–2 Mbps, but **latency matters more than speed** |
| Video conference upload | 2–10 Mbps up |

**One game update saturates a 100 Mbps line for an hour.** Your wife on a video call gets 1.4 Mbps and a 400ms ping. Everyone blames the internet.

### What to prioritise

Rank your traffic from most to least important:

1. **Voice/video calls** — the most latency-sensitive thing in the house. Always top.
2. **Gaming traffic** — low bandwidth but needs low jitter. Priority it.
3. **General browsing and streaming** — normal.
4. **Background downloads** — game updates, OS updates, cloud backups. Nice to have, can wait.

### Doing it properly

**Automatic (easiest):** Most modern routers have a "Smart QoS" that detects application types automatically.
- **TP-Link Omada**: Adaptive QoS, priority by application category
- **UniFi**: Smart Queue Management (SQM) — this is the best out-of-the-box option, it does per-device fair queuing automatically and handles the "everyone's downloading at once" problem better than manual rules
- **Netgear**: Smart QoS, priority by device

**Manual (more control):** Write explicit rules. On the Omni, create bandwidth limits per VLAN:
- Trusted: no limit
- IoT: cap at 30% of total upload
- Kids: cap at 40% of total download during peak hours (7 PM – 11 PM)
- Guest: cap at 20%

**Surgical (if you're me):** The kids' console still stutters while the adults are on calls, because the console's *download* is saturating the queue even though the game traffic is tiny. Fix: on your router or on the console's network settings, exclude the console's download server from the priority queue, or just set the console to "pause downloads while playing" (it's a built-in setting on both PlayStation and Xbox). That one checkbox fixes more lag than any router configuration.

**Linux-based (the fun way):** If your router runs OpenWrt, use `sqm` with `cake`:
```
# /etc/config/sqm
config sqm
	option qdisc 'cake'
	option interface 'wan'
	option download 950000	# 95% of your line — leave headroom
	option upload 280000
	option linklayer 'ethernet'
```
`cake` does per-flow fair queuing, which is genuinely the best answer to "everyone's downloading at once." It's the single best QoS mechanism in existence and it's free.

---

## 3. DHCP Reservations: Stop the IPs Moving

Every device that connects gets an IP from a pool. When the lease expires or the router reboots, the device might get a different one. Then:

- Your port forwarding breaks
- Your Home Assistant integration can't find the device
- Your self-signed certificate is invalid for that IP
- The kid's console won't accept the local DNS server

**Fix it in the router, not on the devices.** Every router has a "DHCP reservation" or "static lease" table: MAC address → IP address. Do it once for each device and it never moves again.

**Which devices need it:**
- NAS (your whole homelab points at it)
- Home Assistant
- Pi-hole / AdGuard Home
- The printer (always, forever, no exceptions)
- The gaming console (so you can prioritise it)
- Anything you port-forward to

**Do NOT hardcode IPs on the device itself.** Set it to DHCP and pin it in the router. If you set a static IP on the device and later change your router, you get a silent network partition and a very bad afternoon.

**Also: keep your DHCP pool outside your static range.** If the router hands out `192.168.1.50–200` and you've reserved `192.168.1.10` for the NAS, fine. But if your pool includes `.10` and the NAS ever loses its reservation, the router hands `.10` to someone's phone and the conflict is maddening to debug.

---

## 4. The Gaming Rig Problem

### Wired, always, if you can

Wi-Fi latency fluctuates. Wired latency doesn't. For a gaming PC in the same room as the router, a €6 Cat5e cable running along the skirting board is a 5–15ms latency improvement over 5GHz Wi-Fi, with zero jitter.

**Don't overspend on cable.** Cat5e supports 2.5 Gbps up to 100m. Cat7 costs 3× as much and buys you nothing on a home network unless you're running 10 Gbps. Most ISP routers have 1 Gbps ports anyway.

**If you're running cable:** Use a **5-port gigabit switch** (~€25) rather than running individual cables to every room. One cable from the router to the living room, then the switch handles the rest. Label both ends of every cable with masking tape. Future you will be grateful.

**PoE is worth it for access points and cameras** — one cable for power and data, and you can reboot them from the router without walking there.

### The storage problem nobody warns you about

Modern games are enormous:

| Game type | Install size |
|---|---|
| Indie / 2D | 1–8 GB |
| AAA (2024–2026) | 80–150 GB |
| With day-one patches | 150–250 GB |

Two kids, four games each, plus one game on the console, plus your library: **1.5–2.5 TB** just for games. Before patches. Before sales.

**The pattern that works:**
- Active game → local SSD (fast load)
- Finished game → move to NAS (free up space)
- Never-playing-again game → delete from local, keep on NAS, reinstall when the mood strikes

Steam's "Uninstall & Delete Steam depot files" or just cut-and-paste the game folder to the NAS works. Most launchers handle a moved install folder fine — you just point the launcher at the new path.

**Buy a big SSD, not a fast one.** A 2TB SATA SSD (~€120) gives more practical value than a 1TB NVMe (~€110) in a gaming rig, because game loading on PCIe 3.0 vs 4.0 is imperceptible but *storage capacity* determines how many games you can keep installed.

### Console-specific: the download war

PlayStation and Xbox both default to downloading games automatically, and they'll happily eat your entire connection at 9 PM on a school night.

**Fix it in the console settings, not the router:**
- PlayStation: Settings → Network → Automatic Downloads → Off, then download games manually when nobody's using the network
- Xbox: Settings → General → Network & Internet → Manage Xbox Live → "Allow background downloads" → Off

This one setting change is worth more than every router QoS setting combined.

---

## 5. The Tinkering Budget

Here's the thing nobody tells you when you start a homelab: **you will break the family network.**

Not "might." Will. You'll change a DNS setting to test something and the whole house loses internet. You'll install a new service on the wrong interface and broadcast DHCP on the wrong VLAN. You'll reboot the router at the wrong moment.

That's fine. That's how you learn. But it stops being fine when it happens during a work call.

### The rules I follow

**Rule 1: Never experiment on the network the family depends on.**
Keep a **lab setup**: an old router and a spare laptop, or a second Raspberry Pi running Pi-hole or OpenWrt. Test there. If it works there, deploy it to production. This is literally the staging/production split, and it exists for the same reason.

**Rule 2: Snapshot before you change.**
Before touching the router config, export the settings file. Before editing the NAS share permissions, screenshot them. Before changing a firewall rule, write down what you're removing.

I have a rule for myself: **I can't make a change I can't describe in one sentence in writing first.** If I can't write it down, I'm not ready.

**Rule 3: Change one thing at a time.**
Two changes at once and it goes wrong means you now have two suspects and no idea which one. Classic. Same rule, same reason, in every environment.

**Rule 4: Have a rollback plan before you need it.**
Before the firmware flash: know exactly how to flash the old version back. Before the disk wipe: know where the backup is *and verify it restores*.

### The tinkering budget itself

Give yourself a **fixed time box**: one evening a month, or one Saturday morning a fortnight. When it's over, you stop, even if you're mid-project. A half-finished config change at midnight is how you wake up to a broken network.

**Maintain a "known good" config.** Once the network works exactly how you want it, export the router settings and store them somewhere you'll remember. When you inevitably break it at 11 PM on a Tuesday, you can restore instead of debug.

This is the single most valuable thing I own for my home network: a folder called `home-network/known-good/` with dated router exports, switch configs, and the Pi-hole config.

---

## 6. The Device Inventory

You cannot manage what you haven't written down. This takes 30 minutes once and then 10 minutes whenever you add something.

```
HOME NETWORK INVENTORY
Last updated: 2026-10-15

ROUTER:      TP-Link ER605, 192.168.1.1, fw 1.4.3
SWITCH:      TP-Link TL-SG105, 192.168.1.2, living room
AP:          Omada AC1200, 192.168.1.3, hallway ceiling
DNS:         Pi-hole (rpi-home), 192.168.1.10
NAS:         TrueNAS, 192.168.1.20, 8TB RAIDZ2
HASS:        Home Assistant, 192.168.1.30
PRINTER:     Brother Laser, 192.168.1.40
PS5:         192.168.1.50, wired, QoS priority 2
XBOX:        192.168.1.51, wired
GAMING PC:   192.168.1.60, wired
WORK LAPTOP: 192.168.1.70, wired
MY LAPTOP:   192.168.1.71, wifi

VLANs:
  10 Trusted   192.168.10.0/24
  20 IoT       192.168.20.0/24
  30 Kids      192.168.30.0/24
  40 Guest     192.168.40.0/24
  50 Work      192.168.50.0/24
```

Now, when something misbehaves, you don't spend an hour working out which IP the Xbox has. You look it up. And when the DHCP lease changes (it shouldn't — you set reservations), you know which devices should be on which VLAN.

**Print it.** Put a copy by the router. Physical paper has never failed to boot.

---

## 7. Preventing the 2 AM Nightmare: Bedtime on the Network

This is the single most appreciated thing I've done in my own house.

Most routers support **parental controls with time-based access**:

- PlayStation: Settings → Users and Accounts → Parental Controls → Set console time restrictions
- Xbox: Family Settings → Xbox Live privacy → "Xbox Live when signed in" schedule
- Xbox (network-wide): router → device schedule → block 21:00–07:00
- Steam: Family Sharing → Parental Controls
- Also: your kid's phone (iOS Screen Time, Android Family Link, or network-wide)

**Network-wide is the strongest version** because it doesn't depend on the device cooperating. A console that isn't connected can't be played, and there's no "I'll just use my phone" loophole.

**Be honest with your kid about it.** I explained it as "the house goes to sleep at 9" rather than "I'm blocking you." It's a household rule, not a punishment. Frame it that way and there's far less resentment.

**And add a "goodbye mode":** the network schedule can be paired with a physical one — the console lives in a specific spot, the router's in the hall, and when the schedule hits, the console's icon greys out with a message. The ritual matters more than the mechanism.

---

## 8. Hardware That Survives a Busy House

### Noise

The single most common complaint about someone's home lab: **it's loud**.

- A NAS with 3.5" spinning drives in the living room is a constant low rumble. Move it to a bedroom, closet, or under a desk.
- 3.5" NAS drives are quieter than spinning up/down constantly. Choose drives designed for NAS (WD Red, Seagate IronWolf).
- A single big fan is often quieter than three small ones spinning fast.
- The gaming rig under the TV will be heard. Put it on a **vibration-damping mat** (~€15) — this genuinely helps more than you'd expect.

### Power

- **Put the router, switch, and AP on a small UPS** (~€60 for a 600VA unit). A 2-second power blip during a brownout can corrupt a NAS write and reboot your router. A UPS bridges that gap and gives you time to shut down cleanly.
- The NAS gets its own UPS if you can. Silent shutdown matters more for storage than for the router.
- Check the wattage. A gaming PC (450W), NAS with 4 drives (60W), router+switch+AP (25W), plus house lighting and appliances — a modern 500W PSU in a gaming rig can be the difference between fine and tripping the breaker.

### Heat

- Every device in a cupboard is a device in a heat trap. A 25°C cupboard can hit 40°C+ with a NAS and a gaming PC in it.
- If you're running a rack in a closet, put a **cheap USB fan** (~€10) on the door, and check the temperature with a €5 sensor.
- Network equipment rated for 40°C ambient will throttle or die at 45°C. Many consumer routers are rated for exactly 40°C.

---

## The Order to Do It In

If you're starting from a flat network with one router and a mess of devices, here's the sequence that gives the most improvement per hour of effort:

**Week 1 — Free, 30 minutes**
- Turn on automatic firmware updates for the router
- Set up DHCP reservations for the 8 most important devices
- Turn off console background downloads
- Check your actual upload speed (not download — the number that matters for calls)

**Week 2 — ~€80, one evening**
- Set up Pi-hole on a Raspberry Pi (or use AdGuard Home if you don't have one)
- Point the router's DNS at it
- Give the kids' consoles a fixed IP

**Month 2 — ~€150–250, one weekend**
- Upgrade to a VLAN-capable router (Omada ER605 + AP, or a UniFi Dream Machine)
- Split into Trusted / IoT / Kids / Guest
- Enable per-VLAN bandwidth caps

**Month 3 — ongoing**
- Write the inventory
- Export a known-good config
- Set your tinkering budget in the calendar

You do not need to do all of this at once. Steps 1 and 2 alone will fix most of what actually annoys people, and they're free or cheap.

---

*What's the thing in your house network that irritates you most? Bandwidth hogs, the smart TV, a kid's console, or the person who keeps "just testing something" on the router at 10 PM? [Tell me](mailto:pragmatic@pragmaticsysadmin.help) — I'll probably have a specific answer.*
