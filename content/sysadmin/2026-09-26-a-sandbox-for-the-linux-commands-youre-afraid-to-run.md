---
title: "A Sandbox for the Linux Commands You're Afraid to Run"
date: 2026-09-26
draft: false
description: "A browser sandbox where you can run rm -rf, dd, mkfs and iptables -F against a fake filesystem, watch the damage, and build the reflex without losing data."
tags: ["linux", "sysadmin", "troubleshooting", "tools", "security"]
categories: ["System administration"]
author: "Pragmatic Sysadmin"
reviewed: true
aiAssisted: true
blogforge:
  provider: "ai-assistant"
  model: "cli-assistant"
  generated_at: "2026-09-26T18:35:00Z"
  attempts: 1
  style_score: 100
  topic: "command-simulator"
---

Almost nobody learns `rm -rf` the easy way. You read the man page, you use it carefully for a year, and then one day you watch your finger hit Enter a fraction of a second before your brain finishes checking the path.

The commands that destroy data don't punish typos. They punish the half second before the typo, when you were certain the path was right.

That half second of doubt isn't something documentation can give you. So I built a place where you can get it wrong on purpose, with nothing at stake but a score.

<!--more-->

## A fake shell that keeps score

The whole thing is one HTML file. No build step, no npm, no CDN — 2,340 lines, about 84 KB, and it runs from a local file if you want it to. You can [try it here](/tools/command-simulator.html).

The prompt reads `sysadmin@danger-zone:~$`, and the `~` isn't decoration. Under the surface there's a small state object holding the entire world:

```js
const state = {
    currentDir: '/home/sysadmin',
    dangerLevel: 'LOW',
    commandsUsed: 0,
    safetyScore: 100,
    history: [],
    currentFile: null
};
```

Seventeen commands are wired up. `ls`, `cd`, `cat`, `find`, `df` and `ps` handle the boring work, so you can navigate a fake filesystem that behaves the way you expect. The other five are the reason the tool exists.

## Every dangerous command costs you twenty points

There is no confirmation prompt anywhere in it. That's on purpose. A real shell doesn't stop to ask, so a simulator that stops to ask teaches you the wrong reflex.

You pay in score instead:

```js
if (result.dangerous) {
    triggerDangerEffects();
    state.safetyScore = Math.max(0, state.safetyScore - 20);
    updateStats();
}
```

Twenty points per mistake, starting from a clean 100. The danger meter recalculates on every keystroke: 80 and above is LOW, 60 is MEDIUM, 40 is HIGH, and anything under that is CRITICAL.

Five mistakes puts you at zero. That number isn't a punishment. It's a count of how many times you would have needed a restore.

## The matcher reads tokens, not a real shell

Each dangerous handler inspects the argument array for the exact tokens that make the command lethal:

```js
function rmCommand(args) {
    if (args.includes('-rf') && (args.includes('/') || args.includes('/home') || args.includes('/etc'))) {
        log('Files would be deleted in a real system.', 'error');
        log('In simulation: No actual files were harmed.', 'success');
        return { dangerous: true };
    }
    log('File deletion simulated safely.', 'info');
    return { dangerous: false };
}
```

`dd if=/dev/zero of=/dev/sda` triggers an explosion animation. `chmod 777 /etc/passwd` and `iptables -F` raise their own security warnings. `mkfs /dev/sda1` formats nothing and tells you so.

It's a token check, not a parser. That distinction turns out to matter more than it sounds.

## `rm -rf /*` walks straight through

Here's the hole, and I'd rather you hear it from me than find it yourself.

The check asks whether `args` contains the literal string `/`. The command that has actually ended careers is `rm -rf /*`, and after splitting on spaces its arguments are `['-rf', '/*']`.

`'/*'` is not `'/'`. No match, no warning, no points deducted. The tool congratulates you: *File deletion simulated safely.*

Same story with `rm -rf ~`, `rm -rf $HOME` and `rm -rf .`. I matched the memorable version of the footgun and missed the common one. If you want to fix that, the honest version is to test each token with a prefix check, not an equality check:

```js
const isRootish = args.some(a => !a.startsWith('-') && /^[/~.]/.test(a));
```

That's four lines and it catches the cases I shipped without. I'd rather show you the gap than let the tool quietly lie to you about your own reflexes.

## Two handlers I wrote and could never reach

The dispatcher splits the line on spaces, then switches on the first token:

```js
const parts = command.split(' ');
const cmd = parts[0];
switch (cmd) {
    case 'cat': catCommand(args[0]); break;
    case 'rm':  result = rmCommand(args); break;
```

Two cases, though, were written as whole commands with spaces still in them:

```js
case 'cat /dev/random':                 result = randomCommand(); break;
case 'echo 1 > /proc/sys/kernel/panic': result = panicCommand(); break;
```

`cmd` is `parts[0]`. It can never contain a space, so neither case can ever fire. `cat /dev/random` falls through to the ordinary `cat` branch and gets quietly ignored.

I found that while going back through the file to write this post. It's the honest argument for writing build logs: the bug had been sitting there since the day I wrote it, and explaining the code out loud is what finally made me look.

## What actually protects your data

A sandbox builds the reflex. It does not protect anything. Before you run anything recursive, work through this list:

- **Dry-run it.** `rsync -av --dry-run` and `find . -name '*.log' -print` list what would be touched. Read the list properly instead of skimming it.
- **Print the variable.** `echo "$TARGET"` immediately before you delete `"$TARGET"`. Most `rm -rf` disasters are a variable that expanded to nothing, or to the wrong path.
- **Refuse a blank expansion.** `set -u` turns an unset variable into an error instead of a silent empty string, which is the difference between a complaint and a wiped directory.
- **Check that the mount is mounted.** A `rm -rf` on an unmounted `/mnt/backup` cheerfully deletes the real directory sitting underneath it.
- **Prove the backup, don't assume it.** Restore one file from last night before you ever need to restore all of them.

The [Friday backup audit](/sysadmin/2025-12-12-the-friday-backup-audit-because-hope-is-not-a-strategy/) is a 20-minute version of that last line, and it beats rebuilding a server on a Saturday. When something does go sideways, [reading the logs properly](/sysadmin/2025-12-17-the-art-of-reading-logs-like-a-detective-finding-needles-in-haystacks/) is where the fix comes from — not from panic.

The transferable skill is the pause. Practising that pause in a simulator that scores you is cheap. Practising it on your only copy is how the stories start.

---

*What's the command you'd never run without `--dry-run`? Tell me which one makes you double-check the path.*

*Related reads:*
- *[The Friday Backup Audit: Because Hope Is Not a Strategy](/sysadmin/2025-12-12-the-friday-backup-audit-because-hope-is-not-a-strategy/)*
- *[The Art of Reading Logs Like a Detective: Finding Needles in Haystacks](/sysadmin/2025-12-17-the-art-of-reading-logs-like-a-detective-finding-needles-in-haystacks/)*
- *[The 5-Minute Server Health Check That Could Save Your Career](/sysadmin/2025-12-09-the-5-minute-server-health-check-that-could-save-your-career/)*
