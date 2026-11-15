---
title: "Newsletter Archive"
date: 2025-08-16
draft: false
description: "All past issues of the Pragmatic Tech newsletter - one practical tip per week since March 2026."
build:
  list: false
  render: true
---

<div class="nl-page">
<div class="nl-hero">
<h1>Newsletter Archive</h1>
<p>All past issues - one practical tip per week. No spam, no marketing.</p>
</div>

<div class="nl-form-card">
<form id="newsletter-form" action="https://buttondown.com/api/emails/embed-subscribe/jonne" method="post" class="embeddable-buttondown-form" target="_top">
  <label for="bd-email">Your email address</label>
  <div class="nl-form-row">
    <input type="email" name="email" id="bd-email" placeholder="you@example.com" required>
    <button type="submit">Subscribe</button>
  </div>
  <input type="hidden" name="embed" value="1">
</form>
</div>

<div class="nl-section">
<h3>Past Issues</h3>
<ul>
<li><strong>Issue 1:</strong> March 7, 2026 - Welcome to Pragmatic Tech</li>
<li><strong>Issue 2:</strong> March 14, 2026 - How to Set Up a Home Network for Your Parents</li>
<li><strong>Issue 3:</strong> March 21, 2026 - 5 Free Tools for Senior Tech Help</li>
<li><strong>Issue 4:</strong> March 28, 2026 - How to Turn On 2FA for Your Elderly Parent's Email</li>
<li><strong>Issue 5:</strong> April 4, 2026 - The Best Free Phone Apps for Seniors in 2026</li>
<li><strong>Issue 6:</strong> April 11, 2026 - How to Reduce Cloud Spend Before Year-End</li>
<li><strong>Issue 7:</strong> April 18, 2026 - How to Replace Google Photos with Immich</li>
<li><strong>Issue 7:</strong> April 25, 2026 - Plex vs Jellyfin in 2026: The Paywall and the Hardware</li>
</ul>
</div>

<div class="nl-support">
<p>Want to support the newsletter and get free cheat sheets?</p>
<a href="https://ko-fi.com/sysadmin_dad" target="_blank" rel="noopener" class="kofi-btn">Support on Ko-fi</a>
</div>

<p class="nl-privacy">
  No analytics, no tracking pixels, no cookies. <a href="/privacy/">Privacy policy</a>.
</p>

<script>
window.addEventListener('DOMContentLoaded', function() {
  var params = new URLSearchParams(window.location.search);
  if (params.get('subscribed') === 'true') {
    var form = document.getElementById('newsletter-form');
    var thanks = document.getElementById('newsletter-thankyou');
    if (form && thanks) {
      form.closest('.nl-form-card').style.display = 'none';
      thanks.style.display = 'block';
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }
});
</script>
</div>