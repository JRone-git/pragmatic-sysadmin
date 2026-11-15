window.PSA = {
  key: "psa.games.v1",
  load() {
    try {
      return JSON.parse(localStorage.getItem(this.key)) || {};
    } catch {
      return {};
    }
  },
  save(patch) {
    localStorage.setItem(
      this.key,
      JSON.stringify({ ...this.load(), ...patch })
    );
  },
  track(name, data = {}) {
    if (window.plausible) plausible(name, { props: data });
    else if (window.umami) umami.track(name, data);
    else console.debug("[game]", name, data);
  },
  // Wire real Ko-fi URLs here once products exist in catalog/products.yaml.
  products: {
    "scam-safety-guide": "https://ko-fi.com/s/REPLACE",
    "tech-confidence-checklist": "https://ko-fi.com/s/REPLACE"
  },
  cta(slug, label) {
    const url = this.products[slug] || "#";
    return `<a class="psa-cta" href="${url}" data-cta="${slug}">${label}</a>`;
  }
};