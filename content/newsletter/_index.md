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

  <!-- ✅ Official Buttondown embed form structure - ALL URLs cleaned -->
<form
  action="https://buttondown.com/api/emails/embed-subscribe/jonne"
  method="post"
  class="embeddable-buttondown-form"
  target="_top"
>
  <label for="bd-email" style="display:block; margin-bottom:0.5em; font-weight:500;">Enter your email</label>
  <div style="display: flex; gap: 10px; flex-wrap: wrap;">
    <input 
      type="email" 
      name="email" 
      id="bd-email" 
      placeholder="you@example.com" 
      required
      style="flex: 1; min-width: 200px; padding: 14px; border: 1px solid #ccc; border-radius: 8px; font-size: 1em;"
    >
    <input 
      type="submit" 
      value="Subscribe" 
      style="padding: 14px 24px; background: #007bff; color: white; border: none; border-radius: 8px; font-size: 1em; font-weight: bold; cursor: pointer; transition: background 0.3s;"
    >
  </div>
  
  <!-- Required hidden field for embed detection -->
  <input type="hidden" name="embed" value="1" />
  
  <!-- Optional: redirect after successful subscription -->
  <input type="hidden" name="redirect" value="https://pragmaticsysadmin.help/newsletter/?subscribed=true" />
  
  <p style="text-align: center; margin-top: 15px; font-size: 0.85em; color: #888;">
    <a href="https://buttondown.com/refer/jonne" target="_blank" style="color: #aaa; text-decoration: none;">Powered by Buttondown.</a>
  </p>
</form>

  <!-- SUCCESS MESSAGE (Hidden by default) -->
  <div id="newsletter-thankyou" style="display: none; background: #e8f5e9; padding: 2em; border-radius: 12px; text-align: center; border: 1px solid #c8e6c9; margin-bottom: 2em;">
    <h3 style="margin-top: 0; color: #2e7d32;">✅ You're subscribed!</h3>
    <p style="margin-bottom: 0.5em;">Check your inbox to confirm your subscription.</p>
    <p style="margin-bottom: 0;"><b>🎁 <a href="/cheat-sheet.html" style="color: #2e7d32; font-weight: bold;">Click here to access your Cheat Sheets</a></b></p>
  </div>

  <!-- FREEBIES SECTION -->
  <div style="background: #f8f9fa; padding: 1.5em; border-radius: 12px; margin-bottom: 2em; border-left: 5px solid #007bff;">
    <h3 style="margin-top: 0; margin-bottom: 0.5em; font-size: 1.2em;">🎁 Instant Access for Subscribers</h3>
    <p style="margin-bottom: 1em; color: #444;">Get immediate access to my library of cheat sheets:</p>
    <ul style="padding-left: 20px; margin-bottom: 1em; color: #333; line-height: 1.6;">
      <li><strong>Linux Commands</strong> - Essentials every sysadmin needs</li>
      <li><strong>Networking</strong> - Troubleshooting & diagnostics</li>
      <li><strong>Security Hardening</strong> - Server security checklist</li>
    </ul>
    <a href="/cheat-sheet.html" style="display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 0.9em;">Access Resources</a>
  </div>

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
