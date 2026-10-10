"""Bagno mansardato e ripostiglio, aggiornamento selettivo del progetto."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as E,uuid,math,io
from PIL import Image,ImageDraw

path=Path(__file__).with_name('Planimetria_due_livelli.sh3d')
with zipfile.ZipFile(path) as z:assets={n:z.read(n) for n in z.namelist()}
r=E.fromstring(assets['Home.xml'])
rooms=[n for n in r.findall('room') if n.get('level')=='L2' and n.get('name') in ('Bagno','Ripostiglio')]
for g in list(r.findall('furnitureGroup')):
    if g.get('name','').startswith(('Bagno su /','Ripostiglio /')):r.remove(g)
storage_door=next(n for n in r.findall('doorOrWindow') if n.get('id')=='o10')
protected=[n for n in r if n not in rooms and n is not storage_door]
before=[E.tostring(n) for n in protected]
insertion=next(i for i,n in enumerate(r) if n.tag=='wall')
def group(name,visible=True):
    global insertion
    g=E.Element('furnitureGroup',dict(id='furnitureGroup-'+str(uuid.uuid4()),level='L2',name=name,visible=str(visible).lower(),movable='true'))
    r.insert(insertion,g);insertion+=1;return g
def box(g,name,x,y,w,d,h,z=0,color='00E9E8E2'):
    return E.SubElement(g,'pieceOfFurniture',dict(id='pieceOfFurniture-'+str(uuid.uuid4()),level='L2',name=name,model='built-in-cabinet/cube.obj',x=str(x),y=str(y),width=str(w),depth=str(d),height=str(h),elevation=str(z),color=color,visible=g.get('visible'),movable='true'))
white='00E9E8E2';blue='00253578';chrome='00B4BCBC'
def bowl(g,name,x,y,w,d,z):
    box(g,'Interno '+name,x,y,w*.69,d*.68,3,z-5,'00C3CAC9')
    for i in range(32):
        a=i*2*math.pi/32
        box(g,'Bordo '+name,x+w*.44*math.cos(a),y+d*.44*math.sin(a),5,5,7,z-3,white)
sanitary=group('Bagno su / WC e bidet')
box(sanitary,'Base WC',1451,575,25,34,32)
bowl(sanitary,'WC',1448,575,38,56,40)
box(sanitary,'Cassetta WC',1467,575,13,39,67,18)
box(sanitary,'Coperchio cassetta',1467,575,15,41,3,85)
box(sanitary,'Base bidet',1450,642,25,30,34)
bowl(sanitary,'bidet',1446,642,38,57,40)
box(sanitary,'Rubinetto bidet',1466,642,3,3,12,43,chrome)
box(sanitary,'Bocca rubinetto',1462,642,9,3,3,52,chrome)
sink=group('Bagno su / lavabo su piano rivestito di piastrelle')
box(sink,'Mobile lavabo in muratura',1306,632,60,104,80,0,white)
box(sink,'Piano lavabo',1306,632,63,108,5,80,white)
bowl(sink,'lavabo',1306,650,47,56,88)
box(sink,'Rubinetto lavabo',1282,650,3,3,16,85,chrome)
box(sink,'Bocca rubinetto lavabo',1288,650,15,3,3,99,chrome)
box(sink,'Specchio',1278,640,2,78,80,104,'00B6CCD2')
box(sink,'Cornice specchio',1277,640,3,84,3,184,chrome)
box(sink,'Barra asciugamano',1320,576,37,3,3,65,chrome)
box(sink,'Asciugamano beige',1310,575,20,2,39,27,'00BFA69A')
shower=group('Bagno su / box doccia in fondo')
box(shower,'Piatto doccia bianco',1318,754,82,82,8,0,white)
box(shower,'Fondo piatto doccia',1318,754,72,72,2,8,'00CEDBD9')
for x in (1278,1358):
    for y in (714,794):box(shower,'Montante box doccia',x,y,3,3,182,8,white)
for y in (714,794):box(shower,'Profilo superiore doccia',1318,y,82,3,3,187)
for x in (1278,1358):box(shower,'Profilo superiore doccia',x,754,3,82,3,187)
box(shower,'Asta doccia',1281,775,2,2,105,65,chrome)
box(shower,'Soffione',1288,775,17,12,3,168,chrome)
box(shower,'Miscelatore',1282,775,4,16,6,95,chrome)
details=group('Bagno su / tappeto e accessori')
box(details,'Tappeto blu',1380,696,58,75,1,0,'001B2D4C')
box(details,'Portasciugamano bidet',1474,646,3,31,3,88,chrome)
box(details,'Asciugamano rosa',1472,646,2,25,38,51,'00BA9B99')
box(details,'Portarotolo',1471,548,3,16,3,67,chrome)
box(details,'Carta igienica',1467,548,8,12,8,63,white)
box(details,'Bilancia',1410,754,29,29,3,0,'00C8CCC6')
box(details,'Asciugamano blu doccia',1279,715,2,21,80,105,'003D7EC5')
panels=group('Bagno su / rivestimento bianco con fasce blu')
for x in (1275,1479):
    spans=[(526,799)] if x==1275 else [(526,662),(742,799)]
    for a,b in spans:
        box(panels,'Rivestimento a parete',x,(a+b)/2,1,b-a,183,0,white)
        for h,th in [(92,4),(174,10)]:box(panels,'Fascia blu',x-1 if x==1479 else x+1,(a+b)/2,1,b-a,th,h,blue)
box(panels,'Rivestimento parete di fondo',1377,798,204,1,183,0,white)
for h,th in [(92,4),(174,10)]:box(panels,'Fascia blu sul fondo',1377,797,204,1,th,h,blue)
storage=group('Ripostiglio / scaffali con scatole')
for cx,cy,w,d in [(1654,668,43,257),(1571,776,85,43)]:
    for x in (cx-w/2+2,cx+w/2-2):
        for y in (cy-d/2+2,cy+d/2-2):box(storage,'Montante scaffale',x,y,3,3,168,0,'007B8585')
    for h in (5,45,85,125,165):box(storage,'Ripiano scaffale',cx,cy,w,d,3,h,'00B4A07C')
    for h in (8,48,88,128):
        for j in range(3 if d>100 else 2):
            y=cy-d/2+28+j*70 if d>100 else cy
            x=cx if d>100 else cx-20+j*40
            box(storage,'Scatola riposta',x,y,32,36,27,h,'00AA9879' if j%2 else '00C7BBA3')
roof=group('Bagno su / falda e lucernario (nascosti)',False)
for i in range(55):
    y=528+i*5
    z=250-(y-526)/273*70
    spans=[(1275,1480)] if not 635<=y<=715 else [(1275,1340),(1420,1480)]
    for a,b in spans:box(roof,'Doghe soffitto',(a+b)/2,y,b-a,5,4,z,'00B7874C')
for y in (575,760):box(roof,'Trave in legno',1377,y,204,21,23,250-(y-526)/273*70-23,'00714B2B')
for x in (1340,1420):box(roof,'Telaio lucernario',x,675,5,80,6,211,white)
for y in (635,715):box(roof,'Telaio lucernario',1380,y,80,5,6,250-(y-526)/273*70,white)
for i in range(16):box(roof,'Vetro lucernario',1380,637.5+i*5,72,5,2,250-(637.5+i*5-526)/273*70+2,'00B5D7E7')
storage_roof=group('Ripostiglio / falda in legno (nascosta)',False)
for i in range(35):
    x=1509+i*5
    box(storage_roof,'Doghe soffitto',x,662,5,274,4,230-(x-1506)/172*55,'00A47846')
tile=Image.new('RGB',(256,256),'#253578');draw=ImageDraw.Draw(tile)
for n in (0,128,255):
    draw.line((n,0,n,256),fill='#788397',width=2);draw.line((0,n,256,n),fill='#788397',width=2)
data=io.BytesIO();tile.save(data,format='PNG');assets['bathroom-floor/blue-tiles.png']=data.getvalue()
for room in rooms:
    for texture in list(room.findall('texture')):
        if texture.get('attribute')=='floorTexture':room.remove(texture)
    image='bathroom-floor/blue-tiles.png' if room.get('name')=='Bagno' else '1/studio-floor.png'
    texture=E.Element('texture',dict(attribute='floorTexture',name='Piastrelle blu' if room.get('name')=='Bagno' else 'Piastrelle diagonali',width='60' if room.get('name')=='Bagno' else '100',height='60' if room.get('name')=='Bagno' else '100',image=image))
    room.insert(len(room.findall('property'))+len(room.findall('textStyle')),texture)
    room.set('floorColor',blue if room.get('name')=='Bagno' else '00C5C2B8')
storage_door.set('name','Porta bianca del ripostiglio');storage_door.set('color',white)
storage_door.set('model','wooden-door/door.obj');storage_door.attrib.pop('modelSize',None)
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
print('Bagno e ripostiglio arredati. Altri ambienti e posizioni delle porte preservati.')
