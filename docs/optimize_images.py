"""Export responsive WebP variants without overwriting the source photography."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
encoder = shutil.which('cwebp')
if not encoder:
    raise SystemExit('Install the official libwebp cwebp encoder first.')
images = root / 'docs/images'
report = []
for source in sorted(images.glob('service-*.png')):
    sizes = []
    for width in (480, 960):
        target = source.with_name(f'{source.stem}-{width}.webp')
        subprocess.run([encoder, '-quiet', '-q', '82', '-m', '6', '-resize', str(width), '0', str(source), '-o', str(target)], check=True)
        sizes.append({'width': width, 'bytes': target.stat().st_size})
    report.append({'source':source.name, 'original_bytes':source.stat().st_size, 'variants':sizes})
for name in ('shenzhen-bay-skyline', 'shenzhen-bay-sunset'):
    source = images / (name + '.jpg')
    sizes = []
    for width in (800, 1600):
        target = source.with_name(f'{name}-{width}.webp')
        subprocess.run([encoder, '-quiet', '-q', '82', '-m', '6', '-resize', str(width), '0', str(source), '-o', str(target)], check=True)
        sizes.append({'width':width, 'bytes':target.stat().st_size})
    report.append({'source':source.name, 'original_bytes':source.stat().st_size, 'variants':sizes})
print(json.dumps(report, indent=2))
