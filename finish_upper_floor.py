"""Porta della camera e altezze decrescenti di bagno e ripostiglio."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as E,math,uuid

path=Path(__file__).with_name('Planimetria_due_livelli.sh3d')
with zipfile.ZipFile(path) as z:assets={n:z.read(n) for n in z.namelist()}
r=E.fromstring(assets['Home.xml'])
for n in list(r):
    if n.get('id') in ('bedroom-entry-wall','bedroom-entry-door','bedroom-entry-ac'):r.remove(n)
high_side,low_side=1257.9447,1694.614
def height(x):return 250-(x-high_side)/(low_side-high_side)*70
wall_ids=('w8','w9','w10','w19','w20')
changed=[n for n in r.findall('wall') if n.get('id') in wall_ids]
groups=[g for g in r.findall('furnitureGroup') if g.get('name','').startswith(('Bagno su /','Ripostiglio /'))]
rooms=[n for n in r.findall('room') if n.get('name') in ('Ingresso su','Camera da letto')]
protected=[n for n in r if n not in changed+groups+rooms]
before=[E.tostring(n) for n in protected]
for w in changed:
    w.set('height',str(round(height(float(w.get('xStart'))),3)))
    w.set('heightAtEnd',str(round(height(float(w.get('xEnd'))),3)))
for g in groups:
    name=g.get('name','')
    if 'falda' in name:
        if name.startswith('Bagno su /'):
            for p in list(g):g.remove(p)
            def panel(label,x,y,width,depth,h,z,color):
                E.SubElement(g,'pieceOfFurniture',dict(id='pieceOfFurniture-'+str(uuid.uuid4()),level='L2',name=label,model='built-in-cabinet/cube.obj',x=str(x),y=str(y),width=str(width),depth=str(depth),height=str(h),elevation=str(z),color=color,visible='false',movable='true'))
            for i in range(41):
                x=1277.5+i*5
                spans=[(526,799)] if not 1340<=x<=1420 else [(526,635),(715,799)]
                for a,b in spans:panel('Doghe soffitto',x,(a+b)/2,5,b-a,4,height(x),'00B7874C')
            for x in (1300,1450):panel('Trave in legno',x,662.5,21,273,23,height(x)-23,'00714B2B')
            for x in (1340,1420):panel('Telaio lucernario',x,675,5,80,6,height(x)+1,'00E9E8E2')
            for i in range(16):
                x=1342.5+i*5
                for y in (635,715):panel('Telaio lucernario',x,y,5,5,6,height(x)+1,'00E9E8E2')
                panel('Vetro lucernario',x,675,5,72,2,height(x)+2,'00B5D7E7')
        for p in g.findall('pieceOfFurniture'):
            x=float(p.get('x'));z=height(x)
            pname=p.get('name','')
            if 'Trave' in pname:z-=float(p.get('height'))
            elif 'Telaio' in pname:z+=1
            elif 'Vetro' in pname:z+=2
            p.set('elevation',str(round(z,3)))
    if 'box doccia' in name:
        for p in g.findall('pieceOfFurniture'):
            if 'Montante' in p.get('name',''):p.set('height','164')
            if 'Profilo superiore' in p.get('name',''):p.set('elevation','172')
    if 'rivestimento' in name:
        for p in g.findall('pieceOfFurniture'):
            if 'Rivestimento' in p.get('name',''):p.set('height','174')
            if 'Fascia' in p.get('name','') and float(p.get('elevation','0'))>150:p.set('elevation','162')
for room in rooms:
    if room.get('name')=='Camera da letto':
        for p in room.findall('point'):
            if abs(float(p.get('x'))-1044.6484)<.1:p.set('x','989.2249')
    else:
        for p in room.findall('point'):
            if abs(float(p.get('x'))-1044.6484)<.1:p.set('x','965.7121')
wall=E.Element('wall',dict(id='bedroom-entry-wall',level='L2',xStart='977.4679',yStart='376.2079',xEnd='977.4679',yEnd='512.2467',thickness='23.513',height='300',leftSideColor='00F5F2EB',rightSideColor='00F5F2EB',topColor='00303030'))
r.insert(next(i for i,n in enumerate(r) if n.tag=='room'),wall)
door=E.Element('doorOrWindow',dict(id='bedroom-entry-door',level='L2',name='Porta in legno della camera',model='wooden-door/door.obj',x='977.4679',y='444',angle=str(math.pi/2),width='90',depth='25',height='210',color='008B5B32',movable='false',boundToWall='true'))
E.SubElement(door,'sash',dict(xAxis='0',yAxis='0',width='1',startAngle='0',endAngle=str(math.pi/2)))
idx=next(i for i,n in enumerate(r) if n.tag=='wall');r.insert(idx,door)
ac=E.Element('furnitureGroup',dict(id='bedroom-entry-ac',level='L2',name='Camera / condizionatore sopra la porta',movable='true'))
def part(name,x,w,d,h,z,color):
    E.SubElement(ac,'pieceOfFurniture',dict(id='pieceOfFurniture-'+str(uuid.uuid4()),level='L2',name=name,model='built-in-cabinet/cube.obj',x=str(x),y='444',angle=str(math.pi/2),width=str(w),depth=str(d),height=str(h),elevation=str(z),color=color,movable='true'))
part('Condizionatore bianco',1001,85,23,28,223,'00E9E8E2')
part('Bocchetta scura',1013,78,2,5,225,'00252A2D')
r.insert(idx+1,ac)
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
print('Porta in legno e climatizzatore aggiunti. Bagno e ripostiglio scendono verso destra, lato TV/ripostiglio.')
