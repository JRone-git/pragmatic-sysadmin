---
title: "Second Life, Part 1: The \u20ac30 Prototype"
canonical_url: https://pragmaticsysadmin.help/sysadmin/2026-10-30-second-life-part-1-the-30-prototype/
tags: sysadmin
---

I want a display on my wall. Not a screen — a *picture* on my wall that happens to be alive.

The spec, in order of priority:

1. Looks like a framed photo, not a monitor
2. Costs pennies to run
3. Never needs a subscription
4. Survives being unplugged without losing the picture
5. Costs less than I spent on dinner

Every homelab eventually grows a display-shaped hole. You've got the NAS, the sensors, the MQTT broker — and nothing to *show* for it. A Pi in a cupboard is a system. A Pi in a frame on the wall is a product.

This is Part 1 of six. I'm building it in **price order, ascending**, so each part teaches the next.

| Part | Title | Cost | What it teaches |
|---|---|---|---|
| **1** ← you are here | **The €30 Prototype** | ~€29 | Wake → fetch → render → sleep. Real current measurements. |
| [2](https://pragmaticsysadmin.help/series/second-life/) | The €56 Wall Mount | ~€45 | 7.5" panel, IKEA frame, ESPHome, 3 months on battery |
| [3](https://pragmaticsysadmin.help/series/second-life/) | What Colour Costs | ~€85 | 4-colour vs Spectra 6, and why photos on the wrong panel look awful |
| [4](https://pragmaticsysadmin.help/series/second-life/) | The Canvas | ~€254 | 13.3" E-Ink, tiled walls, a real e-ink monitor |
| [5](https://pragmaticsysadmin.help/series/second-life/) | The €1,799 Endgame | €1,799 | 43" reflective LCD signage, solar, professional economics |
| [6](https://pragmaticsysadmin.help/series/second-life/) | The €0 Version | €0 | A dead e-reader, reflashed. Full circle. |

<!--more-->

## Part 1 is a bench prototype, not a wall display

This is deliberate. Part 1 has exactly **one job**: prove the architecture works on my desk, with a multimeter, before I commit to a frame and a wall hole.

The architecture is four steps:

```
wake  →  fetch  →  render  →  sleep
```

Wake from deep sleep. Fetch a few hundred bytes of JSON. Draw it. Go back to sleep. That's it. Everything else in this series is detail.

I'm doing the 4.2" panel in Part 1 because it's cheap, it's the size I can prototype on, and **because it's the last size where I can afford to get it wrong.** Part 2 moves to 7.5" — the actual photo-frame size — once I know the power numbers.

One variable at a time. That's the whole discipline, and it's the same discipline the [When Code Meets Life](https://pragmaticsysadmin.help/sysadmin/when-code-meets-life-sysadmin-mindset-family-home-repairs/) post is about.

---

## The Bill of Materials

Prices checked late October 2026, in USD as listed by the sellers.

| Part | Price | Where |
|---|---|---|
| **Waveshare 4.2" e-Paper, 400×300, B/W** (SKU 13187) | **$14.63–15.99** | waveshare.com / AliExpress |
| **Waveshare e-Paper ESP32 Driver Board** (SKU 15823) | **$14.19–14.99** | waveshare.com |
| **TTP223 capacitive touch module** | $0.99–1.48 | AliExpress |
| Jumper wires + breadboard | ~$4–6 | anywhere |
| USB-C cable | ~$3 | anywhere |
| **Total** | **~$29 without touch, ~$30 with** | |

The driver board comes with a 24-pin FFC cable and a connector adapter, so the panel plugs straight in. **No soldering for this build.**

### Why these two and not something else

The panel needs two things most displays don't: a way to generate the high voltages the ink particles need, and a way to switch between image data and commands. That's the boost circuit and the DC line. The driver board has both, plus an ESP32 with every pin broken out, a USB-UART bridge, and an LED.

I'm using the **ESP32** (original, WROVER module) rather than an ESP32-C3 because the board is designed around it and the extra GPIO matters when you get to touch and buttons.

### ⚠️ The BS jumper — read this before you power it up

The driver board has a jumper block labelled `BS` that configures the boost circuit for your panel size. **Set it to `4.2inch` before you plug the panel in.**

From the schematic, the board supports 1.54" / 2.13" / 2.66" / 2.7" / 2.9" / 3.7" / 4.2" / 5.65" / 5.83" / 7.5" / 7.5" HD. Two adjacent resistor positions set `RESE` (0.47 Ω or 2.2 Ω) and `GDR`. Wrong jumper = wrong VCOM voltage = a panel that either doesn't work or degrades over time.

I would not have found this without reading the schematic. It is exactly the kind of thing that turns "I spent an evening on this" into "I spent two evenings and a dead panel."

---

## The Wiring

If you bought the driver board, this is the whole wiring diagram:

```
┌──────────────────────┐        FFC cable        ┌────────────────────┐
│  e-Paper ESP32       │◄───────────────────────►│  4.2" e-Paper      │
│  Driver Board        │        (24-pin FFC)      │  400×300 B/W       │
│                      │                          │                     │
│  USB-C ──► laptop    │                          │                     │
└──────────────────────┘                          └────────────────────┘
```

That's it. The panel's FFC goes into the driver board's socket (using the supplied adapter for the smaller connector), the board goes into USB, and you flash it.

For reference, the board's pin mapping is **fixed in hardware** — you don't wire anything yourself:

| e-Paper signal | ESP32 pin | Function |
|---|---|---|
| DIN | GPIO14 | SPI MOSI (data in) |
| SCLK | GPIO13 | SPI clock |
| CS | GPIO15 | Chip select, low active |
| DC | GPIO27 | Data/Command — low for command, high for data |
| RST | GPIO26 | Reset, low active |
| BUSY | GPIO25 | Output — high while the panel is refreshing |

Note the SPI quirk: the board puts **SCLK on 13 and MOSI on 14**, which is the *opposite* of the ESP32's default VSPI assignment. If you write raw Arduino you'll need `hspi.begin(13, 12, 14, 15)`. If you use ESPHome, you tell it the pins and it handles the mapping.

---

## The ESPHome Config

I'm using ESPHome rather than raw Arduino for one reason: **the deep-sleep-and-fetch loop is already written, tested, and maintained by other people.** Don't hand-roll what you don't need to.

```yaml
esphome:
  name: second-life
  friendly_name: Second Life

esp32:
  board: esp32dev
  framework:
    type: arduino

logger:

api:

ota:
  - platform: esphome
    password: !secret ota_password

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

# The driver board's SPI pins are fixed in hardware:
# SCLK=GPIO13, MOSI=GPIO14, CS=GPIO15, DC=GPIO27, RST=GPIO26, BUSY=GPIO25
spi:
  clk_pin: GPIO13
  mosi_pin: GPIO14
  miso_pin: GPIO12

output:
  - platform: ledc
    pin: GPIO2          # the on-board LED
    id: status_led
    light:
      - lambda: |-
          if (id(update_in_progress)) {
            auto level = (millis() % 1000) < 500 ? 1.0 : 0.0;
            if (level > 0) { ESP_LOGI("led", "update"); }
            return level;
          }
          return 0.0;

  # The e-Paper itself
  - platform: waveshare_epaper
    cs_pin: GPIO15
    dc_pin: GPIO27
    reset_pin: GPIO26
    busy_pin: GPIO25
    update_interval: never
    id: epaper_display

esp32_ble_tracker:

deep_sleep:
  id: deep_sleep_1
  duration: 30min       # how long between refreshes
  run_duration: 30s     # hard safety timeout — re-sleep even if code hangs
  # touch wake comes in Part 2; for now it's a timer

sensor:
  - platform: wifi_signal
    id: wifi_db
    update_interval: 60s

  - platform: template
    id: outside_temp
    unit_of_measurement: "°C"
    accuracy_decimals: 1
    update_interval: 30min
    lambda: |-
      return id(forecast_temp).state;

http_request:
  verify_ssl: true
  timeout: 15s
  url: "https://api.open-meteo.com/v1/forecast?latitude=60.17&longitude=24.94&current=temperature_2m,weather_code&timezone=auto"
  on_response:
    then:
      - lambda: |-
          // Minimal JSON scrape — the payload is small and flat.
          std::string body = id(http_response).get_body();
          // ... parse temperature_2m and weather_code ...
      - component.update: epaper_display
```

Three things in there matter more than the rest:

**1. `update_interval: never`** on the display. The panel doesn't refresh on a timer — it refreshes when I tell it to, after a fetch. Otherwise you get a full panel refresh (with its flash) every minute, which is both ugly and wasteful.

**2. `run_duration: 30s`** on deep sleep. This is the safety net. If the Wi-Fi connection hangs or the JSON parse throws, the ESP32 wakes up again 30 seconds later instead of sitting dead until someone unplugs it. I learned this from a build that hung on a captive portal and stayed dark for three days.

**3. Open-Meteo** instead of a big weather API. No API key to manage or leak, no account, free, and it returns exactly what I need:

```
https://api.open-meteo.com/v1/forecast?latitude=60.17&longitude=24.94&current=temperature_2m,weather_code&timezone=auto
```

That's a few hundred bytes. A phone-tethered version of the same request costs about the same in power. The API isn't the bottleneck — the Wi-Fi association is.

---

## The Measurements

This is the part that makes it a prototype rather than a guess. Five numbers, one multimeter:

| Measurement | What to expect | Why it matters |
|---|---|---|
| Deep sleep current | **5–10 µA** | This is the number the whole design rests on |
| Wi-Fi active (associated) | 80–150 mA | Dominates the wake cycle |
| Wi-Fi connect (transient) | 300–400 mA peak | Can brown out a weak supply |
| E-Paper refresh | 20–50 mA for 2–4 s | Short but not free |
| **Full cycle average** | **~1.4 mA** | The number that decides battery life |

I'll publish my actual measured figures in Part 2 rather than pretending I know them now. But the method:

1. **Deep sleep** — put the meter in series with the board's 5V input, meter on µA, and let it sit. The reading will drift for a minute as the meter settles. This is where you find out if something is keeping the radio warm.
2. **Wi-Fi active** — serial output logging `esp32.get_free_heap()` and the radio state is easier than fighting a meter's auto-ranging.
3. **Cycle average** — don't measure it directly. Compute it from the pieces and the duty cycle:
   ```
   30 s × 100 mA  =  3,000 mA·s   =  0.83 mAh per wake
   96 wakes/day    =  79.7 mAh/day
   ```
4. **Sanity-check with the meter** — set `duration` to 10 seconds, run for 10 minutes, and check the meter's total. It should land within 10% of the calculated figure.

If the measured cycle average comes out at 10× the calculated one, something is keeping the display awake. The most common cause: `update_interval` left at its default, so the panel refreshes constantly.

---

## The Battery Maths

Let me do the actual arithmetic, because the marketing numbers are usually nonsense.

**Assumptions:**
- 18650 cell, 3000 mAh
- Wake every 30 minutes
- Active time per cycle: 30 seconds (Wi-Fi connect + fetch + render + refresh)
- Average current while active: 100 mA

**Per cycle:**
```
30 s × 100 mA = 3,000 mA·s = 0.83 mAh per cycle
```

**Per day (48 cycles):**
```
0.83 mAh × 48 = 39.8 mAh/day
```

**Battery life:**
```
3,000 mAh ÷ 39.8 mAh/day = 75 days
```

Change one variable and it moves a lot:

| Refresh interval | Cycles/day | mAh/day | Battery life (3000 mAh) |
|---|---|---|---|
| Every 5 min | 288 | 239 | **12 days** |
| Every 30 min | 48 | 40 | **75 days** |
| Hourly | 24 | 20 | **150 days** |
| Every 6 hours | 4 | 3.3 | **2.3 years** |

**Now derate it, because reality is worse than arithmetic:**
- E-Paper panels need a periodic full refresh (flash to white, then redraw) or contrast fades. That's an expensive refresh.
- Lithium cells lose capacity in cold rooms — 20–30% less in a cold hallway
- A "3000 mAh" cell is really about 2800 mAh
- Wi-Fi association takes longer than you'd think, especially if the router is in power saving too

**Honest estimate: 6–8 weeks on a single 18650 at 30-minute refreshes. 3–4 months at hourly.**

The TRMNL kit's spec sheet claims 3 months on a 2000 mAh battery with a 6-hour refresh. That checks out against this table, which is a nice sanity check on the method.

**But here's the thing I keep forgetting: it's on a wall.** There's an outlet right behind it. USB power costs you €0.10/year in electricity and removes the entire battery-management problem — no cell, no holder, no charger, no boost circuit, no lithium fire risk in someone's hallway.

The battery is only interesting if there's no outlet. I'll decide that in Part 2.

---

## What Part 1 Proves (and What It Doesn't)

**Proves:**
- The wake → fetch → render → sleep loop works on a real panel
- The deep sleep current is what I think it is
- The BS jumper setting and pin mapping are correct
- I can pre-render a bitmap and push it to the panel

**Doesn't prove:**
- Touch (that's Part 2)
- That it looks good in a frame (Part 2)
- Anything about colour (Part 3)
- Whether a 13.3" panel is worth €254 (Part 4)

---

## Coming next: Part 2 — The €56 Wall Mount

Same architecture, bigger panel, and the first time it goes on an actual wall:

- **7.5" panel** — the TRMNL BYOD DIY Kit ($47.99 at Seeed, **€56.29 incl. VAT at openelab.io** with free German shipping over €50), or the 7.5" monochrome panel plus an ESP32-C3
- **An IKEA frame** (€6–8) instead of a 3D-printed enclosure
- **Touch** — the TTP223 behind the glass, waking on tap
- **Measured numbers** from the Part 1 prototype, finally real
- **The photo carousel** — pre-rendered bitmaps, because an ESP32 cannot decode a JPEG and anyone who tells you otherwise is wrong
- **3 months on battery** — or USB, if the outlet argument wins

---

*Part 1 is a €30 experiment on a kitchen table. If it works, it goes on the wall in Part 2. If it doesn't, I've lost €30 and learned something — which is still a better bet than buying a €83 photo frame and discovering I don't like e-paper.*

*Follow the series: [Second Life](https://pragmaticsysadmin.help/series/second-life/)*
