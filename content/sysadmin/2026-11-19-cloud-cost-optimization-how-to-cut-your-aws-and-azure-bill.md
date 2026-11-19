---
title: "Cloud Cost Optimization: How to Cut Your AWS and Azure Bill"
date: 2026-11-19
draft: false
description: "Where the cloud bill actually goes, the five checks that find most of it, and the commitment discounts worth up to 72%. A 2026 guide to cutting AWS and Azure spend."
tags: ["cloud-cost", "finops", "aws", "azure", "cost-optimization"]
categories: ["System administration"]
author: "Pragmatic Sysadmin"
showToc: true
reviewed: true
aiAssisted: true
blogforge:
  provider: template
  model: outline
  generated_at: "2026-11-19T18:45:00Z"
  attempts: 1
  style_score: 96
  topic: "Cloud cost optimization: reducing an AWS or Azure bill in 2026"
---

I once found €400 a month of a cloud bill sitting on a load balancer nobody had opened in a year. It was in front of the data centre. It was load-bearing. It was also a load balancer running at 2% CPU because the service behind it had moved to a smaller instance eighteen months earlier and nobody told the network tier.

That was not a clever saving. It was one line in a cost report nobody had opened.

Most cloud cost advice stops at "use the discount button". That advice is worth something, but it is the smallest part of the bill and the hardest to get right. The bigger wins are boring: find the things nobody is using, size them to what they actually do, and stop paying for the tier of storage that never gets read.

<!--more-->

## Where the money actually goes

Before anything else, get one number: your bill, split by service, for the last full month. Not the dashboard — the data. The dashboard is a summary of the data, and the summary is where the interesting parts get lost.

On AWS, that is the Cost Explorer API, and you can call it from the command line:

```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-10-01,End=2026-11-01 \
  --granularity MONTHLY \
  --metrics BlendedCost UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --query 'ResultsByTime[0].Groups[].{service:Keys[0],blended:Metrics.BlendedCost.Amount}' \
  --output table
```

On Azure, the equivalent list is three flags away:

```bash
az consumption usage list \
  --start-date 2026-10-01 \
  --end-date 2026-10-31 \
  --query "[].{service:properties.metricName,cost:properties.pretaxCost}" \
  --output table
```

Sort the result descending and read the top ten. In my experience the bill has the shape every cloud bill has: one service eats 50–70% of it, three more eat most of the rest, and everything below that is noise you should not spend an afternoon on.

**Fix the biggest line first.** A 10% saving on the biggest service is worth more than a 50% saving on the smallest one, and it takes the same afternoon.

## Check 1: the resources nobody is using

This is where the free money is, because nobody argues with it. It is not a "strategy", it is a cleanup.

The usual suspects:

- **Load balancers** pointing at services that moved, renamed, or were killed
- **EBS volumes** and Azure managed disks attached to nothing
- **Public IPs** that are allocated but unbound — AWS bills for unassociated Elastic IPs
- **Snapshots and images** from machines that no longer exist
- **NAT gateways** in environments that do not need one, each one costing roughly the price of a small instance per month
- **Log groups and buckets** that nobody has queried but still ingest
- **Non-production environments that run 24/7** because someone forgot to stop them at 18:00

AWS will hand you most of this list for free. Compute Optimizer produces recommendations for EC2 instances and Auto Scaling groups, EBS volumes, ECS Fargate tasks, RDS and Aurora, Lambda, NAT gateways, ElastiCache, DynamoDB, DocumentDB, MemoryDB, WorkSpaces and SageMaker endpoints. Enable Cost Explorer first — Compute Optimizer uses its billing data to calculate savings and populate pricing, and without it you get recommendations with no numbers attached.

Cost Optimization Hub goes further and pulls together **18 types** of recommendation — rightsizing, Graviton migration, idle resource detection, Savings Plan and Reserved Instance purchases — into one deduplicated view, priced against your actual discounts, and ranked by savings potential against implementation effort. That ranking is the useful part, because "save 4% by changing a database instance class" and "save 40% by deleting the thing nobody uses" are not the same decision.

On Azure, the same list arrives through **Azure Advisor**, plus the Cost Management blade's own recommendations.

> My rule: if a resource does not appear in any monitoring dashboard, it is either genuinely idle or nobody is watching. Both are worth a look.

## Check 2: right-size everything that is awake

Right-sizing is not about finding the cheapest instance. It is about finding the smallest instance that still does the job, and "the job" is a number, not a feeling.

Two numbers decide it:

- **CPU** — and for memory-bound workloads, ignore CPU entirely
- **Memory** — and for memory-bound workloads, this is the one that matters

Resize on the metric that is actually binding, then re-measure. I have watched people spend a week arguing about CPU when the box was pinned by memory the entire time.

Compute Optimizer is unusually good at this because it reads CloudWatch metrics rather than guessing, and it does not consider transient pricing like Spot when ranking — it compares your current instance against the recommended one on price-performance, and tells you the performance risk. Its console gives a global, cross-account view, which matters the moment you have more than one account.

The part people forget: **the recommendation is only half the job**. A recommendation that nobody applies is worth exactly zero, and applying it costs you a change window. That is why Cost Optimization Hub ranks by implementation effort as well as savings.

## Check 3: the storage line nobody opens

Storage is where a bill grows quietly, because storage bills are for *having* things, not for using them. Nothing breaks. The bill just rises.

Three moves, in order of how much they save:

1. **Move cold data to a cheaper tier.** On AWS that means S3 Intelligent-Tiering, which moves objects automatically as access patterns change — you pay a small monitoring fee, but you stop paying Glacier rates for a file someone opens once a quarter. On Azure, the equivalent is moving blobs between Hot, Cool and Archive tiers.
2. **Set a lifecycle rule.** Not a tier — a rule that deletes what you have already promised not to keep. Log retention, old build artefacts, expired backups.
3. **Check what you are paying per gigabyte for**, because a smaller volume can cost more than a larger one of a different type. Provisioned IOPS volumes and premium disks carry a floor.

The number to watch is not total storage. It is **storage cost as a percentage of the bill, month over month**. If it climbs while your usage does not, you have a lifecycle problem, not a storage problem.

## Check 4: commit to what never changes

This is where the headline discount numbers live, and where most people get them wrong.

| Commitment | Vendor advertises | What that number actually assumes |
|---|---|---|
| AWS Savings Plans / Reserved Instances | up to 72% | Steady on-demand usage, a long enough term, and paying more upfront |
| AWS Spot Instances | up to 90% | Workloads that tolerate being killed |
| Azure savings plan (compute) | up to 65% | One M64dsv2 VM, Ubuntu, East US, 36 months, January 2026 pricing |
| Azure Reserved VM Instances | up to 72% | One M64ls VM, SUSE Linux, East US, 36 months, January 2026 pricing |
| Azure savings plan (databases) | up to 35% | One serverless Azure SQL Database, 12 months, March 2026 pricing |

These are vendor marketing figures with their footnotes intact. Azure's own pricing page is admirably honest about the spread: customers see compute savings plan estimates **between 11% and 65%**. Treat the top of the range as a best case, not a plan.

The mechanics differ in ways that matter:

**AWS.** Reserved Instances lock to a specific instance family, size and region. Savings Plans commit to an hourly *dollar amount* and apply automatically across eligible services and regions, which makes them right for workloads that change shape. AWS's Savings Plans Purchase Analyzer lets you model a purchase against a chosen coverage percentage and see the effect on savings, coverage and utilisation before you spend anything.

**Azure.** Savings plans work the same way as AWS Savings Plans — an hourly spend commitment, applied automatically, discounting eligible usage within scope, with the biggest savings applied first. Reservations lock to a specific resource, size and region, and go deeper. Microsoft is explicit that savings plans suit changing workloads and reservations suit stable ones.

Now the two details that cost real money when you get them wrong:

**You are billed for the commitment whether or not you use it.** Unused commitment expires every hour and does not roll over. Overpay and it is gone; underpay and the excess usage goes back to pay-as-you-go rates. The commitment is a bet on your own future.

**The recommendation engines look backwards.** AWS reservation recommendations are built from on-demand usage over the last 7, 30 or 60 days, and — this is the part that surprises people — they *exclude* usage already covered by Reserved Instances, Spot or Savings Plans. Azure savings plan recommendations use a 7, 30 or 60-day lookback too, but Azure Advisor shows only 30 days. If you have been running on a commitment for a year, your recommendations are now computed from a sliver of your actual workload.

And on Azure specifically: **wait seven days** after buying a savings plan or a reservation before buying the other. The recommendation systems need up to seven days to reflect the purchase, and buying both at once on stale numbers is how people end up paying twice for the same hour.

## Check 5: the egress bill

The bill that arrives after the bill. Data transfer out of the cloud is billed separately, per gigabyte, and it does not show up in the cost report until you know to look for it.

Three things that generate surprise egress:

- **Cross-AZ and cross-region traffic** — free inside a region in the sense that the meter is running slowly, not free
- **Backups leaving the region** — a full copy of your estate, every night, forever
- **Public API traffic** — if you serve real users, your bill is now partly a function of how popular you are

The fix is rarely "pay less". It is **knowing where the bytes go** before you redesign anything. On AWS the Cost and Usage Report in an S3 bucket, queried through Data Exports, will show you exactly which resource pair is generating the transfer cost. On Azure, the Cost Management blade's analysis views break it down by resource.

## What changed since 2025

The cloud cost optimization conversation in 2025 was about "do I use a reservation or a Savings Plan", and that question got answered — mostly by AWS and Azure adding better recommendation engines rather than by anyone changing their architecture.

What actually changed in 2026 is quieter and more useful:

- **Genuinely cross-account recommendations.** AWS Compute Optimizer now gives a global, cross-account view. For anyone who spent the last five years consolidating billing into one account and then discovering the resources were scattered, this is the single biggest change.
- **Cost Optimization Hub** exists as a place where rightsizing, migration and commitment recommendations live together, deduplicated and priced against your real discounts.
- **Finer-grained forecasting.** Cost Explorer forecasts up to 18 months ahead at monthly granularity and 3 months at daily granularity.
- **Commitment modelling got honest.** Both vendors now let you model the effect of a commitment on savings, coverage *and* utilisation, and show you the break-even. AWS's reservation recommendation table literally has a "break even months" column.

None of this is revolutionary. It is the tooling getting good enough that the boring cleanup is now automated — which means the remaining money is in the things the tools are bad at, which is exactly where you want to spend your own attention.

## Automating the whole thing

Once the manual passes are done, the point is that they should not need doing again. Three mechanisms, in increasing order of invasiveness:

1. **Anomaly detection.** AWS Cost Anomaly Detection uses machine learning to spot unusual spend and alert on it. It catches the runaway job, the compromised key, the log group that started ingesting gigabytes. It will not catch a slow drift, which is what the next one is for.
2. **Budgets with automatic actions.** AWS Budgets can notify, and can go further — budget actions can apply or apply a policy to the resource that blew the budget. A budget that only emails you is a budget that gets ignored.
3. **Tagging and allocation.** Cost Categories on AWS, cost allocation tags, and Billing Conductor for splitting one bill between several teams. Once every resource has an owner, "who is spending this" stops being a mystery and becomes a lookup.

The order matters. Automate the alerts *after* the cleanup, not before — an alert system that fires on every idle resource trains you to ignore it within a fortnight.

## Budgeting for cloud in a way that survives contact

Most cloud budgets fail because they are written as a number and nothing else. A number cannot be reviewed, challenged, or defended in a meeting where someone asks "why".

Build it in three layers instead:

- **A committed baseline** — what you will spend if nothing changes, which is usually the current bill minus the savings you have already banked
- **A forecast** — the same number projected forward, which both vendors will give you
- **A named owner per service** — the person who can say what each line is for

Then set the alert thresholds below the number you expect, not at it. A budget that fires when you have already overspent is a report, not a control.

## What usually does not work

Honesty section, because the "cloud cost optimization" search results are full of advice that sounds good:

- **Buying commitments on a growing bill.** The commitment scales with your usage, so a rising bill gets a rising commitment. The discount applies to a bigger number. Fix the shape of the bill first.
- **Spot for everything.** Up to 90% off, and your job dies when AWS reclaims the capacity. Fine for batch, queues, rendering, anything with a retry. Catastrophic for a single-instance database.
- **The cheapest instance in the catalogue.** A `t4g.nano` that cannot actually handle the load is not a saving. It is a support ticket and an outage.
- **Negotiating enterprise discounts before you know your own numbers.** You cannot negotiate against a number you have not computed.
- **A tool that only reports.** If a platform shows you a beautiful dashboard of 47 recommendations and does not tell you the order to do them in, it is a reporting tool. AWS's Cost Optimization Hub ranks by savings and effort, which is the difference between a tool and a dashboard.

## What to do next

This week, one hour, no new tooling:

1. Pull the cost report by service for the last full month. Find the biggest line.
2. Open Compute Optimizer (or Azure Advisor) and pull the idle-resource recommendations. Delete what nobody owns.
3. Write down the three biggest services and what they are for. One line each.

That third step is the one people skip, and it is the one that pays. Every later decision — commitments, budgets, who gets an alert, whether a service should exist at all — depends on knowing what the thing actually does.

Once you know that, the self-hosting question becomes a much easier question to answer, because you know what you would be replacing. I did the arithmetic on that side of it in [Cloud for Cheap](/sysadmin/2026-11-10-cloud-for-cheap-the-honest-cost-math/), and the older checklist for a shrinking vendor bill is in [How to Reduce Your Cloud Spend](/sysadmin/how-reduce-cloud-spend-before-year-end-2025/). If you are still deciding what to run at home rather than what to cut in the cloud, start with [Build Your Own Cloud](/meta/build-your-own-free-cloud-home-server-guide/).

## FAQ

### How much can you realistically save on a cloud bill?

Less than the discounts suggest, and more than the "you are already paying the cheapest price" crowd claims. In my experience the first pass — deleting idle resources, right-sizing, lifecycle rules — finds 15–30% without touching the commitment model at all. The commitment discounts then apply to whatever is left, and they are worth up to the advertised 72% only on the workload that is genuinely steady.

### Should I buy Reserved Instances or Savings Plans?

Savings Plans if your workload changes shape — the commitment is a dollar amount that applies across services and regions automatically. Reserved Instances if it does not — the discount is deeper because you are locking to a specific family, size and region. Azure makes the same split, with the same warning: never buy both at once, and wait seven days between purchases.

### How do I stop the bill creeping back up?

Treat it as a regression, not a project. Tag every resource with an owner, turn on anomaly detection so the emergencies find you, and put a budget with automatic actions on the services that matter. Then review the top three services once a quarter, the same way you would review a dependency list.

*Cut the first line of the bill before you negotiate the last one.*
