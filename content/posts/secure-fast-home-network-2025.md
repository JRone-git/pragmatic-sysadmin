---
title: "How I Built This Blog: Hugo + Firebase + AWeber in 30 Minutes"
date: 2025-08-16
draft: false
description: "Building a blazing-fast, nearly-free blog with modern static site tools. Here's exactly how I did it."
tags: ["hugo","firebase","blogging","static sites"]
---

## Why This Stack?

As a sysadmin, I wanted a blog that's:
- **Fast**: Static sites load instantly
- **Cheap**: Firebase free tier handles tons of traffic  
- **Simple**: No databases, no server maintenance
- **SEO-ready**: Hugo generates clean, optimized HTML

Here's exactly how I built this site in under 30 minutes.

## The Stack

- **Hugo**: Static site generator (like Jekyll, but faster)
- **PaperMod**: Clean, minimal Hugo theme
- **Firebase Hosting**: Google's CDN with free SSL
- **AWeber**: Newsletter forms that actually work
- **Google Analytics**: Track what people read

## Step-by-Step Build Process

### 1. Install the Tools

On Windows with Chocolatey:
```bash
choco install hugo-extended
npm install -g firebase-tools
```

### 2. Create the Site

```bash
hugo new site pragmatic-sysadmin
cd pragmatic-sysadmin
git init
```

### 3. Add PaperMod Theme

```bash
git submodule add https://github.com/adityatelange/hugo-PaperMod themes/PaperMod
```

### 4. Configure Hugo

Updated `hugo.toml` with SEO basics:

```toml
baseURL = "https://pragmaticsysadmin.help/"
title = "Pragmatic Sysadmin"
theme = "PaperMod"
enableRobotsTXT = true

[pagination]
  pagerSize = 10

[markup]
  [markup.goldmark]
    [markup.goldmark.renderer]
      unsafe = true  # Allows AWeber forms

[params]
  description = "Funny, practical home networking and de-mystified cloud."
  defaultTheme = "auto"
  ShowReadingTime = true
  ShowPostNavLinks = true
  ShowShareButtons = true
```

### 5. Add Google Analytics

Created `layouts/partials/head-end.html` with GA4 tracking:

```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-WCG1VLDG4T"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-WCG1VLDG4T');
</script>
```

### 6. Deploy to Firebase

```bash
hugo --minify          # Build static files
firebase login         # Authenticate
firebase init hosting  # Configure hosting
firebase deploy        # Go live!
```

Firebase setup answers:
- Public directory: `public`
- Single-page app: `No`  
- GitHub deploys: `No`

### 7. Add AWeber Newsletter

Created newsletter page with embedded form:

```markdown
## Join the newsletter
Short, practical tips. No spam, just sysadmin sanity.

<div class="aweber-form">
  <!-- AWeber JavaScript form code -->
</div>
```

### 8. Connect Custom Domain

In Firebase Console → Hosting → Add custom domain, then updated DNS:
- A record: `pragmaticsysadmin.help` → `199.36.158.100`
- TXT record: `pragmaticsysadmin.help` → `hosting-site=johnnysblogman`

## The Results

**Live site**: https://pragmaticsysadmin.help (once DNS propagates)  
**Backup URL**: https://johnnysblogman.web.app  
**Cost**: $0/month for reasonable traffic  
**Build time**: ~2 minutes  
**Deploy time**: ~30 seconds

## Quick Commands

```bash
# Local development
hugo server -D

# Build and deploy
hugo --minify
firebase deploy
```

## Why This Works

This stack scales from zero to thousands of visitors without touching server configs. Hugo pre-builds everything, Firebase's CDN serves it globally, and analytics + newsletter capture runs automatically.

Perfect for technical blogs, documentation sites, or any content that doesn't need real-time data.

Next up: I'll be writing about secure home networking, because apparently everyone's router is still using admin/admin. 🤦‍♂️
