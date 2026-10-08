"""Re-import the .fbx in a clean Blender scene and report names, sizes, materials, texture filter."""
import bpy, sys, mathutils
fbx = sys.argv[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.scale_length = 0.01
bpy.ops.import_scene.fbx(filepath=fbx)
for o in bpy.data.objects:
    if o.type != 'MESH': print('EMPTY', o.name, 'children', [c.name for c in o.children]); continue
    ws = [o.matrix_world @ v.co for v in o.data.vertices]
    lo = mathutils.Vector([min(w[i] for w in ws) for i in range(3)]); hi = mathutils.Vector([max(w[i] for w in ws) for i in range(3)])
    mats = [m.name for m in o.data.materials]
    tex = [(n.image.name if n.image else None, n.interpolation) for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type == 'TEX_IMAGE']
    print('MESH', o.name, 'parent', o.parent.name if o.parent else None, 'tris', sum(len(p.vertices) - 2 for p in o.data.polygons),
          'size(BU)', tuple(round(x, 4) for x in (hi - lo)), 'mats', mats, 'tex', tex)
