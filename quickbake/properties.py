# pyright: reportInvalidTypeForm=false
import bpy


class QuickBakeToolPropertyGroup(bpy.types.PropertyGroup):
    reuse_tex: bpy.props.BoolProperty(
        name='Re-use Texture',
        description='Use the texture from previous bakes',
        default=True,
    )

    clean_up: bpy.props.BoolProperty(
        name='Clean Up',
        description='Remove generated nodes after baking',
        default=True,
    )

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

    save_img: bpy.props.BoolProperty(
        name='Save Images',
        description='Write images to file after baking',
        default=False,
    )

    image_path: bpy.props.StringProperty(
        name='Texture Path',
        description='Directory for baking output',
        default='',
        subtype='DIR_PATH',
    )

    bake_name: bpy.props.StringProperty(
        name='Name',
        description='Name used fot the baked texture images',
        default='BakeTexture',
    )

    bake_uv: bpy.props.StringProperty(
        name='UV',
        description='Name used fot the uv bake layer',
        default='bake_uv',
    )

    bake_size: bpy.props.IntProperty(
        name='Size',
        description='Resolution for the bake texture',
        default=1024,
        soft_min=1024,
        step=1024,
    )

    diffuse_enabled: bpy.props.BoolProperty(
        name='Diffuse',
        description='Bake the diffuse map',
        default=True,
    )

    normal_enabled: bpy.props.BoolProperty(
        name='Normal',
        description='Bake the normal map',
        default=True,
    )

    roughness_enabled: bpy.props.BoolProperty(
        name='Roughness',
        description='Bake the roughness map',
        default=True,
    )

    ao_enabled: bpy.props.BoolProperty(
        name='Ao',
        description='Bake the Ao map',
        default=False,
    )

    shadow_enabled: bpy.props.BoolProperty(
        name='Shadow',
        description='Bake the Shadow map',
        default=False,
    )

    position_enabled: bpy.props.BoolProperty(
        name='Position',
        description='Bake the Position map',
        default=False,
    )

    uv_enabled: bpy.props.BoolProperty(
        name='Uv',
        description='Bake the Uv map',
        default=False,
    )

    emit_enabled: bpy.props.BoolProperty(
        name='Emit',
        description='Bake the Emit map',
        default=False,
    )

    environment_enabled: bpy.props.BoolProperty(
        name='Environment',
        description='Bake the Environment map',
        default=False,
    )

    glossy_enabled: bpy.props.BoolProperty(
        name='Glossy',
        description='Bake the Glossy map',
        default=False,
    )

    transmission_enabled: bpy.props.BoolProperty(
        name='Transmission',
        description='Bake the Transmission map',
        default=False,
    )
