"""Aggiorna solo armadi e porta nel progetto corrente, conservando le modifiche manuali."""
from pathlib import Path
import zipfile, xml.etree.ElementTree as E, math, uuid

path=Path(__file__).with_name('Planimetria_due_livelli.sh3d')
with zipfile.ZipFile(path) as z:
    contents={n:z.read(n) for n in z.namelist()}
root=E.fromstring(contents['Home.xml'])
cabinet=next(g for g in root.findall('furnitureGroup') if 'armadi' in g.get('name',''))
door=next(n for n in root.findall('doorOrWindow') if n.get('id')=='o8')
protected=[n for n in root if n is not cabinet and n is not door]
before=[E.tostring(n) for n in protected]
room=next(r for r in root.findall('room') if r.get('name')=='Studio su')
points=[(float(n.get('x')),float(n.get('y'))) for n in room.findall('point')]
left=min(x for x,y in points); start=min(y for x,y in points); end=max(y for x,y in points)
depth=55; height=110; length=end-start

def boxes_model(boxes):
    lines=['o Furniture','g Furniture'];offset=0
    for x,y,z,w,h,d in boxes:
        for xx,yy,zz in [(x,y,z),(x+w,y,z),(x+w,y+h,z),(x,y+h,z),(x,y,z+d),(x+w,y,z+d),(x+w,y+h,z+d),(x,y+h,z+d)]:lines.append(f'v {xx} {yy} {zz}')
        for face in [(1,4,3,2),(5,6,7,8),(1,2,6,5),(4,8,7,3),(1,5,8,4),(2,3,7,6)]:
            for i in (1,2):lines.append('f '+' '.join(str(offset+j) for j in (face[0],face[i],face[i+1])))
        offset+=8
    return ('\n'.join(lines)+'\n').encode()
contents['built-in-cabinet/cube.obj']=boxes_model([(0,0,0,1,1,1)])
contents['wooden-door/door.obj']=boxes_model([(0,0,0,.055,1,1),(.945,0,0,.055,1,1),(0,.95,0,1,.05,1),(.055,0,.43,.89,.95,.14),(.11,.12,.4,.77,.28,.025),(.11,.5,.4,.77,.35,.025)])
for n in list(cabinet):cabinet.remove(n)
cabinet.set('name','Studio su / armadio a muro bianco a tutta parete')
cabinet.set('x',str(left+depth/2));cabinet.set('y',str((start+end)/2))
cabinet.set('width',str(depth));cabinet.set('depth',str(length));cabinet.set('height',str(height))
cabinet.set('movable','false')
def part(name,x,y,w,d,h,z=0,color='00E5E2D9'):
    E.SubElement(cabinet,'pieceOfFurniture',dict(id='pieceOfFurniture-'+str(uuid.uuid4()),level=cabinet.get('level'),name=name,model='built-in-cabinet/cube.obj',x=str(x),y=str(y),width=str(w),depth=str(d),height=str(h),elevation=str(z),color=color,movable='false'))
part('Corpo armadio incassato',left+depth/2,(start+end)/2,depth-2,length,height-6,6)
part('Zoccolo continuo',left+depth/2,(start+end)/2,depth-4,length,6,color='00C9C7BE')
count=math.ceil(length/62);span=length/count
for i in range(count):
    cy=start+(i+.5)*span
    part('Anta bianca a muro',left+depth-1,cy,2,span-.35,height-8,7)
    part('Pomello anta',left+depth+.5,cy+span/2-5,2,2,2,58,'00B3B0A7')
door.set('name','Porta dello studio in legno')
door.set('color','008B5B32');door.set('model','wooden-door/door.obj')
for attr in ('modelSize','icon','planIcon'):
    door.attrib.pop(attr,None)
assert [E.tostring(n) for n in protected]==before
desks=[g for g in root.findall('furnitureGroup') if 'scrivania con PC' in g.get('name','')]
assert len(desks)==2
contents['Home.xml']=E.tostring(root,encoding='utf-8',xml_declaration=True)
# XML is the editable representation. Drop stale Java serialization and digests.
contents.pop('Home',None);contents.pop('ContentDigests',None)
tmp=path.with_suffix('.tmp')
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
    for name,data in contents.items():z.writestr(name,data)
with zipfile.ZipFile(tmp) as z:
    assert z.testzip() is None
    parsed=E.fromstring(z.read('Home.xml'))
    for n in parsed.iter():
        for attr in ('model','icon','planIcon','image'):
            value=n.get(attr)
            if value and '://' not in value:assert value in z.namelist(),value
tmp.replace(path)
print(f'Armadio a muro: {length:.1f} cm, profondità {depth} cm, altezza {height} cm, {count} ante.')
print('Due scrivanie e tutti gli elementi estranei a porta e armadio conservati senza modifiche.')
