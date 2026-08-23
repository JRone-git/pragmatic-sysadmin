---
title: "I Built Homelab Architect — Plan Your Stack Before You Build It"
date: 2026-08-23
author: Pragmatic Sysadmin
description: "Homelab Architect is a free browser tool that parses your docker-compose.yml and generates a resource dashboard, security audit, dependency map, and backup plan. Works offline, no signup."
draft: false
tags: ["homelab", "docker", "self-hosted", "tools", "beginners"]
slug: homelab-architect-plan-before-you-build
topics: ["homelab", "docker", "tools"]
---

Most homelab beginners make the same mistake: they grab a Docker Compose template, paste it in, and then discover three months later that their "simple setup" is a sprawling mess of undocumented dependencies, a database with no backup, and ports wide open to the internet.

I've been there. I still end up there sometimes.

So I built a tool to catch it before it happens.

<!--more-->

## What Homelab Architect Does

[Homelab Architect](/tools/homelab-architect.html) takes your docker-compose.yml — or lets you build your stack manually from a curated database of 45+ common homelab services — and generates:

- **Resource dashboard** — total CPU and RAM estimates across your entire stack
- **Service cards** — each service with its resource footprint, exposed ports, and restart policy
- **Security audit** — flags `:latest` tags, exposed ports without firewall rules, missing restart policies
- **Single points of failure** — detects services with no backup plan that others depend on
- **Dependency map** — see what talks to what, so you know what to restart in what order
- **Backup plan** — tells you exactly what to back up and how, based on your actual services
- **Export** — save as JSON to share or reload later, or export a Mermaid diagram for documentation

It's essentially the "before you build" companion to [Prism Engine](/tools/prism-engine.html)'s "after you've built" visualization.

## How It Works

**Import tab:** Paste your docker-compose.yml. The parser extracts services, ports, volumes, `depends_on` relationships, and restart policies. It maps image names to a database of 45+ known services (PostgreSQL, Nginx, Plex, Home Assistant, Pi-hole, and more) to fill in resource estimates and security flags automatically.

**Builder tab:** Don't have a compose file yet? Browse services by category (Infrastructure, Media, Automation, Security, Network) or search by name. Add them one by one, specify dependencies, and build your plan from scratch.

## What It Catches

A few examples from my own docker-compose files:

- **`nginx:latest`** → flagged as a security issue. Pin to `:1.27-alpine` or similar
- **Database without `restart: unless-stopped`** → marked as a single point of failure. A crash means manual intervention
- **Service with no backup recommendation** → added to the backup plan with its data directory path

## The Service Database

The builder includes 45+ services with realistic resource estimates:

| Category | Services |
|---|---|
| **Infra** | Nginx, Traefik, Caddy, PostgreSQL, MySQL, MariaDB, Redis, Portainer, Prometheus, Grafana, InfluxDB, MinIO, Watchtower, Docker |
| **Media** | Plex, Jellyfin, Emby, Sonarr, Radarr, Prowlarr, SABnzbd, NZBGet, Bazarr, Calibre-Web, PhotoPrism, Immich |
| **Automation** | Home Assistant, Nextcloud, Gitea, Node-RED, Actual Budget, MQTT, Zigbee2MQTT |
| **Security** | WireGuard, Vaultwarden, Bitwarden, Authelia, Authentik, Duplicati, Vault, Frigate, Mailcow |
| **Network** | Pi-hole, AdGuard Home, UniFi Controller, Uptime Kuma, Statping |

Each entry has CPU/RAM/disk estimates, default ports, known security flags, and backup recommendations.

## No Account, No Upload

Everything runs in your browser. Your docker-compose.yml is never sent anywhere — the YAML parsing, security analysis, and rendering all happen client-side. Works offline after first load.

Try it: [Homelab Architect](/tools/homelab-architect.html)
