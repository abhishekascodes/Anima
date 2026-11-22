"""Blender batch render script for new ANIMA angles and colorways."""

import math
import bpy
from mathutils import Vector, Euler

# 1. Update Material: Vibrant Cyberpunk Cobalt Blue Lacquer
mat = bpy.data.materials.get("02  |  deep petrol lacquer")
if mat and mat.node_tree:
    for node in mat.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            # Rich, deep electric cobalt blue with smooth clearcoat
            node.inputs["Base Color"].default_value = (0.02, 0.22, 0.82, 1.0)
            node.inputs["Roughness"].default_value = 0.16
            if "Coat Weight" in node.inputs:
                node.inputs["Coat Weight"].default_value = 0.5

# Scene settings
scene = bpy.context.scene
scene.cycles.samples = 20
scene.render.resolution_x = 1350
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100

# Helper function to point camera at a target
def look_at(cam_obj, target_pos):
    direction = target_pos - cam_obj.location
    rot_quat = direction.to_track_quat("-Z", "Y")
    cam_obj.rotation_euler = rot_quat.to_euler()

target = Vector((0.0, 0.0, 0.32))  # Torso center

shots = [
    {
        "name": "ANIMA_Hero_Low_Angle.png",
        "cam_pos": Vector((-0.28, 0.88, 0.22)),  # Low front angle looking up
        "target": Vector((0.0, 0.0, 0.38)),
        "lens": 48.0,
    },
    {
        "name": "ANIMA_Striker_Mechanism_Side.png",
        "cam_pos": Vector((-0.82, 0.32, 0.38)),  # Right striker arm side profile
        "target": Vector((-0.12, 0.0, 0.32)),
        "lens": 55.0,
    },
    {
        "name": "ANIMA_Top_Isometric_Workbench.png",
        "cam_pos": Vector((-0.55, 0.85, 0.82)),  # High 45-degree isometric workbench view
        "target": Vector((0.0, 0.0, 0.25)),
        "lens": 42.0,
    },
    {
        "name": "ANIMA_Head_and_Chest_Portrait.png",
        "cam_pos": Vector((-0.22, 0.62, 0.48)),  # Tight macro on face and illuminated chest
        "target": Vector((0.0, 0.0, 0.46)),
        "lens": 65.0,
    },
]

# Create a dedicated rendering camera
cam_data = bpy.data.cameras.new(name="Render_Cam")
cam_obj = bpy.data.objects.new("Render_Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

for shot in shots:
    cam_obj.location = shot["cam_pos"]
    cam_data.lens = shot["lens"]
    look_at(cam_obj, shot["target"])
    
    out_path = f"//../docs/images/{shot['name']}"
    scene.render.filepath = out_path
    print(f"Rendering {shot['name']} from {cam_obj.location}...")
    bpy.ops.render.render(write_still=True)
    print(f"Finished {shot['name']}")

print("All 4 new angle renders completed successfully!")
