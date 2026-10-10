"""Arredi dello studio mansardato; quote in cm, posizioni nello schizzo."""
import math, io
from PIL import Image, ImageDraw

def furnish(root, el, assets, scale, xy):
    root.set('selectedLevel','L2')
    # Furniture is inserted before walls, as required by Home.xml.
    insertion=next(i for i,n in enumerate(root) if n.tag=='wall')
    def group(name):
        nonlocal insertion
        g=el('furnitureGroup',name=name,level='L2',movable='true')
        root.remove(g);root.insert(insertion,g);insertion+=1
        return g
    def box(g,name,x,y,w,d,h,z=0,color='D8C3A0',angle=0,pitch=0,roll=0):
        X,Y=xy(x,y)
        return el('pieceOfFurniture',parent=g,name=name,level='L2',x=X,y=Y,width=w,depth=d,height=h,elevation=z,model='models/step.obj',color=color,angle=angle,pitch=pitch,roll=roll,horizontallyRotatable='true',movable='true')
    def delta(cm): return cm/scale
    wood='8B5B32';pine='BB8A4F';black='24272B';white='E5E2D9';grey='858988'
    desk=group('Studio su / scrivania con PC, monitor e tastiera')
    box(desk,'Piano scrivania in legno',272,267,180,72,4,73,wood)
    for xx in (-80,80):
        for yy in (-26,26):box(desk,'Gamba scrivania',272+delta(xx),267+delta(yy),6,6,73,0,black)
    box(desk,'Monitor principale',278,280,64,5,39,86,black)
    box(desk,'Schermo',278,278,59,1,33,89,'B4CDD8')
    box(desk,'Piedistallo monitor',278,279,5,5,12,77,black)
    box(desk,'Base monitor',278,278,27,18,2,77,black)
    box(desk,'Monitor secondario verticale',323,278,4,31,44,83,black)
    box(desk,'Computer tower',217,277,24,43,46,77,black)
    for x in (211,215,219):box(desk,'Luce blu PC',x,264,2,1,24,89,'155BD5')
    box(desk,'Tastiera chiara',272,256,43,16,2,77,'DCDDD3')
    box(desk,'Tappetino mouse',240,253,27,24,1,77,black)
    box(desk,'Mouse',240,250,6,10,3,78,'47494B')
    chair=group('Studio su / sedia da ufficio grigia')
    box(chair,'Seduta imbottita',280,208,53,49,9,44,grey)
    box(chair,'Schienale in rete',280,194,53,5,62,49,grey)
    box(chair,'Poggiatesta',280,194,39,8,15,111,grey)
    box(chair,'Pistone',280,208,6,6,44,0,'C5C8C8')
    for angle in (0,math.pi/2):box(chair,'Base a razze',280,208,63,5,5,9,'C5C8C8',angle)
    for x,y in [(263,208),(297,208),(280,191),(280,225)]:box(chair,'Ruota',x,y,6,5,7,2,black)
    for x in (263,297):
        box(chair,'Bracciolo',x,208,8,36,4,67,black)
        box(chair,'Supporto bracciolo',x,208,4,4,19,48,'C5C8C8')
    cabinets=group('Studio su / armadi bassi bianchi sotto falda')
    for y in (48,107,166,225):
        box(cabinets,'Anta armadio sottotetto',87,y,48,96,94,0,white)
        box(cabinets,'Maniglia anta',102,y,2,4,2,52,'C3C1B9')
    bed=group('Studio su / letto singolo con coperta blu')
    box(bed,'Telaio letto',144,91,90,195,13,23,black)
    box(bed,'Materasso con coperta blu',144,91,92,195,17,36,'405B83')
    box(bed,'Cuscino',144,41,66,38,12,53,'7F8B9E')
    for x in (123,165):
        for y in (38,143):box(bed,'Piede letto',x,y,5,5,23,0,black)
    dresser=group('Studio su / cassettiera bianca e mensola')
    box(dresser,'Cassettiera',220,34,67,44,110,0,white)
    for z in (18,39,60,81,102):
        box(dresser,'Fronte cassetto',220,48,64,1,19,z-10,'EEECE4')
        box(dresser,'Pomello nero',220,49,4,2,2,z,black)
    box(dresser,'Mensola sopra cassettiera',233,20,135,23,3,167,pine)
    box(dresser,'Base lampada',220,34,16,16,3,110,black)
    box(dresser,'Stelo lampada',220,34,2,2,32,113,black)
    box(dresser,'Paralume lampada',220,34,18,16,16,145,black)
    books=group('Studio su / libreria in legno con libri e oggetti')
    for x in (302,399):box(books,'Fianco libreria',x,30,3,32,211,0,pine)
    for z in (3,38,75,112,149,186,211):box(books,'Ripiano libreria',350,30,166,32,3,z,pine)
    colors=['374F6C','6F3435','D3C9AB','303637','8D9C83']
    for shelf,z in enumerate((6,41,78,115,152,189)):
        for i in range(9 if shelf<3 else 5):
            box(books,'Libro o cofanetto',310+i*7,28,7+(i%3),20,20+(i%4)*3,z,colors[i%5])
        if shelf in (2,3,4):
            for x in (377,389):box(books,'Oggetto da collezione stilizzato',x,32,9,9,23,z,'B99368')
    bike=group('Studio su / cyclette grigia e nera')
    for y in (106,156):box(bike,'Piede stabilizzatore',235,y,54,8,7,0,black)
    box(bike,'Basamento cyclette',235,132,34,71,38,7,'737D87')
    box(bike,'Montante manubrio',235,109,9,12,88,35,'A2AAB1')
    box(bike,'Manubrio',235,107,48,6,6,123,black)
    for x in (222,248):box(bike,'Impugnatura',x,105,5,19,5,127,black)
    box(bike,'Display',235,108,21,9,16,121,black)
    box(bike,'Tubo sella',235,148,7,7,62,35,'A2AAB1')
    box(bike,'Sella',235,147,30,23,7,97,black)
    for x in (222,248):box(bike,'Pedale',x,132,8,17,3,21,black)
    wooden=group('Studio su / sedia in legno')
    box(wooden,'Seduta sedia',275,100,42,42,4,43,pine)
    box(wooden,'Schienale',275,88,43,3,36,47,pine)
    for x in (264,286):
        for y in (89,111):box(wooden,'Gamba sedia',x,y,4,4,43,0,pine)
    cats=group('Studio su / tiragraffi grigio e pesi')
    box(cats,'Base tiragraffi',397,69,55,48,4,0,'545455')
    box(cats,'Cuccia tiragraffi',397,69,45,42,35,18,'66676A')
    for z in (67,111):
        box(cats,'Palo tiragraffi',397,69,10,10,41,z-41,'B9AE95')
        box(cats,'Ripiano tiragraffi',397,69,51,42,4,z,'77787B')
    box(cats,'Vassoio manubri',355,95,65,37,4,0,'8E9290')
    for x in (342,360):
        box(cats,'Manubrio',x,95,5,25,5,7,'B0B1B0')
        for y in (89,101):box(cats,'Disco peso',x,y,15,5,15,4,black)
    ac=group('Studio su / climatizzatore e quadri')
    box(ac,'Climatizzatore bianco',349,289,85,23,29,198,white)
    box(ac,'Bocchetta climatizzatore',349,281,78,2,5,201,black)
    for x in (158,190):box(ac,'Quadro sulla parete',x,291,35,2,50,120,'514A66')
    # A true sloping plane made of thin horizontal strips: no solid wedge.
    roof=group('Studio su / falda in legno con lucernario')
    roof.set('visible','false')
    def roof_z(x):return 115+(x-68)/(420-68)*155
    window=(225,285,78,140)
    for i in range(88):
        x=70+i*4; lo,hi=window[2],window[3]
        ranges=[(10,296)] if not window[0]<=x<=window[1] else [(10,lo),(hi,296)]
        for a,b in ranges:box(roof,'Doghe della falda',x,(a+b)/2,4*scale,(b-a)*scale,4,roof_z(x),pine if i%3 else 'AD7A40')
    for x in (112,248):box(roof,'Trave a vista',x,153,22,480,22,roof_z(x)-22,wood)
    for y in (window[2],window[3]):
        for i in range(15):
            x=window[0]+(i+.5)*4
            box(roof,'Telaio lucernario',x,y,4*scale,7,7,roof_z(x)+1,white)
    for x in (window[0],window[1]):box(roof,'Telaio laterale lucernario',x,109,7,62*scale,7,roof_z(x)+1,white)
    for i in range(14):
        x=window[0]+3+(i+.5)*3.85
        box(roof,'Tenda oscurante blu del lucernario',x,109,3.85*scale,53*scale,2,roof_z(x)+3,'232B45')
    for panel in roof: panel.set('visible','false')
    tile=Image.new('RGB',(256,256),'#C5C2B8');draw=ImageDraw.Draw(tile)
    for v in range(-256,513,128):
        draw.line((v,0,v+256,256),fill='#8F8B80',width=2)
        draw.line((v,256,v+256,0),fill='#8F8B80',width=2)
    stream=io.BytesIO();tile.save(stream,format='PNG');assets['textures/studio-floor.png']=stream.getvalue()
    for r in root.findall('room'):
        if r.get('name')=='Studio su':
            r.set('floorColor','C5C2B8')
            texture=el('texture',parent=r,attribute='floorTexture',name='Piastrelle grigie diagonali',width=100,height=100,image='textures/studio-floor.png')
            r.remove(texture);r.insert(1,texture)
    # The photo places the skylight over the centre of the room, facing the door.
    for p in list(root.findall('polyline')):
        if p.get('color')=='008FCC' and float(p.find('point').get('x'))<600:root.remove(p)
    for l in list(root.findall('label')):
        if l.findtext('text')=='Lucernario (posizione)' and float(l.get('x'))<600:root.remove(l)
    outline=el('polyline',level='L2',color='008FCC',thickness=2,closedPath='true')
    for x,y in [(225,78),(285,78),(285,140),(225,140)]:
        X,Y=xy(x,y);el('point',parent=outline,x=X,y=Y)
    # Split the perimeter at the studio so only its walls follow the roof.
    for wall in list(root.findall('wall')):
        if wall.get('level')!='L2':continue
        x0,x1=float(wall.get('xStart')),float(wall.get('xEnd'))
        if abs(x0)<.01 and abs(x1)<.01:wall.set('height','115');wall.set('heightAtEnd','115')
        split=xy(428,0)[0]
        if min(x0,x1)<split<max(x0,x1) and abs(float(wall.get('yStart'))-float(wall.get('yEnd')))<.01:
            new=Eclone(wall);new.set('id',wall.get('id')+'studio')
            if x0<x1:
                new.set('xEnd',str(split));new.set('height','115');new.set('heightAtEnd','270');wall.set('xStart',str(split))
            else:
                new.set('xStart',str(split));new.set('height','270');new.set('heightAtEnd','115');wall.set('xEnd',str(split))
            root.insert(list(root).index(wall),new)
        if abs(x0-split)<.01 and abs(x1-split)<.01:wall.set('height','270')
    X,Y=xy(403,259)
    camera=el('observerCamera',attribute='storedCamera',name='Studio su - vista dalla porta',x=X,y=Y,z=450,yaw=math.pi/2,pitch=.08,fieldOfView=1.35)
    root.remove(camera)
    root.insert(next(i for i,n in enumerate(root) if n.tag=='level'),camera)

def Eclone(node):
    import xml.etree.ElementTree as E
    return E.fromstring(E.tostring(node))
