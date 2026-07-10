# Guardi — Production Architecture

**Status:** Design document for the path from prototype (`guardi/index.html`, sample data,
published as a Claude artifact) to a real deployed app. Nothing below is built yet unless
labeled "prototype has this." Companion docs: `docs/business-plan.md`, `docs/execution-plan.md`.

---

## 1. System overview

Guardi is three thin layers: a mobile-web client, a serverless API that fans out to a
handful of free/cheap external services, and two cross-cutting modules (analytics,
ad-ranking) that sit inside the API layer rather than as separate systems.

```
                         ┌─────────────────────────────┐
                         │      MOBILE WEB CLIENT       │
                         │   (PWA — React/HTML+JS)      │
                         │                               │
                         │  camera capture  →  scan UI   │
                         │  results list    ←  swap card │
                         └───────────────┬───────────────┘
                                         │ HTTPS (photo or barcode string)
                                         ▼
                         ┌─────────────────────────────┐
                         │      SERVERLESS API          │
                         │  (Vercel/Netlify/Cloudflare   │
                         │   function — holds API keys)  │
                         │                               │
                         │  /scan   /search   /nearby     │
                         └───┬───────┬───────┬───────┬───┘
                             │       │       │       │
              ┌──────────────┘   ┌───┘   ┌───┘   ┌───┘
              ▼                  ▼       ▼       ▼
      ┌───────────────┐  ┌─────────────┐ ┌──────────────┐ ┌─────────────────┐
      │ Claude Vision  │  │ Open Food   │ │ OpenStreetMap│ │ Affiliate links  │
      │ (identify      │  │ Facts       │ │ / Overpass   │ │ (ShareASale,     │
      │ product/       │  │ (ingredients,│ │ + browser    │ │ Impact, direct   │
      │ barcode)       │  │ NOVA, Nutri-│ │ Geolocation  │ │ brand programs)  │
      │                │  │ Score, ODbL) │ │ (nearby      │ │                  │
      └───────────────┘  └─────────────┘ │  stores)      │ └─────────────────┘
                                          └──────────────┘
                             │
                    ┌────────┴─────────┐
                    ▼                  ▼
           ┌─────────────────┐ ┌───────────────────┐
           │  AD-RANKING      │ │  ANALYTICS         │
           │  MODULE          │ │  MODULE             │
           │  (slot 1/3        │ │  (Plausible/PostHog│
           │  organic, 2/4     │ │  events: scans,    │
           │  sponsored, rest  │ │  swap clicks, ad    │
           │  values-mixed;    │ │  impressions,       │
           │  monetization     │ │  retention)         │
           │  on/off flag)     │ │                     │
           └─────────────────┘ └───────────────────┘
```

Both modules live as code paths *inside* the serverless API — they are not separate
servers. Analytics writes events on every request; ad-ranking runs only when building the
swap-results list, and is a no-op (organic-only) while the monetization flag is off.

---

## 2. Frontend

**Form factor: mobile-first Progressive Web App (PWA), not a native app — at least
through the 90-day plan and likely well beyond it.**

| Aspect | Choice | Why |
|---|---|---|
| Framework | Plain HTML/CSS/JS today (the artifact prototype); React or similar once the backend lands, if component complexity demands it | Prototype is already a working single-file app; don't rewrite before validating demand |
| Camera capture | `<input type="file" accept="image/*" capture="environment">` on mobile Safari/Chrome; `getUserMedia` for a live in-page camera view on desktop/testing | `<input capture>` is the reliable cross-browser baseline on phones — no permissions dance, no iOS Safari getUserMedia quirks in a PWA context |
| Install | "Add to Home Screen" via a Web App Manifest + service worker | Gets an app-icon, full-screen feel, and offline shell without an App Store review cycle |
| Distribution | Shareable URL (text a link, QR code at a farmers market table, etc.) | Zero-friction distribution is the whole point of nights-and-weekends solo growth — no $99/yr developer account, no 1-2 week review wait, no forced 30% IAP cut if a marketplace ever needs in-app purchases |

**Why PWA before native App Store, explicitly:** the app's core loop (photo → answer) needs
a camera and a screen, not push notifications, native background jobs, or deep OS
integration. A PWA ships in minutes (redeploy = live), works on iOS and Android from one
codebase, and defers the App Store's cost, review risk, and platform lock-in until there's
evidence (from Day 90 metrics — see `execution-plan.md` §5) that native distribution or
App Store discovery actually moves the needle. The 90-day plan already frames this as an
explicit Day 61-90 decision, defaulting to PWA unless data says otherwise.

---

## 3. The scan pipeline

```
1. User photographs a product (or types a search / scans a barcode string)
        ↓
2. Photo (base64/blob) → serverless /scan endpoint
        ↓
3. Claude vision call: "what product is this, and/or what barcode is visible?"
   → returns a best-guess product name + brand + optional barcode number
        ↓
4. Open Food Facts lookup by barcode (exact) or by name/brand (fuzzy search fallback)
   → returns ingredients list, additives, NOVA group, Nutri-Score, allergens, images
        ↓
5. toGuardiReadout(offProduct) — a pure transform function that maps raw OFF JSON into
   Guardi's plain-English shape: health flags, environment flags, source citations,
   confidence level, and a candidate swap query
        ↓
6. Ad-ranking module orders the swap/alternatives list (organic small-biz first per the
   slot model in §5); analytics module logs the scan + result event
        ↓
7. Client renders: plain-English readout, cited sources, ranked swap card(s)
```

Step 4 is the load-bearing step and the reason Open Food Facts was chosen over building a
database from scratch (see `business-plan.md`): it is free, has no API key requirement,
and already covers 2.8M+ products with structured additive/NOVA/Nutri-Score data.

**Explicit limitation — no free API gives per-store shelf inventory.** Open Food Facts
tells you what's *in* a product, not *where* it's physically sitting on a shelf today.
"Is this in stock at the store three blocks from me" is a fundamentally different,
partnership-gated data problem — it requires a retailer's live POS/inventory feed, which
no free or public API exposes. That capability arrives later via a formal **Instacart or
Mercatus partnership** (Mercatus being the platform, owned by Instacart, that already
powers many independent grocers' online storefronts — see execution-plan.md's Fairway
Market analysis). Until that partnership exists, the app can tell a user what a product
is and whether a cleaner alternative exists in the abstract; it cannot tell them which
physical store to walk into. Any "available near you" UI before that partnership should
degrade honestly to "search this online" / affiliate-link behavior, not a fabricated
in-stock claim.

---

## 4. Data sources

| Source | Used for | License / cost | Notes |
|---|---|---|---|
| **Open Food Facts (OFF)** | Ingredients, additives, NOVA processing group, Nutri-Score, allergens, product images | Free, no API key, **ODbL (Open Database License)** | ODbL requires attribution and share-alike on any *database* derived from OFF — a visible "Data from Open Food Facts" credit + link on every readout satisfies attribution; Guardi is consuming/transforming per-query, not redistributing a derived database, but attribute anyway as a trust signal and a legal safety margin |
| **OpenStreetMap / Overpass API** | Finding nearby grocery stores/pharmacies for the "where to buy locally" surface | Free, no key; ODbL-style attribution (© OpenStreetMap contributors) | Overpass has informal rate limits (fair-use, not a hard quota) — cache nearby-store results client-side or per-geohash server-side once volume grows |
| **Browser Geolocation API** | User's current position, to query Overpass "near me" | Free, built into the browser | Requires explicit user permission prompt; must work (degrade gracefully) if denied |
| **Claude vision (Anthropic API)** | Identifying the product/barcode from a photo | Paid, per-token/per-image — see §8 for cost estimate | The one paid, load-bearing external dependency in the scan pipeline |
| **EWG (Environmental Working Group), CSPI (Center for Science in the Public Interest)** | Curated context/citations on specific additives or ingredient categories (e.g., "titanium dioxide — EWG concern level") | **No open API from either org** | These are **curated and linked, not programmatically queried**. Practically: build (and periodically hand-update) a small static reference table mapping known additives/ingredient flags → a citation URL and a one-line curated summary, maintained by the founder, not fetched live. This is also the top trust-risk mitigation named in the execution plan — a static curated set avoids the model hallucinating a citation that doesn't exist |
| **Instacart / Mercatus** (future) | Real per-store inventory/availability | Partnership-gated, not a public API | See §3 and §9 — Stage 2, not launch |
| **Affiliate networks** (ShareASale, Impact, direct brand programs) | Swap-card purchase links | Free to join; revenue-share, not a cost | Not a data source for product truth — purely commercial, kept separate per §7 |

---

## 5. Ad-ranking engine

This is the mechanic that lets Guardi monetize without becoming "just another ad-ranked
feed" — it's worth being explicit about, because it's the core brand-integrity claim.

**The slot model**, for any result list showing N alternatives/swaps:

| Slot | Type | Who decides it | Labeling |
|---|---|---|---|
| 1 | Organic — small/independent brand | Earned, by the ranking formula below | Unlabeled (it's the default, non-paid state) |
| 2 | Sponsored — larger enterprise brand | Paid placement | Clearly labeled "Sponsored" / "Ad" inline, not just in a tooltip |
| 3 | Organic — small/independent brand | Earned | Unlabeled |
| 4 | Sponsored — larger enterprise brand | Paid placement | Labeled "Sponsored" / "Ad" |
| 5+ | Values-weighted mixed pool | Blend of organic score and, if monetization is on, a lighter paid-boost weight | Sponsored items in this range still labeled |

**Monetization on/off flag.** A single config flag (env var or remote config value) controls
whether slots 2/4 (and any paid boost past slot 4) are populated at all:
- **Off (launch state):** slots 2/4 are simply *not sold* — they either sit empty, collapse,
  or are backfilled with the next-best organic result. No ad code path executes.
- **On (post-traction):** slots 2/4 activate for paying sponsors; the organic slots (1/3)
  and their ranking formula are completely untouched by the flag — flipping monetization on
  never changes what makes slot 1 vs slot 3 vs slot 5 organically.

**How organic ranking is computed — so it can't simply be bought.** The slot-1/3 ranking
is a formula over signals no advertiser payment can touch:
- Company size/independence signal (employee count tier, private vs. large-conglomerate
  ownership — sourced from a small curated brand registry the founder maintains, not
  self-reported by brands)
- Ingredient/health/environment score fit relative to the scanned product (cleaner NOVA
  group, fewer flagged additives, better Nutri-Score, closer match to what the user scanned)
- Affiliate-availability (can the user actually buy it via a live affiliate link — a swap
  nobody can purchase is a bad recommendation regardless of how "clean" it is)
- A small exploration/diversity term so one small brand doesn't permanently monopolize
  slot 1 for a given product category

None of these inputs is "did this brand pay us." A large enterprise brand cannot buy its
way into slot 1 or 3 — its only paid path is the explicitly labeled slot 2/4 sponsored
inventory. This separation (paid buys *placement*, never buys *rank-among-organic* or
*the health verdict*) is what should be said out loud to users, in-app, in an "how we rank"
explainer — it is the single biggest thing protecting the brand once money is flowing.

**FTC / native-ad honesty:** every slot 2/4 item and every values-mixed-pool item that is
paid must carry a persistent, visually distinct "Sponsored" or "Ad" marker adjacent to the
item (not just in a hover state or footnote) — this mirrors FTC native-advertising guidance
and the existing affiliate-disclosure requirement already noted in
`execution-plan.md` §10.

---

## 6. Analytics & the "become the market" tracker

**Recommended tool:** Plausible or PostHog (both have a workable free tier at this scale,
both are privacy-friendlier than Google Analytics — no cross-site cookie tracking, easier
GDPR/CCPA posture). PostHog's edge is event-level product analytics (funnels, retention
cohorts) if the founder wants to self-serve those views without a spreadsheet; Plausible's
edge is simplicity and a lighter footprint if only high-level traffic trends matter early.
Either is a reasonable Day 1-30 choice per the execution plan; a spreadsheet-via-webhook is
an acceptable zero-cost stopgap before either is wired up.

**Events to log:**

| Event | Fields | Why it matters |
|---|---|---|
| `scan_started` | timestamp, anonymous session id | Funnel entry point |
| `scan_completed` | product id/name, confidence, NOVA/Nutri-Score, latency | Core usage volume; latency flags a slow/broken pipeline |
| `search_performed` | query text (no PII), result count | Demand signal for products not yet easily scanned |
| `product_viewed` | product id, source (scan vs. search) | Distinguishes browsing from active scanning |
| `swap_click` | swap product id, slot number, sponsored (bool) | The single most important trust+monetization signal — is the recommendation actually acted on |
| `ad_impression` | slot number, sponsor id | Required before any sponsor can be billed on impressions |
| `ad_click` | slot number, sponsor id | Required before any sponsor can be billed on clicks |
| `session_return` | days since last session | Feeds the returning-user / retention metric directly |

**Thresholds that justify flipping monetization on** (aligned with the Day-90 bars in
`execution-plan.md` §5): sustained 100+ monthly active users, a non-trivial swap-click
rate (evidence the organic recommendations are already trusted before ads are introduced —
selling ad slots into a feed nobody clicks is worthless inventory), and at least a couple
of unprompted brand inquiries about paid placement. Flipping the flag on before organic
trust is established risks poisoning the "slot 1/3 is earned" credibility the whole engine
depends on.

---

## 7. Trust & integrity

Guardi's own framing (from `README.md`): **an aggregator with citations, not a judge of
truth** — it reports what sources say and links every claim, rather than asserting an
independent verdict.

- **Every claim cited.** Ingredient/NOVA/Nutri-Score claims cite Open Food Facts directly
  (with attribution per §4); any EWG/CSPI-style commentary cites the specific curated
  reference entry, never a bare unlinked assertion.
- **Paid placement never touches the health verdict.** The NOVA group, Nutri-Score,
  additive flags, and citation set for a given product are computed once, from OFF data,
  before the ad-ranking module ever runs. The ad-ranking module only reorders *which
  alternatives* are shown and *in what slot* — it has no code path that can alter a
  product's own health/environment readout. This separation should be an explicit
  architectural invariant (health computation and ad computation are different functions
  that never share a mutation path), not just a policy.
- **Disclaimers.** Every readout carries a persistent "informational summary of publicly
  cited sources, not medical/health advice — consult a professional" line, per
  `execution-plan.md` §10.
- **FTC disclosures.** Affiliate links carry "contains affiliate links, Guardi may earn a
  commission"; sponsored slots carry the "Sponsored"/"Ad" marker described in §5. Both are
  disclosure obligations already flagged as launch-blocking in the execution plan, not
  optional polish.

---

## 8. Cost & scaling

*(Estimates only — the execution plan already flags these as rough until validated with
real test scans; do not treat any number below as a quote.)*

| Item | Estimate | Grows with |
|---|---|---|
| Claude vision, per scan | A few cents at most, likely well under $0.05/scan depending on image size/model choice (validate with 20-30 real test scans) | Volume; mitigations are output caching for repeat/common products and prompt/image-size tuning |
| Open Food Facts | $0 (free, no key, no quota beyond fair use) | Does not grow with cost — it's a genuinely free public dataset |
| OpenStreetMap/Overpass, Nominatim | $0 at low volume (fair-use limits, not billed) | May need a caching layer or a paid Overpass instance only at meaningfully large scale |
| Serverless hosting (Vercel/Netlify/Cloudflare) | $0 on free tier | Function invocations and bandwidth — grows with traffic, but free tiers cover thousands of users before billing kicks in |
| Analytics (Plausible/PostHog) | $0 on free tier | Event volume; both have paid tiers once monthly events exceed the free allotment |
| **Where cost actually grows:** | Claude vision calls scale roughly linearly with scans, and are the only line item with real per-user marginal cost — everything else is flat-$0 until a much larger volume threshold | Revisit model choice/caching strategy once monthly scans move from hundreds into the thousands+ range (per execution-plan.md §6 budget table) |

---

## 9. Build sequence

| Stage | What it is | Status |
|---|---|---|
| **Prototype (today)** | Static sample-data client (`guardi/index.html`), no camera, no backend, no real API calls, published as a Claude artifact | **Done** |
| **Deploy unlocks (Days 1-30)** | Real camera capture; a live serverless function; real Claude vision + Open Food Facts calls wired into the pipeline in §3; basic analytics; a real deployed URL instead of an artifact-only link | Not started — this doc describes the target shape |
| **Commerce unlocks (Days 31-60)** | Affiliate links wired to the swap card with disclosure; ad-ranking module's organic formula (§5) live, monetization flag still off; first small-brand affiliate relationships | Depends on Day 1-30 backend existing first |
| **Partnership-gated (Stage 2+)** | Real per-store inventory/availability (needs an Instacart/Mercatus partnership — not a solo build task); monetization flag flipped on (needs the traction thresholds in §6); owned marketplace checkout (needs affiliate-margin data to justify the build) | Explicitly deferred — these require either external partnerships or traction data that doesn't exist yet |

---

## 10. Risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| **Claude vision misidentifies a product** | Wrong product → wrong ingredients → wrong health claim shown to a real person; the single scariest failure mode for a health-adjacent app | Show a confidence indicator; let the user confirm/correct the identified product before showing a verdict; weekly manual QA of scan output during early volume (already planned in execution-plan.md §3); prefer barcode match (exact) over name-fuzzy-match (approximate) whenever a barcode is visible |
| **Open Food Facts data gaps or wrong entries** | OFF is crowdsourced — some products are missing, mislabeled, or stale, especially newer/regional/small-brand products (ironically the exact products Guardi wants to favor) | Degrade honestly to "we don't have enough data on this yet" rather than guessing; consider a lightweight founder-reviewed correction/flag path once volume justifies it |
| **Ad-integrity perception** | Even a well-built slot 1/3-organic model can *look* like pay-to-play if labeling is subtle or the "how we rank" explanation isn't visible; one viral "Guardi sold out" post could be existential for a trust-based brand | Make the organic-vs-sponsored separation loud and simple in the UI (§5); publish the ranking explainer; keep the health-verdict/ad-ranking code paths structurally separate (§7) so it's provably true, not just claimed |
| **Per-store inventory absence** | Users may expect "is this near me" to mean "in stock at that exact store right now" — a gap the current architecture cannot close without a partnership | Be explicit in-product about what "near you" currently means (stores that carry this *category*, not live shelf inventory) until an Instacart/Mercatus partnership lands; don't imply real-time stock data that doesn't exist |
