import bpy

from .op import RENDER_OT_bake
from .panel import RENDER_PT_main
from .properties import QuickBakeToolPropertyGroup


def register():
    bpy.utils.register_class(RENDER_OT_bake)
    bpy.utils.register_class(RENDER_PT_main)
    bpy.utils.register_class(QuickBakeToolPropertyGroup)
    bpy.types.Scene.QuickBakeToolPropertyGroup = bpy.props.PointerProperty(  # type: ignore
        type=QuickBakeToolPropertyGroup
    )


def unregister():
    bpy.utils.unregister_class(RENDER_OT_bake)
    bpy.utils.unregister_class(RENDER_PT_main)
    bpy.utils.unregister_class(QuickBakeToolPropertyGroup)
    del bpy.types.Scene.QuickBakeToolPropertyGroup  # type: ignore


if __name__ == "__main__":
    register()
