"""Dependency-free navigation shell contract check."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).parent
PAGES = [
    'index.html', 'services.html', 'maintenance.html', 'brake-repair.html',
    'diagnostics.html', 'engine-repair.html', 'electrical-repair.html',
    'ac-heating.html', 'suspension-steering.html', 'wheel-alignment.html',
    'about.html', 'reviews.html', 'bgsu.html', 'contact.html', 'privacy.html',
    '404.html',
]
errors = []
for name in PAGES:
    html = (ROOT / name).read_text(encoding='utf-8')
    required = [
        'class="top"',
        'class="brand" href="index.html"',
        'src="assets/jt-logo.png"',
        'aria-label="Primary" id="nav"',
        'aria-controls="servicesMenu"',
        'href="reviews.html">Reviews</a>',
        'href="bgsu.html">BGSU Students</a>',
        'href="about.html">About</a>',
        'href="contact.html">Contact</a>',
        'class="navPhone" href="tel:+14198194069"',
        'class="cta small desktop-cta" href="tel:+14198194069">Call J&amp;T</a>',
        'class="mobileCallCta" href="tel:+14198194069">Call J&amp;T</a>',
        'class="mobileCall" href="tel:+14198194069">(419) 819-4069</a>',
        'class="mobileDirections" href="https://www.google.com/maps/dir/',
    ]
    for token in required:
        if token not in html:
            errors.append(f'{name}: missing canonical navigation token {token!r}')
    if not re.search(r'class="servicesNavButton(?:\s+[^"]+)?"', html):
        errors.append(f'{name}: missing Services menu control')
    nav = re.search(r'<nav[^>]*id="nav"[^>]*>(.*?)</nav>', html, re.S)
    if not nav:
        errors.append(f'{name}: missing primary nav')
        continue
    for label in ['Reviews', 'BGSU Students', 'About', 'Contact']:
        if f'>{label}</a>' not in nav.group(1):
            errors.append(f'{name}: missing {label} in primary nav')

if errors:
    print('NAVIGATION QA: FAIL')
    print('\n'.join(f' - {error}' for error in errors))
    sys.exit(1)
print(f'NAVIGATION QA: PASS — {len(PAGES)} pages share the call-first navigation and mobile dock.')
