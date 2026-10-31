---
title: "Give Old Tech a Second Life: Building a Low-Power Smart Display with ESP32 and E-Paper"
canonical_url: https://pragmaticsysadmin.help/sysadmin/2026-10-30-give-old-tech-second-life-low-power-smart-display-esp32-epaper/
tags: sysadmin
---

Every sysadmin has a drawer.

Mine currently holds: an old Android tablet with a cracked digitizer, two Raspberry Pi 3Bs that are too slow for anything I'd deploy today, a pile of ESP8266 boards from 2019, a box of 7-segment displays, and — somewhere at the bottom — a laptop LCD panel I pulled out of a ThinkPad that died.

None of it will ever run a modern app. All of it is perfectly capable of running something *useful*.

This series is about giving that drawer a purpose. Not a nostalgia project — a practical one. We're building a **wall-mounted smart display**: photo frame when idle, weather dashboard on demand, and it runs for months on a single battery because it spends 99.9% of its life asleep.

<!--more-->

## The Goal

Let's be specific, because vague DIY projects die in week two.

**What we're building:**
- A framed display on the wall, powered by a USB cable or a single 18650 cell
- Shows a rotating photo (or a family photo carousel) when idle
- Tap it → shows current weather, forecast, and the date
- Tap again → back to photos
- Wi-Fi for data, battery for life
- No cloud account, no app, no subscription

**What we're *not* building:** a general-purpose dashboard with 30 widgets, a touch UI framework, or anything that needs a phone app. The whole point is that it works when nobody's thinking about it.

**Why this is worth doing:** it's the cheapest possible home dashboard. No tablet, no screen, no HDMI, no account. And it solves a real problem — the tablet that "does nothing" but you keep meaning to set up.

---

## Three Paths to a Low-Power Smart Display

There are three honest ways to get there. Each trades off screen quality, complexity, and how long the battery lasts.

### Path A — ESP32 + E-Paper (the one we're building)

**How it works:** E-Ink displays only draw power when the image *changes*. Hold a static image and the panel draws essentially zero current. Pair that with an ESP32 in deep sleep and the whole thing sips power in microamps.

**The build (verified prices, checked October 2026):**
- ESP32-C3 SuperMini — **$1.09** (~$1.20 on a 5-pack deal)
- Waveshare 4.2" E-Paper (G), 400×300, 4-colour — **$18.99–28.99**
- Waveshare 7.5" E-Paper (B), 800×480, 3-colour — **$45.27–47.99**
- TTP223 capacitive touch module — **$0.99–1.48**
- 18650 cell (2600mAh) — **$5–8** · 2-cell holder — **$1**
- USB 18650 charger (1-slot) — **$3.79–5.06**

**Realistic battery life:** 4–6 weeks on a single 2600–3500mAh 18650, refreshing every 15 minutes. Once a day: over a year.

**Vibe:** Looks like printed paper. Zero glare, no backlight, completely invisible at night. In a hallway it reads as a framed photo, not a computer.

**Verdict:** ✅ This is the one. Best power characteristics by a wide margin, cheapest parts, and no cloud dependency.

---

### Path B — Old Tablet + ESP32 Wake Controller

**How it works:** Keep the original tablet — it's a real touchscreen with a good panel — but add an ESP32 that handles presence detection and wakes the tablet via a local API or a capacitive sensor wired to the power button. The tablet sleeps; the ESP32 stays awake on a tiny budget and only powers the tablet when someone walks past.

**The build:**
- Old Android tablet (free — it's in your drawer)
- ESP32-C3 SuperMini ($1.09) + TTP223 ($1)
- A relay or transistor to cut the tablet's power rail ($1)
- ADB-over-Wi-Fi for the wake command (no root required)

**Realistic battery life:** The tablet dominates. A 2016-era tablet idling might pull 300–600mA. If it sleeps properly, a 10,000mAh USB power bank gives you 16–30 hours of *awake* time, or weeks if it's mostly asleep and the ESP32 handles wake.

**Vibe:** Colour, touch, full Android. Heavier, hungrier, and you're fighting Android's doze mode, background services, and "optimising" apps that kill your wake commands.

**Verdict:** ⚠️ Great if you want colour and interactivity, and you already own the tablet. Painful if you're buying one.

---

### Path C — Salvaged LCD Panel + Driver Board

**How it works:** Pull the panel out of a dead laptop, buy a cheap driver board (usually an HDMI controller board for $15–25), and drive it with an ESP32 or Raspberry Pi. Add a MOSFET on the backlight's power rail so you can kill the backlight entirely when idle — which is the only way a salvaged LCD becomes low-power.

**The build:**
- Dead laptop or monitor (free)
- HDMI driver board ($15–25)
- ESP32-C3 ($1.09) or Pi ($35–60)
- MOSFET + resistor for backlight control (~$1)
- A panel that physically fits your frame

**Realistic battery life:** Worse than Path A, better than Path B. The panel itself draws some current, and the driver board adds its own. With backlight switching you can get it low enough to matter, but it's a chore.

**Vibe:** The most "proper" build. Genuinely satisfying, and the display quality is usually excellent. Highest risk of the three — you can ruin a panel.

**Verdict:** ⚠️ For the tinkerer who already has dead hardware and wants the project to be about the build, not the result.

---

### The Price Reality Check

I originally wrote this post from memory and got the prices wrong in both directions. The microcontroller is far cheaper than I thought; the display is far more expensive. Here's what I actually found when I went and looked (checked late October 2026, USD as listed by the sellers):

**Microcontroller / board**

| Item | Price | Notes |
|---|---|---|
| ESP32-C3 SuperMini | **$1.09** | The sweet spot. 4MB flash, 160MHz RISC-V, Wi-Fi + BLE |
| ESP32-C6 SuperMini | ~$0.33–1.09 | Newer, Wi-Fi 6, sometimes cheaper still |
| ESP32-C3 SuperMini (5-pack) | $1.09–1.27 each | Buy in bulk, same price basically |
| ESP32-S3 1.54" e-Paper AIoT board | **$17.99–18.99** | ESP32-S3 + 1.54" 4-colour e-paper, all in one |
| ESP32-C6 1.54" e-Paper AIoT board | $16.99–17.99 | Same, with Wi-Fi 6 |
| ESP32-S3 2.9" e-Paper dev board (LR1121) | $25.99 | 296×128, battery management built in |
| ESP32-S3 3.97" e-Paper dev board | $34.99–47.99 | 800×480, onboard microphone |
| Universal e-Paper ESP32 driver board | $14.19–14.99 | For raw panels — power, connector, ESP32 in one |

**Displays**

| Item | Price | Notes |
|---|---|---|
| 1.54" E-Paper (E), full colour | $7.49–12.49 | Tiny, 240×240 |
| 2.15" E-Paper (B) | $5.99–13.99 | 296×160 |
| 3.52" E-Paper (B) | $11.99–19.99 | 360×240 |
| 4.2" E-Paper raw, B/W | $14.63–15.99 | 400×300 — **best value for a first build** |
| 4.2" E-Paper (G), 4-colour | $18.99–28.99 | 400×300, red/yellow/black/white |
| 4.26" E-Paper (G) | $22.99–31.99 | 800×480 — bigger than you'd expect |
| 7.5" E-Paper (B) raw | $45.27–47.99 | 800×480, 3-colour |
| 7.5" E-Paper (H) | $47.99–56.99 | 800×480, 4-colour |
| 7.5" E-Paper HAT (B) + driver board | $50.91–54.99 | Pi-shaped, but works with anything over SPI |
| 7.3" E6 full-colour + solid wood photo frame | $72.99–143.99 | Already framed — see "just buy it" below |
| **ESP32-S3-PhotoPainter 7.3"** | **$82.99–83.99** | Wood frame + ESP32-S3 + full-colour e-paper, battery optional |

**Touch & power**

| Item | Price |
|---|---|
| TTP223 capacitive touch module | $0.99–1.48 (10-pack: $6.12) |
| 18650 cell, 2600mAh | $5.07–8.48 |
| 18650 cell, 3500mAh | $10.84–15.63 |
| 2-cell 18650 holder with leads | $0.99–1.19 |
| 3×AAA to 18650 adapter | $0.63–1.09 |
| 1-slot USB 18650 charger | $3.79–5.06 |
| 4-slot LCD charger | $19.79 |

**Buying in Europe:** Amazon adds 19–25% VAT. The 7.5" HAT V2 lists at €78.99 on Amazon.ie, and the raw 7.5" panel at 723.99 SEK (~€62) on Amazon.se — both noticeably worse than buying direct from Waveshare or AliExpress and paying import VAT once.

**AliExpress is consistently cheaper than the Waveshare store** for the same panels. The 7.5" (B) raw display is $45–48 official but $55–58 on AliExpress — actually *worse* there, so check both. The 4.2" range is where AliExpress wins clearly ($23–33 vs $27–39).

### Three Realistic Builds

**Budget / learning build — ~$21**
```
ESP32-C3 SuperMini                        $1.09
4.2" E-Paper raw (B/W), 400×300           $14.63
TTP223 touch module                       $1.00
2-cell 18650 holder + 2 cells             $13.00
                                          ────────
                                          ~$29.72
```
With the display and ESP32, no touch, USB power: **~$16**

**Proper 4-colour build — ~$31**
```
ESP32-C3 SuperMini                        $1.09
4.2" E-Paper (G) 4-colour                 $22.99
TTP223 touch module                       $1.00
18650 holder + cell + charger             $10.00
                                          ────────
                                          ~$35
```

**Full-size photo frame build — ~$48**
```
ESP32-C3 SuperMini                        $1.09
7.5" E-Paper (B) raw, 800×480             $47.99
TTP223 touch module                       $1.00
                                          ────────
                                          ~$50
```

**Or just buy the finished thing — ~$83**
The ESP32-S3-PhotoPainter is a 7.3" full-colour E-Ink display in a solid wood photo frame with the ESP32-S3 built in, battery optional, ultra-long standby. It's exactly this project, pre-built, with a phone app for pushing images.

Read that last option carefully, because it's the actual answer for most people. Building it yourself is the fun part. But if you want a working wall display this weekend, **$83 and an afternoon is better than $50 and a fortnight.**

---

### Comparison at a glance

| | Path A: ESP32 + E-Paper | Path B: Old Tablet | Path C: Salvaged LCD |
|---|---|---|---|
| **Total cost** | $16–50 | $0–15 (own the tablet) | $16–90 |
| **Battery life** | 2.5–4 months | Weeks | 1–3 weeks |
| **Idle power** | ~10 µA | ~300 mA (asleep, optimistically) | ~50–200 mA |
| **Colour** | Monochrome (or 3-colour) | Full | Full |
| **Touch** | Add-on module | Native | Usually none |
| **Setup difficulty** | Medium | Medium-Hard | Hard |
| **Cloud required** | No | No | No |
| **Survives a power cut** | Yes (restores) | Yes | Yes |

---

## The Architecture: Click-to-Wake

This is the core idea that makes it work, and it comes down to four decisions.

### 1. Deep Sleep as the default state

The device spends essentially all its life in deep sleep. Not idle. Not "waiting on a timer." Actually asleep, with the CPU halted and the radio off.

For an ESP32-C3, deep sleep current is around **5 µA**. For the original ESP32, around **10 µA**. A naive always-on ESP32 running a web server pulls 80–120 mA. That's a **20,000× difference** — the whole project is built on this.

In ESPHome, this is a single block:

```yaml
esp32:
  board: esp32-c3-devkitm-1
  framework:
    type: arduino

deep_sleep:
  id: deep_sleep_1
  duration: 15min
  run_duration: 30s
  wakeup_pin: GPIO4      # the touch module's signal line
```

`run_duration: 30s` means: wake up, do your thing, then go back to sleep after 30 seconds no matter what. That's your safety net — if the code hangs, it still re-sleeps.

### 2. Capacitive touch as the wake trigger

A **TTP223** module is a $1 capacitive touch sensor that sits behind the frame's glass or acrylic and outputs a high/low signal. Touch the front of the frame, GPIO4 goes high, the ESP32 wakes.

It doesn't need to see a finger through anything — it works through 3–5mm of glass or acrylic. That's the trick that makes the whole thing look like a normal photo frame.

**One gotcha:** the ESP32's *built-in* capacitive touch pins are only on the original ESP32, and they're deprecated on newer chips. Don't plan around them — use a TTP223 (or the TTP229) as a discrete module. It's a euro.

Another gotcha: mount the TTP223 so it's *behind* the display but in front of the frame backing, and keep the sensor away from the E-Ink panel itself, which can produce false triggers when it refreshes.

### 3. Fetch the smallest possible payload

On wake, the ESP32 needs three things: the current temperature, the weather condition, and the current date. That's it.

**Open-Meteo** gives you all of that for free, with no API key, no account, and no rate limit that matters for this:

```
https://api.open-meteo.com/v1/forecast
  ?latitude=60.1699
  &longitude=24.9384
  &current=temperature_2m,weather_code
  &timezone=auto
```

That returns a small JSON. A few hundred bytes. The ESP32 parses it, renders a bitmap, pushes it to the E-Paper, and goes back to sleep.

**Why Open-Meteo and not the big weather APIs:**
- No API key to manage or leak
- No account to create
- Free, and they ask you to self-host it if you care about scale
- It returns exactly what you need and nothing else
- It's a European project with genuinely good coverage in Finland

For photos, the model is different: you don't fetch them over Wi-Fi every wake. You **pre-render** them. Convert each photo to a 1-bit or 4-colour bitmap at exactly the panel's resolution, store them in the ESP32's flash (or on a microSD card), and the ESP32 just swaps between pre-rendered buffers. No image processing on an ESP32. None. It can't.

That's the trick that makes a photo frame possible on a microcontroller. A server does the hard work once, offline. The ESP32 does a memcpy.

### 4. Render once, then hold

E-Ink refreshes are slow (2–10 seconds depending on panel) and flash as they update, but they consume power only during the refresh. Between refreshes: near zero.

That means your update interval is a **design decision, not a technical limit**:
- Every 15 minutes → 4–6 weeks on one cell
- Every hour → 3–4 months on one cell, or plug in a USB power bank and never think about it
- Once a day → over a year

My recommendation for the wall: **refresh every 30 minutes when awake, and refresh the photo once a day.** The weather doesn't need to be live to the minute. The photo doesn't need to change at all.

---

## The Battery Maths (Honest Numbers)

Let's do the actual calculation, because the marketing numbers are usually nonsense.

**Assumptions:**
- 18650 cell, 3000 mAh
- Wake every 15 minutes
- Active time per cycle: 30 seconds (Wi-Fi connect + fetch + render + e-paper refresh)
- Average current while active: 100 mA (Wi-Fi dominates)

**Per cycle:**
```
30 s × 100 mA = 3,000 mA·s = 0.83 mAh per cycle
```

**Per day (96 cycles):**
```
0.83 mAh × 96 = 79.7 mAh/day
```

**Battery life:**
```
3,000 mAh ÷ 79.7 mAh/day = 37.6 days ≈ 5 weeks
```

Add deep sleep current (~5 µA average) and you're at roughly **5 weeks** for 15-minute updates.

**Now change one variable:**
- Hourly updates (24 cycles/day) → **~5 months**
- Daily updates (1 cycle/day) → **over 3 years**

**Now add real-world derating:**
- E-Paper panels lose contrast over time and need a full refresh cycle (flash to white, then redraw) every few weeks — that costs more power
- Lithium cells lose capacity in cold rooms — expect 20–30% less in a cold hallway
- Real capacity of a 3000 mAh cell is more like 2800 mAh
- Wi-Fi association takes longer to connect than you think when the router is asleep too

**Honest estimate: 4–6 weeks on a single 18650 with 15-minute updates. 3–4 months with hourly updates.**

If you want it to live forever, use a 10,000mAh USB power bank ($10–20) plugged into the wall. The battery math becomes irrelevant.

---

## What Part 2 Covers

In the next installment, I'll build this on a breadboard and measure it:

- **The actual parts list** with links and current prices — re-verified at the time of writing, not from memory
- **Breadboard prototype** — ESP32-C3, TTP223, and a 4.2" Waveshare E-Paper
- **Real current measurements** with a multimeter: deep sleep, Wi-Fi active, E-Paper refresh, and full cycle average
- **The 18650 power circuit** — boost converter to 3.3V, proper battery management, and why you should *not* run a Li-ion cell directly into the ESP32's regulator
- **Rendering a photo to the right bitmap format** — the part that's actually hard
- **Weather code → icon mapping** for the E-Paper's limited palette
- **Enclosure** — making it look like a real frame, including where to hide the touch sensor

**Part 3** will cover the solar option: a small panel + charge controller + the panel duty-cycling, for a display that genuinely never needs a wire.

---

## A Note on E-Waste

There's a reason this project is worth the effort beyond the dopamine of a blinking e-ink screen.

The tablet in my drawer isn't harmful sitting there. But the *instinct* to bin old hardware — and the ease of it, since it's just a drawer — means functional electronics get thrown away while still perfectly capable of running a 40-byte weather API call.

E-Ink panels are cheap by the standards of displays: a 4.2" four-colour panel is $19–29, a 7.5" three-colour panel is $45–48. They're made from the overproduction of display factories, which is why the panels that a year ago were €60 have fallen so far. The ESP32-C3 costs **$1.09**. A $16 build — display, microcontroller, power — that draws 5 µA while asleep and does one job properly.

That's a decent trade for something the tablet it replaces can't do at all: run for months without a cable.

---

## A Correction Worth Making Public

I wrote the first draft of this post from memory. When I went back and actually checked the prices, I had them wrong in both directions:

- I said the 7.5" e-Paper was €25–30. It's **$45–48** (€43–55) — I was off by nearly 2×
- I said the ESP32-C3 SuperMini was €3–4. It's **$1.09** — I was over by 3×

And I missed the best option entirely: the **ESP32-S3-PhotoPainter**, a 7.3" full-colour E-Ink display in a solid wood photo frame with the microcontroller built in, for $83. That's the finished product this post describes, and it's cheaper than building a 7.5" panel yourself once you add the driver board, the touch sensor, the enclosure, and your time.

I've left the corrected prices in the tables above with the date I checked them. Prices on AliExpress and Waveshare move constantly — check before you order, and treat every number here as a starting point rather than a quote.

The lesson is the same one this whole series is about: **don't trust the number in your head, go and look at it.** I write it in a hardware post, I write it in a sysadmin post, and I write it on the house log next to the boiler.

---

*Got a drawer full of forgotten tech? What's in yours? I'd genuinely like to know — [send me your strangest salvage idea](mailto:pragmatic@pragmaticsysadmin.help).*
