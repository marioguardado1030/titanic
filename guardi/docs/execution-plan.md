# Guardi — 90-Day Execution Plan v1

**Founder:** Mario Guardado (solo, nights-and-weekends, non-engineer, builds with AI tools)
**Current state:** Clickable web prototype (static sample data, no backend, no camera) at `guardi/index.html`, published as a private artifact.
**Prepared for:** Lead editor review — working draft, not locked.

---

## 1. Operating Principles

| Principle | Meaning |
|---|---|
| Solo + AI agents | Every estimate assumes Mario + Claude Code, not a team |
| Validate before building | No phase starts until the prior gate is passed |
| Smallest real thing first | Ship the thinnest version that produces a real signal |
| Every phase has a kill/proceed gate | Fail a gate → stop and rethink, don't quietly keep building |
| Nights-and-weekends is the constraint | ~8-10 hrs/week; cut scope, not sleep |

---

## 2. THIS WEEKEND — Validation Sprint

**Goal:** 5 real people, honest proceed/kill signal.

| When | Task | Solo | w/ AI |
|---|---|---|---|
| Fri | Deploy `index.html` to GitHub Pages/Vercel (real URL, not artifact-only) | 45-60 min | 15-20 min |
| Fri | Write 3-question test script (use it? trust it? click a swap?) | 30 min | 10 min |
| Fri | DM 5-8 real people — not family — friends, Walmart colleagues, retail-media contacts | 30 min | n/a |
| Sat | Run 5 sessions, watch live, don't explain, just observe | 2-3 hrs | n/a (un-outsourceable) |
| Sat | Log reactions (table below) | 20 min | 10 min |
| Sun | Tally, apply gate, write 1-paragraph decision memo | 1 hr | 20 min |

**Reaction log:**

| Tester | Relationship | "I'd use this" (Y/N) | Trust in sources (1-5) | Would click swap (Y/N) | Best quote |
|---|---|---|---|---|---|
| 1-5 | | | | | |

**Gate:** 2+ of 5 say "I'd use this" → proceed. Else → kill or redesign before spending more.

---

## 3. Days 1-30 — "Make It Real"

**Goal:** Real camera + real AI backend. 25 real users. Basic analytics.

| # | Task | Solo | w/ AI | Notes |
|---|---|---|---|---|
| 1 | Real camera capture (`getUserMedia` desktop, `<input capture>` mobile) | 6-10 hrs | 2-4 hrs | Test actual phones — Safari iOS is the gotcha |
| 2 | Lock structured output schema (name, category, health/env flags, cited sources, one swap) | 2-3 hrs | 1 hr | Do before wiring the API |
| 3 | Backend call: photo/name → Claude API (vision) → structured JSON w/ citations | 10-15 hrs | 4-6 hrs | Needs a thin serverless function to hold the API key |
| 4 | Source strategy: curated static reference set (EWG/CSPI/FDA/USDA) model cites against, not open scraping | 4-6 hrs | 2-3 hrs | Reduces hallucinated citations — top trust risk |
| 5 | Log rough API cost/scan | 30 min | 15 min | See Section 6 |
| 6 | Deploy to a real domain | 1-2 hrs | 30 min | |
| 7 | Recruit 25 users (friends, social, Walmart network) | 3-5 hrs/mo | same | Relationship work, AI doesn't help much |
| 8 | Basic analytics: scans/user, swap-click rate (Plausible/PostHog free tier, or a sheet via webhook) | 3-4 hrs | 1-2 hrs | Don't over-engineer at this scale |
| 9 | Weekly manual QA: read every scan result, flag bad/hallucinated output | 1 hr/wk | 1 hr/wk | Safety net until volume forces automation |

**Gate (Day 30):** 25 users, 40%+ do a second scan, no "clearly wrong/dangerous" health-claim feedback. If missed, diagnose trust (citations) vs. UX (camera friction) vs. demand before Day 31.

---

## 4. Days 31-60 — "First Dollar"

**Goal:** First affiliate dollar. 100 users. Early small-brand relationships.

| # | Task | Solo | w/ AI | Notes |
|---|---|---|---|---|
| 1 | Apply: Amazon Associates | 1-2 hrs + wait | same | Needs live site w/ traffic |
| 2 | Apply: Thrive Market, iHerb, ShareASale (gateway to small brands) | 2-3 hrs | 1 hr | |
| 2b | Apply: Instacart (or DoorDash) affiliate — the "buy it at YOUR local store" path | 1-2 hrs | same | Local-store fulfillment with online-checkout attribution; makes swaps feel local from day 1 |
| 3 | Wire swap card → affiliate link w/ disclosure | 4-6 hrs | 2 hrs | One link-resolution layer so networks can change later |
| 4 | Build outreach list: 20-30 small clean-label brands | 3-4 hrs | 1-2 hrs (AI drafts) | Target categories that show up most in scans |
| 5 | Recruit 5-10 brands for direct partnership talks — founder's home turf | 6-10 hrs/mo | same | Pitch: "rank first for values-aligned shoppers" |
| 6 | Track clicks → conversions | 2 hrs | 1 hr | |
| 7 | Push 25 → 100 users via referral + 1-2 community posts | ~2 hrs/wk | same | No paid ads yet |

**Gate (Day 60):** $1+ real affiliate revenue AND 100 users AND 3+ brand conversations past first contact. Brands ghosting is fine if affiliate infra works; zero swap clicks at all is a monetization problem to fix before Day 61.

---

## 5. Days 61-90 — "Decide the Future"

**Goal:** Fork-in-the-road decisions, backed by data.

| # | Task | Solo | w/ AI | Notes |
|---|---|---|---|---|
| 1 | iOS decision: PWA vs native vs App Store | 3-4 hrs | 1-2 hrs | Default PWA unless data says otherwise (App Store = weeks + $99/yr + review risk) |
| 2 | Scope marketplace v0 (own checkout vs. stay affiliate-only) | 4-6 hrs | 2 hrs | Only worth it if affiliate margins/attribution are visibly leaky |
| 2b | Scope one-city local pilot: 2-3 local grocers, "available at [store]" + per-redemption promo codes; receipt-scan attribution as fallback | 4-6 hrs | 2-3 hrs | Retail-media BD — founder's home discipline; pilot sellers become first marketplace tenants |
| 3 | Verified-ads pitch deck for brands (founder's retail-media edge) | 6-8 hrs | 3-4 hrs (AI drafts, Mario edits) | Strongest edge — lean in |
| 4 | Fundraise-or-bootstrap framework (below) | 2-3 hrs | 1 hr | Written decision, not a vibe |
| 5 | Target metrics per path (below) | 1-2 hrs | 30 min | |

**Fundraise-or-bootstrap:**

| Signal | Bootstrap | Raise |
|---|---|---|
| Growth | Organic, low-cost acquisition works | Capped by capital (paid UA, native app, brand deals) |
| Revenue | Affiliate + deals cover costs | Big upside but needs speed to beat competitors |
| Bandwidth | Nights-and-weekends is enough | Needs full-time + salary bridge |
| Moat | Curation/trust, compounds slowly | Data/network effects reward speed |

**Day-90 metric bars:**

| Path | Bar |
|---|---|
| Stay bootstrap | <200 users, revenue covers costs, no brand inbound pressure |
| Small pre-seed / part-time | 200-500 users, $500+/mo affiliate revenue trending up, 2+ unprompted brand asks |
| Seed / full-time | 500+ users w/ strong retention, inbound ad interest, clear 10x story |

**Gate (Day 90):** A written decision on iOS path and fundraise-vs-bootstrap, backed by these metrics.

---

## 6. Budget Table

| Item | Cost | Notes |
|---|---|---|
| Domain | ~$12/yr | Namecheap/Google Domains |
| Hosting | $0 | Vercel/GitHub Pages free tier |
| Serverless API proxy | $0 | Free tier covers this scale |
| Claude API @ ~100 scans/mo | ~$1-5/mo | Rough; depends on model/output size |
| Claude API @ ~1,000 scans/mo | ~$10-50/mo | Consider caching common products |
| Claude API @ ~10,000 scans/mo | ~$100-500/mo | Revisit model/caching then — not a Day 1-90 problem |
| Analytics | $0 | Free tier sufficient under ~1k events/mo |
| Affiliate network fees | $0 | Amazon, ShareASale, Thrive, iHerb — free to join |
| LLC formation | $100-300 | State-dependent; before first affiliate dollar |
| Business bank account | $0 | Usually free at this scale |
| **Total Day 1-90** | **~$120-350** | Dominated by LLC, not tech |

*Validate the per-scan estimate with 20-30 real test scans — it depends heavily on model/prompt choice.*

---

## 7. Weekly Cadence (8-10 hrs/week)

| Slot | Focus |
|---|---|
| Weeknight #1 (~2 hrs) | Build/fix — one shipped unit of progress |
| Weeknight #2 (~2 hrs) | Build/fix, or outreach if build queue is empty |
| Weeknight #3 (~1 hr, optional) | Buffer/catch-up |
| Saturday (~3 hrs) | Deep work: hardest task of the week |
| Sunday (~1-2 hrs) | Metrics review + pick next week's top 3 + 1 relationship touch |

**Rule:** If it's not one of Sunday's top 3, it doesn't happen this week.

---

## 8. Metrics Dashboard — 5 Numbers That Matter

| # | Metric | Why | Cadence |
|---|---|---|---|
| 1 | Weekly scans | Core usage | Weekly |
| 2 | Scan → swap-click rate | Is the recommendation trusted/compelling | Weekly |
| 3 | Swap-click → purchase rate | Is monetization working | Weekly (once affiliate live) |
| 4 | Returning users (2+ sessions/14 days) | Habit vs. novelty | Weekly |
| 5 | Small-brand signups/conversations | Supply side (Mario's edge) building | Bi-weekly |

One spreadsheet tab. No dashboard tooling before Day 60 — premature infrastructure.

---

## 9. Kill Criteria (Be Brutal)

| Trigger | Action |
|---|---|
| <2 of 5 weekend testers say "I'd use this" | Kill or redesign concept before writing more code |
| <20% of Day-30 users return within 2 weeks | Stop adding features; diagnose before Day 31 spend |
| Health/environment claim called wrong/unsafe by 2+ users | Immediate stop-ship on that claim path; fix sourcing first |
| Zero affiliate clicks after 100 users see a swap | Monetization model broken — fix before marketplace/ads planning |
| Founder can't sustain 8 hrs/wk for 2+ weeks | Cut scope, not sleep — re-plan smaller |
| No brand responds after 20+ outreach attempts | Reassess whether small-brand angle fits v1 |

---

## 10. Legal / Compliance Quick Hits

| Item | Action | Priority |
|---|---|---|
| **Employer moonlighting/IP policy** | **Check Walmart's outside-work/IP policy before any revenue or public brand deals** — retail media is Mario's day job domain, real conflict-of-interest risk | **Flag: do first, before Section 4** |
| "Not health advice" positioning | Disclaimer on every readout: "informational summaries of publicly cited sources, not medical/health advice, consult a professional" | Before this weekend's launch |
| Affiliate disclosure (FTC) | Conspicuous "contains affiliate links, Guardi may earn a commission" near every swap link | Before first affiliate link goes live (Day 31) |
| Source citation accuracy | Cite EWG/CSPI/FDA/USDA as sources, never imply their endorsement/sponsorship | Ongoing, esp. Day 1-30 backend |
| Terms of Service / Privacy Policy | Minimal real ToS + Privacy Policy (AI drafts, human/lawyer skims) once collecting user data/photos | By Day 30 |
| LLC formation | Before first affiliate dollar collected | Day 31-45 |
| Photo data handling disclosure | Disclose if photos touch a third-party API (Claude) — no silent off-device transfer | By Day 30 |

---

*End of draft. Companion document: `guardi/docs/business-plan.md`.*
