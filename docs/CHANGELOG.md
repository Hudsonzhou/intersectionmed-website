# Changelog

## 2026-10-27 - P0 local implementation

- Clarify homepage coordination scope, improve first-screen inquiry/WhatsApp CTAs,
  retain visit imagery and add concise support/why-us sections and FAQ.
- Add persistent mobile header inquiry access without a floating chat widget.
- Preserve native FormSubmit CAPTCHA while adding local validation, pending status,
  duplicate handoff protection, offline/tab errors and explicit same-tab recovery.
- Adopt requested channel/attempt/error event names. Do not emit an unverifiable
  `contact_form_success`; owner approved this remaining integration gap.
- Centralize the existing GA4 ID without duplicate loaders; suppress loading on
  previews and under DNT/GPC, and sanitize configured URL/referrer values.
- Strengthen static SEO/asset/analytics checks and add offline analytics unit tests.
- Keep 32 page URLs, contact details, map, QR, country search and provider CAPTCHA.
- Add SITE_AUDIT and implementation handover. No deploy, push, DNS/hosting changes,
  real form submission, invented medical proof, prices or partnerships.
