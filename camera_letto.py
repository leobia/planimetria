"""Ricostruzione fotografica della camera sul progetto corrente."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as E,uuid,math

path=Path(__file__).with_name('Planimetria_due_livelli.sh3d')
with zipfile.ZipFile(path) as z:assets={n:z.read(n) for n in z.namelist()}
r=E.fromstring(assets['Home.xml'])
room=next(n for n in r.findall('room') if n.get('name')=='Camera da letto')
door=next(n for n in r.findall('doorOrWindow') if n.get('id')=='o9')
for g in list(r.findall('furnitureGroup')):
    if g.get('name','').startswith('Camera /'):r.remove(g)
for wall in list(r.findall('wall')):
    if wall.get('id') in ('w7camera','w8camera'):r.remove(wall)
walls=[n for n in r.findall('wall') if n.get('id') in ('w7','w8','w19','w18')]
protected=[n for n in r if n is not room and n is not door and n not in walls]
before=[E.tostring(n) for n in protected]
index=next(i for i,n in enumerate(r) if n.tag=='wall')
def group(name,visible=True):
    global index
    g=E.Element('furnitureGroup',dict(id='furnitureGroup-'+str(uuid.uuid4()),level='L2',name='Camera / '+name,movable='true',visible=str(visible).lower()))
    r.insert(index,g);index+=1
    return g
def box(g,name,x,y,w,d,h,z=0,color='00E6E3D9'):
    return E.SubElement(g,'pieceOfFurniture',dict(id='pieceOfFurniture-'+str(uuid.uuid4()),level='L2',name=name,model='built-in-cabinet/cube.obj',x=str(x),y=str(y),width=str(w),depth=str(d),height=str(h),elevation=str(z),color=color,visible=g.get('visible'),movable='true'))
white='00E6E3D9';wood='00916435';black='00252A2D'
bed=group('letto matrimoniale bianco con comodini')
box(bed,'Telaio letto',1242,163,180,205,32,0,white)
box(bed,'Materasso con lenzuolo tortora',1242,163,174,199,21,32,'00918A83')
box(bed,'Testiera bianca',1242,59,183,5,105,0,white)
for x in (1200,1284):box(bed,'Cuscino grigio verde',x,94,69,42,12,53,'00858D80')
box(bed,'Coperta chiara',1242,205,178,110,2,54,'00D9D3C7')
for x in (1100,1384):
    box(bed,'Comodino bianco',x,87,47,41,54,0,white)
    box(bed,'Cassetto comodino',x,65,43,2,16,29,white)
    box(bed,'Base lampada',x,87,18,18,2,54,black)
    box(bed,'Stelo lampada',x,87,3,3,22,56,black)
    box(bed,'Paralume bianco',x,87,23,23,19,78,white)
wardrobe=group('armadi bianchi a muro sotto falda')
start,end=16.7948,497.132;span=(end-start)/8
box(wardrobe,'Corpo armadio a tutta parete',1650.3192,(start+end)/2,55,end-start,115)
for i in range(8):
    y=start+(i+.5)*span
    box(wardrobe,'Anta bianca',1622.8192,y,2,span-.35,108,6)
    box(wardrobe,'Pomello anta',1620.8192,y+span/2-5,2,2,2,61,'00BAB7AE')
tv=group('mobile TV in legno vicino al bagno')
box(tv,'Mobile basso in legno',1545,465,102,49,78,0,wood)
for x in (1520,1570):
    box(tv,'Anta mobile',x,439,48,2,67,6,wood)
    box(tv,'Pomello mobile',x,437,2,2,2,41,black)
box(tv,'Televisore nero',1545,469,98,6,60,89,black)
box(tv,'Schermo TV',1545,465.5,93,1,54,92,'001A2028')
box(tv,'Base TV',1545,469,43,24,3,78,black)
box(tv,'Supporto TV',1545,469,7,7,9,81,black)
chair=group('sedia in legno')
box(chair,'Seduta',1550,258,44,43,4,44,wood)
for x in (1532,1568):
    for y in (241,275):box(chair,'Gamba sedia',x,y,4,4,44,0,wood)
for z in (57,70,83):box(chair,'Traversa schienale',1550,276,44,3,5,z,wood)
for x in (1532,1568):box(chair,'Montante schienale',x,276,4,4,48,44,wood)
armchair=group('poltroncina bianca')
box(armchair,'Seduta poltrona',1083,292,66,62,18,30,white)
box(armchair,'Schienale',1083,323,76,12,60,31,white)
for x in (1048,1118):box(armchair,'Bracciolo',x,292,12,64,48,25,white)
for x in (1055,1111):
    for y in (268,316):box(armchair,'Piede poltrona',x,y,6,6,30,0,wood)
fan=group('ventilatore bianco e sgabello azzurro')
box(fan,'Base ventilatore',1500,358,37,37,4,0,'00DADCD8')
box(fan,'Colonna ventilatore',1500,358,5,5,94,4,'00DADCD8')
# Circular frame represented by short bars; no opaque rectangular panel.
for i in range(48):
    angle=i*2*math.pi/48
    box(fan,'Bordo griglia ventilatore',1500+25*math.cos(angle),358,3,3,3,115+25*math.sin(angle),'00D8DAD7')
for i in range(-4,5):
    x=i*5;hh=2*math.sqrt(25**2-x*x)
    box(fan,'Filo verticale griglia',1500+x,358,.7,1,hh,115-hh/2,'00B7BBB8')
box(fan,'Mozzo ventilatore',1500,356,11,6,11,109,'00D8DAD7')
for angle in (0,2*math.pi/3,4*math.pi/3):
    x=1500+9*math.cos(angle);z=115+9*math.sin(angle)
    box(fan,'Pala ventilatore semplificata',x,357,10,2,13,z-6,'00D0D4D0')
box(fan,'Seduta sgabello azzurro',1453,404,40,28,4,24,'003781A6')
for x in (1437,1469):
    for y in (394,414):box(fan,'Gamba sgabello',x,y,4,4,24,0,'003781A6')
decor=group('quadro sopra il letto')
box(decor,'Cornice scura',1242,18,74,2,55,139,'00564B35')
box(decor,'Immagine nel quadro',1242,16,68,1,49,142,'009A978D')
# Hidden by default to keep both plan and aerial view readable.
roof=group('falda in legno con travi e lucernario',False)
west,east=989.2249,1677.8192
def roof_z(x):return 300-(x-west)/(east-west)*165
window=(1450,1550,112,214)
for i in range(138):
    x=west+(i+.5)*(east-west)/138
    ranges=[(start,end)] if not window[0]<=x<=window[1] else [(start,window[2]),(window[3],end)]
    for a,b in ranges:box(roof,'Doghe in legno',x,(a+b)/2,(east-west)/138,b-a,4,roof_z(x),'00BC8B50' if i%3 else '00AC7942')
for x in (1270,1585):box(roof,'Trave a vista',x,(start+end)/2,23,end-start,24,roof_z(x)-24,'00734B2B')
for x in (window[0],window[1]):box(roof,'Telaio lucernario',x,163,7,102,7,roof_z(x)+1,white)
for y in (112,214):
    for i in range(20):
        x=1450+(i+.5)*5;box(roof,'Telaio lucernario',x,y,5,7,7,roof_z(x)+1,white)
for i in range(19):
    x=1454+(i+.5)*4.84;box(roof,'Oscurante blu scuro',x,163,4.84,94,2,roof_z(x)+3,'001F293F')
for n in list(room.findall('texture')):
    if n.get('attribute')=='floorTexture':room.remove(n)
room.insert(len(room.findall('property'))+len(room.findall('textStyle')),E.Element('texture',dict(attribute='floorTexture',name='Piastrelle grigie diagonali',width='100',height='100',image='1/studio-floor.png')))
room.set('floorColor','00C5C2B8')
door.set('name','Porta del bagno in legno');door.set('model','wooden-door/door.obj');door.set('color','008B5B32')
door.attrib.pop('modelSize',None)
# Only the bedroom portion of the shared perimeter follows this roof.
for wall in walls:
    if wall.get('id')=='w7':
        clone=E.fromstring(E.tostring(wall));clone.set('id','w7camera')
        clone.set('xStart',str(west));clone.set('xEnd','1694.614');clone.set('height','300');clone.set('heightAtEnd','135')
        wall.set('xEnd',str(west));r.insert(list(r).index(wall)+1,clone)
    elif wall.get('id')=='w8':
        clone=E.fromstring(E.tostring(wall));clone.set('id','w8camera')
        clone.set('yStart','0');clone.set('yEnd','512.2467');clone.set('height','135');clone.set('heightAtEnd','135')
        wall.set('yStart','512.2467');r.insert(list(r).index(wall),clone)
    elif wall.get('id')=='w19':wall.set('height',str(roof_z(float(wall.get('xStart')))));wall.set('heightAtEnd','135')
    elif wall.get('id')=='w18':wall.set('height','300')
assert [E.tostring(n) for n in protected]==before
assets['Home.xml']=E.tostring(r,encoding='utf-8',xml_declaration=True)
assets.pop('Home',None);assets.pop('ContentDigests',None)
tmp=path.with_suffix('.tmp')
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
    for name,data in assets.items():z.writestr(name,data)
with zipfile.ZipFile(tmp) as z:
    assert z.testzip() is None
    for n in E.fromstring(z.read('Home.xml')).iter():
        for attr in ('model','icon','planIcon','image'):
            if n.get(attr) and '://' not in n.get(attr):assert n.get(attr) in z.namelist()
tmp.replace(path)
print('Camera arredata. Porte mantenute in posizione; modifiche degli altri ambienti conservate.')
