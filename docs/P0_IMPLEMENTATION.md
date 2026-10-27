# P0 Implementation and Handover

Date: 2026-10-27. Local code changes only. No production deployment, commit/push,
DNS modification, hosting mutation, paid purchase or real customer submission.

## Architecture and files

The site remains static HTML. Update content/templates in `docs/build_site.py`,
then regenerate all 32 existing URLs. CSS and JavaScript remain shared. No new
runtime dependencies or backend were introduced.

```sh
python3 docs/build_site.py .
python3 docs/validate_site.py .
node --check docs/site.js
node --check docs/analytics.js
node docs/test_analytics.cjs
```

No TypeScript project or package build exists, so type checking/npm builds are
not applicable. The Python generator and validator execute directly.

## Contact form

- Original native FormSubmit POST recipient and `_captcha=true` are preserved.
- No-JavaScript users keep browser required/email validation and same-tab native
  provider submission. The enhanced flow opens verification in a separate tab,
  detaches its opener and retains the original entries on the contact page.
- Adds whitespace-only validation, accessible field errors/status, a duplicate
  handoff guard and explicit return-to-editing control. Nothing is saved in
  localStorage/sessionStorage or logs by the site.
- The verification transfer uses FormData to preserve current select, checkbox
  and text values; it does not rely on DOM cloning of default form state.
- If offline or a verification tab is blocked, explain the local error and keep
  the entered text. Blocked-tab recovery allows an explicit same-tab submission.
- No automatic retries, no CAPTCHA bypass, no inference from window closure,
  redirects, a success URL parameter or an HTTP 2xx response.
- After handoff the status remains **Verification Pending**, not **Sent**.
  The provider's final acceptance and downstream email delivery are not observable
  from this static site. No station-owned fake success page was added.
- User explicitly approved preserving CAPTCHA and leaving the success integration
  incomplete rather than reporting an unverified success.

## Homepage and mobile

- Uses the requested headline: "Need Medical Care in Shenzhen? We'll Help You
  Navigate It." Clarifies coordination versus clinical care near the first CTA.
- Primary inquiry and direct WhatsApp CTAs, four concrete non-clinical support
  roles, existing visit imagery, three-step process, grounded reasons to choose
  the service, expandable FAQ and contact CTA.
- Persistent mobile header inquiry link, without a floating chat circle.
- Existing service pages, country search, map, QR and shared footer are retained.
- Source comment marks an owner-content slot for an approved team biography,
  credentials and permissioned portrait. Do not publish invented replacements.
  Legal operating entity, responsible-person details and verified credentials
  must be supplied/approved by the owner before insertion.

## SEO

- Preserves all existing URLs, role disclaimer and response-time wording.
- Improves homepage title/description and updates meaningful sitemap dates only
  for Home, Contact and Privacy. Keeps unique titles/descriptions and exact
  canonical/OG URLs, one H1 and responsive image alt/dimensions.
- Adds validation of these properties, analytics loader uniqueness and CAPTCHA.
- Robots already permits crawling and points to the canonical sitemap; it was
  not changed just for appearance. No broken internal target found in validation.
- Live read-only www TLS + 308 + Contact HTTP 200 passed on 2026-10-27.
  Removed `/cases.html` has a genuine 404 and no current internal reference;
  this is not repaired with an unrelated homepage redirect.
- Read-only HEAD checks covered 11 unique external links: 8 resolved to HTTP 200;
  two Unsplash attribution URLs returned 401 and the Shenzhen airport URL 403.
  These are access restrictions for the test client, not proven broken links.
  Keep the attribution and official source URLs; review those three manually in
  a regular browser. A reachable WhatsApp endpoint does not verify account identity.

## GA4: meaning, privacy and limits

Reuses existing `G-JMX3WEED6K`, with one shared loader on the 31 previously tracked
pages. Privacy remains untracked. Local/preview hosts and DNT/GPC do not load it.
Configured location/referrer strip query strings/fragments; Google signals and
advertising personalization are disabled in the loader.

| Event | Implemented trigger | Meaning |
| --- | --- | --- |
| whatsapp_click | Click the preserved WhatsApp link | Intent, not message receipt |
| email_click | Click the public email link | Intent, not email delivery |
| contact_form_attempt | Explicit enhanced form submission attempt/retry | May fail local validation; not a lead |
| contact_form_error | Local validation, offline, blocked tab or handoff exception | Fixed `error_type`, not a provider failure claim |
| contact_form_success | **Not emitted** | Blocked pending authenticated provider receipt; owner approved this boundary |

Error types: `validation`, `offline`, `popup_blocked`, `handoff_error`. Custom event
parameters contain fixed channel, sanitized page location, empty referrer and
fixed error category only. No fields, email, names, country, service selections,
message text or raw exceptions are passed to GA4. `im_*` names are retired, not
dual-emitted. Existing reports require a date boundary when comparing names.

GA4 Enhanced Measurement may generate its own outbound/form events based on
account settings. In the account, review those settings, disable automatic form
interaction measurement if it duplicates/misstates this funnel, and confirm no
URL/form data is collected through other tags. This is not a full consent platform
or certification of legal compliance. Key-event definitions must not sum clicks,
attempts and errors as unique customers or confirmed leads.

## Owner actions and external blockers

1. Review local changes before any publishing. This P0 did not deploy or push.
2. Log into the receiving mailbox, check FormSubmit activation and spam folders,
   then authorize one synthetic inquiry through the production site. Complete
   CAPTCHA manually, confirm provider receipt, and check actual delivered email
   including Reply-To and fields. No patient information is needed.
3. Verify `whatsapp_click`, `email_click`, `contact_form_attempt` and
   `contact_form_error` in the correct GA4 property's Realtime/DebugView after an
   approved deployment. This implementation does not claim account receipt.
4. A genuine `contact_form_success` requires a provider-supported, authenticated
   receipt/backend integration, with secure credentials and delivery semantics.
   A redirect query, user confirmation button or opening/closing a tab is not
   acceptable evidence. Do not enable an invented client-side success signal.
5. Supply approved public legal entity/team details; do not add unverifiable
   claims. No public fee amounts or hospital names were introduced.

## Verification

- Generator and expanded static validator passed for all 32 existing pages.
  JavaScript syntax checks and `node docs/test_analytics.cjs` passed.
- Chromium browser regression: 32 pages at 1440px and 375px, plus Home, Contact,
  Services, Guides and Shenzhen at 320px and 768px: **74 page/viewport checks**.
  No overflow, broken local image, duplicate H1/footer or page runtime error.
- Menu/Escape, known/unknown inquiry preselection, country filtering, keyboard
  selection and required-field validation passed. Existing native datalist has
  200 entries; enhanced country/region selection has over 240 entries.
- Intercepted form tests passed: whitespace validation, offline, blocked tab,
  explicit same-tab fallback, detached provider tab, duplicate guard, retained
  values (including service/stage choices, country, consent and optional fields),
  handoff exception, DNT and an unavailable analytics function.
  Two native POST requests were mocked inside the browser, not sent externally.
- An additional no-JavaScript, reduced-motion keyboard test passed native email/
  required validation, target-market datalist entries, consent and CAPTCHA
  preservation. Its native POST was also intercepted, not sent externally.
- Fake HTTP 200 provider responses and a `success=true` query never produced
  `contact_form_success`. Custom-event payloads contained no test names, email,
  country, message or private query; no browser-storage persistence was added.
- Local mobile Lighthouse: performance, accessibility, best practices and SEO
  **100 each**, LCP about **1.6 s**, CLS **0**, TBT **0 ms**, no run warnings.
  These are local lab results, not production field metrics or ranking promises.
  Audit suggestions about caching and image delivery remain informational;
  hosting settings were not changed.
- Desktop/mobile first-screen screenshots were visually reviewed after image
  decoding. Chromium was tested; real iOS/Safari, provider CAPTCHA completion,
  mailbox receipt and GA account ingestion remain manual checks.

Screenshots, browser scripts and Lighthouse JSON are retained privately in the
workspace `docs/p0-review/`, not copied into the website repository. Third-party
requests were blocked/mocked for browser interaction tests; embedded Map content
and the WhatsApp account identity were not re-certified by those tests.
No real FormSubmit POST or mailbox delivery has been tested during this change.

## Reference docs

- https://formsubmit.co/documentation
- https://formsubmit.co/help
- https://developers.google.com/analytics/devguides/collection/ga4/events
