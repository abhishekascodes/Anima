# render facial expressions in blender

import math
import bpy
from mathutils import Vector, Euler

# 1. Update Material: Cobalt Blue Lacquer
mat = bpy.data.materials.get("02  |  deep petrol lacquer")
if mat and mat.node_tree:
    for node in mat.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            node.inputs["Base Color"].default_value = (0.02, 0.22, 0.82, 1.0)
            node.inputs["Roughness"].default_value = 0.16

# 2. Scene setup
scene = bpy.context.scene
scene.cycles.samples = 22
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100

# Portrait camera framing the head and upper torso
cam_data = bpy.data.cameras.new(name="Emotion_Cam")
cam_obj = bpy.data.objects.new("Emotion_Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

cam_obj.location = Vector((-0.18, 0.58, 0.50))
cam_data.lens = 68.0

# Look at face center
target = Vector((0.0, 0.04, 0.49))
direction = target - cam_obj.location
rot_quat = direction.to_track_quat("-Z", "Y")
cam_obj.rotation_euler = rot_quat.to_euler()

# Objects
b0 = bpy.data.objects.get("Optic | brow ridge")
b1 = bpy.data.objects.get("Optic | brow ridge.001")
p0 = bpy.data.objects.get("Optic | pupil")
p1 = bpy.data.objects.get("Optic | pupil.001")
ring0 = bpy.data.objects.get("Optic | amber annulus")
ring1 = bpy.data.objects.get("Optic | amber annulus.001")
glint0 = bpy.data.objects.get("Optic | aperture glint")
glint1 = bpy.data.objects.get("Optic | aperture glint.001")

# Store original brow points
orig_b0 = [pt.co.copy() for pt in b0.data.splines[0].bezier_points]
orig_b1 = [pt.co.copy() for pt in b1.data.splines[0].bezier_points]

def reset_face():
    for i, pt in enumerate(b0.data.splines[0].bezier_points):
        pt.co = orig_b0[i].copy()
    for i, pt in enumerate(b1.data.splines[0].bezier_points):
        pt.co = orig_b1[i].copy()
    for p in [p0, p1, ring0, ring1]:
        p.scale = Vector((1.0, 1.0, 1.0))
        p.rotation_euler = Euler((0.0, 0.0, 0.0))

emotions = [
    {
        "name": "ANIMA_Emotion_Focused_Countdown.png",
        "setup": lambda: (
            # Furrow inner brows downward for focused game mode
            setattr(b0.data.splines[0].bezier_points[2].co, "z", orig_b0[2].z - 0.007),
            setattr(b0.data.splines[0].bezier_points[0].co, "z", orig_b0[0].z + 0.003),
            setattr(b1.data.splines[0].bezier_points[0].co, "z", orig_b1[0].z - 0.007),
            setattr(b1.data.splines[0].bezier_points[2].co, "z", orig_b1[2].z + 0.003),
            setattr(p0, "scale", Vector((0.9, 0.9, 0.9))),
            setattr(p1, "scale", Vector((0.9, 0.9, 0.9))),
        )
    },
    {
        "name": "ANIMA_Emotion_Smug_Victory_Wink.png",
        "setup": lambda: (
            # Right brow raised high, left brow arched smugly
            setattr(b0.data.splines[0].bezier_points[1].co, "z", orig_b0[1].z + 0.006),
            setattr(b0.data.splines[0].bezier_points[2].co, "z", orig_b0[2].z + 0.005),
            # Wink left eye (scale pupil and ring down to a wink slit)
            setattr(p1, "scale", Vector((1.2, 0.2, 0.2))),
            setattr(ring1, "scale", Vector((1.1, 0.2, 0.2))),
        )
    },
    {
        "name": "ANIMA_Emotion_Shocked_Defeat.png",
        "setup": lambda: (
            # Sad / surprised: inner brows raised high, outer brows drooped
            setattr(b0.data.splines[0].bezier_points[2].co, "z", orig_b0[2].z + 0.008),
            setattr(b0.data.splines[0].bezier_points[0].co, "z", orig_b0[0].z - 0.005),
            setattr(b1.data.splines[0].bezier_points[0].co, "z", orig_b1[0].z + 0.008),
            setattr(b1.data.splines[0].bezier_points[2].co, "z", orig_b1[2].z - 0.005),
            # Wide pupils
            setattr(p0, "scale", Vector((1.25, 1.25, 1.25))),
            setattr(p1, "scale", Vector((1.25, 1.25, 1.25))),
        )
    },
    {
        "name": "ANIMA_Emotion_Happy_Curious.png",
        "setup": lambda: (
            # Gentle lifted friendly brows
            setattr(b0.data.splines[0].bezier_points[1].co, "z", orig_b0[1].z + 0.005),
            setattr(b1.data.splines[0].bezier_points[1].co, "z", orig_b1[1].z + 0.005),
        )
    }
]

for emo in emotions:
    reset_face()
    emo["setup"]()
    out_path = f"//../docs/images/{emo['name']}"
    scene.render.filepath = out_path
    print(f"Rendering emotion: {emo['name']}...")
    bpy.ops.render.render(write_still=True)
    print(f"Finished {emo['name']}")

reset_face()
print("All facial emotions rendered successfully!")
