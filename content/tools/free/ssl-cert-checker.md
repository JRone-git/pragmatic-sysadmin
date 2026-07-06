---
title: "SSL Certificate Expiry Checker"
date: 2026-06-30T10:00:00.000Z
description: "Find certificates about to expire before they break your site — Free bash script from Pragmatic Sysadmin"
author: "Pragmatic Sysadmin"
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "SSL Certificate Expiry Checker",
  "description": "Find certificates about to expire before they break your site",
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

# 🔒 SSL Certificate Expiry Checker

**Find certificates about to expire before they break your site**

A simple bash script that checks SSL certificate expiry dates for
one or more domains and alerts you if they're expiring soon.
Exit codes make it perfect for cron + monitoring integration.

## Features

- ✅ Check one or many domains at once
- ✅ Configurable warning (default 30 days) and critical (default 7 days) thresholds
- ✅ Exit codes for monitoring integration (0=OK, 1=warning, 2=critical)
- ✅ Reads domains from args, file, or stdin
- ✅ Color output when run interactively

## Usage

```bash
./ssl-cert-checker.sh prag mati csysadmin.help github.com google.com
./ssl-cert-checker.sh -f domains.txt

```

## Download

Get the script from the [Free Tools Pack](/shop/#free-tools), or grab it directly:

```bash
# Clone from the repo (scripts are in /products/free/)
curl -O https://pragmaticsysadmin.help/downloads/ssl-cert-checker.sh
chmod +x ssl-cert-checker.sh
./ssl-cert-checker.sh --help
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
