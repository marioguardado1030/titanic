# Guardi — Business Plan v1

**Tagline:** Know what's really in it.
**Founder:** Mario Guardado · **Status:** pre-revenue, prototype live · **Companion doc:** `execution-plan.md`

---

## 1. Executive Summary

Guardi lets anyone photograph a product — food first, then consumer goods, then beauty/personal care — and get a plain-English readout of what's in it, built from existing third-party sources (EWG, CSPI, FDA labeling data, USDA, peer-reviewed studies, recall databases). Every claim carries a citation. Guardi doesn't render verdicts; it aggregates what credentialed sources already say and shows its work. It also recommends one "cleaner swap," prioritizing small and independent brands.

The main competitor, Yuka, has ~50-85M users (estimate) and proved the demand for ingredient transparency. But Yuka refuses all manufacturer money on principle, which caps what it can build: no marketplace, no way to help small brands grow, no revenue path beyond app extras. Guardi monetizes from day one via a three-stage ladder: affiliate commissions on swaps, an owned marketplace for clean-label brands, and verified advertising where brand claims get source-checked before they run. Guardi never holds inventory.

Founder Mario Guardado is a Partner Manager at Walmart Connect, giving him direct fluency in the retail-media and marketplace mechanics the later stages depend on. He's building solo, nights and weekends, with AI coding tools; a working web prototype already exists. Immediate milestone: show the prototype to 5 people, succeed if 2+ say they'd use it.

This is pre-revenue, pre-funding. The current ask is a go/no-go read on the wedge, not capital.

---

## 2. The Problem

Consumers want to know what's in the food, household products, and personal care items they buy — additives, seed oils, synthetic dyes, endocrine disruptors — but the information is scattered, dense, and written for regulators, not shoppers.

- Ingredient labels are minimal by law and don't explain health context.
- Authoritative sources with that context — EWG, CSPI, FDA recalls, USDA, peer-reviewed literature — live in different sites and formats a normal shopper won't bridge.
- Existing tools (Yuka, Think Dirty) mostly hide sourcing behind a proprietary score, and only work if the product is barcode-scanned into their database — a miss for anything unpackaged, private-label, imported, or new.
- Small "clean" brands have no good discovery channel; consumers can't tell them apart from big brands with bigger marketing budgets.

Result: people default to vague heuristics or don't bother, and small honest brands stay invisible.

---

## 3. The Solution

Photograph a product → AI vision identifies it and its ingredients → Guardi's aggregation layer pulls what third-party sources say about those ingredients (EWG scores, CSPI concerns, FDA recall history, USDA data, relevant studies) → plain-English summary where every claim links to its source → one "cleaner swap" recommendation, weighted toward small/independent brands.

**Core positioning: Guardi is an aggregator with citations, not a judge of truth.** It doesn't claim "this ingredient is bad" — it reports "EWG rates this X for reason Y; CSPI flags concern Z; here's the primary study." This is closer to how Ground News aggregates news coverage with sourcing shown, rather than declaring a story true or false.

This matters two ways:
- **Liability.** Guardi isn't asserting novel health claims — it's citing what accredited third parties already publish, a materially lower liability posture than "our algorithm says this causes harm."
- **Monetization compatibility.** Because Guardi isn't the one judging, taking money from brands doesn't compromise the reporting — the citations are still the citations. This is the structural unlock Yuka's model forecloses (Section 5).

---

## 4. Market

Figures below are estimates from general market awareness, not sourced statistics — directional only.

- **Clean-label/healthy food:** widely estimated as a multi-billion-dollar category growing at high-single to low-double-digit rates annually — a common but imprecise estimate.
- **Clean beauty/personal care:** also frequently cited as a large, fast-growing segment, though "clean" is an unregulated marketing term industry-wide — an opening for Guardi's citation-based approach.
- **Proxy demand validation:** Yuka's own scale (~50-85M users, estimate) is the strongest evidence a mass audience wants ingredient transparency without a black-box score.
- **Consumer goods generally:** the largest eventual surface, but the least proven wedge — deliberately sequenced last.

Guardi isn't creating net-new demand. The bet is a better experience (photo vs. barcode) and a monetization model the incumbent can't pursue.

---

## 5. Competition & Positioning

**Yuka** built its user base on a clear principle: no manufacturer money, so scores can't be bought. That integrity is real. But it's also Yuka's ceiling — it can't accept brand advertising, can't build a marketplace without looking like an endorsement, and has no seller-side business to help small honest brands grow. Its core interaction (barcode scan) fails silently on anything not in its database, and its home screen is a scan button, not a place to browse or return to.

Guardi's aggregator-with-citations model sidesteps the "no manufacturer money" trap: since the cited sources are the judge, not Guardi, a swap commission or verified ad doesn't quietly change the verdict.

| | Yuka | Guardi |
|---|---|---|
| Input method | Barcode scan | Photo (AI vision), works on unscanned products |
| Verdict style | Proprietary score (implicit judgment) | Cited claims from named sources (explicit sourcing) |
| Revenue from brands | None, by design | Affiliate, marketplace, verified ads |
| Small-brand support | None | Prioritized in swap recs; marketplace seller path |
| Home screen | Scan-only utility | Browsable, discovery-oriented |
| Scale | ~50-85M users (estimate) | Pre-launch |

**The broader field (reality check).** Yuka is the giant, but the scanner category is crowded — and, importantly, the "AI vision + cleaner swaps + plain-English" angle is already shipping:

| App | Position | Overlap |
|---|---|---|
| CheckIt AI | Real-time visual AI scan (no barcode), AR shelf, recall alerts | High — same "photograph anything" pitch |
| Olive | Ultra-processed detection + cleaner-swap suggestions | High — the swaps too |
| Gud For Us | Photo scan, plain-language, personal profile | Medium-high |
| Fooducate, Trash Panda | Food grades + "what the research says" | Medium (citation-style) |
| Think Dirty, INCI Beauty, EWG Healthy Living | Cosmetics/beauty scanners | Category overlap (beauty) |
| Buycott | Scan → parent company / values alignment | Values angle |

**Honest implication:** the scanner itself is **table stakes, not the moat** — CheckIt AI, Olive and Gud For Us already do AI-vision scanning with swaps and plain-English readouts. What **none** of them are is a **marketplace**: none connect buyers to small sellers, rank small brands first, or monetize via verified brand ads. Guardi's defensible position is therefore the **commerce + small-brand engine + verified ads**, not "better scanning" — which aligns exactly with the founder's retail-media expertise. Positioning must lead with the marketplace/values-commerce story; the scanner is the acquisition hook, not the differentiator.

**Build-vs-buy — don't build the database.** The product/ingredient data is a solved, free problem: **Open Food Facts** (2.8M+ products, additives, NOVA/Nutri-Score, allergens) with an official JS SDK plus Python/Dart wrappers and an AI service (Robotoff). Guardi builds the *experience and the commerce layer* on top; it does not rebuild the food database.

Secondary reference points: Ground News proves aggregator-with-citations can be a standalone trusted brand (in news). Thrive Market proves a curated clean-label marketplace has commercial demand, though as a closed-catalog retailer, not a scanner. Amazon/Walmart marketplace mechanics (seller fees, sponsored placement, verified selling) are the model for Stages 2-3 — and the founder's day job.

---

## 6. Business Model

Asset-light at every stage — Guardi never buys, stores, or ships inventory.

**Stage 1 — Affiliate commissions (start here).** One cleaner swap per scan, commission on purchase through an affiliate link. Typical norms run roughly 5-20% of sale value depending on category (food/CPG often 5-10%, specialty/DTC sometimes higher — estimates, not confirmed program terms). Zero inventory risk, no upfront brand relationships needed. Validates which swaps convert.

**Stage 2 — Owned marketplace.** Once swap-conversion data and an engaged user base exist, open direct listings for small clean-label brands; Guardi takes a transaction cut (marketplaces commonly charge roughly high-single-digits to ~15%, an estimate, not a committed number). Converts Guardi from referral layer to sales channel.

**Stage 3 — Verified ads.** Brands pay to promote, but their claims get source-triangulated against the same citation base used for scans before the ad runs — "ad integrity as a feature." This is where Guardi looks most like a retail media network, and where the founder's domain expertise applies most directly (Section 8).

Stages are additive — by Stage 3, ideally all three revenue lines run simultaneously, similar to how Amazon and Walmart layer retail, marketplace, and ad revenue today.

---

## 7. Why Now

1. **AI vision + LLM aggregation just became cheap.** Reliable photo-based ingredient ID and multi-source synthesis weren't viable for a solo builder a few years ago; today they run on consumer-grade APIs a nights-and-weekends project can afford.
2. **The clean-label wave is mainstream.** Ingredient scrutiny has moved from niche to a default expectation for a large segment (Yuka's scale, clean-label/beauty growth in Section 4).
3. **Retail media is booming.** Brands are shifting budget toward retail media networks (Walmart Connect, Amazon Ads, Instacart Ads) because they convert closer to purchase. Guardi's Stage 3 rides that shift with a differentiated pitch: verified, source-checked claims, not just placement.

---

## 8. Founder Edge

Mario Guardado is a Partner Manager at Walmart Connect, giving him practitioner-level exposure to how brands plan and buy retail media, how a marketplace monetizes sellers at scale, and how CPG partners think about claims and brand safety — directly relevant to designing Stage 3's claim-checking workflow.

He is not an engineer; he's building solo, nights and weekends, with AI coding tools, and already has a working web prototype. The technical build happens in spare capacity while the commercial design of Stages 2-3 — usually the harder part for technical founders — is shaped by someone who does this professionally at scale. The open question isn't domain competence; it's execution bandwidth and the conflict-of-interest handling in Section 10.

---

## 9. Go-To-Market

1. **Wedge: food scanner.** Launch food-only, where the source base (USDA, FDA, CSPI, EWG food data) is richest. Also where Yuka is most entrenched, making the photo-vs-barcode and citation-vs-score differences easiest to feel.
2. **Content/social loops.** The shareable moment is "wait, THAT'S in it?" — screenshot-and-share native, similar to how Yuka scans go viral on TikTok/Instagram. Organic content is the primary early channel, not paid.
3. **Local purchase, early.** Guardi's magic moment happens in a store aisle, so the swap should be buyable *here, today*, not just shippable. Classic affiliate doesn't cover in-store buys (attribution), so the local path is staged: (a) direct one-city partnerships with local grocers — "available at [store], aisle 5" plus per-redemption promo deals — retail-media business development, the founder's home discipline; (b) receipt-scan / cashback mechanics (the Ibotta model) to attribute true in-store purchases; (c) *optional bridge only:* grocery-delivery affiliates (Instacart et al.) — turnkey local feel, but it stacks a second middleman that thins the cut and shares data with another platform, so it's a tactic, never the strategy.

**Platform-exposure policy (founder decision):** no Amazon Associates in Stage 1. Reasons: affiliate rate risk (Amazon cut rates from ~8% to 1–3% overnight in 2020), strategic dependence on a platform with a documented history of cloning what works on it, and brand mismatch — "we champion small honest brands" can't route checkout to Amazon. Deeper Big-Tech integrations (marketplace selling, investment conversations) are deferred until Guardi has its own audience and leverage.
4. **Small-brand partnerships.** With real swap-click data, approach small clean-label brands as affiliate/discovery partners — building the seller relationships Stage 2 needs.
5. **Marketplace.** Once data shows which swaps convert and which brands want deeper ties, open direct listings online — converting the strongest affiliate partners *and* pilot-city local sellers into the first marketplace tenants.

Immediate next step: the demand test — 5 people, prototype, 2+ "I'd use this" reactions as the green light.

---

## 10. Risks & Honest Answers

**Liability around health claims.** Photographing ingredients and reporting health implications risks reading as medical claims. *Mitigation:* the citation-only, aggregator-not-judge model reports what named sources say, not independent medical fact. UI copy must reflect this precisely (attribution on every claim, not a footnote), and health-adjacent claims should get counsel review before shipping — treated here as a real open task, not solved.

**Yuka could add affiliate/marketplace features itself.** Nothing stops it. *Honest answer:* Yuka's brand is built on "we take no manufacturer money," repeated in its own marketing for years — reversing that costs it credibility in a way it wouldn't cost Guardi, which never made that promise. A positioning moat, not a technical one — worth monitoring, not assuming permanent.

**Conflict of interest with the founder's employer.** Mario works at Walmart Connect while building a company whose Stage 3 is also a retail-media-style ad product. *This needs careful, explicit handling, not a shrug:* review Walmart's moonlighting/outside-work and IP assignment policies before Stage 2/3 development goes further, confirm Guardi is built on personal time/equipment with no use of Walmart confidential information, and consider disclosure to Walmart once the overlap becomes commercially real rather than hypothetical. At this pre-revenue stage it's a flag to track, and a gating item before fundraising or launching the ad product specifically.

**Data accuracy.** Aggregating EWG/CSPI/FDA/USDA/study sources correctly, keeping citations current, and handling source disagreement is an ongoing operational burden, not a one-time build. *Mitigation:* the product's promise is "we show you what sources say" — disagreement should be surfaced as disagreement, not silently resolved, which is consistent with the framing but requires deliberate UX work.

---

## 11. Financial Sketch

Pre-revenue. This is a directional sketch of Stage 1 (affiliate) economics — every number is a scenario input, not a measured result.

| MAU | Scans/user/mo (assumption) | Swap click-through (assumption) | Purchase rate (assumption) | Avg. order value (assumption) | Commission (assumption) | Rough monthly affiliate revenue |
|---|---|---|---|---|---|---|
| 1,000 | 4 | 10% | 10% | $15 | 8% | ~$48 |
| 10,000 | 4 | 10% | 10% | $15 | 8% | ~$480 |
| 100,000 | 4 | 10% | 10% | $15 | 8% | ~$4,800 |

Worked example at 1,000 MAU: 4,000 scans → 10% click a swap (400) → 10% of those buy (40) → × $15 avg order = $600 in sales → × 8% commission = **~$48/mo**. Each 10× in users is roughly 10× in revenue under these placeholder assumptions.

These per-MAU figures are illustrative only, built on placeholder assumptions, to show the shape of the model — not a projection. Real inputs come from Stage 1 usage data once the app is live; the near-term goal is getting that instrumentation in place. Marketplace and ad revenue aren't modeled — they depend on user scale and seller relationships that don't exist yet.

Cost structure is minimal: AI API costs per scan, hosting, and the founder's own unpaid time. No team, no inventory, no fulfillment — consistent with the asset-light positioning throughout.

---

## 12. The Ask / Next Milestones

Guardi is not raising capital at this stage. The ask is validation, not funding:

1. **Run the demand test** — 5 real people, prototype, success = 2+ "I'd use this" or visible surprise.
2. **If it passes:** deepen food-category source integrations (EWG/CSPI/FDA/USDA), tighten citation UX so sourcing is unmissable, begin outreach to a few independent clean-label food brands for early affiliate relationships.
3. **If it fails or is ambiguous:** revisit the wedge — check whether the readout format, category, or framing is the weak link before concluding the core idea is wrong.
4. **In parallel, not blocking:** start the conflict-of-interest review relative to the founder's Walmart Connect role (Section 10), so it's resolved well before Stage 3 becomes a real build.

No hiring, fundraising, or marketplace build is planned until the demand test and initial affiliate data provide real signal. Stages 2 and 3 wait until Stage 1 proves anyone wants Stage 1.
