---
title: "When Code Meets Life: Applying the Sysadmin Mindset to Family Chaos & Home Repairs"
canonical_url: https://pragmaticsysadmin.help/sysadmin/2026-10-28-when-code-meets-life-sysadmin-mindset-family-home-repairs/
tags: sysadmin
---

Last Tuesday the kitchen tap started dripping.

Not a lot. Just one drip every four seconds or so. Annoying, not alarming. The kind of thing you notice, mentally file under "weekend," and then forget about for three weeks until it's dripping onto the floor and you've got a puddle forming near the dishwasher.

I did what any sysadmin does. I didn't fix it. I **investigated** it.

<!--more-->

## Step 1: Is This Actually a Tap Problem?

Twenty minutes of observation established the following:

- The drip continued with the tap fully closed ✅ (real leak, not a dripping faucet)
- The drip rate was **exactly one drip every 4.1 seconds** — metronomic, suspiciously regular
- The drip was coming from the spout outlet, not the handle or the joint

I turned off the stopcock under the sink. Drip stopped. Turned it back on. Drip resumed.

Root cause confirmed: **the ceramic cartridge was worn**. Not the washer, not the supply line, not a loose fitting. A €6 part.

Ninety seconds of work. Five minutes of diagnosis. €6 and a YouTube video.

I thought about how I'd actually spent that same Tuesday at work: 40 minutes of a service outage, and the eventual conclusion was "the connection pool was exhausted because someone left a connection open." Same thing. Look at the actual symptom, don't guess at the cause, check the cheapest explanation first.

## A Family Is a Distributed System

Here's the thing I realized somewhere between the second drip and the cartridge replacement:

**The troubleshooting methodology I use on servers is identical to the one that works in my house.** Not similar. Identical.

And once I saw that, I couldn't stop seeing it everywhere.

| Sysadmin | Home / Family |
|---|---|
| Read the logs before you touch anything | Notice *when* it started, not just *that* it started |
| Isolate one variable at a time | Change one thing, wait a week, see if it helped |
| The obvious cause is usually right | Is it plugged in? Is there a battery? |
| Reproduce the bug before you fix it | Can you make it happen on purpose? |
| Working backwards from the symptom | Which end of the pipe is wet? |
| Root cause vs. surface symptom | The drip is the symptom — the cartridge is the cause |
| Escalation path | When do I call a plumber vs. a YouTube video? |
| Document everything | The house manual, receipts, warranty dates |
| Capacity planning | When does this thing need replacing? |
| Patch management | Annual boiler service, smoke alarm batteries |
| Single point of failure | The one person who knows where everything is |
| Redundancy | Two spare light bulbs, not one |
| Technical debt | The shelf held up with card and tape |
| On-call rotation | Tag team parenting |
| Incident response | It's 2 AM and the toilet is flooding |
| Change management | Nap schedule, new school, moving house |
| Blast radius | One person's bad mood affects the entire household |
| Cache | The freezer meal stash, the spare key |
| Legacy system | That appliance that works — don't touch it |
| Monitoring & alerting | The leak sensor, the doorbell camera, the fall detector |
| Backup | Photos of receipts, serial numbers, warranty PDFs |
| Rollback | Knowing how to undo what you changed |

I keep going back to that last one. **Rollback.** When I put the smart plug on the boiler's smart control, I wrote down how to put it back to manual. When we changed the DNS settings, I screenshotted the old ones. When the kid's bedtime moved from 7 to 7:30, I didn't just change it — I kept the old routine for a week in case reverting was needed.

Nobody does this for a family. But it works exactly the same.

---

## The House Log

The single most useful thing I've done for my household is keep a **house log**. It's a note on my phone. That's it.

When something breaks, I don't start from scratch. I check the log first:

```
2026-10-28  Kitchen tap dripping every 4 sec. Closed stopcock → stopped.
            Root cause: ceramic cartridge (€6, took 90 min).
            Fixed. Water pressure in the kitchen is lower than the bathroom.

2026-09-14  Boiler making a clicking noise when it heats. Not a fault.
            Was the same noise last winter. Ignore.

2026-08-02  Fridge freezer stopped freezing. Defrosted, thermostat was
            set to -15 instead of -18. Not the compressor.

2026-06-19  Hallway light flickers. Bulb was fine. The switch was loose.
            Tightened the terminal. Fixed.
```

Why this works: it stops you re-diagnosing solved problems. The boiler clicking noise? I already know. It's the same as last winter. Ignore it. That alone has saved me hours and probably a pointless £150 engineer call.

It also captures **the pattern**. Six months after the tap, when the bath tap starts dripping too, I don't start from zero — I go straight to "cartridge."

**The house log is the single highest-ROI thing on this list.** It takes 30 seconds to write and it's the difference between "I don't know what's wrong" and "I think I know what's wrong."

I keep mine in a phone note because I always have my phone. If you prefer, a physical notebook by the boiler works too — old school, zero apps, nobody can break it.

---

## Escalation: When to Stop

The most important sysadmin skill — and the one I was worst at learning — is knowing when to **stop** and call for help.

My personal escalation criteria, in order:

**1. It involves electricity and water in the same job.** Stop. Call someone. No exceptions, ever.

**2. The instructions say "if you are unsure, contact a qualified professional."** Stop. That's the manufacturer telling you the job is beyond a YouTube video.

**3. You need to cut into the wall, drill through tiles, or move a gas line.** Stop. These aren't DIY tasks, no matter how many videos you watch.

**4. The fix involves a part you'd have to order anyway.** If the part costs €60 and you need an electrician to install it, use an electrician. Don't buy the part and spend two hours learning a skill you'll use once.

**5. The symptom is "it worked yesterday and now it doesn't."** That's the hardest category. Sometimes it's genuinely simple. Sometimes it's a failing component that would have failed anyway. If you've spent 30 minutes and you're guessing, escalate.

**Everything else is fair game.** Dripping taps, running toilets, blocked sinks, squeaky hinges, slow drains, flickering lights, doors that don't latch. These are the sysadmin equivalent of a restart: low risk, clear scope, you can undo it if it goes wrong.

The cost asymmetry helps: a bad DIY job on a tap costs €6 in parts. A bad DIY job on an electrical circuit costs a house.

---

## Parenting as Incident Response

I wasn't expecting the parenting parallels to be this obvious, but they are.

**Debugging a tantrum** is variable isolation. Four-year-olds have a small number of recurring triggers, and if you write them down you'll find them fast:

- Tired
- Hungry
- Overstimulated
- Transition given too late

My daughter has a tantrum roughly 20 minutes before any transition — leaving the park, ending a TV show, going to bed. Same input, same output, every time. Once I spotted the 20-minute pattern, I could pre-empt it: "We have 15 more minutes, then we go home." No tantrum. Because I stopped treating each one as a new incident and started treating it as a **known reproducer**.

That's just bug reproduction. You can't fix what you can't reproduce.

**The nap log is a metrics dashboard.** Sleep times, wake times, total sleep, mood rating. After two weeks of actual data I stopped guessing about whether she needed a longer nap and started just... knowing. I'd lost weeks to "should she nap?" debates that a two-column note would have settled.

**Load balancing is capacity planning.** Two parents, one demanding toddler, one work deadline. The failure mode isn't that one person works too hard — it's that both parents independently take on half of *everything*, which is more than half. You need explicit division: one person owns the morning, the other owns bedtime. Not both halves of both.

**Blast radius matters.** One parent's bad mood in the morning sets the tone for the whole day, for everyone. I know this from production systems — one unhealthy dependency poisons everything downstream. A ten-minute reset before the day starts ("I'm having a rough morning, here's my plan") does more than you'd think.

**Change management for a toddler is brutal.** We moved her bedtime by 30 minutes and it took eleven days. Then we moved it back and it took four. Never have I seen a rollback take so long or fail so spectacularly.

---

## The One I Didn't Expect: Technical Debt in the Home

Every house I've been in has a shelf somewhere that is technically held together by a piece of card and masking tape. Every house has a door that only closes if you lift it slightly. Every house has one electrical socket that's slightly loose.

These are **technical debt**. They work right now, so nobody fixes them. Then one day the shelf falls, or the socket fails, and the fix takes twice as long as it should because it's built on a hack nobody documented.

**The house log is how you pay down technical debt.** When you finally fix the shelf properly, write it down: what it was, how you fixed it, that the tape is gone. Future you doesn't have to reverse-engineer a 2019 hack.

I also started a simple rule: **one fix a quarter.** Not a renovation. One thing that was held together with tape gets fixed properly. Rotating a small list of debt, three or four times a year, and the house gets steadily less held together with tape.

---

## On-call Is a Role, Not a Personality Trait

One thing I got wrong for years: I thought being "the tech person in the family" was a personality trait. It's a **role**, and it needs boundaries.

Being on call for the family tech means:
- Being reachable for real emergencies (no Wi-Fi, no heating in February)
- Being **explicitly not** on call for "the printer is acting weird" at 9 PM on a Sunday
- Having a backup (a sibling, a partner, a family friend who's comfortable with technology)
- Rotating it — the person who was on call this month isn't automatically next month

The difference between "on call" and "always on" is the difference between a resilient system and a burnout. I learned this one the expensive way.

The whole point of automating things — the smart plug, the leak sensor, the [Buddy app](https://pragmaticsysadmin.help/buddy/) on my dad's phone — is to reduce the number of pages that reach a human. Every alert that fires at 3 AM erodes the willingness to respond to the alert that actually matters.

**Automation is a force multiplier for attention, not a replacement for it.** The smart plug that turns off the iron means one fewer thing to think about, which means more attention for the stuff that genuinely needs me.

---

## The Actual Point

None of this is a clever analogy. I know how it sounds — "everything is distributed systems" is a cliché, and I'm not claiming the metaphor is illuminating.

But the *method* transfers. And the method is:

1. **Look at the actual symptom before theorizing about the cause**
2. **Write down what you learn**
3. **Change one thing at a time**
4. **Know the cheapest explanation, and check it first**
5. **Know when you're out of your depth, and escalate without shame**

That's it. That's the whole method. It works on a leaking tap, a frustrated four-year-old, and a production database at 2 AM, and the reason it works is the same in all three cases: the person who wrote the code doesn't know what the bug is until they look.

---

*What's the house log entry you wrote down this year that you still remember? I'd genuinely like to know — send me yours at [pragmatic@pragmaticsysadmin.help](mailto:pragmatic@pragmaticsysadmin.help).*
