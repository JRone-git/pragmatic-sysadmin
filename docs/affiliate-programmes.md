# Affiliate programmes — what to apply for, and why

**Status date: 2026-11-24.** Every rate and rule below was checked against the
programme's own site on that date. Rates change; re-check before you quote them
in a post. Section 1 (Taobao) and the Newegg widget evidence were measured
directly against the live account rather than read off a help page.

---

## The short version

| # | Programme | Pays | Cookie | Payout floor | Fit | Effort |
|---|-----------|------|--------|--------------|------|--------|
| 0 | **Taobao** (via Rakuten, **already applied**) | per product | 7 days | — | **Excellent** | 5 min |
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

---

## 1. Taobao — already approved, and the only programme that works today

**State: applied.** The Rakuten account shows **Taobao, MID 54014, `Partnered`**,
with links running since October 2025. Nothing is pending. This is the one
programme on this page you already have.

**Everything below was measured on 2026-11-24**, not read off a help page.

| Fact | Value |
|---|---|
| Publisher id | `9bfb/6Q9Df4` |
| Taobao offer | `2095036` |
| Tracked link | `https://click.linksynergy.com/fs-bin/click?id=9bfb%2f6Q9Df4&offerid=2095036.<linkid>&type=3&subid=0` |
| Where it lands | `world.taobao.com/wow/z/oversea/gam/ovs-affiliate-pdp?itemId=…&pid=mm_…&relationId=…` |
| Impression pixel | `https://ad.linksynergy.com/fs-bin/show?id=9bfb%2f6Q9Df4&bids=2095036.<linkid>&type=3&subid=0` → 200, `image/gif` |

**The offerid link id is not the product.** It is a Rakuten-side record; the
product itself lives in Rakuten's database and is resolved server side on click.
Registered ids (18–49) resolve to their own item. An **unregistered id falls
back to the Taobao Global storefront** — still attributed, still paid, but the
reader lands on the shop instead of the item. It fails silently.

**Taobao does not allow deep linking through Rakuten.** `…/deeplink?id=…&mid=54014&murl=…`
ignores `murl` completely and always lands on the storefront, whatever you put
in it. A registered offerid link id is the only way to point at a product.

**Taobao's own short links are already attributed.** `https://intl.taobao.com/sk/_b.XXXX`
redirects to the affiliate product page with the `pid` intact — with or without
the Rakuten wrapper. The wrapper adds Rakuten's own click report and does not
break the Taobao layer.

**Steps**

1. Rakuten dashboard → **Links** → **Link Tools** → **Link Locator** → search the
   Taobao catalogue for the product you want to link.
2. Take the link id from the result and build the link:
   `python3 scripts/rakuten-link.py build 49`
3. Put it in the post:
   `{{< aff merchant="taobao" link="49" text="the reflective TFT panel" >}}`
4. `scripts/check-affiliate-links.py` **fails the build** if the link id is
   missing and the `{link}` placeholder ships unsubstituted — a Taobao link
   without its id is a link to the wrong thing.

**Check any link before you publish it:**
`python3 scripts/rakuten-link.py resolve "<url>"` follows the whole chain and
prints the `itemId` and `pid` it lands on.

---

## 2. Newegg — the plumbing is installed, and the widget is dead

**Do this first.** It is the only one where the site is already 100% wired up.

The Rakuten Automate widget (`widgetKey 7LPHGCV9BUkW9tlD8KQFcwkPMqUmzwsW`) is
installed and loading. It rewrites plain `newegg.com` links into tracked links
**on click** — you do not have to change a single URL. There are **40 Newegg
links** across 7 posts.

But Rakuten's own help centre is explicit about why they earn nothing today:

> "If a link is not being affiliated, first check that you are partnered with
> that advertiser." — [Rakuten Automate troubleshooting](https://pubhelp.rakutenadvertising.com/hc/en-us/articles/7494855698061-Automate-Overview)

Your Rakuten account is **not yet partnered with Newegg**. But that turns out
**not** to be the only missing piece — see the evidence at the bottom of this
section. The widget matches **no merchant at all**, including Taobao, which is
already partnered.

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

**But that is not the whole story, and this section was wrong before.** On
2026-11-24 the widget was measured properly: the live site was loaded in a
headless browser, a real Newegg link on the Plex post was clicked, and the
console was read.

```
Automate is initialized.
Original: https://www.newegg.com/p/pl?d=intel+n100+mini+pc, Matched: null
Failure. No merchant.
```

**"No merchant" — not "no relationship".** The widget resolved *nothing* for
*every* domain tried: newegg.com, amazon.com, aliexpress.com, taobao.com,
ebay.com, etsy.com, walmart.com, bhphotovideo.com, adorama.com, microcenter.com,
ikea.com, backblaze.com, digitalocean.com, siteground.com and proton.me. All
sixteen produced the same `err_code=2` and the same plain destination.

The widget key resolves at `automate-prod.storage.googleapis.com/info/<key>` to
publisher `esid 9bfb/6Q9Df4` — and that **is** the publisher id in the site's
own link code, so the widget is not bound to a stale account. It is simply
matching no merchant.

Rakuten's own troubleshooting says to wait 24 hours after a relationship
change and then contact support. Taobao has been partnered since October 2025,
so the 24 hours have long passed. **This is a support ticket**, not something
Newegg's approval fixes.

**Send Rakuten publisher support these five facts:**

> Widget key `7LPHGCV9BUkW9tlD8KQFcwkPMqUmzwsW`, publisher id / esid
> `9bfb/6Q9Df4`, site `pragmaticsysadmin.help`. Every outbound link logs
> `Failure. No merchant.` and is rewritten with `err_code=2` — including
> `taobao.com` (MID 54014), which is `Partnered` on my account. Same result on
> Newegg, Amazon, AliExpress and thirteen other domains. The widget loads and
> the wakeup call returns 200.

**Meanwhile, do not rely on the widget.** There is a second path that works
today and needs no support ticket: build the link by hand with
`scripts/rakuten-link.py` (see the Taobao section) and put the tracked URL
straight into the post. Until the widget is fixed, every hand-written link is
the only kind that earns.

**Forty-nine links on Newegg product pages, and every one of them currently
earns nothing** — not because Newegg has not approved the account, but because
the mechanism that would have tracked them matches nothing.


---

## 3. DigitalOcean — best economics for this audience

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

## 4. SiteGround — the hosting programme that actually fits

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

## 5. eBay Partner Network — approved, and the fastest approval of the lot

**State: approved.** eBay says *"You'll receive a notification when your
application has been approved, usually within just a few hours"*, and *"What
should I do if your eBay Partner Network application is still pending after 24
hours?"* — there is a published 24-hour SLA. This one went through in hours.

**Why it matters here.** eBay carries the cheap Chinese hardware the site keeps
recommending, and the European marketplaces count:

> Participating Sites and Content: ebay.com, ebay.de, ebay.co.uk, ebay.fr,
> ebay.it, ebay.es, ebay.nl, ebay.at, ebay.be, ebay.ch, ebay.ie, ebay.pl

- **1–4% of the sale price**, plus the 0% final-value-fee seller credit
- **24-hour cookie, last-click** attribution
- Paid **monthly on the 10th**, **$10 threshold**
- Not commissionable: gift cards, charity items, real estate

**The link format**, from eBay's own EPN documentation:

```
[TARGET][?|&]mkevt=1&mkcid=1&mkrid=[ROTATION-ID]&campid=[EPN-CAMPAIGN-ID]&toolid=[TOOL-ID]&customid=[SUB-ID]
```

The target changes per product; the tracking does not. So the account values
live **once** in `catalog/affiliates.json` and every link is built from them —
no hand-editing six parameters into a URL.

**Your account values, measured 2026-11-25 from eBay's own Smart Tools
script:**

| Value | |
|---|---|
| `campid` | **5339259773** — your EPN campaign id, the parameter that makes a link yours |
| `toolid` | **20001** — the Smart Tools id (the Link Generator's own default is 10001) |
| `customid` | `link` for links, `page` for impressions |

**The rotation id and site id are per marketplace**, and they are *not*
guessable. eBay's own `epn-smart-tools.js` carries the table; it was lifted
verbatim from there:

| Marketplace | mkrid | siteid | | Marketplace | mkrid | siteid |
|---|---|---|---|---|---|---|
| ebay.com | 711-53200-19255-0 | 0 | | ebay.de | 707-53477-19255-0 | 77 |
| ebay.ca | 706-53473-19255-0 | 2 | | ebay.it | 724-53478-19255-0 | 101 |
| ebay.co.uk | 710-53481-19255-0 | 3 | | ebay.nl | 1346-53482-19255-0 | 146 |
| ebay.com.au | 705-53470-19255-0 | 15 | | ebay.es | 1185-53479-19255-0 | 186 |
| ebay.at | 5221-53469-19255-0 | 16 | | ebay.ch | 5222-53480-19255-0 | 193 |
| ebay.be | 1553-53471-19255-0 | 23 | | ebay.ie | 5282-53468-19255-0 | 205 |
| ebay.fr | 709-53476-19255-0 | 71 | | ebay.pl | 4908-226936-19255-0 | 212 |

A first attempt guessed these from the pattern, and it was **wrong for eight
of the fourteen** — ebay.fr is `709-53476`, not `709-53480`; ebay.es is
`1185-53479`, not `706-53476`. A link with the wrong rotation id looks
perfectly correct and attributes to nobody. The table now lives in
`catalog/affiliates.json` and comes straight from eBay's script.

**One command and you are live:**

```bash
python3 scripts/ebay-link.py build "https://www.ebay.de/itm/302266213227?var=601108617967"
python3 scripts/ebay-link.py verify "<the link>"
```

`build` produces a correctly tracked link for any eBay URL, picking the
rotation id and site id that match the marketplace. `verify` proves a link
carries this site's own campaign id rather than one pasted in from somewhere
else.

**And eBay's Smart Tools script is installed too**, in
`layouts/partials/extend_head.html`:

```html
<script>window._epn = {campaign: 5339259773, smartPopover: false};</script>
<script src="https://epnt.ebay.com/static/epn-smart-tools.js" async></script>
```

Measured in a headless browser on the built page:

- The script loads and fires an **impression** pixel to
  `ebayadservices.com/marketingtracking/v1/impression?...campid=5339259773&toolid=20001`
  — so eBay counts the *view*, not only the click
- It **normalises** a link that already carries the parameters instead of
  duplicating them, so the two mechanisms coexist
- It leaves non-eBay links alone
- `smartPopover: false` switches off the mobile share bubble. The rewriting
  still works with it off.

That means the links work **with JavaScript disabled** (they carry the
parameters in the source) *and* pick up impression tracking when it runs.

**In a post:** `{{< aff merchant="ebay" url="https://www.ebay.de/itm/..." text="the Harmony Elite" >}}`

**What to link to eBay rather than Newegg.** The 16 commodity Newegg links —
4× 1TB NVMe SSD, 2× Raspberry Pi 5, the Waveshare 3.2" LCD, the Intel N100
mini PC, external drive, USB hub, keyboard, managed switch, monitor, UPS —
are all better served by eBay, and eBay also carries the Waveshare
**ESP32-S3-RLCD-4.2** board that the wall-display series is built around.

**One honest caveat:** eBay is full of 4.2" **e-paper** panels at $15–45, but
the **reflective TFT** (ST7306) that this build actually needs is rare there.
The cheapest reflective TFT is the AliExpress listing at $3.57.

The Resources page links to a **refurbished Logitech Harmony Elite on eBay**
because Logitech discontinued the model. That is a genuinely useful link for
someone whose parent has four remotes, and it is one click from earning.

- **1–4%** depending on category, plus a bonus on the top categories.
- eBay runs bonus promotions roughly every fortnight — a burst of promo codes
  raises the rate for a limited window.

**Steps:** [ebay.com/us/help/selling/earned-recommendations](https://www.ebay.com/us/help/selling/earned-recommendations) →
join the programme → get your campaign ID → paste into `catalog/affiliates.json`.

---

## 6. Vultr — cheap, fast, fits the homelab audience

- **$10 per paid account**, 30-day cookie, direct programme with no network in
  between, so no cut taken by an intermediary.
- Two Vultr links already sit in the Kubernetes post and the cloud-spend post.

**Steps:** [vultr.com/affiliate](https://www.vultr.com/affiliate/) →
`referral` code → paste into `catalog/affiliates.json`.

---

## 7. Amazon Associates — apply, but expect it to fail

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

## 8. Bluehost — skip it

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

## 9. The small ones — five minutes each

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
| **eBay Partner Network** | **23** | **Yes** — `campid=5339259773`, click + impression |
| NordVPN | 3 | **Yes** — `aff_id=143264` |
| NordPass | 1 | **Yes** — `aff_id=143264` |
| Ko-fi | 5 | **Yes** — donations |
| Newegg | 27 | No — the Rakuten widget matches no merchant |
| Lively | 7 | No — no code |
| Amazon | 3 | No — not applied |
| Consumer Cellular | 3 | No — no code |
| Vultr | 2 | No — no code |
| Backblaze | 2 | No — no code |
| Audible | 1 | No — no separate programme |
| 1Password | 1 | No — no code |
| Bay Alarm | 1 | No — no code |
| DigitalOcean | 1 | No — no code |
| Hetzner | 1 | No — no programme |

**81 affiliate links. 27 earn a commission (23 eBay, 3 NordVPN, 1 NordPass).
5 more are donations. 49 earn nothing.**

That ratio is the actual state of the site, and until this morning nobody
could have seen it, because the disclosure was hand-written prose listing
programmes the site was not enrolled in.

### What moved to eBay, and what did not

18 links moved from Newegg to eBay on 2026-11-25. The rule was simple:
**generic hardware moves, anything with an authorised distributor or a
counterfeit risk stays.**

**Moved to eBay** — commodity parts where the shop does not matter:
1TB NVMe SSD (×4), 16GB and 8GB DDR4 RAM kits, external hard drive (×2),
Intel N100 mini PC, ESP32 DevKit, Cat6a cable (×2), managed network switch
(×2), mechanical keyboard, 12-port USB hub, 24" monitor, APC UPS, cable
management, mini PC, GNU Parallel book.

**Stayed on Newegg** — anything where the store is part of the
recommendation: Raspberry Pi 4 and Pi 5 (Newegg is an authorised Pi
distributor, and marketplaces are full of Pi clones), iPhone SE, GrandPad,
the five tablets, TP-Link / ASUS / Netgear routers, Dell OptiPlex, Echo Show 8.

**Two of the moved links were broken as well as untracked.** The Cat6a cable
pointed at `newegg.com/p/3C6-02B0-001B3` and the managed switch at
`newegg.com/Switches/SubCategory/ID-30` — both recycled item IDs. Newegg
recycles those, and two of the site's URLs pulled from its search index
resolved to a Team T-FORCE SSD and a laptop case. Every moved link is now an
eBay **search** URL, which cannot point at the wrong product.

**The gear page prices were checked against eBay** before moving:
APC Back-UPS Pro BR1500G is $150 brand new and $75 used, eBay minis run
$80–$285, 24" 1080p monitors sit at $150–250. The stated prices hold.

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
