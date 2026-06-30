---
title: "SSH Key Security Auditor"
date: 2026-06-30T10:00:00.000Z
description: "Find weak keys, suspicious restrictions, and bad permissions — Free bash script from Pragmatic Sysadmin"
author: "Pragmatic Sysadmin"
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "SSH Key Security Auditor",
  "description": "Find weak keys, suspicious restrictions, and bad permissions",
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

# 🔑 SSH Key Security Auditor

**Find weak keys, suspicious restrictions, and bad permissions**

Audit SSH keys across all user accounts. Reports every authorized
key with type and length, flags weak DSA/short RSA keys, finds
private keys with world-readable permissions.

## Features

- ✅ Scans /home and /root/.ssh automatically
- ✅ Reports key types (ed25519, RSA, DSA, ECDSA)
- ✅ Flags weak keys (DSA, short RSA)
- ✅ Detects restricted keys (command=, from=, no-pty)
- ✅ Finds private keys with bad permissions (not 600/400)
- ✅ Reports known_hosts entry counts

## Usage

```bash
./ssh-key-auditor.sh
sudo ./ssh-key-auditor.sh      # includes /root
./ssh-key-auditor.sh -u alice,bob

```

## Download

Get the script from the [Free Tools Pack](/shop/#free-tools), or grab it directly:

```bash
# Clone from the repo (scripts are in /products/free/)
curl -O https://pragmaticsysadmin.help/downloads/ssh-key-auditor.sh
chmod +x ssh-key-auditor.sh
./ssh-key-auditor.sh --help
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
