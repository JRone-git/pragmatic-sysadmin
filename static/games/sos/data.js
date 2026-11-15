window.SOS_TREE = {
  start: "root",
  nodes: {
    root: {
      type: "q",
      text: "Your parent calls: “Nothing works, the internet is broken.” What do you ask first?",
      options: [
        { label: "“Is the Wi-Fi light on the router?”", next: "router" },
        { label: "“What exactly were you trying to do?”", next: "task" },
        { label: "“Did you restart it?”", next: "restart" }
      ]
    },
    task: {
      type: "q",
      text: "They say they can't open their email, but the browser opens other sites fine. What now?",
      options: [
        { label: "Ask them to open a different website to confirm", next: "only-email" },
        { label: "Tell them to restart the computer", next: "restart" }
      ]
    },
    router: {
      type: "q",
      text: "The router light is off. Is anything else in the house offline?",
      options: [
        { label: "Yes — the smart TV is offline too", next: "wifi-down" },
        { label: "No — only their phone", next: "phone-only" }
      ]
    },
    restart: {
      type: "outcome",
      title: "Restart first — but explain why",
      likely: "A restart fixes a surprising share of these calls. The risk is that it becomes the only tool in the toolbox.",
      steps: [
        "Ask them to hold the power button (not the screen) for 10 seconds.",
        "Wait 30 seconds before turning it back on.",
        "If it works, tell them what a restart does — so next time they can try it alone."
      ],
      guide: "/guides/parent-phone-sos/",
      product: "tech-confidence-checklist"
    },
    "wifi-down": {
      type: "outcome",
      title: "Whole-house outage",
      likely: "Router or ISP issue, not the device.",
      steps: [
        "Power-cycle the router (unplug 30 s, plug back in).",
        "Check the ISP's status page from your own phone.",
        "If still down, call the ISP — this is not something they did."
      ],
      guide: "/guides/home-network-triage/",
      product: "tech-confidence-checklist"
    },
    "phone-only": {
      type: "outcome",
      title: "Single-device Wi-Fi problem",
      likely: "The phone has dropped or forgotten the network.",
      steps: [
        "Settings → Wi-Fi → toggle off, then on.",
        "Re-select the home network and re-enter the password.",
        "If the password is unknown, find it on the router label."
      ],
      guide: "/guides/reconnect-phone-wifi/",
      product: "tech-confidence-checklist"
    },
    "only-email": {
      type: "outcome",
      title: "One service, not the whole internet",
      likely: "Account lock, password issue, or a service outage — not a broken computer.",
      steps: [
        "Open the provider's status page on your own device.",
        "Ask them to try logging in on a phone using mobile data.",
        "If it fails there too, it's an account problem — reset via the official site only."
      ],
      guide: "/guides/email-account-recovery/",
      product: "tech-confidence-checklist"
    }
  }
};