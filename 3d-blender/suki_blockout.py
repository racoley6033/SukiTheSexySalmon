"""Blender Python: procedural Suki BLOCKOUT. Run from Blender's Scripting workspace."""
import bpy
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, roughness=0.35):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    return m

salmon = material('Salmon coral', (0.95, 0.32, 0.16))
rice = material('Rice', (0.95, 0.92, 0.84))
avocado = material('Avocado', (0.55, 0.73, 0.25))
jalapeno = material('Jalapeno', (0.08, 0.33, 0.09))
sauce = material('Hot sauce', (0.78, 0.04, 0.02), 0.18)
nori = material('Nori limbs', (0.025, 0.055, 0.035))
white = material('Eye whites', (1, 0.98, 0.93))
green = material('Green irises', (0.10, 0.65, 0.20))
pupil = material('Pupils', (0.01, 0.02, 0.01))

def sphere(name, loc, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return obj

def limb(name, start, end, width):
    delta = Vector(end) - Vector(start)
    mid = (Vector(start) + Vector(end)) / 2
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=width, depth=delta.length, location=mid)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(nori)
    bpy.ops.object.shade_smooth()

sphere('Rice base', (0,0,0.9), (1.05,0.60,0.62), rice)
sphere('Salmon nigiri', (0,0,1.35), (1.18,0.72,0.55), salmon)
sphere('Avocado fringe', (0.12,-0.69,1.73), (0.24,0.12,0.52), avocado)
sphere('Jalapeno topping', (0.10,0,1.91), (0.37,0.32,0.10), jalapeno)
sphere('Hot sauce dot', (0.10,-0.03,2.04), (0.12,0.12,0.065), sauce)
for x in (-0.38, 0.38):
    sphere('Eye white', (x,-0.70,1.37), (0.19,0.08,0.24), white)
    sphere('Green iris', (x,-0.78,1.37), (0.115,0.06,0.16), green)
    sphere('Pupil', (x,-0.833,1.37), (0.055,0.027,0.09), pupil)
for side in (-1, 1):
    limb('Nori arm', (side*0.95,0,1.1), (side*1.42,-0.06,0.8), 0.10)
    limb('Nori leg', (side*0.4,0,0.5), (side*0.47,-0.02,0.05), 0.13)

bpy.ops.object.light_add(type='AREA', location=(0,-4,6))
bpy.context.object.data.energy = 650
bpy.ops.object.camera_add(location=(3,-6,3))
camera = bpy.context.object
target = Vector((0,0,1.15))
camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.camera = camera
bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1080
print('Suki blockout generated. Next: refined mesh, materials, mouth, rig and animation.')
