# IntersectionMed P0 Site Audit

Audit date: 2026-10-27. Scope: P0 only. No production deployment or hosting/DNS mutation.

## Baseline and evidence

- Local repository: `intersectionmed-website`, branch `main`, baseline commit
  `a7da1ab`. Working tree was clean before this work. Source is staged for safe
  editing in the workspace before synchronization back to the repository.
- Static HTML site: 32 existing URLs, shared Python generator, CSS and plain
  JavaScript under `docs/`. No package manifest, framework, backend, root README,
  checked-in Vercel config, or CI configuration was found in the inspected repo.
  `docs/website-maintenance.md` is the existing maintenance reference.
- Workspace AGENTS.md and BUSINESS.md were read. No additional repository-local
  AGENTS.md was found. Licensed institutions make all clinical decisions.
- Production read-only checks: Vercel response headers; www Contact URL has valid
  TLS, returns 308 to the non-www path, then HTTP 200. Old `/cases.html` returns a
  real HTTP 404. Neither is currently a confirmed broken-live-link problem.
- Baseline static validator passes 32 pages, markup nesting, shared chrome,
  internal paths/anchors/assets, sitemap and business boundaries.

## Findings and decisions

| Priority | Finding | Evidence / status | P0 response |
| --- | --- | --- | --- |
| P0 | Native contact submission has no site-owned pending state, duplicate guard or local error recovery | Confirmed in `docs/site.js` and generated form | Add accessible state, whitespace validation, offline/popup handling, same-tab fallback; keep provider CAPTCHA |
| P0 | Email receipt and activation are not verified | External dependency, not proven failure | Owner must verify FormSubmit activation, CAPTCHA and actual mailbox delivery; no automatic real test submission |
| P0 | Final success cannot be reliably observed by this static site | Native cross-origin provider page, no verified callback/backend | Owner approved keeping CAPTCHA and leaving `contact_form_success` unimplemented rather than fabricating a signal |
| P0 | Event vocabulary does not match requested funnel | Existing `im_*` names measure handoffs only | Replace with `whatsapp_click`, `email_click`, `contact_form_attempt`, `contact_form_error`; document success gap |
| P0 | Contact shortcuts are less visible while browsing on mobile | Contact inside collapsed menu outside Contact page | Add a persistent header inquiry link and direct WhatsApp in key CTAs; no floating chat circle |
| P0 | Homepage describes visit categories more clearly than the actual coordination service | Confirmed content review; UX judgment, not an outage | Use requested headline, four non-clinical support roles, process, grounded reasons and short FAQ |
| P0 | SEO validator does not assert unique titles/descriptions, exact canonicals, alt text or analytics uniqueness | Confirmed test coverage gap, not proof metadata is broken | Expand static checks and keep sitemap dates meaningful |
| P0 | Local previews can load production analytics | Existing global inline loader has no host gate | Centralize existing ID once; do not load on localhost or under DNT/GPC; strip queries/fragments |
| Verify | GA4 enhanced measurement, event receipt and permissions | ID `G-JMX3WEED6K` exists on 31 pages; Privacy intentionally untracked | Reuse ID, avoid duplicate loaders; account-side receipt/settings still require verification |
| Verify | WhatsApp contact identity/continued validity | Owner-supplied QR link remains in source | Preserve link and QR; opening a link does not prove a sent message or receipt |
| Not a defect | No custom 404 page | Old removed URL correctly returns 404, no current internal reference | Do not resurrect invented cases or create soft-404 redirects |
| Not a defect | www TLS/redirect | Live read-only test passed on audit date | No domain mutation needed or made |

## Scope boundaries

Keep all 32 URLs, country selector, map, QR, native form fallback, provider CAPTCHA,
existing contact details, 1-2 business-day response wording and role disclaimer.
No invented prices, hospital partnerships, staff credentials, testimonials or cases.
Place unconfirmed owner/team content slots in source comments and handover notes,
not as fabricated public claims. No patient records, payments or social posting.

## Sources checked

- FormSubmit native settings / CAPTCHA / AJAX / activation context:
  https://formsubmit.co/documentation and https://formsubmit.co/help
- GA4 custom events and account-side verification:
  https://developers.google.com/analytics/devguides/collection/ga4/events

Implementation, final test results and external blockers are recorded in
`P0_IMPLEMENTATION.md`. This audit distinguishes verified behavior from unknowns;
it does not certify legal compliance, email deliverability or clinical services.

## Local verification outcome

Code-remediable items above are implemented and validated locally: 32-page static
checks, 74 page/viewport browser checks, offline analytics unit tests, intercepted
form state/error tests and a no-JavaScript keyboard/native submission test.
No real third-party submission or deployment was performed. Final provider
acceptance, mailbox delivery and GA account ingestion remain explicitly unverified.
The approved success-event gap remains open; it is not reported as a fixed defect.
External-link HEAD checks found 8/11 destinations reachable with HTTP 200. Two
Unsplash attribution links returned 401 and the Shenzhen airport link 403 for
the audit client; these remain manual-review items, not confirmed dead URLs.
