---
title: "What IT Pros Actually Do On Their Own Machines (vs What They Tell You)"
date: 2026-03-18T05:30:00.000Z
categories:
  - General
description: "There’s the advice IT gives everyone else. Then there’s what they actually do on their own machines. Here’s the honest version."
---

-----

## title: “What IT Pros Actually Do On Their Own Machines (vs What They Tell You)”
date: 2026-03-17
draft: false
author: “Pragmatic Sysadmin”
tags: [“productivity”, “security”, “tips”, “sysadmin”, “real-talk”]
categories: [“insights”]
description: “There’s the advice IT gives everyone else. Then there’s what they actually do on their own machines. Here’s the honest version.”
slug: “what-it-pros-do-on-their-own-machines”

# What IT Pros Actually Do On Their Own Machines (vs What They Tell You)

There’s the advice IT hands out. The official line. The stuff in the company handbook.

Then there’s what actually happens on the machines of the people who wrote that handbook.

I’m not here to throw anyone under the bus. But after years in this industry, there are some pretty consistent gaps between what gets preached and what gets practised. And honestly? Closing that gap will make your computing life significantly better.

Here’s the honest version.

-----

## “Use a Strong, Unique Password for Everything”

**What they tell you:** Use a different complex password for every account. Never reuse passwords.

**What IT pros actually do:** Exactly this — but they don’t memorise any of them. They use a **password manager** and have one very strong master password. That’s it. One password to remember, everything else is a randomly generated 20-character string they’ve never read.

The dirty secret is that most IT people have genuinely no idea what their own passwords are. The password manager knows. They don’t.

**What you should do:**

Pick one. Bitwarden is free, open source, and excellent. 1Password is worth paying for if you want something polished. Install it today, spend a weekend migrating your accounts, and never think about passwords again.

The people giving you password advice aren’t memorising 200 unique passwords. Neither should you.

-----

## “Don’t Install Software That Isn’t Approved”

**What they tell you:** Only install software from official sources. Stick to what’s approved.

**What IT pros actually do:** Run a package manager that installs and updates everything in one command.

On their personal machines, no IT pro is manually downloading installers, clicking through wizards, and hunting for update buttons. That’s for everyone else.

**Windows:**

```powershell
winget install Microsoft.VisualStudioCode
winget upgrade --all
```

`winget` is built into Windows 11. One command updates every app on your system. No hunting for update buttons, no installer wizards, no accidentally clicking “install toolbar.”

**Linux:**

```bash
sudo apt update && sudo apt upgrade -y
```

You already know this one. But if you’re managing a list of apps across machines, look into `ansible` or even just a simple shell script that reinstalls your whole setup from scratch.

**macOS:**

```bash
brew upgrade
```

Homebrew does the same thing. One command, everything updated.

The people telling you to be careful about software are themselves installing things faster and more safely than you are — because they use tools that handle it properly.

-----

## “Always Keep Backups”

**What they tell you:** Back up your data regularly.

**What IT pros actually do:** They automate it completely and then forget about it. They also follow the **3-2-1 rule** — three copies of data, on two different types of media, with one offsite.

More importantly: they test their backups. A backup you’ve never restored from is a backup you don’t actually have.

**The setup most IT pros use personally:**

- **Local backup** to an external drive (automated, runs nightly)
- **Cloud backup** to something like Backblaze ($9/month, unlimited data)
- **Occasional test restore** — actually pulling a file back from backup to confirm it works

**Windows — built in and free:**

```
Settings → Update & Security → Backup → Add a drive
```

File History backs up your files automatically once it’s set up. Takes 5 minutes to configure.

**Linux:**

```bash
rsync -av --delete /home/user/ /mnt/backup/
```

Stick that in a cron job and you’re done.

The people who lose data are the ones who meant to set up backups. IT pros lose less data because they stopped relying on intention and started relying on automation.

-----

## “Restart Your Computer Regularly”

**What they tell you:** Restart regularly to keep things running smoothly.

**What IT pros actually do:** On servers, they aim for maximum uptime and only restart when forced to. On their personal machines, they restart strategically — after updates, after something weird happens, not on a rigid schedule.

But here’s what they actually do that nobody mentions: they **monitor what’s running.**

```
Ctrl + Shift + Esc
```

IT pros check Task Manager the way mechanics listen to an engine. Before a restart, they want to know *why* something is slow. A restart fixes symptoms. Finding the process causing the problem fixes the cause.

**The habit worth stealing:** When your machine feels slow, check what’s at the top of the CPU and memory list before you do anything else. You’ll learn more about your computer in a week of doing this than in years of blind restarting.

-----

## “Be Careful What You Click”

**What they tell you:** Don’t click suspicious links. Be careful with email attachments.

**What IT pros actually do:** They’ve built an environment where a bad click does less damage.

- They run a **standard user account** for daily use, not an admin account. If something malicious runs, it runs with limited permissions.
- They use a **DNS-level ad and tracking blocker** like Pi-hole or NextDNS. Most malicious links never even resolve.
- They keep software updated obsessively, because most attacks exploit known vulnerabilities in outdated software.

The advice “be careful what you click” puts all the responsibility on human judgement, which is fallible. IT pros build systems where human error has less consequence.

**The one thing you can do today:**

Create a second user account on your computer without admin rights. Use that for daily browsing and work. Keep the admin account for installs and settings changes only. This one change dramatically limits what malware can do if it does get in.

-----

## “Contact IT Support If Something Goes Wrong”

**What they tell you:** Don’t try to fix it yourself. Log a ticket.

**What IT pros actually do on their own machines:** Google the exact error message. In quotes.

```
"Windows cannot access the specified device path or file"
```

The quoted search finds exact matches. Stack Overflow, Microsoft docs, Reddit threads from people with the exact same problem. Nine times out of ten the answer is on the first page.

After that: Event Viewer on Windows, `journalctl` on Linux. The actual error logs, not the user-friendly message that tells you nothing.

**Windows:**

```
Start Menu → Event Viewer → Windows Logs → Application or System
```

Filter by Error. Find the timestamp when things went wrong. Read what it actually says.

**Linux:**

```bash
journalctl -p err -b
```

All errors from the current boot. Specific, searchable, useful.

The gap between IT pros and everyone else isn’t knowledge of every solution. It’s knowing where to look for answers. Those two habits — quoted Google searches and reading actual logs — close that gap faster than anything else.

-----

## “Antivirus Will Keep You Safe”

**What they tell you:** Install antivirus and you’re protected.

**What IT pros actually do:** Run the built-in defender (which is genuinely good now), keep everything updated, and treat antivirus as one layer of a multi-layered approach — not a magic shield.

Windows Defender has been excellent for years. Most IT pros on personal Windows machines run nothing else. What they do instead:

- Enable the firewall (it should be on by default — check it)
- Use a browser with good privacy defaults (Firefox with uBlock Origin)
- Don’t run as admin (see above)
- Keep software updated

Paid antivirus products often slow your machine down more than they protect it. The money is better spent on a password manager.

-----

## The Pattern

Read back through all of this and you’ll notice something.

IT pros don’t have secret knowledge. They have **better habits and better tools.** They automate the things that humans forget. They build systems that limit the damage of mistakes. They look at actual data instead of guessing.

None of this is complicated. None of it requires a computer science degree.

It just requires doing the thing, instead of meaning to do the thing.

Pick one item from this list. Do it today. Come back for the next one next week.

-----

*Which of these surprised you most? Or — IT people — what did I leave off the list? Drop it in the comments.*