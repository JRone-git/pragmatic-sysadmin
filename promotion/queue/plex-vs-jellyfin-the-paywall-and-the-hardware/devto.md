---
title: "Plex vs Jellyfin in 2026: The Paywall and the Hardware"
canonical_url: https://pragmaticsysadmin.help/sysadmin/2026-11-10-plex-vs-jellyfin-the-paywall-and-the-hardware/
tags: selfhosted, streaming, mediaserver, homelab
---

My old Plex server stopped working for my parents the moment they left the house. Not broken — *working exactly as designed*. Remote streaming had become a subscription, the person watching from abroad needed their own pass, and I had become the family's IT department for a media server I'd already paid for.

That is the whole story of Plex in 2026, and it is why the answer for most people is Jellyfin. But the interesting part is what the paywall does and doesn't cover, and how much hardware a free media server actually needs. I have moved two households off Plex and the second was much easier, because I'd already made the mistakes on the first one.

<!--more-->

## What changed, and when

Two dates matter here, and both are recent.

**April 2025** is when Plex removed free remote playback. Before that, streaming your own library from anywhere was included in the free server. After it, remote streaming needs either a Plex Pass on the account that owns the server, or a separate Remote Watch Pass on each viewer's account. Plex's own support documentation is blunt about the second one: it "only enables remote streaming of personal content and does not provide access to any other premium features."

**1 July 2026** is when the price of a new Lifetime Plex Pass went from $249.99 to $749.99. Plex says existing lifetime holders keep everything, which is fair, but it means the "buy it once" option now costs three times what it did.

Jellyfin, meanwhile, was forked from Emby in 2018 and has never had a paid tier. No subscription, no account, no premium unlock. The server, every official client, hardware transcoding, live TV and recording are all free.

## The price list

Checked against Plex's own plans page on 10 November 2026:

- **Jellyfin** — $0.00. No paid tier, no account, no telemetry, no feature behind a paywall.
- **Plex Pass** — $6.99 a month, $69.99 a year, or $749.99 for the lifetime.
- **Remote Watch Pass** — $2.99 a month or $29.99 a year, remote streaming only, for someone watching a server they don't own.
- **Plex free** — still free, but local streaming only. Your phone on the same Wi-Fi, and nothing else.

So the honest comparison for somebody whose parents watch from another country: Plex costs $6.99 a month forever, or $2.99 a month per viewer with the cheaper pass, or $749.99 once. Jellyfin costs nothing and your time, which for me was a weekend and then never again.

## What Plex Pass actually unlocks

This is the part worth reading twice, because it's longer than most people assume:

- Remote streaming, for everyone on the server
- Hardware transcoding — offloading the codec work to the GPU
- Live TV and DVR recording, with a tuner
- Offline sync, downloads for offline viewing
- Skip Intro and Skip Credits
- Parental controls and the Plex Dash monitoring app

Against that, Jellyfin gives you all of it, free, except that you have to set up the network path yourself.

That last part is the actual trade. Plex runs a relay service so you don't have to open a port on your router. Jellyfin doesn't run anything for you, so remote access means port forwarding, a reverse proxy with a real certificate, or a VPN back to your house. It's maybe half an hour of work and it's yours forever. I did it with a reverse proxy and a Let's Encrypt certificate, and it's been running for two years without a single interruption.

## The hardware question

People assume a media server needs a big machine. It doesn't, unless you want to transcode.

**Direct play** means the phone or TV plays the file exactly as it is stored. No processing, no GPU, almost no power. A Raspberry Pi 4 or 5 handles direct play for a normal family's library without breaking a sweat, and mine has been doing exactly that for years.

**Transcoding** happens when the client can't handle the codec, the bitrate is too high for the connection, or subtitles have to be burned in. That's when you want a GPU.

The practical guidance from Jellyfin's own hardware notes, and the reason I like this project:

- An **Intel N100 mini PC** handles 8 to 12 simultaneous 1080p hardware transcodes. The chip's integrated GPU does Intel Quick Sync with H.264, HEVC and AV1 decode and encode.
- A **Pi 4 or 5** is fine for direct play only.
- Jellyfin's guide recommends against AMD integrated graphics, and suggests an Intel Core i5-11400, a Pentium Gold G7400, an N100, or Apple silicon if you want to go further.
- Jokes aside, the guide also wants 8 GB of RAM and a 100 GB SSD for the config and metadata.

Jellyfin supports Intel QSV, NVIDIA NVENC, AMD AMF, VA-API on Linux, Apple VideoToolink on macOS and Rockchip RKMPP. On an N100 box that's free hardware acceleration. On Plex, hardware transcoding is behind Plex Pass — so the same box costs you $70 a year, or $249.99 for the five-year pass, to do the identical job.

## The privacy difference

Plex requires a plex.tv account, and authentication routes through Plex's own cloud servers even for local-only playback. That's not a bug — it's how a hosted service works — but it does mean the operator of your media server is talking to Plex on every playback.

Jellyfin runs no servers for its users. There is no account to create, no telemetry to opt out of, and nothing phoned home. The only traffic is between your devices and your own server.

Neither project will ever get into your files. But one of them gets a log of when you watch things.

## The thing Jellyfin does not replace

Let me be blunt, because this is where "replace Netflix with Jellyfin" advice goes wrong.

**Jellyfin does not replace Netflix.** It streams the media you already own. If you don't own the films, Jellyfin has nothing to play, and neither does any other self-hosted server on earth. A 4 TB disk of your own library is worth more than a catalogue you rent.

What Jellyfin replaces is the **software**. The Plex paywall, the account, the client apps and the "your server is offline" messages. That's a real saving, and for the price of a weekend it's an enormous one.

The same logic applies to the rest of this site. If you're weighing up replacing a subscription with a self-hosted box, the honest question is whether you were going to use it anyway. Sometimes the answer is yes and the saving is enormous. Sometimes the answer is that you never used it and the saving is zero — in which case, cancel.

## Running it

If you want the transcoding, this is the whole thing — the `/dev/dri` mount is what lets Jellyfin reach your Intel GPU for Quick Sync:

```bash
docker run -d --name jellyfin \
  --restart unless-stopped \
  -v /opt/jellyfin/config:/config \
  -v /mnt/media/movies:/media/movies:ro \
  -v /mnt/media/tv:/media/tv:ro \
  -p 8096:8096 \
  --device /dev/dri:/dev/dri \
  --group-add "$(getent group render | cut -d: -f3)" \
  jellyfin/jellyfin:latest
```

Then open `http://<server-ip>:8096`, create the admin account, and turn on the hardware transcoder under Dashboard, Playback, Transcoding. I skipped that step on my first install and spent an evening wondering why a 4K film stuttered on the TV while the same file played fine on the laptop.

## Migrating from Plex

This part is genuinely easy, which surprises people who've spent years inside Plex's ecosystem.

1. **Point Jellyfin at the same folders.** Plex's library structure carries over. Your movies, your show metadata, your artwork — all of it.
2. **Let Jellyfin fetch its own metadata.** It scans the same files and pulls from the same sources. Give it an evening.
3. **Point the clients at the new server.** Jellyfin has official apps for the platforms Plex covers.
4. **Sort out the remote path.** Port forward 8096, or put a reverse proxy with a certificate in front of it.
5. **Keep Plex running for a fortnight** before you cancel anything. Not because it will be missed, but because you will find something.

The clients are the only real difference, and it's a small one. Jellyfin's smart TV apps are good rather than beautiful, and its interface takes an afternoon to make sense of. Plex is a bit more polished. Neither is a reason to pay a subscription forever.

## What to do next

If you want the whole home-lab picture rather than just the media server, the [Build Your Own Cloud guide](https://pragmaticsysadmin.help/meta/build-your-own-free-cloud-home-server-guide/) has the stack and the order to install it in, and the [honest cost post](https://pragmaticsysadmin.help/sysadmin/2026-11-10-cloud-for-cheap-the-honest-cost-math/) works out what the box and the electricity come to.

If you want the short version of the hardware decision:

- **Direct play only** — a Pi, an old laptop, whatever is in the cupboard.
- **Transcoding** — an N100 mini PC and Jellyfin, and that's the whole bill.

Check your library before you commit. Run the hardware through Jellyfin's own transcoding guide with a few of your actual files, not a demo clip. The format that breaks everything is the one you own.

*Free software and a free subscription are different things. One of them stops working when the company changes its mind.*
