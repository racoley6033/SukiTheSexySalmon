"""Validate generated deliverables without requiring Blender or Cairo."""
import json, struct, subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
EXPRESSIONS = ('happy', 'wink', 'excited', 'love', 'surprised', 'sad', 'angry', 'sleepy')
ROOT=Path(__file__).resolve().parents[1]
for e in EXPRESSIONS:
    ET.parse(ROOT/f'assets/2d/{e}.svg')
    path=ROOT/f'assets/2d/{e}.png'
    with Image.open(path) as im:
        assert im.mode=='RGBA' and im.size==(1080,1080),path
        assert im.getextrema()[3][0]==0 and im.getextrema()[3][1]==255,path
    data=(ROOT/f'assets/3d/suki-{e}.glb').read_bytes()
    magic,version,length=struct.unpack_from('<4sII',data)
    assert magic==b'glTF' and version==2 and length==len(data),e
    chunklen,kind=struct.unpack_from('<II',data,12); assert kind==0x4E4F534A
    doc=json.loads(data[20:20+chunklen]); assert doc.get('meshes') and doc.get('materials') and doc.get('animations'),e
    assert sum(len(a['channels']) for a in doc['animations'])>=2,e
    with Image.open(ROOT/f'assets/3d/suki-{e}.png') as im: assert im.mode=='RGBA' and im.size==(1080,1080),e
for clip in ('idle','wave','dance'):
    with Image.open(ROOT/f'assets/social/{clip}.webp') as im: assert im.n_frames==48,clip
    for fmt,dim in [('square',(1080,1080)),('portrait',(1080,1920))]:
        file=ROOT/f'assets/social/{clip}-{fmt}.mp4'
        doc=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(file)]))
        stream=doc['streams'][0]; assert (stream['width'],stream['height'])==dim and int(stream['nb_frames'])==48,file
print('PASS: eight 2D/3D expressions, alpha images, animated GLBs, three loops and six social videos.')
