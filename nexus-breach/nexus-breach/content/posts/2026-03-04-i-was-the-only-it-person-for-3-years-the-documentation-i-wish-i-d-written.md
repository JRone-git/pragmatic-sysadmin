---
title: "I Was the Only IT Person for 3 Years: The Documentation I Wish I'd Written"
date: 2026-03-04T07:10:00.000Z
categories:
  - General
description: "When I left my solo IT job, my replacement called me 47 times in the first month. Here's the documentation I wish I had written before I left - and the template you can use today."
---

title: "I Was the Only IT Person for 3 Years: The Documentation I Wish I'd Written"
date: 2026-03-03T23:00:00Z
draft: false
tags: ["documentation", "career", "solo-it", "best-practices", "knowledge-transfer"]
categories: ["Career", "Best Practices"]
description: "When I left my solo IT job, my replacement called me 47 times in the first month. Here's the documentation I wish I had written before I left - and the template you can use today."
The Call I Didn't Want to Get
Three weeks after leaving my job as the only IT person at a mid-sized company, my phone rang. It was Mike, the guy they hired to replace me.

"Hey, uh, do you remember that backup script you set up? The one that runs on Sundays? It's throwing an error and I can't find where it's configured."

I helped him. Then he called again the next day about the VPN. Then about the firewall rules. Then about why the CEO's email kept going to spam.

By the end of month one, Mike had called me 47 times.

Here's the thing: I thought I had done a good job documenting everything. I had wiki pages. I had a SharePoint folder full of PDFs. I had even written a "handover document" before I left.

But none of it was useful because I had documented the wrong things in the wrong way.

The Invisible Knowledge Problem
When you're the only IT person, you become a walking encyclopedia of institutional knowledge that exists nowhere else:

You know that the server in the closet makes a weird noise every Tuesday at 3 AM (it's the backup tape drive, and it's fine)
You know that the CFO's laptop needs special VPN settings because of some legacy accounting software
You know that the "critical" production database is actually just a reporting copy and can go down for maintenance
You know where the network cables behind the bookshelf go (even though they're not on any diagram)
None of this is in your documentation. It's all in your head.

And when you leave - whether for a new job, a vacation, or because you got hit by a bus - that knowledge leaves with you.

The Bus Factor Quiz
Quick test: If you got hit by a bus tomorrow, could someone else:

Access your password manager and all your accounts?
Find the recovery codes for your two-factor authentication?
Know which servers are critical vs. which can go down?
Understand what that weird cron job does at 2 AM?
Contact your vendors and actually get help?
If you answered "no" or "maybe" to any of these, you have a bus factor problem. And in solo IT, your bus factor is always 1.

Why Most IT Documentation Fails
I used to think documentation meant writing everything down. So I did:

47-page network diagram (outdated within a month)
Change management procedures (nobody followed them)
Server inventory spreadsheet (missing half the VMs)
Disaster recovery plan (never tested, probably wouldn't work)
The problem? I was documenting for auditors, not for the poor soul who would eventually need to actually run things.

What Actually Works
After Mike's 47 calls, I started keeping track of what he actually needed to know. Here's what came up most often:

The "Why" Behind Decisions

Why is this server configured this way? (Usually because of some edge case nobody remembers)
Why do we have two different backup systems? (The old one is for legal compliance, the new one is for actual recovery)
Why does the CEO have local admin rights? (Don't ask, just don't take them away)
The Hidden Dependencies

This server depends on that one, which depends on a service running on a third one
The WiFi in the conference room breaks if you restart the main switch in the wrong order
The CRM integration breaks every time the accounting software updates
The "Normal" Abnormalities

Yes, that error message appears every day and it's fine
No, that server doesn't need more RAM, it's just badly configured
The warning in the logs is expected behavior, we've been ignoring it for two years
The Documentation Template That Would Have Saved Me 47 Phone Calls
Here's what I should have left behind. This is a template you can copy and fill in today - not when you're about to leave, but right now, while you still remember why you configured things the way you did.

Section 1: The "If I Get Hit By a Bus" Page
This is a single document that lives somewhere obvious. Not in a wiki that requires login. Not in a folder buried five levels deep. Print it. Put it on the server room door.

CRITICAL INFORMATION - START HERE
Master Passwords
Password manager master password: [Location of sealed envelope or key escrow]
Domain admin account: [Account name and where credentials are stored]
Cloud console access: [Which email address receives MFA codes]
Critical Contacts
Internet provider support: 1-XXX-XXX-XXXX, Account #XXXXX
Hardware vendor support: 1-XXX-XXX-XXXX, Contract #XXXXX
MSP or consultant (if any): Name, phone, email
CEO's personal cell (for emergencies only): XXX-XXX-XXXX
The "Don't Touch" List
These things will break if you change them:

[Server/service] - Reason: [Why]
[Configuration] - Reason: [Why]
Known Issues We're Living With
[Issue] - Why we haven't fixed it: [Reason] - Impact: [What happens]
Section 2: The Services Inventory
Not just "what servers do we have" but "what services exist and why do they matter?"

Services Inventory
Tier 1 - Critical (Down = Business Stopped)
Service	Server	What It Does	Who Uses It	Restart Procedure
Main database	PROD-SQL-01	All customer data	Everyone	See Runbook #3
File server	FS-01	All company files	Everyone	Auto-restart, check shares after
Email	Office 365	Email	Everyone	Microsoft handles it
Tier 2 - Important (Down = Some People Can't Work)
Service	Server	What It Does	Who Uses It	Restart Procedure
Tier 3 - Nice to Have (Down = Annoying But Not Urgent)
Service	Server	What It Does	Who Uses It	Restart Procedure
Tier 4 - We Should Probably Turn This Off
Service	Server	Why It Still Exists	Can We Delete It?
Old CRM	LEGACY-01	Legal requires 7 years	Delete after 2027
Section 3: The "Why" Document
For every non-obvious configuration decision:

Configuration Decisions & Rationale
Why Does the VPN Require Two-Factor Auth for Some Users But Not Others?
Reason: Executives complained about the extra step. Yes, this is a security risk. No, I couldn't convince them otherwise. The CFO specifically requested exemption.

Date of Decision: March 2024Who Approved: CFO, CEOCan This Be Changed? Only with CFO approval

Why Is the Backup Server Running an Old OS Version?
Reason: The backup software vendor hasn't certified the new OS version yet. We tried upgrading in test and it broke the backup catalog.

Date of Decision: January 2024Workaround: Applied all security patches that don't affect the backup softwareRevisit Date: Check vendor website monthly

Why Does the CEO Have Local Admin Rights?
Reason: He installs software for "productivity" and refuses to wait for IT. We tried restricting it. He complained to the board.

Date of Decision: Before my timeMitigation: His laptop has extra monitoring and we image it monthlyCan This Be Changed? LOL no

Section 4: The Dependency Map
Service Dependencies
If Server X Goes Down, What Breaks?
PROD-WEB-01 (Main Web Server)├── Requires: PROD-SQL-01 (Database)├── Requires: REDIS-01 (Cache)├── Requires: NFS-01 (File uploads)└── If down: External customers cannot access the website

PROD-SQL-01 (Main Database)├── Requires: BACKUP-01 (Backup jobs)├── Requires: MON-01 (Monitoring)└── If down: EVERYTHING breaks (see affected services list)

Startup Order (After Power Outage)
Wait 5 minutes for network switches
Start PROD-DC-01 (Domain Controller)
Start PROD-SQL-01 (Database)
Start REDIS-01 (Cache)
Start PROD-WEB-01 (Web Server)
Verify services with checklist in Runbook #5
Section 5: The Vendor & License Tracker
Vendors & Licenses
Software Licenses
Software	License Type	Renewal Date	Admin Contact	License Key Location
Microsoft 365	50 seats	Annual, March	admin@company.com	Admin portal
Backup Software	Perpetual	N/A	N/A	License.txt on BACKUP-01
Antivirus	100 seats	Annual, June	vendor@support.com	Email from 2023
Hardware Support
Device	Serial Number	Support Expires	Vendor Support #
Server PROD-01	SN123456	2025-12-31	1-800-XXX-XXXX
SAN Storage	SN789012	2024-06-30 (EXPIRING!)	1-800-XXX-XXXX
Cloud Services
Service	Account	Billing Contact	MFA Recovery
AWS	root@company.com	CFO	Security team email
Azure	admin@company.com	IT	Backup codes in safe
How to Actually Take a Vacation
The real test of your documentation isn't whether someone can replace you - it's whether you can disappear for two weeks without your phone ringing.

The Pre-Vacation Checklist
Two weeks before:

 Identify who will cover while you're gone (even if it's just "call this MSP")
 Walk them through the critical systems
 Test that they can actually access everything they need
 Update the "If I Get Hit By a Bus" document
 Schedule any risky changes for after you return
One week before:

 No new changes. Period. Even "small" ones.
 Verify backups are running and test a restore
 Check disk space on all critical systems
 Review monitoring alerts - are there any that might trigger?
Before you leave:

 Set email auto-reply with contact info for coverage
 Forward critical alerts to your backup person
 Leave your phone number for absolute emergencies only
 Define what counts as an emergency (server down = yes, printer jam = no)
The Coverage Handoff Document
Vacation Coverage Handoff
I Will Be Gone: [Dates]
Who to Contact (In Order)
[Name/Company] - First line of defense
[Name] - For decisions above [First contact]'s level
Me - For absolute emergencies only: [Phone number]
What I've Already Done
 Checked disk space (all OK)
 Verified backups (restored test file successfully)
 Patched critical servers (reboots done)
 No changes scheduled during my absence
Things That Might Break (And What to Do)
If This Happens	Do This	Call Me If
Website down	Restart PROD-WEB-01, see Runbook #2	Not back up in 15 min
Email not sending	Check Microsoft 365 status page	Outage lasts > 1 hour
Can't access files	Check FS-01, restart if needed	Files missing/corrupted
Things That Will Definitely Happen (And Are Fine)
Backup alerts on Sunday night (normal, check logs)
CEO's laptop "slow" (clear browser cache)
Printer jam in accounting (turn it off and on again)
The Quarterly "Knowledge Transfer" Meeting
Even if you're the only IT person, you should have a quarterly meeting with someone - your manager, an MSP, anyone who might need to step in.

Agenda Template
What's changed since last quarter? (New services, retired services, major config changes)
What's keeping you up at night? (Risks, aging hardware, upcoming expirations)
Review the "Bus Factor" document (Is everything still accurate? Any new passwords?)
Walk through one disaster scenario ("If the main server died right now, what would we do?")
Budget/Project updates (What do you need? What's coming up?)
This meeting does two things: it forces you to keep documentation current, and it ensures someone else has context when things go wrong.

Start Today, Not When You're Leaving
The best time to write this documentation isn't your last week on the job. It's right now, while the context is fresh in your mind.

Here's your homework:

This week: Fill out the "If I Get Hit By a Bus" document. Print it. Put it somewhere accessible.
Next week: Start the Services Inventory. Just do Tier 1 (critical systems).
The week after: Add one entry to the "Why" document every time you make a non-obvious configuration change.
This month: Schedule your first quarterly knowledge transfer meeting.
Your future self will thank you. And the next person in your role? They'll thank you even more.

Pro tip: If you want to practice documentation before the pressure is on, check out the Incident Report Generator - it turns your raw notes into professional documentation. Because sometimes you need corporate language to get management to actually pay attention.