#!/usr/bin/env python3
"""CADERNA visual-QA contract v0.7. Deterministic checks, not a taste oracle."""
from pathlib import Path
from PIL import Image
import json,sys
W,H=1080,1350

class VisualGateError(Exception): pass

def require(condition,message):
    if not condition:raise VisualGateError(message)

def validate(qa,media_dir):
    require(qa.get('schema')=='caderna.design.qa.v07','wrong QA schema')
    require(qa.get('canvas')==[W,H],'wrong aspect ratio')
    require(qa.get('human_approved') is False,'machine cannot approve editor')
    require(qa.get('published_to_instagram') is False,'art-only job cannot publish')
    require(qa.get('logo')=='assets/logo-horizontal-inverse-v01.svg','logo must be canonical')
    blocks=qa.get('text_blocks',[])
    require(isinstance(blocks,list) and len(blocks)>=9,'text content insufficient')
    require(len({x['label'] for x in blocks})==len(blocks),'duplicate text ID')
    headline=[x for x in blocks if x['label'].startswith('headline_line_')]
    require(len(headline)==2,'exactly two primary headline lines')
    require({x['font'] for x in headline}=={'display'},'headline must use one font family')
    require(len({x['size'] for x in headline})==1,'headline lines have conflicting size hierarchy')
    require(headline[0]['size']>=110,'headline size too small')
    require(max(x['anchor_x'] for x in headline)-min(x['anchor_x'] for x in headline)<=3,
            'headline left alignment not consistent')
    for x in headline:
        left,top,right,bottom=x['bbox']
        require(left>=88 and right<=1012 and top>=920 and bottom<=1230,'headline exceeds bounded safe column')
        require(x['size']*320/W>=34,'headline unreadable at 320 mobile')
    headline.sort(key=lambda x:x['bbox'][1])
    require(headline[1]['bbox'][1]-headline[0]['bbox'][3]>=36,
            'headline vertical rhythm is too tight')
    for i,b in enumerate(blocks):
        x0,y0,x1,y1=b['bbox']
        require(0<=x0<x1<=W and 0<=y0<y1<=H,'text outside canvas: '+b['label'])
        for other in blocks[i+1:]:
            a=other['bbox']
            require(min(x1,a[2])-max(x0,a[0])<=3 or min(y1,a[3])-max(y0,a[1])<=3,
                'text overlap: '+b['label']+' and '+other['label'])
    root=Path(media_dir);stem=qa.get('name')
    require(isinstance(stem,str) and stem.endswith('-v2'),'must version revised output')
    for suffix,format_,size in (('.jpg','JPEG',(W,H)),('.png','PNG',(W,H)),('-mobile.png','PNG',(320,400))):
        path=root/(stem+suffix)
        require(path.exists(),'missing export '+path.name)
        with Image.open(path) as im:
            require(im.format==format_ and im.size==size,'wrong export format/dimensions: '+path.name)
            if suffix=='.jpg':require(im.mode=='RGB' and path.stat().st_size<8_000_000,'Meta incompatible JPEG')
    with Image.open(root/(stem+'.png')) as im:
        require(im.getpixel((5,5))==(234,103,77),'brand top stripe changed')
        require(im.getpixel((5,180))==(16,28,46),'hero color changed')
        require(im.getpixel((5,830))==(245,243,237),'editorial paper changed')
    return {'result':'PASS_TECHNICAL_ONLY','headlines':2,'headline_gap':headline[1]['bbox'][1]-headline[0]['bbox'][3],
            'mobile_preview':True,'editor_approval':False}

if __name__=='__main__':
    base=Path(__file__).resolve().parents[1]/'media'
    meta=json.loads((base/'caderna-enem-2026-001-v2-qa.json').read_text(encoding='utf8'))
    try:print(json.dumps(validate(meta,base),ensure_ascii=False))
    except VisualGateError as e:print('BLOCKED: '+str(e),file=sys.stderr);sys.exit(1)
