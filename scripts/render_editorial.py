#!/usr/bin/env python3
"""CADERNA: source-anchored editorial art renderer. Free Pillow/CairoSVG.
Run: python scripts/render_editorial.py incoming/<slug>.json
Only renders supplied editorial copy. Never invents facts or touches Meta.
"""
from __future__ import annotations
import io,json,re,sys,os,textwrap,datetime,hashlib
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image,ImageDraw,ImageFont,ImageOps
import cairosvg

ROOT=Path(__file__).resolve().parents[1]
INK='#101C2E';PAPER='#F5F3ED';CORAL='#EA674D';MUTED='#5C6B7B';BLUE='#3356EA'
W,H=1080,1350
FONT={
  'display':'/usr/share/fonts/truetype/noto/NotoSansDisplay-ExtraCondensedBlack.ttf',
  'serif':'/usr/share/fonts/truetype/noto/NotoSerifDisplay-CondensedBlackItalic.ttf',
  'bold':'/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf',
  'reg':'/usr/share/fonts/opentype/inter/InterDisplay-Regular.otf',
}
for name,path in FONT.items():
    if not Path(path).is_file():raise RuntimeError('Required free font missing: '+name)
def font(face,size):return ImageFont.truetype(FONT[face],size)
def assert_story(m):
    if not isinstance(m,dict):raise ValueError('JSON story required')
    slug=m.get('id','')
    if not isinstance(slug,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}-[a-z0-9-]{7,64}',slug):
        raise ValueError('Dated, unique story slug required')
    if m.get('kind') not in ('headline','carousel','explainer'):raise ValueError('Unexpected family')
    if m.get('theme') not in ('ink','cream'):raise ValueError('Choose canonical theme')
    if m.get('risk') not in ('low','high'):
        raise ValueError('Every story must declare low or high risk')
    high=m.get('risk')=='high'
    if high:
        if m.get('editorial_process')!='source-anchored-triple-review':
            raise ValueError('High impact infographic requires triple-source editorial process')
        if m.get('claim_status')!='verified' or m.get('disputed_claims') not in ([],None):
            raise ValueError('Unresolved disputed claim cannot appear in a public render')
        checks=m.get('review_checks',{})
        flags=('claims_checked','contradictions_checked','attribution_checked',
               'editorial_neutrality_checked','primary_source_checked')
        if not isinstance(checks,dict) or any(checks.get(key) is not True for key in flags):
            raise ValueError('High impact brief needs documented checks before rendering')
        if not isinstance(m.get('verification_log'),list) or len(m['verification_log'])<3:
            raise ValueError('High impact brief needs evidence excerpts from three sources')
    for key,minlen,maxlen in [('headline',22,100),('deck',55,210),('section',5,32)]:
        if not isinstance(m.get(key),str) or not minlen<=len(m[key].strip())<=maxlen:
            raise ValueError(key+' insufficient or too long for journalistic grid')
    bad=r'(?i)\b(elei[çc][ãa]o|fraude|candidatura|partido|presidente|homic[ií]dio|morte|assassin|guerra|crime|tratamento|c[âa]ncer|pandemia|acidente|trag[ée]dia|bomba|conflito armado)\b'
    if not high and re.search(bad,' '.join([m['headline'],m['deck']])):
        raise ValueError('Misclassified low-risk headline contains high impact terms')
    sources=m.get('sources')
    if not isinstance(sources,list) or len(sources)<(3 if high else 2):
        raise ValueError('High impact needs three source links; other stories need two')
    hosts=set()
    for s in sources:
        if not isinstance(s,str) or not s.startswith('https://'):raise ValueError('HTTPS original evidence links required')
        p=urlparse(s)
        if not p.hostname or p.hostname.endswith('.example.com') or p.username:raise ValueError('Invalid source URL')
        hosts.add(p.hostname)
    if len(hosts)<(3 if high else 2):
        raise ValueError('Require distinct source hosts for cross-check')
    if high and len({entry.get('source_url') for entry in m['verification_log']
                     if isinstance(entry,dict) and entry.get('source_url') in sources})<3:
        raise ValueError('Each high-impact source must have an evidence record')
    if not isinstance(m.get('source_label'),str) or len(m['source_label'])>44:raise ValueError('Source credit missing')
    require_real_photo(m)
    v=m.get('visual')
    if v is not None:
        if not isinstance(v,dict) or v.get('kind')!='metric_split':
            raise ValueError('Unknown infographic visual')
        total=v.get('total')
        entries=v.get('entries')
        if not isinstance(total,int) or not 1<=total<=9999 or not isinstance(entries,list) or len(entries)!=2:
            raise ValueError('Metric must be numeric with exactly two locations')
        if any(not isinstance(e,dict) or not isinstance(e.get('value'),int) or
               not 1<=e['value']<=total or not isinstance(e.get('name'),str) or
               not 3<=len(e['name'])<=18 for e in entries):
            raise ValueError('Invalid source-anchored metric entry')
        if sum(e['value'] for e in entries)!=total:
            raise ValueError('Graphic arithmetic must sum to its headline total')
        if not isinstance(v.get('note'),str) or not 24<=len(v['note'])<=105:
            raise ValueError('Graphic needs evidence-oriented qualification')
    for slide in m.get('slides',[]):
        if 'highlight' in slide and (not isinstance(slide['highlight'],str) or not 3<=len(slide['highlight'])<=28):
            raise ValueError('Highlight must be a concise fact')
    if m['kind']!='headline':
        slides=m.get('slides')
        if not isinstance(slides,list) or len(slides)!=3:raise ValueError('Carousel requires exactly three informative inner slides')
        for x in slides:
            if not isinstance(x,dict) or not isinstance(x.get('title'),str) or not 9<=len(x['title'])<=55:
                raise ValueError('Inner slide title must be concise and non-empty')
            if not isinstance(x.get('body'),str) or not 90<=len(x['body'])<=350:
                raise ValueError('Inner slide body needs sourced context, not placeholders')
            if not high and re.search(bad,x['title']+' '+x['body']):
                raise ValueError('Sensitive inner slide misclassified low risk')
    if not isinstance(m.get('caption'),str) or not 120<=len(m['caption'])<=2100:raise ValueError('Natural caption missing')
    return m


PHOTO_LICENSES={
    'CC BY 2.0':'https://creativecommons.org/licenses/by/2.0/',
    'CC BY 3.0':'https://creativecommons.org/licenses/by/3.0/',
    'CC BY 4.0':'https://creativecommons.org/licenses/by/4.0/',
    'CC BY-SA 3.0':'https://creativecommons.org/licenses/by-sa/3.0/',
    'CC BY-SA 4.0':'https://creativecommons.org/licenses/by-sa/4.0/',
    'CC0 1.0':'https://creativecommons.org/publicdomain/zero/1.0/',
}
def require_real_photo(story):
    """Mandatory, source-licensed documentary photograph on every published cover."""
    p=story.get('photo')
    if not isinstance(p,dict):raise ValueError('REAL_PHOTO_REQUIRED: every cover must include a documented photograph')
    for key in ('image_url','source_page','author','credit','license','license_url','description','context','context_note','date_taken'):
        if not isinstance(p.get(key),str) or not p[key].strip():
            raise ValueError('REAL_PHOTO_PROVENANCE_REQUIRED: '+key)
    image=urlparse(p['image_url'])
    source=urlparse(p['source_page'])
    if image.scheme!='https' or image.hostname!='upload.wikimedia.org' or not image.path.startswith('/wikipedia/commons/'):
        raise ValueError('PHOTO_ORIGIN_UNVERIFIED: use an actual Wikimedia Commons photo URL')
    if source.scheme!='https' or source.hostname!='commons.wikimedia.org' or not source.path.startswith('/wiki/File:'):
        raise ValueError('PHOTO_SOURCE_PAGE_REQUIRED: Wikimedia Commons file page is mandatory')
    if p['license'] not in PHOTO_LICENSES or p['license_url']!=PHOTO_LICENSES[p['license']]:
        raise ValueError('PHOTO_LICENSE_NOT_VERIFIED: source must have an explicitly supported reusable license')
    if p['context'] not in ('archive_illustrative','event_documentary'):
        raise ValueError('PHOTO_CONTEXT_REQUIRED: distinguish archive from event photographs')
    if p['context']=='archive_illustrative' and len(p['context_note'])<35:
        raise ValueError('PHOTO_ARCHIVE_MUST_NOT_MISLEAD: explain precisely what the file does not depict')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',p['date_taken']):
        raise ValueError('PHOTO_CAPTURE_DATE_REQUIRED')
    if len(p['credit'])>92 or len(p['description'])>220:
        raise ValueError('PHOTO_CREDIT_TOO_LONG')
    return p

def acquire_photo(story,out):
    """Cache one real source photograph; fail closed if fetch or image proof fails."""
    p=require_real_photo(story)
    out.mkdir(parents=True,exist_ok=True)
    image_file=out/(story['id']+'-source-photo.jpg')
    source_meta=out/(story['id']+'-source-photo-provenance.json')
    fingerprint=hashlib.sha256(json.dumps(p,sort_keys=True,ensure_ascii=False).encode('utf8')).hexdigest()
    if image_file.is_file() and source_meta.is_file():
        try:
            cached=json.loads(source_meta.read_text(encoding='utf8'))
            if cached.get('fingerprint')==fingerprint and cached.get('sha256')==hashlib.sha256(image_file.read_bytes()).hexdigest():
                with Image.open(image_file) as im:return im.convert('RGB').copy(),cached['sha256']
        except (ValueError,OSError,KeyError):pass
    req=Request(p['image_url'],headers={
        'User-Agent':'CadernaNewsroom/1.0 (https://github.com/pedrole1601-bit/caderna-media; photo licensing check)',
        'Accept':'image/jpeg,image/png,image/webp;q=0.8'})
    try:
        with urlopen(req,timeout=28) as response:
            content_type=response.headers.get('Content-Type','').split(';')[0].lower()
            if content_type not in ('image/jpeg','image/png','image/webp'):
                raise ValueError('PHOTO_INVALID_MIME: original source did not return a photograph')
            raw=response.read(12_000_001)
    except (HTTPError,URLError,TimeoutError) as exc:
        raise ValueError('PHOTO_DOWNLOAD_UNAVAILABLE: do not publish without a real image') from exc
    if not 30000<len(raw)<=12_000_000:raise ValueError('PHOTO_INVALID_DOWNLOAD_SIZE')
    try:
        with Image.open(io.BytesIO(raw)) as im:
            if im.format not in ('JPEG','PNG','WEBP'):raise ValueError('PHOTO_INVALID_FORMAT')
            im=ImageOps.exif_transpose(im).convert('RGB')
            if im.width<1000 or im.height<600:
                raise ValueError('PHOTO_LOW_RESOLUTION: minimum 1000x600')
            im.thumbnail((2400,1800),Image.Resampling.LANCZOS)
            im.save(image_file,'JPEG',quality=92,subsampling=0,optimize=True)
            result=im.copy()
    except (OSError,ValueError) as exc:raise ValueError('PHOTO_INVALID_IMAGE: '+str(exc)) from exc
    photo_sha=hashlib.sha256(image_file.read_bytes()).hexdigest()
    source_meta.write_text(json.dumps({
        'source_page':p['source_page'],'image_url':p['image_url'],'author':p['author'],
        'license':p['license'],'license_url':p['license_url'],'credit':p['credit'],
        'date_taken':p['date_taken'],'context':p['context'],'context_note':p['context_note'],
        'fingerprint':fingerprint,'sha256':photo_sha
    },ensure_ascii=False,indent=2),encoding='utf8')
    return result,photo_sha

def brand_header(im,issue,theme):
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,158),fill=INK)
    d.rectangle((0,0,W,8),fill=CORAL)
    logo=ROOT/'assets/logo-horizontal-inverse-v01.svg'
    if not logo.exists():raise ValueError('Canonical logo missing')
    raw=cairosvg.svg2png(url=str(logo),output_width=432,output_height=92)
    img=Image.open(io.BytesIO(raw)).convert('RGBA')
    im.paste(img,(63,33),img)
    d=ImageDraw.Draw(im)
    d.rectangle((828,51,834,115),fill=CORAL)
    d.text((857,58),'CADERNA / 2026',font=font('bold',22),fill=PAPER,anchor='lt')
    d.text((857,93),'EDIÇÃO '+issue,font=font('reg',18),fill='#D5DDE4',anchor='lt')

def textbox(d,xy,text,size,face,color,bounds,registry,label):
    f=font(face,size)
    bb=d.textbbox(xy,text,font=f,anchor='lt')
    a,b,c,e=bounds
    if not(a<=bb[0] and b<=bb[1] and bb[2]<=c and bb[3]<=e):raise ValueError(f'{label} beyond its grid {bb}/{bounds}')
    for name,p in registry:
        if min(bb[2],p[2])-max(bb[0],p[0])>3 and min(bb[3],p[3])-max(bb[1],p[1])>3:
            raise ValueError('Glyph collision between '+label+' and '+name)
    d.text(xy,text,font=f,fill=color,anchor='lt')
    registry.append((label,bb))
    return bb

def split_lines(d,text,size,maxwidth,face,maxlines):
    words=text.split()
    if not words:raise ValueError('Text empty')
    groups=[];line=''
    for w in words:
        candidate=(line+' '+w).strip()
        if d.textbbox((0,0),candidate,font=font(face,size),anchor='lt')[2]>maxwidth and line:
            groups.append(line);line=w
        else:line=candidate
    if line:groups.append(line)
    if len(groups)>maxlines:raise ValueError('Copy overflows '+str(maxlines)+' rows at '+str(size)+'px')
    return groups

def title_lines(d,title,width,slot_rows):
    # One font/size for the entire title. Reject if no comfortable fit.
    for size in (126,120,114,108,102,96):
        try: lines=split_lines(d,title.upper(),size,width,'display',2)
        except ValueError:continue
        if len(lines)==2:return size,lines
    # Three-line fallback intentionally uses a smaller uniform size and
    # a stable optical baseline. Never render a 126px third row into footer.
    for size in (84,78):
        try:lines=split_lines(d,title.upper(),size,width,'display',3)
        except ValueError:continue
        if len(lines)==3:return size,lines
    raise ValueError('Editorial headline failed: rewrite, do not squash individual lines')


def cover(story,idx,photo_image):
    # The photo is the lead element and occupies 56% of the 4:5 cover.
    theme=story['theme']
    panel=INK if theme=='cream' else PAPER
    ink=PAPER if theme=='cream' else INK
    muted='#CAD2D9' if theme=='cream' else MUTED
    im=Image.new('RGB',(W,H),panel)
    brand_header(im,story['id'][:10],theme)
    photo_bounds=(0,148,1080,900)
    photograph=ImageOps.fit(photo_image,(1080,752),method=Image.Resampling.LANCZOS,centering=(0.5,0.5))
    im.paste(photograph,(0,148))
    d=ImageDraw.Draw(im)
    d.rectangle((0,148,1080,158),fill=CORAL)
    d.rectangle((61,187,715,245),fill=INK)
    reg=[]
    textbox(d,(83,202),story['section'].upper(),27,'bold',PAPER,(78,190,690,244),reg,'section')
    p=story['photo']
    badge='FOTO REAL DE ARQUIVO · ILUSTRATIVA' if p['context']=='archive_illustrative' else 'FOTO DOCUMENTAL DO FATO'
    d.rectangle((61,842,1004,896),fill=INK)
    textbox(d,(84,855),badge,25,'bold',PAPER,(80,849,990,891),reg,'photo_context')
    d.rectangle((0,899,1080,907),fill=CORAL)
    size,lines=title_lines(d,story['headline'],905,3)
    # Keep a single type size and a baseline clear of the photographic panel.
    if len(lines)==2:
        start=969
        stride=size+34
    else:
        start=934
        stride=size+34
    boxes=[]
    for i,line in enumerate(lines):
        y=start+i*stride
        bb=textbox(d,(90,y),line,size,'display',ink,(88,925,1000,1248),reg,'headline_'+str(i))
        boxes.append(bb)
    for prev,nxt in zip(boxes,boxes[1:]):
        if nxt[1]-prev[3]<22:raise ValueError('Unacceptable photo-cover headline spacing')
    credit='FOTO: '+p['credit']+' · '+p['license']
    if len(credit)>92:raise ValueError('Photo credit does not fit cover')
    textbox(d,(90,1264),credit,18,'reg',muted,(87,1258,1000,1294),reg,'photo_credit')
    d.rectangle((90,1302,990,1305),fill=CORAL)
    textbox(d,(90,1315),'FONTES: '+story['source_label'].upper()[:40],17,'bold',muted,(88,1307,778,1340),reg,'source')
    textbox(d,(850,1315),'CADERNA',18,'bold',ink,(844,1307,999,1340),reg,'footer')
    return im,{'headline_size':size,'headline_lines':lines,
        'boxes':[(label,list(bb)) for label,bb in reg],
        'theme':theme,'slide_index':0,'photograph_bounds':list(photo_bounds),
        'photograph_fraction':752/1350,'photograph_context':p['context']}

def inside(story,idx):
    info=story['slides'][idx-1]
    theme=story['theme']
    im=Image.new('RGB',(W,H),PAPER if theme=='ink' else INK)
    d=ImageDraw.Draw(im)
    brand_header(im,story['id'][:10],theme)
    d=ImageDraw.Draw(im)
    fg=INK if theme=='ink' else PAPER
    reg=[]
    d.rectangle((86,202,92,267),fill=CORAL)
    textbox(d,(109,214),f'{idx+1:02d} / 04   •   '+story['section'].upper(),25,'bold',fg,(105,207,990,263),reg,'section')
    d.rectangle((87,329,330,336),fill=CORAL)
    for size in (97,91,85,79):
        try:tl=split_lines(d,info['title'].upper(),size,900,'display',2);break
        except ValueError:continue
    else:raise ValueError('Slide title too long for editorial grid')
    previous=None
    for li,line in enumerate(tl):
        bb=textbox(d,(89,382+li*(size+42)),line,size,'display',fg,(87,377,990,642),reg,'subheadline_'+str(li))
        if previous and bb[1]-previous[3]<22:raise ValueError('Inner headline gap below limit')
        previous=bb
    d.rectangle((90,665,988,668),fill=CORAL)
    for size in (43,40,37,34):
        try:lines=split_lines(d,info['body'],size,885,'reg',7);break
        except ValueError:continue
    else:raise ValueError('Slide content too dense; edit copy, never squeeze')
    current=711
    for li,line in enumerate(lines):
        textbox(d,(90,current),line,size,'reg',fg,(88,700,991,1176),reg,'body_'+str(li))
        current+=size+23
    if current>1185:raise ValueError('Too much body copy')
    if info.get('highlight'):
        if current>1075:raise ValueError('Highlight requires sufficient negative space')
        d.rectangle((90,1106,990,1197),outline=CORAL,width=3)
        d.rectangle((90,1106,102,1197),fill=CORAL)
        textbox(d,(124,1126),info['highlight'].upper(),39,'bold',fg,(120,1117,969,1181),reg,'highlight')
    d.rectangle((90,1234,990,1238),fill=CORAL)
    textbox(d,(90,1264),'FONTE: '+story['source_label'].upper()[:40],20,'bold',fg,(88,1257,810,1305),reg,'source')
    textbox(d,(888,1264),f'{idx+1}/4',23,'bold',fg,(885,1258,990,1310),reg,'pagination')
    return im,{"body_size":size,"inner_heading_size":tl and size,"boxes":[(label,list(bb)) for label,bb in reg],"theme":theme,"slide_index":idx}

def render(story,out):
    assert_story(story)
    out.mkdir(parents=True,exist_ok=True)
    photo_image,photo_sha=acquire_photo(story,out)
    count=4 if story['kind']!='headline' else 1
    qa=[]
    sha256_jpegs={}
    for i in range(count):
        image,check=(cover(story,i,photo_image) if i==0 else inside(story,i))
        stem=f"{story['id']}-{i+1:02d}"
        image.save(out/(stem+'.jpg'),format='JPEG',quality=94,subsampling=0,optimize=True)
        sha256_jpegs[stem+'.jpg']=hashlib.sha256((out/(stem+'.jpg')).read_bytes()).hexdigest()
        image.save(out/(stem+'.png'),format='PNG',optimize=True)
        image.resize((320,400),Image.Resampling.LANCZOS).save(out/(stem+'-mobile.png'),format='PNG')
        with Image.open(out/(stem+'.jpg')) as v:
            if v.mode!='RGB' or v.size!=(W,H):raise ValueError('Invalid JPEG output')
        qa.append(check)
    return {'status':'PASS_TECHNICAL_ONLY','slug':story['id'],'kind':story['kind'],
            'theme':story['theme'],'jpeg_count':count,'qa':qa,
            'editorial_approval':False,'published_to_instagram':False,
            'source_links':story['sources'],'risk':story['risk'],
            'sha256_jpegs':sha256_jpegs,
            'photograph':{'source_photo_file':story['id']+'-source-photo.jpg',
              'sha256':photo_sha,'image_url':story['photo']['image_url'],
              'source_page':story['photo']['source_page'],
              'license':story['photo']['license'],'author':story['photo']['author'],
              'context':story['photo']['context'],'photo_fraction':752/1350}}
def main():
    if len(sys.argv)!=2:raise SystemExit('Usage: render_editorial.py incoming/<slug>.json')
    path=Path(sys.argv[1])
    if path.parent!=Path('incoming') or not re.fullmatch(r'\d{4}-\d{2}-\d{2}-[a-z0-9-]{7,64}\.json',path.name):
        raise ValueError('Only incoming/dated-slug.json is accepted')
    story=json.loads(path.read_text(encoding='utf8'))
    if path.stem!=story['id']:raise ValueError('Story ID must equal file name')
    output=ROOT/'media'/'auto'
    result=render(story,output)
    (output/(story['id']+'-qa.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'result':'QA_TECH_PASS','slug':result['slug'],'count':result['jpeg_count']},ensure_ascii=False))
if __name__=='__main__':main()
