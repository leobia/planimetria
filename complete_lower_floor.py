"""Completa cucina, studio e bagno dalle foto senza rigenerare la casa."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as E,uuid,math,io
from PIL import Image,ImageDraw
path=Path(__file__).with_name('Planimetria_due_livelli.sh3d')
with zipfile.ZipFile(path) as z:assets={n:z.read(n) for n in z.namelist()}
r=E.fromstring(assets['Home.xml'])
rooms=[n for n in r.findall('room') if n.get('level')=='L1' and n.get('name') in ('Cucina','Studio','Bagno')]
doors=[n for n in r.findall('doorOrWindow') if n.get('name','').startswith('Porta') and not n.get('name','').startswith('Portafinestra')]
for g in list(r.findall('furnitureGroup')):
    if g.get('name','').startswith(('Cucina /','Studio giu /','Bagno giu /')):r.remove(g)
protected=[n for n in r if n not in rooms+doors];before=[E.tostring(n) for n in protected]
for door in doors:
    door.set('model','wooden-door/door.obj');door.set('color','008B5B32')
    door.set('name','Porta in legno' if door.get('name')=='Porta' else door.get('name'))
idx=next(i for i,n in enumerate(r) if n.tag=='wall')
def group(name):
    global idx
    g=E.Element('furnitureGroup',id='lower-'+str(uuid.uuid4()),level='L1',name=name,movable='true')
    r.insert(idx,g);idx+=1;return g
def box(g,name,x,y,w,d,h,z=0,color='00EAE8DF',model='built-in-cabinet/cube.obj'):
    return E.SubElement(g,'pieceOfFurniture',dict(id='lower-'+str(uuid.uuid4()),level='L1',name=name,model=model,x=str(x),y=str(y),width=str(w),depth=str(d),height=str(h),elevation=str(z),color=color,movable='true'))
def cyl(g,name,x,y,w,d,h,z=0,color='00262829'):
    return box(g,name,x,y,w,d,h,z,color,'salotto/cylinder.obj')
white='00EAE8DF';black='00262829';steel='00AFB7B8';wood='00755335'
def chair(g,x,y):
    box(g,'Seduta sedia',x,y,43,43,5,43,'00616D4F')
    for xx in (x-17,x+17):
        for yy in (y-17,y+17):box(g,'Gamba sedia',xx,yy,4,4,43,0,wood)
    for xx in (x-17,x+17):box(g,'Montante schienale',xx,y+19,4,4,46,46,wood)
    box(g,'Schienale',x,y+19,43,4,15,77,wood)
def bowl(g,name,x,y,w,d,z,color=white):
    cyl(g,'Interno '+name,x,y,w*.78,d*.75,3,z-5,'008B9698')
    for i in range(40):
        a=i*math.pi/20;box(g,'Bordo '+name,x+w*.44*math.cos(a),y+d*.44*math.sin(a),5,5,7,z-3,color)
def faucet(g,x,y,z):
    box(g,'Rubinetto',x,y,4,4,18,z,steel);box(g,'Bocca rubinetto',x,y+7,4,17,3,z+15,steel)

k=group('Cucina / basi bianche e piano scuro')
for x in (1042,1112,1182,1252,1322,1392,1462):
    box(k,'Base cucina',x,48,69,60,83,5)
    box(k,'Anta bianca',x,79,67,2,73,10)
    box(k,'Maniglia metallica',x,81,46,2,2,78,steel)
box(k,'Piano scuro continuo',1252,48,490,63,4,88,'003A3C37')
box(k,'Zoccolo',1252,48,485,54,8,0,'00C6C4BC')
ap=group('Cucina / forno, lavastoviglie, lavatrice e frigorifero')
box(ap,'Forno inox',1112,79,60,3,76,10,steel)
box(ap,'Vetro forno',1112,81,50,1,43,23,black)
box(ap,'Maniglia forno',1112,83,46,4,3,68,steel)
box(ap,'Piano cottura',1112,48,62,52,2,92,steel)
for x in (1096,1128):
    for y in (34,59):cyl(ap,'Bruciatore',x,y,17,17,2,94,black)
for x in (1092,1105,1118,1131):cyl(ap,'Manopola forno',x,81,6,2,6,79,black)
box(ap,'Lavastoviglie bianca',1182,81,60,3,78,8)
box(ap,'Pannello lavastoviglie',1182,83,57,2,10,73,'00D8D9D5')
box(ap,'Lavatrice bianca',1392,80,60,4,80,5)
p=cyl(ap,'Oblo nero lavatrice',1392,84,43,43,4,27,black);p.set('pitch',str(math.pi/2))
p=cyl(ap,'Vetro oblo',1392,87,33,33,1,32,'0065777B');p.set('pitch',str(math.pi/2))
box(ap,'Pannello lavatrice',1392,84,58,2,12,73,black)
box(ap,'Frigorifero inox',1538,52,72,66,193,0,steel)
for z,h in ((5,56),(65,124)):
    box(ap,'Porta frigorifero',1538,86,69,3,h,z,'009A9E9D')
    box(ap,'Maniglia frigorifero',1510,89,3,3,25,z+16,black)
up=group('Cucina / pensili bianchi e cappa')
for x in (1042,1112,1182,1252,1322,1392,1462,1538):
    box(up,'Pensile bianco',x,36,68,35,88,145)
    box(up,'Anta pensile',x,54,66,2,84,147)
    box(up,'Maniglia pensile',x,56,51,2,2,150,steel)
box(up,'Cappa sopra fornelli',1112,41,67,46,16,137)
box(up,'Cornice superiore',1290,36,573,40,4,233)
sink=group('Cucina / lavello e piccoli elettrodomestici')
box(sink,'Lavello inox',1282,48,105,47,2,92,steel)
bowl(sink,'vasca lavello',1267,50,49,36,94,steel)
faucet(sink,1267,27,94)
box(sink,'Scolapiatti',1314,48,35,39,1,94,steel)
box(sink,'Macchina caffe',1042,45,29,33,39,92,black)
box(sink,'Griglia macchina caffe',1042,65,23,9,2,99,steel)
box(sink,'Portacoltelli',1462,31,22,14,27,92,wood)
tab=group('Cucina / tavolo in legno, sedie e mensole')
box(tab,'Piano tavolo',1240,309,145,65,5,74,wood)
for x in (1178,1302):
    for y in (283,335):box(tab,'Gamba tavolo',x,y,7,7,74,0,wood)
for x in (1195,1285):chair(tab,x,254)
box(tab,'Tavolino vicino portafinestra',1598,307,55,49,4,75,'00B49B70')
for x in (1576,1620):
    for y in (287,327):box(tab,'Gamba tavolino',x,y,4,4,75,0,'00B49B70')
box(tab,'Friggitrice ad aria',1598,307,30,33,35,79,black)
for z,x,w in ((185,1310,155),(218,1250,210)):
    box(tab,'Mensola in legno',x,343,w,24,4,z,wood)
    for j in range(6):cyl(tab,'Bottiglia sulla mensola',x-w/2+17+j*22,343,7,7,23,z+4,('003A6045','00C4C3B8')[j%2])
pan=group('Cucina / rivestimento bianco con riga verde')
for y in (17,355):
    box(pan,'Rivestimento ceramico',1335,y,680,1,135,0,white)
    box(pan,'Riga verde',1335,y+(1 if y==17 else -1),680,1,1.5,90,'00375B58')

s=group('Studio giu / armadio chiaro a quattro ante')
box(s,'Corpo armadio',1475,578,210,60,218,0,'00C6AD7D')
for i in range(4):
    x=1396+i*52.5;box(s,'Anta armadio',x,609,51.5,2,213,4,'00D8BB85')
    box(s,'Maniglia scura',x,612,43,3,3,103,black)
d=group('Studio giu / scrivania in legno e sedia da ufficio')
box(d,'Piano scrivania',1598,767,130,65,3,74,'00C28842')
for x in (1540,1656):
    for y in (741,793):box(d,'Gamba scrivania',x,y,4,4,74,0,'00B99661')
box(d,'Borsa nera sulla scrivania',1608,767,44,29,16,77,black)
box(d,'Seduta sedia ufficio',1560,697,49,48,10,42,black)
box(d,'Schienale sedia ufficio',1560,674,48,6,53,48,black)
cyl(d,'Stelo sedia ufficio',1560,697,7,7,35,7,black)
for a in range(5):
    a=a*math.pi*2/5;p=box(d,'Raggio base sedia',1560+14*math.cos(a),697+14*math.sin(a),36,4,4,5,black);p.set('angle',str(a))
b=group('Studio giu / libreria bassa e radiatore')
box(b,'Fondo libreria',1620,835,91,3,91,0,wood)
for x in (1576,1664):box(b,'Fianco libreria',x,823,4,29,91,0,wood)
for z in (0,29,58,89):box(b,'Ripiano libreria',1620,823,94,30,3,z,wood)
for i in range(13):box(b,'Libro',1582+i*6,823,4,22,22,32,('0085573C','00C6BB93')[i%2])
for y in range(659,749,7):box(b,'Elemento radiatore sotto finestra',1670,y,12,6,65,12,white)
acc=group('Studio giu / sedie, lettiera e scala pieghevole')
for x,y in ((1301,713),(1301,793),(1630,643)):chair(acc,x,y)
box(acc,'Specchio appoggiato alla sedia',1630,662,39,4,58,44,white)
box(acc,'Superficie specchio',1630,665,33,1,50,48,'00AFC4C4')
box(acc,'Base lettiera coperta',1460,807,45,52,12,0,'007E8580')
box(acc,'Copertura lettiera',1460,807,44,51,34,12,'00CDD0C5')
box(acc,'Apertura lettiera',1460,780,28,1,26,15,black)
box(acc,'Tappetino lettiera',1460,755,47,48,1,0,black)
box(acc,'Cestino bianco',1455,717,23,23,34,0,white)
for x in (1510,1547):box(acc,'Montante scala pieghevole',x,833,3,5,155,0,steel)
for z in (20,47,74,101):box(acc,'Gradino scala pieghevole',1528,829,38,17,3,z,steel)
box(acc,'Quadro con cornice',1450,846,58,3,65,155,'00784840')
box(acc,'Stampa nel quadro',1450,844,52,1,59,158,'00C5B18C')

san=group('Bagno giu / WC e bidet sotto finestra')
for name,y in (('WC',474),('bidet',413)):
    box(san,'Base '+name,1644,y,28,27,33)
    bowl(san,name,1643,y,57,38,41)
    if name=='bidet':faucet(san,1666,y,41)
box(san,'Sedile WC alzato',1668,474,4,37,43,43)
lav=group('Bagno giu / mobile lavabo, specchio e doccetta')
box(lav,'Mobile lavabo in legno',1476,410,102,48,78,0,'007E5B42')
box(lav,'Piano lavabo bianco',1476,410,106,51,5,78)
bowl(lav,'lavabo',1476,414,64,38,86);faucet(lav,1476,391,83)
box(lav,'Specchio grande',1476,387,100,2,90,105,'00B0C7CC')
for x in (1425,1527):box(lav,'Cornice specchio',x,386,2,3,94,103,steel)
box(lav,'Luce sopra specchio',1476,389,90,4,4,199,'00D8EEEF')
box(lav,'Asta doccetta a parete',1552,386,3,3,110,90,steel)
box(lav,'Soffione doccetta',1552,394,13,19,3,197,steel)
box(lav,'Miscelatore doccetta',1552,390,18,5,5,109,steel)
box(lav,'Pensile bagno bianco',1600,394,37,24,75,137)
for x in (1591,1609):box(lav,'Anta pensile',x,407,17,2,72,139)
det=group('Bagno giu / radiatore e asciugamani verdi')
for x in range(1440,1512,7):box(det,'Elemento radiatore',x,506,6,10,65,10,white)
box(det,'Asciugamano verde',1480,499,33,2,59,32,'00859536')
box(det,'Portasciugamano bidet',1604,389,3,25,3,80,steel)
box(det,'Asciugamano verde bidet',1604,392,2,22,43,38,'0098A748')
box(det,'Portarotolo WC',1650,505,15,4,3,66,steel)
box(det,'Carta igienica',1650,501,12,7,10,58)

# Small repeating blue rosettes evoke the photographed ceramic pattern.
im=Image.new('RGB',(256,256),'#EEE8D2');dr=ImageDraw.Draw(im)
dr.rectangle((0,0,255,255),outline='#B8B4A6',width=2)
for cx,cy,rad in ((128,128,35),(25,25,14),(231,25,14),(25,231,14),(231,231,14)):
    for i in range(16):
        a=i*math.pi/8;x=cx+rad*.65*math.cos(a);y=cy+rad*.65*math.sin(a)
        dr.ellipse((x-4,y-4,x+4,y+4),fill='#41688D')
    dr.ellipse((cx-7,cy-7,cx+7,cy+7),fill='#41688D')
buf=io.BytesIO();im.save(buf,format='PNG');assets['lower-bath/rosettes.png']=buf.getvalue()
clad=group('Bagno giu / piastrelle crema con motivi blu')
def panel(name,x,y,w,d,h,z=0):
    p=box(clad,name,x,y,w,d,h,z,'00EEE8D2')
    E.SubElement(p,'texture',attribute='texture',name='Ceramica con rosette blu',width='20',height='20',image='lower-bath/rosettes.png')
panel('Rivestimento parete lavabo',1543,383,270,1,220)
panel('Rivestimento parete radiatore',1543,513,270,1,220)
panel('Rivestimento sotto finestra',1678,448,1,128,139)
panel('Rivestimento sopra finestra',1678,448,1,128,15,205)
for y in (389,508):panel('Rivestimento ai lati finestra',1678,y,1,10,66,139)
for room in rooms:
    for t in list(room.findall('texture')):
        if t.get('attribute')=='floorTexture':room.remove(t)
    bath=room.get('name')=='Bagno'
    image='bathroom-floor/blue-tiles.png' if bath else '1/studio-floor.png'
    room.insert(len(room.findall('property'))+len(room.findall('textStyle')),E.Element('texture',attribute='floorTexture',name='Piastrelle blu' if bath else 'Piastrelle diagonali chiare',width='40' if bath else '100',height='40' if bath else '100',image=image))
    room.set('floorColor','00253578' if bath else '00C5C2B8')
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
print('Cucina, studio e bagno completati; porte interne in legno. Altri elementi preservati.')
