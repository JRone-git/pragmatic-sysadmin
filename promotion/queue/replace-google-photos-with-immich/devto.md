---
title: "Replace Google Photos with Immich (The Honest 2026 Guide)"
canonical_url: https://pragmaticsysadmin.help/sysadmin/2026-11-10-replace-google-photos-with-immich/
tags: selfhosted, immich, photos, privacy
---

The moment I moved my parents off Google Photos, the free 15 GB of Google One became 200 GB of headroom, and I got back the photos Google had been helping itself to. That part was easy.

The part nobody mentions is that Immich is a real server, not a web app, and it has requirements Google quietly pays for on your behalf. Six gigabytes of RAM, a disk you will back up separately, and a public endpoint on your home connection — which is where most of the sharp edges live.

Here is what actually happened for me when I replaced Google Photos with Immich, checked against the official documentation on 10 November 2026. I've run it on a Pi 5 and on an N100 box, and both taught me something different.

<!--more-->

## What you actually get

Immich is an open-source photo and video backup platform, AGPL-3.0, with apps for Android and iOS that upload new shots to your server automatically. On top of the backup it gives you the things people actually miss when they leave Google Photos:

- **A timeline and albums** that mirror your phone's structure, with the option to exclude an album from backup.
- **Face recognition and natural-language search.** Type "beach 2024" or "grandchildren" and it finds them, because the machine learning runs on your hardware.
- **Original quality.** No compression, no re-encoding. EXIF and GPS stay intact.
- **Shared albums** and public links, so your family can drop photos in without touching your admin account.
- **Free Up Space** on the phone, which removes the backed-up copy from the device once the server has it.

The version numbers matter here. Immich 3.3.6 shipped on 4 November 2026, and it carries a fix for CVE-2026-111497 — a critical buffer overflow in the Brotli decompression library. If you read a guide from 2025, it will predate this and it will tell you to run something with a known critical CVE in it.

## The hardware it actually needs

This is where most guides either lie or skip. Here's what the official requirements actually say:

| Resource | Minimum | Recommended |
|---|---|---|
| RAM | 6 GB | 8 GB |
| CPU | 2 cores | 4 cores |
| Disk | Whatever your library needs | SSD for the database |
| Storage overhead | — | 10 to 20% on top of your originals |

The 10 to 20% is for thumbnails and transcoded video, and it surprised me too. A 100 GB library becomes 120 GB on the disk.

Two more constraints that aren't obvious:

**The database can't live on a network share.** The Postgres files have to sit on a local filesystem with proper user and group ownership — EXT4, ZFS, APFS, BTRFS, XFS all work. NTFS, exFAT and network mounts don't. The database itself is typically 1 to 3 GB, so give it local SSD space and let the photos live wherever you like.

**Since version 3, the machine learning container on x86-64 needs at least the x86-64-v2 instruction set.** That's most CPUs built since around 2012. On an older machine, the machine learning features either fail to start or you run the ARM build.

## Installing it

The official quick start is a Docker Compose file and an environment file, and it takes about five minutes:

```bash
mkdir -p ~/immich-app && cd ~/immich-app

# The official compose file and environment template
wget -O docker-compose.yml \
  https://github.com/immich-app/immich/releases/latest/download/docker-compose.yml
wget -O .env \
  https://github.com/immich-app/immich/releases/latest/download/example.env

# Set your upload location and a database password before starting
sed -i 's|^UPLOAD_LOCATION=.*|UPLOAD_LOCATION=./library|' .env
sed -i 's|^DB_PASSWORD=.*|DB_PASSWORD='"$(pwgen 24 1 -A)"|' .env

docker compose up -d
```

Then open `http://<your-server-ip>:2283` and register. **The first account you create becomes the administrator**, and Immich locks admin sign-up automatically after that first registration. Nobody else can register until you deliberately open it up again. If you expose this to the internet before you have claimed the admin role, you are one unlucky scan away from handing your server to a stranger — so keep port 2283 behind a firewall until the admin account exists.

## The phone setup is where the friction is

The apps are good. The permissions dance is not. Both platforms need one specific thing turned on, and if you skip it the backup silently does nothing:

**On iOS**, enable **Background App Refresh** — Settings, General, Background App Refresh, then Immich on. iOS decides for itself when to run the upload, so the more often your parent opens the app, the more often the backup happens.

**On Android**, you've got to exempt Immich from battery optimisation. Android's aggressive power management will kill the background worker and the upload stops with no error message. The community guide for this is literally called "Don't kill my app". If the phone is on a manufacturer's skin, expect a different path through the settings.

If you have the phone connected over USB, you can check it and fix it from the shell:

```bash
# Is the app on the battery-optimisation ignore list?
adb shell dumpsys deviceidle whitelist | grep -i immich

# If it isn't, add it
adb shell dumpsys deviceidle whitelist +app.immich.android

# Confirm the background worker is actually alive
adb shell dumpsys jobscheduler | grep -A3 immich
```

Backups default to Wi-Fi only, which is the right default. Your parent's phone will not thank you for a 4K video uploading over mobile data.

## The honest downsides

**It only works while it's reachable.** Google Photos works from a hotel in Spain. Immich on your home connection works from your kitchen. You need a real domain, a certificate, and a reverse proxy, or a tunnel. That is the single biggest quality-of-life difference between the two, and it is the reason I would not hand Immich to a parent who travels.

**Pulling from iCloud eats mobile data.** If you select an iCloud album for backup, Immich pulls those assets from iCloud into a cache folder on the phone, then uploads them. On a metered connection, that is your data plan disappearing.

**The built-in backup only covers the database.** The database holds metadata and user records. The actual photos and videos in your upload location need their own backup, and a second one at that, ideally off-site. People discover this on the bad day.

**In my experience it's a lot of surface area for a photo album.** Anyone running a server for a hobby has learned that the interesting part is never the application. It is keeping the thing patched, the disk monitored and the certificate renewed.

## When it is worth it

The honest summary:

- **Worth it** if you have more photos than Google One's cheapest plan holds, if you want face recognition that Google doesn't hand you for free, or if the privacy matters to you.
- **Not worth it** if your library fits comfortably in the free 15 GB and the idea of running a public endpoint makes your stomach turn.
- **Not worth it yet** if the person using the phone travels or isn't technical — they will call you the first time the backup stops, and it will be because iOS didn't feel like running a background task.

If you want the whole stack rather than just the photos, the [Build Your Own Cloud guide](https://pragmaticsysadmin.help/meta/build-your-own-free-cloud-home-server-guide/) has the order to install it in, and the [honest cost post](https://pragmaticsysadmin.help/sysadmin/2026-11-10-cloud-for-cheap-the-honest-cost-math/) works out what the disk and the electricity actually come to. A machine that can run Immich comfortably is not a machine you should buy on impulse — the RAM floor alone rules out most of the cheap boxes.

## Before you start

Three things to sort out first, in this order:

1. **How much data is this?** Google Takeout will export your whole library, and the download is slower and more painful than you expect. Do it before you commit.
2. **Where does it live?** The upload location needs to be on a real filesystem with real space. Decide that before you install anything.
3. **Who else touches it?** Every extra person with an account is another invitation to forget a password.

Then install it, put the admin account in place, and only then open it to the family.

*Self-hosting your photos is not saving money. It is deciding that the photos are yours, and then accepting what that costs.*
