#!/usr/bin/env python3
"""Create public SEO files after the final production domain is known.

Example: python tools/prepare-seo-launch.py --domain https://example.com --commit
Without --commit the utility previews only, preserving the private concept.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parent.parent
PUBLIC=['index.html','services.html','about.html','reviews.html','bgsu.html','contact.html','maintenance.html','brake-repair.html','diagnostics.html','engine-repair.html','electrical-repair.html','ac-heating.html','suspension-steering.html','wheel-alignment.html']
DIRECTIVE='index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1'
SOCIAL_IMAGE='/assets/social-share-jt-auto-service.png'
SOCIAL_IMAGE_ALT='Dark performance sedan in a clean J&T-style service bay with subtle lime workshop lighting'

def args():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--domain',required=True,help='Final HTTPS canonical origin')
    p.add_argument('--commit',action='store_true',help='Write files; omit for preview')
    p.add_argument('--business-image',help='Absolute URL to a genuine J&T shop image')
    p.add_argument('--social-image',default=SOCIAL_IMAGE,help='Absolute URL or site-relative social card image')
    p.add_argument('--latitude',type=float); p.add_argument('--longitude',type=float)
    p.add_argument('--price-range',help='Owner-approved value such as $$')
    return p.parse_args()

def domain(value):
    value=value.strip().rstrip('/'); parsed=urlparse(value)
    if parsed.scheme!='https' or not parsed.netloc or parsed.query or parsed.fragment:
        raise SystemExit('ERROR: --domain must be a clean HTTPS origin, e.g. https://www.example.com')
    return value

def url(base,name): return base+'/' if name=='index.html' else f'{base}/{name}'
def asset_url(base,value): return value if value.startswith(('http://','https://')) else base+'/'+value.lstrip('/')

def tag_with_content(source,attribute,key,content):
    pattern=rf'<meta\b(?=[^>]*\b{attribute}="{re.escape(key)}")(?=[^>]*\bcontent=")[^>]*>'
    def replace(match): return re.sub(r'\bcontent="[^"]*"',f'content="{content}"',match.group(0))
    source,count=re.subn(pattern,replace,source,count=1,flags=re.I)
    if not count: source=source.replace('</head>',f'<meta {attribute}="{key}" content="{content}"/></head>',1)
    return source

def set_canonical(source,canonical):
    tag=f'<link rel="canonical" href="{canonical}"/>'
    source,count=re.subn(r'<link\b(?=[^>]*\brel="canonical")[^>]*>',tag,source,count=1,flags=re.I)
    return source if count else source.replace('</head>',tag+'</head>',1)

def set_favicon(source):
    tag='<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg"/>'
    source,count=re.subn(r'<link\b(?=[^>]*\brel="icon")[^>]*>',tag,source,count=1,flags=re.I)
    return source if count else source.replace('</head>',tag+'</head>',1)

def meta_content(source,attribute,key):
    for tag in re.findall(r'<meta\b[^>]*>',source,re.I):
        if re.search(rf'\b{attribute}="{re.escape(key)}"',tag,re.I):
            match=re.search(r'\bcontent="([^"]*)"',tag,re.I)
            return match.group(1) if match else ''
    return ''

def absolute(value,base,filename):
    if not isinstance(value,str) or value.startswith(('http://','https://','mailto:','tel:')): return value
    if value=='index.html': return url(base,'index.html')
    if value.endswith('.html'): return url(base,value)
    return url(base,filename)+value if value.startswith('#') else value

def enrich(node,base,filename,opt):
    if isinstance(node,dict):
        kind=node.get('@type')
        if kind=='AutoRepair':
            node['url']=url(base,'index.html')
            if opt.business_image: node['image']=opt.business_image
            if opt.latitude is not None: node['geo']={'@type':'GeoCoordinates','latitude':opt.latitude,'longitude':opt.longitude}
            if opt.price_range: node['priceRange']=opt.price_range
        if kind=='WebSite': node.update({'url':url(base,'index.html'),'@id':url(base,'index.html')+'#website'})
        if kind=='WebPage': node.update({'url':url(base,filename),'@id':url(base,filename)+'#webpage'})
        if kind=='BreadcrumbList':
            for item in node.get('itemListElement',[]):
                if isinstance(item,dict) and 'item' in item: item['item']=absolute(item['item'],base,filename)
        for key,value in node.items():
            if key not in {'sameAs','url','image'}: enrich(value,base,filename,opt)
    elif isinstance(node,list):
        for value in node: enrich(value,base,filename,opt)

def transform(path,base,opt):
    source=path.read_text(encoding='utf-8')
    for name in ('robots','googlebot','bingbot'): source=tag_with_content(source,'name',name,DIRECTIVE)
    title=re.search(r'<title>(.*?)</title>',source,re.I|re.S)
    if title: source=tag_with_content(source,'property','og:title',title.group(1).strip())
    description=meta_content(source,'name','description')
    if description: source=tag_with_content(source,'property','og:description',description)
    source=tag_with_content(source,'property','og:type','website')
    source=tag_with_content(source,'property','og:site_name','J&amp;T Auto Service of BG')
    social_image=asset_url(base,opt.social_image)
    source=tag_with_content(source,'property','og:image',social_image)
    source=tag_with_content(source,'property','og:image:alt',SOCIAL_IMAGE_ALT)
    source=tag_with_content(source,'name','twitter:card','summary_large_image')
    if title: source=tag_with_content(source,'name','twitter:title',title.group(1).strip())
    if description: source=tag_with_content(source,'name','twitter:description',description)
    source=tag_with_content(source,'name','twitter:image',social_image)
    source=tag_with_content(source,'name','twitter:image:alt',SOCIAL_IMAGE_ALT)
    source=tag_with_content(source,'property','og:url',url(base,path.name)); source=set_canonical(source,url(base,path.name))
    source=set_favicon(source)
    pattern=r'(<script\b[^>]*\btype="application/ld\+json"[^>]*>)(.*?)(</script>)'
    def schema(match):
        payload=json.loads(match.group(2)); enrich(payload,base,path.name,opt)
        return match.group(1)+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+match.group(3)
    return re.sub(pattern,schema,source,flags=re.I|re.S)

def main():
    opt=args(); base=domain(opt.domain)
    if (opt.latitude is None)!=(opt.longitude is None): raise SystemExit('ERROR: provide both --latitude and --longitude, or neither.')
    outputs={ROOT/name:transform(ROOT/name,base,opt) for name in PUBLIC}
    rows='\n'.join(f'  <url><loc>{url(base,name)}</loc></url>' for name in PUBLIC)
    outputs[ROOT/'sitemap.xml']=f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}\n</urlset>\n'
    outputs[ROOT/'robots.txt']=f'User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n'
    print('SEO launch preview\n'+'\n'.join(f' - {path.relative_to(ROOT)}' for path in outputs))
    if not opt.commit: print('\nPrivate mode preserved. Re-run with --commit after reviewing final facts.'); return
    for path,text in outputs.items(): path.write_text(text,encoding='utf-8',newline='\n')
    print(f'\nWrote {len(outputs)} launch files. Review the diff before deploying.')
if __name__=='__main__': main()
