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
        self.script = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag not in VOID:
            self.stack.append(tag)
        if tag == 'h1':
            self.h1 += 1
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.references.append(attrs[key])
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
    assert len(parsed.ids) == len(set(parsed.ids)), (file.name, 'Duplicate IDs')
    assert len(parsed.scripts) == 1, (file.name, 'Structured data')
    assert source.count('class="site-footer"') == 1, file.name
    assert 'does not provide medical diagnosis, treatment, or medical advice' in source, file.name
    assert 'Usually within 1-2 business days.' in source, file.name
    assert not re.search(r'within (?:1 business day|24 hours)|Five starting points|See the five', source, re.I), file.name
    pages[file.name] = (source, parsed)

assert len(pages) == 32, len(pages)
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
    assert f'docs/images/service-{asset}.png' in home, ('Missing service image', asset)
assert 'AI-generated service illustrations' in home and 'AI-generated illustration, not a partner clinic.' in home
assert 'class="visual-process"' in home
contact = pages['contact.html'][0]
assert 'value="checkup"' in contact and 'value="dental"' in contact and 'value="digestive"' in contact
assert 'https://formsubmit.co/intersectionmed@gmail.com' in contact
assert 'privacy-consent' in contact and 'country-options' in contact
assert 'https://wa.me/qr/TY3MLSWE4SS7D1' in contact
print(f'PASS: {len(pages)} pages; valid nesting, shared header/footer, local links/anchors/assets, metadata, sitemap and content boundaries.')
