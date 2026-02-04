"""Baking helper functions."""

import typing

if typing.TYPE_CHECKING:
    from .op import RENDER_OT_bake

import bpy
from bpy_extras.node_shader_utils import PrincipledBSDFWrapper

from .properties import BakeMode, SaveMode


class MaterialBaker:
    layer_input_map = {
        # From bpy types
        # "COMBINED",  # Combined.
        # "AO",  # Ambient Occlusion.
        # "SHADOW",  # Shadow.
        # "POSITION",  # Position.
        # "NORMAL",  # Normal.
        # "UV",  # UV.
        # "ROUGHNESS",  # ROUGHNESS.
        # "EMIT",  # Emission.
        # "ENVIRONMENT",  # Environment.
        # "DIFFUSE",  # Diffuse.
        # "GLOSSY",  # Glossy.
        # "TRANSMISSION",  # Transmission.
        # Old
        "DIFFUSE": "Base Color",
        "ROUGHNESS": "Roughness",
        "NORMAL": "Normal",
        "METALLIC": "Metallic",
        # "SPECULAR": "Specular IOR Level",
        # "ALPHA": "Alpha",
        # "EMISSION": "Emission",
    }

    def __init__(
        self,
        op: "RENDER_OT_bake",
        obj: bpy.types.Object,
        material_name: str,
        resolution: int,
        bake_mode: BakeMode,
        save_mode: SaveMode,
        save_path: str | None = None,
    ):
        """

        Args:
            op (QuickBake_OT_bake): operator instance for access to report
            obj (Object): object being baked
            material_name(str): name of existing material on object to be baked
            bake_mode (BakeMode): what to do with baked images
            save_mode (SaveMode): where to save baked images
            save_path (str, optional): where to save images if save mode is EXTERNAL

        """
        self.op = op
        self.obj = obj  # TODO THIS IS REALLY BAD, MAYBE?
        self.material_name = material_name
        self.resolution = resolution
        self.bake_mode = bake_mode
        self.save_mode = save_mode
        self.save_path = save_path

        # layer : image
        self.images = {}  # TODO THIS IS REALLY BAD, MAYBE?
        self.bake_uv = None  # TODO THIS IS REALLY BAD, MAYBE?
        # (material, texture node)
        self._bake_nodes = []  # TODO THIS IS REALLY BAD, MAYBE?
        self._material = None  # TODO THIS IS REALLY BAD, MAYBE?
        self._curr_img = None

    def cleanup(self):
        for mat, node in self._bake_nodes:
            mat.node_tree.nodes.remove(node)
        self._bake_nodes.clear()

    def layer_done(self):
        return self._curr_img is not None and self._curr_img.is_dirty

    def start_layer(self, layer: str):
        self._curr_img = None
        layer = layer.upper()

        uv = self._unwrap_object()
        self._setup_bake_nodes()
        self._create_or_reuse_image(layer, layer != "DIFFUSE")

        filepath = ""
        if self.save_mode == SaveMode.EXTERNAL:
            filepath = f"{self.save_path}/{self.material_name}_{layer}"

        result = bpy.ops.object.bake(
            "INVOKE_DEFAULT",
            type=layer,  # type: ignore
            pass_filter={"COLOR"},  # TODO change this for other textures
            uv_layer=uv.name,
            use_clear=True,
            save_mode=self.save_mode,  # type: ignore
            filepath=filepath,
        )

        return result

    def _unwrap_object(self):
        # Keeping type hints happy
        assert isinstance(self.obj.data, bpy.types.Mesh), "Object is not a mesh"
        data = self.obj.data

        uv_name = f"{self.material_name}_bake_uv"

        bake_uv = data.uv_layers.get(uv_name)
        if bake_uv is None:
            bake_uv = self.obj.data.uv_layers.new(name=uv_name)

        # Store currently active layer
        active_layer = None
        for layer in data.uv_layers:
            if layer.active:
                active_layer = layer
                break

        bake_uv.active = True
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(island_margin=0.001)
        bpy.ops.object.mode_set(mode="OBJECT")
        bake_uv.active = False

        # Restore active layer
        if active_layer is not None:
            active_layer.active = True

        self.bake_uv = bake_uv
        return bake_uv

    def _setup_bake_nodes(self):
        # Keeping type hints happy
        assert isinstance(self.obj.data, bpy.types.Mesh), "Object is not a mesh"

        node_name = f"{self.material_name}_bake_node"
        for mat in self.obj.data.materials:
            # Keeping type hints happy
            assert mat is not None
            assert mat.node_tree is not None

            # Enable shader nodes if not already enabled
            mat.use_nodes = True
            nodes = mat.node_tree.nodes

            # Create the bake image node or reuse the existing
            texture_node = mat.node_tree.get(node_name)
            if texture_node is None:
                texture_node = nodes.new("ShaderNodeTexImage")
                texture_node.name = node_name
                self._bake_nodes.append((mat, texture_node))

            texture_node.select = True
            nodes.active = texture_node

    def _create_or_reuse_image(self, layer: str, is_data=False):
        image_name = f"{self.material_name}_{layer}"

        # Lookup image from blender instead of using local in case something changed
        img = bpy.data.images.get(image_name)

        # Images have to be replaced for new bakes
        if img is not None:
            bpy.data.images.remove(img)

        img = bpy.data.images.new(
            image_name, self.resolution, self.resolution, is_data=is_data
        )

        self._curr_img = img
        self.images[layer] = img

        for _, node in self._bake_nodes:
            node.image = img

    def create_material(self):
        # Different from images, will use local before trying to find in blender data
        if self._material is not None:
            return self._material

        return self._setup_bake_material()

    def _setup_bake_material(self):
        mat = bpy.data.materials.get(self.material_name)
        if mat is None:
            mat = bpy.data.materials.new(name=self.material_name)
            mat.use_nodes = True
            # obj.data.materials.append(mat)

            principled_mat = PrincipledBSDFWrapper(mat, is_readonly=False)  # pyright: ignore[reportCallIssue]
            principled_mat.roughness = 1.0

            principled_node = principled_mat.node_principled_bsdf

            # Keeping type hints happy
            assert mat.node_tree is not None

            nodes = mat.node_tree.nodes
            links = mat.node_tree.links

            uv_node = nodes.new(type="ShaderNodeUVMap")
            uv_node.uv_map = self.bake_uv.name  # type: ignore
            uv_node.location.x -= 1000
            # uv_node.location.y += 300

            mapping_node = nodes.new(type="ShaderNodeMapping")
            mapping_node.location.x -= 800
            # mapping_node.location.y += 300
            links.new(uv_node.outputs["UV"], mapping_node.inputs["Vector"])

            def make_tex_node(img, y):
                tex_node = nodes.new(type="ShaderNodeTexImage")
                tex_node.image = img  # type: ignore
                tex_node.location.x -= 500
                tex_node.location.y += y

                links.new(mapping_node.outputs["Vector"], tex_node.inputs["Vector"])

                # TODO: color space if not set by default
                # tex_node.image.colorspace_settings.name = '...'

                return tex_node

            y = 400
            for layer, img in self.images.items():
                if layer not in self.layer_input_map:
                    self.op.report(
                        {"WARNING"}, f"Layer {layer} has no mapping to shader node"
                    )
                    continue

                shader_input = self.layer_input_map[layer]

                tex_node = make_tex_node(img, y)

                if layer == "NORMAL":
                    norm_map_node = nodes.new(type="ShaderNodeNormalMap")
                    norm_map_node.location.x -= 200
                    norm_map_node.location.y -= 200
                    links.new(tex_node.outputs["Color"], norm_map_node.inputs["Color"])
                    links.new(
                        norm_map_node.outputs["Normal"],
                        principled_node.inputs["Normal"],
                    )

                else:
                    links.new(
                        tex_node.outputs["Color"], principled_node.inputs[shader_input]
                    )

                y -= 300

        self._material = mat
        return mat
