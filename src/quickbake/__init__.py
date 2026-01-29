import bpy

from .op import QuickBake_OT_bake
from .panel import QuickBake_PT_main
from .properties import QuickBakeToolPropertyGroup

# the value DEV_BUILD is replaced with the version string by ci
version_str = '0.0.1'.strip('v').split('-', 1)[0]
version_tuple = tuple(map(int, version_str.split('.')))

bl_info = {
    'name': 'Quick Bake',
    'author': 'Thomas Harrison',
    'description': 'Fast baking for blender',
    'blender': (2, 80, 0),
    'version': version_tuple,
    'location': '',
    'warning': '',
    'category': 'Render',
}


def register():
    bpy.utils.register_class(QuickBake_OT_bake)
    bpy.utils.register_class(QuickBake_PT_main)
    bpy.utils.register_class(QuickBakeToolPropertyGroup)
    bpy.types.Scene.QuickBakeToolPropertyGroup = bpy.props.PointerProperty(
        type=QuickBakeToolPropertyGroup
    )


def unregister():
    bpy.utils.unregister_class(QuickBake_OT_bake)
    bpy.utils.unregister_class(QuickBake_PT_main)
    bpy.utils.unregister_class(QuickBakeToolPropertyGroup)
    del bpy.types.Scene.QuickBakeToolPropertyGroup


if __name__ == '__main__':
    register()
