---
title: "Linux Things That Are Easy to Miss (Until They Bite You)"
date: 2026-07-13T08:00:00.000Z
categories:
  - System administration
  - Linux
tags:
  - linux
  - bash
  - bashrc
  - sysadmin
  - cron
  - systemd
  - devops
  - common mistakes
  - troubleshooting
description: "A practical list of subtle Linux habits and gotchas that bite you the 10th, 50th, or 1000th time you do them. From bashrc pitfalls to cron environment traps, to 'I'll fix this later' chmod 777 sins."
keywords:
  - linux gotchas
  - bashrc issues
  - sudo apt update
  - cron environment
  - systemd tips
  - linux troubleshooting
  - sysadmin mistakes
  - linux daily habits
author: "Pragmatic Sysadmin"
ShowShareButtons: true
ShowReadingTime: true
aliases:
  - /posts/2026-07-13-linux-things-easy-to-miss/

---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Linux Things That Are Easy to Miss (Until They Bite You)",
  "description": "A practical list of subtle Linux habits and gotchas that bite you the 10th, 50th, or 1000th time you do them.",
  "author": {"@type": "Person", "name": "Pragmatic Sysadmin"},
  "publisher": {"@type": "Organization", "name": "Pragmatic Tech"},
  "datePublished": "2026-07-13",
  "dateModified": "2026-07-13",
  "mainEntityOfPage": {"@type": "WebPage", "id": "https://pragmaticsysadmin.help/sysadmin/2026-07-13-linux-things-easy-to-miss/"},
  "image": {"@type": "ImageObject", "url": "https://pragmaticsysadmin.help/og/2026-07-13-linux-things-easy-to-miss.png", "width": 1200, "height": 630}
}
</script>

# Linux Things That Are Easy to Miss (Until They Bite You)

The other day I spent 20 minutes debugging a cron job that worked perfectly when I ran it from the shell. The fix? `PATH` was different in cron. That's not a one-time thing — I trip over the same class of subtle Linux papercuts every few months. So I wrote them all down.

This is the post I wish someone had handed me on day one. None of these are catastrophic. They're the everyday habits that quietly cost you hours, then you forget about them, then they bite again six months later.

If you've been a Linux sysadmin for more than a year, you'll recognize most of these. If you're newer, **bookmark this** — it'll save you real time.

---

## 1. The `~/.bashrc` trap: commands that run every shell

I used to have this in my `~/.bashrc`:

```bash
# Update package lists when opening a new shell
sudo apt update -y
```

Which means: **every time I opened a new terminal, it would prompt me for my password, run apt, and add ~2 seconds to startup**. On a server I SSH into 20 times a day, that's 40 seconds of pure waiting. And worse — it trained me to type my password without thinking, which is bad security hygiene.

Worse variants I've seen:
- `docker system prune -f` in bashrc (deletes data on shell open)
- `make build` in bashrc (compiles a project on every shell)
- `kubectl get pods` in bashrc (network call on every shell)

**The rule:** bashrc is for **interactive setup only** — aliases, prompts, env vars, `cd` to your work dir. Not for running things with side effects.

**Better pattern:** if you want a reminder, use an alias:

```bash
# Add to ~/.bashrc
alias apt-up='sudo apt update && sudo apt full-upgrade -y'
# Now you run it when you want, not when bash decides
```

If you have an existing bashrc with side effects, audit it:

```bash
grep -E '^[^#]*(sudo|rm|make|docker|kubectl|curl|wget|nc)' ~/.bashrc
```

Anything that matches in a non-`alias` line is suspect.

---

## 2. `sudo` without `-E` drops your environment

You set `HTTP_PROXY` in your shell. You run `sudo apt update`. It fails because the proxy isn't set. Surprise: `sudo` resets most environment variables by default.

Two fixes:
```bash
# Quick fix for one command
sudo -E apt update

# Permanent: add to /etc/sudoers.d/proxy (use visudo!)
Defaults env_keep += "HTTP_PROXY HTTPS_PROXY NO_PROXY"
```

The `Defaults env_keep +=` line tells sudo to **preserve** those specific variables. Add `PATH`, `JAVA_HOME`, `LANG`, `EDITOR`, and anything else your tooling needs.

Same problem hits `cron`, `systemd`, `tmux`, and `screen` — each has its own environment. **Anything that isn't your interactive shell is a different world.**

---

## 3. Your cron environment is NOT your shell environment

This is the one that cost me 20 minutes last week. I had a backup script that ran fine from the shell but failed in cron. The reason: my shell had `PATH=/usr/local/bin:/usr/bin:/bin:/snap/bin`, but cron runs with `PATH=/usr/bin:/bin`.

Two fixes:

```bash
# Option 1: Set PATH at the top of your crontab
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
0 3 * * * /opt/backup/run.sh

# Option 2: Use absolute paths in your crontab
0 3 * * * /opt/backup/run.sh >> /var/log/backup.log 2>&1
```

I use option 2. Always. No surprises.

**Bonus gotcha:** cron also doesn't load your `~/.bashrc`, so any aliases or functions you've defined are gone. If your script is meant to be run by cron, write it as a real shell script with absolute paths and the `#!/bin/bash` shebang. Don't depend on shell config.

---

## 4. Backgrounding processes that die when you disconnect

You SSH in, start a long-running command, hit `Ctrl+Z`, type `bg`, and... your process dies when you disconnect.

Three options, increasing reliability:

```bash
# 1. nohup (simplest, redirect output)
nohup ./long-process.sh > output.log 2>&1 &

# 2. disown (after &)
./long-process.sh &
disown
# Now it survives shell exit

# 3. tmux/screen (best, lets you reattach)
tmux new -s mywork
./long-process.sh
# Ctrl+B, then D to detach
# tmux attach -t mywork  to come back
```

For anything that needs to actually run unattended, use **systemd**. That'll handle restarts, logging, dependencies, and survive reboots.

---

## 5. Disk full but `df` shows space

The most common cause: **out of inodes**.

```bash
df -h        # shows disk space — usually fine
df -i        # shows inodes — can be 100% full
```

When inodes are exhausted, you can't create any new files, even with free disk space. Common cause: a directory with millions of tiny files (cached PHP sessions, mail queues, log file rotation gone wrong).

Fix:
```bash
# Find directories with the most files
sudo find / -xdev -type d -exec sh -c 'echo "$(find "$0" -maxdepth 1 | wc -l) $0"' {} \; \
  | sort -rn | head -20

# Look for the offender, then clean up
sudo rm -rf /var/lib/php/sessions/*
# (or whatever the bad directory is)
```

**Prevention:** logrotate properly. Set `postrotate` scripts that actually delete old logs, not just rotate them.

---

## 6. `chmod 777` "I'll fix it later"

The classic. Something doesn't work, you don't know why, you `chmod 777` to make it go away. Now:

- Any user on the system can read/write that file
- Security scanners flag it (every audit tool, every compliance check)
- It's almost certainly **not the right fix** — usually it's a permission for a specific user (www-data, postgres, etc.) or a specific group

Quick diagnostics before reaching for 777:
```bash
# What's the file's actual owner/group?
ls -la /path/to/file

# What user is the process running as?
ps aux | grep -i 'process-name'

# What does the error actually say?
# (Read the error message, don't just chmod blindly)
```

The right fix is almost always:
```bash
# Change owner to the service user
sudo chown www-data:www-data /var/www/html

# Or add your user to the right group
sudo usermod -aG docker $USER
```

Don't `chmod 777`. Add a 30-second timer on your phone if you have to.

---

## 7. `iptables` rules lost on reboot

You spent 20 minutes carefully crafting firewall rules. Reboot the server. They're gone. Why: iptables rules live in memory, not on disk.

Fix based on distro:

```bash
# Debian/Ubuntu with iptables-persistent
sudo apt install iptables-persistent
sudo netfilter-persistent save
# Now rules persist across reboots

# RHEL/CentOS/Rocky
sudo service iptables save
# Or:
sudo iptables-save > /etc/iptables/rules.v4

# Modern alternative: nftables with systemd
sudo nft list ruleset > /etc/nftables.conf
```

Same problem with `/etc/resolv.conf` on systemd-resolved systems, network config on netplan, etc. **Anything you do at runtime is a draft until you save it.**

---

## 8. SSH config: `PermitRootLogin yes` and other footguns

Default SSH config is mostly safe, but easy to misconfigure:

```bash
# /etc/ssh/sshd_config
PermitRootLogin no              # Yes, even if you "trust" yourself
PasswordAuthentication no       # Use keys only
PermitEmptyPasswords no         # Defense in depth
X11Forwarding no                # If you don't need it
AllowUsers jon                  # Whitelist, not blacklist
```

After editing:
```bash
# ALWAYS test before disconnecting
sudo sshd -t                    # validates config
# Then in another terminal:
ssh user@server                 # make sure it works
# If it doesn't, you still have your original session open
```

The number of "I locked myself out of my own server" stories is endless. Don't add to it.

---

## 9. `kill -9` as a first resort

`kill -9` (SIGKILL) sends "die, no cleanup". The process can't:
- Flush buffers to disk
- Close network connections gracefully
- Remove lock files
- Notify child processes
- Update database state

For most cases, `kill <pid>` (SIGTERM, the default) is correct. The process gets a chance to clean up. If it doesn't respond in 5-10 seconds, **then** escalate to `kill -9`.

For services:
```bash
# Right: graceful then force
sudo systemctl stop myservice
# If that hangs:
sudo systemctl kill -s SIGKILL myservice

# Or via PID
kill $(pidof myservice)
sleep 5
kill -9 $(pidof myservice) 2>/dev/null
```

Save `kill -9` for actual emergencies (zombie process, hung kernel call).

---

## 10. `find` + `rm` with whitespace or newlines in filenames

```bash
# This WILL break on filenames with spaces
find . -name "*.log" -exec rm {} \;

# Safer (handles whitespace)
find . -name "*.log" -print0 | xargs -0 rm
```

Or even better, use `find -delete`:
```bash
find . -name "*.log" -type f -delete
# -delete is atomic, no exec shenanigans
```

`find` has so many subtle footguns (symlink loops, permission issues, argument lists too long with `-exec`). Read the man page if you're doing anything non-trivial. Or use [`fd`](https://github.com/sharkdp/fd) — `fd '*.log' --type f --exec rm` — much saner.

---

## 11. Aliases that bite you in scripts

```bash
# In your ~/.bashrc
alias rm='rm -i'           # "be safe" 
alias cp='cp -i'
alias mv='mv -i'
```

Great for interactive use. **Disaster in scripts.** When your cron job runs `rm -rf /tmp/cache/*` and your alias makes it `rm -i -rf /tmp/cache/*`, the `-i` flag means **the script prompts for confirmation, gets no input, and fails silently**.

For scripts, always use full paths and no aliases:
```bash
#!/bin/bash
/bin/rm -rf /tmp/cache/*     # Use full path to bypass any alias
```

Or explicitly disable aliases for the script:
```bash
#!/bin/bash
unalias -a                  # Remove all aliases for this script
```

---

## 12. Forgetting the inodes on package installs

Ran `apt install` on a system that was 100% inodes. It looked like it succeeded but the package wasn't actually installed (no error, just silent failure). The post-install hooks all failed silently.

Quick check after any install:
```bash
# Verify the binary actually exists
which <command>

# Verify the package is actually installed
dpkg -l | grep <package>     # Debian/Ubuntu
rpm -qa | grep <package>     # RHEL family
```

Don't trust "exit code 0" alone when you've been bitten by inodes before.

---

## 13. `history` expansion breaking scripts

`!` characters in shell scripts cause "event not found" errors. This is the bane of anyone who's tried to use `!` in a docker-compose or curl command in bash.

```bash
# This breaks:
echo "I can't believe it!"

# Workarounds:
set +H                        # Disable history expansion (for the session)
# Or use single quotes
echo 'I can'\''t believe it!'  # Or escape
```

If a script mysteriously fails with "event not found", suspect this first.

---

## 14. `systemd` services that "work" but aren't actually running

```bash
# Looks fine, right?
sudo systemctl status myservice
# Active: active (exited) since ...

# That's not the same as running!
# 'active (exited)' means the unit ran once and finished.
# You probably want 'active (running)'.
```

This is a huge trap for OneShot and Type=oneshot services. They "succeed" without doing anything ongoing.

Use `Type=notify` or `Type=simple` for actual long-running services. Add a watchdog timer if you want to detect silent crashes.

---

## 15. Not reading the actual error message

This one's not Linux-specific but I'm including it because I do it too. The number of "broken" systems I've fixed just by reading the error message carefully is embarrassing.

When something breaks:
1. Read the error, **in full**, including any stack traces
2. Google the **exact** error string (or unique part of it) in quotes
3. Check `man` pages of the relevant tool (`man some-tool` or `:help` in some)
4. Then ask for help, including the full error

80% of the time the answer is in step 2.

---

## Defend against all of these

The pattern across all of these: **subtle configuration that doesn't fail loudly until it does.** A few habits that catch most of them:

1. **Idempotent setup scripts.** Treat your server config as code. Use Ansible, shell scripts, whatever. Don't manually `vim` files on a server.
2. **A "post-install" checklist** for new servers. After every setup, run through the gotchas above. Took 10 minutes, saves 10 hours of debugging later.
3. **Test in non-shell environments.** Run your script via `bash <script>` and via `cron` and via `systemd-run --scope` to make sure all three work.
4. **Log everything.** When a thing fails silently, it's because there's no log. Add `set -x` to debug, add `2>&1 | tee` to capture errors.
5. **Read the error messages.** Yes, really. All of them.

Most of these aren't "Linux is broken". They're "Linux is doing exactly what you told it to, and you didn't tell it what you thought you did." Knowing that, you can avoid 90% of the time-sinks.

What's the worst one of these you've been bitten by? [Drop me a line](mailto:pragmatic@pragmaticsysadmin.help) — I read every response.

---

*Related reads:*
- *[The 5-Minute Server Health Check](/sysadmin/2025-12-09-the-5-minute-server-health-check-that-could-save-your-career/) — catches most of the silent failures above before they bite*
- *[Why Your Monitoring is Broken](/sysadmin/2025-11-06-why-your-monitoring-is-broken-and-how-to-fix-it-before-your-boss-notices/)*
- *[Setting Up a Home Lab](/sysadmin/2025-10-29-setting-up-a-home-lab-a-beginner-s-guide/) — practice all of these safely before they hit production*
- *[Reading Logs Like a Detective](/sysadmin/2025-12-17-the-art-of-reading-logs-like-a-detective-finding-needles-in-haystacks/)*