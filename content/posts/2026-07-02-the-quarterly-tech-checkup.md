---
title: "The Quarterly Tech Checkup: What to Do When You Visit Your Aging Parent's Phone"
date: 2026-07-02T10:00:00.000Z
categories:
  - Family Tech
  - iOS
  - Accessibility
tags:
  - senior phone maintenance
  - aging parent tech checkup
  - elderly phone check
  - quarterly tech check
  - parent phone emergency
  - senior tech maintenance
  - iPhone troubleshooting elderly
slug: the-quarterly-tech-checkup
description: "A step-by-step quarterly checkup routine for your aging parent's phone. What to check, what to clean up, what to fix — in 20 minutes per visit. Plus an emergency playbook for when something goes wrong between visits."
author: "Pragmatic Sysadmin"
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "The Quarterly Tech Checkup: What to Do When You Visit Your Aging Parent's Phone",
  "description": "A step-by-step quarterly checkup routine for your aging parent's phone. What to check, what to clean up, what to fix — in 20 minutes per visit. Plus an emergency playbook for when something goes wrong between visits.",
  "author": {
    "@type": "Person",
    "name": "Pragmatic Sysadmin"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Pragmatic Tech",
    "url": "https://pragmaticsysadmin.help"
  },
  "datePublished": "2026-07-02",
  "dateModified": "2026-07-02",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://pragmaticsysadmin.help/posts/the-quarterly-tech-checkup/"
  },
  "image": {
    "@type": "ImageObject",
    "url": "https://pragmaticsysadmin.help/images/quarterly-tech-checkup.jpg",
    "width": 1200,
    "height": 630
  },
  "articleSection": "Family Tech",
  "keywords": ["senior phone maintenance", "aging parent tech checkup", "elderly phone check", "quarterly tech check", "parent phone emergency", "senior tech maintenance", "iPhone troubleshooting elderly", "helping parents with phone", "senior phone cleanup", "preventive tech care"],
  "wordCount": "2200"
}
</script>

You set up your mom's phone. You installed the right apps, hid the confusing ones, configured the accessibility settings. You walked her through the emergency gestures and laminated a cheat sheet for her fridge. You did everything right.

Then three months later you visit, and her phone has 47 unread notifications, Location Services is off somehow, the storage is full, and she's been typing her Apple ID password into a phishing site because "it looked like Apple was asking me to verify."

This is normal.

Setting up a phone for an aging parent is like installing a server. The setup matters, but the **maintenance** is what keeps it running. Without it, entropy takes over. Settings drift. Storage fills up. Apps update and rearrange their interfaces. The phone you carefully configured three months ago slowly becomes the phone you didn't configure.

The solution isn't more setup. It's a quarterly checkup — a 20-minute routine you do every time you visit (or remotely, if you can't be there in person). It catches the slow drift before it becomes a crisis. And it gives you a structured way to ask "has anything weird happened?" without making your parent feel like they're being audited.

This post is the fourth in a series. The first three covered the conversations you need to have, the initial phone setup, and the apps worth installing. This one covers what happens *after* the setup — the ongoing care that keeps everything working.

---

## The 20-minute quarterly checkup

Do this every 3 months, or whenever you visit in person. It works in the same order every time so you don't forget a step. Print it, keep it on your phone, whatever works. The consistency matters more than the speed.

### 1. Storage check (2 minutes)

**Settings → General → iPhone Storage**

This is always the first thing I check. Seniors don't delete things. Photos pile up. Apps they opened once sit there. iOS updates require 5+ GB of free space, and if the phone is full, updates fail silently — which means your parent is running unpatched software.

**What to look for:**
- Less than 2 GB free? You need to clean up now.
- "Recommendations" section at the top — iOS will suggest what to delete. Follow the easy ones.
- Photos & Camera taking more than 10 GB? Turn on iCloud Photos (Settings → [Name] → iCloud → Photos → iCloud Photos ON) if you haven't already. This offloads full-resolution photos to iCloud while keeping small versions on the phone. It costs $0.99/month for 50 GB. Worth every penny.

**What to delete:**
- Apps they haven't opened in 3+ months (check the "last used" date in iPhone Storage)
- Old message attachments (Settings → General → iPhone Storage → Messages → review large attachments)
- Any app they don't recognize — ask first, but if they say "what's that?", delete it

**Don't delete:** Photos themselves. Your parent's photos are their memories. Offload them to iCloud instead of deleting them. Deleting photos from a senior's phone without asking is the fastest way to destroy trust.

### 2. Software update (2 minutes)

**Settings → General → Software Update**

Install any pending iOS update. This is non-negotiable. iOS updates patch security holes, and your parent is in the demographic most targeted by exploits. If an update requires a passcode or Face ID that they can't do, that's a separate problem — solve it now, don't defer it.

If "Automatic Updates" is off, turn it on: **Settings → General → Software Update → Automatic Updates → turn on both "Download iOS Updates" and "Install iOS Updates."**

This alone prevents 80% of "my phone is acting weird" calls, because most weird behavior after a certain age is caused by running outdated software that's incompatible with newer versions of apps and websites.

### 3. App updates (2 minutes)

**App Store → tap profile icon → scroll down to see pending updates → "Update All"**

Apps update constantly, and each update can change the interface. Your parent won't notice a new feature, but they *will* notice when a button moved or a menu changed. Updating all apps at once means you can check if anything moved right now, while you're there, rather than having your parent discover it alone at 10pm on a Sunday.

After updating, open the three apps they use most (probably Phone, Messages, and whatever you set as their hub — Buddy, FaceTime, etc.) and confirm they still look and work the same. If an app changed its interface, walk your parent through the new layout once.

### 4. Notification audit (3 minutes)

**Settings → Notifications**

This is where the 47-unread-notifications problem lives. Over three months, apps your parent never intentionally uses will have sent dozens of notifications — news alerts, game prompts, shopping deals, "your order has shipped" from something they don't remember ordering.

**The fix:**
- Go through the notification list. For each app, ask: "Does this app need to buzz your phone?"
- Turn off notifications for anything that isn't a person trying to reach them. That means: Phone, Messages, FaceTime, and their medication app stay ON. Everything else — news, shopping, games, social media — turn off banners, sounds, and badges.
- The exception: if your parent actively uses and enjoys an app's notifications (e.g., they like getting Wordle reminders), leave it. But ask first. Most seniors don't know they can turn notifications off and just live with the noise.

The goal: **a phone that only buzzes when it matters.** Every unnecessary notification trains your parent to ignore their phone, which means they'll ignore the *important* notification too.

### 5. Security sweep (3 minutes)

This is the most important part of the checkup. It catches the things your parent won't think to tell you.

**Check Safari for strange tabs:**
- Open Safari → tap the tabs icon (two overlapping squares)
- Close anything that looks like an ad, a pop-up, or a login page they don't recognize
- Common red flags: tabs with "Apple ID Verification," "Your iPhone is Infected," or any site asking for a password

**Check for unfamiliar apps on the home screen:**
- Swipe through all home screens. Ask about anything you don't recognize.
- If they say "I don't know what that is" or "it just appeared," delete it.
- Some scam sites install web clips (Safari shortcuts that look like apps). Long-press → "Remove App" → check if it says "Delete Web Clip" — if so, it was never a real app.

**Review recent app installations:**
- App Store → profile icon → look at "Updated Recently" — if there are apps here you didn't install and your parent didn't intentionally install, delete them and check the App Store purchase history for unexpected charges.

**Check Screen Time hasn't been disabled:**
- Settings → Screen Time — if it's off and you turned it on, someone (or some scam) may have talked your parent into disabling it. Re-enable it with the passcode only you know.

**Review saved passwords for breaches:**
- Settings → Passwords — iOS will flag compromised passwords with a yellow warning triangle. If you see any, change those passwords immediately. This is also a good time to confirm your parent is using the built-in password manager (Apple Passwords) instead of writing passwords on paper or reusing the same one everywhere.

### 6. Settings drift check (3 minutes)

Over time, settings change. Sometimes your parent changes them accidentally. Sometimes an iOS update resets them. Sometimes a scam walks them through changing something.

**Quick-check these critical settings:**

| Setting | Where | What it should be |
|---------|-------|-------------------|
| Silence Unknown Callers | Settings → Phone | ON |
| Find My iPhone | Settings → [Name] → Find My | ON |
| Face ID | Settings → Face ID & Passcode | Working (test it) |
| Auto-Lock | Settings → Display → Auto-Lock | 2-5 minutes (not Never) |
| Medical ID "Show When Locked" | Health → Medical ID → Edit | ON |
| Back Tap (Double Tap → Home) | Settings → Accessibility → Touch → Back Tap | Home Screen |
| Screen Time | Settings → Screen Time | ON with your passcode |

Run through this list. If anything has drifted, fix it and make a mental note — a setting that keeps reverting might mean your parent is accidentally changing it, which means you need to find the gesture or menu path that's causing the problem and block it.

### 7. Ask the three questions (5 minutes)

This is the part that matters most, and it's the part most people skip because it feels awkward. But these three questions — asked gently, without judgment — will tell you more about your parent's tech life than any settings audit.

**Question 1: "What's been confusing lately?"**

Don't ask "has anything been confusing?" — that gives them an easy out. Ask "what's been confusing" and wait. They'll think of something. Everyone has something. When they tell you, don't fix it immediately. Ask them to show you what happened. Watch where they get stuck. The place they get stuck is the place your setup needs to be simpler.

**Question 2: "Has anyone called or messaged you asking for money or information?"**

Ask this every time. Don't assume that because you had the scam conversation once, it's handled. Scammers are persistent and creative. Your parent may have forgotten the conversation, or a new type of scam may have come along that sounds more convincing than the last one.

If they say yes, stay calm. Don't panic, don't lecture. Ask: "What did they say? Did you give them anything?" If they did give information, go straight to the emergency playbook below. If they didn't, reinforce: "You did the right thing by not giving them anything. I'm glad you told me."

**Question 3: "Is there anything you wish the phone could do that it doesn't?"**

This question catches the things your parent is struggling with silently. They may not know how to video-call the grandkids. They may be squinting at text that's still too small. They may want to listen to audiobooks but not know how. Whatever it is, this is your chance to add one thing that genuinely improves their life — not just prevents problems, but creates joy.

---

## The remote checkup (when you can't visit)

If you live far away, you can do most of this remotely using a few built-in tools.

**Find My** — You can check your parent's phone location from your own iPhone (Find My app → Devices → their phone). This doesn't tell you about their phone's health, but it tells you the phone is on and has a data connection.

**Family Sharing** — If you've set up Family Sharing (Settings → [Name] → Family Sharing), you can:
- See their screen time reports remotely
- Approve or deny app downloads
- Share subscriptions (Apple Music, iCloud storage)
- Set up Ask to Buy so they can't install apps without your approval

**Shared Calendar** — Set up a shared Google Calendar or Apple Calendar. Add their doctor's appointments, your visits, and reminders like "Quarterly tech checkup — call [your name]."

**FaceTime walk-through** — Call them on FaceTime and ask them to show you their home screen, their notifications, their Safari tabs. It's not as thorough as doing it in person, but it catches the biggest issues. Guide them through the checkup steps over video.

**The Buddy app** — If you set up [Buddy](https://pragmaticsysadmin.help/buddy/) on their phone, you can ask them to open it and tap "How-To" for guided walkthroughs of common tasks. If they're stuck, the How-To section has step-by-step instructions for things like "how to make a phone call" and "how to send a photo." It's not a replacement for you, but it's a safety net for the times you're not available.

---

## The emergency playbook

Sometimes things go wrong between checkups. Here's what to do in the most common emergencies.

### "My phone is frozen / acting weird"

1. **Force restart:** Press and quickly release Volume Up, then Volume Down, then hold the Side Button until the Apple logo appears (10-15 seconds). This fixes 90% of "weird" behavior.
2. **If that doesn't work:** Connect to a computer with a USB cable and check if the computer recognizes the phone. If it does, the phone is alive but the screen may be unresponsive. If the computer doesn't see it either, the phone may have a hardware problem — time to visit an Apple Store or authorized repair shop.
3. **Check storage after restart:** A phone that's completely full will behave erratically. If storage was the trigger, do the storage cleanup steps above immediately.

### "I think I clicked something bad"

1. **Don't panic.** Most "I clicked a bad link" situations don't result in actual compromise, especially on iPhones, which are sandboxed. But you should still check.
2. **Close the tab:** Open Safari → tabs icon → close any tab that looks suspicious.
3. **Check for new profiles:** Settings → General → VPN & Device Management. If there's a profile here you don't recognize, delete it immediately. Scam sites sometimes try to install configuration profiles that redirect web traffic.
4. **Check for web clips:** Long-press any unfamiliar app icon. If it says "Delete Web Clip," it was installed by a website, not the App Store. Delete it.
5. **Change their Apple ID password** if they entered it anywhere suspicious. Do this from YOUR device: [appleid.apple.com](https://appleid.apple.com) → sign in → Change Password. Then update it on their phone.
6. **Check for unauthorized purchases:** App Store → profile → Purchase History. If you see charges you don't recognize, [report them to Apple](https://reportaproblem.apple.com).

### "I got a call from Microsoft / the IRS / the bank"

1. **It's a scam. 100% of the time.** Microsoft does not call people. The IRS does not call people. Your bank will never ask you to verify your password over the phone.
2. **If they didn't give any information:** No action needed. Reinforce the rule: "If someone calls saying they're from Microsoft or the bank, hang up. You can always call the bank back using the number on your card."
3. **If they gave information or installed something:** Go to the "I think I clicked something bad" playbook above. Then:
   - Call the bank and freeze the account if any financial info was shared
   - Change the Apple ID password
   - Check for configuration profiles (Settings → General → VPN & Device Management)
   - Run a full check of saved passwords for any that were shared

### "My phone was lost or stolen"

1. **Open Find My on YOUR phone** → Devices → their phone → Mark as Lost
2. This locks the phone with a passcode and displays a custom message with your phone number
3. If the phone is nearby, tap "Play Sound" — it will ring at full volume even if on silent
4. **Do NOT tap "Erase This Device" yet** — you can't undo it, and it removes the ability to track the phone
5. If the phone doesn't appear in Find My at all, it's either turned off or not connected to the internet. Check "Notify When Found" — you'll get an alert when it comes back online
6. **Report it to the carrier** — they can suspend the SIM to prevent unauthorized calls and charges
7. **If it was stolen:** File a police report. You'll need it for insurance claims and for disputing any fraudulent charges

### "I forgot my passcode"

This is the hardest emergency because Apple designed it to be — the passcode is the key to everything, and if it's lost, the only option is a full device wipe.

1. **Try the passcode a few more times.** Sometimes it's a finger-position issue, not a memory issue. Have them try slowly and deliberately.
2. **If Face ID is set up**, the phone might accept Face ID instead. Try that first.
3. **If it's truly forgotten:** You'll need to put the phone into Recovery Mode and restore it from a computer. This erases everything. If they have an iCloud backup, the data can be restored during setup. If they don't, it's gone.
4. **Prevention:** Write the passcode on a card and keep it in a secure place at their home (not in their wallet, not in the phone case). Tell them: "This card is your backup. If you ever forget the code, look here."

---

## Making the checkup sustainable

The quarterly checkup only works if you actually do it. Here's how to make it a habit.

**Set a recurring calendar event.** Every 90 days, on a day you'd normally visit or call. Title it: "Mom's phone checkup — 20 min." Set a reminder for 1 hour before so you can prepare.

**Combine it with something else.** Do the checkup right after Sunday dinner, or while you're both having coffee, or during a regular FaceTime call. Don't make it a separate "appointment" — that makes it feel like a chore for both of you.

**Keep notes.** After each checkup, jot down what you found and what you fixed. I use a note on my phone titled "Mom's phone" with dates and bullet points. After a year, you'll see patterns — "storage always fills up in month 3" or "she keeps turning off Silence Unknown Callers." Patterns tell you where the setup needs to be simpler, not where your parent needs to be "better."

**Don't over-engineer.** The biggest temptation during a checkup is to add new things — a new app, a new automation, a new shortcut. Resist it. Every addition is one more thing that can break or confuse. The best quarterly checkup is the one where you find nothing wrong and leave everything exactly as it was.

---

## The full senior-tech series

This post is part four of a series on helping aging parents with technology. If you haven't read the others, start at the beginning:

1. **[5 Conversations to Have with Your Aging Parent About Online Safety](/posts/5-conversations-aging-parent-online-safety/)** — the conversations that prevent scams before they happen.
2. **[How to Set Up an iPhone for an Elderly Parent](/posts/setup-iphone-elderly-parent/)** — the 30-minute setup that prevents 90% of support calls.
3. **[The Best Free Phone Apps for Seniors in 2026](/posts/best-free-phone-apps-seniors/)** — the mom-tested list of apps worth installing.
4. **The Quarterly Tech Checkup** — this post. The maintenance routine that keeps everything working.

**Want a printable version?** I made a [Senior Phone Setup & Maintenance Checklist](https://ko-fi.com/s/c26d7c8a0c) that covers all four posts in one place — initial setup, quarterly checkup steps, and the emergency playbook. Laminate it, keep it in your bag, and you'll never forget a step.

---

*Setting up a phone for an aging parent? [Try Buddy](https://pragmaticsysadmin.help/buddy/) — it's the only app that goes on the home screen. Free, accessible, designed specifically for non-techies.*

*Read next: [5 Conversations to Have with Your Aging Parent About Online Safety](/posts/5-conversations-aging-parent-online-safety/)*
