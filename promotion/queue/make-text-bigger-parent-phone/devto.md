---
title: "How to Make Text Bigger on an Elderly Parent's Phone"
canonical_url: https://pragmaticsysadmin.help/senior-tech/2026-11-09-make-text-bigger-parent-phone/
tags: seniors, accessibility, android, iphone
---

You are on the phone with your dad. He holds the screen out at arm's length, squints, and says the thing every child eventually hears: "I can't read that."

Here is what I know after setting this up on both sides of my family: the fix takes 5 minutes, it is free, and it is already on the phone. Nobody needs a new device. You just need the right settings, because the default is wrong for most people over 70.

<!--more-->

## The quick answer

| | iPhone | Android |
|---|---|---|
| Where it lives | Settings → Accessibility → Display & Text Size | Settings → Accessibility → Display size and text |
| The slider | Larger Text | Font size, up to 200% |
| Extra size | Turn on **Larger Accessibility Sizes** | The slider already goes to 200% |
| Also switch on | Bold Text, Increase Contrast | Bold text, high-contrast text |
| Magnify everything | Settings → Appearance → Display Zoom → Larger Text | Display size slider |

That last row is the one most people never find. It is a different setting and it fixes a different problem, so it gets its own section below.

## iPhone: four taps

**Settings → Accessibility → Display & Text Size → Larger Text.** Drag the slider until the sample sentence is comfortable to read, then turn on **Larger Accessibility Sizes** to unlock the steps beyond the normal maximum. Apple documents this path for iOS 26, and it is the same on iOS 18 and earlier.

While you are in that screen, turn on two more things:

- **Bold Text** — heavier strokes, less squinting, no downside.
- **Increase Contrast** — pushes the text further away from the background.

Then go back and set **Settings → Appearance → Display Zoom → Larger Text.** This is the part that people miss. Accessibility text size changes the *words*. Display Zoom magnifies the *entire screen* — icons, buttons, everything. If your parent is reading the words fine but cannot hit the right icon, this is the setting that fixes it.

> On iOS 27, Text Size, Bold Text and Display Zoom move out of Display & Brightness into a new **Appearance** section. If you cannot find them, search for "Text Size" in Settings.

## Android: the same idea, one menu over

**Settings → Accessibility → Display size and text.** You get a **Font size** slider that goes to 200%, a **Display size** slider for the icons and buttons, and switches for **Bold text** and, on Android 16 and up, **Outline text**. On Android 15 and below, use high-contrast text instead.

There is a faster route on any recent Android phone: open Settings and **search for "Font size"**. It jumps straight to the slider. Google also adds a Font Size tile to Quick Settings the moment you touch the slider, so your parent can bump it later without going into Settings at all — swipe down, tap the tile, tap Increase.

## The bit nobody warns you about

**The system font size does not apply to every app.** Google's own documentation says so, and the one you will hit is Chrome: it has its own text scaling and ignores the system setting. If your parent tells you "I made it bigger and the browser looks exactly the same", that is why, and the fix lives in Chrome's settings, not the phone's.

Budget 10 minutes for the settings and 5 minutes for the app check afterwards. I have never needed more than that on either platform.

So after you change the system setting, **open the 3 apps they actually use** and look at them:

- **Messages** — can every word fit without pinching to zoom?
- **Chrome** — the browser ignores the system font size and has its own setting
- **Email** — Gmail and Outlook both follow the system setting, so this one should already be right

Anything still small gets fixed inside that app, not on the phone.

Second warning, and it is the one that causes repeat visits: **font size alone is often not enough.** If the words are readable but the buttons are tiny, you want Display Zoom on iPhone and the Display size slider on Android. They are separate settings. People find the first one, assume they are done, and call you back a week later.

## When the phone is genuinely too small

Somewhere around 200% with the reading glasses off, the phone has run out of room. More pixels on a 6-inch screen is not an infinite resource — you have already set every text size the hardware offers.

At that point there are two honest answers. One is a phone with a genuinely large screen; I tested several in the [best phones for seniors](https://pragmaticsysadmin.help/senior-tech/2026-07-01-best-phones-for-seniors-2026/) roundup. The other is an app that does the one thing they need, with nothing else on screen to tap.

If they can read the text and simply cannot work the settings, that second answer is the cheaper one — a focused app beats a €400 handset. If they cannot read the text at all, no app is going to save them, and the phone itself has to change.

## FAQ

### Does making the text bigger drain the battery?

No. Font size is a rendering setting, not a display mode like dark mode. There is no measurable difference in battery life between the smallest and the largest text size. Brightness is what affects the battery.

### Will my parent break something by changing these settings?

No. Every one of them is reversible. On Android there is a **Reset settings** button on the Display size and text screen that puts the sliders back to factory values. On iPhone, drag each slider back to the middle.

### Can I do this remotely?

On iPhone, yes — you can drive the Accessibility settings from a Mac over USB. On Android it is possible over USB with developer mode on, but it is fiddly and depends on the manufacturer. If you have the phone for five minutes, doing it in person is faster, and you can check the result in the apps they actually use.

## What to do next

Set the text size and the display size — both, not one. Check the three apps they use daily. If the words still do not work at maximum, stop fighting the phone and either move to a bigger screen or to an app with nothing on it but the buttons they need. It is also worth adding this to the [quarterly tech checkup](https://pragmaticsysadmin.help/senior-tech/2026-07-02-the-quarterly-tech-checkup/) you do when you visit — every 3 months, at the same time as everything else — because text size drifts back to default more often than you would think, especially after a system update or a new phone.
