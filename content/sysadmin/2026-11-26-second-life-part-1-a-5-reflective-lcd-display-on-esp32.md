---
title: "Second Life, Part 1: A $5 Reflective LCD Display on ESP32"
date: 2026-11-26
author: Pragmatic Sysadmin
description: "Part 1 of the hallway display build: a $3.57 reflective LCD panel, a $1.09 ESP32-C3, the wiring, and the three tests that decide whether it works."
tags: ["sysadmin", "budget-hardware", "edge-compute", "esp32", "diy", "performance"]
categories: ["System administration"]
topics: ["esp32", "display", "diy"]
draft: true
reviewed: false
no_publish: true
aiAssisted: true
ShowToc: true
blogforge:
  provider: assistant
  model: "MiniMax-M3.1-Flash"
  generated_at: "2026-11-26T12:00:00Z"
  attempts: 1
  style_score: 100
  topic: "Second Life, Part 1: A $5 Reflective LCD Display on ESP32"
---

In early November I published the plan for a wall display for my parents: a reflective LCD panel, a $1.09 microcontroller, and a prototype on a breadboard.

Then I found a $3.57 panel from the same family. Same controller, same 300×400 geometry, same 24-pin connector. A third of the price, and it ships as one piece instead of a minimum order of five.

That price is the difference between a weekend project and a project I keep postponing. This is the spike: the parts, the wiring, and the three tests that decide whether it works.

<!--more-->

## I assumed this was e-paper, and I was wrong

I went into this expecting the panel family I already wrote about: draw an image, cut the power, the image stays. That's e-paper, and it's exactly why e-paper is good for something that hangs on a wall for months.

The Sitronix ST7305/ST7306 controller in these panels is not memory-in-pixel. It's a TFT backplane controller with two power modes. In high-power mode (command `0x38`) the panel refreshes itself at 32 Hz while you write a frame. In low-power mode (command `0x39`) it drops to 1 Hz and holds a static image on its own, with the microcontroller doing nothing at all.

So the picture survives the ESP32 going to deep sleep. It does not survive the panel losing power. That one difference decides the power design before I've wired anything up.

Two more things come free with the same datasheet, and both of them are why you might prefer this panel to an e-paper one. There's no backlight — the panel makes its image out of the light already in the room, the way paper does, at a contrast ratio of 15:1. And updates are silent. No black-and-white flash, no two-second e-paper wave, no tearing.

If you've used e-paper, that's the pitch: same paper-like look, no strobe, and the panel refreshes itself at 1 Hz instead of every few seconds.

## The parts list, and the two items you can skip

Prices checked 26 November 2026. AliExpress moves them around, so check the listing against your own basket before you pay.

| Item | Price | Where | Notes |
|---|---|---|---|
| **4.2" reflective TFT, ST7306, 300×400, breakout board** | **$3.57** | AliExpress | One piece, header already fitted |
| 4.2" reflective TFT, ST7305 | $10.83 | Good Display | The fallback if the cheap panel won't initialise |
| 4.2" reflective TFT, ST7306, bare FPC | $2.56 each | Alibaba | Minimum order of five, so $12.80 to get one |
| ESP32-C3 SuperMini | $1.09 | AliExpress or eBay | 4 MB flash, Wi-Fi and BLE |
| 24-pin 0.5 mm FFC ribbon | $1–3 | AliExpress | Only for the bare panel |
| 24-pin FPC-to-header adapter | $1.09–3.25 | AliExpress | Only for the bare panel |
| Breadboard and jumper wires | $3–6 | Anywhere | |
| USB-C cable | $3 | Anywhere | Must be a data cable, not charge-only |

The panel is [this AliExpress listing](https://www.aliexpress.com/item/1005012318553820.html), and you want the breakout-board variant. It fits the header for you, which removes the ribbon and the adapter from the list entirely — two 0.5 mm pitch connectors you can get wrong, and the single most likely reason a build like this ends in a silent blank screen.

The microcontroller is the {{< aff merchant="ebay" text="ESP32-C3 SuperMini" url="https://www.ebay.com/sch/i.html?_nkw=esp32+c3+supermini" >}}, and any {{< aff merchant="ebay" text="830-point breadboard" url="https://www.ebay.com/sch/i.html?_nkw=830+point+breadboard" >}} will do.

Panel plus microcontroller is $4.66. Add the breadboard and a cable and you're at roughly $11.

Buy two panels. The most likely failure in your build is a panel that never initialises, and it looks exactly like a dead panel. Two of them turn a dead end into a twenty-minute swap instead of a week of waiting for shipping.

## The cheapest listing costs more than the good one

The cheapest reflective TFT listing on Alibaba is a minimum order of five. If you need one panel, that listing costs more in total than buying the panel you actually want from Good Display, which sells a single one with the adapter board already fitted.

The minimum order only makes sense if you want spare panels, and you can get those far more cheaply by buying two of the single-piece ones. So the five-panel listing is a trap for a first build, and a bargain if you're building five of them.

## Two pins you must leave unconnected

The panel's 24-pin connector carries its own gate drive voltages, and this is the bit that surprises people.

Pin 18 is VGH. Pin 24 is VGL. Both are **outputs** — the panel generates its own high and low gate voltages internally and exposes them on the connector. There's no boost converter to buy, which is nice. But leave them unconnected and leave them unconnected: tie either one to a rail and the panel stops working, and you'll lose an evening to a fault that looks exactly like a dead panel.

The rest of the pinout:

- Panel pins 5 and 6 → 3V3 (2.55–3.3 V accepted)
- Panel pins 1, 4, 7, 13, 20 and 21 → GND — tie all of them, none floating
- Pin 8, RESET → GPIO10
- Pin 9 or 10, SCL → GPIO4, the native FSPI clock
- Pin 12, SDA → GPIO5, the native FSPI data line
- CS → GPIO6
- DC → GPIO7
- Pin 18, VGH and pin 24, VGL → leave unconnected
- TE → leave unconnected; the drivers don't use it

The exact pin numbers for CS and DC depend on which adapter board you end up with, so read them off your own parts. The GPIO each signal goes to doesn't change.

## The wiring, in the YAML you actually flash

```yaml
external_components:
  - source: github://kylehase/ESPHome-ST7305-RLCD
    components: [st7305_rlcd]

spi:
  clk_pin: GPIO4
  mosi_pin: GPIO5

display:
  - platform: st7305_rlcd
    model: WAVESHARE_400X300
    id: wall_display
    width: 400
    height: 300
    cs_pin: GPIO6
    dc_pin: GPIO7
    reset_pin: GPIO10
    data_rate: 1MHz
    update_interval: 60s
    show_test_card: true
    auto_clear_enabled: false
```

One thing to know before you flash. ESPHome's native `st7305` platform covers the ST7305 chip, and the cheap panel is an ST7306. The community component above handles both, and the `WAVESHARE_400X300` model carries the verified init sequence and address window, so there are no register bytes for you to guess.

And the dashboard is just a lambda:

```cpp
// White paper, black ink. That is the whole aesthetic.
it.fill(Color::WHITE);
it.print(12, 6, id(font_title), Color::BLACK, "BUDDY");

char timebuf[16];
strftime(timebuf, sizeof(timebuf), "%H:%M", id(clock).now());
it.print(14, 54, id(font_clock), Color::BLACK, timebuf);
```

Big type, few items. A face in a 400×300 panel is about 80×100 pixels, which is recognisable rather than admiring.

## Three tests that decide whether this works

- **Does the glass work?** Flash with `show_test_card: true`. Get a test card and you know the panel, the SPI bus, the init sequence and the power rails are all right.
- **Does the image survive the microcontroller sleeping?** Set `update_interval: never`, add a deep sleep, render one frame, and watch the panel. The picture must stay.
- **Does the image survive power-off?** Unplug the USB. The picture must vanish.

The deep sleep is four lines:

```yaml
esphome:
  on_boot:
    priority: -100
    then:
      - deep_sleep:
          id: bench_sleep
          duration: 10min
```

The third test is the interesting one, and it's the honest core of this post. The datasheet says the answer is no — the panel's VCC has to stay alive — but a build that changes the power design deserves one afternoon of verification rather than a paragraph of reasoning. If the picture doesn't vanish, the panel is more bistable than I think it is, and the battery question comes back on the table.

## What it costs to run, and what it doesn't

Take €0.35 per kWh and a 5 V rail, and your display's running cost falls out in two lines.

Always-on, Wi-Fi associated, refreshing every 60 seconds: roughly 80 mA, which works out to about €1.23 a year.

Deep sleep between refreshes: 2–4 mA, which works out to somewhere between €0.03 and €0.06 a year.

That's around 27× less. The microcontroller is the easy half of that story — the ESP32 goes from 80 mA to 10 µA on its own — but the device never gets anywhere near it, because the floor is set by the panel's low-power current and the regulator's quiescent current, not by the chip.

Either way the electricity is a rounding error, and that's the point. Your twenty-euro device should cost about a euro a year to run, not a hundred. The reasons to deep sleep aren't on the electricity bill at all: an always-hot ESP32 sealed inside a picture frame is a reliability problem, and transmitting every ten minutes instead of every sixty seconds is kinder to everyone else's Wi-Fi.

## Why there's no battery in this build

Cut the power and the picture dies. So a battery build must never fully discharge the cell, which means a boost converter, a capacity-based cutoff, and a lithium cell that never actually gets used up.

That's strictly worse than e-paper, where you can cut power completely and the image stays.

Meanwhile the display hangs on a wall, and there's an outlet behind it. USB power. Skip the cell, skip the charger, skip the boost circuit, skip the lithium fire risk, and skip the ten-odd dollars the wall board charges for a battery holder you won't use.

## The one number I still don't have

The panel's low-power current. Everything above depends on it and I don't have it yet.

The datasheet lists IVCC ≤ 30 µA for the logic rail and leaves the panel supply blank, which tells you nothing useful. So measure it: put a 10 Ω shunt in series with the panel's VCC, run the panel in low-power mode off a bench supply, and read the millivolts across it. Three numbers, one afternoon.

If your measurement comes back high, the fix isn't a bigger battery. It's a longer sleep interval.

## Five things on the screen, and the phone does the rest

The panel has no touch screen and I'm not adding one. It stays read-only, and the phone does the tapping.

So your wall gets: the date, the weather from Open-Meteo (no API key, no account, no cost), the indoor temperature, the next medication reminder, and a QR code that opens the Buddy app on your phone. A second page holds a family photo, dithered to 1-bit with the [Photo Dither](/tools/photo-dither.html) tool I built for exactly this. A third page holds the home automation states.

One warning, and it's the same one from the plan: with no backlight the panel is invisible in an unlit room. It goes in a lit hallway. If your parent's room is dark at eleven at night, this is the wrong project, and I'd rather tell you now than have you hang a blank rectangle on the wall.

## Part 2 is a wiring change, not a rewrite

The spike proves the glass on a dollar microcontroller. Part 2 moves the identical software onto your wall board — the Waveshare ESP32-S3, which has the RTC, the temperature sensor and the frame hardware already on it. The display block, the fonts and the dashboard are byte-identical between the two stages. Only the SPI pins, the control pins and the MCU change. If the spike works, Part 2 is a wiring change.

After that, the series gets bigger: a 13.3" canvas, the full-colour E6 board in a wooden frame, and the $1,799 professional signage option, so you know what you're not paying. And eventually the zero-euro version — a dead e-reader with a failed frontlight, which works as a reflective mono panel if you can stop it going completely blank.

The [cloud cost post](/sysadmin/2026-11-19-cloud-cost-optimization-how-to-cut-your-aws-and-azure-bill/) is the reason none of this sits behind a subscription, and [my ESP32 weather station](/sysadmin/2026-11-17-esp32-weather-station-3-2-lcd-what-broke/) is what happens when a display doesn't cooperate.

{{< aff-disclosure-inline >}}

**Related:** [I'm Building a Hallway Display for My Parents](/meta/hallway-display-for-my-parents-the-idea/) — the plan this post prices up · [Photo Dither](/tools/photo-dither.html) — the dithering tool for the photo page

*Which of the five would you put on the wall first: today's date, the weather, or the family photo?*
