/**
 * ============================================================================
 * off-client.js — Guardi's Open Food Facts data engine
 * ============================================================================
 *
 * USAGE.md (inline)
 * ------------------
 * WHAT THIS IS
 *   This is the *real* data engine behind Guardi's product readouts. It talks
 *   directly to the Open Food Facts (OFF) public API (world.openfoodfacts.org)
 *   using nothing but the global `fetch` — no npm dependencies, no SDK.
 *
 * WHERE THIS RUNS
 *   This module MUST run server-side (a Node/Deno/Bun server, or a deployed
 *   serverless function such as Vercel/Netlify — see api-scan.js in this same
 *   folder) or from some other deployed origin that can make outbound HTTPS
 *   requests. It CANNOT run inside a published Claude Artifact: Artifacts are
 *   served with a strict Content-Security-Policy that blocks all external
 *   network calls (fetch/XHR/WebSocket to any host), even though Open Food
 *   Facts itself sets permissive CORS headers and would otherwise happily
 *   accept the request. In other words: OFF is not the blocker, the Artifact
 *   sandbox is. Once Guardi is deployed to its own origin (or this file runs
 *   inside a serverless function), the calls in this module work as-is.
 *
 * RATE-LIMIT ETIQUETTE
 *   Open Food Facts asks API consumers to:
 *     - Send a descriptive User-Agent identifying the app, e.g.
 *       "Guardi/1.0 (contact: hello@guardi.app)" — do NOT ship the default
 *       browser/fetch UA. See below, `USER_AGENT`.
 *     - Avoid hammering the API — cache responses where reasonable, and don't
 *       fire duplicate lookups for the same barcode in a tight loop.
 *     - Use the `.json` / api/v2 endpoints (as this module does) rather than
 *       scraping HTML pages.
 *     - For heavy/bulk use, OFF prefers you use their data dumps or the
 *       dedicated "Search-a-licious" search API rather than hammering cgi/
 *       search.pl in production at scale. cgi/search.pl is fine for
 *       interactive, human-scale traffic (the volume Guardi expects).
 *
 * ATTRIBUTION (REQUIRED)
 *   Open Food Facts data is published under the Open Database License (ODbL).
 *   Product names, brands, images etc. are also individually licensed by
 *   contributors, generally under CC-BY-SA. Using this data requires visible
 *   attribution. Guardi's UI must show, near any OFF-derived readout, text
 *   equivalent to:
 *     "Data from Open Food Facts (openfoodfacts.org), available under the
 *      Open Database License (ODbL)."
 *   and link back to https://world.openfoodfacts.org/product/{barcode} for
 *   the specific product where practical. Do not strip attribution when
 *   caching or re-serving this data.
 *
 * HONESTY CONTRACT
 *   toGuardiReadout() only restates what OFF (and the small citation
 *   dictionary below, sourced from EWG / CSPI / OFF's own additive info)
 *   already says. It does not invent health verdicts, does not diagnose,
 *   and does not claim regulatory findings that aren't in the underlying
 *   sources. Every flag carries a `src` and, where known, a `url` so a
 *   reviewer or user can check the underlying claim themselves.
 * ============================================================================
 */

const OFF_BASE = "https://world.openfoodfacts.org";

// OFF explicitly asks integrators to identify themselves. Replace the contact
// email with Guardi's real support address before shipping.
const USER_AGENT = "Guardi/1.0 (+https://guardi.app; contact: hello@guardi.app)";

const PRODUCT_FIELDS = [
  "product_name",
  "brands",
  "ingredients_text",
  "additives_tags",
  "additives_original_tags",
  "nutriscore_grade",
  "nova_group",
  "image_front_small_url",
  "ecoscore_grade",
].join(",");

const SEARCH_FIELDS = [
  "code",
  "product_name",
  "brands",
  "nutriscore_grade",
  "nova_group",
  "additives_tags",
].join(",");

/**
 * Look up a single product by barcode (EAN/UPC/GTIN).
 *
 * @param {string|number} barcode
 * @returns {Promise<object|null>} the raw OFF `product` object, or null if
 *   OFF has no record for this barcode (status !== 1).
 */
async function lookupByBarcode(barcode) {
  if (barcode === undefined || barcode === null || String(barcode).trim() === "") {
    throw new Error("lookupByBarcode: barcode is required");
  }

  const code = encodeURIComponent(String(barcode).trim());
  const url = `${OFF_BASE}/api/v2/product/${code}.json?fields=${PRODUCT_FIELDS}`;

  const res = await fetch(url, {
    headers: { "User-Agent": USER_AGENT },
  });

  if (!res.ok) {
    throw new Error(`OFF lookupByBarcode failed: HTTP ${res.status} for barcode ${barcode}`);
  }

  const data = await res.json();

  // OFF's v2 product endpoint returns status: 1 when found, 0 when not found.
  if (!data || data.status !== 1 || !data.product) {
    return null;
  }

  return data.product;
}

/**
 * Search OFF by free-text product name.
 *
 * @param {string} name
 * @param {number} [page=1]
 * @returns {Promise<object[]>} array of raw OFF product objects (may be empty).
 */
async function searchByName(name, page = 1) {
  if (!name || !String(name).trim()) {
    throw new Error("searchByName: name is required");
  }

  const params = new URLSearchParams({
    search_terms: String(name).trim(),
    json: "1",
    page_size: "10",
    page: String(page || 1),
    fields: SEARCH_FIELDS,
  });

  const url = `${OFF_BASE}/cgi/search.pl?${params.toString()}`;

  const res = await fetch(url, {
    headers: { "User-Agent": USER_AGENT },
  });

  if (!res.ok) {
    throw new Error(`OFF searchByName failed: HTTP ${res.status} for query "${name}"`);
  }

  const data = await res.json();

  return Array.isArray(data && data.products) ? data.products : [];
}

// ----------------------------------------------------------------------------
// Additive dictionary
// ----------------------------------------------------------------------------
// Small, honest, non-exhaustive dictionary for the additives users ask about
// most often. Each entry cites where the concern comes from (EWG = Environ-
// mental Working Group's Food Scores; CSPI = Center for Science in the Public
// Interest's additive ratings; OFF = Open Food Facts' own additive/ingredient
// info). This is NOT a claim that these additives are illegal or banned
// everywhere — regulatory status varies by country and changes over time.
// Sources should be checked directly for current guidance; `url` links to a
// citable reference where available.
//
// Tags follow OFF's `additives_tags` convention: "en:e102" etc. Some non-"e"
// entries (palm oil, HFCS) are matched via ingredient text rather than an E
// number, and are handled separately in deriveFlags()/toGuardiReadout().
const ADDITIVE_DICTIONARY = {
  "en:e102": {
    name: "E102 (Tartrazine / Yellow 5)",
    sev: "med",
    txt: "A synthetic yellow dye. CSPI rates it as a concern for hyperactivity in some children and recommends caution; it also requires a warning label in the EU.",
    src: "CSPI",
    url: "https://www.cspinet.org/eating-healthy/food-safety/food-dyes-rainbow-risks",
  },
  "en:e110": {
    name: "E110 (Sunset Yellow FCF / Yellow 6)",
    sev: "med",
    txt: "A synthetic orange-yellow dye linked in some studies to hyperactivity in children; CSPI advises avoiding it.",
    src: "CSPI",
    url: "https://www.cspinet.org/eating-healthy/food-safety/food-dyes-rainbow-risks",
  },
  "en:e129": {
    name: "E129 (Allura Red / Red 40)",
    sev: "med",
    txt: "The most widely used synthetic red dye in the US. CSPI flags possible links to hyperactivity and recommends it be avoided, especially by children.",
    src: "CSPI",
    url: "https://www.cspinet.org/eating-healthy/food-safety/food-dyes-rainbow-risks",
  },
  "en:e211": {
    name: "E211 (Sodium Benzoate)",
    sev: "low",
    txt: "A common preservative. Generally recognized as safe by regulators, but can form trace benzene when combined with vitamin C, and CSPI notes it as worth watching in combination with dyes.",
    src: "CSPI",
    url: "https://www.cspinet.org/eating-healthy/chemical-cuisine",
  },
  "en:e250": {
    name: "E250 (Sodium Nitrite)",
    sev: "high",
    txt: "A curing agent used in processed meats. CSPI rates it as a concern because it can form nitrosamines, compounds linked to cancer risk, particularly in cured/processed meats.",
    src: "CSPI",
    url: "https://www.cspinet.org/eating-healthy/chemical-cuisine",
  },
  "en:e621": {
    name: "E621 (Monosodium Glutamate / MSG)",
    sev: "low",
    txt: "A flavor enhancer. Considered safe by most regulators and OFF's own data; some people report sensitivity (headaches, flushing) though controlled studies have not consistently confirmed this.",
    src: "OFF",
    url: "https://world.openfoodfacts.org/additive/e621-monosodium-glutamate",
  },
  "en:e320": {
    name: "E320 (BHA — Butylated Hydroxyanisole)",
    sev: "high",
    txt: "A synthetic antioxidant/preservative. Listed by some health agencies as \"reasonably anticipated to be a human carcinogen\"; EWG recommends minimizing exposure.",
    src: "EWG",
    url: "https://www.ewg.org/foodscores/content/food-additives/",
  },
  "en:e321": {
    name: "E321 (BHT — Butylated Hydroxytoluene)",
    sev: "med",
    txt: "A synthetic antioxidant/preservative chemically related to BHA. EWG flags it as a additive worth limiting pending more long-term safety data.",
    src: "EWG",
    url: "https://www.ewg.org/foodscores/content/food-additives/",
  },
  "en:e951": {
    name: "E951 (Aspartame)",
    sev: "med",
    txt: "An artificial sweetener. Approved by most regulators, but classified by IARC as \"possibly carcinogenic to humans\" (Group 2B) in 2023 pending more data; CSPI recommends caution.",
    src: "CSPI",
    url: "https://www.cspinet.org/eating-healthy/chemical-cuisine",
  },
  "en:e955": {
    name: "E955 (Sucralose)",
    sev: "low",
    txt: "An artificial sweetener. Generally recognized as safe, though some newer studies have raised questions about effects on gut microbiome and glucose response that CSPI flags as needing more research.",
    src: "CSPI",
    url: "https://www.cspinet.org/eating-healthy/chemical-cuisine",
  },
};

// Ingredient-text based flags (no E-number tag exists for these in OFF).
const INGREDIENT_TEXT_FLAGS = [
  {
    match: /palm oil/i,
    flag: {
      nm: "Palm Oil",
      sev: "low",
      txt: "High in saturated fat, and a major driver of tropical deforestation. Not a direct health hazard at typical intake, but flagged by EWG and sustainability groups for environmental impact.",
      src: "EWG",
      url: "https://www.ewg.org/foodscores/content/palm-oil/",
    },
  },
  {
    match: /high[\s-]?fructose corn syrup|hfcs/i,
    flag: {
      nm: "High Fructose Corn Syrup",
      sev: "med",
      txt: "A highly refined sweetener linked in observational studies to higher risk of obesity and metabolic issues when consumed in excess. CSPI recommends limiting added sugars generally, HFCS included.",
      src: "CSPI",
      url: "https://www.cspinet.org/eating-healthy/chemical-cuisine",
    },
  },
];

// Generic fallback for any additive tag we don't have a specific entry for.
// Deliberately vague and non-alarmist: we don't know enough about it to make
// a claim, so we say that plainly and point to OFF's own additive page.
function genericAdditiveFlag(tag) {
  const code = String(tag).replace(/^en:/, "").toUpperCase();
  return {
    nm: code,
    sev: "low",
    txt: `${code} is a food additive. Guardi doesn't have a specific note on it yet — check Open Food Facts' additive page for what it is and how it's used.`,
    src: "OFF",
    url: `https://world.openfoodfacts.org/additive/${String(tag).replace(/^en:/, "")}`,
  };
}

/**
 * Build the additive-derived flags for a product from its additives_tags
 * and (if present) ingredients_text.
 * @param {object} offProduct
 * @returns {Array<{nm:string, sev:string, txt:string, src:string, url:string}>}
 */
function deriveAdditiveFlags(offProduct) {
  const flags = [];
  const tags = Array.isArray(offProduct.additives_tags) ? offProduct.additives_tags : [];

  for (const tag of tags) {
    const key = String(tag).toLowerCase();
    const known = ADDITIVE_DICTIONARY[key];
    if (known) {
      flags.push({ nm: known.name, sev: known.sev, txt: known.txt, src: known.src, url: known.url });
    } else {
      const generic = genericAdditiveFlag(tag);
      flags.push(generic);
    }
  }

  const ingredientsText = offProduct.ingredients_text || "";
  if (ingredientsText) {
    for (const entry of INGREDIENT_TEXT_FLAGS) {
      if (entry.match.test(ingredientsText)) {
        // Avoid duplicate flags if OFF also tagged it (rare, but be safe).
        const already = flags.some((f) => f.nm === entry.flag.nm);
        if (!already) flags.push({ ...entry.flag });
      }
    }
  }

  return flags;
}

// Base score per Nutri-Score grade. Unknown/missing grade gets a neutral
// midpoint rather than punishing the product for missing data.
const NUTRISCORE_BASE = { a: 90, b: 75, c: 55, d: 40, e: 25 };
const DEFAULT_SCORE = 50;
const SCORE_FLOOR = 5;

/**
 * Derive Guardi's 0-100 score from Nutri-Score, NOVA group, and additive count.
 * This is intentionally simple and transparent — not a proprietary "secret
 * algorithm" — so it can be explained to a user in one sentence: "starts from
 * Nutri-Score, docked for ultra-processing and for each flagged additive."
 *
 * @param {object} offProduct
 * @returns {number} integer 0-100
 */
function deriveScore(offProduct) {
  const grade = (offProduct.nutriscore_grade || "").toLowerCase();
  let score = NUTRISCORE_BASE[grade] !== undefined ? NUTRISCORE_BASE[grade] : DEFAULT_SCORE;

  // NOVA group 4 = "ultra-processed food and drink products" per the NOVA
  // classification that OFF publishes alongside each product.
  const nova = Number(offProduct.nova_group);
  if (nova === 4) {
    score -= 15;
  }

  const additiveCount = Array.isArray(offProduct.additives_tags) ? offProduct.additives_tags.length : 0;
  score -= additiveCount * 3;

  score = Math.max(SCORE_FLOOR, Math.min(100, Math.round(score)));
  return score;
}

/**
 * Pick a short, honest one-line "bottom line" summary based on the score
 * and the strongest flag present. Does not invent claims beyond what the
 * score/flags already represent.
 */
function deriveBottomLine(score, flags) {
  const hasHigh = flags.some((f) => f.sev === "high");
  const hasMed = flags.some((f) => f.sev === "med");

  if (score >= 80 && flags.length === 0) {
    return "Solid choice — no flagged additives and a good Nutri-Score.";
  }
  if (hasHigh) {
    return "Has at least one additive some health groups recommend limiting or avoiding.";
  }
  if (hasMed) {
    return "A few additives worth knowing about — not alarming, but worth a look.";
  }
  if (score < 50) {
    return "Nutri-Score and processing level suggest this is closer to an occasional treat.";
  }
  return "Middle of the road — nothing egregious flagged, nothing to celebrate either.";
}

/**
 * Suggest a "swap" note. Guardi doesn't have a recommendation engine here —
 * this is a placeholder pointing at what a real swap feature would need
 * (a category-matched, higher-scoring alternative from OFF or a curated
 * list). We keep it honest by not inventing a specific product name.
 */
function deriveSwap(offProduct, score) {
  if (score >= 75) return null;
  return "Look for a similar product with a Nutri-Score of A or B and fewer additives in the same category.";
}

/**
 * Transform a raw Open Food Facts product into Guardi's readout shape.
 *
 * @param {object} offProduct - raw product object as returned by OFF (from
 *   lookupByBarcode() or an entry from searchByName()).
 * @returns {{
 *   id: string,
 *   name: string,
 *   brand: string,
 *   score: number,
 *   bottom: string,
 *   flags: Array<{nm:string, sev:string, txt:string, src:string, url:string}>,
 *   swap: string|null
 * }}
 */
function toGuardiReadout(offProduct) {
  if (!offProduct || typeof offProduct !== "object") {
    throw new Error("toGuardiReadout: offProduct is required");
  }

  const id = offProduct.code || offProduct._id || "";
  const name = offProduct.product_name || "Unknown product";
  const brand = offProduct.brands || "Unknown brand";

  const score = deriveScore(offProduct);
  const flags = deriveAdditiveFlags(offProduct);
  const bottom = deriveBottomLine(score, flags);
  const swap = deriveSwap(offProduct, score);

  return { id, name, brand, score, bottom, flags, swap };
}

export { lookupByBarcode, searchByName, toGuardiReadout };
