---
title: "ESP32 Weather Station: What Broke and Why I Switched to a Pi"
date: 2026-11-17
author: Pragmatic Sysadmin
description: "An ESP32, a 3.2-inch ILI9341 LCD, and a blank screen. The wiring was right and the code compiled - so what actually went wrong?"
tags: ["esp32", "ili9341", "waveshare", "lcd", "homelab", "weather-station", "honest-guide"]
categories: ["System administration"]
draft: false
showToc: true
topics: ["esp32", "lcd", "homelab"]
---

I wanted a small, always-on weather and photo dashboard for the kitchen. Something that shows temperature, humidity, and a rotating photo slideshow on a 3.2-inch screen. No cloud subscription, no phone app, just a box on the wall.

I bought a **Waveshare SpotPear 3.2" RPi LCD (V2)** — a 320×240 SPI display with an ILI9341 controller. It plugs directly into Raspberry Pi GPIO pins, so I assumed it would be straightforward.

It wasn't.

---

## The Plan

**Hardware:** ESP32 DevKit (ESP-WROOM-32)  
**Display:** Waveshare 3.2" RPi LCD (ILI9341, SPI)  
**Software:** Arduino IDE, TFT_eSPI (after LovyanGFX failed to compile)  
**Data:** Open-Meteo API for weather, local JPG photos via LittleFS or SD card

**Where to buy:**

- {{< aff merchant="ebay" text="ESP32 DevKit (ESP-WROOM-32)" url="https://www.ebay.com/sch/i.html?_nkw=esp32+devkit+esp-wroom-32+cp2102" >}} — the board this build used
- {{< aff merchant="newegg" text="Waveshare 3.2\" 320x240 SPI LCD (ILI9341)" url="https://www.newegg.com/p/pl?d=waveshare+3.2+inch+320x240+ili9341+spi+lcd" >}} — the exact display, ILI9341 controller, 40-pin RPi header

Prices move every week, so those links show today's price rather than me quoting one that is wrong by the time you read it.

The wiring is simple — eight jumper wires from the display's 40-pin RPi header to the ESP32:

| Display Pin | Function | ESP32 GPIO |
|-------------|----------|------------|
| Pin 1 | 3.3V | 3V3 |
| Pin 6 | GND | GND |
| Pin 19 | MOSI | GPIO 23 |
| Pin 21 | MISO | GPIO 19 |
| Pin 23 | SCLK | GPIO 18 |
| Pin 24 | CS / CE0 | GPIO 5 |
| Pin 22 | DC | GPIO 2 |
| Pin 18 | RST | GPIO 4 |

The header on these Waveshare displays isn't labeled, so counting from the corner with Pin 1 is essential. I verified the wiring twice before applying power.

---

## What Worked

- **Wiring:** All eight connections verified with a multimeter before power-up.
- **Compilation:** The TFT_eSPI test sketch compiles and uploads cleanly to the ESP32 Dev Module.
- **Serial output:** The ESP32 boots, prints `Käynnistetään TFT_eSPI...` (Starting TFT_eSPI...), and reaches `tft.init()` without crashing.
- **Backlight:** Power flows to the display; the backlight comes on.

In other words, the microcontroller is alive, the code runs, and the display receives power. But no pixels appear.

---

## What Didn't Work

### LovyanGFX (first attempt)

I started with LovyanGFX because it has built-in JPG support — important for the photo slideshow part. The code wouldn't compile:

```
expected unqualified-id before '<' token
```

A stray `<lvgl.h>` line without `#include` broke the file. After removing it, a second error appeared: `write_3byte_unaligned was not declared in this scope` — a library/ESP32 core version mismatch. I fixed both issues, but by then I'd already sunk an evening into library configuration.

### TFT_eSPI (second attempt)

Switched to TFT_eSPI. The `User_Setup.h` file ships configured for ESP8266 (NodeMCU pin numbers like `PIN_D6`, `PIN_D7`). I changed it to match my ESP32 wiring:

```cpp
#define TFT_MISO 19
#define TFT_MOSI 23
#define TFT_SCLK 18
#define TFT_CS    5   // Display Pin 24
#define TFT_DC    2   // Display Pin 22
#define TFT_RST   4   // Display Pin 18
#define SPI_FREQUENCY  16000000  // Lowered from 27 MHz for jumper-wire reliability
```

The sketch compiled, uploaded, and the Serial Monitor confirmed it reached `tft.init()`. Still, the screen remained blank or white.

---

## Current State: Code Runs, Screen Is Dead

Right now, this is where I am:

- ✅ ESP32 boots and runs
- ✅ TFT_eSPI initializes without errors
- ✅ Backlight is on
- ❌ No image, no text, no color bars on the LCD

The last suggestion I received was to enable two flags in `User_Setup.h`:

```cpp
#define RPI_DISPLAY_TYPE   // 20MHz maximum SPI
#define TFT_INVERSION_ON   // If colors are inverted / screen is white
```

I haven't tried those yet. But I've spent enough evenings on this.

---

## Why I'm Reverting to Raspberry Pi B

I have an old Raspberry Pi B sitting in a drawer. Here's why I'm going back to it for this project:

| Factor | ESP32 + SPI LCD | Raspberry Pi B |
|--------|----------------|----------------|
| Display interface | SPI, custom drivers, `User_Setup.h` | HDMI or composite, "just works" |
| Graphics | Framebuffer via ILI9341 init sequence | Standard Linux framebuffer `/dev/fb0` |
| Photos | JPG decode in C++, LittleFS/SD card | Python + Pillow, any image format |
| Weather API | ArduinoJson + HTTPClient | `requests` in Python, 5 lines |
| Debugging | Serial monitor guesswork | SSH, logs, X11/framebuffer |
| Time spent this week | ~6 hours, still broken | 0 hours, but it would boot |

The Raspberry Pi B is slower, draws more power, and is overkill for a weather display. But it runs a real operating system. I can write a Python script with Pygame or Pillow, pull weather from Open-Meteo with `requests`, and rotate photos on a 320×240 surface without fighting SPI initialization sequences at 11 PM.

**Honest cost math:** The ESP32 cost about €6. My time costs more than that per hour. If the Pi B gets this working in one evening, it's the cheaper option.

---

## The Real Lesson

The ESP32 is a fantastic microcontroller. For sensor nodes, Wi-Fi relays, and battery-powered devices, it's unbeatable. But driving a 320×240 color TFT with custom pin mappings and library version mismatches is not where it shines — not when you just want a screen that shows pictures and temperature.

I'll keep the ESP32 for something it's actually good at. The weather station is going on a Raspberry Pi B.

---

{{< aff-disclosure-inline >}}

*Have you driven an ILI9341 display from an ESP32 and actually gotten pixels to show? I'd like to know what I missed. [Email me](mailto:pragmatic@pragmaticsysadmin.help).*