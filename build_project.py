from pathlib import Path
import xml.etree.ElementTree as E
import zipfile, math, io
from PIL import Image, ImageDraw

OUT=Path(__file__).parent
S=1400/1009
root=E.Element('home',version='7500',name='Planimetria su due livelli - quote provvisorie',selectedLevel='L1',wallHeight='270')
def el(tag,parent=root,**a): return E.SubElement(parent,tag,{k:str(v) for k,v in a.items()})
el('property',name='com.eteks.sweethome3d.SweetHome3D.Units',value='CENTIMETER')
el('environment',allLevelsVisible='false',groundColor='DDE1E4',skyColor='CCE3F5',lightColor='D0D0D0')
el('compass',x=-100,y=-100,diameter=70,visible='false')
el('camera',attribute='topCamera',x=700,y=1600,z=1800,yaw=0,pitch=0.8,fieldOfView=1.05)
for lid,name,z,h in [('L1','Primo piano',0,270),('L2','Secondo piano (mansardato)',290,250)]:
    el('level',id=lid,name=name,elevation=z,floorThickness=20,height=h)

assets={}
def obj_boxes(name,boxes):
    lines=['# Generated editable architectural placeholder']; n=0
    for x,y,z,w,h,d in boxes:
        for xx,yy,zz in [(x,y,z),(x+w,y,z),(x+w,y+h,z),(x,y+h,z),(x,y,z+d),(x+w,y,z+d),(x+w,y+h,z+d),(x,y+h,z+d)]: lines.append(f'v {xx} {yy} {zz}')
        for f in [(1,4,3,2),(5,6,7,8),(1,2,6,5),(4,8,7,3),(1,5,8,4),(2,3,7,6)]: lines.append('f '+' '.join(str(n+i) for i in f))
        n+=8
    assets[name]=('\n'.join(lines)+'\n').encode()
obj_boxes('models/door.obj',[(0,0,0,.06,1,.18),(.94,0,0,.06,1,.18),(0,.94,0,1,.06,.18),(.06,0,.08,.88,.94,.035)])
obj_boxes('models/window.obj',[(0,0,0,.055,1,.18),(.945,0,0,.055,1,.18),(0,0,0,1,.055,.18),(0,.945,0,1,.055,.18),(.48,0,0,.04,1,.18)])
steps=[]
for i in range(8): steps.append((i/10,0,0,.1,(i+1)/12,.48))
steps.append((.8,0,0,.2,8/12,.48))
for i in range(4): steps.append((.8,0,.48+i*.13,.2,(9+i)/12,.13))
obj_boxes('models/stairs.obj',steps)
obj_boxes('models/step.obj',[(0,0,0,1,1,1)])
stair_icon=Image.new('RGBA',(330,220),(0,0,0,0))
sd=ImageDraw.Draw(stair_icon)
sd.rectangle((1,1,263,105),fill='#E3D8C4',outline='#333333',width=3)
for i in range(1,9): sd.line((i*26,1,i*26,105),fill='#333333',width=2)
sd.rectangle((263,1,328,218),fill='#E3D8C4',outline='#333333',width=3)
for y in (105,133,161,189): sd.line((263,y,328,y),fill='#333333',width=2)
buf=io.BytesIO(); stair_icon.save(buf,format='PNG'); assets['models/stairs-plan.png']=buf.getvalue()

openings=[]
def xy(x,y): return round((x-58)*S,3),round(y*S,3)
def opening(lid,x,y,width,angle,kind='door',height=210,elev=0):
    X,Y=xy(x,y); w=width*S
    a=dict(id=f'o{len(openings)}',level=lid,name={'door':'Porta','window':'Finestra','french':'Portafinestra'}[kind],x=X,y=Y,width=w,depth=28,height=height,elevation=elev,angle=angle,model='models/'+('door' if kind=='door' else 'window')+'.obj',color='EEE9DE',movable='false',wallThickness=1,wallDistance=0,boundToWall='true')
    node=el('doorOrWindow',**a)
    if kind=='door': el('sash',parent=node,xAxis=0,yAxis=0,width=1,startAngle=0,endAngle=math.pi/2)
    openings.append((lid,x,y,width,angle,kind))
opening('L1',428,257,55,math.pi/2)
opening('L1',643,169,55,math.pi/2)
opening('L1',889,274,50,math.pi/2)
opening('L1',847,312,48,0)
opening('L1',58,133,90,math.pi/2,'window',125,85)
opening('L1',1067,102,108,math.pi/2,'french',220)
opening('L1',1067,265,50,math.pi/2,'window',65,140)
opening('L1',1067,419,65,math.pi/2,'window',125,85)
opening('L2',428,110,50,math.pi/2)
opening('L2',869,305,50,0)
opening('L2',947,418,45,math.pi/2)
opening('L2',535,305,65,0,'window',110,90)
stair_group=el('furnitureGroup',id='stairs',level='L1',name='Scala aperta in legno e ferro, curva a ventaglio',movable='false')
def stair_step(index,cx,cy,w,depth,top):
    X,Y=xy(cx,cy)
    el('pieceOfFurniture',parent=stair_group,id=f'step{index}',level='L1',name=f'Pedata in legno {index}',x=X,y=Y,width=w*S,depth=depth*S,height=5,elevation=top-5,model='models/step.obj',movable='false',color='A26B39')
rise=290/15
for i in range(8): stair_step(15-i,470+(i+.5)*14,40,14,60,(15-i)*rise)
for i in range(4): stair_step(4-i,607,70+(i+.5)*12.5,50,12.5,(4-i)*rise)
def prism_asset(name,pts):
    lines=[]
    for h in (0,1):
        for x,z in pts: lines.append(f'v {x} {h} {z}')
    n=len(pts)
    faces=[list(range(n,0,-1)),list(range(n+1,2*n+1))]
    for i in range(n): j=(i+1)%n; faces.append([i+1,j+1,j+1+n,i+1+n])
    for face in faces:
        for i in range(1,len(face)-1): lines.append('f '+' '.join(map(str,[face[0],face[i],face[i+1]])))
    assets[name]=('\n'.join(lines)+'\n').encode()
winders=[[(582,70),(632,70),(632,35)],[(582,70),(632,35),(632,10),(607,10)],[(582,70),(607,10),(582,10)]]
for index,pts in enumerate(winders,5):
    x0,x1=min(x for x,y in pts),max(x for x,y in pts); y0,y1=min(y for x,y in pts),max(y for x,y in pts)
    name=f'models/winder{index}.obj';prism_asset(name,[((x-x0)/(x1-x0),(y-y0)/(y1-y0)) for x,y in pts])
    X,Y=xy((x0+x1)/2,(y0+y1)/2)
    el('pieceOfFurniture',parent=stair_group,id=f'winder{index}',level='L1',name=f'Pedata a ventaglio {index}',x=X,y=Y,width=(x1-x0)*S,depth=(y1-y0)*S,height=5,elevation=index*rise-5,model=name,color='A26B39',movable='false')
def iron_box(parent,lid,name,cx,cy,w,dep,height,elevation):
    X,Y=xy(cx,cy)
    return el('pieceOfFurniture',parent=parent,level=lid,name=name,x=X,y=Y,width=w*S,depth=dep*S,height=height,elevation=elevation,model='models/step.obj',color='242424',movable='false')
# Thin steel supports under the wooden treads leave the risers open.
for i in range(8):
    top=(15-i)*rise
    iron_box(stair_group,'L1','Supporto metallico',470+(i+.5)*14,40,5,48,7,top-12)
    iron_box(stair_group,'L1','Montante ringhiera',470+(i+.5)*14,70,1.8,1.8,95,top)
for i in range(4):
    top=(4-i)*rise
    iron_box(stair_group,'L1','Supporto metallico',607,70+(i+.5)*12.5,40,5,7,top-12)
    iron_box(stair_group,'L1','Montante ringhiera',582,70+(i+.5)*12.5,1.8,1.8,95,top)
def sloped_rail(name,a,b):
    # Short solid sections remain thin even in viewers that show model bounds.
    x0,y0,z0=a; x1,y1,z1=b
    count=math.ceil(max(abs(x1-x0),abs(y1-y0))/1.5)
    for i in range(count):
        t=(i+.5)/count
        cx=x0+(x1-x0)*t; cy=y0+(y1-y0)*t
        height=4+abs(z1-z0)/count
        iron_box(stair_group,'L1','Corrimano' if 'handrail' in name else 'Cosciale',cx,cy,max(2,abs(x1-x0)/count),max(2,abs(y1-y0)/count),height,z0+(z1-z0)*t-height/2)
for offset,label in [(95,'handrail'),(-16,'stringer')]:
    sloped_rail(f'models/{label}-upper.obj',(477,70,15*rise+offset),(575,70,8*rise+offset))
    sloped_rail(f'models/{label}-lower.obj',(582,76.25,4*rise+offset),(582,113.75,rise+offset))
gate=el('furnitureGroup',id='gate',level='L2',name='Parapetto con cancelletto nero al vano scala',movable='false')
for x in (472,499,526,553,580,607,632): iron_box(gate,'L2','Barra cancelletto',x,72,1.5,1.5,100,0)
for h in (8,54,98): iron_box(gate,'L2','Traversa cancelletto',552,72,160,1.5,3,h)

walls=[]
def wall(lid,x1,y1,x2,y2,t=18):
    a,b=xy(x1,y1),xy(x2,y2)
    el('wall',id=f'w{len(walls)}',level=lid,xStart=a[0],yStart=a[1],xEnd=b[0],yEnd=b[1],thickness=t*S,height=270 if lid=='L1' else 250,leftSideColor='F5F2EB',rightSideColor='F5F2EB',topColor='303030')
    walls.append((lid,x1,y1,x2,y2,t))
for lid in ['L1','L2']:
    bottom=308 if lid=='L1' else 305; left=799 if lid=='L1' else 807; low=516 if lid=='L1' else 486
    for seg in [(58,0,1067,0),(1067,0,1067,low),(1067,low,left,low),(left,low,left,bottom),(left,bottom,58,bottom),(58,bottom,58,0)]: wall(lid,*seg)
    wall(lid,428,0,428,bottom,16)
for seg in [(643,0,643,219),(643,219,1067,219),(889,219,889,314),(799,314,1067,314)]: wall('L1',*seg,14)
for seg in [(640,0,640,224),(807,305,1067,305),(947,305,947,486)]: wall('L2',*seg,14)
rooms=[]
def room(lid,name,points,color):
    r=el('room',id=f'r{len(rooms)}',level=lid,name=name,nameYOffset=0,floorColor=color,ceilingVisible='false',areaVisible='false')
    if name=='Ingresso': r.set('nameXOffset','-110'); r.set('nameYOffset','35')
    el('textStyle',parent=r,attribute='nameStyle',fontSize=22)
    for p in points:
        x,y=xy(*p); el('point',parent=r,x=x,y=y)
    rooms.append((lid,name,points,color))
def rect(lid,name,x1,y1,x2,y2,color): room(lid,name,[(x1,y1),(x2,y1),(x2,y2),(x1,y2)],color)
rect('L1','Salotto',68,10,420,299,'E5D8C3')
room('L1','Ingresso',[(436,10),(636,10),(636,227),(881,227),(881,305),(436,299)],'BFC0BB')
rect('L1','Cucina',650,10,1057,212,'E2E8DC')
rect('L1','Bagno',896,227,1057,306,'D6E8ED')
rect('L1','Studio',809,322,1057,506,'E5D8C3')
rect('L2','Studio su',68,10,420,296,'E5D8C3')
room('L2','Ingresso su',[(436,10),(470,10),(470,70),(582,70),(582,120),(633,120),(633,224),(680,224),(680,296),(436,296)],'BFC0BB')
room('L2','Camera da letto',[(647,10),(1057,10),(1057,296),(680,296),(680,224),(647,224)],'E6DCCF')
rect('L2','Bagno',817,313,939,476,'D6E8ED')
rect('L2','Ripostiglio',955,313,1057,476,'E5E2DD')
def stair_line(lid,points,closed=False):
    p=el('polyline',level=lid,thickness=1.5,color='333333',closedPath=str(closed).lower())
    for x,y in points:
        X,Y=xy(x,y);el('point',parent=p,x=X,y=Y)
for lid in ('L1','L2'):
    stair_line(lid,[(470,10),(632,10),(632,120),(582,120),(582,70),(470,70)],True)
    for i in range(1,9): stair_line(lid,[(470+i*14,10),(470+i*14,70)])
    for y in (82.5,95,107.5): stair_line(lid,[(582,y),(632,y)])
    for pt in [(632,35),(607,10)]: stair_line(lid,[(582,70),pt])
for cx,cy in [(356,163),(967,154),(875,421)]:
    p=el('polyline',level='L2',thickness=2,color='008FCC',closedPath='true',dashStyle='DASH')
    for x,y in [(cx-28,cy-28),(cx+28,cy-28),(cx+28,cy+28),(cx-28,cy+28)]:
        X,Y=xy(x,y); el('point',parent=p,x=X,y=Y)
    l=el('label',level='L2',x=xy(cx,cy)[0],y=xy(cx,cy+44)[1],color='007DAA');el('textStyle',parent=l,fontSize=13);el('text',parent=l).text='Lucernario (posizione)'

def polygon_area(pts):
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pts,pts[1:]+pts[:1])))/2
lower_area=sum(polygon_area(pts)*S*S for lid,name,pts,color in rooms if lid=='L1')/10000
ratio=math.sqrt(90/lower_area)
for node in root.iter():
    if node.tag in ('wall','room','point','doorOrWindow','pieceOfFurniture','polyline','label','camera','compass'):
        for key in ('x','y','xStart','yStart','xEnd','yEnd','width','depth','thickness','diameter','nameXOffset','nameYOffset'):
            if key in node.attrib: node.set(key,str(round(float(node.get(key))*ratio,4)))
S*=ratio
lower_area=sum(polygon_area(pts)*S*S for lid,name,pts,color in rooms if lid=='L1')/10000
assert abs(lower_area-90)<0.001
xml=E.tostring(root,encoding='utf-8',xml_declaration=True)
(OUT/'Home.xml').write_bytes(xml)
with zipfile.ZipFile(OUT/'Planimetria_due_livelli.sh3d','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('Home.xml',xml)
    for name,data in assets.items(): z.writestr(name,data)
im=Image.new('RGB',(1200,1280),'white');d=ImageDraw.Draw(im)
for lid,oy,title in [('L1',70,'PRIMO PIANO'),('L2',690,'SECONDO PIANO (MANSARDATO)')]:
    d.text((45,oy-35),title,fill='black',font_size=25)
    for ll,name,pts,color in rooms:
        if ll!=lid:continue
        d.polygon([(x+5,y+oy) for x,y in pts],fill='#'+color)
        xs=[p[0] for p in pts];ys=[p[1] for p in pts]
        tx,ty=(min(xs)+max(xs))/2+5,(min(ys)+max(ys))/2+oy
        if name=='Ingresso': tx,ty=540+5,180+oy
        d.text((tx,ty),name,fill='black',anchor='mm',font_size=19)
    for ll,x1,y1,x2,y2,t in walls:
        if ll==lid:d.line((x1+5,y1+oy,x2+5,y2+oy),fill='#303030',width=int(t))
    for ll,x,y,w,a,k in openings:
        if ll!=lid:continue
        if a: box=(x-8+5,y-w/2+oy,x+8+5,y+w/2+oy)
        else: box=(x-w/2+5,y-8+oy,x+w/2+5,y+8+oy)
        d.rectangle(box,fill='white',outline='#529bb0' if k!='door' else '#a47737',width=2)
    for i in range(8): d.rectangle((470+i*14+5,oy+10,484+i*14+5,oy+70),outline='black',width=1)
    for pts in winders: d.polygon([(x+5,y+oy) for x,y in pts],fill='#A26B39',outline='black')
    for i in range(4):d.rectangle((582+5,oy+70+i*12.5,632+5,oy+82.5+i*12.5),fill='#A26B39',outline='black',width=1)
    if lid=='L2':
        for x,y in [(356,163),(967,154),(875,421)]:d.rectangle((x-28+5,y-28+oy,x+28+5,y+28+oy),outline='#008fcc',width=3)
d.text((45,1230),f'Piano inferiore: 90 m² netti circa. Larghezza {1009*S/100:.2f} m. Falde da definire.',fill='#555555',font_size=18)
im.save(OUT/'Anteprima_planimetria.png')
print('Creato progetto:',len(walls),'muri;',len(rooms),'stanze;',len(openings),'porte/finestre')
with zipfile.ZipFile(OUT/'Planimetria_due_livelli.sh3d') as z:
    assert z.testzip() is None
    doc=E.fromstring(z.read('Home.xml'))
    for node in doc.iter():
        for attr in ('model','icon','planIcon'):
            if attr in node.attrib: assert node.attrib[attr] in z.namelist()
    for name in z.namelist():
        if name.endswith('.obj'):
            lines=z.read(name).decode().splitlines()
            count=sum(line.startswith('v ') for line in lines)
            assert count>0
            for line in lines:
                if line.startswith('f '): assert all(1<=int(v)<=count for v in line.split()[1:])
print('Archivio, XML e riferimenti ai modelli verificati.')
print(f'Superficie inferiore: {lower_area:.2f} m²; larghezza: {1009*S/100:.2f} m')
