# Website maintenance

The site is static HTML. No Node build or backend is required to view it.

## Shared files

- `docs/site.css`: layout, navigation, footer, content and form styles.
- `docs/site.js`: mobile navigation, the searchable country selector and
  allowlisted inquiry preselection from service/scenario links.
- `docs/build_site.py`: shared navigation/footer templates and page content.
- `docs/validate_site.py`: static markup, local target, inventory and content checks.

From the repository root, regenerate the existing pages with:

```sh
python3 docs/build_site.py .
```

The builder keeps all 32 current page URLs. It updates HTML and `sitemap.xml`;
it does not publish, commit, or send messages. Make durable copy or template
changes in the builder before regenerating. Update its release date when the
page content has actually changed.

Preview by opening `index.html`, or run a temporary local server:

```sh
python3 -m http.server 8766 --bind 127.0.0.1
```

Then visit `http://127.0.0.1:8766/`. Close the temporary server when finished.

## Business facts confirmed on 2026-10-15

- Brand name: IntersectionMed.
- Coordination fees are discussed through a specific inquiry; do not publish
  amounts or imply that an initial inquiry is free unless confirmed.
- Public and private hospital options may be discussed. Do not publish
  cooperating institutions' names or imply a formal partnership.
- Replies are usually within 1-2 business days; do not promise live responses.
- WhatsApp contact link was decoded from the owner's supplied QR image:
  `https://wa.me/qr/TY3MLSWE4SS7D1`. If the QR is reset, update both the image and
  the link in the builder.

## Facts to confirm before adding public claims

- Legal operating entity and the public responsible-person profile.
- Team credentials and permissions for real staff photographs.
- Payment, deposit, rescheduling and cancellation terms.
- Data retention practices and the agreed sensitive-document transfer channel.

Do not fill these gaps with invented prices, credentials, testimonials, terms
or healthcare claims.

## Short-visit focus approved on 2026-10-21

- Three core categories: health checkups, dental checks/basic care, and
  digestive consultations/endoscopy coordination.
- TCM consultations and rehabilitation assessments are optional visits, not
  promises of completing a treatment course.
- Fertility consultation stays available only as an individual request; it is
  not a core package or an offer of a complete IVF cycle.
- One or two appointments is a feasibility question for the institution, not
  a guarantee of completed treatment, all reports or clearance to travel.
- Keep women's/men's health within checkup planning. Other specialist requests
  need individual provider confirmation, not automatic package expansion.
- Implants, orthodontics, complex restorative care, surgery and ongoing
  rehabilitation are not advertised as short-visit packages.

## Assets and sources

- The two Shenzhen photographs retain their existing Unsplash source links
  on the Shenzhen page. They illustrate the destination, not hospital partners.
- `docs/images/visit-planning.png` is an AI-generated planning still life.
  Its visible caption identifies it as an illustration, not a real team,
  patient, office or proof of services delivered.
- Digestive visit boundaries were checked against NHS endoscopy information:
  https://www.nhs.uk/tests-and-treatments/endoscopy/
- Fertility scheduling boundaries were checked against NHS information:
  https://www.nhs.uk/conditions/infertility/diagnosis/
- TCM visit boundaries were checked against the provider's session guidance:
  https://www.guysandstthomas.nhs.uk/health-information/acupuncture

Run `python3 docs/validate_site.py .` after rebuilding. The browser checks
should cover every URL at desktop and mobile widths, in addition to inquiry
preselection, country keyboard selection and menu focus behavior.

## Image-led homepage update on 2026-10-21

- Homepage copy is intentionally shorter; detailed preparation and boundaries
  remain on service and guide pages rather than being flattened into images.
- The three core visit entries share their image-led component with Services.
- `docs/images/service-checkup.png`, `service-dental.png`,
  `service-digestive.png` and `service-tcm.png` are generated illustrations.
  Visible captions identify them as AI-generated, not partner-facility photos.
- Images have stable aspect ratios, descriptive alt text and lazy loading.
  Keep headings and important information as HTML text, not baked into images.
- The homepage retains three accessible, expandable FAQs, the full role
  disclaimer and the usual 1-2 business day response note.
- Keep the existing URLs and country selector behavior intact.

## Publishing checks

Keep the HTML pages, `docs/site.css`, `docs/site.js`, images and sitemap in the
same commit. Verify desktop/mobile navigation, internal links, country search,
form field labels and footer consistency. Do not send a real contact form
submission during routine visual testing. The external FormSubmit delivery and
mailbox activation require a separate authorized delivery check.

## Search and performance update on 2026-10-23

- Keep page-specific meaningful update dates in `CONTENT_UPDATED` in the builder;
  do not advance every sitemap date for a shared style or analytics change.
- Rebuild responsive service and city images with `python3 docs/optimize_images.py .`
  before building HTML. This requires the official `cwebp` executable on PATH.
  Original PNG/JPEG assets remain available; rendered pages use WebP variants.
- Service images use 480/960 pixel variants, city images use 800/1600 pixel
  variants. Preserve `srcset`, `sizes`, intrinsic dimensions and descriptive alt
  text. The first hero image loads eagerly with high fetch priority.
- Three priority pages cover checkups, dental checks/basic care, and
  English-Chinese interpretation. Keep practical appointment FAQs as HTML.
- `docs/seo-measurement.md` defines keyword ownership, event meaning and outreach
  drafts. Never copy private Search Console reports into this public repository.
- Existing analytics page views omit URL query strings and fragments. Custom
  contact events do not read form values and respect DNT/GPC signals; this is not
  a consent-management system or a claim of compliance in every jurisdiction.
- Do not mark the form handoff as a delivered inquiry or a confirmed appointment.
  Verify actual delivery separately with the owner before reporting lead totals.
