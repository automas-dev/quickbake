"""QuickBake n Menu."""

import bpy
from .op import RENDER_OT_bake
from .properties import SaveMode


class RENDER_PT_main(bpy.types.Panel):
    """Creates a Sub-Panel in the Property Area of the 3D View."""

    bl_label = "Quick Bake"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # bl_category = 'Tool'
    bl_category = "Item"  # TODO revert this after testing
    bl_context = "objectmode"

    def draw(self, context):
        """Override Panel draw method."""
        layout = self.layout
        scene = context.scene

        # Make types happy
        assert layout is not None, "Missing layout from parent Panel"
        assert scene is not None, "Missing scene from context"

        props = scene.QuickBakeToolPropertyGroup  # type: ignore

        # This is the bake button
        row = layout.row()
        row.operator(RENDER_OT_bake.bl_idname)
        row.enabled = not RENDER_OT_bake.active

        if RENDER_OT_bake.active:
            layout.progress(text=f"{RENDER_OT_bake.progress}%", factor=0.0)

        layout.prop(props, "bake_name")

        # col = layout.column(align=True)
        # split = col.split(factor=0.25, align=True)
        # split.label(text="Name")
        # split.prop(props, "bake_name", text="")

        layout.prop(props, "bake_uv")
        # Probably not useful, select from list of existing uv maps
        # me = context.object.data
        # row.template_list("MESH_UL_uvmaps", "uvmaps", me, "uv_layers", me.uv_layers, "active_index", rows=2)

        layout.prop(props, "bake_size")

        # row = layout.row()
        # row.prop(props, "combine_arm")

        layout.prop(props, "save_mode")

        row = layout.row()
        row.enabled = props.save_mode == SaveMode.EXTERNAL
        row.prop(props, "save_path")

        layout.prop(props, "bake_mode")

        # layout.prop(props, "create_mat")

        # row = layout.row()
        # row.enabled = props.create_mat
        # row.prop(props, "replace_mat")

        layout.separator()
        layout.label(text="Layers")

        layout.prop(props, "diffuse_enabled")
        layout.prop(props, "roughness_enabled")
        layout.prop(props, "normal_enabled")

        row = layout.row()
        row.enabled = False
        row.prop(props, "metallic_enabled")

        row = layout.row()
        row.enabled = False
        row.prop(props, "clearcoat_enabled")

        row = layout.row()
        row.enabled = False
        row.prop(props, "anisotropic_enabled")

        row = layout.row()
        row.enabled = False
        row.prop(props, "ao_enabled")

        row = layout.row()
        row.enabled = False
        row.prop(props, "shadow_enabled")

        row = layout.row()
        row.enabled = False
        row.prop(props, "height_enabled")

        row = layout.row()
        row.enabled = False
        row.prop(props, "emit_enabled")

        row = layout.row()
        row.enabled = False
        row.prop(props, "transmission_enabled")
