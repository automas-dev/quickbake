import logging

import bpy

from .op import RENDER_OT_bake
from .panel import RENDER_PT_main
from .properties import QuickBakeToolPropertyGroup
from .util import is_development, enable_logging
from .preferences import QuickBakeAddonPreferences


_log = logging.getLogger(__package__)

if is_development():
    enable_logging()


def register():
    _log.debug("Register extension")
    bpy.utils.register_class(RENDER_OT_bake)
    bpy.utils.register_class(RENDER_PT_main)
    bpy.utils.register_class(QuickBakeToolPropertyGroup)
    bpy.utils.register_class(QuickBakeAddonPreferences)
    bpy.types.Scene.QuickBakeToolPropertyGroup = bpy.props.PointerProperty(  # type: ignore
        type=QuickBakeToolPropertyGroup
    )


def unregister():
    _log.debug("Unregister extension")
    bpy.utils.unregister_class(RENDER_OT_bake)
    bpy.utils.unregister_class(RENDER_PT_main)
    bpy.utils.unregister_class(QuickBakeToolPropertyGroup)
    bpy.utils.unregister_class(QuickBakeAddonPreferences)
    del bpy.types.Scene.QuickBakeToolPropertyGroup  # type: ignore


if __name__ == "__main__":
    register()
