---
title: "Second Life — Building a Wall Display From Almost Nothing"
date: 2026-08-01
description: "A six-part build series: turning an ESP32 and an e-paper panel into a wall-mounted smart display. Starting at €30 on a bench, ending at €0 with a dead e-reader."
draft: false
slug: second-life
---

## The idea

Every homelab eventually produces a display-shaped hole. You've got the NAS, the sensors, the MQTT broker — and nothing to *show* for it. A Raspberry Pi in a cupboard is a system. A Raspberry Pi in a frame on the wall is a product.

This series is me building one. A wall-mounted smart display: shows the weather, shows photos, costs almost nothing to run, and doesn't need a subscription.

The twist is that I'm building it in **price order, ascending**, so every part teaches the next one.

| Part | Title | Build cost | What it teaches |
|---|---|---|---|
| **1** | [**The €30 Prototype**](/sysadmin/second-life-part-1-the-30-prototype/) ← read this | ~€29 | Wake → fetch → render → sleep. Real current measurements. |
| 2 | The €56 Wall Mount | ~€45 | 7.5" panel, IKEA frame, ESPHome, 3 months on battery |
| 3 | What Colour Costs | ~€85 | 4-colour vs Spectra 6, and why photos on the wrong panel look awful |
| 4 | The Canvas | ~€254 | 13.3" E-Ink, tiled walls, a real e-ink monitor |
| 5 | The €1,799 Endgame | €1,799 | 43" reflective LCD signage, solar, professional economics |
| 6 | The €0 Version | €0 | A dead e-reader, reflashed. Full circle. |

The prices are real — I checked them, and where I got them wrong the first time I say so in the post.

## Why an ESP32 at all?

Because the constraint is power, not compute.

A Raspberry Pi in a frame draws 3–8 watts. A phone charging on the wall draws 5–15. An old tablet idles at 300–600 mA. That's €30–60/year in electricity and a permanently warm rectangle.

An ESP32 in deep sleep draws **5 µA**. The panel holds its image with literally zero power — it's e-ink, so the picture stays on screen whether or not the device is awake. Wake up every 30 minutes, fetch a 400-byte JSON payload, redraw, go back to sleep.

That's the whole idea. Everything else in this series is detail.

## Start here

### [→ Part 1: The €30 Prototype](/sysadmin/second-life-part-1-the-30-prototype/)

A 4.2" e-paper panel and an ESP32 driver board on a kitchen table. Real current measurements, a working ESPHome config, and the BS jumper setting that can ruin a panel if you get it wrong.
