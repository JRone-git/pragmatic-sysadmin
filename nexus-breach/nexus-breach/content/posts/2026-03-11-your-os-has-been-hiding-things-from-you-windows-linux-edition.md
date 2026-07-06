---
title: "Your OS Has Been Hiding Things From You (Windows & Linux Edition)"
date: 2026-03-11T06:06:00.000Z
categories:
  - General
---

-----

## title: “Your OS Has Been Hiding Things From You (Windows & Linux Edition)”
date: 2026-03-10
draft: false
author: “Pragmatic Sysadmin”
tags: [“windows”, “linux”, “productivity”, “tips”, “automation”]
categories: [“tutorials”]
description: “Both Windows and Linux are packed with powerful hidden features most users never touch. Here’s a side-by-side breakdown of the best ones.”
slug: “windows-linux-hidden-tricks”

# Your OS Has Been Hiding Things From You (Windows & Linux Edition)

Windows users think Linux is complicated. Linux users think Windows is a toy.

Both are wrong. Both operating systems are packed with powerful features that most people — on either side — have never touched.

This isn’t a “which is better” post. That argument is boring. This is about what your machine can *actually* do, regardless of which camp you’re in.

Let’s go feature by feature.

-----

## 1. Clipboard History

You copy something. Then copy something else. The first thing is gone forever.

Both systems solved this. Most users don’t know it.

**Windows:**

```
Windows + V
```

Enable it the first time you press it. Now you have a full scrollable history of everything you’ve copied — text, images, all of it.

**Linux (X11/Wayland):**
Install `copyq` or `gpaste` — unlike Windows, this isn’t built in, but it’s one command away:

```bash
sudo apt install copyq && copyq &
```

CopyQ runs in your system tray and stores unlimited clipboard history. It also supports scripting your clipboard, which Windows can’t touch.

**Pro tip (Linux):** CopyQ has a built-in scripting engine. You can write rules like “whenever I copy a URL, automatically strip tracking parameters.” Try doing that on Windows.

-----

## 2. Automation Without Writing Code

Both systems let you automate repetitive tasks. The approach couldn’t be more different.

**Windows — Power Automate Desktop:**

```
Start Menu → Power Automate
```

Visual drag-and-drop automation. Record your mouse clicks and keystrokes, turn them into a reusable flow. No coding required. Rename 500 files, auto-fill forms, move folders on a schedule — all point and click.

**Linux — cron + bash:**

```bash
crontab -e
```

Add a line like this to run a script every day at 8 AM:

```bash
0 8 * * * /home/user/scripts/morning_backup.sh
```

Steeper learning curve, zero limits. Once you know it, you’ll never go back.

**Honest take:** Power Automate wins for accessibility. Cron wins for power. If you’re on Linux and haven’t learned cron yet, that’s the most valuable 30 minutes you can spend this week.

-----

## 3. Virtual Desktops

Multiple desktops. Work on one, personal on another, music on a third. Both systems do this natively and almost nobody uses it.

**Windows:**

```
Windows + Tab → New Desktop
```

Or swipe with three fingers on a touchpad. Switch between desktops with `Windows + Ctrl + Left/Right`.

**Linux (most distros):**
Usually visible right in your taskbar as numbered workspaces. Keyboard shortcut varies by desktop environment, but typically:

```
Super + number key    # jump to workspace
Super + Shift + number  # move window to workspace
```

**Pro tip:** On both systems, assign specific apps to always open on specific desktops. On Linux, most window managers let you set this per-application in settings. On Windows, right-click a window in the Task View.

This one feature alone can completely change how you work.

-----

## 4. Screenshot Superpowers

Both systems go way beyond “press Print Screen.”

**Windows — Snipping Tool:**

```
Windows + Shift + S
```

Select a region, window, or full screen. But here’s what most people miss — it does **video recording** now too. And it has OCR: screenshot any image with text in it, and Windows will let you copy that text directly.

**Linux — Flameshot:**

```bash
sudo apt install flameshot
flameshot gui
```

Flameshot is arguably the best screenshot tool on any platform. Annotate, blur, highlight, add arrows — all before you even save the image. Blur out sensitive info in one click.

**Pro tip (Linux):** Bind Flameshot to your Print Screen key:

```bash
# In your keyboard shortcuts settings:
flameshot gui
```

Now Print Screen opens a full annotation suite instead of just saving a file.

-----

## 5. Find Anything Instantly

Searching your own computer shouldn’t be hard. Both systems have tools that make it instant.

**Windows — Everything (+ built-in search):**

The built-in `Windows + S` search is decent but slow for files. Install **Everything** by voidtools (free) — it indexes your entire drive in seconds and finds any file instantly as you type. It’s genuinely magic.

Built-in alternative that most people overlook:

```
Windows + R → type: shell:recent
```

Instantly opens your recently accessed files. Faster than any search for stuff you touched today.

**Linux — locate / fzf:**

```bash
# Find any file instantly
locate filename

# Update the database first if needed
sudo updatedb
```

For power users, `fzf` is a game changer:

```bash
sudo apt install fzf
# Then press Ctrl+R in terminal for fuzzy search through command history
```

`fzf` gives you fuzzy search on *anything* — files, command history, processes. Once you use it, you’ll want it everywhere.

-----

## 6. See What’s Eating Your Disk

Running out of space and don’t know why?

**Windows — WinDirStat / built-in Storage Sense:**

```
Settings → System → Storage
```

Windows shows you a breakdown by category. For a visual map of exactly which files and folders are taking space, download **WinDirStat** — it’s free and shows your entire drive as a colour-coded treemap.

**Linux — ncdu:**

```bash
sudo apt install ncdu
ncdu /
```

Navigate your entire filesystem like a file manager, sorted by size. Find the 20GB folder you forgot about in under a minute. No GUI needed.

**Pro tip:** On Linux, the hidden culprit is almost always Docker images or old kernel versions:

```bash
docker system prune    # clean up unused Docker data
sudo apt autoremove    # remove old kernels
```

-----

## 7. Scheduled Tasks You Actually Control

Both systems can run things automatically. Both hide this from you by default.

**Windows — Task Scheduler:**

```
Start Menu → Task Scheduler
```

Most people use this to run scripts on a schedule. The thing they miss: you can trigger on *events*, not just time. Run something every time a USB is plugged in. Run something every time a specific user logs in. Run something when the system becomes idle.

**Linux — systemd timers:**
Cron is great. Systemd timers are more powerful and have better logging:

```bash
# Check all running timers
systemctl list-timers

# View logs for a specific timer
journalctl -u your-timer-name
```

Unlike cron, systemd timers integrate with the journal, so you can actually see whether your scheduled task succeeded or failed and why.

-----

## The Side-by-Side

|Feature          |Windows                |Linux                 |
|-----------------|-----------------------|----------------------|
|Clipboard History|Built-in (Win + V)     |CopyQ / GPaste        |
|Automation       |Power Automate (visual)|cron + bash (powerful)|
|Virtual Desktops |Win + Tab              |Super + number        |
|Screenshots      |Snipping Tool + OCR    |Flameshot             |
|File Search      |Everything (free app)  |locate / fzf          |
|Disk Usage       |WinDirStat             |ncdu                  |
|Scheduled Tasks  |Task Scheduler         |systemd timers        |

-----

## What This Actually Means

The OS wars are mostly noise. Both Windows and Linux are genuinely capable, and both hide their best features from casual users.

The difference isn’t which OS is better. It’s whether you’ve taken the time to learn what your tools can actually do.

Windows gives you more handholding to get started. Linux gives you more power once you do. Neither has a monopoly on good ideas.

Pick up one trick from each side this week. Your future self will thank you.

-----

*Which one surprised you most? Anything I missed? Drop it in the chat — I’m always adding to the list.*