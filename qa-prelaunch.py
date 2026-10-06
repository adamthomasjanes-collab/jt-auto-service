"""Dependency-free release gate for the static J&T website."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).parent
PAGES = [
    'index.html', 'services.html', 'about.html', 'reviews.html', 'bgsu.html',
    'contact.html', 'privacy.html', 'maintenance.html', 'brake-repair.html',
    'diagnostics.html', 'engine-repair.html', 'electrical-repair.html',
    'ac-heating.html', 'suspension-steering.html', 'wheel-alignment.html',
]
errors = []
for name in PAGES:
    page = ROOT / name
    html = page.read_text(encoding='utf-8')
    if not re.search(r'<meta[^>]+name="viewport"', html, re.I):
        errors.append(f'{name}: missing responsive viewport meta tag')
    if not re.search(r'<meta(?=[^>]*name="robots")(?=[^>]*noindex)[^>]*>', html, re.I):
        errors.append(f'{name}: private-preview noindex guard missing')
    if re.search(r'<form\b|serviceRequestForm|contact\.html#request|href="#request"', html, re.I):
        errors.append(f'{name}: retired online-request workflow remains')
    if not re.search(r'class="[^"]*desktop-cta[^"]*"[^>]+href="tel:\+14198194069"', html, re.I):
        errors.append(f'{name}: desktop call CTA does not use the business number')
    dock = re.search(r'<div aria-label="Quick actions" class="mobileBar">(.*?)</div>', html, re.S)
    expected_dock = ('mobileCallCta" href="tel:+14198194069">Call J&amp;T</a>'
                     '<a class="mobileCall" href="tel:+14198194069">(419) 819-4069</a>'
                     '<a class="mobileDirections" href="https://www.google.com/maps/dir/')
    if not dock or expected_dock not in dock.group(1):
        errors.append(f'{name}: mobile dock must be Call J&T, phone number, Directions')
    elif (len(re.findall(r'<a\b', dock.group(1), re.I)) != 3 or
          'mobileRequest' in dock.group(1) or
          dock.group(1).count('mobileCallCta') != 1):
        errors.append(f'{name}: mobile dock must contain exactly three actions (no duplicate call CTA)')
    for actions in re.findall(r'<div class="actions">(.*?)</div>', html, re.S):
        if len(re.findall(r'href="tel:\+14198194069"', actions)) > 1:
            errors.append(f'{name}: duplicate call actions in one decision group')

system = (ROOT / 'system.css').read_text(encoding='utf-8')
card_images = {
    'maintenance.html': 'maintenance-hero-ai-v2.png',
    'brake-repair.html': 'brake-hero-ai.png',
    'diagnostics.html': 'diagnostics-engine-ai.png',
    'engine-repair.html': 'engine-hero-ai.png',
    'electrical-repair.html': 'electrical-hero-ai.png',
    'ac-heating.html': 'climate-hero-ai.png',
    'suspension-steering.html': 'suspension-hero-ai.png',
    'wheel-alignment.html': 'alignment-hero-ai.png',
}
for route, asset in card_images.items():
    if f'.serviceCard[href="{route}"]:after' not in system:
        errors.append(f'system.css: missing related-card image rule for {route}')
    if not (ROOT / 'assets' / 'image-audit' / asset).exists():
        errors.append(f'assets/image-audit/{asset}: missing related-card image asset')

if errors:
    print('PRELAUNCH QA: FAIL')
    print('\n'.join(f' - {error}' for error in errors))
    sys.exit(1)
print(f'PRELAUNCH QA: PASS — {len(PAGES)} pages, call-first conversion, private-preview guards and related-card imagery verified.')
