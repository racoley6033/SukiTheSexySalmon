"""Blender 4.3+: build Suki, export expression GLBs and a transparent render.
blender --background --python 3d-blender/export_suki.py -- --render
"""
import argparse, math, random, sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/3d'; OUT.mkdir(parents=True,exist_ok=True)
EXPRESSIONS=('happy','wink','excited','love','surprised','sad','angry','sleepy')

def material(name,color):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=.4
    return m

def build(expression):
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    palette={k:material(k,v) for k,v in {'salmon':(.96,.30,.20),'rice':(.96,.91,.74),'stripe':(1,.65,.40),'avocado':(.48,.68,.18),'jalapeno':(.08,.32,.11),'sauce':(.8,.025,.015),'nori':(.015,.045,.028),'white':(1,.98,.88),'iris':(.10,.55,.20),'pink':(.9,.13,.23)}.items()}
    root=bpy.data.objects.new('Suki_root',None); bpy.context.collection.objects.link(root)
    def ball(name,loc,scale,mat,parent=root):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=loc)
        o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(palette[mat]); o.parent=parent
        for p in o.data.polygons: p.use_smooth=True
        return o
    def line(name,points,radius,mat,parent=root):
        c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.bevel_depth=radius; c.bevel_resolution=3
        s=c.splines.new('POLY'); s.points.add(len(points)-1)
        for p,co in zip(s.points,points): p.co=(*co,1)
        o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(palette[mat]); o.parent=parent
        # Mesh conversion makes facial strokes portable in glTF.
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o; bpy.ops.object.convert(target='MESH')
        return bpy.context.object
    def rounded(name,loc,scale,mat):
        bpy.ops.mesh.primitive_cube_add(size=2,location=loc); o=bpy.context.object; o.name=name; o.scale=scale
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        o.data.materials.append(palette[mat]); o.parent=root
        b=o.modifiers.new('Soft rounded edges','BEVEL'); b.width=.25; b.segments=6
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o
    rounded('Rice cushion',(0,0,.92),(1,.60,.43),'rice')
    rounded('Salmon topping',(0,-.02,1.47),(1.12,.67,.40),'salmon')
    random.seed(12)
    for i in range(45):
        x=random.uniform(-.86,.86); z=random.uniform(.64,1.12)
        ball(f'Rice grain {i:02}',(x,-.587,z),(.065,.035,.025),'rice')
    for i,x in enumerate([-.85,-.43,0,.43,.85]):
        line(f'Salmon marbling {i}',[(x+t*.22,-.58+t*.95,1.88) for t in [j/14 for j in range(15)]],.032,'stripe')
    # Short, perpendicular fringe stays on forehead, above the eyes.
    ball('Avocado fringe',(.05,-.66,1.76),(.12,.065,.19),'avocado')
    bpy.ops.mesh.primitive_torus_add(major_radius=.22,minor_radius=.075,location=(.20,0,1.98))
    o=bpy.context.object; o.name='Jalapeno slice'; o.parent=root; o.data.materials.append(palette['jalapeno'])
    for x,y in [(.05,0),(.30,.08),(.26,-.10)]: ball('Jalapeno seed',(x,y,1.99),(.035,.025,.015),'rice')
    ball('Single hot sauce dot',(.20,-.03,2.07),(.085,.085,.06),'sauce')
    for side in (-1,1):
        x=side*.43
        closed=expression=='sleepy' or (expression=='wink' and side==1)
        if closed:
            line('Closed eyelid',[(x-.17+i*.034,-.738,1.48+.06*math.sin(i*math.pi/10)) for i in range(11)],.027,'nori')
        elif expression=='love':
            # Two lobes and a tapered lower half form a heart eye.
            ball('Heart lobe',(x-.065,-.75,1.51),(.09,.05,.10),'pink'); ball('Heart lobe',(x+.065,-.75,1.51),(.09,.05,.10),'pink')
            line('Heart point',[(x-.11,-.75,1.49),(x,-.75,1.30),(x+.11,-.75,1.49)],.055,'pink')
        else:
            ball('Eye white',(x,-.684,1.48),(.20,.07,.24),'white'); ball('Green iris',(x+.02,-.75,1.47),(.115,.04,.16),'iris'); ball('Pupil',(x+.025,-.787,1.47),(.055,.025,.11),'nori'); ball('Eye sparkle',(x-.012,-.81,1.54),(.035,.012,.04),'white')
        if expression=='angry': line('Angry eyebrow',[(x-.17,-.75,1.77+side*.05),(x+.17,-.75,1.77-side*.05)],.032,'nori')
        ball('Blush',(side*.77,-.71,1.25),(.11,.025,.045),'pink')
        line('Leg',[(side*.40,0,.60),(side*.44,-.02,.18)],.085,'nori'); ball('Foot',(side*.49,-.12,.12),(.20,.23,.10),'nori')
    line('Left arm',[(-1.0,0,1.10),(-1.32,-.08,.83)],.075,'nori')
    pivot=bpy.data.objects.new('Wave_pivot',None); bpy.context.collection.objects.link(pivot); pivot.parent=root; pivot.location=(1.02,0,1.15)
    line('Right waving arm',[(0,0,0),(.33,-.08,.40)],.075,'nori',pivot)
    for dx in (-.10,0,.10): line('Fingers',[(.33,-.08,.40),(.33+dx,-.08,.55)],.035,'nori',pivot)
    if expression in ('surprised','excited'): ball('Open mouth',(0,-.722,1.20),(.13,.035,.16),'nori')
    else:
        sign=-1 if expression in ('sad','angry') else 1
        line('Mouth',[(-.23+i*.046,-.725,1.22-sign*.10*math.sin(i*math.pi/10)) for i in range(11)],.025,'nori')
    scene=bpy.context.scene; scene.render.fps=24; scene.frame_start=1; scene.frame_end=48
    for obj,path in [(root,'location'),(pivot,'rotation_euler')]:
        for f in range(1,50):
            t=(f-1)/48*math.tau
            if path=='location': obj.location.z=.045*math.sin(t)
            else: obj.rotation_euler.y=.35*math.sin(t)
            obj.keyframe_insert(data_path=path,frame=f)
        obj.animation_data.action.name='Idle_bob' if obj==root else 'Wave'
    scene.frame_set(1)
    bpy.ops.object.camera_add(location=(3,-7,3.0)); camera=bpy.context.object
    camera.rotation_euler=(Vector((0,0,1.1))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=4.3; scene.camera=camera
    for loc,power,size in [((0,-4,6),550,4),((-4,-1,3),350,3),((2,3,5),700,3)]:
        bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.data.energy=power; l.data.shape='DISK'; l.data.size=size; l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
    scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=False; scene.render.film_transparent=True
    scene.render.resolution_x=1080; scene.render.resolution_y=1080; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'
    bpy.ops.export_scene.gltf(filepath=str(OUT/f'suki-{expression}.glb'),export_format='GLB',export_cameras=False,export_lights=False,export_apply=True,export_animations=True)
    return scene

def main():
    p=argparse.ArgumentParser(); p.add_argument('--render',action='store_true'); p.add_argument('--expression',choices=EXPRESSIONS); p.add_argument('--animation',action='store_true'); a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    for e in ([a.expression] if a.expression else EXPRESSIONS):
        scene=build(e)
        if e=='happy' or a.expression:
            bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'suki-{e}.blend'))
        if a.render:
            scene.render.filepath=str(OUT/f'suki-{e}.png'); bpy.ops.render.render(write_still=True)
        if a.animation:
            scene.render.filepath=str(OUT/f'{e}-frames/frame-'); bpy.ops.render.render(animation=True)
    print('Suki exports complete.')
if __name__=='__main__': main()
