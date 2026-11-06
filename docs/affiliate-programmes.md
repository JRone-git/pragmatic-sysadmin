# Affiliate programmes — what to apply for, and why

**Status date: 2026-11-06.** Every rate and rule below was checked against the
programme's own site on that date. Rates change; re-check before you quote them
in a post.

---

## The short version

| # | Programme | Pays | Cookie | Payout floor | Fit | Effort |
|---|-----------|------|--------|--------------|------|--------|
| 1 | **Newegg** (via Rakuten) | varies by category | 7 days | — | **Excellent** | 10 min |
| 2 | **DigitalOcean** | 10% of spend for 12 months | 30 days | — | **Excellent** | 10 min |
| 3 | **SiteGround** | $50 → $100+/sale | 60 days | none, weekly | Good | 15 min |
| 4 | **eBay Partner Network** | 1–4% + bonuses | 24h–7d | — | Good | 15 min |
| 5 | **Vultr** | $10/account | 30 days | — | Good | 10 min |
| 6 | **Amazon Associates** | 1–10% by category | **24 hours** | $10 | Weak | 20 min |
| 7 | **Bluehost** | $65/sale | 30 days | $10 | **Poor** | 10 min |
| 8 | **1Password / Lively / Consumer Cellular / Bay Alarm / Backblaze** | $5–25 each | varies | varies | Good | 5 min each |

Three of these need your identity, tax details and a bank account, so **you** have
to click through and sign up. Everything else — the config, the links, the
disclosure text — is already done and waiting for the code.

---

## 1. Newegg — the cheapest win, because the plumbing is already installed

**Do this first.** It is the only one where the site is already 100% wired up.

The Rakuten Automate widget (`widgetKey 7LPHGCV9BUkW9tlD8KQFcwkPMqUmzwsW`) is
installed and loading. It rewrites plain `newegg.com` links into tracked links
**on click** — you do not have to change a single URL. There are **40 Newegg
links** across 7 posts.

But Rakuten's own help centre is explicit about why they earn nothing today:

> "If a link is not being affiliated, first check that you are partnered with
> that advertiser." — [Rakuten Automate troubleshooting](https://pubhelp.rakutenadvertising.com/hc/en-us/articles/7494855698061-Automate-Overview)

Your Rakuten account is **not yet partnered with Newegg**. That is the only
missing piece.

**Steps**

1. Go to the [Rakuten Advertising publisher dashboard](https://pubhelp.rakutenadvertising.com/hc/en-us/categories/200113518-Publisher-Dashboard)
   → **Advertisers** → search **Newegg** → **Apply**.
2. Fill in the site URL: `https://pragmaticsysadmin.help/`
3. Describe how you promote it: *"A practical tech blog for sysadmins and
   family caregivers. I write buying guides for senior-friendly phones,
   routers and tablets, plus honest homelab and self-hosting guides. Product
   recommendations are based on devices I have tested."*
4. Rakuten also has a direct route — [Newegg's affiliate page](https://promotions.newegg.com/affiliate_program/affiliate.html)
   says sign-up is through their Rakuten partnership and the application is
   reviewed manually.
5. When approved, **nothing in the code changes.** Set
   `"status": "applied"` for `newegg` in `catalog/affiliates.json`, rebuild, and
   the 40 links start earning and the disclosure appears by itself.

**Which links pay.** Newegg pays nothing on cell phones, TVs, video games and
consoles. That matters here: the iPhone SE link earns nothing, but the
routers, tablets, monitors, hard drives, RAM and SSDs do. Consumer Electronics
sits around 1–2% for publishers.

**Note on the 7-day window.** Newegg's attribution window is 7 days against
Amazon's 24 hours. On a product roundup where a reader browses for a week and
then buys, Newegg is the better bet than Amazon.

**The evidence, measured.** A headless browser was pointed at the live site
and a real Newegg link clicked. The Rakuten widget does fire — it calls

```
https://automate.linksynergy.com/click?origin=…&link=https://www.newegg.com/p/2E3-010D-00308&widget_key=7LPHGCV9BUkW9tlD8KQFcwkPMqUmzwsW&err_code=2&domain=newegg.com
```

— and then sends the reader to `https://www.newegg.com/p/2E3-010D-00308` with
**no referral parameter at all**. The same happens for amazon.com, ko-fi.com
and lively.com: `err_code=2` every time, no affiliate link created, plain
destination.

So the widget is not broken. It is doing exactly what it is supposed to do
with an account that has no advertiser partnership behind it. Forty clicks a
month on Newegg product links, and every one of them currently earns nothing.


---

## 2. DigitalOcean — best economics for this audience

Your readers are self-hosters. They run their own servers. DigitalOcean is the
one product they actually buy.

- **Affiliate programme:** **10% of the referred customer's spend for 12
  months**, via Awin. That is real recurring money, not a one-off.
- **Referral programme:** the referrer gets **$25 of account credit** (not cash);
  the referred account gets **$200 of credit for 60 days**, which only applies
  when they arrive through your referral link.
- These need **different codes**.

**Steps**

1. [DigitalOcean referral programme](https://www.digitalocean.com/referral)
   — personal account, instant, no review. Paste the code into
   `catalog/affiliates.json` under `digitalocean` and set
   `"param": "ref"`.
2. [DigitalOcean affiliate programme](https://www.digitalocean.com/affiliates)
   — 10% for 12 months, via Awin. Needs a tax form and a bank account.
3. The `$200 for 60 days` line in the post is **only true for referral-link
   arrivals**. It is generated from the config, so it appears the moment the
   code is in and stays hidden until then.

**Where it plugs in:** one link on the Resources page, `content/resources/_index.md`.

---

## 3. SiteGround — the hosting programme that actually fits

Bluehost is WordPress shared hosting. Your readers already run servers. If you
promote a host at all, promote one that sells VPS and cloud.

- **$50 per sale** for 1–5 sales/month, **$75** for 6–10, **up to $100** for
  11–20, custom above 21. [Rate card](https://www.siteground.com/kb/affiliate_program_earnings)
- **60-day cookie**, 30-day holding period.
- **Paid weekly with no minimum threshold** — the only programme here that pays
  on a single sale without a floor.
- **Catch:** the referred customer has to keep the account **active for 30 days**
  (multi-month terms) or **90 days** (monthly terms) before the sale validates.
  A cancellation or refund voids it.
- **Disclosure is mandatory** — the site's generated disclosure covers this.

**Steps:** [siteground.com/affiliates](https://www.siteground.com/affiliates).
Paste the `afcode` into `catalog/affiliates.json`.

---

## 4. eBay Partner Network — the rescued Harmony Elite link

The Resources page links to a **refurbished Logitech Harmony Elite on eBay**
because Logitech discontinued the model. That is a genuinely useful link for
someone whose parent has four remotes, and it is one click from earning.

- **1–4%** depending on category, plus a bonus on the top categories.
- eBay runs bonus promotions roughly every fortnight — a burst of promo codes
  raises the rate for a limited window.

**Steps:** [ebay.com/us/help/selling/earned-recommendations](https://www.ebay.com/us/help/selling/earned-recommendations) →
join the programme → get your campaign ID → paste into `catalog/affiliates.json`.

---

## 5. Vultr — cheap, fast, fits the homelab audience

- **$10 per paid account**, 30-day cookie, direct programme with no network in
  between, so no cut taken by an intermediary.
- Two Vultr links already sit in the Kubernetes post and the cloud-spend post.

**Steps:** [vultr.com/affiliate](https://www.vultr.com/affiliate/) →
`referral` code → paste into `catalog/affiliates.json`.

---

## 6. Amazon Associates — apply, but expect it to fail

**The rule you need to know before you start.** Amazon's own programme text:

> "You have 180 days to refer a sale… Once you have referred three qualifying
> sales, we'll evaluate your application within a day or two."

If three sales have not happened in 180 days, the account is **withdrawn** and
the Associates ID **cannot be reinstated**. It is one shot.

**Your traffic.** Search Console for Jun 26 – Aug 15 2026: 14 clicks, 1,626
impressions, 0.86% CTR, average position 25.0. Roughly 0.2 clicks a day. You
need three *purchases* in six months off that. The odds are poor.

**Other rules that bite:**

- The cookie is **24 hours**. Amazon's own documentation recommends adding a
  disclaimer like *"As an Amazon Associate I earn from qualifying purchases."*
  — which the generated disclosure does.
- Only your **own** purchases count. You may not buy your own products, and you
  may not ask friends and family to buy them either; that voids the account.
- You need **10 substantial original posts**, a privacy policy, and content
  updated within the last 60 days. The site clears all three easily — 52
  published posts, a privacy page, and constant new material.
- **Qualifying categories** for this site: consumer electronics 4%, computers
  2.5%, camera/photo 3%, video games 8%, DVDs 4.5%, toys 3%, musical
  instruments 2%, kitchen 4%, furniture 3%. **Books, groceries and most
  clothing are excluded.**

**Recommendation:** apply anyway — it costs fifteen minutes and the store ID
is useful for Audible too — but put the real effort into Newegg, whose 7-day
window beats Amazon's 24 hours for a considered purchase, and into DigitalOcean,
whose 12-month recurring commission is worth more than a 4% one-off.

**Steps:** [affiliate-program.amazon.com](https://affiliate-program.amazon.com)
→ sign in → create a Store ID → paste the ID into `catalog/affiliates.json`
as `code` with `param: tag`.

---

## 7. Bluehost — skip it

- $65 per qualified sale, 30-day cookie, paid through Impact.

**Two reasons to skip.** First, the fit is wrong: Bluehost sells shared
WordPress hosting, and your readers run their own servers. Second, Bluehost's
own programme says applications get declined when the site *"lacks sufficient
traffic"* — with 0.2 clicks a day, that is a likely outcome. The Impact payout
table also pays only 70% of the order on orders under $23, so the "$65" is not
always $65.

Leave the entry in `catalog/affiliates.json` at `not-applied` and revisit if
the traffic ever moves.

---

## 8. The small ones — five minutes each

These have the best commission-per-click in the whole list and the shortest
application forms. Batch them into one sitting.

| Programme | Network | Pays | Where it plugs in |
|---|---|---|---|
| **Lively** | **CJ Affiliate** | **$25+ per device**, 45-day cookie | 7 links, senior phone roundups |
| **Consumer Cellular** | varies | CPA per activation | 3 links, phone roundups |
| **1Password** | **Impact** | ~$5–10 per sale | Resources page |
| **Bay Alarm Medical** | in-house | recurring, `?affiliate_id=rr_<id>` | Resources page |
| **Backblaze** | in-house | ~$5 per customer | 2 links, homelab + backup posts |

**Two networks, five programmes.** Lively and Bluehost are on **CJ Affiliate**;
1Password is on **Impact**; DigitalOcean is on Awin or CJ depending on the
route you take. Bay Alarm and Backblaze are in-house, so they need no network
at all — just an approval and a link format.

CJ and Impact each need one account, one tax form and one payout method, and
then each advertiser inside them is a separate application. That is why the
small ones are worth batching: it is one afternoon, not five.

**Lively is the best of the lot.** $25 per device sale with a 45-day cookie and
unlimited referrals, and the audience is literally "an adult child buying a
phone for a parent". That is a $89.99 device with a $25/month service attached
to it, and it is a conversion that happens in a week, not a quarter.

Careful with Lively: **the commission is per device, and only on the devices
in the programme** (Jitterbug Flip2, Jitterbug Smart4, Lively Mobile2). A
reader who buys a plain smartphone through the Lively site earns you nothing,
so link the device pages, not the homepage.

---

## The other thing that already earns

**Ko-fi** — `https://ko-fi.com/sysadmin_dad`, five links, live and working.
Donations, not commission, so it is excluded from the commission disclosure.
Ko-fi pays out at $5. If it ever out-earns every affiliate programme
combined, that is the real lesson.

---

## How to add a code

One file. One line. Then rebuild.

`catalog/affiliates.json`:

```json
"digitalocean": {
  "name": "DigitalOcean",
  "url": "https://digitalocean.com",
  "param": "ref",
  "code": "PASTE-YOUR-CODE-HERE",
  "status": "applied",
  ...
}
```

Set `"status": "applied"` and the link starts carrying tracking, the per-link
claim appears, and the page disclosure names the programme — all from the same
value, so they cannot disagree with each other.

**`scripts/check-affiliate-links.py` runs on every deploy** and fails the build
if any page promises a commission on a link that earns nothing. Run it locally
before you push:

```
python scripts/check-affiliate-links.py public
```

---

## What this site actually earns today

| Programme | Links | Earning? |
|---|---|---|
| NordVPN | 3 | **Yes** — `aff_id=143264` |
| NordPass | 1 | **Yes** — `aff_id=143264` |
| Ko-fi | 5 | **Yes** — donations |
| Newegg | 40 | No — Rakuten partnership pending |
| Lively | 7 | No — no code |
| Amazon | 3 | No — not applied |
| Consumer Cellular | 3 | No — no code |
| Vultr | 2 | No — no code |
| Backblaze | 2 | No — no code |
| Audible | 1 | No — no separate programme |
| 1Password | 1 | No — no code |
| Bay Alarm | 1 | No — no code |
| DigitalOcean | 1 | No — no code |
| eBay | 1 | No — no code |
| Hetzner | 1 | No — no programme |

**72 affiliate links. 4 earn a commission. 5 more are donations. 63 earn nothing.**

That ratio is the actual state of the site, and until this morning nobody
could have seen it, because the disclosure was hand-written prose listing
programmes the site was not enrolled in.

---

## How the link modes work

`catalog/affiliates.json` gives every merchant a `mode`:

| Mode | What it does | Used by |
|---|---|---|
| `param` | Appends `?param=code` to the URL | DigitalOcean, SiteGround, Bluehost, Vultr, Amazon, eBay |
| `url` | The code is already baked into the URL; the checker verifies it is still there | NordVPN, NordPass |
| `widget` | Tracking is done by the Rakuten Automate widget on click — do **not** add a parameter, a second one breaks it | Newegg |
| `direct` | A plain link to somewhere that earns nothing and never will | Ko-fi, Hetzner, Audible, Lively, Consumer Cellular, Bay Alarm, Backblaze, 1Password |

And a `status`:

| Status | Meaning |
|---|---|
| `applied` | The code is in place and working. The link tracks, the claim appears, the disclosure names it. |
| `pending` | Applied for, waiting on approval. The link still works, it just earns nothing yet. |
| `not-applied` | Not applied for. The link works, it earns nothing, and the site says so. |

`kind: "donation"` marks a link that earns money but is not a commission
programme. Ko-fi has it, so the disclosure never claims a "commission" from
your readers' donations.
