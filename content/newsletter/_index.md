---
title: "Newsletter"
date: 2025-08-16
draft: false
description: "Join the Pragmatic Sysadmin newsletter for practical tips and insights."
---

<div style="max-width: 600px; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;">

  <div style="text-align: center; margin-bottom: 2em;">
    <h2 style="margin-bottom: 0.3em;">Join the Newsletter</h2>
    <p style="color: #555; font-size: 1.1em; margin-top: 0;">Short, practical tips. No spam, just sysadmin sanity.</p>
  </div>

<form action="https://buttondown.com/api/emails/embed-subscribe/jonne" method="post" class="embeddable-buttondown-form" target="_top" style="margin:2em 0;padding:1.5em;background:#f7f7f7;border-radius:8px;border:1px solid #e0e0e0;">
  <label for="bd-email" style="display:block;margin-bottom:0.5em;font-weight:bold;">Enter your email:</label>
  <div style="display:flex;gap:0.5em;flex-wrap:wrap;">
    <input type="email" name="email" id="bd-email" placeholder="you@example.com" required style="flex:1;min-width:200px;padding:0.7em 1em;border:1px solid #ccc;border-radius:6px;font-size:1em;">
    <button type="submit" style="padding:0.7em 1.5em;background:#2563eb;color:#fff;font-weight:bold;border:none;border-radius:6px;cursor:pointer;font-size:1em;">Subscribe</button>
  </div>
  <input type="hidden" name="embed" value="1">
</form>

  <!-- WHAT TO EXPECT -->
  <div style="margin-bottom: 2.5em; color: #333;">
    <h3 style="font-size: 1.2em; border-bottom: 1px solid #eee; padding-bottom: 0.5em;">Weekly Insights</h3>
    <ul style="line-height: 1.8; padding-left: 20px;">
      <li>Home networking security</li>
      <li>Cloud infrastructure tips</li>
      <li>Practical automation tricks</li>
      <li>Tool recommendations</li>
    </ul>
  </div>

  <!-- SUPPORT SECTION -->
  <div style="text-align: center; padding: 1.5em; background: #fffce6; border-radius: 12px; border: 1px solid #ffeeba;">
    <a href="https://buymeacoffee.com/pragmaticadmin" target="_blank" rel="noopener" 
       style="display: inline-block; padding: 0.8em 2em; background: #ffdd00; color: #222; font-weight: bold; border-radius: 8px; font-size: 1.2em; text-decoration: none; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
      ☕ Buy Me a Coffee
    </a>
    <div style="margin-top: 0.5em; color: #888; font-size: 0.9em;">Support the newsletter and get more free resources!</div>
  </div>

</div>

<script>
// Script to handle the success redirect
window.onload = function() {
  var urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('subscribed') === 'true') {
    var form = document.getElementById('newsletter-form');
    var thanks = document.getElementById('newsletter-thankyou');
    if (form && thanks) {
      form.style.display = 'none';
      thanks.style.display = 'block';
      // Clean URL without query parameter
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }
};
</script>
>>>>>>> b96e2153a8965a98a1309b6041b5caf5e652018c
