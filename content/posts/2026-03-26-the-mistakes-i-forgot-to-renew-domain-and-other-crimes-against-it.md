---
title: "The Mistakes I Made (And Why They Led Me to Build My Own Password Manager)"
date: 2026-03-26T12:00:00.000Z
categories:
  - General
description: "I've locked myself out of servers, forgotten more domains than you've heard of, and once deleted a production database on a Friday. Here's the mistakes that taught me more than any certification."
---

title: "The Mistakes I Made (And Why They Led Me to Build My Own Password Manager)"
date: 2026-03-26
draft: false
author: "Pragmatic Sysadmin"
tags: ["mistakes", "security", "passwords", "learning", "story"]
categories: ["stories", "security"]
description: "I've locked myself out of servers, forgotten more domains than you've heard of, and once deleted a production database on a Friday. Here's the mistakes that taught me more than any certification."
slug: "mistakes-that-taught-me-password-manager"

# The Mistakes I Made (And Why They Led Me to Build My Own Password Manager)

Every IT professional has a graveyard of mistakes behind them. Most of us just don't talk about them until we're several drinks in at a conference, or until we're writing a blog post that we hope will save someone else the same pain.

This is that blog post.

I'm going to tell you about the mistakes that shaped how I think about security. And then I'm going to show you how I built my own password manager - not because commercial ones are bad, but because building one taught me more about security than any certification ever could.

Let's start with the shame.

-----

## The Domain I Forgot to Renew

It was 2019. I was managing about twenty small business websites on the side. Good money, steady work, the dream freelance side hustle.

Then I got an email from a client.

*"Hey, our website is showing some weird Russian porn site. Is this a hack?"*

It was not a hack. It was me.

I had set up a calendar reminder to renew the domain. The calendar reminder had been on my laptop. My laptop had died. I had bought a new laptop. I had not migrated the calendar. The domain had expired. Some domain squatter had grabbed it within hours and put up exactly the kind of content that makes a small business owner question their life choices.

The fix took three days. The client almost fired us. The embarrassment lasted months.

**What I should have done:** Set up auto-renewal and store registration credentials in a centralized, backed-up location.

**What I actually did:** Trusted a calendar reminder on a single device.

-----

## The Server I Locked Myself Out Of

Picture this: I'm working on a client's firewall. I'm making good progress. I'm being thorough, which means I'm being paranoid, which means I'm double-checking the SSH configuration.

I make a change.

The SSH service restarts.

I try to reconnect.

*Connection refused.*

My heart rate doubles. I check the IP address. Correct. I check the port. Correct. I check the firewall rules I just modified.

Oh.

I had accidentally removed the SSH rule entirely. The server was now a very expensive doorstop in a data center three hours away.

Fortunately, this client had an on-site IT person. Unfortunately, that IT person was on vacation. Fortunately, they had a data center access badge. Unfortunately, I had to explain why I needed them to plug a keyboard and monitor into a server that was technically "my problem."

The fix took four hours and cost me two tickets to a baseball game I didn't want to attend anyway.

**What I should have done:** Use configuration management (Ansible, Terraform, anything) that would have prevented the lockout and allowed me to roll back.

**What I actually did:** Manual edits directly on the server like it was 2005.

-----

## The Friday 5PM Production Delete

This one still gives me nightmares.

I was cleaning up a test environment that had grown stale. Old VMs, old databases, cruft that had accumulated over months of development. Standard maintenance stuff.

I typed the command.

```bash
rm -rf /var/www/production/*
```

Wait.

I was on the production server.

The cursor was still blinking.

I yanked the power cord.

Yes, I know that's not the correct way to stop a running process. But I had about two seconds of memory of what I had just done, and my hands were doing their own thinking at this point.

Did I mention this was a Friday at 5PM?

The client's website was down for three hours while we restored from backup. The backup was six hours old because someone had turned off the nightly backup job three weeks ago to "fix a minor issue" and never turned it back on.

I did not sleep well that weekend.

**What I should have done:** 
- Never run commands without double-checking the current directory
- Use `rm -i` as a safety net
- Have proper backup verification in place

**What I actually did:** Trusted that I would never make a typo.

-----

## The Pattern

Look at these three stories. Different mistakes, different consequences, same root cause: **I was managing too much stuff with too few tools and too much manual work.**

The domain? Managed in one place, backed up nowhere.
The server lockout? No configuration management, no rollback plan.
The Friday delete? No automation, no backups being tested.

The common thread is that I was trying to keep everything in my head. Passwords for dozens of systems. Configuration notes that only I understood. Backup schedules that only I knew about.

That's when I realized: I needed a password manager. And not just "use 1Password" - I needed to understand how one worked.

-----

## Why I Built My Own Password Manager

Here's the thing about password managers: they're not magic. They're just encrypted databases with a good interface.

I started learning C# because I wanted to understand what was actually happening when I stored a password. And honestly? I wanted to see if I could build something that was actually *better* for my specific use case than the commercial options.

Turns out, I could. And I learned a ton in the process.

Here's what I built (and what it taught me):

### The Core Concept

A password manager does three things:

1. **Stores** credentials in an encrypted database
2. **Retrieves** credentials when you need them
3. **Generates** strong passwords so you don't have to think

That's it. Everything else is UI.

### The Encryption

The key insight is that your password manager doesn't encrypt with your master password directly. What it does is derive an encryption key from your master password using something called a **Key Derivation Function (KDF)**.

```csharp
// Simplified example of key derivation
using var pbkdf2 = new Rfc2898DeriveBytes(
    masterPassword,
    salt,
    iterations: 100000,
    HashAlgorithmName.SHA256
);
byte[] encryptionKey = pbkdf2.GetBytes(32); // 256-bit key
```

The `salt` is unique per database. The `iterations` makes brute-forcing slow by design. This is why your master password matters - it's not just "the password to unlock the app," it's the key that generates the actual encryption key.

### The Database

Your passwords live in an encrypted file on your hard drive. Mine uses SQLite with a twist - the entire database is encrypted, not just the password field.

```csharp
public class PasswordEntry
{
    public Guid Id { get; set; }
    public string ServiceName { get; set; }
    public string Username { get; set; }
    public string EncryptedPassword { get; set; }
    public string Url { get; set; }
    public string Notes { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime ModifiedAt { get; set; }
}
```

The `EncryptedPassword` field contains the actual password, encrypted with AES-256-GCM. If someone steals your database file, they get nothing without your master password.

### The Password Generator

This is the fun part. Strong passwords aren't memorable, but they're essential:

```csharp
public string GeneratePassword(int length = 20, bool includeSymbols = true)
{
    const string lowercase = "abcdefghijklmnopqrstuvwxyz";
    const string uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const string digits = "0123456789";
    const string symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?";

    string chars = lowercase + uppercase + digits;
    if (includeSymbols) chars += symbols;

    var random = new Random();
    return new string(Enumerable.Repeat(chars, length)
        .Select(s => s[random.Next(s.Length)]).ToArray());
}
```

Yes, `Random` isn't cryptographically secure. In a real implementation, you'd use `RandomNumberGenerator`. But for understanding the concept, this works.

-----

## The Lesson I Learned

After building my own password manager, I started using it everywhere. Not because it's better than Bitwarden or 1Password (it's not), but because I now *understand* what those tools are doing.

When someone asks me "is it safe to store passwords in the cloud?", I can actually answer the question. The encryption is happening client-side before anything leaves your device. The cloud provider never sees your actual passwords. The security isn't in the cloud - it's in your master password and the encryption key derived from it.

Understanding the mechanics made me a better IT professional. I stopped treating security as magic and started treating it as math.

-----

## Should You Build Your Own?

Honestly? Probably not for production use. Commercial password managers have had years of security auditing, they handle edge cases you haven't thought of, and they have dedicated security teams.

But should you build one to *learn*? Absolutely.

Here's what you'll learn:
- Why master passwords matter (key derivation)
- How encryption actually works (AES-256-GCM)
- Why password reuse is dangerous (they're all stored together)
- What "zero knowledge" actually means (the server can't read your data)

That's worth a weekend project.

-----

## My Setup Today

I use Bitwarden now. Self-hosted on my own server. It syncs across devices, has all the features I need, and I understand exactly how it works because I built something similar first.

The domain got auto-renewed. The firewall has Ansible managing its configuration. The backups are tested monthly.

And I never, ever run commands without checking my current directory twice.

Some mistakes you only make once.

-----

*What about you? Any disasters you'd be willing to share in the comments? I'm convinced every IT person has at least one story like this. Let's normalize talking about them.*