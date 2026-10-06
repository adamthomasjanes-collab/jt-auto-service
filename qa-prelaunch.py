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
    if not re.search(r'<meta(?=[^>]*name="robots")(?=[^>]*content="index,follow)[^>]*>', html, re.I):
        errors.append(f'{name}: production index,follow robots directive missing')
    if 'https://jtautobg.com/' not in html or 'rel="canonical"' not in html:
        errors.append(f'{name}: production canonical URL missing')
    required_social = (
        ('property', 'og:title', None), ('property', 'og:description', None),
        ('property', 'og:image', 'https://jtautobg.com/assets/social-share-jt-auto-service.png'),
        ('property', 'og:image:secure_url', 'https://jtautobg.com/assets/social-share-jt-auto-service.png'),
        ('property', 'og:image:type', 'image/png'), ('property', 'og:image:width', '1734'),
        ('property', 'og:image:height', '907'), ('name', 'twitter:card', 'summary_large_image'),
        ('name', 'twitter:image', 'https://jtautobg.com/assets/social-share-jt-auto-service.png'),
    )
    if any(not re.search(rf'<meta(?=[^>]*\b{attribute}="{re.escape(key)}")' +
                         (rf'(?=[^>]*\bcontent="{re.escape(value)}")' if value else '') +
                         r'[^>]*>', html, re.I)
           for attribute, key, value in required_social):
        errors.append(f'{name}: complete Open Graph and X/Discord social-card metadata missing')
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
script = (ROOT / 'script.js').read_text(encoding='utf-8')
if "['Bowling Green', 'Bowling\\u00a0Green']" not in script:
    errors.append('script.js: Bowling Green no-break proper-noun guard missing')
if "parent.closest('script,style,h1,h2,h3,h4,h5,h6')" in script:
    errors.append('script.js: proper-noun guard must also protect headings')
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
    if f'.serviceCard[href="{route}"]{{--service-card-image:' not in system:
        errors.append(f'system.css: missing shared service-card image rule for {route}')
    if not (ROOT / 'assets' / 'image-audit' / asset).exists():
        errors.append(f'assets/image-audit/{asset}: missing service-card image asset')

services_html = (ROOT / 'services.html').read_text(encoding='utf-8')
directory_routes = re.findall(r'<a class="serviceCard[^>]+href="([^"]+)"', services_html)
if set(directory_routes) != set(card_images):
    errors.append('services.html: every directory service card must map to a known image-backed service route')
for page in ROOT.glob('*.html'):
    html = page.read_text(encoding='utf-8')
    for route in re.findall(r'<a class="serviceCard" href="([^"]+)"', html):
        if route not in card_images:
            errors.append(f'{page.name}: related service card {route} has no image mapping')

if errors:
    print('PRELAUNCH QA: FAIL')
    print('\n'.join(f' - {error}' for error in errors))
    sys.exit(1)
robots = (ROOT / 'robots.txt').read_text(encoding='utf-8')
if 'Allow: /' not in robots or 'https://jtautobg.com/sitemap.xml' not in robots:
    print('PRELAUNCH QA: FAIL\n - robots.txt: public crawler access and sitemap reference required')
    sys.exit(1)
if not (ROOT / 'sitemap.xml').exists():
    print('PRELAUNCH QA: FAIL\n - sitemap.xml: missing production sitemap')
    sys.exit(1)
print(f'PRELAUNCH QA: PASS — {len(PAGES)} public pages, call-first conversion, canonical SEO and related-card imagery verified.')
