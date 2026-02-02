# pyright: reportInvalidTypeForm=false
import bpy


class QuickBakeToolPropertyGroup(bpy.types.PropertyGroup):
    # Bake

    bake_name: bpy.props.StringProperty(
        name='Name',
        description='Name used for the baked texture images',
        default='BakeTexture',
    )

    bake_uv: bpy.props.StringProperty(
        name='UV',
        description='Name used for the uv bake layer',
        default='bake_uv',
    )

    bake_size: bpy.props.IntProperty(
        name='Size',
        description='Resolution for the bake texture',
        default=1024,
        soft_min=1024,
        step=1024,  # not yet implemented
    )

    combine_arm: bpy.props.BoolProperty(
        name='Combine ARM Images',
        description='Combine ambient occlusion, roughness and metallic into a single image',
        default=False,
    )

    save_img: bpy.props.BoolProperty(
        name='Save Images',
        description='Write images to file after baking',
        default=False,
    )

    image_path: bpy.props.StringProperty(
        name='Image Path',
        description='Directory for baking output',
        default='',
        subtype='DIR_PATH',
    )

    # Material

    create_mat: bpy.props.BoolProperty(
        name='Create Material',
        description='Create a material after baking and assign it.',
        default=True,
    )

    mat_name: bpy.props.StringProperty(
        name='Name',
        description='Name used to create a new material after baking',
        default='BakeMaterial',
    )

    # Layers

    """Godot mapping
    Diffuse -> Albedo
    -> Metallic
    -> Roughness
    -> Normal
    -> Clearcoat
    -> Anisotropy
    -> Ambient Occlusion
    -> Height
    -> Subsurface Scatter
    TODO IOR? -> Refraction
    -> Emission
    Alpha -> Transparency
    Transmission -> None

    TODO - ARM
    """

    diffuse_enabled: bpy.props.BoolProperty(
        name='Diffuse',
        description='Bake the diffuse map',
        default=True,
    )

    roughness_enabled: bpy.props.BoolProperty(
        name='Roughness',
        description='Bake the roughness map',
        default=True,
    )

    normal_enabled: bpy.props.BoolProperty(
        name='Normal',
        description='Bake the normal map',
        default=True,
    )

    metallic_enabled: bpy.props.BoolProperty(
        name='Metallic',
        description='Bake the metallic map',
        default=False,
    )

    clearcoat_enabled: bpy.props.BoolProperty(
        name='Clearcoat',
        description='Bake the clearcoat map',
        default=False,
    )

    anisotropic_enabled: bpy.props.BoolProperty(
        name='Anisotropic',
        description='Bake the anisotropic map',
        default=False,
    )

    ao_enabled: bpy.props.BoolProperty(
        name='Ambient Occlusion',
        description='Bake the ambient occlusion map',
        default=False,
    )

    # TODO is this real?
    shadow_enabled: bpy.props.BoolProperty(
        name='Shadow',
        description='Bake the shadow map',
        default=False,
    )

    height_enabled: bpy.props.BoolProperty(
        name='Height',
        description='Bake the height map',
        default=False,
    )

    emit_enabled: bpy.props.BoolProperty(
        name='Emit',
        description='Bake the Emit map',
        default=False,
    )

    transmission_enabled: bpy.props.BoolProperty(
        name='Transmission',
        description='Bake the Transmission map',
        default=False,
    )
