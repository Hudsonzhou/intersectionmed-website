"""Validate the generated site's inventory, markup, local targets and business boundaries."""

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(sys.argv[1]).resolve()
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.references, self.ids, self.scripts = [], [], [], [], []
        self.h1 = 0
        self.headings = []
        self.metadata, self.images = {}, []
        self.script = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag not in VOID:
            self.stack.append(tag)
        if tag == 'h1':
            self.h1 += 1
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.headings.append(int(tag[1]))
        if tag == 'meta':
            self.metadata[attrs.get('name') or attrs.get('property')] = attrs.get('content', '')
        if tag == 'link' and attrs.get('rel') == 'canonical':
            assert 'canonical' not in self.metadata, 'Duplicate canonical'
            self.metadata['canonical'] = attrs.get('href')
        if tag == 'img':
            self.images.append(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.references.append(attrs[key])
        if attrs.get('srcset'):
            self.references.extend(candidate.strip().split()[0] for candidate in attrs['srcset'].split(','))
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.script = ''

    def handle_endtag(self, tag):
        if tag in VOID:
            self.errors.append(f'Closing void tag: {tag}')
        elif not self.stack or self.stack[-1] != tag:
            self.errors.append(f'Mismatched closing {tag}: {self.stack[-3:]}')
        else:
            self.stack.pop()
        if tag == 'script' and self.script is not None:
            self.scripts.append(json.loads(self.script))
            self.script = None

    def handle_data(self, data):
        if self.script is not None:
            self.script += data


pages = {}
for file in ROOT.glob('*.html'):
    source = file.read_text()
    parsed = Page()
    parsed.feed(source)
    assert not parsed.errors and not parsed.stack, (file.name, parsed.errors, parsed.stack)
    assert parsed.h1 == 1, (file.name, 'H1 count')
    assert parsed.headings[0] == 1 and all(next_level <= level + 1 for level, next_level in zip(parsed.headings, parsed.headings[1:])), (file.name, 'Skipped heading level')
    assert len(parsed.ids) == len(set(parsed.ids)), (file.name, 'Duplicate IDs')
    assert len(parsed.scripts) == 1, (file.name, 'Structured data')
    title = re.findall(r'<title>(.*?)</title>', source, re.S)
    assert len(title) == 1 and title[0].strip(), (file.name, 'Title')
    parsed.metadata['title'] = title[0]
    assert parsed.metadata.get('description', '').strip(), (file.name, 'Description')
    canonical = 'https://intersectionmed.com/' + ('' if file.name == 'index.html' else file.name)
    assert parsed.metadata.get('canonical') == canonical, (file.name, 'Canonical')
    assert parsed.metadata.get('og:url') == canonical, (file.name, 'OG URL')
    assert parsed.metadata.get('viewport') == 'width=device-width, initial-scale=1'
    assert all(img.get('alt', '').strip() and img.get('width') and img.get('height') for img in parsed.images), (file.name, 'Image accessibility or dimensions')
    assert source.count('src="docs/analytics.js?') == (0 if file.name == 'privacy.html' else 1), (file.name, 'Analytics loader')
    assert 'googletagmanager.com/gtag/js' not in source, (file.name, 'Duplicate inline analytics')
    assert source.count('class="site-footer"') == 1, file.name
    assert 'does not provide medical diagnosis, treatment, or medical advice' in source, file.name
    assert 'Usually within 1-2 business days.' in source, file.name
    assert not re.search(r'within (?:1 business day|24 hours)|Five starting points|See the five', source, re.I), file.name
    pages[file.name] = (source, parsed)

assert len(pages) == 32, len(pages)
for key in ('title', 'description'):
    values = [page.metadata[key] for _, page in pages.values()]
    assert len(values) == len(set(values)), ('Duplicate SEO metadata', key)
footers = {re.search(r'<footer class="site-footer">.*?</footer>', source, re.S).group() for source, _ in pages.values()}
headers = {re.search(r'<header class="site-header">.*?</header>', source, re.S).group().replace(' aria-current="page"', '') for source, _ in pages.values()}
assert len(footers) == 1 and len(headers) == 1, 'Shared chrome mismatch'

for name, (_, page) in pages.items():
    for reference in page.references:
        url = urlsplit(reference)
        if url.scheme or url.netloc:
            continue
        target = ROOT / unquote(url.path) if url.path else ROOT / name
        assert target.exists(), (name, reference, 'Missing local target')
        if url.fragment and target.suffix == '.html':
            assert unquote(url.fragment) in pages[target.name][1].ids, (name, reference, 'Missing fragment')

sitemap = ET.parse(ROOT / 'sitemap.xml')
locations = [element.text for element in sitemap.iter() if element.tag.endswith('}loc')]
expected = {'https://intersectionmed.com/' if name == 'index.html' else 'https://intersectionmed.com/' + name for name in pages}
assert set(locations) == expected, 'Sitemap inventory mismatch'
home = pages['index.html'][0]
assert 'Fertility assessment coordination' not in home and 'Optional consultation' in home
assert home.count('class="visual-service"') == 3, 'Core visual service entries'
for asset in ('checkup', 'dental', 'digestive', 'tcm'):
    assert f'docs/images/service-{asset}-960.webp' in home, ('Missing service image', asset)
assert 'AI-generated service illustrations' in home and 'AI-generated illustration, not a partner clinic.' in home
assert 'class="visual-process"' in home
assert 'class="hero-image"' in home and 'fetchpriority="high"' in home
assert 'srcset=' in home and '?v=20261027' in home
assert 'Need Medical Care in Shenzhen?' in home and 'Why choose IntersectionMed?' in home
assert 'Hospital Appointment Coordination' in home and 'class="header-inquiry"' in home
contact = pages['contact.html'][0]
assert 'value="checkup"' in contact and 'value="dental"' in contact and 'value="digestive"' in contact
assert 'https://formsubmit.co/intersectionmed@gmail.com' in contact
assert 'privacy-consent' in contact and 'country-options' in contact
assert 'https://wa.me/qr/TY3MLSWE4SS7D1' in contact
assert 'name="_captcha" value="true"' in contact, 'CAPTCHA must remain enabled'
assert contact.count('name="_url" value="https://intersectionmed.com/contact.html"') == 1, 'Missing fixed FormSubmit source URL'
assert 'local-preview-notice' in contact, 'Missing local-file preview warning'
assert 'form-status' in contact and 'same-tab-submit' in contact and 'edit-inquiry' in contact
assert 'novalidate' not in contact, 'No-JS validation must remain native'
robots = (ROOT / 'robots.txt').read_text()
assert 'Sitemap: https://intersectionmed.com/sitemap.xml' in robots
assert 'Disallow: /\n' not in robots and 'Disallow: /docs/' not in robots
print(f'PASS: {len(pages)} pages; valid nesting, shared header/footer, local links/anchors/assets, metadata, sitemap and content boundaries.')
