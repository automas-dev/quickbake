# pyright: reportInvalidTypeForm=false
import bpy

from enum import StrEnum


class MaterialMode(StrEnum):
    IMAGES = "IMAGES"
    CREATE = "CREATE"
    ASSIGN = "ASSIGN"
    COPY = "COPY"


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

    mat_mode: bpy.props.EnumProperty(
        name="Mode",
        description="What to do with images after baking",
        items=[
            (
                MaterialMode.IMAGES,
                "Image Only",
                "Only generate images",
            ),
            (
                MaterialMode.CREATE,
                "Create Material",
                "Create a new material with the baked images",
            ),
            (
                MaterialMode.ASSIGN,
                "Assign material",
                "Assign the material to active object",
            ),
            (
                MaterialMode.COPY,
                "Copy Object",
                "Make a copy of the object with baked material assigned",
            ),
        ],
        default="ASSIGN",
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
