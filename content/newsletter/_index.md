---
title: "Newsletter"
date: 2025-08-16
draft: false
description: "Join the Pragmatic Tech newsletter — one practical tip every Tuesday. No spam, no marketing fluff."
build:
  list: false
  render: true
---

<style>
.nl-page {
  max-width: 640px;
  margin: 0 auto;
}
.nl-hero {
  text-align: center;
  padding: 2rem 0 1.5rem;
}
.nl-hero h1 {
  font-size: 1.9rem;
  font-weight: 700;
  color: var(--primary, #2a2a2a);
  margin: 0 0 0.5rem 0;
  line-height: 1.2;
}
.nl-hero p {
  font-size: 1.05rem;
  color: var(--secondary, #5a5a5a);
  margin: 0;
  line-height: 1.5;
}
.nl-form-card {
  background: var(--code-bg, #fafaf6);
  border: 1px solid var(--border, #d6cfbe);
  border-left: 4px solid #5a7a5e;
  border-radius: 8px;
  padding: 1.8rem;
  margin: 1.5rem 0;
}
.nl-form-card label {
  display: block;
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--primary, #2a2a2a);
  margin-bottom: 0.6rem;
}
.nl-form-row {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}
.nl-form-row input[type="email"] {
  flex: 1;
  min-width: 200px;
  padding: 0.7rem 1rem;
  border: 1px solid var(--border, #d6cfbe);
  border-radius: 6px;
  font-size: 1rem;
  background: var(--background, #fff);
  color: var(--primary, #2a2a2a);
  outline: none;
  transition: border-color 0.15s ease;
}
.nl-form-row input[type="email"]:focus {
  border-color: #5a7a5e;
  box-shadow: 0 0 0 2px rgba(90, 122, 94, 0.15);
}
.nl-form-row button {
  padding: 0.7rem 1.5rem;
  background: #5a7a5e;
  color: #fff;
  font-weight: 600;
  font-size: 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s ease, transform 0.1s ease;
  white-space: nowrap;
}
.nl-form-row button:hover {
  background: #4a6a4e;
}
.nl-form-row button:active {
  transform: scale(0.98);
}
.nl-thanks {
  display: none;
  text-align: center;
  padding: 2rem 1.5rem;
  background: #f0f7f0;
  border: 1px solid #c5dfc5;
  border-left: 4px solid #5a7a5e;
  border-radius: 8px;
  margin: 1.5rem 0;
}
.nl-thanks h2 {
  margin: 0 0 0.4rem 0;
  color: #2d5a30;
  font-size: 1.4rem;
}
.nl-thanks p {
  color: #3d6a40;
  margin: 0 0 0.8rem 0;
}
.nl-thanks a {
  color: #5a7a5e;
  font-weight: 600;
  text-decoration: none;
  border-bottom: 1px solid #5a7a5e;
}
.nl-section {
  margin: 2rem 0 1.5rem;
}
.nl-section h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--primary, #2a2a2a);
  border-bottom: 1px solid var(--border, #d6cfbe);
  padding-bottom: 0.5rem;
  margin-bottom: 0.8rem;
}
.nl-section ul {
  padding-left: 1.2rem;
  margin: 0;
}
.nl-section li {
  color: var(--secondary, #5a5a5a);
  font-size: 0.95rem;
  line-height: 1.85;
}
.nl-topics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.8rem;
  margin: 1rem 0 0;
}
.nl-topic {
  display: block;
  padding: 0.8rem 1rem;
  background: var(--code-bg, #fafaf6);
  border: 1px solid var(--border, #d6cfbe);
  border-radius: 6px;
  text-decoration: none;
  color: var(--primary, #2a2a2a);
  font-size: 0.9rem;
  line-height: 1.35;
  transition: border-color 0.15s ease, transform 0.1s ease;
}
.nl-topic:hover {
  border-color: #5a7a5e;
  transform: translateY(-1px);
}
.nl-topic strong {
  display: block;
  font-size: 0.95rem;
  margin-bottom: 0.15rem;
}
.nl-topic span {
  color: var(--secondary, #5a5a5a);
  font-size: 0.83rem;
}
.nl-support {
  text-align: center;
  padding: 1.5rem;
  background: var(--code-bg, #fafaf6);
  border: 1px solid var(--border, #d6cfbe);
  border-radius: 8px;
  margin: 2rem 0 1rem;
}
.nl-support p {
  color: var(--secondary, #5a5a5a);
  font-size: 0.9rem;
  margin: 0.6rem 0 1rem;
}
.nl-support a.kofi-btn {
  display: inline-block;
  padding: 0.7rem 1.6rem;
  background: #FF5E5B;
  color: #fff;
  font-weight: 700;
  border-radius: 6px;
  text-decoration: none;
  font-size: 1rem;
  box-shadow: 0 2px 6px rgba(255, 94, 91, 0.2);
  transition: background 0.15s ease, transform 0.1s ease;
}
.nl-support a.kofi-btn:hover {
  background: #e54e4b;
  transform: translateY(-1px);
}
.nl-privacy {
  font-size: 0.85rem;
  color: #888;
  text-align: center;
  margin-top: 1.5rem;
  line-height: 1.5;
}
.nl-privacy a {
  color: var(--secondary, #5a5a5a);
  text-decoration: underline;
}
@media (max-width: 640px) {
  .nl-hero h1 { font-size: 1.5rem; }
  .nl-form-card { padding: 1.2rem; }
}
</style>

<div class="nl-page">

<div class="nl-hero">
<h1>One practical tip every Tuesday</h1>
<p>Short, tested, no-fluff advice for sysadmins and family tech helpers. Read by 3,200+ people.</p>
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

<div id="newsletter-thankyou" class="nl-thanks">
<h2>You're in.</h2>
<p>Check your inbox for a confirmation email, then grab your free downloads.</p>
<a href="/newsletter/thank-you/">Get your free scripts & checklists &rarr;</a>
</div>

<div class="nl-section">
<h3>What you'll get</h3>
<div class="nl-topics">
  <a href="/sysadmin/" class="nl-topic">
    <strong>Server health</strong>
    <span>Checks, monitoring fixes, backup tricks</span>
  </a>
  <a href="/senior-tech/" class="nl-topic">
    <strong>Family tech</strong>
    <span>Phone setup tips, scam prevention</span>
  </a>
  <a href="/sysadmin/" class="nl-topic">
    <strong>Automation</strong>
    <span>Scripts, workflows, time-savers</span>
  </a>
  <a href="/resources/" class="nl-topic">
    <strong>Tool picks</strong>
    <span>Honest recommendations, no sponsors</span>
  </a>
</div>
</div>

<div class="nl-section">
<h3>The fine print</h3>
<ul>
  <li><strong>Frequency:</strong> Once a week, every Tuesday morning (Finland time).</li>
  <li><strong>Length:</strong> One tip, one explanation, one actionable takeaway. Under 3 minutes to read.</li>
  <li><strong>No spam:</strong> I've never sent a promotional email. Unsubscribe with one click.</li>
  <li><strong>Your data:</strong> Handled by Buttondown. Never sold, never shared. That's it.</li>
</ul>
</div>

<div class="nl-support">
<p>Want to support the newsletter and get free cheat sheets?</p>
<a href="https://ko-fi.com/sysadmin_dad" target="_blank" rel="noopener" class="kofi-btn">Support on Ko-fi</a>
</div>

<p class="nl-privacy">
  No analytics, no tracking pixels, no cookies. <a href="/privacy/">Privacy policy</a>.
</p>

</div>

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