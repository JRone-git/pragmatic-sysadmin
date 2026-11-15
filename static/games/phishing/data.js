window.PHISHING_DECK = [
  {
    id: "parcel-fee",
    from: "Posti <ilmoitus@posti-tracking-fi.com>",
    subject: "Your parcel is on hold — 2.99 € fee required",
    body: "Dear customer, your parcel could not be delivered. [[Pay the small handling fee here]] within 24 hours or it will be returned to sender.",
    verdict: "phishing",
    flags: [
      "The domain is posti-tracking-fi.com, not posti.fi",
      "A tiny 'release fee' for a parcel is a classic card-harvesting pattern",
      "The 24-hour deadline exists to stop you from checking"
    ],
    explain: "Real carriers never ask for card details to release a parcel. If you're unsure, open the carrier's app or type the address yourself — never tap the link."
  },
  {
    id: "bank-real",
    from: "Nordea <no-reply@nordea.fi>",
    subject: "Your statement for October is ready",
    body: "Your monthly statement is available in the app. No action is required. [[We will never ask for your password by email.]]",
    verdict: "safe",
    flags: [
      "Correct domain (nordea.fi)",
      "No link asking you to log in",
      "Explicitly states it won't ask for credentials"
    ],
    explain: "This is what legitimate bank mail looks like: informational, no urgency, no credential request. The safest habit is still to open the app directly rather than click."
  },
  {
    id: "account-locked",
    from: "PayPal <security@paypal-security-update.net>",
    subject: "Your account has been permanently limited",
    body: "We noticed unusual activity on your account. [[Log in now to restore access]] or your account will be closed within 48 hours.",
    verdict: "phishing",
    flags: [
      "The domain is paypal-security-update.net, not paypal.com",
      "Permanent account limitation used as fear tactic",
      "Demands immediate login via email link"
    ],
    explain: "PayPal never sends account-limited notices demanding login by email. Log in by typing paypal.com directly in your browser."
  },
  {
    id: "pharmacy-receipt",
    from: "Apotti <noreply@apotti.fi>",
    subject: "Your e-prescription is ready",
    body: "Your prescription has been sent to your pharmacy. You can view it in the Omakanta service. No action is needed from you.",
    verdict: "safe",
    flags: [
      "Correct Finnish domain (apotti.fi)",
      "No link, no login request, no urgency",
      "Describes exactly what happened"
    ],
    explain: "Finnish healthcare notifications are informational. When in doubt, open Omakanta through your browser bookmark — not through an email link."
  }
];
  {
    id: "invoice-zip",
    from: "DHL Express <invoices@dhl-delivery-tracking.com>",
    subject: "Invoice #INV-44821 attached",
    body: "Please review the attached invoice for your recent shipment. [[Open the document to view charges]] and arrange payment.",
    verdict: "phishing",
    flags: [
      "The domain is dhl-delivery-tracking.com, not dhl.com",
      "Unexpected invoice with attachment",
      "Urges you to open a document you didn't request"
    ],
    explain: "Zip/HTML attachments from unknown senders commonly hide malware. If you didn't order anything from DHL, delete it."
  },
  {
    id: "appointment-reminder",
    from: "Mehiläinen <viesti@mehilainen.fi>",
    subject: "Appointment reminder — Tuesday 14:00",
    body: "This is a reminder for your appointment on Tuesday at 14:00. If you need to cancel, please call customer service.",
    verdict: "safe",
    flags: [
      "Correct domain (mehilainen.fi)",
      "Specific date and time",
      "Gives a phone number to call rather than a link to click"
    ],
    explain: "Legitimate appointment reminders are specific and give you a phone number. No login, no payment, no urgency."
  },
  {
    id: "prize-winner",
    from: "Amazon <winners@amazon-prize-claim.info>",
    subject: "You won a €100 Amazon gift card!",
    body: "Congratulations! You have been randomly selected. [[Claim your prize now]] before the offer expires.",
    verdict: "phishing",
    flags: [
      "The domain is amazon-prize-claim.info, not amazon.com",
      "You didn't enter a contest",
      "Too-good-to-be-true prize with urgency"
    ],
    explain: "Amazon doesn't email random people saying they won gift cards. This is a classic advance-fee scam."
  },
  {
    id: "software-update",
    from: "Microsoft <noreply@account.microsoft.com>",
    subject: "Security update available for your account",
    body: "A new security update is available. We recommend reviewing your recent sign-in activity in your account settings.",
    verdict: "safe",
    flags: [
      "Correct domain (account.microsoft.com)",
      "No link, just a recommendation to check settings",
      "No urgency, no threat"
    ],
    explain: "Legitimate security updates point you to your account settings — they don't embed login links in email."
  },
  {
    id: "netflix-payment",
    from: "Netflix <billing@netflix-payment-verification.com>",
    subject: "Your payment method failed",
    body: "We couldn't process your monthly payment. [[Update your payment details]] to keep watching.",
    verdict: "phishing",
    flags: [
      "The domain is netflix-payment-verification.com, not netflix.com",
      "Payment failure used to harvest card data",
      "Links directly to a fake payment form"
    ],
    explain: "Netflix billing issues are handled inside the app or at netflix.com — never through an email link."
  },
  {
    id: "friend-email",
    from: "sarah.nieminen@gmail.com",
    subject: "Dinner next week?",
    body: "Are you free for dinner next Thursday? Let me know what works and I'll book a table.",
    verdict: "safe",
    flags: [
      "Personal, expected correspondence",
      "No links, no urgency, no money",
      "Matches a real relationship"
    ],
    explain: "Ordinary email from someone you know. The safest emails are boring — no links, no urgency, no requests."
  },
  {
    id: "tax-refund",
    from: "Verohallinto <refund@vero-fi-taxrefund.com>",
    subject: "Tax refund of €432.50 awaiting your action",
    body: "You are entitled to a tax refund. [[Click here to claim your refund]] within 7 days or it will be forfeited.",
    verdict: "phishing",
    flags: [
      "The domain is vero-fi-taxrefund.com, not vero.fi",
      "Unexpected money with a deadline",
      "Tax authorities never refund by email link"
    ],
    explain: "The Finnish Tax Administration (Vero) never sends refunds by email. Check your tax status at vero.fi or in the OmaVero service."
  },
  {
    id: "library-due",
    from: "Helsinki City Library <ilmoitukset@helmet.fi>",
    subject: "Your book is due in 3 days",
    body: "The book 'Practical Self-Hosting' is due on 20 November. You can renew it in your library account.",
    verdict: "safe",
    flags: [
      "Correct domain (helmet.fi)",
      "Specific item and date",
      "Tells you to use your account, not click a link"
    ],
    explain: "Library notices are routine and specific. Renew through the library's own website — not through email links."
  },
  {
    id: "virus-alert",
    from: "Windows Security <alert@microsoft-security-warning.org>",
    subject: "VIRUS DETECTED — act now",
    body: "Your computer is infected with 3 viruses. [[Run a free scan now]] to remove them before they steal your files.",
    verdict: "phishing",
    flags: [
      "The domain is microsoft-security-warning.org, not microsoft.com",
      "Browser-based virus scans are always fake",
      "All-caps subject with urgency"
    ],
    explain: "A website cannot scan your computer for viruses. Close the tab and never call the phone number shown."
  }
];