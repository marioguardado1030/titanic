/**
 * ============================================================================
 * api-scan.js — Guardi's serverless scan endpoint
 * ============================================================================
 *
 * WHAT THIS IS
 *   A serverless-function-style HTTP handler that fronts off-client.js. It's
 *   written to the common Vercel/Netlify Node function signature:
 *
 *     export default async function handler(req, res)
 *
 *   ...but the exact req/res shape varies by host:
 *     - Vercel (Node runtime):     req.query.barcode, res.status(n).json(obj)
 *     - Netlify Functions (Node):  no `res` — you instead `return { statusCode, body }`
 *       from the handler; if targeting Netlify, adapt the `respond()` helper
 *       below to return a value instead of calling res.* methods.
 *     - Vercel Edge / Deno Deploy: handler takes a raw `Request` and must
 *       return a `Response` — again, swap the respond() helper.
 *   This file targets the Node-style (req, res) signature since that's what
 *   the prompt asked for; treat `respond()` as the one seam to touch when
 *   porting to a different host.
 *
 * WHAT IT DOES
 *   1. Reads `?barcode=` or `?q=` (search text) from the query string.
 *   2. Calls off-client.js (lookupByBarcode or searchByName).
 *   3. Runs each raw OFF product through toGuardiReadout().
 *   4. Returns JSON: either a single readout (barcode lookup) or an array of
 *      readouts (name search).
 *
 * DEPLOYMENT NOTE
 *   This must run server-side / from a deployed function, not inside a
 *   published Claude Artifact — see the USAGE block at the top of
 *   off-client.js for why (Artifact CSP blocks outbound fetch; OFF itself is
 *   not the blocker). Once deployed, this becomes the real backend Guardi's
 *   frontend calls, e.g. `GET /api/scan?barcode=3017620422003`.
 *
 * WHERE A FUTURE CLAUDE VISION CALL SLOTS IN (NOT IMPLEMENTED HERE)
 *   Guardi's eventual "point your camera at a product" flow needs a step
 *   *before* this handler's current logic:
 *
 *     photo (base64 image) --> [Claude vision call] --> identified product
 *       name and/or barcode string --> (existing code below) --> OFF lookup
 *       --> toGuardiReadout()
 *
 *   Concretely, that would mean:
 *     - Accepting a POST with an image (e.g. `req.body.imageBase64`) in
 *       addition to the GET ?barcode=/?q= path already here.
 *     - Calling the Claude API (e.g. `client.messages.create` with an image
 *       content block) asking it to read any visible barcode digits and/or
 *       identify the product name and brand from packaging.
 *     - Taking Claude's output and feeding it into the exact same
 *       `lookupByBarcode()` / `searchByName()` calls already implemented
 *       below — no other change needed downstream.
 *   That vision call is intentionally NOT implemented in this file. Adding
 *   it means: pick an SDK, decide on prompt/schema for structured barcode/
 *   name extraction, decide fallback behavior when Claude can't read a
 *   barcode confidently, and handle the additional latency/cost of a vision
 *   call per scan. All of that is a deliberate follow-up, not scope creep
 *   here.
 * ============================================================================
 */

import { lookupByBarcode, searchByName, toGuardiReadout } from "./off-client.js";

/**
 * Attribution string Guardi's UI/response must surface alongside any
 * OFF-derived data. See off-client.js's USAGE block for the full ODbL
 * attribution requirement.
 */
const OFF_ATTRIBUTION =
  "Data from Open Food Facts (openfoodfacts.org), available under the Open Database License (ODbL).";

/**
 * Small host-agnostic response helper. Adjust this one function when
 * porting to a runtime whose response shape differs from Vercel's Node
 * (req, res) convention (e.g. Netlify's `return { statusCode, body }`, or
 * Edge runtimes' `return new Response(...)`).
 */
function respond(res, statusCode, payload) {
  // Vercel / Express-like Node handlers:
  if (res && typeof res.status === "function") {
    res.status(statusCode).json(payload);
    return;
  }
  // Fallback for hosts that don't give us a `res` object with .status/.json
  // (shouldn't happen under the Vercel/Netlify Node signature this file
  // targets, but keeps this from throwing if wired up differently).
  // eslint-disable-next-line no-console
  console.error("api-scan: response object did not support res.status().json() — adapt respond() for this host");
}

/**
 * Serverless handler entry point.
 *
 * Supported query params (mutually exclusive; barcode takes priority if
 * both are somehow present):
 *   ?barcode=<upc/ean>   -> single product readout, or 404-shaped error if
 *                           not found in Open Food Facts.
 *   ?q=<search text>     -> array of readouts (up to 10, from OFF's search).
 *
 * @param {object} req - platform request object; expected to expose a
 *   parsed query string as `req.query` (Vercel/Next-style). If your host
 *   only gives a raw URL, parse it yourself before reading barcode/q, e.g.:
 *     const { searchParams } = new URL(req.url, `https://${req.headers.host}`);
 *     const barcode = searchParams.get("barcode");
 * @param {object} res - platform response object; expected to expose
 *   res.status(code).json(obj) (Vercel/Express-style). See respond() above
 *   for adapting to hosts that don't.
 */
export default async function handler(req, res) {
  // Support both `req.query` (Vercel/Next/Express-style, already parsed)
  // and a raw `req.url` fallback (some minimal Node hosts only give you
  // the URL and you must parse it yourself).
  let barcode;
  let q;
  let page = 1;

  if (req && req.query) {
    barcode = req.query.barcode;
    q = req.query.q;
    if (req.query.page) page = Number(req.query.page) || 1;
  } else if (req && req.url) {
    try {
      const parsed = new URL(req.url, `https://${(req.headers && req.headers.host) || "localhost"}`);
      barcode = parsed.searchParams.get("barcode") || undefined;
      q = parsed.searchParams.get("q") || undefined;
      page = Number(parsed.searchParams.get("page")) || 1;
    } catch (err) {
      respond(res, 400, { error: "Could not parse request URL", detail: String(err) });
      return;
    }
  }

  if (!barcode && !q) {
    respond(res, 400, {
      error: "Missing query parameter: provide either ?barcode=<code> or ?q=<search text>",
    });
    return;
  }

  try {
    if (barcode) {
      const product = await lookupByBarcode(barcode);

      if (!product) {
        respond(res, 404, {
          error: `No Open Food Facts record found for barcode ${barcode}`,
          attribution: OFF_ATTRIBUTION,
        });
        return;
      }

      const readout = toGuardiReadout(product);
      respond(res, 200, { readout, attribution: OFF_ATTRIBUTION });
      return;
    }

    // Name search path: return an array of readouts.
    const products = await searchByName(q, page);
    const readouts = products.map(toGuardiReadout);

    respond(res, 200, {
      results: readouts,
      count: readouts.length,
      page,
      attribution: OFF_ATTRIBUTION,
    });
  } catch (err) {
    // Network errors, OFF outages, or malformed responses all land here.
    // Don't leak stack traces to clients; log server-side if a logger is
    // available on this host.
    // eslint-disable-next-line no-console
    console.error("api-scan handler error:", err);
    respond(res, 502, {
      error: "Failed to reach Open Food Facts or process its response",
      detail: err && err.message ? err.message : String(err),
    });
  }
}
