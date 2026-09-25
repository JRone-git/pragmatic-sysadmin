---
title: "Software That's Never Been Done: On Building Things That Should Exist But Don't"
date: 2026-08-04
author: Pragmatic Sysadmin
description: "Most software is iteration. Better UI, faster, more features. But sometimes you see something that makes you think: why didn't this exist before? Here's what I've learned about spotting and building truly novel software."
draft: false
tags: ["philosophy", "software", "innovation", "ux", "product-thinking"]
slug: software-thats-never-been-done-out-of-the-box-thinking
topics: ["meta", "thinking", "software"]
---

I had a problem.

My dad had dementia. He couldn't remember if he'd taken his pills. He couldn't remember what day it was. He couldn't reliably use the phone he'd been using for a decade.

I looked at the App Store. I found 47 medication reminder apps. Every single one of them had: user accounts, push notification permissions, onboarding flows, settings screens, cloud sync, subscription upsells.

Not one of them was: open the app, tap green when you've taken your pill, done.

So I built Buddy. And I kept running into the same reaction from everyone I showed it to: "why doesn't this already exist?"

That's the question behind this post.

<!--more-->

## The "Someone Should Build That" Test

You know that feeling. You're using a piece of software and something is obviously wrong — not a bug, but a fundamental mismatch between what the tool does and what you actually need. You think: *someone should build something that does X*.

Most of the time, X has already been built. You just didn't find it.

But sometimes — rarely — X genuinely hasn't been built. Not well, not accessibly, not without 15 years of enterprise baggage. Sometimes the thing you want to exist actually doesn't exist.

Learning to tell the difference between those two cases is a skill. And it's worth developing, because the second case is where the interesting work is.

## What Makes Something "Never Been Done"

I've been thinking about this for a while, since Buddy started getting used by actual people. Here's what I've noticed about the genuinely novel stuff:

**It solves a problem that was considered unsolvable or not-worth-solving.** The mainstream solution requires accounts, setup, maintenance. The problem is "not worth" solving for the general population. But for a specific person, it's the most important thing in the world.

**It inverts the default.** Most apps add features. Novel software removes them. Not features that don't matter — features that *everyone assumed were necessary but actually weren't*. Buddy doesn't have user accounts. That's not a missing feature. It's the point.

**It works for the hardest case.** If something only works for the easy 80%, it's probably been done. The 20% — the person with dementia, the non-English speaker, the person with a flip phone — that's where you find the gaps. And filling those gaps is novel.

**It makes the expert feel like a beginner.** Not in a condescending way. In the way that when you first discovered `grep`, or `tmux`, or `git stash` — you thought differently about the problem after. The tool changed how you thought, not just what you could do.

## Three Examples of Software That Should Have Existed Sooner

### 1. Buddy — The App for People Who Can't Learn New Apps

Medication reminder apps existed. Phone apps for seniors existed. Emergency contact apps existed.

What didn't exist: an app that a person with moderate dementia could use reliably without help. That was the gap.

The hard part wasn't the code. The hard part was the restraint — every feature I wanted to add, I had to fight myself not to add. Dark mode. Widgets. Reminders for vitamins. A second screen for special instructions.

None of those things help someone who can't remember how to get back to the home screen.

### 2. `curl` — The Tool That Was Already There

Roy Fielding didn't create HTTP. He created a tool that exposed what HTTP already was.

Before `curl`, you wrote a custom program to test an HTTP endpoint. `curl` made the protocol itself the interface. You didn't learn `curl` — you already knew HTTP, and `curl` just let you say what you meant.

That's the other kind of novelty: not building something new, but making something that was always true suddenly easy to express.

### 3. Mosh — The SSH That Doesn't Break When Your WiFi Does

SSH is 25 years old. It's reliable. It's universal.

It also freezes completely when your connection drops. You're stuck looking at a frozen terminal until the connection times out, then you reconnect and start over.

Mosh did something SSH could have done at any point in 25 years: run the terminal session on the server, sync the current screen state over UDP, reconnect instantly when the connection comes back. Same SSH keys. Same remote servers. Just... works when you're on a train through a tunnel.

The gap wasn't technical. SSH could have done this in 2005. The gap was that SSH had always worked a certain way, and nobody asked whether that way was actually the right way.

## The Pattern Behind the Pattern

Here's what I've come to believe: most software that "should exist but doesn't" doesn't exist because of **accumulated assumptions**.

Each assumption is reasonable on its own. User accounts are necessary for data sync. Settings screens are necessary for flexibility. Onboarding is necessary to explain features.

But stacked together, they make something unusable for the people who need it most. The features designed for power users become barriers for everyone else.

The out-of-the-box thinking isn't a creative exercise. It's subtraction. It's asking, for each thing you assumed was necessary: *what if it wasn't?*

## How to Spot a Gap Worth Filling

Not every gap is worth filling. Here's the filter I use:

**1. Does the hard case actually exist, or am I imagining it?** Buddy only exists because my dad was real, with a real problem, and I watched him fail with real apps. If I'd imagined the problem theoretically, I would have built something theoretical and wrong.

**2. Would removing the assumed-feature break the 80%?** If yes, the feature is actually serving a real need. If no — if the 80% only uses it because it's there — then it's a candidate for removal.

**3. Is there a way to make it simple without making it limited?** The hardest design problem in Buddy was medicine tracking. It's dead simple (tap green when taken). It's also complete (resets daily, supports any schedule). Those two things usually conflict. When they don't conflict, you're probably onto something.

**4. Would I use it myself?** This is my final test. I've built tools that solved a problem I imagined someone else had. I've never shipped something I personally used and valued that failed. If I wouldn't use it daily, I slow down and ask why I'm building it.

## What You Lose When You Subtract

Subtraction is not free. When you remove accounts, you remove password recovery. When you remove settings screens, you remove customization. When you remove onboarding, you remove the chance to explain your brilliant UX decisions.

The honest answer is: some users will get lost. Some edge cases will break. Some power users will complain that it's "too simple."

That's the trade. Simple enough for the hardest case, complex enough for the common case. That line is never in the same place twice.

Buddy is too simple for someone managing 20 medications. It's too simple for someone who needs HIPAA-compliant medical records. That's fine. It was never meant to be those things.

It was meant to be the app my dad could use at 2 AM when he couldn't remember what day it was.

That mission is narrow enough to be achievable.

## The Question to Ask Before You Start

Before you build anything, ask:

> *What would this look like if the person using it had five minutes of attention and zero technical experience?*

Now build that version.

Not the version with the settings screen. Not the version with the subscription tiers. Not the version with the "power user mode."

The version for the person who just needs it to work, right now, without help.

That's the version that usually doesn't exist.

---

*If you're working on something that fits this description — genuinely novel, subtraction-first, for the hard cases — I'd love to hear about it. The best software I've ever used was built by someone who refused to accept the conventional answer to "but what about X?"*
