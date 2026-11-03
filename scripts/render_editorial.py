#!/usr/bin/env python3
"""CADERNA: source-anchored editorial art renderer. Free Pillow/CairoSVG.
Run: python scripts/render_editorial.py incoming/<slug>.json
Only renders supplied editorial copy. Never invents facts or touches Meta.
"""
from __future__ import annotations
import io,json,re,sys,os,textwrap,datetime,hashlib
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image,ImageDraw,ImageFont
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

def cover(story,idx):
    theme=story['theme']
    im=Image.new('RGB',(W,H),INK)
    d=ImageDraw.Draw(im)
    brand_header(im,story['id'][:10],theme)
    d=ImageDraw.Draw(im)
    hero=INK if theme=='ink' else PAPER
    contrast=PAPER if theme=='ink' else INK
    d.rectangle((0,158,W,795),fill=hero)
    d.rectangle((68,221,74,263),fill=CORAL)
    reg=[]
    textbox(d,(90,222),story['section'].upper(),26,'bold',contrast,(88,210,900,265),reg,'section')
    v=story.get('visual')
    if v and v.get('kind')=='metric_split':
        # A real metric is the hero. No decorative 'C' or fictitious chart values.
        total=str(v['total'])
        textbox(d,(87,315),total,270,'serif',contrast,(80,305,605,610),reg,'hero_metric_total')
        textbox(d,(94,604),'VAGAS / 2027',31,'bold',contrast,(90,590,530,658),reg,'hero_metric_label')
        d.rectangle((624,292,628,585),fill=CORAL)
        for i,item in enumerate(v['entries']):
            row_y=315+i*154
            textbox(d,(652,row_y),item['name'].upper(),24,'bold',contrast,(646,row_y-3,998,row_y+38),reg,'metric_label_'+str(i))
            textbox(d,(655,row_y+37),str(item['value']),66,'display',contrast,(650,row_y+30,840,row_y+115),reg,'metric_value_'+str(i))
            bar_w=round(325*item['value']/v['total'])
            d.rectangle((650,row_y+114,650+bar_w,row_y+128),fill=CORAL if i==0 else BLUE)
            d.rectangle((650+bar_w,row_y+114,975,row_y+128),fill='#C7CFD7' if theme=='cream' else '#40516A')
        d.rectangle((84,686,992,690),fill=CORAL)
        textbox(d,(90,722),v['note'],20,'bold',contrast,(85,710,999,778),reg,'metric_qualification')
    else:
        # Generic motif only for stories without a verified focal number.
        d.ellipse((581,218,1060,695),outline=BLUE if theme=='ink' else '#C8D5E9',width=23)
        d.arc((632,267,1014,651),30,290,fill=CORAL,width=15)
        d.line((674,284,939,551),fill=BLUE if theme=='ink' else INK,width=14)
        d.ellipse((869,475,919,525),fill=CORAL)
        textbox(d,(79,320),'C',286,'serif',contrast,(70,306,550,641),reg,'editorial_motif')
        d.rectangle((85,702,982,707),fill=CORAL)
        textbox(d,(88,726),'INFORMAÇÃO  /  CONTEXTO',25,'bold',contrast,(85,718,720,778),reg,'hero_subtitle')
    panel=INK if theme=='cream' else PAPER
    ink=PAPER if theme=='cream' else INK
    muted='#CAD2D9' if theme=='cream' else MUTED
    d.rectangle((0,795,W,H),fill=panel)
    d.rectangle((83,819,308,866),fill=CORAL)
    textbox(d,(100,829),'CADERNA  /  '+('FATO' if story['kind']=='headline' else 'EXPLICA'),20,'bold',INK,(97,824,307,854),reg,'kicker')
    size,lines=title_lines(d,story['headline'],910,3)
    # top-aligned single column, fixed line gap and unified font size.
    stride=size+54
    if len(lines)==2:start=900
    else:start=861
    boxes=[]
    for i,line in enumerate(lines):
        y=start+i*stride
        bb=textbox(d,(90,y),line,size,'display',ink,(88,871,1000,1227),reg,'headline_'+str(i))
        boxes.append(bb)
    for prev,nxt in zip(boxes,boxes[1:]):
        if nxt[1]-prev[3]<20:raise ValueError('Unacceptable headline interline spacing')
    if len({x for x in [size]*len(lines)})!=1:raise ValueError('Inconsistent headline sizes')
    if len(lines)==2:
        deck=story['deck']
        d.rectangle((90,1217,988,1221),fill=CORAL)
        deck_lines=split_lines(d,deck,22,900,'bold',2)
        for i,line in enumerate(deck_lines):
            textbox(d,(90,1234+i*28),line,22,'bold',ink,(88,1230,995,1298),reg,'deck_'+str(i))
    else:
        d.rectangle((90,1265,988,1269),fill=CORAL)
    textbox(d,(90,1310),'FONTE: '+story['source_label'].upper()[:40],17,'bold',muted,(88,1305,760,1340),reg,'source')
    textbox(d,(840,1310),'CADERNA',18,'bold',ink,(835,1307,999,1340),reg,'footer')
    return im,{"headline_size":size,"headline_lines":lines,"boxes":[(label,list(bb)) for label,bb in reg],"theme":theme,"slide_index":0}

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
    count=4 if story['kind']!='headline' else 1
    qa=[]
    sha256_jpegs={}
    for i in range(count):
        image,check=(cover(story,i) if i==0 else inside(story,i))
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
            'sha256_jpegs':sha256_jpegs}
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
