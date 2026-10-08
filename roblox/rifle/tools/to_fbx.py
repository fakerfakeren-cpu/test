"""Blender (bpy) conversion: .glb -> binary .fbx. 1 FBX unit = 1 stud (UnitScaleFactor 1), Y up, muzzle -Z,
axis conversion baked into the geometry, palette texture embedded with Closest filtering."""
import bpy, sys
glb, fbx = sys.argv[1], sys.argv[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
for img in bpy.data.images:
    img.pack() if img.packed_file is None else None
for m in bpy.data.materials:
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type == 'TEX_IMAGE': n.interpolation = 'Closest'
us = bpy.context.scene.unit_settings
us.system = 'METRIC'; us.scale_length = 0.01          # 1 Blender unit written as 1 cm-unit = 1 stud in Roblox
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=False, object_types={'EMPTY', 'MESH'},
    apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE', global_scale=1.0,
    axis_forward='-Z', axis_up='Y', bake_space_transform=True,
    mesh_smooth_type='OFF', use_mesh_modifiers=False, add_leaf_bones=False, bake_anim=False,
    path_mode='COPY', embed_textures=True)
print('OBJECTS', [(o.name, o.type, o.parent.name if o.parent else None) for o in bpy.data.objects])
