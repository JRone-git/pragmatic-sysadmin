---
title: "Why I Built Buddy: The Free App I Wish I'd Had When My Dad Got Sick"
date: 2026-08-03
author: Pragmatic Sysadmin
description: "I built a free, multi-language companion app for my dad when dementia made his phone unusable. Here's what I learned about designing for elderly users — and why I gave it away for free."
draft: false
tags: ["buddy", "personal", "elderly", "ux", "accessibility"]
slug: why-i-built-buddy-free-app-dad-sick
topics: ["buddy", "personal-story"]
resources:
  - name: buddy
    url: /buddy/
    description: Try Buddy — free, no account needed
---

My dad called me at 2 AM.

"I can't find my medication," he said. "I don't know what day it is."

He was 76. He had dementia — early stage, we thought, until it wasn't. What he actually had was a UTI that no one had caught, accelerating everything. But at 2 AM, I didn't know that. I just knew he was confused, scared, and alone in his apartment 400 miles away.

I drove up that morning. Sat with him. Watched him stare at his phone like it was a foreign object — which, in a sense, it was. Small text. Too many apps. Notifications everywhere. He'd been using it for 10 years and suddenly it might as well have been written in hieroglyphics.

That's when I started building Buddy.

<!--more-->

## What I Learned Watching My Dad Use a Phone

I thought I understood elderly users. I've been doing sysadmin work for 15 years. I'd set up my parents' computers, tablets, and phones more times than I could count. I thought the solution was "make things simpler."

It wasn't that simple.

The real problem wasn't complexity. It was **cognitive load**. Every app demanded decisions: what does this icon mean? What happens if I tap here? Where am I now? For someone whose short-term memory was deteriorating, each decision was a small failure waiting to happen.

My dad didn't need fewer features. He needed **fewer decisions per action**.

Buddy is the app I wish I'd had. Here's what I learned building it.

## Design Principle 1: One Screen, One Job

Most apps scatter functionality across dozens of screens. Buddy has five:

- **People** — tap a face to call someone
- **Medicines** — tap green when you've taken something
- **Safety** — quick access to emergency contacts
- **Notes** — PIN-protected reminders
- **Help** — what to do if something goes wrong

That's it. No settings labyrinth. No hamburger menus. No "did you know you can also..." screens.

From any screen, you can get back to home with one tap. Home is five tiles, and each tile takes you somewhere you need to be.

## Design Principle 2: Photos Replace Text

My dad can't read small text. Neither can most people over 75.

So instead of a contact list with names, Buddy shows faces. Tap Sarah's photo, and it calls Sarah. No reading required.

This sounds obvious. It's shocking how few apps do it. The mainstream apps all assume you can read — they use text as the primary navigation medium. A person with macular degeneration or early dementia simply can't use them reliably.

Buddy also lets you add photos from the camera — no uploading, no accounts, everything stays on the device.

## Design Principle 3: Medicine Tracking That Resets

My dad has seven medications. Some are twice a day, some once, one is every other day. Keeping track of what he'd taken was a full-time job for both of us.

The existing pill reminder apps were overwhelming — too many features, too many screens, too easy to accidentally mark the wrong pill as taken.

Buddy's medicine tracker is dead simple: green circle means taken, empty circle means not yet. It resets every morning at midnight. If dad was confused about what day it was, at least he could see "have I taken my morning pills?"

The alarm feature lets you set a reminder for each medication. When it's time, your phone tells you — even if you're not looking at the app.

## Design Principle 4: It Works in Seven Languages

My dad speaks Finnish. His care coordinator speaks English. My aunt in Spain speaks Spanish.

Most health apps are English-only. Buddy isn't. I translated it into English, Spanish, French, German, Portuguese, Chinese, and Finnish — covering the native languages of most of the world's elderly population.

Translation isn't just swapping words. It's rewriting sentences to be shorter. Choosing vocabulary that works for someone with a grade-school reading level in that language. Making sure the tone is respectful, not condescending.

"SUBMIT" becomes "Done" in English, "Listo" in Spanish. Same meaning. Different cognitive weight.

## Design Principle 5: No Account, No Data, No Cost

I deliberately built Buddy so it doesn't need an account. No email. No password to forget. No data on a server somewhere.

Everything lives in your browser — or on your phone if you add it to your home screen. The app works offline. It never calls home.

This was a philosophical decision and a practical one:

- **Philosophical**: an app for vulnerable elderly people shouldn't be monetizing their health data
- **Practical**: every barrier to entry (create account, verify email, set password) is a barrier for someone with cognitive decline

The app is free because I didn't want money to be the reason someone couldn't use it.

## What I Got Wrong (And Fixed)

Building v1, I made the text too small by default. "It's a phone screen," I thought, "there isn't much room."

My 78-year-old mom tried it and said: "I can't read this."

Fixed. There are now three display sizes: Comfortable, Large, and Extra Large. You pick once, it remembers forever.

I also initially used a complicated PIN entry system for the notes section. The PIN is just four digits. Four. That's it. One more feature I thought would be helpful was actually just friction.

## The Feature I Want to Build Next

Voice. Real text-to-speech and speech-to-text.

My dad sometimes couldn't read at all — but he could still talk. An app that reads the medicine list out loud, that lets you add a contact by speaking — that's the next version.

I've started building it. It needs service worker support for background notifications, which adds complexity. But the core is there: `navigator.speechSynthesis` for reading text aloud.

If you want to follow that journey, the code is [on GitHub](https://github.com/JRone-git/pragmatic-sysadmin/tree/main/static/buddy).

## Why Free?

I've been asked this a few times. Here's the honest answer:

My dad died in March. Not from dementia — from the UTI that accelerated everything. He was 77.

I built Buddy for him. I couldn't save him. But I could build something that might help someone else's dad, someone else's mom, someone else's grandparent — keep track of their pills, call their kids, feel a little less lost.

That's why it's free.

---

**Try Buddy:** [pragmaticsysadmin.help/buddy](/buddy/) — works on any phone, no account needed, works offline, in 7 languages.

If you find it useful, consider buying the [5-Minute Server Health Check Toolkit](https://pragmaticsysadmin.help/products/health-check-toolkit/) — it funds the server costs and gives you something you'll actually use.
