"""Arreda il salotto dalle tre foto, preservando il resto del progetto."""
from pathlib import Path
import zipfile, xml.etree.ElementTree as E, uuid, math

path=Path(__file__).with_name('Planimetria_due_livelli.sh3d')
with zipfile.ZipFile(path) as z: assets={n:z.read(n) for n in z.namelist()}
r=E.fromstring(assets['Home.xml'])
room=next(n for n in r.findall('room') if n.get('name')=='Salotto')
for g in list(r.findall('furnitureGroup')):
    if g.get('name','').startswith('Salotto /'):r.remove(g)
protected=[n for n in r if n is not room]
before=[E.tostring(n) for n in protected]
index=next(i for i,n in enumerate(r) if n.tag=='wall')

def group(name):
    global index
    g=E.Element('furnitureGroup',id='salotto-'+str(uuid.uuid4()),level='L1',name='Salotto / '+name,movable='true')
    r.insert(index,g);index+=1
    return g
def box(g,name,x,y,w,d,h,z=0,color='00E9E6DC',model='built-in-cabinet/cube.obj'):
    return E.SubElement(g,'pieceOfFurniture',dict(id='salotto-'+str(uuid.uuid4()),level='L1',name=name,model=model,x=str(x),y=str(y),width=str(w),depth=str(d),height=str(h),elevation=str(z),color=color,movable='true'))

# Cylinders provide round tables, lamp shades and the cat scratching post.
lines=[]
for yy in (0,1):
    for i in range(48):
        a=2*math.pi*i/48;lines.append(f'v {math.cos(a)/2} {yy} {math.sin(a)/2}')
lines.append('f '+' '.join(str(i) for i in range(48,0,-1)))
lines.append('f '+' '.join(str(i) for i in range(49,97)))
for i in range(48):
    j=(i+1)%48;lines.append(f'f {i+1} {j+1} {j+49} {i+49}')
assets['salotto/cylinder.obj']=('\n'.join(lines)+'\n').encode()
def cyl(g,name,x,y,w,d,h,z=0,color='006F452C'):
    return box(g,name,x,y,w,d,h,z,color,'salotto/cylinder.obj')
wood='0066432E';black='00222526';white='00EEEBDD'
sofa=group('divano bianco con cuscini rossi')
box(sofa,'Base divano',320,450,225,88,30,8,white)
box(sofa,'Schienale',320,486,225,16,65,25,white)
for x in (212,428):box(sofa,'Bracciolo',x,450,16,86,47,17,white)
for x in (252,320,388):box(sofa,'Cuscino seduta',x,445,66,68,15,38,white)
for x in (255,320):box(sofa,'Cuscino rosso',x,469,55,15,40,51,'00A72742')
tv=group('mobile TV nero, diffusori e giradischi')
box(tv,'Mobile TV',320,48,180,44,42,0,black)
for x in (261,320,379):box(tv,'Anta mobile TV',x,71,58,2,29,3,'002C3030')
box(tv,'Televisore',320,44,112,6,66,52,black)
box(tv,'Schermo TV',320,47.5,107,1,60,55,'00131920')
box(tv,'Piedistallo TV',320,48,46,24,3,42,black)
box(tv,'Supporto TV',320,44,6,6,8,45,black)
for x in (245,395):
    box(tv,'Diffusore in legno',x,45,30,29,56,42,wood)
    box(tv,'Griglia diffusore',x,60,28,1,51,45,black)
box(tv,'Mobile giradischi',455,48,65,46,74,0,'00323838')
box(tv,'Giradischi in legno',455,48,49,35,9,74,wood)
box(tv,'Coperchio giradischi',455,48,49,35,5,83,'00999790')
coffee=group('tavolino in vetro e tappeto chiaro')
box(coffee,'Tappeto chiaro decorato',320,340,250,190,0.7,0,'00D7D0BF')
for x in (221,419):box(coffee,'Bordo tappeto',x,340,3,175,0.2,.7,'009AABA8')
for y in (253,427):box(coffee,'Bordo tappeto',320,y,200,3,.2,.7,'009AABA8')
glass=box(coffee,'Piano in vetro',320,330,115,65,1.5,42,'00B8D2D0')
E.SubElement(glass,'material',name='glass',color='66B8D2D0',shininess='0.9')
for x in (278,362):box(coffee,'Supporto nero tavolino',x,330,12,52,42,0,black)
box(coffee,'Ripiano basso',320,330,85,49,3,12,black)
book=group('libreria in legno accanto alla finestra')
box(book,'Fondo libreria',38,396,4,94,190,0,wood)
for y in (351,441):box(book,'Fianco libreria',55,y,38,5,190,0,wood)
for z in (0,50,92,134,183):box(book,'Ripiano libreria',55,396,38,94,5,z,wood)
box(book,'Cornice superiore',55,396,43,102,8,188,wood)
for y in (373,419):box(book,'Anta inferiore',76,y,2,44,43,5,wood)
for i in range(13):box(book,'Libro',58,357+i*6,26,4,30+(i%3)*3,55,('00554A3E','00873437','00282D34')[i%3])
for i in range(7):box(book,'Libro e album',58,360+i*10,24,6,28,139,('00B8AB88','00514639')[i%2])
table=group('tavolo rotondo in legno e sedie')
cyl(table,'Piano tavolo rotondo',104,100,110,110,5,73,wood)
cyl(table,'Piede centrale',104,100,21,21,70,3,wood)
for a in (0,2.094,4.189):
    b=box(table,'Base del tavolo',104+20*math.cos(a),100+20*math.sin(a),55,9,8,0,wood);b.set('angle',str(a))
def chair(g,x,y,back_y):
    box(g,'Seduta sedia',x,y,42,42,5,43,'00B4A278')
    for xx in (x-17,x+17):
        for yy in (y-17,y+17):box(g,'Gamba sedia',xx,yy,4,4,43,0,wood)
    for xx in (x-17,x+17):box(g,'Montante schienale',xx,back_y,4,4,46,45,wood)
    box(g,'Schienale sedia',x,back_y,42,4,13,76,wood)
chair(table,104,178,198)
chair(table,104,32,15)
chairs=group('due sedie accanto al giradischi')
chair(chairs,523,57,37);chair(chairs,552,116,96)
access=group('lampada, tavolino nero, sgabello e tiragraffi')
cyl(access,'Tavolino nero rotondo',480,417,45,45,3,58,black)
for x,y in ((464,402),(496,402),(480,434)):box(access,'Gamba tavolino',x,y,2,2,58,0,black)
cyl(access,'Base lampada',458,473,27,27,4,0,black)
cyl(access,'Stelo lampada',458,473,4,4,115,4,black)
cyl(access,'Paralume bianco',458,473,38,38,35,119,white)
box(access,'Seduta sgabello sotto finestra',40,246,30,30,4,39,'00B08E58')
for x in (28,52):
    for y in (234,258):box(access,'Gamba sgabello',x,y,3,3,39,0,'00B08E58')
box(access,'Base tiragraffi',466,354,40,40,3,0,'00797976')
cyl(access,'Colonna tiragraffi',466,354,12,12,83,3,'00C9B68B')
cyl(access,'Robot aspirapolvere vicino ingresso',565,342,35,35,9,0,black)
for t in list(room.findall('texture')):
    if t.get('attribute')=='floorTexture':room.remove(t)
t=E.Element('texture',attribute='floorTexture',name='Piastrelle beige diagonali',width='100',height='100',image='1/studio-floor.png')
room.insert(len(room.findall('property'))+len(room.findall('textStyle')),t)
room.set('floorColor','00C5C2B8')
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
            if n.get(attr) and '://' not in n.get(attr):assert n.get(attr) in z.namelist(),n.get(attr)
tmp.replace(path)
print('Salotto arredato. Tutti gli elementi esterni al salotto preservati.')
