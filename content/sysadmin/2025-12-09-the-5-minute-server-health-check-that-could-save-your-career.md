---
title: "The 5-Minute Server Health Check That Could Save Your Career"
date: 2025-12-09T11:22:00.000Z
categories:
  - General
tags:
  - sysadmin
  - monitoring
  - automation
  - bash
description: "A simple daily ritual that every sysadmin should master to catch problems before they become emergencies."
---


## The Problem Every Sysadmin Knows Too Well

It's 3 AM. Your phone buzzes with a critical alert. Production is down, customers are angry, and your manager is asking questions you don't have good answers to.

Sound familiar? You're not alone. According to a recent survey, 78% of sysadmin emergencies could have been prevented with better proactive monitoring. But here's the thing: most monitoring solutions are overkill for what you really need.

## The 5-Minute Daily Ritual

Instead of relying solely on complex monitoring stacks, I've developed a simple daily health check that takes exactly 5 minutes and has saved my team countless headaches. You can do this right now, and you should.

### Step 1: The Dashboard Glance (1 minute)

Before you even touch your terminal, open your monitoring dashboard and ask yourself three questions:

1. **Are there any red indicators?** (Obvious, but people miss this)
2. **Are the numbers within expected ranges?** (Know your baselines)
3. **Are there any unusual patterns?** (Trends matter more than single data points)

**Pro tip:** If you're looking at more than 10 metrics, you're probably over-engineering your monitoring.

### Step 2: The Disk Space Reality Check (1 minute)

```bash
# The command that saves careers
```

![The command that saves careers](/images/posts/2025-12-09-the-5-minute-server-health-check-that-could-save-your-career.png)

```bash
df -h

# But here's what you actually need to check
df -h | grep -E '9[0-9]%'
```

If anything shows 90% or higher, you've got a problem brewing. 95%+ means you need to act *today*, not tomorrow. I've seen entire production databases crash because a log file filled the only remaining 2% of disk, and the application couldn't write its temp files. It's embarrassing when it happens, and it's completely preventable.

**Common culprits I see in production:**

- **Log files growing uncontrollably** — Set up `logrotate` or configure your application's log manager. Nginx, for instance, can rotate logs weekly with `access_log /var/log/nginx/access.log combined;` plus a cron job. If you're running Docker, container logs can silently eat gigabytes — set `--log-opt max-size=10m --log-opt max-file=3` on your containers.
- **Temporary files never cleaned up** — `/tmp` and `/var/tmp` are black holes. Add a weekly cron: `find /tmp -type f -atime +7 -delete`. Be careful with `/tmp` if you have long-running jobs that rely on temp files, but for most web servers this is safe.
- **Someone's home directory full of movies** — It happens more than you'd think. Set disk quotas per user with `edquota` if you're on Linux. It takes 5 minutes to configure and saves you from the "developer downloaded 50GB of training data to /home" scenario.
- **That "temporary" test database that's been running for 6 months** — Tag your test resources. I use a convention where any test database, VM, or container has `TEST-` in the name and an automated cleanup script runs monthly. If something needs to persist, it gets explicitly excluded.

### Step 3: The Process Health Scan (1 minute)

```bash
# Find the real troublemakers
ps aux --sort=-%mem | head -10
ps aux --sort=-%cpu | head -10
```

Look for:

- **Processes consuming abnormal amounts of CPU or memory** — If a web server is suddenly eating 90% CPU, it's either handling a traffic spike (check your monitoring dashboard) or stuck in a loop (restart it and check the logs). For memory, remember that Linux uses free RAM for disk caching — the `available` column in `free -h` is more useful than `free`.
- **Zombie processes** — Processes marked with a `Z` in the `STAT` column of `ps aux`. They're already dead but their parent process hasn't acknowledged the death. A few zombies are normal; dozens usually mean a poorly-written application. Find the parent with `ps -o ppid= -p <zombie_pid>` and restart it.
- **Processes that should have stopped but didn't** — Maybe you killed a deployment script but the underlying build process kept running. Or a cron job spawned a child process that outlived the cron. These orphaned processes eat resources silently.

### Step 4: The Log Pattern Check (1 minute)

```bash
# Check for recent errors
journalctl --since "1 hour ago" | grep -i error | tail -5

# Or for systems using traditional syslog
tail -100 /var/log/syslog | grep ERROR
```

**What to look for:**

- **Repeated error patterns** (indicates systemic issues) — If you see the same error 50 times in an hour, it's not a fluke. Something changed. A config file got overwritten, a dependency updated, or a disk is failing. Find the first occurrence with `journalctl --since "1 hour ago" | grep -i error | head -1` and work forward from there.
- **Permission denied errors** (usually means a service broke) — A deployment probably ran as the wrong user, or a file got moved and lost its permissions. Quick fix: `sudo -u <service_user> cat /path/to/file` to verify the service user can actually read it.
- **Connection timeouts** (network or service issues) — If a service can't reach its database, check three things in order: is the database process running (`systemctl status mysql`), is the network reachable (`nc -zv db-host 3306`), and is the DNS resolving (`dig db-host`). I've wasted hours chasing "network issues" that were just a typo in a config file.

### Step 5: The Service Status Reality (1 minute)

```bash
# Quick service health check
systemctl list-failed

# Or for older systems
service --status-all 2>&1 | grep -E "(FAIL|STOP)"
```

## What About Remote Servers?

If you manage more than 2-3 servers, logging into each one manually defeats the purpose. Here's how to scale this:

### The SSH One-Liner Approach

```bash
# Check disk + failed services across 5 servers in 10 seconds
for host in web1 web2 db1 db2 cache1; do
  echo "=== $host ==="
  ssh $host "df -h | grep -E '9[0-9]%'; systemctl list-failed --no-pager"
done
```

Set this up with SSH keys (not passwords) and a `~/.ssh/config` file with host aliases. If you're managing more than 10 servers, use Ansible — a simple `ansible all -m command -a "df -h"` does the same thing across your entire fleet in parallel.

### The Cron Approach

For a daily automated report that hits your inbox at 8:55 AM:

```bash
# /etc/cron.d/daily-health-check
55 8 * * * root /opt/scripts/health-check.sh | mail -s "Daily Server Health" you@yourdomain.com
```

This way, problems are waiting in your inbox when you sit down with your coffee. No logging in required.

## Making This Actionable

The secret isn't having the perfect monitoring setup—it's developing the habit of doing this daily check before you get your coffee.

### Create Your Script

Here's a simple script I use:

```bash
#!/bin/bash
# Daily sysadmin health check
echo "=== $(date) ==="

echo "Disk Usage:"
df -h | grep -E '9[0-9]%'

echo -e "

Top Memory Processes:"
ps aux --sort=-%mem | head -5

echo -e "

Top CPU Processes:"
ps aux --sort=-%cpu | head -5

echo -e "

Failed Services:"
systemctl list-failed --no-pager

echo -e "

Recent Errors (last hour):"
journalctl --since "1 hour ago" --no-pager | grep -i error | tail -3
```

Run this every morning at 9 AM. Set it as a cron job, or better yet, do it manually while you wait for your coffee to brew.

## The Real Secret

The most important part isn't the commands—it's the *consistency*. When you do this every day, you start to recognize what's normal for your environment. That baseline knowledge is more valuable than any monitoring tool.

### Warning Signs You Should Know

- **Sudden spikes in error rates** (even if still "low")
- **Processes that restart frequently** (usually indicates resource issues)
- **Disk usage that increases daily** (disk leaks are real)
- **Memory usage that never decreases** (memory leaks are realer)

## When This Isn't Enough

This 5-minute check won't catch everything, and that's not its purpose. It's designed to catch the 80% of problems that are obvious if you just look.

For the remaining 20%, you'll need proper monitoring, alerting, and incident response procedures. But start with this—it's the foundation everything else builds on.

## Make It Part of Your Morning Routine

Pick a consistent time, make it non-negotiable, and do it every single day. Your future self (and your sleep schedule) will thank you.

Remember: the best time to find problems is when you're not in crisis mode. This simple habit has saved me countless late nights and probably my job more than once.

---

*What are your daily health check routines? Share your favorite commands or scripts in the comments below. Let's build a community of proactive sysadmins.*

*Related reads:*
- *[Why Your Monitoring is Broken (And How to Fix It Before Your Boss Notices)](/sysadmin/2025-11-06-why-your-monitoring-is-broken-and-how-to-fix-it-before-your-boss-notices/)*
- *[The Friday Backup Audit: Because Hope Is Not a Strategy](/sysadmin/2025-12-12-the-friday-backup-audit-because-hope-is-not-a-strategy/)*
- *[Stop Doing Things Manually: 5 Scripts That'll Make You Look Like a Genius](/sysadmin/stop-doing-things-manually/)*