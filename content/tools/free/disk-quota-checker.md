---
title: "Disk Quota Checker"
date: 2026-06-30T10:00:00.000Z
description: "Find who's using the most disk on shared systems — Free bash script from Pragmatic Sysadmin"
author: "Pragmatic Sysadmin"
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Disk Quota Checker",
  "description": "Find who's using the most disk on shared systems",
  "applicationCategory": "UtilitiesApplication",
  "operatingSystem": "Linux",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "author": {
    "@type": "Person",
    "name": "Pragmatic Sysadmin"
  }
}
</script>

# 📊 Disk Quota Checker

**Find who's using the most disk on shared systems**

Find top disk space users on shared /home or any other directory.
Auto-flags users over 10GB as cleanup candidates. Useful for
finding runaway logs, large Docker workloads, or old data.

## Features

- ✅ Top N biggest directories with sizes
- ✅ Auto-flag any user over 10GB
- ✅ Breakdown of the largest directory
- ✅ Suggested cleanup actions
- ✅ Works without root for current user's data

## Usage

```bash
./disk-quota-checker.sh
sudo ./disk-quota-checker.sh -d /var/www -n 20

```

## Download

Get the script from the [Free Tools Pack](/shop/#free-tools), or grab it directly:

```bash
# Clone from the repo (scripts are in /products/free/)
curl -O https://pragmaticsysadmin.help/downloads/disk-quota-checker.sh
chmod +x disk-quota-checker.sh
./disk-quota-checker.sh --help
```

## License

MIT — use, modify, redistribute.

## Support

Bugs or questions: [pragmatic@pragmaticsysadmin.help](mailto:pragmatic@pragmaticsysadmin.help)

## More tools

See [/shop/](/shop/) for the full catalog, including paid toolkits:

- **[The 5-Minute Server Health Check Toolkit](/products/health-check-toolkit/)** ($9) — the "do everything" Monday morning ritual

---

Made with care by [Pragmatic Sysadmin](https://pragmaticsysadmin.help).
