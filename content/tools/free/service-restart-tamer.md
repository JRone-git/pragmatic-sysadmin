---
title: "Safe Service Restart"
date: 2026-06-30T10:00:00.000Z
description: "Restart services with pre-checks and rollback guidance — Free bash script from Pragmatic Sysadmin"
author: "Pragmatic Sysadmin"
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Safe Service Restart",
  "description": "Restart services with pre-checks and rollback guidance",
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

# 🔄 Safe Service Restart

**Restart services with pre-checks and rollback guidance**

Restart a systemd service safely. Records state before restart,
runs your custom health check before and after, waits for the
service to come back up, and prints recent logs if something fails.

## Features

- ✅ Pre-check and post-check with custom commands
- ✅ Configurable wait time for service to become active
- ✅ Auto-shows journalctl logs if restart fails
- ✅ Records PID + uptime before restart for audit trail
- ✅ Color-coded step-by-step output

## Usage

```bash
./service-restart-tamer.sh nginx
./service-restart-tamer.sh postgresql --wait 30
./service-restart-tamer.sh my-app --pre-check "curl -s http://localhost:8080/health" --post-check "curl -f http://localhost:8080/health"

```

## Download

Get the script from the [Free Tools Pack](/shop/#free-tools), or grab it directly:

```bash
# Clone from the repo (scripts are in /products/free/)
curl -O https://pragmaticsysadmin.help/downloads/service-restart-tamer.sh
chmod +x service-restart-tamer.sh
./service-restart-tamer.sh --help
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
