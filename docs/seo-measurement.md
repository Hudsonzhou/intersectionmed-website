# Search visibility and contact measurement

Updated: 2026-10-23. Internal maintenance guide, not a public service promise.

## Priority and keyword ownership

Improve existing useful pages before creating more URLs for near-identical queries.
These are target phrases, not claims of measured search volume or guaranteed rank.

| Intent | Existing page | Target phrases | Practical information to maintain |
| --- | --- | --- | --- |
| Plan a checkup | health-checkup-china.html | health checkup Shenzhen; health checkup China for foreigners | Passport registration, provider-confirmed scope, report timing and language |
| Arrange basic dental visits | dental-treatment-china.html | dental checkup Shenzhen; teeth cleaning Shenzhen for foreigners | Assessment first, basic care subject to dentist approval, separate complex care |
| Get language support | medical-translation-shenzhen.html | medical interpreter Shenzhen; English Chinese medical interpretation | Already-booked appointments, spoken vs document support, hours and follow-up scope |
| Digestive appointment planning | colonoscopy-shenzhen.html; endoscopy-shenzhen.html | colonoscopy Shenzhen; endoscopy China for foreigners | Separate procedure-specific preparation and logistics; no medical instructions from IntersectionMed |
| Optional TCM assessment | traditional-chinese-medicine-rehabilitation-shenzhen.html | TCM consultation Shenzhen; rehabilitation appointment support | Initial assessment versus ongoing care, clinician decisions and realistic scheduling |
| Travel through Hong Kong | hong-kong-to-shenzhen-medical-visit-guide.html | Hong Kong to Shenzhen medical visit | Border/travel sources, appointment timing and travel contingency |

Never create a new near-duplicate merely to match a keyword. Do not remove a live
indexed URL solely because its phrase is broad.

## Measurement routine

1. Record the actual publication date and scope of each change.
2. In Search Console, compare the latest complete 28 days with the previous 28.
   Save clicks, impressions, CTR, position, query, landing page, country and device.
3. Separate branded and non-branded searches; compare each page with itself.
   Small click counts are volatile. An average position is not a fixed ranking.
4. Inspect priority URLs after publication if they are new or materially changed.
   Repeated requests do not ensure indexing. Sitemap discovery is not indexing.
5. Review exclusions by exact URL. Expected redirects/canonical duplicates are
   different from broken live pages. Keep a removed page's genuine 404 unless a
   relevant replacement exists; do not invent cases or redirect every 404 home.
6. Check production mobile performance after deployment and field Core Web
   Vitals when available. A localhost Lighthouse score is only a lab baseline.

Keep account reports in private working documents, not in the public website repo.
No paid links, invented reviews, guaranteed appointments or clinical claims.

## Contact event definitions

The site retains its existing Google Analytics configuration. After publication,
check these events in that property's Realtime/DebugView and subsequent reports.
Their local dispatch has been tested; GA account receipt is a separate check.

| Event | Trigger | Meaning and limit |
| --- | --- | --- |
| im_whatsapp_click | Click the supplied WhatsApp contact link | Channel intent, not a sent message |
| im_email_click | Click the public email link | Email intent, not a delivered email |
| im_inquiry_handoff | Valid form submit event | Handoff attempt, not FormSubmit delivery or appointment confirmation |

Custom parameters are only `contact_channel` and sanitized `page_location`, plus
the beacon transport setting. No names, emails, country selections, service
selections or free text are read into these custom events. URL query strings and
fragments are stripped from configured page location and referrer. DNT/GPC
suppresses these custom events, not necessarily all existing third-party tracking.

GA enhanced measurement can have its own settings; review those in the account.
Do not infer complete privacy compliance from the custom-event test. Review consent
and retention requirements for the markets served before expanding tracking.
Never attach medical details or personal contact details to analytics events.

Do not aggregate channel clicks and form handoffs as confirmed leads. One visitor
can trigger several actions. Qualified inquiries, delivered messages and confirmed
bookings require a separate consent-aware operational record.

## External entry points: draft workflow

Prepare one genuinely useful planning resource for each relevant expat, travel or
international business community. Confirm its audience, posting rules, commercial
disclosure and editorial policy before sending. Do not scrape members or mass-post.

Potential categories: Shenzhen expat publications, Hong Kong travel communities,
international relocation guides and chambers' member/resource directories.
Check each current site's rules and suitability before choosing a recipient.
This guide does not assert that any outlet has agreed to publish or partner.

Draft editor introduction (not sent):

> Hello, I represent IntersectionMed, a Shenzhen-based healthcare coordination
> and patient support service. We have a practical English guide for international
> visitors on appointment communication, interpretation and travel planning.
> Would a clearly disclosed resource contribution be relevant to your readers?
> IntersectionMed is not a healthcare provider and does not provide diagnosis,
> treatment or medical advice. Medical decisions belong to licensed physicians
> and healthcare institutions.

Link to the relevant guide or service page, not always the homepage. Disclose
commercial affiliation and obtain permission for any patient story or photograph.
Do not claim a formal hospital relationship or offer a ranking of providers.
No outreach has been sent or backlink placement purchased through this update.

## Primary references

- Google Search image guidance: https://developers.google.com/search/docs/appearance/google-images
- GA4 event implementation: https://developers.google.com/analytics/devguides/collection/ga4/events
- Search Console sitemap report: https://support.google.com/webmasters/answer/7451001
