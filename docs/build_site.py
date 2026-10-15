"""Apply the approved content and shared presentation to the existing static site."""

import json
import re
import sys
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
DATE = "2026-10-15"
BASE = "https://intersectionmed.com/"
WA = "https://wa.me/qr/TY3MLSWE4SS7D1"
SCOPE = "IntersectionMed is not a hospital or healthcare provider and does not provide medical diagnosis, treatment, or medical advice. Medical decisions are made solely by licensed physicians and healthcare institutions."
MUNICIPAL = "https://www.sz.gov.cn/en_szgov/life/hospitals/municipal/index.html"
AIRPORT = "https://www.szairport.com/szairporten/index.shtml"
HK_ENTRY = "https://www.immd.gov.hk/eng/services/visas/visit_transit.html"
NIA = "https://en.nia.gov.cn/"


def p(text):
    return f"<p>{text}</p>"


def ul(items, ordered=False):
    tag = "ol" if ordered else "ul"
    return f"<{tag}>" + "".join(f"<li>{item}</li>" for item in items) + f"</{tag}>"


def section(title, text, ident=""):
    return f'<section id="{ident}"><h2>{title}</h2>{text}</section>'


def band(title, text, soft=False, eyebrow=""):
    heading = (f'<p class="eyebrow">{eyebrow}</p>' if eyebrow else "") + f"<h2>{title}</h2>"
    return f'<section class="band{" soft" if soft else ""}"><div class="wrap"><div class="section-heading">{heading}</div>{text}</div></section>'


def cards(items, two=False):
    return f'<div class="grid{" two" if two else ""}">' + "".join(
        f'<article class="item"><span class="number">{i:02d}</span><h3>{title}</h3><p>{desc}</p>'
        + (f'<a href="{href}">{label}</a>' if href else "") + '</article>'
        for i, (title, desc, href, label) in enumerate(items, 1)) + "</div>"


def table(headers, rows):
    return '<div class="table-scroll" tabindex="0" role="region" aria-label="Comparison table"><table><thead><tr>' + "".join(f'<th scope="col">{v}</th>' for v in headers) + '</tr></thead><tbody>' + "".join('<tr>' + "".join(f'<td>{c}</td>' for c in row) + '</tr>' for row in rows) + '</tbody></table></div>'


def faq(items):
    return '<div class="faq">' + "".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in items) + '</div>'


def scope():
    return f'<div class="scope"><p>{SCOPE}</p></div>'


def cta(title="Discuss your Shenzhen visit", text="Share the service you are considering, your dates and language needs. Ask about the support available and the coordination fee for your request."):
    return f'<section class="cta"><div class="wrap"><div><h2>{title}</h2><p>{text}</p></div><a class="button" href="contact.html">Request Coordination Support</a></div></section>'


NAV = [("index.html", "Home"), ("about.html", "About"), ("services.html", "Services"), ("shenzhen.html", "Why Shenzhen"), ("guides.html", "Patient Guides"), ("contact.html", "Contact")]


def navigation(active):
    def links():
        return "".join(f'<a href="{url}"' + (' aria-current="page"' if url == active else '') + f'>{label}</a>' for url, label in NAV)
    return '<a class="skip-link" href="#main-content">Skip to content</a><header class="site-header"><nav class="site-nav" aria-label="Main navigation"><a class="brand" href="index.html" aria-label="IntersectionMed home"><img src="logo.png" width="80" height="80" alt="IntersectionMed"></a><div class="desktop-links">' + links() + '</div><button type="button" class="nav-toggle" aria-label="Open navigation" title="Navigation" aria-controls="mobile-menu" aria-expanded="false"><span></span><span></span><span></span></button></nav></header><nav id="mobile-menu" class="mobile-links" aria-label="Mobile navigation" hidden>' + links() + '</nav>'


FOOTER = '''<footer class="site-footer"><div class="wrap"><div class="site-footer-grid"><div><img class="site-footer-logo" src="logo.png" width="82" height="82" alt="IntersectionMed"><p class="site-footer-copy">IntersectionMed helps international patients coordinate planned healthcare visits in Shenzhen through appointment communication, translation, accompaniment, travel planning, and post-visit support.</p></div><div class="site-footer-block"><h2>Explore</h2><a href="services.html">Services</a><a href="shenzhen.html">Why Shenzhen</a><a href="guides.html">Patient Guides</a><a href="about.html">About</a></div><div class="site-footer-block"><h2>Contact</h2><a href="mailto:intersectionmed@gmail.com">intersectionmed@gmail.com</a><p>Shenzhen, China</p><p>English and Chinese. Additional language support subject to availability.</p><p>Usually within 1-2 business days.</p></div></div><div class="site-footer-bottom"><p><a href="privacy.html">Privacy</a></p><p>&copy; 2026 IntersectionMed. All rights reserved.</p></div></div></footer>'''


def intro(title, desc, category="", article=False):
    crumbs = '<div class="breadcrumbs"><a href="guides.html">Patient Guides</a> / ' + category + '</div>' if article else ''
    return f'<header class="page-intro"><div class="wrap">{crumbs}<h1>{title}</h1><p>{desc}</p></div></header>'


def article(title, desc, sections, related, category="Visit planning"):
    toc = ''.join(f'<a href="#part-{i}">{heading}</a>' for i, (heading, _) in enumerate(sections, 1))
    body = ''.join(section(heading, content, f'part-{i}') for i, (heading, content) in enumerate(sections, 1))
    references = '<h2>Related reading</h2>' + ''.join(f'<a href="{url}">{label}</a>' for url, label in related)
    return intro(title, desc, category, True) + '<div class="band"><div class="wrap article-layout"><article class="article-body">' + body + scope() + f'<p class="article-meta">IntersectionMed &middot; Updated {DATE}</p></article><aside class="article-side" aria-label="Guide contents"><h2>In this guide</h2>{toc}{references}</aside></div></div>' + cta()


SERVICE_INFO = [
    ("Health checkup coordination", "Appointment, hospital navigation and communication around a planned checkup.", "health-checkup-china.html", "Explore health checkup support"),
    ("Digestive screening support", "Gastroenterology, colonoscopy and endoscopy appointment and preparation communication.", "colonoscopy-shenzhen.html", "Explore digestive visit support"),
    ("Dental consultation support", "Dental assessment appointments, provider explanations and staged visit planning.", "dental-treatment-china.html", "Explore dental consultation support"),
    ("Fertility assessment coordination", "Specialist consultation and evaluation planning, with language and document support.", "ivf-consultation-china.html", "Explore fertility assessment support"),
    ("TCM and rehabilitation coordination", "Provider-led traditional Chinese medicine, rehabilitation and physiotherapy visits.", "traditional-chinese-medicine-rehabilitation-shenzhen.html", "Explore TCM and rehabilitation support"),
]

PAGES = {}


def add(name, title, desc, body, kind="WebPage"):
    PAGES[name] = {"title": title, "desc": desc, "body": body, "kind": kind}


home = '''<header class="hero"><div class="wrap"><p class="eyebrow">IntersectionMed &middot; Shenzhen, China</p><h1>Healthcare travel support in Shenzhen.</h1><p class="lead">Hospital appointments, English-Chinese interpretation and in-person accompaniment for international visitors planning a healthcare visit.</p><div class="actions"><a class="button" href="contact.html">Discuss Your Visit</a><a class="button secondary" href="services.html">Explore Services</a></div><div class="facts"><div><strong>Planned visits</strong><p>Initial appointments and short-stay planning; timing confirmed for each request.</p></div><div><strong>English and Chinese</strong><p>Communication before, during and after the appointment.</p></div><div><strong>Public and private options</strong><p>Appointment options depend on service, language needs and availability.</p></div></div></div></header>'''
home += band("Start with the visit you are planning", cards(SERVICE_INFO), eyebrow="Our focus")
home += band("From your first question to the hospital visit", cards([
    ("Tell us what you need", "Share your preferred service, approximate dates and language needs. Dates can still be undecided.", "contact.html", "Send an initial inquiry"),
    ("Discuss support and fees", "Ask about appointment options, the support scope, coordination fees and any hospital or travel costs to confirm.", "services.html#fees", "Understand the service scope"),
    ("Confirm the arrangements", "Check the appointment, documents, support timing and provider instructions before finalizing your visit.", "medical-travel-shenzhen.html", "Read the visit planning guide"),
]), soft=True)
home += '''<section class="band"><div class="wrap split"><div><p class="eyebrow">Why Shenzhen</p><h2>A city connected to your journey.</h2><p>A mainland China destination next to Hong Kong, with an international airport and rail connections. Choose your hospital area and accommodation together rather than planning each separately.</p><div class="actions"><a class="button secondary" href="shenzhen.html">Explore Shenzhen</a></div></div><div><img class="city-photo" src="docs/images/shenzhen-bay-sunset.jpg" alt="Shenzhen waterfront and city skyline" loading="lazy" width="1200" height="525"></div></div></section>'''
home += band("Questions worth asking before you travel", faq([
    ("How are coordination fees calculated?", "Support depends on the appointment, language needs, time on site and any follow-up assistance. Contact us for a discussion of your request and the applicable fee. Hospital and travel costs should also be confirmed separately."),
    ("Can you help with public and private hospitals?", "We can help coordinate options in both settings. The department, language support, appointment availability and provider requirements need to be checked for each request."),
    ("Do I need to book flights before contacting you?", "You can inquire before choosing travel dates. Check appointment timing, any provider requirements and travel documents before making fixed arrangements."),
]) + scope(), soft=True)
home += cta()
add("index.html", "Healthcare Travel Support in Shenzhen, China | IntersectionMed", "Plan a healthcare visit to Shenzhen with IntersectionMed: appointments, English-Chinese interpretation, accompaniment and travel coordination. Inquire about support and fees.", home)

about = intro("About IntersectionMed", "Healthcare coordination and patient support for international visitors to Shenzhen, China.")
about += band("A local point of contact for an unfamiliar process", '<div class="split"><div>' + p("IntersectionMed helps international patients navigate the non-clinical parts of a planned healthcare visit: communicating with hospitals, arranging appointments, understanding the visit process and coordinating language support.") + p("We work around the service you are seeking, your travel dates and the communication support you need. Public and private hospital options can be discussed; availability and clinical suitability are confirmed by the institution.") + p('For questions about who will assist you and the proposed support, contact <a href="mailto:intersectionmed@gmail.com">intersectionmed@gmail.com</a>. Replies are usually within 1-2 business days.') + '</div><div><img class="city-photo" src="docs/images/shenzhen-bay-skyline.jpg" alt="Shenzhen Bay skyline, the city where IntersectionMed coordinates visits" width="1200" height="525" loading="lazy"><p class="photo-credit">Shenzhen, China. City photography is illustrative of the destination.</p></div></div>')
about += band("Who is responsible for each part of the visit?", table(["Part of the visit", "Role"], [
    ("Coordination and communication", "IntersectionMed helps with appointment communication, interpretation, navigation and travel logistics within the agreed scope."),
    ("Clinical assessment and care", "The healthcare institution and licensed clinicians determine consultation, tests, treatment, preparation instructions and medical recommendations."),
    ("Travel and personal decisions", "You decide whether to proceed after reviewing provider information, support arrangements, fees and travel requirements."),
]), soft=True)
about += band("Before agreeing to support", ul(["Confirm the proposed appointment or hospital setting and any requirements still outstanding.", "Discuss the coordination fee, included support, additional costs and payment arrangements.", "Ask who will assist you, which languages are available and how schedule changes are handled.", "Share only general planning information initially; discuss an appropriate channel before sending sensitive records."]) + scope()) + cta()
add("about.html", "About IntersectionMed | Shenzhen Healthcare Coordination", "Learn how IntersectionMed coordinates public and private hospital appointments, language support and planned healthcare visits in Shenzhen.", about, "AboutPage")

services = intro("Support for your Shenzhen healthcare visit", "Choose the visit you are considering, then discuss the appointment, language and travel support you need.")
services += band("Five starting points", cards(SERVICE_INFO))
services += band("Choose the support around your appointment", table(["Support", "What to discuss"], [
    ("Appointment coordination", "Institution or department, preferred dates, registration requirements and appointment confirmation."),
    ("On-site interpretation and accompaniment", "English-Chinese communication, registration, navigation, appointment location, time on site and waiting time."),
    ("Written translation and document organization", "Documents, language, length, turnaround and whether a separately certified translation is required."),
    ("Travel logistics", "Arrival timing, accommodation area and airport or local transport coordination. Confirm any third-party arrangements separately."),
    ("Post-visit communication", "Report collection, translation requests, questions to relay to the provider and further appointment arrangements."),
]), soft=True)
services += '<section class="band" id="fees"><div class="wrap split"><div><p class="eyebrow">Scope and fees</p><h2>Discuss the support before you commit.</h2><p>Coordination fees depend on your service request, language needs, time on site and follow-up requirements. Contact us to discuss the support available and the fee for your visit.</p><div class="actions"><a class="button" href="contact.html">Ask About Support and Fees</a></div></div><div class="aside-note"><h3>Questions to confirm</h3>' + ul(["What support and time are included?", "Which hospital, translation, transport or accommodation charges are separate?", "Who receives each payment, and in which currency?", "What happens if an appointment changes or the visit is cancelled?"]) + '</div></div></section>'
services += band("Public and private hospital options", p('We can help coordinate appointment options in public and private settings. Compare department availability, language support, location, registration and billing before choosing. See the <a href="shenzhen-hospitals-for-foreigners.html">hospital access guide</a> for questions to ask.') + faq([("Can I request interpretation if I already have an appointment?", "Yes, you can inquire about interpretation or accompaniment for an appointment you have arranged. Share the institution, date and support required so availability and scope can be discussed."), ("Does a short visit mean treatment will be completed?", "An initial consultation or appointment is different from a full course of care. Tests, reports, further visits and travel timing depend on the healthcare institution and clinician.")]) + scope(), soft=True) + cta()
add("services.html", "Healthcare Coordination Services in Shenzhen | IntersectionMed", "Explore health checkup, digestive, dental, fertility and TCM visit support. Ask IntersectionMed about appointment, interpretation, accompaniment and coordination fees.", services)

shenzhen = '''<header class="hero city-hero"><div class="wrap"><p class="eyebrow">Why Shenzhen</p><h1>A connected city for a carefully planned visit.</h1><p class="lead">A mainland China base beside Hong Kong, with public and private healthcare settings and city connections to build your itinerary around.</p><div class="actions"><a class="button" href="contact.html">Discuss Your Visit</a><a class="button secondary" href="#healthcare">Explore the Healthcare Setting</a></div></div></header>'''
shenzhen += band("Choose the location around your appointment", cards([
    ("Arrive directly", f'Shenzhen Bao\'an International Airport is one arrival option. Check current transport connections on the <a href="{AIRPORT}" target="_blank" rel="noopener noreferrer">airport website</a>.', "", ""),
    ("Connect through Hong Kong", "Plan your border or rail connection as well as the journey on the Shenzhen side. Entry requirements and current routes must be checked before travel.", "hong-kong-to-shenzhen-medical-visit-guide.html", "Plan a Hong Kong connection"),
    ("Stay near the right district", "A convenient hotel for one hospital may be a long journey from another. Confirm the appointment location before choosing accommodation.", "medical-tourism-shenzhen-guide.html", "Prepare your local stay"),
]))
shenzhen += '<section class="band soft" id="healthcare"><div class="wrap"><div class="section-heading"><p class="eyebrow">Healthcare setting</p><h2>Compare the setting as well as the appointment.</h2><p>Public hospitals, private providers and international departments have different registration, communication and billing arrangements. Availability must be checked with the institution.</p></div>' + table(["Setting", "What to clarify"], [("Public hospital", "The department and campus, passport registration, booking channel and whether language support is needed."), ("Private provider", "The service offered, clinician credentials, language arrangements, written fees and follow-up process."), ("International department", "Whether the department offers your requested service, what the fee includes and which languages are available.")]) + p(f'Use the <a href="{MUNICIPAL}" target="_blank" rel="noopener noreferrer">Shenzhen Government municipal hospital directory</a> as one official starting point. A listing is not an endorsement or a statement of partnership with IntersectionMed.') + '<div class="actions"><a class="button secondary" href="shenzhen-hospitals-for-foreigners.html">Read the Hospital Access Guide</a></div></div></section>'
shenzhen += '''<section class="band"><div class="wrap"><img class="city-photo" src="docs/images/shenzhen-bay-skyline.jpg" alt="Shenzhen Bay waterfront and skyline" width="1200" height="525" loading="lazy"><p class="photo-credit">City photography: <a href="https://unsplash.com/photos/city-skyline-across-body-of-water-during-daytime-4P2nfbuygys" target="_blank" rel="noopener noreferrer">Weichao Deng</a> and <a href="https://unsplash.com/photos/a-city-skyline-with-a-body-of-water-in-the-foreground-qOLl1J2uVP0" target="_blank" rel="noopener noreferrer">koala z</a> via Unsplash.</p></div></section>'''
shenzhen += band("Make the rest of the stay work for you", cards([("Accommodation", "Compare the actual hospital journey, step-free access and room arrangements for any companion. Confirm the hotel's registration requirements directly.", "", ""), ("Daily communication", "Keep the hospital name and address in Chinese as well as English, appointment details and a way to contact your accommodation and coordinator.", "medical-translation-shenzhen-guide.html", "Prepare for communication"), ("Time around the visit", "Waterfronts, parks and dining can be part of a wider itinerary. Follow the provider's instructions when deciding what activities and return travel fit around care.", "medical-tourism-shenzhen-guide.html", "Read the travel checklist")]), soft=True)
shenzhen += band("Check before booking travel", p(f'Confirm the appointment and campus, report timing, follow-up needs and travel documents. Use <a href="{NIA}" target="_blank" rel="noopener noreferrer">Mainland immigration information</a> and, where relevant, <a href="{HK_ENTRY}" target="_blank" rel="noopener noreferrer">Hong Kong Immigration</a> to check entry requirements for your circumstances.') + scope()) + cta()
add("shenzhen.html", "Why Shenzhen for a Planned Healthcare Visit? | IntersectionMed", "Explore Shenzhen's location, public and private healthcare settings, airport and Hong Kong connections, accommodation planning and official travel resources.", shenzhen)

SERVICE_PAGES = [
    ("health-checkup-china.html", "Health checkup coordination in Shenzhen", "Appointment and English-Chinese support for international visitors arranging a health checkup.", [
        ("Before the appointment", "Discuss the checkup provider, appointment date, language needs and the provider's document and preparation requirements. The provider determines which tests are appropriate."),
        ("At the checkup", "Ask about registration assistance, interpretation and navigation between departments. Confirm the time and location of any accompaniment in advance."),
        ("Reports and follow-up", "Confirm when each report will be ready, its language and how to arrange a clinician's explanation. Document translation is separate from clinical interpretation."),
    ], [("How many days should I allow?", "Some initial checkup visits may be planned around 1-2 days. Report availability, additional tests and clinician follow-up can take longer; confirm those dates separately."), ("Can I choose a package from a list?", "Ask the provider for an itemized package and consultation requirements. IntersectionMed can support communication but does not select medically necessary tests.")], [("health-checkup-china-planning-guide.html", "Prepare for your checkup"), ("health-checkup-cost-china.html", "Understand the cost breakdown")]),
    ("colonoscopy-shenzhen.html", "Colonoscopy appointment support in Shenzhen", "Gastroenterology appointment coordination, provider-issued preparation communication and on-site language support.", [
        ("Confirm the clinical appointment", "The clinician determines whether colonoscopy is appropriate. We can help communicate your appointment request, availability and registration requirements."),
        ("Coordinate provider instructions", "Ask how preparation, medication questions, consent and any companion arrangements will be explained by the provider. We can help translate those instructions."),
        ("Plan the visit and report handover", "Discuss interpretation, hospital navigation, report collection and questions to relay to the care team after the appointment."),
    ], [("Is a 2-3 day stay enough?", "It can be an initial planning window for some visits, but consultation, preparation, procedure availability, reports and follow-up must be checked with the institution before travel."), ("Do you supply preparation or medication instructions?", "No. Instructions and any changes to medication must come from the healthcare institution or licensed clinician. We assist with communication.")], [("colonoscopy-endoscopy-shenzhen-guide.html", "Plan a digestive screening visit"), ("colonoscopy-china-planning-guide.html", "Questions for a colonoscopy appointment")]),
    ("endoscopy-shenzhen.html", "Endoscopy visit coordination in Shenzhen", "Appointment, interpretation and hospital navigation for planned endoscopy-related visits.", [
        ("Clarify the requested appointment", "Endoscopy is a broad term. Tell us whether your request concerns gastroscopy (upper gastrointestinal endoscopy), colonoscopy or a consultation to discuss the next step. The clinician confirms the procedure."),
        ("Understand the provider's requirements", "Confirm appointment timing, provider-issued preparation instructions, consent and any companion arrangements. Request language support before arrival."),
        ("Keep reports and follow-up connected", "Ask when documents will be available and how to obtain a clinician's explanation or further consultation. Translation and document organization can be discussed separately."),
    ], [("Can I ask for gastroscopy and colonoscopy together?", "You can raise the request with the institution. Whether both are appropriate and how they are scheduled must be decided by the clinician."), ("What should I send initially?", "Share the appointment you are seeking, approximate dates and language needs. Describe whether previous reports exist; wait to agree an appropriate channel before sharing records.")], [("endoscopy-shenzhen-planning-guide.html", "Coordinate endoscopy preparation communication"), ("colonoscopy-shenzhen.html", "Colonoscopy appointment support")]),
    ("dental-treatment-china.html", "Dental consultation support in Shenzhen", "Dental assessment appointments, interpretation and planning around provider-led treatment discussions.", [
        ("Prepare for the consultation", "Describe the concern or consultation you are seeking and your available dates. Ask which previous images or records the dental provider needs."),
        ("Understand the provider's proposal", "Interpretation can support discussion of findings, proposed stages, materials and written costs. The dental professional determines the treatment plan."),
        ("Plan further visits", "Lab work, staged treatment and follow-up may require additional appointments or return trips. Discuss the whole schedule rather than assuming care finishes during one stay."),
    ], [("Can implants, crowns or veneers be completed in one trip?", "The answer depends on the clinician's assessment and proposed treatment stages. Ask the provider to distinguish the consultation, treatment, laboratory work and follow-up dates."), ("How do I compare costs?", "Request a written breakdown covering assessment, imaging, proposed treatment, materials and follow-up. Ask separately about coordination and interpretation fees.")], [("dental-treatment-china-planning-guide.html", "Plan dental consultations and staged visits"), ("dental-treatment-shenzhen-foreigners.html", "Prepare for follow-up after travelling home")]),
    ("ivf-consultation-china.html", "Fertility assessment coordination in Shenzhen", "Specialist consultation and evaluation planning with interpretation and document support.", [
        ("Define the first appointment", "Ask about a fertility evaluation, a discussion of existing reports or a specialist consultation. An inquiry about an assessment does not confirm access to a full IVF treatment cycle."),
        ("Confirm institution requirements", "The institution needs to confirm service eligibility, required documents and appointment timing. Share general planning information first; sensitive records require an agreed channel."),
        ("Plan any next stage separately", "An initial visit and any subsequent testing or treatment have different schedules. Eligibility, clinical decisions and ongoing care remain with the provider."),
    ], [("Does this service include a complete IVF cycle?", "This page covers coordination for evaluation and specialist consultation. Any subsequent fertility treatment requires separate confirmation by the licensed institution."), ("Can I receive an opinion on existing records?", "You may ask about arranging a specialist discussion. The provider confirms whether a consultation is available and which records it needs.")], [("medical-travel-shenzhen.html", "Understand the coordination process"), ("privacy.html", "Read the information-sharing notice")]),
    ("traditional-chinese-medicine-rehabilitation-shenzhen.html", "TCM and rehabilitation visit support in Shenzhen", "Coordination for provider-led traditional Chinese medicine, rehabilitation and physiotherapy appointments.", [
        ("Traditional Chinese medicine consultation", "Discuss appointment coordination and interpretation for a consultation. Available therapies and whether they are appropriate must be confirmed by a qualified provider."),
        ("Rehabilitation and physiotherapy", "Ask about an initial assessment or a planned appointment. The provider determines the plan, number of sessions and follow-up; a short trip does not imply a completed rehabilitation course."),
        ("Language and practical support", "Coordinate documents, registration, hospital or clinic navigation and communication about the provider's instructions. Travel arrangements should fit the confirmed appointment schedule."),
    ], [("Can I request a particular therapy?", "You can tell us what consultation or provider-led service you are researching. The healthcare institution must confirm availability and clinical appropriateness."), ("Will a short stay be enough?", "An initial consultation may fit a short visit, but treatment sessions or rehabilitation can have a longer schedule. Ask the provider to distinguish assessment from ongoing care.")], [("services.html#fees", "Discuss scope and coordination fees"), ("medical-translation-shenzhen.html", "Explore interpretation and accompaniment")]),
    ("medical-translation-shenzhen.html", "Medical interpretation and accompaniment in Shenzhen", "English-Chinese communication support for appointments you are arranging or have already booked.", [
        ("At the hospital", "Request interpretation for registration, consultation communication, provider instructions and navigation. Confirm the campus, appointment time, duration and any waiting-time arrangements."),
        ("Written documents", "Discuss which reports or letters need translation, their length, target language and turnaround. Certified translation, where required, needs separate confirmation with an appropriate provider."),
        ("After the appointment", "Ask about report organization, translating questions and relaying the care team's response. Interpretation conveys clinical information; it does not provide an independent medical opinion."),
    ], [("Can I book only an interpreter?", "Yes, you can inquire about an appointment you have booked yourself. Share its location, date, language and support needs so availability and fees can be discussed."), ("How is the fee confirmed?", "The request may involve time on site, travel, written documents and follow-up. Contact us with the scope and ask what is included, how waiting or overtime is handled and what is charged separately.")], [("medical-translation-shenzhen-guide.html", "Prepare for an interpreted consultation"), ("medical-translation-shenzhen-hospitals.html", "Organize documents after the visit")]),
]

for name, title, desc, stages, questions, related in SERVICE_PAGES:
    body = intro(title, desc)
    body += band("Support around your appointment", cards([(h,t,"","") for h,t in stages]))
    body += band("Before you request coordination", '<div class="split"><div>' + ul(["Share the service or appointment, approximate dates and communication language.", "Tell us whether an appointment is already booked and whether you need accompaniment, written translation or travel support.", "Mention whether relevant records exist; do not send passport numbers, payment details or full medical files in the initial inquiry."]) + '</div><div class="aside-note"><h3>Ask about your support and fee</h3><p>The coordination fee is discussed for your request. Confirm the support included, time on site and any separately charged hospital or travel services.</p><a href="contact.html">Discuss Your Visit</a></div></div>', soft=True)
    body += band("Questions before you travel", faq(questions) + '<ul class="link-list">' + ''.join(f'<li><a href="{url}">{label}</a></li>' for url,label in related) + '</ul>' + scope()) + cta()
    add(name, title + " | IntersectionMed", desc, body, "Service")

GUIDES = []


def guide(name, title, desc, category, sections, related):
    add(name, title + " | IntersectionMed", desc, article(title, desc, sections, related, category), "Article")
    GUIDES.append((name, title, desc, category))


guide("medical-travel-shenzhen.html", "Your healthcare visit: from inquiry to follow-up", "A complete planning guide to roles, scope, fees, appointments and the handover after a Shenzhen visit.", "Start here", [
    ("Start with the visit, not a flight booking", p("Tell us the appointment you are researching, your approximate dates, your language and whether you already have a hospital in mind. You do not need to have booked travel to make an initial inquiry.") + p("Share a general description first. Say whether reports exist without attaching sensitive records to a website form or ordinary email.")),
    ("Discuss options and the scope of support", p("Public and private hospital options can be discussed. An institution must confirm the service, appointment availability and requirements; a discussion with IntersectionMed is not an appointment confirmation.") + ul(["Will you arrange the appointment or ask for help with one already booked?", "Do you need on-site interpretation, accompaniment or written translation?", "Which arrival, accommodation or transport questions affect the visit?", "Will you need report collection or follow-up communication after leaving Shenzhen?"])),
    ("Clarify fees and changes", p('Ask about the coordination fee for the scope you need. Separate it from the institution\'s medical charges and from travel expenses. Use the <a href="health-checkup-cost-china.html">cost checklist</a> to compare included items, payees, payment timing and changes.') + p("Confirm cancellation, rescheduling and any third-party charges before agreeing to arrangements. Do not assume all costs are refundable.")),
    ("Confirm the visit details", ul(["Exact institution, campus or clinic and appointment details.", "Documents requested by the provider and an appropriate way to share them.", "Provider-issued preparation instructions, including questions that require a clinician's answer.", "Support location, language, timing and contact arrangements.", "Expected report dates and any further visits."], True)),
    ("Arrange the handover", p("Before departure, confirm how reports, receipts and translated documents will be obtained. Ask the provider who will answer subsequent clinical questions and how to arrange a further consultation if needed.") + p("An initial appointment window of a few days is different from completion of treatment or receipt of every report. Plan each stage separately.")),
], [("services.html", "Support scope and fees"), ("contact.html", "Make an initial inquiry")])

guide("how-medical-travel-to-shenzhen-works.html", "A visit-planning timeline: what to confirm at each stage", "Use a stage-by-stage checklist to keep appointment confirmation, travel and reports aligned.", "Start here", [
    ("Stage 1: while dates are flexible", p("Choose the type of visit you want to discuss, your language and an approximate travel window. Compare the provider setting and ask what information is required before an appointment can be considered.")),
    ("Stage 2: before fixed arrangements", table(["Confirm", "Why it matters"], [("Appointment and campus", "An inquiry or proposed date is not a confirmed booking."), ("Scope and fees", "Interpretation, waiting time, documents and travel coordination may be different parts of the request."), ("Clinical preparation", "The provider may need a consultation, preparation or documents before the planned appointment."), ("Reports and follow-up", "These may have a different timeline from the day at the hospital.")])),
    ("Stage 3: before arriving", ul(["Keep the Chinese address, appointment details and provider contact available offline.", "Check the official entry requirements and your arrival route.", "Confirm the interpreter or accompaniment meeting details if arranged.", "Keep any clinician-issued instructions accessible in a language you understand."])),
    ("Stage 4: before leaving Shenzhen", p("Check which documents are ready, which will follow later and who will contact you. Ask the care team about any further appointments and travel-related questions specific to your care.")),
], [("medical-travel-shenzhen.html", "Read the full coordination process"), ("hong-kong-to-shenzhen-medical-visit-guide.html", "Connect through Hong Kong")])

guide("shenzhen-hospitals-for-foreigners.html", "Public and private hospitals: planning access in Shenzhen", "Compare registration, language, location and billing before choosing an institution for a planned visit.", "Hospital access", [
    ("Compare three service settings", table(["Setting", "Questions to ask"], [("Public hospital outpatient service", "Which department and campus? How is a foreign passport registered? Is an appointment required?"), ("Private hospital or clinic", "Does it offer the service requested? How are clinician details, written charges and follow-up confirmed?"), ("International department", "Does it cover the appointment requested, which languages are offered and how are fees and insurance handled?")]) + p("International departments may be part of a public or private institution; they are not a guarantee of every specialty or language.")),
    ("Check the source of an appointment", p(f'Use official institution channels and the <a href="{MUNICIPAL}" target="_blank" rel="noopener noreferrer">Shenzhen Government municipal hospital directory</a> as starting points. The directory does not cover every private provider and is not a statement of partnership with IntersectionMed.') + ul(["Confirm the institution's full name, campus and official contact channel.", "Check that the department handles the type of consultation requested.", "Ask which identity documents and records are required.", "Ask how fees, receipts and follow-up contacts are provided."])),
    ("Language and payment need separate confirmation", p("An English website does not establish that every department offers an English-speaking clinician. Check consultation interpretation, written reports and payment support separately.") + p("If using insurance, ask the provider and insurer about direct billing, pre-authorization and the required documents. Do not assume a foreign insurance policy will be accepted.")),
    ("How IntersectionMed can support the choice", p("We can help communicate appointment options in public and private settings based on your requested service, dates, language and location. Licensed clinicians and institutions make clinical decisions. Ask about the proposed support and coordination fee before proceeding.")),
], [("can-foreigners-use-hospitals-in-shenzhen.html", "Prepare identity and registration details"), ("shenzhen-hospital-appointment-foreigners.html", "Check an appointment confirmation")])

guide("can-foreigners-use-hospitals-in-shenzhen.html", "Foreign-passport registration: questions before a hospital visit", "Clarify registration documents, name matching and booking channels with the institution before arrival.", "Hospital access", [
    ("Confirm the registration route", p("Ask the institution which booking channel accepts your identity document, whether an account is needed and whether registration is completed online or on arrival. Requirements vary by institution and department.")),
    ("Keep identity details consistent", ul(["Use the name format requested by the institution, matching your travel document.", "Ask which original identity document must be shown at registration.", "Confirm the contact number or email used for appointment messages.", "If booking for someone else, ask about any authorization requirements."])),
    ("Prepare without oversharing", p("For an initial inquiry to IntersectionMed, a general service request, dates and preferred language are enough to begin. Do not enter a passport number or attach sensitive records. When an institution requires documents, confirm a suitable sharing method first.")),
    ("If an online system does not work", p("Record the booking channel, the step that failed and any non-sensitive error message. Contact the institution's official service channel or ask about coordination support. Avoid making a second booking or payment without checking whether the first was recorded.")),
], [("shenzhen-hospitals-for-foreigners.html", "Compare public and private access"), ("foreigners-see-doctor-shenzhen.html", "Prepare for the day at the hospital")])

guide("shenzhen-hospital-appointment-foreigners.html", "What to check in a Shenzhen appointment confirmation", "A booking checklist for the campus, department, registration, payment and any changes.", "Hospital access", [
    ("If the appointment is not yet booked", p("Share the requested department or consultation, date range and language. Ask which details the institution needs and when a proposed time becomes confirmed. Keep travel plans flexible until those requirements are clear.")),
    ("If you have already booked", ul(["Confirm the full institution and exact campus or clinic.", "Check date, arrival time, department and booking reference where provided.", "Ask whether registration, payment or document checks must happen before the consultation.", "Request the address in Chinese and the contact channel for changes.", "If asking for an interpreter, share the confirmed location and support window."])),
    ("A booking is separate from a care plan", p("A consultation slot does not establish that a test or procedure will happen that day. The institution and clinician must confirm any preparation, consent, clinical assessment and further scheduling.")),
    ("When plans change", p("Ask the institution about its rescheduling process and notify any interpreter, transport or accommodation provider separately. Discuss the coordination scope and any change-related charges rather than assuming one cancellation covers every service.")),
], [("how-medical-travel-to-shenzhen-works.html", "Use the visit timeline"), ("contact.html", "Ask about appointment support")])

guide("foreigners-see-doctor-shenzhen.html", "The day at the hospital: registration to report collection", "Understand the practical handoffs during a planned Shenzhen appointment.", "Hospital access", [
    ("Find the right building and registration desk", p("Use the exact campus and department from your confirmation. Ask whether an original identity document, booking reference or registration payment is needed before joining the consultation queue.")),
    ("Make the consultation easier to follow", p("Prepare a brief list of questions and tell the care team which language you understand. If interpretation is arranged, speak in short sections and ask for clarification before agreeing to the next step.")),
    ("Confirm any additional steps", p("A clinician may discuss tests, other departments or another visit. Ask the provider where to go, whether another booking is needed, how charges are confirmed and when results will be ready. Clinical recommendations come from the care team.")),
    ("Before leaving the building", ul(["Keep receipts and provider-issued documents.", "Confirm report collection or online access instructions.", "Ask who will explain results and how to arrange follow-up.", "Confirm how to contact the institution with later questions."])),
], [("medical-translation-shenzhen.html", "Ask about on-site interpretation"), ("medical-translation-shenzhen-hospitals.html", "Organize the document handover")])

guide("medical-tourism-shenzhen-guide.html", "Your Shenzhen stay: accommodation, transport and daily essentials", "A travel checklist around a confirmed healthcare appointment, with room for schedule changes.", "Travel and arrival", [
    ("Choose accommodation after the appointment location", p("Check the actual route to the confirmed campus, accessibility, room arrangements for a companion and the hotel's guest-registration requirements. A familiar district name alone does not establish a short hospital journey.")),
    ("Keep essential information available", ul(["Institution and hotel names and addresses in Chinese and English.", "Appointment confirmation and official contact channels.", "A working phone connection and a way to contact your coordinator if arranged.", "Payment methods confirmed with the hospital and accommodation provider.", "Transport options for arrival and the appointment day."])),
    ("Build flexibility into the itinerary", p("A consultation, procedure, report and follow-up may fall on different dates. Check the provider's schedule and instructions before planning sightseeing, onward travel or a fixed return journey.")),
    ("Use current travel sources", p(f'Check <a href="{AIRPORT}" target="_blank" rel="noopener noreferrer">Shenzhen Airport</a> for current arrival information and <a href="{NIA}" target="_blank" rel="noopener noreferrer">official Mainland immigration information</a> for entry questions. A hospital appointment does not by itself establish permission to enter.')),
], [("shenzhen.html", "Explore Shenzhen's setting"), ("hong-kong-to-shenzhen-medical-visit-guide.html", "Plan a Hong Kong connection")])

guide("hong-kong-to-shenzhen-medical-visit-guide.html", "Hong Kong to Shenzhen: coordinate the whole journey", "Check entry, connections and the final hospital journey before fixing an appointment itinerary.", "Travel and arrival", [
    ("Check entry requirements for each part of the trip", p(f'Check the requirements for your passport and itinerary with <a href="{HK_ENTRY}" target="_blank" rel="noopener noreferrer">Hong Kong Immigration</a> and <a href="{NIA}" target="_blank" rel="noopener noreferrer">Mainland immigration authorities</a>. Do not assume eligibility for one part of the journey confirms the other.') + p("Check any return to Hong Kong as well as the first arrival. IntersectionMed coordinates travel logistics; entry decisions and requirements come from the authorities.")),
    ("Compare routes using the final destination", table(["Possible connection", "Confirm before choosing"], [("Cross-border rail", "Current departure and arrival stations, ticket availability, document checks and the onward hospital journey."), ("Land border connection", "Current crossing hours, transport on both sides and the final journey to your hotel or institution."), ("Airport and onward transfer", "Arrival time, the transfer operator's current route and the appointment arrival window.")]) + p("These are planning categories, not live timetables. Confirm current routes and operating information with the operator.")),
    ("Allow for more than scheduled travel time", p("Consider flight delays, immigration, luggage, transfers and registration before deciding whether arrival and a hospital appointment can share a day. Ask the institution whether a later arrival would affect the booking.")),
    ("Coordinate the return separately", p("Check any provider instructions, documents still pending and further appointments. Confirm accommodation, return transport and entry requirements for the return route before making fixed plans.")),
], [("medical-tourism-shenzhen-guide.html", "Prepare for your stay"), ("shenzhen-hospital-appointment-foreigners.html", "Check the appointment details")])

guide("health-checkup-china-planning-guide.html", "Prepare for a Shenzhen health checkup", "Separate package details, provider instructions, the day at the hospital and report follow-up.", "Service preparation", [
    ("Before choosing an appointment", p("Ask the provider what the package includes, which clinical consultation is available and whether any items require separate booking. The clinician determines what is medically appropriate; a larger list of tests is not itself a recommendation.")),
    ("Receive preparation from the provider", p("Confirm how to receive and understand instructions about attendance, food or drink, medication questions and documents. Ask the care team about any unclear instruction; do not rely on a generic travel checklist as medical preparation.")),
    ("Organize the day and the documents", ul(["Original identity document required by the institution.", "Appointment location and registration time.", "Relevant earlier reports requested by the provider, shared through an agreed channel.", "Questions for the clinician and the interpretation scope if arranged."])),
    ("Separate the checkup from the report timeline", p("An initial visit may fit around 1-2 days, while some reports or consultations may follow later. Ask when each report is expected, in which language, whether it can be accessed remotely and who provides the clinical explanation.")),
], [("health-checkup-china.html", "Health checkup coordination"), ("health-checkup-cost-china.html", "Compare the fee breakdown")])

guide("health-checkup-cost-china.html", "Health checkup costs: what to confirm in a quote", "Compare hospital charges, coordination support and travel expenses before making arrangements.", "Costs and scope", [
    ("Separate the three parts of your budget", table(["Cost", "What to clarify"], [("Healthcare provider", "Consultation, package items, any additional tests, reports and follow-up appointments."), ("Coordination and language support", "Appointment support, interpretation time, accompaniment, document translation and post-visit communication."), ("Travel and daily expenses", "Flights or rail, accommodation, local transport and companion arrangements.")]) + p("IntersectionMed coordination fees are discussed for your request. Contact us with the appointment type, dates and support you need; hospital and travel charges also require confirmation.")),
    ("Compare scope before comparing totals", ul(["Does the hospital quote list the actual items and consultations included?", "What could be charged separately, and who approves additional costs?", "Are English documents, interpretation and certified translations separate?", "Does support include waiting time, travel between sites or another visit?", "Which payee, currency, payment timing and receipt apply to each charge?"])),
    ("Discuss changes before paying", p("Ask how changes, cancellations, deposits and third-party charges would be handled. Appointment availability, the final clinical plan and the cost of additional care can change; request clarification for the particular booking.")),
    ("Request a discussion for your visit", p('A useful inquiry includes the service you are considering, approximate dates, whether a hospital is already chosen and any interpretation or accompaniment needs. <a href="contact.html">Ask about support and the applicable coordination fee</a>.')),
], [("services.html#fees", "Explore support scope"), ("health-checkup-china.html", "Health checkup service")])

guide("health-checkup-shenzhen-foreigners.html", "After a health checkup: reports, explanations and next steps", "Plan how to obtain, translate and discuss reports after leaving the checkup center.", "Reports and language", [
    ("Check the report timeline", p("Ask the provider which reports are available the same day and which will follow later. Confirm whether collection is on site, online or through another official route.")),
    ("Separate translation from clinical explanation", p("Written translation can convey the report's wording. The meaning of findings, any diagnosis and recommended follow-up must be explained by a licensed clinician. Ask how that discussion is arranged.")),
    ("Prepare a document handover", ul(["Keep original reports alongside translations.", "Record which documents are pending and the expected provider contact.", "Ask whether records can be shared with a clinician in your home country.", "Keep provider instructions and receipts available after departure."])),
    ("If questions arise after travelling home", p("Contact the healthcare institution about clinical questions or a further consultation. You can inquire about help translating questions and organizing the response, with the follow-up scope confirmed separately.")),
], [("health-checkup-china-planning-guide.html", "Prepare for the original visit"), ("medical-translation-shenzhen-hospitals.html", "Document handover checklist")])

guide("colonoscopy-endoscopy-shenzhen-guide.html", "Plan a digestive screening visit in Shenzhen", "Coordinate the consultation, provider-issued preparation, appointment day and report follow-up.", "Service preparation", [
    ("Identify the appointment being discussed", p("Gastroscopy, colonoscopy and an initial gastroenterology consultation are different requests. A clinician determines which examination, if any, is appropriate and whether further assessment is needed.")),
    ("Plan four stages rather than one appointment", table(["Stage", "Confirm with the provider"], [("Clinical consultation", "Whether assessment or review of prior records is needed before scheduling."), ("Preparation", "How and when provider instructions are delivered and questions answered."), ("Hospital attendance", "Registration, consent, language support and any companion requirements."), ("Results and follow-up", "Report timing, clinical explanation, further appointments and travel-related instructions.")])),
    ("Keep medical questions with the care team", p("Questions about medicines, food or drink, sedation, preparation, aftercare and return travel require provider instructions. IntersectionMed can help communicate those questions and translate the response.")),
    ("Allow flexibility", p("A 2-3 day window can be a starting point for some planned visits, not a guarantee that every stage will be completed. Confirm the actual appointment and report timeline before fixing travel.")),
], [("colonoscopy-shenzhen.html", "Colonoscopy appointment support"), ("endoscopy-shenzhen.html", "Endoscopy appointment support")])

guide("colonoscopy-china-planning-guide.html", "Questions before a colonoscopy-related visit", "A conversation checklist for the clinician and institution, covering scheduling and communication.", "Service preparation", [
    ("Ask about the initial assessment", ul(["Is a gastroenterology consultation needed before scheduling?", "Which previous reports or procedure records should the clinician review?", "How should medication and allergy information be provided securely?"])),
    ("Ask how instructions will reach you", p("Confirm the language and contact channel for provider-issued preparation, consent and aftercare information. Ask whom to contact if an instruction is unclear or your circumstances change.")),
    ("Ask about attendance arrangements", ul(["What arrival and registration time should you plan for?", "Are there companion or discharge arrangements to confirm?", "What questions should be answered before arranging return travel?", "When will the clinician explain findings and any further documents?"])),
    ("Use the checklist to support a conversation", p("These questions do not recommend colonoscopy or provide preparation instructions. The licensed clinician and institution must assess the request and supply the medical guidance.")),
], [("colonoscopy-endoscopy-shenzhen-guide.html", "Plan the full digestive visit"), ("colonoscopy-shenzhen.html", "Ask about coordination")])

guide("endoscopy-shenzhen-planning-guide.html", "Understanding provider instructions for an endoscopy visit", "Arrange the language, delivery and confirmation of preparation information from the healthcare institution.", "Service preparation", [
    ("Confirm which procedure is being discussed", p("Ask the care team to identify the proposed examination clearly, including whether it is upper gastrointestinal endoscopy (gastroscopy), colonoscopy or another procedure. Similar travel arrangements do not mean the clinical preparation is interchangeable.")),
    ("Request an understandable version", p("Confirm when instructions will arrive and ask for interpretation or translation if needed. Keep the original alongside any translation so questions can be checked against the provider's wording.")),
    ("Resolve questions before the visit", ul(["Which questions about medicines or health history should be raised with the clinician?", "Who should be contacted if instructions are missing or unclear?", "Which attendance, consent or companion arrangements need advance confirmation?", "How will changes to the appointment or preparation be communicated?"])),
    ("Keep provider guidance connected to the itinerary", p("Discuss the appointment, reports and any post-visit instructions before finalizing transport and activities. IntersectionMed does not set fasting, medication, preparation or aftercare rules.")),
], [("endoscopy-shenzhen.html", "Explore endoscopy coordination"), ("medical-translation-shenzhen.html", "Ask about interpretation")])

guide("dental-treatment-china-planning-guide.html", "Plan a dental consultation and any staged visits", "Separate the assessment, proposed treatment, laboratory work and follow-up before fixing travel.", "Service preparation", [
    ("Start with the consultation", p("Tell the provider the concern or treatment discussion you are seeking. Ask which earlier images or records it needs. The dentist assesses the case and proposes any clinical plan.")),
    ("Ask for the stages in writing", table(["Stage", "Questions"], [("Assessment", "Which examination and imaging are proposed, and how are they charged?"), ("Treatment discussion", "What options, materials, limitations and alternatives will the dentist explain?"), ("Scheduling", "Are laboratory work, healing intervals or additional visits part of the proposed plan?"), ("Follow-up", "What review or ongoing care is expected, and what happens after travelling home?")])),
    ("Compare the practical proposal", p("Ask for the appointment dates, cost breakdown, payment arrangements and the language of records. Confirm coordination and interpretation fees separately. A consultation does not guarantee a particular treatment or result.")),
    ("Plan travel after the stages are understood", p("Some visits are consultations only; other plans involve more than one trip. Ask the dental provider which parts can be scheduled during your stay and which remain provisional.")),
], [("dental-treatment-china.html", "Dental consultation coordination"), ("dental-treatment-shenzhen-foreigners.html", "Plan follow-up after travel")])

guide("dental-treatment-shenzhen-foreigners.html", "Dental follow-up after returning home", "Discuss records, provider contact and further appointments before leaving Shenzhen.", "Reports and language", [
    ("Ask about ongoing care before agreeing to a plan", p("Ask the dental provider which follow-up appointments are expected, whether further visits in Shenzhen are part of the plan and which questions require in-person assessment.")),
    ("Request the relevant records", ul(["Ask for the provider's written plan and any documents it can release.", "Confirm access to available images and reports.", "Keep payment records and provider-issued information about materials or procedures where applicable.", "Ask which information a clinician at home may need and in what language."])),
    ("Confirm the follow-up contact", p("Find out how to reach the dental team with clinical questions and what information it needs to identify the visit. Translation support may help communication but does not replace assessment by a licensed professional.")),
    ("Discuss additional costs and travel", p("Ask whether further consultations, translation, document work or return travel are separate charges. If arrangements change, confirm the provider's and coordination service's change terms individually.")),
], [("dental-treatment-china-planning-guide.html", "Understand staged dental visits"), ("medical-translation-shenzhen.html", "Discuss written translation")])

guide("medical-translation-shenzhen-guide.html", "Prepare for an interpreted medical consultation", "Make the language support useful by preparing questions, records and the scope of interpretation.", "Reports and language", [
    ("Confirm the interpretation task", p("Tell us the institution, campus, appointment type, date and language. Distinguish consultation interpretation from registration accompaniment, document translation and later follow-up. Ask about time on site and waiting or overtime arrangements.")),
    ("Prepare your questions", ul(["Write the main concerns you want the clinician to address.", "Ask which earlier reports or images the provider needs.", "Bring or securely share the original documents requested, rather than an unverified summary alone.", "Say if a companion will join and how you want communication handled."])),
    ("During the discussion", p("Address questions to the clinician, pause for interpretation and ask for clarification when needed. The interpreter conveys information; clinical advice, diagnoses, consent discussions and treatment decisions belong to the provider.")),
    ("Before leaving", p("Confirm that you understand the provider's next steps and how to obtain documents or further answers. Ask which written translations or later conversations require a separate support request.")),
], [("medical-translation-shenzhen.html", "Interpretation and accompaniment service"), ("medical-translation-shenzhen-hospitals.html", "Organize documents and follow-up")])

guide("medical-translation-shenzhen-hospitals.html", "Hospital documents: translation and handover checklist", "Keep original records, translated wording and clinical explanations distinct after a visit.", "Reports and language", [
    ("Create a document inventory", table(["Document", "Confirm"], [("Reports and images", "Which are ready, where to obtain them and whether any remain pending."), ("Provider instructions", "How to receive an understandable explanation and who answers clinical questions."), ("Receipts and supporting documents", "The payee, visit details and any insurer-specific document requirements."), ("Translations", "The target language, scope, deadline and whether certification is required.")])),
    ("Keep the original with the translation", p("A translation conveys document wording and should remain linked to the original. It does not independently explain the medical significance of findings. Ask a licensed clinician for interpretation and recommendations.")),
    ("Check certification requirements first", p("Hospitals, insurers and other receiving organizations may have different document rules. Ask the receiving organization whether it requires a certified translation, named translator or particular format before arranging the work.")),
    ("Share only through an agreed channel", p("Confirm which records are needed, who will receive them and how they should be transferred. Avoid putting detailed records, identity document numbers or payment information in an initial website inquiry.")),
], [("medical-translation-shenzhen-guide.html", "Prepare for interpretation"), ("privacy.html", "Information-sharing notice")])

# Keep every existing URL while directing the directory to distinct customer questions.
guide_groups = [
    ("Start here", "start-here", "Begin with the process, the timeline and the hospital setting.", ["medical-travel-shenzhen.html", "how-medical-travel-to-shenzhen-works.html", "shenzhen-hospitals-for-foreigners.html"]),
    ("Hospital access", "hospital-access", "Registration, booking confirmation and the day at the institution.", ["can-foreigners-use-hospitals-in-shenzhen.html", "shenzhen-hospital-appointment-foreigners.html", "foreigners-see-doctor-shenzhen.html"]),
    ("Service preparation", "preparation", "Prepare questions for the provider and plan the stages of your visit.", ["health-checkup-china-planning-guide.html", "colonoscopy-endoscopy-shenzhen-guide.html", "colonoscopy-china-planning-guide.html", "endoscopy-shenzhen-planning-guide.html", "dental-treatment-china-planning-guide.html"]),
    ("Costs and travel", "costs-travel", "Understand the budget and plan arrival and accommodation.", ["health-checkup-cost-china.html", "hong-kong-to-shenzhen-medical-visit-guide.html", "medical-tourism-shenzhen-guide.html"]),
    ("Reports and language", "reports-language", "Interpretation, documents and the handover after travelling home.", ["medical-translation-shenzhen-guide.html", "medical-translation-shenzhen-hospitals.html", "health-checkup-shenzhen-foreigners.html", "dental-treatment-shenzhen-foreigners.html"]),
]
guides = intro("Patient guides", "Clear answers for your first inquiry, hospital visit and travel planning.")
guides += '<div class="wrap"><nav class="topic-nav" aria-label="Guide topics">' + ''.join(f'<a href="#{ident}">{title}</a>' for title,ident,_,_ in guide_groups) + '</nav></div>'
for i, (title, ident, desc, filenames) in enumerate(guide_groups):
    grid = '<div class="grid">' + ''.join(f'<article class="guide-card"><span class="tag">{title}</span><h3>{PAGES[name]["title"].replace(" | IntersectionMed", "")}</h3><p>{PAGES[name]["desc"]}</p><a href="{name}">Read: {PAGES[name]["title"].replace(" | IntersectionMed", "")}</a></article>' for name in filenames) + '</div>'
    guides += f'<section class="band{" soft" if i%2 else ""}" id="{ident}"><div class="wrap"><div class="section-heading"><h2>{title}</h2><p>{desc}</p></div>{grid}</div></section>'
guides += band("Looking for coordination rather than a guide?", p('See the five <a href="services.html">visit support services</a>, including fertility assessment and TCM or rehabilitation coordination. If an appointment is already booked, you can also ask about <a href="medical-translation-shenzhen.html">interpretation and accompaniment</a>.') + scope()) + cta()
add("guides.html", "Patient Guides | Shenzhen Healthcare Travel | IntersectionMed", "Find distinct guides to hospital access, visit preparation, coordination costs, Hong Kong connections, interpretation and report handover.", guides, "CollectionPage")

original_contact = (ROOT / "contact.html").read_text()
country_match = re.search(r'<datalist id="country-options">.*?</datalist>', original_contact, re.S)
if not country_match:
    raise SystemExit("The existing country fallback was not found")
country_fallback = re.sub(r'<option\b([^>]*)>(?!</option>)', r'<option\1></option>', country_match.group())
contact = intro("Contact IntersectionMed", "Tell us the visit you are considering. We can discuss appointment support, language needs and the coordination fee for your request.")
contact += f'<div class="wrap contact-top"><a class="button" href="{WA}" target="_blank" rel="noopener noreferrer">Chat on WhatsApp</a><a href="mailto:intersectionmed@gmail.com">Email IntersectionMed</a><p>Usually within 1-2 business days &middot; China Standard Time (UTC+8)</p></div>'
contact += '''<section class="band"><div class="wrap contact-layout"><div class="contact-form"><h2>Request coordination support</h2><p class="privacy-hint" id="privacy-hint">Share general planning information only. Do not send passport numbers, payment details, medical records or imaging files in this initial inquiry.</p><form action="https://formsubmit.co/intersectionmed@gmail.com" method="POST" aria-describedby="privacy-hint"><input type="hidden" name="_subject" value="New Appointment Support Request - IntersectionMed"><input type="hidden" name="_captcha" value="true"><div class="form-row"><div class="field"><label for="fullname">Name *</label><input id="fullname" name="fullname" autocomplete="name" required maxlength="120"></div><div class="field"><label for="email">Email address *</label><input id="email" name="email" type="email" autocomplete="email" required maxlength="254"></div></div><div class="form-row"><div class="field"><label for="country">Country or region of residence *</label><div class="country-combo"><div class="country-controls"><input id="country" name="country" list="country-options" placeholder="Type to search or choose" autocomplete="country-name" required maxlength="100"><button class="country-open" type="button" aria-label="Show all countries and regions" title="Show all countries and regions" aria-controls="country-results" hidden>&#9662;</button></div><ul class="country-options" id="country-results" role="listbox" aria-label="Countries and regions" hidden></ul>''' + country_fallback + '''</div></div><div class="field"><label for="language">Preferred language</label><input id="language" name="language" placeholder="e.g., English or Chinese" autocomplete="off" maxlength="100"></div></div><div class="field"><label for="service-type">Service you are considering</label><select id="service-type" name="service_type"><option value="">Not yet decided</option><option>Health checkup coordination</option><option>Digestive screening support</option><option>Dental consultation support</option><option>Fertility assessment coordination</option><option>TCM and rehabilitation coordination</option><option>Interpretation or accompaniment</option><option>Other planned visit</option></select></div><div class="field"><label for="preferred-dates">Approximate travel dates</label><input id="preferred-dates" name="preferred_dates" placeholder="Month or date range, or not yet decided" maxlength="150"><p class="hint">You can inquire before booking travel.</p></div><div class="field"><label for="message">What would you like help with? *</label><textarea id="message" name="message" required maxlength="4000" placeholder="Describe the visit, whether an appointment is already booked, and any interpretation, accompaniment or travel support you need."></textarea></div><div class="consent"><input type="checkbox" id="privacy-consent" name="privacy_consent" value="accepted" required><label for="privacy-consent">I have read the <a href="privacy.html">Privacy Notice</a> and understand this is a non-emergency inquiry.</label></div><button class="button" type="submit">Send Inquiry</button></form></div><aside><section class="sidebar-section"><h2>What happens next?</h2><ol class="steps-list"><li>We review the service, timing and support you are asking about.</li><li>We reply with follow-up questions or the next coordination steps.</li><li>Discuss availability, support scope and fees before confirming arrangements.</li></ol><p>English and Chinese support. Other languages are subject to availability.</p></section><section class="sidebar-section"><div class="whatsapp-row"><div><h2>WhatsApp</h2><p>Open the contact link on your phone or scan from another device.</p>''' + f'<a href="{WA}" target="_blank" rel="noopener noreferrer">Open WhatsApp</a>' + '''</div><img src="whatsapp-qr.png" width="112" height="112" alt="Scan to contact IntersectionMed on WhatsApp" loading="lazy"></div></section><section class="sidebar-section"><h2>Service area: Shenzhen</h2><p>This city map shows the service area, not an office or a hospital appointment location.</p><iframe class="contact-map" title="Google Map of the Shenzhen service area" src="https://www.google.com/maps?q=Shenzhen%2C%20China&amp;z=12&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe><p><a href="https://www.google.com/maps/search/?api=1&amp;query=Shenzhen%2C%20China" target="_blank" rel="noopener noreferrer">Open full map</a></p></section><p class="privacy-hint">For urgent symptoms or emergencies, contact local emergency services or an appropriate medical facility. This inquiry channel is for planned visits.</p></aside></div><div class="wrap">''' + scope() + '</div></section>'
add("contact.html", "Contact IntersectionMed | Shenzhen Visit Support and Fees", "Discuss your Shenzhen appointment, interpretation, accompaniment and coordination fees. Contact IntersectionMed by WhatsApp, email or initial inquiry form.", contact, "ContactPage")

privacy = intro("Privacy notice", "Information shared through the IntersectionMed website and initial inquiry channels.")
privacy_sections = [
    ("Who to contact", p('IntersectionMed coordinates planned healthcare visits in Shenzhen. For questions about information you share with us, contact <a href="mailto:intersectionmed@gmail.com">intersectionmed@gmail.com</a>.')),
    ("Information in an initial inquiry", p("The form asks for your name, email, country or region of residence and a general description of the support requested. You may also provide language preferences and approximate travel dates. This information is used to respond and discuss coordination options.")),
    ("Sensitive documents", p("Do not submit passport numbers, payment details, full medical records or imaging through the website form or ordinary email. If records are needed for further coordination, first discuss which documents are necessary, who needs to receive them and an appropriate sharing channel.")),
    ("Website and communication services", ul(["The inquiry form posts to FormSubmit to deliver the message to intersectionmed@gmail.com. The service processes the submitted fields and may show its own verification or confirmation page.", "Opening a WhatsApp link takes you to WhatsApp; communication there is also subject to its service and privacy terms.", "The site uses Google Fonts. Pages that load Google Analytics use it for website-usage information. The contact page embeds a Google Map, which requests content from Google when loaded."]) + p('You can read the <a href="https://formsubmit.co/privacy.pdf" target="_blank" rel="noopener noreferrer">FormSubmit privacy information</a> and <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Google Privacy Policy</a>.')),
    ("Coordination and onward sharing", p("If you continue beyond an initial inquiry, clarify which information a hospital, interpreter or other service provider needs before sharing records. An inquiry alone is not a confirmed appointment or agreement to a care plan.")),
    ("Questions, corrections and deletion requests", p("Email us to ask about information submitted to IntersectionMed, request a correction or raise a deletion request. Identify the inquiry using minimal details; do not attach sensitive records to make the request. Handling depends on the information concerned and any applicable requirements.")),
]
privacy += '<div class="band"><div class="wrap reading article-body">' + ''.join(section(h,t,f'privacy-{i}') for i,(h,t) in enumerate(privacy_sections)) + scope() + f'<p class="article-meta">Updated {DATE}</p></div></div>'
add("privacy.html", "Privacy Notice | IntersectionMed", "How IntersectionMed's initial inquiry form and website services handle information, with contact details for privacy questions.", privacy)


def write_pages():
    existing = {p.name for p in ROOT.glob("*.html")}
    if existing != set(PAGES):
        raise SystemExit(f"Page inventory mismatch: missing={existing-set(PAGES)}, unexpected={set(PAGES)-existing}")
    for name, info in PAGES.items():
        original = (ROOT / name).read_text()
        analytics = ''
        if "G-JMX3WEED6K" in original:
            analytics = '''<script async src="https://www.googletagmanager.com/gtag/js?id=G-JMX3WEED6K"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-JMX3WEED6K');</script>'''
        canonical = BASE if name == 'index.html' else BASE + name
        active = name if name in dict(NAV) else 'services.html' if info['kind'] == 'Service' else 'guides.html' if info['kind'] == 'Article' else ''
        if info['kind'] == 'Service':
            schema = {"@context":"https://schema.org", "@type":"Service", "name":info['title'].split(' | ')[0], "description":info['desc'], "url":canonical, "provider":{"@type":"Organization","name":"IntersectionMed","url":BASE}, "areaServed":{"@type":"City","name":"Shenzhen"}}
        else:
            schema = {"@context":"https://schema.org", "@type":info['kind'], "name":info['title'], "description":info['desc'], "url":canonical}
            if info['kind'] == 'Article':
                schema.update({"headline":info['title'].split(' | ')[0], "author":{"@type":"Organization","name":"IntersectionMed","url":BASE}, "dateModified":DATE})
        if name == 'index.html':
            schema = {"@context":"https://schema.org", "@type":"Organization", "name":"IntersectionMed", "url":BASE, "logo":BASE+'logo.png', "email":"intersectionmed@gmail.com", "description":info['desc'], "address":{"@type":"PostalAddress","addressLocality":"Shenzhen","addressCountry":"CN"}}
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(info['title'])}</title>
<meta name="description" content="{escape(info['desc'], quote=True)}">
<link rel="icon" href="logo.png" type="image/png">
<link rel="canonical" href="{canonical}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="docs/site.css?v=20261015">
<script src="docs/site.js?v=20261015" defer></script>
{analytics}
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=True)}</script>
</head>
<body>
{navigation(active)}
<main id="main-content" tabindex="-1">
{info['body']}
</main>
{FOOTER}
</body>
</html>
'''
        (ROOT / name).write_text(html, encoding='utf-8')
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace('', namespace)
    tree = ET.ElementTree(ET.Element(f'{{{namespace}}}urlset'))
    for name in sorted(PAGES):
        entry = ET.SubElement(tree.getroot(), f'{{{namespace}}}url')
        ET.SubElement(entry, f'{{{namespace}}}loc').text = BASE if name == 'index.html' else BASE + name
        ET.SubElement(entry, f'{{{namespace}}}lastmod').text = DATE
    ET.indent(tree, space='  ')
    tree.write(ROOT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    print(f"Updated {len(PAGES)} existing pages and sitemap. No URLs removed.")


write_pages()
