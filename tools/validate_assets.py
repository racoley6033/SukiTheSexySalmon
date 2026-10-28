"""Validate generated deliverables without requiring Blender or Cairo."""
import json, struct, subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
CHARACTER=json.loads((ROOT/'character.json').read_text())
EXPRESSIONS=CHARACTER['expressions']
assert set(CHARACTER['referenceExpressions']) <= set(EXPRESSIONS)
for e in EXPRESSIONS:
    tree=ET.parse(ROOT/f'assets/2d/{e}.svg')
    ids={node.get('id') for node in tree.iter()}
    assert {'peach-face','salmon-bob-locks','rice-collar','boots','left-arm-glove','jalapeno-hat','avocado-forehead'} <= ids,e
    path=ROOT/f'assets/2d/{e}.png'
    with Image.open(path) as im:
        assert im.mode=='RGBA' and im.size==(1080,1080),path
        assert im.getextrema()[3][0]==0 and im.getextrema()[3][1]==255,path
        box=im.getchannel('A').getbbox()
        assert box and box[0]>0 and box[1]>0 and box[2]<im.width and box[3]<im.height,path
    data=(ROOT/f'assets/3d/suki-{e}.glb').read_bytes()
    magic,version,length=struct.unpack_from('<4sII',data)
    assert magic==b'glTF' and version==2 and length==len(data),e
    chunklen,kind=struct.unpack_from('<II',data,12); assert kind==0x4E4F534A
    doc=json.loads(data[20:20+chunklen]); assert doc.get('meshes') and doc.get('materials') and doc.get('animations'),e
    assert sum(len(a['channels']) for a in doc['animations'])>=2,e
    names={n.get('name','') for n in doc['nodes']}
    assert {'Peach face','Avocado forehead slice','Jalapeno seeded ring','Peace glove palm','Sally_root'} <= names,e
    assert any(n.startswith('Rice grain') for n in names),e
    assert any(n.startswith('Boot toe') for n in names),e
    assert not any(n in ('Salmon topping','Rice cushion') for n in names),e
    with Image.open(ROOT/f'assets/3d/suki-{e}.png') as im:
        assert im.mode=='RGBA' and im.size==(1080,1080),e
        box=im.getchannel('A').getbbox()
        assert box and box[0]>0 and box[1]>0 and box[2]<im.width and box[3]<im.height,e
for clip in ('idle','wave','dance'):
    with Image.open(ROOT/f'assets/social/{clip}.webp') as im: assert im.n_frames==48,clip
    for fmt,dim in [('square',(1080,1080)),('portrait',(1080,1920))]:
        file=ROOT/f'assets/social/{clip}-{fmt}.mp4'
        doc=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(file)]))
        stream=doc['streams'][0]; assert (stream['width'],stream['height'])==dim and int(stream['nb_frames'])==48,file
with Image.open(ROOT/'assets/artwork/sally-menu-hero.png') as im:
    assert im.mode=='RGBA' and im.getextrema()[3][0]==0
with Image.open(ROOT/'assets/artwork/sally-expressions-atlas.png') as im:
    assert im.mode=='RGBA' and im.width%3==0 and im.height%2==0
    assert im.getextrema()[3][0]==0 and im.getextrema()[3][1]>=240
print('PASS: ten Sally 2D/3D expressions, alpha images, animated GLBs, three loops and six social videos.')
