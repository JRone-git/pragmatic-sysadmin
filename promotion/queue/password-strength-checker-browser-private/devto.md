---
title: "I Built a Password Strength Checker That Runs 100% in Your Browser (and What It Taught Me About Passwords)"
canonical_url: https://pragmaticsysadmin.help/sysadmin/2026-10-06-password-strength-checker-browser-private/
tags: sysadmin
---

## The Phone Call That Started This

A client's junior admin called me last month. Their company had just rolled out a new password policy — 14 characters, three character classes, rotation every 90 days — and the helpdesk was drowning in reset tickets. The admin was proud of the policy. The users were writing the new passwords on sticky notes stuck to their monitors.

That is the entire password industry in one story: we keep making the rules harder without making the passwords better.

So I did what I always do when I'm annoyed: I built the thing I wish existed.

## The Tool: 100% Client-Side, Nothing Leaves Your Browser

[Try the Password Strength Checker](https://pragmaticsysadmin.help/tools/password-checker.html) — paste a password, get an honest strength rating: length, character classes, and common-pattern weaknesses. No account, no tracking, no server. Open the network tab in dev tools if you don't believe me; nothing is sent anywhere.

Why does that matter? Because a non-trivial number of online "password checkers" submit what you type to their backend for "analysis." Think about that for a second. You are sending your *actual password* to a stranger's server to find out if it's good. I built mine specifically so that can't happen — there is no backend. The HTML file doesn't even make a fetch request.

## What I Actually Learned Testing 200 Passwords

I ran a pile of real-world-style passwords through the checker while building it — the kind of passwords people actually use, not the kind security training pretends they use. Three findings surprised me:

**1. Length beats cleverness, every time.** A 20-character passphrase of plain words (`correct horse battery staple` style) outscores an 8-character symbol-soup password on every honest metric. The math isn't close: each extra character multiplies the search space, while swapping `e` for `3` adds almost nothing because attackers already try that.

**2. The complexity rules actively hurt.** Forcing symbols and numbers pushes people toward predictable patterns: `Password1!`, `Summer2025!`, company-name-plus-year. Attackers' rule lists contain exactly these mutations. A policy that bans those patterns would be ten times more effective than a policy that demands a symbol — but "must contain !" is easier to audit than "must not be predictable," so here we are.

**3. Rotation policies create the problem they claim to solve.** Every 90-day rotation study I've read says the same thing: users increment a number (`...Q3` → `...Q4`) or rotate through three passwords. The new password is never stronger; it's just newer. If a password is strong and unique, leave it alone. Rotate on *suspicion of compromise*, not on a calendar.

## What To Do Instead (The Pragmatic Version)

For yourself and your users:

- **Use a password manager.** Bitwarden is free and open source. This is the single highest-leverage security change a normal person can make, and I wrote a [10-minute setup guide for elderly parents](https://pragmaticsysadmin.help/senior-tech/2026-07-27-password-manager-for-elderly-parents/) that works for anyone.
- **One long, unique password per service** — generated, never reused. Reuse is what actually gets accounts taken over, not weak passwords.
- **Turn on 2FA everywhere that matters**, especially email — email is the master key to every "forgot password" flow you have.
- **Test your own passwords** with the checker. If your scheme produces anything the tool flags as a common pattern, change the scheme, not the password.

## The Build Notes (For Fellow Tinkerers)

The whole tool is one self-contained HTML file: vanilla JS, no dependencies, no build step. The scoring is deliberately simple and explainable — entropy estimate from length and character classes, minus penalties for dictionary words, keyboard walks (`qwerty`, `1qaz`), repeated characters, and date/sequence patterns. No machine learning, no API calls, no analytics.

Simplicity is the point. A security tool you can't audit is a security tool you shouldn't trust, and "trust me, it runs locally" is a claim anyone can verify in the network tab.

---

*Try it: [Password Strength Checker](https://pragmaticsysadmin.help/tools/password-checker.html) — free, private, no account. If it saves one person from sending their password to a stranger's server, it was worth the afternoon.*
