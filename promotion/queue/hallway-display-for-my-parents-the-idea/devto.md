---
title: "I'm Building a Hallway Display for My Parents \u2014 It Costs Less to Run Than the Light Bulb Above It"
canonical_url: https://pragmaticsysadmin.help/meta/hallway-display-for-my-parents-the-idea/
tags: sysadmin
---

When my dad's phone became unusable, the answer everyone gives you is a tablet. Big screen, big buttons, simple. And it works.

But here's what a tablet actually is, mounted on a hallway wall:

- A rectangle of light that pulls your eye whether you want it to or not
- A wallpaper nobody chose, glowing in a dark hallway at 11pm
- Something that buzzes when a stranger sends a WhatsApp
- Something that needs charging, and doesn't work when it isn't
- €150 and a sheet of glass that breaks
- And — this is the actual problem — **an interactive device**, for a person whose problem is that interactive devices got hard

None of those are why tablets fail. Tablets fail because of what they *are*: a second computer, asking for attention.

But the thing that has always worked for this is the **fridge door**. A printed notice. The date. The weather. What the doctor said. *Call your son back.* Nobody charges it. Nobody has to learn it. Nobody can accidentally swipe it into a shopping app at 2am. It's just there.

So the question I keep coming back to:

> What if the fridge door was alive?

Not alive in the "smart home" way. Alive in the way that it knows today's date, the weather outside, and what is next on the medication list.

## The idea, in one line

**The phone is the input device. The wall display is the output.**

You already own the phone. Your parents already have it, or they will. You do **not** need to give them a second interactive thing to learn and maintain. You need a passive surface that shows the five things that matter, in type big enough to read from the doorway, that nobody can accidentally break.

The panel has no touch screen, and I don't want one. The phone in your pocket is a better touchscreen than any 4-inch panel ever will be — it just has to be *invited*. So the wall display carries a QR code, and scanning it opens [Buddy](https://pragmaticsysadmin.help/buddy/), the free companion app I built for my dad: contact photos you can tap to call, medication reminders, safety information. Seven languages, no account needed.

The wall is a shortcut. The phone does the work.

## Why one bit, and why that's the feature

I went through the obvious options honestly.

| Option | What I checked | The problem |
|---|---|---|
| 7" IPS LCD + ESP32 | $32–42 for the boards I priced | Backlight. Glare at night. 200–500 mA. It looks like a TV. |
| 7.5" E Ink | $45–48 (Waveshare), €56 for the TRMNL DIY kit | Every update flashes black and white for ~2 seconds. On a wall in a living room, that is a strobe. |
| A tablet | €150–250 for a basic 10" | Notifications, charging, breakable glass, and still interactive. |
| **4.2" reflective TFT, 1-bit** | **$10.83** | No backlight. No flash. Silent. |

The last one is the panel I want. It's *reflective* — it makes its image out of the light already in the room, the way paper does. No backlight means no glare at night and no power burned on a lamp you don't need.

**The thing that surprised me:** I expected 1-bit to be a compromise. It's the opposite. For a screen you're reading from three metres away, black ink on paper-white is the highest-contrast, most legible thing you can possibly show. Colour would be noise. A dashboard would be noise. You want the date in 48-point type and nothing else competing with it.

For this use case, one bit isn't a limitation. It's the whole design.

## The prices (I checked, and there are traps)

The headline price you'll find for a 4.2" reflective TFT panel is **$2.56**. Great number. Misleading number.

- It's **MOQ 5**. Minimum spend is **$12.80** — for five panels.
- Good Display sells **one** for **$10.83**. If you need one panel, and this project needs one, the "cheap" one costs *more* in total.
- The microcontroller: ESP32-C3 SuperMini, **$1.09**.
- The FPC-to-header adapter: **$1.09–3.25**. The 24-pin FFC ribbon: **~$1–3**.

So the honest Stage 0 total is **$20–27**, not $12. The panel plus the microcontroller is **$11.92**; the adapter, the ribbon, a breadboard and a USB cable are the bits I hadn't budgeted for.

There's an escape hatch for people who don't want to solder: the **Waveshare ESP32-S3-RLCD-4.2** board at **€34.44** (openelab.io, EU warehouse, VAT included) comes with the 4.2" panel, an ESP32-S3 with 16 MB of flash and 8 MB of PSRAM, an RTC, a temperature and humidity sensor, a battery holder, a speaker, and acrylic stands. €34.44 for all of that is the better deal the moment you stop wanting a breadboard.

## The part that surprised me (and it's the good part)

I assumed this would behave like e-paper: draw it, cut the power, image stays. **It doesn't.**

The Sitronix ST7305 is a TFT-backplane controller, not memory-in-pixel. It has a low-power mode where the panel refreshes *itself* at 1 Hz. So the image survives the microcontroller going to sleep. **But it dies the moment the power goes.** The panel's VCC has to stay alive, always.

That sounds like a limitation and it's actually a gift, because it settles the power question completely.

**The arithmetic** (5 V rail, €0.35/kWh):

| Mode | Average draw | Per year |
|---|---|---|
| Wi-Fi associated all day, refreshing every 60 s | ~80 mA | 3.5 kWh ≈ **€1.23** |
| Deep sleep 10 min between refreshes | ~2–4 mA | 0.09–0.18 kWh ≈ **€0.03–0.06** |

Roughly **27× less electricity**. The ESP32 chip on its own would go from 80 mA to 10 µA — 8000× — but the device as a whole can't get near that, because **the floor is set by the panel's low-power current and the regulator's quiescent current, not by the microcontroller.**

And the money is trivial either way, which is the actual point. A twenty-euro device should cost about a euro a year to run, not a hundred. The reasons to deep sleep aren't on the electricity bill at all:

- **Heat.** An always-hot ESP32 sealed inside a picture frame on a wall is a reliability problem.
- **Battery viability.** Deep sleep is what makes the cordless option possible at all. Hours become weeks.
- **Radio hygiene.** Transmitting every 10 minutes instead of every 60 seconds is kinder to the spectrum.

And because the image dies with the power, **there is no point in a battery here.** E Ink can be switched off completely; this can't. A battery would buy you nothing and add a lithium cell to someone's hallway wall. Skip it. USB power, cable behind the frame, done.

## What it shows

Five things. That's the whole feature list.

- **The date and time** — 48-point type. The thing you actually glance at.
- **The weather** — from Open-Meteo. No API key, no account, no cost. The free tier allows 10,000 calls a day for non-commercial use; this thing makes 144 a day, and attribution is required.
- **Inside temperature** — the board has a sensor on it. Free.
- **The next medication reminder** — pulled from Home Assistant.
- **A QR code to Buddy** — because the panel can't be touched, the phone does that job.

Then a second page with a family photo, dithered to black and white. Which brings me to something I built this week.

## The photo problem, and a tool for it

A colour photo on a 1-bit screen doesn't work. Threshold it and a face becomes a black blob. You need error diffusion — dithering — so the mid-tones survive as texture instead of turning to mud.

I built **[Photo Dither](https://pragmaticsysadmin.help/tools/photo-dither.html)** to do exactly that: drop in a photo, pick the panel size, choose between Floyd–Steinberg, Atkinson, Jarvis-Judice-Ninke and Bayer, and export a **true 1-bit PNG** — bit depth 1, greyscale — that the ESP32 can display directly. It also emits an 8-bit greyscale version, because that's the safer format for ESPHome's image decoder.

It runs entirely in your browser. Your family's photos never touch a server, which for this use case is the entire point.

Be realistic about the resolution though: on a 400 × 300 panel, a face in a group photo is maybe 80 × 100 pixels. That's "recognisable", not "admiring". It is genuinely not a photo frame, and pretending otherwise would be dishonest.

## Where this goes

I have a plan, and it escalates:

1. **The prototype** — $10.83 panel, $1.09 microcontroller, breadboard, no case. Does it even work?
2. **The wall mount** — the same code on the €31 board, in a frame, with sensors.
3. **What colour costs** — the honest price of a real photo frame, and why 3-colour E Ink isn't one.
4. **The canvas** — 13.3", because if you're going to hang it, hang it big.
5. **The endgame** — the €1,799 professional digital signage option, so you know what you're *not* paying.
6. **The €0 version** — a dead e-reader, resurrected.

## The honest limitations

- **No backlight.** In an unlit room at 11pm it is a blank rectangle. This is a lit-room device. If your parent's room is dark at night, this is the wrong project.
- **400 × 300.** Five things, big. Not a dashboard.
- **It's a build.** The panel arrives on a 24-pin 0.5 mm FPC connector and needs an adapter board. If the contact side of your ribbon doesn't match the socket, you get an expensive sheet of glass and no error message. I've ordered the parts; I'll report exactly what happened, including the parts I got wrong.
- **The driver is one commit away from working.** ESPHome's native `st7305` platform lands in 2026.11.0; today it runs through a community component. Both work, but it's not a first-party component yet.

## Why it's worth the effort

Because the tablet is the wrong *shape* of answer. It assumes the problem is "they need a better interface". It isn't. The problem is that a fridge notice never needs charging, never needs updating, never asks for a password, and never tempts anyone into a shopping app.

A good screen should ask the same. And the cheapest screen that asks nothing is one that costs twenty-something euros, doesn't flash when it updates, and shows five things in type you can read from the doorway.

That's the idea. Parts are on the way — I'll write up the build when they land.

---

**Related:** [Why I Built Buddy](https://pragmaticsysadmin.help/meta/why-i-built-buddy-free-app-dad-sick/) · [Essential Home Automation for Older Parents](https://pragmaticsysadmin.help/senior-tech/essential-home-automation-older-parents-practical-setup-guide/) · [Photo Dither](https://pragmaticsysadmin.help/tools/photo-dither.html)
