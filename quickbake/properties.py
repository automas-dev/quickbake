# pyright: reportInvalidTypeForm=false
import bpy

from enum import StrEnum


class QuickBakeToolPropertyGroup(bpy.types.PropertyGroup):
    # Bake

    bake_name: bpy.props.StringProperty(
        name="Name",
        description="Name used for the baked texture images",
        default="Bake",
    )

    bake_size: bpy.props.IntProperty(
        name="Size",
        description="Resolution for the bake texture",
        default=1024,
        soft_min=1024,
        step=1024,  # not yet implemented
    )

    use_mat: bpy.props.BoolProperty(
        name="Assign Material",
        description="Assign new material with baked textures to the selected object",
        default=True,
    )

    save_img: bpy.props.BoolProperty(
        name="Save Images",
        description="Save images to a folder",
        default=False,
    )

    save_path: bpy.props.StringProperty(
        name="Output Directory",
        description="Directory for baking output",
        default="",
        subtype="DIR_PATH",
    )

    # Layers

    diffuse_enabled: bpy.props.BoolProperty(
        name="Diffuse", description="Bake the Diffuse map", default=True
    )

    roughness_enabled: bpy.props.BoolProperty(
        name="Roughness", description="Bake the Roughness map", default=True
    )

    normal_enabled: bpy.props.BoolProperty(
        name="Normal", description="Bake the Normal map", default=True
    )

    glossy_enabled: bpy.props.BoolProperty(
        name="Glossy", description="Bake the Glossy map", default=False
    )

    transmission_enabled: bpy.props.BoolProperty(
        name="Transmission", description="Bake the Transmission map", default=False
    )

    emit_enabled: bpy.props.BoolProperty(
        name="Emission", description="Bake the Emission map", default=False
    )

    ao_enabled: bpy.props.BoolProperty(
        name="Ambient Occlusion",
        description="Bake the Ambient Occlusion map",
        default=False,
    )

    shadow_enabled: bpy.props.BoolProperty(
        name="Shadow", description="Bake the Shadow map", default=False
    )

    environment_enabled: bpy.props.BoolProperty(
        name="Environment", description="Bake the Environment map", default=False
    )

    position_enabled: bpy.props.BoolProperty(
        name="Position", description="Bake the Position map", default=False
    )

    uv_enabled: bpy.props.BoolProperty(
        name="UV", description="Bake the UV map", default=False
    )
