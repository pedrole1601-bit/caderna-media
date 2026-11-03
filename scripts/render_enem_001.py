#!/usr/bin/env python3
"""CADERNA edição 001 — arte editorial original para o Enem 2026.

Fonte factual: Inep 27–29/10/2026. Sem fotografia de terceiro e SEM publicação no Instagram.
Reprodução: CADERNA_OUTPUT_DIR=media python scripts/render_enem_001.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os, json
W,H=1080,1350
INK='#101C2E'; PAPER='#F5F3ED'; CORAL='#EA674D'; BLUE='#3356EA'
MUTED='#9CAABB'; PALEBLUE='#DFE8F5'
base=Image.new('RGB',(W,H),PAPER)
d=ImageDraw.Draw(base)
fontdir=Path('/usr/share/fonts')
candidates={
 'cond':['truetype/noto/NotoSansDisplay-ExtraCondensedBlack.ttf','truetype/noto/NotoSansDisplay-CondensedBlack.ttf','truetype/dejavu/DejaVuSansCondensed-Bold.ttf'],
 'heavy':['opentype/inter/InterDisplay-Black.otf','opentype/inter/InterDisplay-Bold.otf','truetype/lato/Lato-Heavy.ttf'],
 'regular':['opentype/inter/InterDisplay-Regular.otf','truetype/lato/Lato-Regular.ttf'],
 'bold':['opentype/inter/InterDisplay-Bold.otf','truetype/lato/Lato-Bold.ttf'],
 'serif':['truetype/noto/NotoSerifDisplay-CondensedBlackItalic.ttf','truetype/noto/NotoSerif-CondensedBlackItalic.ttf','truetype/dejavu/DejaVuSerifCondensed-BoldItalic.ttf']
}
fontpaths={k:next((fontdir/f for f in names if (fontdir/f).exists()),None) for k,names in candidates.items()}
if any(f is None for f in fontpaths.values()):raise RuntimeError('Missing free fonts: '+str(fontpaths))
def font(size,face='regular'):return ImageFont.truetype(str(fontpaths[face]),size)
boxes=[]
def text(x,y,msg,size,fill,face='regular',maxright=1008,limitbottom=1340):
    f=font(size,face)
    bb=d.textbbox((x,y),msg,font=f,anchor='lt')
    if bb[0]<0 or bb[2]>maxright or bb[3]>limitbottom:
        raise ValueError(f'TEXT GRID FAIL {msg!r}: {bb}')
    for other,prev in boxes:
        if min(bb[2],prev[2])-max(bb[0],prev[0])>3 and min(bb[3],prev[3])-max(bb[1],prev[1])>3:
            raise ValueError(f'TEXT OVERLAP: {msg!r} & {other!r}')
    boxes.append((msg,bb))
    d.text((x,y),msg,font=f,fill=fill,anchor='lt')
    return bb

def fit(x,y,s,preferred,minimum,fill,face='cond',right=1008,bottom=1340):
    for size in range(preferred,minimum-1,-1):
        if d.textbbox((x,y),s,font=font(size,face),anchor='lt')[2]<=right:
            return text(x,y,s,size,fill,face,maxright=right,limitbottom=bottom)
    raise ValueError('Headline does not fit: '+s)

# Cabeçalho: assinatura CADERNA v0.4, azul profundo e coral.
d.rectangle((0,0,1080,165),fill=INK)
d.rectangle((0,0,1080,9),fill=CORAL)
d.rounded_rectangle((59,31,159,131),radius=22,fill=PAPER)
d.line((126,51,98,51,85,63,85,94,98,108,126,108),fill=INK,width=11,joint='curve')
for y,end in [(69,135),(81,128),(94,135)]:d.line((101,y,end,y),fill=INK,width=7)
d.rounded_rectangle((137,78,144,94),radius=2,fill=CORAL)
text(183,44,'CADERNA',63,PAPER,'heavy',maxright=733)
text(188,111,'J O R N A L   D I G I T A L',13,PALEBLUE,'bold',maxright=764)
d.rectangle((826,46,831,119),fill=CORAL)
text(849,51,'EDIÇÃO / 001',24,PAPER,'bold')
text(853,91,'03 NOV 2026',21,MUTED,'regular')

# Campo editorial original, sem fingir fotografia documental.
d.rectangle((0,165,1080,777),fill=INK)
for yy in range(198,760,70):d.line((28,yy,1050,yy),fill='#1C2C40',width=2)
for xx in range(70,1070,95):d.line((xx,179,xx,755),fill='#1A293D',width=1)
d.ellipse((585,174,1170,752),fill='#223A68')
d.ellipse((696,256,1155,716),fill=BLUE)
d.rectangle((64,208,70,255),fill=CORAL)
text(86,213,'BRASIL  /  EDUCAÇÃO',25,PAPER,'bold',maxright=600)
fit(63,292,'08',337,275,PAPER,'serif',right=606,bottom=630)
d.rectangle((74,637,526,641),fill=CORAL)
text(76,658,'NOVEMBRO',69,CORAL,'cond',maxright=547)
text(77,722,'DOMINGO',26,PALEBLUE,'bold',maxright=580)

# Elemento gráfico: caderno de respostas ilustrativo, chamado SIMULADO.
pad=Image.new('RGBA',(440,590),(0,0,0,0))
p=ImageDraw.Draw(pad)
p.rounded_rectangle((27,33,414,562),radius=27,fill=(0,0,0,35))
p.rounded_rectangle((13,12,401,546),radius=20,fill=PAPER)
p.rectangle((53,57,337,65),fill=INK)
p.text((53,84),'SIMULADO',font=font(42,'heavy'),fill=INK)
p.text((53,138),'CADERNO DE RESPOSTAS',font=font(15,'bold'),fill='#637082')
p.line((53,167,349,167),fill='#BEC6CD',width=3)
for row in range(7):
    yy=210+row*42
    p.text((53,yy-10),f'{row+1:02d}',font=font(19,'bold'),fill='#677485')
    for k in range(4):
        cx=141+k*56; r=9
        selected=(row==1 and k==2) or (row==4 and k==0)
        p.ellipse((cx-r,yy-r,cx+r,yy+r),outline=CORAL if selected else '#92A0AC',width=3)
        if selected:p.ellipse((cx-4,yy-4,cx+4,yy+4),fill=CORAL)
p.rectangle((52,508,349,512),fill='#D7DFE4')
rot=pad.rotate(10,Image.Resampling.BICUBIC,expand=True)
base.paste(rot,(547,191),rot)
d=ImageDraw.Draw(base)
d.ellipse((992,666,1018,692),fill=CORAL)
for i,top in enumerate((730,715,701)):d.rectangle((960+i*15,top,967+i*15,757),fill=BLUE)

# Título: três linhas auditadas por caixas reais.
d.rectangle((0,777,1080,1350),fill=PAPER)
d.rectangle((64,750,303,811),fill=CORAL)
text(85,769,'ENEM  /  2026',29,INK,'bold',maxright=293)
fit(73,831,'PRIMEIRA PROVA',138,98,INK,'cond',right=1010,bottom=973)
fit(73,961,'É NESTE',169,120,INK,'cond',right=1010,bottom=1124)
fit(73,1128,'DOMINGO',138,123,INK,'cond',right=1010,bottom=1238)
d.rectangle((55,838,62,1203),fill=CORAL)
d.rectangle((55,838,85,845),fill=CORAL)
d.rectangle((64,1243,1016,1247),fill=CORAL)
text(68,1258,'LOCAL DE PROVA DISPONÍVEL NO CARTÃO DE CONFIRMAÇÃO',23,INK,'bold',maxright=1017,limitbottom=1292)
text(68,1304,'FONTE: INEP  •  03.11.2026',17,'#657386','bold',maxright=580)
text(727,1303,'8 E 15 NOVEMBRO',19,INK,'bold',maxright=1018)
assert len(boxes)>=12

output=Path(os.getenv('CADERNA_OUTPUT_DIR','media'))
output.mkdir(parents=True,exist_ok=True)
base.save(output/'caderna-enem-2026-001.png',format='PNG',optimize=True)
base.save(output/'caderna-enem-2026-001.jpg',format='JPEG',quality=94,subsampling=0,optimize=True)
base.resize((320,400),Image.Resampling.LANCZOS).save(output/'caderna-enem-2026-001-mobile.png')
(output/'caderna-enem-2026-001-qa.json').write_text(
    json.dumps({'size':[1080,1350],'text_blocks':len(boxes),'no_text_overlap':True,
                'subject':'ENEM 2026','photo_used':False,'published_to_instagram':False},
                ensure_ascii=False,indent=2),encoding='utf8')
print('QA PASS | 1080x1350 | '+str(len(boxes))+' boxes | exported JPG/PNG | NO Instagram publication')
