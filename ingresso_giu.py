"""Ingresso inferiore dalle foto; porta del salotto in legno."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as E,uuid
path=Path(__file__).with_name('Planimetria_due_livelli.sh3d')
with zipfile.ZipFile(path) as z:assets={n:z.read(n) for n in z.namelist()}
r=E.fromstring(assets['Home.xml'])
room=next(n for n in r.findall('room') if n.get('name')=='Ingresso')
door=next(n for n in r.findall('doorOrWindow') if n.get('id')=='o0')
for g in list(r.findall('furnitureGroup')):
    if g.get('name','').startswith('Ingresso giu /'):r.remove(g)
protected=[n for n in r if n not in (room,door)]
before=[E.tostring(n) for n in protected]
door.set('name','Porta in legno del salotto');door.set('model','wooden-door/door.obj');door.set('color','008B5B32')
idx=next(i for i,n in enumerate(r) if n.tag=='wall')
def group(name):
    global idx
    g=E.Element('furnitureGroup',id='ingresso-giu-'+str(uuid.uuid4()),level='L1',name='Ingresso giu / '+name,movable='true')
    r.insert(idx,g);idx+=1;return g
def box(g,name,x,y,w,d,h,z=0,color='006C4933',model='built-in-cabinet/cube.obj'):
    return E.SubElement(g,'pieceOfFurniture',dict(id='ingresso-giu-'+str(uuid.uuid4()),level='L1',name=name,model=model,x=str(x),y=str(y),width=str(w),depth=str(d),height=str(h),elevation=str(z),color=color,movable='true'))
wood='006C4933';white='00E7E3D9';black='00262929'
desk=group('mobile in legno sotto scala e lampada')
box(desk,'Mobile antico',668,232,54,130,80)
box(desk,'Piano mobile',668,232,60,138,4,80)
for y in (201,263):
    box(desk,'Anta frontale',696,y,2,60,61,9)
    box(desk,'Pomello',698,y,3,3,3,48,'00978256')
box(desk,'Cassetto',696,232,2,123,13,68)
box(desk,'Base lampada',669,269,17,17,4,84)
box(desk,'Stelo lampada',669,269,6,6,20,88)
box(desk,'Paralume beige',669,269,27,27,26,108,'00BDB6A6')
box(desk,'Portapenne',679,188,10,10,13,84,black)
box(desk,'Carte sul piano',678,216,26,32,1,84,white)
seats=group('due sedie in legno con seduta verde')
def chair(x,y):
    box(seats,'Seduta verde',x,y,42,42,6,42,'00616D4F')
    for xx in (x-17,x+17):
        for yy in (y-17,y+17):box(seats,'Gamba sedia',xx,yy,4,4,42,0,'00B39467')
    for yy in (y-17,y+17):box(seats,'Montante schienale',x-19,yy,4,4,42,46,'00B39467')
    box(seats,'Schienale in legno',x-19,y,4,43,17,73,'00B39467')
chair(721,135);chair(727,272)
mirror=group('specchio con cornice sotto scala')
box(mirror,'Cornice specchio',640,192,4,52,69,133)
box(mirror,'Specchio',643,192,1,43,60,137,'00AFC5C7')
cab=group('scarpiera alta nel corridoio')
box(cab,'Scarpiera in legno scuro',1150,488,75,30,146,0,'00483529')
for z in (8,44,80,116):
    box(cab,'Frontale scarpiera',1150,472,70,2,33,z,'00483529')
    box(cab,'Maniglia',1150,470,14,2,2,z+24,black)
box(cab,'Casco nero sulla scarpiera',1150,488,31,28,27,146,black,'salotto/cylinder.obj')
coat=group('appendiabiti in legno e giacche')
box(coat,'Pannello appendiabiti',1270,500,63,4,162,25)
box(coat,'Mensola cappelli',1270,486,69,29,4,180)
for x in (1249,1270,1291):
    box(coat,'Gancio',x,494,2,8,6,164,black)
    box(coat,'Giacca appesa',x,483,19,13,95,67,'00463C32' if x==1270 else '002C3031')
access=group('citofono, radiatore e quadri')
box(access,'Citofono bianco',1074,497,21,9,28,155,white)
box(access,'Cornetta',1067,491,5,6,24,157,white)
box(access,'Display citofono',1078,491,7,1,5,174,black)
box(access,'Centralina a parete',1100,497,12,9,18,164,white)
for x in range(991,1028,6):box(access,'Elemento radiatore',x,494,5,11,63,12,white)
box(access,'Valvola radiatore',1030,488,6,6,5,68,'00B5B0A2')
box(access,'Vaso in terracotta',1058,480,29,29,35,0,'00A27650','salotto/cylinder.obj')
def picture(x,y,w,h,z,side=False):
    box(access,'Cornice quadro',x,y,3 if side else w,w if side else 3,h,z,wood)
    box(access,'Stampa decorativa',x+2 if side else x,y if side else y-2,1 if side else w-6,w-6 if side else 1,h-6,z+3,'0099ADA8')
for z in (100,145,190):picture(981,396,25,19,z,True)
for x in (1035,1120,1200):picture(x,502,48,59,178)
box(access,'Termostato vicino cucina',972,211,3,13,10,166,white)
# Keep the already reconstructed staircase and all door positions.
for t in list(room.findall('texture')):
    if t.get('attribute')=='floorTexture':room.remove(t)
room.insert(len(room.findall('property'))+len(room.findall('textStyle')),E.Element('texture',attribute='floorTexture',name='Piastrelle beige diagonali',width='100',height='100',image='1/studio-floor.png'))
room.set('floorColor','00C5C2B8')
assert [E.tostring(n) for n in protected]==before
assets['Home.xml']=E.tostring(r,encoding='utf-8',xml_declaration=True)
assets.pop('Home',None);assets.pop('ContentDigests',None)
tmp=path.with_suffix('.tmp')
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
    for name,data in assets.items():z.writestr(name,data)
with zipfile.ZipFile(tmp) as z:
    assert z.testzip() is None
    doc=E.fromstring(z.read('Home.xml'))
    for n in doc.iter():
        for attr in ('model','icon','planIcon','image'):
            if n.get(attr) and '://' not in n.get(attr):assert n.get(attr) in z.namelist()
    ids=[n.get('id') for n in doc.iter() if n.get('id')];assert len(ids)==len(set(ids))
tmp.replace(path)
print('Ingresso inferiore arredato e porta salotto in legno. Altri elementi preservati.')
