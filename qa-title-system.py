from pathlib import Path
import re, sys
root=Path(__file__).parent
customer=['index.html','services.html','about.html','reviews.html','bgsu.html','contact.html','maintenance.html','brake-repair.html','diagnostics.html','engine-repair.html','electrical-repair.html','ac-heating.html','suspension-steering.html','wheel-alignment.html']
errors=[]
for name in customer:
    s=(root/name).read_text(encoding='utf-8')
    h1s=re.findall(r'<h1\b[^>]*>.*?</h1>',s,re.S|re.I)
    if not h1s:
        errors.append(f'{name}: missing H1')
        continue
    h=h1s[0]
    if 'title-pair' not in h or 'title-setup' not in h or 'title-payoff' not in h:
        errors.append(f'{name}: H1 does not use universal setup/payoff title system')
    if name=='index.html' and 'title-hero' not in h:
        errors.append('index.html: homepage H1 must use title-hero')
    if name!='index.html' and 'title-page' not in h:
        errors.append(f'{name}: interior H1 must use title-page')
css=(root/'styles.css').read_text(encoding='utf-8')
for token in ['--title-hero-setup','--title-hero-payoff','--title-page-setup','--title-page-payoff','--title-section-setup','--title-section-payoff']:
    if token not in css: errors.append(f'styles.css: missing {token}')
if errors:
    print('TITLE QA: FAIL')
    print('\n'.join(' - '+e for e in errors))
    sys.exit(1)
print(f'TITLE QA: PASS — {len(customer)} customer-facing pages checked')
