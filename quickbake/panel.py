"""QuickBake n Menu."""

import bpy
from .op import RENDER_OT_bake


class RENDER_PT_main(bpy.types.Panel):
    """Creates a Sub-Panel in the Property Area of the 3D View."""

    bl_label = "Quick Bake"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_context = "objectmode"

    def draw(self, context):
        """Override Panel draw method."""
        layout = self.layout
        scene = context.scene

        # Make types happy
        assert layout is not None, "Missing layout from parent Panel"
        assert scene is not None, "Missing scene from context"

        props = scene.QuickBakeToolPropertyGroup  # type: ignore

        layout.prop(props, "bake_name")
        layout.prop(props, "bake_size")
        layout.prop(props, "uv_name")
        layout.prop(props, "unwrap_object")
        layout.prop(props, "mat_mode")
        layout.prop(props, "save_img")

        row = layout.row()
        row.enabled = props.save_img
        row.prop(props, "save_path", text="")

        # This is the bake button
        layout.operator(RENDER_OT_bake.bl_idname)

        layout.separator()
        layout.label(text="Layers")

        layout.prop(props, "diffuse_enabled")
        layout.prop(props, "roughness_enabled")
        layout.prop(props, "normal_enabled")
        layout.prop(props, "glossy_enabled")
        layout.prop(props, "transmission_enabled")
        layout.prop(props, "emit_enabled")
        if props.emit_enabled:
            layout.prop(props, "emit_strength")
        layout.prop(props, "ao_enabled")
        layout.prop(props, "shadow_enabled")
        layout.prop(props, "environment_enabled")
        layout.prop(props, "position_enabled")
        layout.prop(props, "uv_enabled")
