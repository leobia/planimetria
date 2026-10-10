"""Arreda l'ingresso superiore nel file corrente senza rigenerare la casa."""
from pathlib import Path
import zipfile, xml.etree.ElementTree as E, uuid

path=Path(__file__).with_name('Planimetria_due_livelli.sh3d')
with zipfile.ZipFile(path) as z: assets={n:z.read(n) for n in z.namelist()}
root=E.fromstring(assets['Home.xml'])
room=next(n for n in root.findall('room') if n.get('name')=='Ingresso su')
old=[g for g in root.findall('furnitureGroup') if g.get('name','').startswith('Ingresso su /')]
for g in old:root.remove(g)
protected=[n for n in root if n is not room]
before=[E.tostring(n) for n in protected]
insertion=next(i for i,n in enumerate(root) if n.tag=='wall')
def group(name):
    global insertion
    g=E.Element('furnitureGroup',dict(id='furnitureGroup-'+str(uuid.uuid4()),level='L2',name='Ingresso su / '+name,movable='true'))
    root.insert(insertion,g);insertion+=1
    return g
def box(g,name,x,y,w,d,h,z=0,color='00E8E6DF'):
    return E.SubElement(g,'pieceOfFurniture',dict(id='pieceOfFurniture-'+str(uuid.uuid4()),level='L2',name=name,model='built-in-cabinet/cube.obj',x=str(x),y=str(y),width=str(w),depth=str(d),height=str(h),elevation=str(z),color=color,movable='true'))
white='00E8E6DF';black='00252A2D'
wardrobe=group('armadio bianco a quattro ante')
box(wardrobe,'Corpo armadio',938,287,55,170,228)
for i in range(4):
    y=202+(i+.5)*42.5
    box(wardrobe,'Anta bianca',910,y,2,42.1,220,5)
    box(wardrobe,'Maniglia metallica',908,y+(-15 if i%2 else 15),2,2,12,105,'00A6A49E')
box(wardrobe,'Zoccolo',937,287,52,170,5,0,'00CECBC3')
desk=group('tavolino bianco con monitor')
box(desk,'Piano tavolino',703,473,92,46,4,74)
box(desk,'Fascia frontale',703,452,88,3,12,62)
for x in (662,744):
    for y in (454,492):box(desk,'Gamba tavolino',x,y,4,4,74)
box(desk,'Monitor nero',703,483,55,5,34,87,black)
box(desk,'Schermo scuro',703,480,51,1,29,90,'00161C23')
box(desk,'Supporto monitor',703,483,5,5,10,78,black)
box(desk,'Base monitor',703,481,24,16,2,78,black)
box(desk,'Tastiera nera',703,460,43,15,2,78,black)
box(desk,'Mouse',735,459,6,10,3,78,'007D8589')
box(desk,'Telefono cordless',733,482,6,6,20,78,black)
shelf=group('mensola e quadro')
box(shelf,'Mensola bianca',704,499,102,23,3,165)
for x in (669,739):box(shelf,'Supporto mensola',x,503,3,13,14,151,'00C7C5BE')
box(shelf,'Scatola',679,499,25,17,17,168,'00A9967D')
box(shelf,'Scatola chiara',679,499,23,16,9,185,'00D6D0C5')
box(shelf,'Confezione rossa',708,499,14,13,37,168,'00883743')
box(shelf,'Cornice in legno',704,510,57,2,38,209,'00917B55')
box(shelf,'Stampa nel quadro',704,508,49,1,30,213,'00C7CDCB')
window=next(n for n in root.findall('doorOrWindow') if n.get('id')=='o11')
wx=float(window.get('x'));wy=float(window.get('y'));ww=float(window.get('width'))
curtain=group('tenda azzurra alla finestra')
box(curtain,'Bastone tenda',wx,wy-11,ww+12,3,3,215,'00B8B6B0')
for i in range(24):
    box(curtain,'Piega tenda azzurra',wx-ww/2+(i+.5)*ww/24,wy-13,ww/24+.15,1.5,115,98,'006CAAE0' if i%2 else '0083BDE9')
radiator=group('radiatore bianco')
for i in range(8):box(radiator,'Elemento radiatore',872+(i-3.5)*6,502,5.5,10,62,12,'00DDDCD5')
box(radiator,'Valvola radiatore',897,502,7,7,6,69,'00C1C0B9')
pet=group('lettiera coperta accanto al tavolino')
box(pet,'Base lettiera',778,463,42,48,9,0,'00383C3A')
box(pet,'Copertura chiara',778,463,41,47,32,9,'00D4DCCF')
box(pet,'Apertura frontale scura',778,438.8,27,1,21,12,'003E4745')
box(pet,'Filtro superiore',778,463,16,18,1,41,'00B2B9AE')
# Reuse the studio's diagonal tile texture without duplicating the image.
for n in list(room.findall('texture')):
    if n.get('attribute')=='floorTexture':room.remove(n)
texture=E.Element('texture',dict(attribute='floorTexture',name='Piastrelle grigie diagonali',width='100',height='100',image='1/studio-floor.png'))
room.insert(len(room.findall('property'))+len(room.findall('textStyle')),texture)
room.set('floorColor','00C5C2B8')
assert [E.tostring(n) for n in protected]==before
assert len([g for g in root.findall('furnitureGroup') if 'scrivania con PC' in g.get('name','')])==2
assets['Home.xml']=E.tostring(root,encoding='utf-8',xml_declaration=True)
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
print('Ingresso arredato; cestino centrale escluso. Altri ambienti e modifiche manuali preservati.')
