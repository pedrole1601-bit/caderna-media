#!/usr/bin/env python3
"""CADERNA v0.7 — edição 001. Design auditável e sem postagem no Instagram.
Foco editorial: um só bloco de manchete, alinhamento óptico e teste mobile.
Aprovado tecnicamente != aprovado pelo editor.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import io,cairosvg,os,json
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.getenv('CADERNA_OUTPUT_DIR',str(ROOT/'media')))
W,H=1080,1350
INK='#101C2E'; PAPER='#F5F3ED'; CORAL='#EA674D'
MUTED='#667487'; SOFT='#D5DDE4'
FONT={
  'display':'/usr/share/fonts/truetype/noto/NotoSansDisplay-ExtraCondensedBlack.ttf',
  'serif':'/usr/share/fonts/truetype/noto/NotoSerifDisplay-CondensedBlackItalic.ttf',
  'bold':'/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf',
  'heavy':'/usr/share/fonts/opentype/inter/InterDisplay-Black.otf',
  'reg':'/usr/share/fonts/opentype/inter/InterDisplay-Regular.otf'
}
for name,path in FONT.items():
    if not Path(path).exists(): raise RuntimeError('Missing free font '+name)
def font(f,s):return ImageFont.truetype(FONT[f],s)
im=Image.new('RGB',(W,H),INK)
d=ImageDraw.Draw(im)
blocks=[]
def put(label,x,y,message,size,face,color,rect):
    if not message:raise ValueError('Empty text: '+label)
    f=font(face,size)
    bb=d.textbbox((x,y),message,font=f,anchor='lt')
    x0,y0,x1,y1=rect
    if not (bb[0]>=x0-2 and bb[1]>=y0-2 and bb[2]<=x1+2 and bb[3]<=y1+2):
        raise ValueError('BLOCK OUT OF SAFE GRID '+label+' '+str(bb))
    for other in blocks:
        a=other['bbox']
        if min(bb[2],a[2])-max(bb[0],a[0])>3 and min(bb[3],a[3])-max(bb[1],a[1])>3:
            raise ValueError('TEXT COLLISION: '+label+' and '+other['label'])
    d.text((x,y),message,font=f,fill=color,anchor='lt')
    blocks.append(dict(label=label,text=message,bbox=bb,size=size,font=face,anchor_x=x,anchor_y=y))
    return bb

# Brand header: uses OFFICIAL CADERNA SVG; never redraws logo as lookalike.
d.rectangle((0,0,W,155),fill=INK)
d.rectangle((0,0,W,9),fill=CORAL)
svg=ROOT/'assets/logo-horizontal-inverse-v01.svg'
if not svg.is_file():raise RuntimeError('Canonical CADERNA logo missing')
logo=Image.open(io.BytesIO(cairosvg.svg2png(url=str(svg),output_width=444,output_height=94))).convert('RGBA')
im.paste(logo,(63,30),logo)
d=ImageDraw.Draw(im)
d.rectangle((817,48,822,110),fill=CORAL)
put('issue',849,53,'EDIÇÃO / 001',23,'bold',PAPER,(844,49,1030,80))
put('edition_date',852,91,'03 NOV 2026',18,'reg',SOFT,(846,87,1030,112))

# Hero: one meaningful date + illustration, without gratuitous grid marks.
d.rectangle((0,155,1080,815),fill=INK)
d.rectangle((66,212,73,250),fill=CORAL)
put('section',85,215,'BRASIL   /   EDUCAÇÃO',25,'bold',SOFT,(80,203,505,247))
put('day',74,283,'08',268,'serif',PAPER,(67,275,550,574))
d.rectangle((82,612,340,617),fill=CORAL)
put('month',80,636,'NOV',77,'display',CORAL,(75,631,320,721))
put('weekday',84,740,'DOMINGO',25,'bold',SOFT,(80,735,470,774))
paper=Image.new('RGBA',(428,548),(0,0,0,0))
p=ImageDraw.Draw(paper)
p.rounded_rectangle((38,37,406,526),radius=18,fill=(0,0,0,60))
p.rounded_rectangle((20,19,388,510),radius=18,fill=PAPER)
p.rectangle((58,58,335,63),fill=INK)
p.text((57,78),'CADERNO DE ESTUDO',font=font('heavy',24),fill=INK)
p.text((58,120),'ILUSTRAÇÃO EDITORIAL',font=font('bold',15),fill=MUTED)
p.line((56,154,336,154),fill='#AFB9C2',width=2)
for row in range(6):
    yy=199+row*47
    p.text((59,yy-11),f'{row+1:02d}',font=font('bold',19),fill=MUTED)
    for k in range(4):
        cx=145+k*55;r=10;selected=(row,k) in ((1,2),(4,1))
        p.ellipse((cx-r,yy-r,cx+r,yy+r),outline=CORAL if selected else '#8EA0AF',width=3)
        if selected:p.ellipse((cx-4,yy-4,cx+4,yy+4),fill=CORAL)
p.rectangle((58,469,334,471),fill='#C9D2DA')
rot=paper.rotate(9,Image.Resampling.BICUBIC,expand=True)
im.paste(rot,(542,214),rot)
d=ImageDraw.Draw(im)

# Primary headline: one type size, one column, two fixed baselines.
d.rectangle((0,815,W,H),fill=PAPER)
d.rectangle((78,847,300,893),fill=CORAL)
put('kicker',98,855,'ENEM  /  2026',24,'bold',INK,(95,849,292,886))
x=94
h1=put('headline_line_1',x,935,'ENEM COMEÇA',126,'display',INK,(92,925,1010,1070))
h2=put('headline_line_2',x,1096,'NESTE DOMINGO',126,'display',INK,(92,1077,1012,1230))
d.rectangle((94,1244,1006,1248),fill=CORAL)
put('dek',94,1260,'LOCAL DE PROVA JÁ DISPONÍVEL NO CARTÃO DE CONFIRMAÇÃO',23,'bold',INK,(80,1256,1008,1300))
put('source',94,1310,'FONTE: INEP  •  03.11.2026',17,'bold',MUTED,(80,1303,700,1338))
put('date_range',791,1310,'8 E 15 NOV',19,'bold',INK,(785,1304,1004,1338))

# Strict visual coherence gates; these catch the exact prior failing composition.
headline=[b for b in blocks if b['label'].startswith('headline_line_')]
assert len(headline)==2, 'Headlines require exactly 2 balanced lines'
assert len({b['font'] for b in headline})==1, 'One headline font only'
assert len({b['size'] for b in headline})==1, 'No arbitrary font-size per row'
assert max(b['anchor_x'] for b in headline)-min(b['anchor_x'] for b in headline)<=3, 'Anchor misalignment'
assert min(b['bbox'][0] for b in headline)>=84, 'Headline invades left margin'
assert max(b['bbox'][2] for b in headline)<=1012, 'Headline invades right margin'
assert h2[1]-h1[3]>=36, 'Headline line gap under 36px'
assert min(b['size'] for b in headline)*320/W>=37, 'Illegible mobile headline'
assert all(b['bbox'][2]<=1030 for b in blocks), 'Text overruns artboard'
assert h1[3]<h2[1], 'Headline collision'

OUT.mkdir(parents=True,exist_ok=True)
name='caderna-enem-2026-001-v2'
im.save(OUT/(name+'.png'),format='PNG',optimize=True)
im.save(OUT/(name+'.jpg'),format='JPEG',quality=94,subsampling=0,optimize=True)
im.resize((320,400),Image.Resampling.LANCZOS).save(OUT/(name+'-mobile.png'),format='PNG')
qa={'schema':'caderna.design.qa.v07','canvas':[W,H],
    'render_status':'TECHNICAL_PASS_EDITOR_APPROVAL_PENDING','name':name,
    'headline_x':[b['anchor_x'] for b in headline],
    'headline_font_sizes':[b['size'] for b in headline],
    'headline_gap':h2[1]-h1[3],
    'illustration_not_photograph':True,'logo':'assets/logo-horizontal-inverse-v01.svg',
    'human_approved':False,'published_to_instagram':False,'text_blocks':blocks}
(OUT/(name+'-qa.json')).write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
print('PASS: strict grid, typography, brand logo, 1080x1350, JPEG/PNG, mobile QA')
