---
title: "The Friday Backup Audit: Because Hope Is Not a Strategy"
date: 2025-12-14T08:00:00Z
draft: false
tags: ["backups", "recovery", "bash", "disaster-recovery"]
categories: ["Operations", "Safety Nets"]
description: "Backups are useless if they don't restore. Here is the 10-minute audit to prevent the 'Schrödinger's Backup' scenario."
---

## The Nightmare Scenario

We’ve all heard the horror stories. A database corruption hits production. The team stays calm because "Don't worry, we have nightly backups." 

Then comes the moment of truth: `tar -xvf backup.tar.gz`.

**Error: Unexpected EOF in archive.** 
Or worse: The file extracts perfectly, but the database inside is empty because the `mysqldump` command failed silently three months ago.

If you haven't restored a backup, you don't have a backup. You just have a file taking up disk space.

## The "Schrödinger's Backup" Problem

A backup exists in a state of quantum superposition: it is both successful and failed until you actually try to use it. 

Most sysadmins automate the *creation* of backups but rarely automate the *verification*. I’ve learned the hard way that you need a ritual for this, just like your daily health check. I do this every Friday.

### Step 1: The Timestamp Reality Check (1 minute)

First, ensure your automation is actually running. A silent cron job is a deadly cron job.

```bash
# Check if your backup files are actually new

![Check if your backup files are actually new](/images/posts/2025-12-12-the-friday-backup-audit-because-hope-is-not-a-strategy.png)

find /mnt/backups/ -name "*.tar.gz" -mtime -1 -ls
```

If that returns nothing, your backup script died yesterday. If it returns files from 2024, you've been flying blind for a year. I once discovered that a backup cron job had been silently failing for 8 months because the backup server's SSH key had been rotated and nobody updated the authorized_keys file on the other end. The backup script ran every night, created a zero-byte file, and exited with a success code. Nobody noticed until we needed the backup.

**Pro tip:** Don't trust the filename (e.g., `backup-2025-12-14.tar.gz`). Trust the filesystem timestamp. Scripts can name empty files with today's date easily. I've seen backup scripts that do `touch backup-$(date +%F).tar.gz` as a "placeholder" before the actual backup runs — and then the actual backup fails. You're left with a zero-byte file named with today's date. Always check `ls -la`, not just `ls`.

### Step 2: The Size Deviation Scan (2 minutes)

Backups should grow slowly over time. If a backup is suddenly 50% smaller than yesterday, you didn't save space—you lost data.

```bash
# Compare sizes of the last 5 backups
ls -lhSr /mnt/backups/db-prod-*.sql.gz | tail -5
```

**Red Flags:**

- **A sudden drop in file size** (did the table lock fail?) — If your database dump goes from 2.1 GB to 800 MB overnight, something went wrong. Maybe `mysqldump` hit a lock timeout and only dumped half the tables. Maybe a table was dropped. Either way, investigate before you need this backup.
- **A file size of exactly 0 bytes or 4kb** (empty header) — This means the backup process started but produced nothing. The most common cause: the source directory was empty (maybe a mount point didn't mount), or the backup command failed silently.
- **A size that hasn't changed by a single byte in weeks** (is it backing up a stale staging copy?) — If your production data is growing but your backups aren't, you might be backing up the wrong volume. This happened to me once: the production database moved to a new volume, but the backup script was still pointing at the old mount path. The old volume had been frozen for weeks.

### Step 3: The Integrity Test (2 minutes)

You don't need to do a full restore to check for corruption. Most archive tools have a "test" flag that reads the file without writing to disk.

```bash
# For GZIP files (checks for CRC errors)
gzip -t /mnt/backups/latest-backup.tar.gz

# For TAR files (lists contents, proving readability)
tar -tf /mnt/backups/latest-backup.tar > /dev/null
```

If `gzip` complains, that file is garbage. Better to know now than when the CEO is standing behind your desk.

### Step 4: The "Golden Sample" Grep (2 minutes)

This is my favorite trick. Don't just check the container; check the data. Grep the compressed file for a string you *know* should be there (like the current year or a specific recent user).

```bash
# Check if the SQL dump actually contains recent data
zgrep "2025-12" /mnt/backups/db-dump.sql.gz | head -5
```

If your "daily" backup only contains dates from 2023, you're backing up an old volume. I caught exactly this problem once — a backup script was pointed at a snapshot volume that hadn't been updated since a server migration six months earlier. The backups ran every night, the files grew at the expected rate, and the integrity checks passed. The only thing wrong was that none of the data was current. The golden sample grep was the only check that would have caught it.

## Automating the Paranoia

Manual checks are good, but scripts don't forget. Here is a verification script I run immediately after my backup jobs finish.

### The Verification Script

```bash
#!/bin/bash
# verify_backups.sh
# Fails loudly if backups look suspicious

BACKUP_DIR="/mnt/backups"
MIN_SIZE_KB=10240 # 10MB minimum expected size

echo "=== Starting Backup Verification ==="

# 1. Find the newest backup file
LATEST_BACKUP=$(ls -t $BACKUP_DIR/*.tar.gz 2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "CRITICAL: No backup files found!"
    exit 1
fi

echo "Checking: $LATEST_BACKUP"

# 2. Check if it is stale (older than 24 hours)
if test `find "$LATEST_BACKUP" -mtime +1`; then
    echo "CRITICAL: Latest backup is older than 24 hours!"
    exit 1
fi

# 3. Check file size
FILE_SIZE=$(du -k "$LATEST_BACKUP" | cut -f1)
if [ "$FILE_SIZE" -lt "$MIN_SIZE_KB" ]; then
    echo "CRITICAL: Backup is suspiciously small ($FILE_SIZE KB)."
    exit 1
fi

# 4. Check integrity
if ! gzip -t "$LATEST_BACKUP"; then
    echo "CRITICAL: Gzip integrity check failed. File corrupted."
    exit 1
fi

echo "SUCCESS: Backup appears healthy."
```

## The "Fire Drill"

There is one final step that scripts can't do: **The Full Restore.**

Once a month, take your backup and actually restore it to a virtual machine or a test container. Not a "selective extract" — a full, from-scratch restore. This is the only test that actually proves your backup works end-to-end.

*   Does the app start?
*   Can you log in?
*   Is the data from yesterday there?
*   Are the file permissions correct?
*   Did the database credentials get restored properly (if they were in config files)?

Documentation is great, but muscle memory is better. When production is down, you don't want to be reading `man tar` for the first time in years. I keep a one-page "restore runbook" for every critical system — the exact commands, in order, to go from backup file to running application. It's saved me during two actual outages.

### Real Disaster Stories (From My Career)

I promised I'd share, so here are two real situations where backups either saved the day or nearly ended careers. Names changed to protect the embarrassed.

**The $50,000 Database That Wasn't Backing Up**

A client ran an e-commerce platform on a managed database service. They assumed the managed service provider handled backups because the dashboard showed "backups enabled." Turns out, that toggle only enabled *manual* snapshots — not automatic ones. Nobody had clicked "create snapshot" in 14 months.

When a developer ran an `UPDATE` without a `WHERE` clause and wiped the `orders` table, we went to restore. The most recent snapshot was 14 months old. They lost every order from the past year. The cost of re-entering those orders (customer service time, lost records, GDPR implications) was estimated at over €50,000. All because someone saw a green toggle and assumed it meant "automated daily backups."

After that incident, I added a specific check to my Friday audit: log into every managed service dashboard once a month and verify that automatic backups are actually scheduled, not just "enabled."

**The Backup That Restored Perfectly — Into the Wrong Database**

This one's almost comical. A PostgreSQL backup was running perfectly every night, integrity checks passed, golden sample grep showed current data. Everything looked great. Then during a restore test, we realized the backup script was dumping the *staging* database instead of *production*. Both were on the same server, and the script had been pointing at the wrong database name since a migration three months earlier.

The staging database was a static copy that didn't change, so the backups looked fine — same size every day, always passed integrity, always had the right dates in the data. But it wasn't production. We only caught this because we did a full restore test and compared the record counts to the live production database.

Lesson: your golden sample should include something that changes frequently — a record count comparison, a checksum of a known-changing table, or at minimum a `SELECT COUNT(*) FROM <frequently_updated_table>` compared against the live database.

## Backup Tools Compared: rsync vs Borg vs Restic

If you're building a backup system, you'll eventually need to pick a tool. Here's my honest comparison based on years of using all three in production and at home:

**rsync** — The Old Reliable

rsync has been around since 1996 and it's installed on virtually every Linux system. It does incremental file-level transfers and not much else.

Strengths: Zero learning curve, already installed everywhere, great for simple directory mirroring. If you just need to copy files from A to B, rsync is perfect.
Weaknesses: No built-in encryption, no deduplication, no compression of the backup archive. You need to layer these features yourself. No snapshot management — you're responsible for rotation and retention. If you want point-in-time recovery, you need to maintain multiple full copies.
Best for: Simple directory syncs, mirroring files between servers, copying data to an NFS mount.

**BorgBackup** — The Sweet Spot

Borg adds deduplication, compression, encryption, and efficient storage to the rsync concept. It's what I used for years before switching to restic.

Strengths: Excellent deduplication (backups are fast and small), built-in encryption (AES-256), automatic compression, easy to set up with a simple CLI. The `borg list` and `borg diff` commands make it easy to browse and compare backups. Active community, well-documented.
Weaknesses: The server side requires Borg to be installed on the remote machine — you can't back up to arbitrary SFTP servers or cloud storage without workarounds. Repository format changed between versions (though migrations are handled automatically). Requires a dedicated "repository" directory structure.
Best for: Backing up to a Linux server you control, especially over SSH. Great for home labs and small-to-medium production setups.

**Restic** — The Modern Choice

Restic was designed from the start to support multiple storage backends (S3, B2, SFTP, local disk, etc.) while keeping Borg's strengths.

Strengths: Supports cloud storage natively — Backblaze B2, AWS S3, Wasabi, MinIO all work out of the box. Built-in encryption and deduplication. The `restic check` command is thorough and fast. Clean, consistent CLI. No server-side software needed for most backends. Can back up directly to S3-compatible storage without SSH.
Weaknesses: Slightly slower than Borg for local-to-local backups (the overhead of the abstraction layer). The `restic forget --prune` command for retention management can be confusing at first. Less mature ecosystem than Borg (fewer GUI tools, though you probably don't need one).
Best for: Backing up to cloud storage, any environment where you want to push to S3/B2, heterogeneous backup targets.

My current setup: I use restic for everything. The ability to back up directly to Backblaze B2 without needing a Borg server on the other end was the deciding factor. For a Friday audit, restic makes it easy — `restic check` verifies repository integrity, and `restic ls latest | head -20` shows you what's in the most recent snapshot.

## The 3-2-1 Rule (Because It Actually Matters)

You've probably heard this before, but are you actually doing it?

- **3 copies** of your data (production + primary backup + secondary backup)
- **2 different storage types** (local disk + cloud/object storage)
- **1 copy off-site** (different building, different provider, different region)

I use [Backblaze B2](https://www.backblaze.com/b2/) for the off-site copy. It's $6/TB/month, which means my 50 GB of critical backups cost about $0.30/month. There's no excuse for not having an off-site copy in 2026. The upload can be automated with `restic` or `rclone` on a cron schedule. Set it up once, check it monthly, and forget about it.

## Summary

Backups are a promise to your future self. Keep that promise.

1.  **Check timestamps** (ensure it ran).
2.  **Check sizes** (ensure it grabbed data).
3.  **Check integrity** (ensure it's not corrupt).
4.  **Check content** (ensure the data inside is actually recent — the golden sample grep).
5.  **Practice the restore** (ensure you know how).

Do this every Friday. It takes 10 minutes. That 10 minutes has saved me from two potentially career-ending restore failures. One where the backup file was corrupt (gzip CRC error, caught by Step 3), and one where the backup was pulling from a stale volume that hadn’t been updated in weeks (caught by Step 4’s golden sample grep).

The ugly truth about backups is that most organizations only discover their backups are broken when they actually need them. By then, it’s too late. The Friday audit is how you find out on a quiet Tuesday afternoon, when there’s still time to fix it.

If you only do one thing from this post, set up the verification script and wire it to send you an email when it fails. That single step moves you from “hoping” to “knowing.”

Do this, and you’ll sleep through the night — even when the alerts start firing.

---

*Do you have a backup horror story? Or a script that saved your bacon? Drop it in the comments below.*

*Related reads:*
- *[The 5-Minute Server Health Check That Could Save Your Career](/sysadmin/2025-12-09-the-5-minute-server-health-check-that-could-save-your-career/)*
- *[Why Your Monitoring is Broken (And How to Fix It Before Your Boss Notices)](/sysadmin/2025-11-06-why-your-monitoring-is-broken-and-how-to-fix-it-before-your-boss-notices/)*
- *[The Art of Reading Logs Like a Detective: Finding Needles in Haystacks](/sysadmin/2025-12-17-the-art-of-reading-logs-like-a-detective-finding-needles-in-haystacks/)*
