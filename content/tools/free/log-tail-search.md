---
title: "Log Pattern Search with Context"
date: 2026-06-30T10:00:00.000Z
description: "Find errors across multiple log files in seconds — Free bash script from Pragmatic Sysadmin"
author: "Pragmatic Sysadmin"
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Log Pattern Search with Context",
  "description": "Find errors across multiple log files in seconds",
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

# 🔍 Log Pattern Search with Context

**Find errors across multiple log files in seconds**

Search multiple log files for patterns with surrounding context lines.
Smart time-range filtering, case-insensitive option, and color output
make debugging much faster than grep + manual context-finding.

## Features

- ✅ Search across multiple log files in one go
- ✅ Configurable context lines before/after each match
- ✅ Time-range filter (-s 1h, -s 24h, -s 7d)
- ✅ Case-insensitive search
- ✅ Color-coded output, grouped by file

## Usage

```bash
./log-tail-search.sh -p "Out of memory" -d /var/log
./log-tail-search.sh -p "Failed password" -s 24h -i
./log-tail-search.sh -p "error" -f syslog,messages -n 5

```

## Download

Get the script from the [Free Tools Pack](/shop/#free-tools), or grab it directly:

```bash
# Clone from the repo (scripts are in /products/free/)
curl -O https://pragmaticsysadmin.help/downloads/log-tail-search.sh
chmod +x log-tail-search.sh
./log-tail-search.sh --help
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
