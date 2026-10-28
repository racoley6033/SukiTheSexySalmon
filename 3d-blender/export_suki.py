"""Blender 4.3+: build Suki, export expression GLBs and a transparent render.
blender --background --python 3d-blender/export_suki.py -- --render
"""
import argparse, json, math, random, sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/3d'; OUT.mkdir(parents=True,exist_ok=True)
EXPRESSIONS=tuple(json.loads((ROOT/'character.json').read_text())['expressions'])

def material(name,color):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=.4
    return m

def build(expression):
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    colors={'salmon':(1,.15,.025),'skin':(1,.52,.25),'rice':(.96,.90,.76),'stripe':(1,.71,.45),'avocado':(.59,.76,.17),'jalapeno':(.12,.25,.014),'seed':(1,.79,.35),'sauce':(.85,.035,.005),'nori':(.006,.012,.007),'white':(1,.98,.90),'iris':(.19,.36,.015),'irislight':(.40,.64,.035),'pink':(.97,.19,.16),'blush':(.85,.07,.05),'brow':(.26,.062,.013),'mouth':(.22,.013,.009),'tongue':(1,.17,.20),'sole':(.012,.018,.008)}
    palette={k:material(k,v) for k,v in colors.items()}
    for name in ('nori','salmon','sauce','jalapeno'):
        bs=palette[name].node_tree.nodes.get('Principled BSDF'); bs.inputs['Roughness'].default_value=.23 if name!='sauce' else .13
        bs.inputs['Coat Weight'].default_value=.25
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
    # Suki: round salmon bob around a separate peach face, never a fish block.
    ball('Salmon bob volume',(0,.12,2.20),(1.13,.76,1.01),'salmon')
    ball('Peach face',(0,-.49,2.04),(.91,.48,.75),'skin')
    ball('Rice collar core',(0,.04,1.30),(.89,.57,.26),'rice')
    random.seed(21)
    for row in range(4):
        z=1.14+row*.11
        for i in range(24):
            angle=i*math.tau/24+(row%2)*.12
            x=.86*math.cos(angle); y=.52*math.sin(angle)
            o=ball(f'Rice grain {row:02}-{i:02}',(x,y,z+random.uniform(-.025,.025)),(.115,.085,.095),'rice')
            o.rotation_euler=(random.random()*.4,random.random()*.5,random.random()*2)
    def bezier(points,t):
        a,b,c,d=map(Vector,points)
        return (1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d
    def lock(name,points,width,depth):
        # Tapered closed mesh following a cubic arc, flattened as a salmon slice.
        vertices=[]; faces=[]; rows=25; sides=16
        for i in range(rows):
            t=i/(rows-1); center=bezier(points,t)
            tangent=bezier(points,min(t+.01,1))-bezier(points,max(t-.01,0))
            across=Vector((tangent.z,0,-tangent.x)).normalized()
            taper=max(.035,math.sin(math.pi*(.03+.94*t))**.55)
            for j in range(sides):
                theta=j/sides*math.tau
                p=center+across*(width*taper*math.cos(theta))+Vector((0,depth*taper*math.sin(theta),0))
                vertices.append(tuple(p))
        for i in range(rows-1):
            for j in range(sides):
                a=i*sides+j; b=i*sides+(j+1)%sides; faces.append((a,b,b+sides,a+sides))
        faces.extend([tuple(range(sides-1,-1,-1)),tuple((rows-1)*sides+j for j in range(sides))])
        mesh=bpy.data.meshes.new(name); mesh.from_pydata(vertices,[],faces); mesh.update()
        o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.parent=root; o.data.materials.append(palette['salmon'])
        for p in mesh.polygons:p.use_smooth=True
        # Ivory bands sit on the salmon surface rather than raised tube stripes.
        for k in (.26,.43,.62,.78):
            bandverts=[]; bandfaces=[]
            for j in range(19):
                u=-.88+j*1.76/18
                for edge in (-1,1):
                    t=k+.035*u+edge*.009
                    c=bezier(points,t)
                    tangent=bezier(points,min(t+.01,1))-bezier(points,max(t-.01,0))
                    across=Vector((tangent.z,0,-tangent.x)).normalized()
                    taper=max(.035,math.sin(math.pi*(.03+.94*t))**.55)
                    p=c+across*(width*taper*u)+Vector((0,-depth*taper*math.sqrt(1-u*u)-.004,0))
                    bandverts.append(tuple(p))
            for j in range(18):
                a=j*2; bandfaces.append((a,a+1,a+3,a+2))
            bm=bpy.data.meshes.new(name+' marbling'); bm.from_pydata(bandverts,[],bandfaces); bm.update()
            band=bpy.data.objects.new(name+' ivory marbling',bm); bpy.context.collection.objects.link(band); band.parent=root; band.data.materials.append(palette['stripe'])
            for p in bm.polygons:p.use_smooth=True
    lock('Left side salmon curl',[(-.66,-.30,2.91),(-1.25,-.50,2.75),(-1.31,-.59,1.65),(-.88,-.61,1.57)],.24,.16)
    lock('Left cheek salmon curl',[(-.72,-.42,2.68),(-1.09,-.67,2.55),(-1.15,-.69,1.72),(-.91,-.68,1.62)],.18,.12)
    lock('Right side salmon curl',[(.55,-.32,3.00),(1.15,-.41,2.80),(1.31,-.40,1.75),(.84,-.55,1.60)],.28,.17)
    lock('Right cheek salmon curl',[(.69,-.57,2.73),(1.03,-.61,2.54),(1.17,-.58,1.88),(.90,-.61,1.69)],.18,.11)
    lock('Sweeping salmon fringe',[(.40,-.42,3.02),(.04,-.91,3.05),(-.72,-.88,2.89),(-.99,-.70,2.47)],.25,.14)
    lock('Lower salmon fringe',[(.40,-.62,2.88),(.02,-1.02,2.92),(-.60,-.98,2.68),(-.72,-.86,2.54)],.17,.09)
    # Broad perpendicular avocado, tapered tip stops between the eyebrows.
    verts=[]; faces=[]; rows=30; cols=12
    for i in range(rows):
        t=i/(rows-1); y=.47-1.47*t; z=3.16-.57*t**3
        width=.29*(1-.93*t**6)
        for j in range(cols):
            u=-1+2*j/(cols-1); verts.append((.17+u*width,y,z+.075*(1-u*u)))
    for i in range(rows-1):
        for j in range(cols-1):
            a=i*cols+j; faces.append((a,a+1,a+1+cols,a+cols))
    mesh=bpy.data.meshes.new('Perpendicular avocado mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    avo=bpy.data.objects.new('Avocado forehead slice',mesh); bpy.context.collection.objects.link(avo); avo.parent=root; avo.data.materials.append(palette['avocado'])
    solid=avo.modifiers.new('Slice thickness','SOLIDIFY'); solid.thickness=.045
    for p in mesh.polygons:p.use_smooth=True
    bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=16,major_radius=.28,minor_radius=.075,location=(.17,-.02,3.27))
    hat=bpy.context.object; hat.name='Jalapeno seeded ring'; hat.parent=root; hat.data.materials.append(palette['jalapeno'])
    for p in hat.data.polygons:p.use_smooth=True
    ball('Jalapeno inner flesh',(.17,-.02,3.26),(.25,.25,.045),'avocado')
    for i in range(9):
        a=i*math.tau/9; o=ball('Jalapeno cream seed',(.17+.17*math.cos(a),-.02+.17*math.sin(a),3.31),(.075,.035,.020),'seed'); o.rotation_euler.z=a
    ball('One hot sauce dot',(.17,-.02,3.38),(.12,.12,.105),'sauce')
    # Eyes are mounted on the peach face with lashes and layered green irises.
    for side in (-1,1):
        x=side*.43; eyey=-.921
        closed=expression in ('flirty','excited','sleepy') or (expression=='wink' and side==1)
        if closed:
            line('Closed eyelid',[(x-.24+i*.048,eyey,2.22+.10*math.sin(i*math.pi/10)) for i in range(11)],.028,'nori')
        elif expression=='love':
            ball('Heart lobe',(x-.08,eyey,2.23),(.11,.035,.12),'pink'); ball('Heart lobe',(x+.08,eyey,2.23),(.11,.035,.12),'pink')
            line('Heart eye tip',[(x-.14,eyey,2.22),(x,eyey,2.00),(x+.14,eyey,2.22)],.06,'pink')
        else:
            ball('Eye white',(x,-.887,2.20),(.265,.095,.30),'white')
            ball('Green iris',(x+.015,-.976,2.19),(.18,.045,.225),'iris')
            ball('Iris inner green',(x+.02,-1.013,2.16),(.125,.025,.17),'irislight')
            ball('Pupil',(x+.018,-1.036,2.20),(.085,.025,.143),'nori')
            ball('Eye large highlight',(x-.04,-1.058,2.31),(.060,.012,.060),'white')
            ball('Eye small highlight',(x+.09,-1.053,2.12),(.025,.012,.025),'white')
            line('Upper eyeliner',[(x-.255+i*.051,-.968,2.23+.25*math.sin(i*math.pi/10)) for i in range(11)],.027,'nori')
            if expression=='sassy': ball('Sassy upper eyelid',(x,-.998,2.40),(.255,.035,.13),'skin')
        for i in range(3):
            lx=x+side*(.13+i*.055); z=2.40-i*.032
            if closed: z=2.27-i*.008
            line('Long black eyelash',[(lx,-.965,z),(lx+side*.07,-.98,z+.05),(lx+side*.10,-.975,z+.13)],.024,'nori')
        browz=2.61
        line('Brow',[(x-.15+i*.03,-.85,browz+.055*math.sin(i*math.pi/10)+(side*(i-5)*.012 if expression=='angry' else 0)) for i in range(11)],.021,'brow')
        ball('Rosy cheek',(side*.65,-.858,1.91),(.21,.027,.10),'pink')
        for d in (-.05,.02,.09): line('Cheek accent',[(side*.65+d,-.89,1.91),(side*.65+d+.025,-.89,1.95)],.008,'blush')
    ball('Tiny nose',(0,-.98,1.99),(.065,.045,.03),'skin')
    if expression=='surprised':
        ball('Surprised mouth',(0,-.928,1.77),(.13,.035,.18),'mouth'); ball('Tongue',(0,-.962,1.68),(.08,.012,.055),'tongue')
    elif expression in ('sad','angry','sleepy','sassy','flirty'):
        sign=-1 if expression in ('sad','angry') else 1
        line('Expression mouth',[(-.18+i*.036,-.952,1.79-sign*.065*math.sin(i*math.pi/10)+(i*.006 if expression in ('sassy','flirty') else 0)) for i in range(11)],.020,'mouth')
    else:
        ball('Joyful open mouth',(0,-.922,1.78),(.25,.045,.18),'mouth')
        ball('Smile teeth',(0,-.965,1.88),(.21,.017,.045),'white')
        ball('Smile tongue',(.04,-.967,1.69),(.13,.017,.065),'tongue')
    # Articulated nori limbs with real glove fingers and chunky cuffed boots.
    for side in (-1,1):
        x=side*.36
        line('Nori leg',[(x,.02,1.15),(side*.42,-.02,.70),(side*.48,-.10,.35)],.085,'nori')
        ball('Boot cuff',(side*.48,-.10,.38),(.18,.18,.14),'nori')
        ball('Boot upper',(side*.49,-.16,.23),(.19,.26,.20),'nori')
        ball('Boot toe',(side*.54,-.31,.17),(.24,.30,.14),'nori')
        ball('Boot sole',(side*.53,-.25,.075),(.26,.35,.055),'sole')
    pivot=bpy.data.objects.new('Wave_pivot',None); bpy.context.collection.objects.link(pivot); pivot.parent=root; pivot.location=(1.0,-.20,1.57)
    line('Right nori arm',[(0,0,0),(.25,-.20,-.04),(.39,-.38,.26)],.075,'nori',pivot)
    ball('Right glove palm',(.39,-.38,.35),(.145,.10,.16),'nori',pivot)
    for i in range(4):
        x=.27+i*.078
        ball('Right glove finger',(x,-.39,.50+(1-abs(i-1.5)/2)*.05),(.047,.06,.11),'nori',pivot)
    ball('Right thumb',(.24,-.43,.34),(.085,.065,.065),'nori',pivot)
    line('Left bent arm',[(-.96,-.18,1.52),(-1.16,-.38,1.41),(-1.35,-.65,1.80)],.08,'nori')
    ball('Left glove cuff',(-1.35,-.65,1.78),(.14,.11,.09),'nori')
    ball('Peace glove palm',(-1.36,-.69,1.96),(.17,.11,.18),'nori')
    # Raised two fingers make the signature peace sign from the sheet.
    line('Peace finger left',[(-1.43,-.69,2.03),(-1.53,-.70,2.24),(-1.53,-.70,2.31)],.057,'nori')
    line('Peace finger right',[(-1.32,-.69,2.05),(-1.23,-.70,2.25),(-1.21,-.70,2.31)],.057,'nori')
    for dx,dz in [(-.10,-.03),(.025,-.06),(.12,.01)]: ball('Folded glove finger',(-1.36+dx,-.79,1.98+dz),(.075,.055,.075),'nori')
    scene=bpy.context.scene; scene.render.fps=24; scene.frame_start=1; scene.frame_end=48
    for obj,path in [(root,'location'),(pivot,'rotation_euler')]:
        for f in range(1,50):
            t=(f-1)/48*math.tau
            if path=='location': obj.location.z=.045*math.sin(t)
            else: obj.rotation_euler.y=.35*math.sin(t)
            obj.keyframe_insert(data_path=path,frame=f)
        obj.animation_data.action.name='Idle_bob' if obj==root else 'Wave'
    scene.frame_set(1)
    bpy.ops.object.camera_add(location=(3,-8,3.5)); camera=bpy.context.object
    camera.rotation_euler=(Vector((0,0,1.75))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=4.5; scene.camera=camera
    for loc,power,size in [((0,-4,6),550,4),((-4,-1,3),350,3),((2,3,5),700,3)]:
        bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.data.energy=power; l.data.shape='DISK'; l.data.size=size; l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
    scene.world.color=(.25,.25,.25); scene.render.engine='CYCLES'; scene.cycles.samples=48; scene.cycles.use_denoising=False; scene.render.film_transparent=True
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
