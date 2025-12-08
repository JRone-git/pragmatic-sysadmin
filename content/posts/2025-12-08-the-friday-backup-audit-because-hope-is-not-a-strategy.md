
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
find /mnt/backups/ -name "*.tar.gz" -mtime -1 -ls
```

If that returns nothing, your backup script died yesterday. If it returns files from 2024, you've been flying blind for a year.

**Pro tip:** Don't trust the filename (e.g., `backup-2025-12-14.tar.gz`). Trust the filesystem timestamp. Scripts can name empty files with today's date easily.

### Step 2: The Size Deviation Scan (2 minutes)

Backups should grow slowly over time. If a backup is suddenly 50% smaller than yesterday, you didn't save space—you lost data.

```bash
# Compare sizes of the last 5 backups
ls -lhSr /mnt/backups/db-prod-*.sql.gz | tail -5
```

**Red Flags:**
- A sudden drop in file size (did the table lock fail?)
- A file size of exactly 0 bytes or 4kb (empty header)
- A size that hasn't changed by a single byte in weeks (is it backing up a stale staging copy?)

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

If your "daily" backup only contains dates from 2023, you're backing up an old volume.

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

Once a month, take your backup and actually restore it to a virtual machine or a test container. 
*   Does the app start?
*   Can you log in?
*   Is the data from yesterday there?

Documentation is great, but muscle memory is better. When production is down, you don't want to be reading `man tar` for the first time in years.

## Summary

Backups are a promise to your future self. Keep that promise.

1.  **Check timestamps** (ensure it ran).
2.  **Check sizes** (ensure it grabbed data).
3.  **Check integrity** (ensure it's not corrupt).
4.  **Practice the restore** (ensure you know how).

Do this, and you’ll sleep through the night—even when the alerts start firing.

---

*Do you have a backup horror story? Or a script that saved your bacon? Drop it in the comments below.*
```
