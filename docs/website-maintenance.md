# Website maintenance

The site is static HTML. No Node build or backend is required to view it.

## Shared files

- `docs/site.css`: layout, navigation, footer, content and form styles.
- `docs/site.js`: mobile navigation and the searchable country selector.
- `docs/build_site.py`: shared navigation/footer templates and page content.

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

## Publishing checks

Keep the HTML pages, `docs/site.css`, `docs/site.js`, images and sitemap in the
same commit. Verify desktop/mobile navigation, internal links, country search,
form field labels and footer consistency. Do not send a real contact form
submission during routine visual testing. The external FormSubmit delivery and
mailbox activation require a separate authorized delivery check.
