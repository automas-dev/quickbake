# import os
import typing

import bpy
from bpy_extras.node_shader_utils import PrincipledBSDFWrapper

if typing.TYPE_CHECKING:
    from .properties import QuickBakeToolPropertyGroup


class RENDER_OT_bake(bpy.types.Operator):
    """Do the bake."""

    # Blender fields

    bl_idname = "render.quickbake_bake"
    bl_label = "Bake"
    bl_options = {"REGISTER", "UNDO"}

    input_order = [
        "DIFFUSE",
        "ROUGHNESS",
        "NORMAL",
        "GLOSSY",
        "TRANSMISSION",
        "EMIT",
        "AO",
        "SHADOW",
        "ENVIRONMENT",
        "POSITION",
        "UV",
    ]

    layer_input_map = {
        "DIFFUSE": "Base Color",
        "ROUGHNESS": "Roughness",
        "NORMAL": "Normal",
        # "GLOSSY": "",
        "TRANSMISSION": "Transmission Weight",
        "EMIT": "Emission Color",
        # "AO": "",
        # "SHADOW": "",
        # "ENVIRONMENT": "",
        # "POSITION": "",
        # "UV": "",
    }

    @classmethod
    def poll(cls, context):
        """Disable baking until a mesh object is selected."""
        obj = context.active_object
        return obj is not None and obj.type == "MESH"

    def execute(self, context: bpy.types.Context):
        # Keeping type hints happy, should not be possible
        scene = context.scene
        assert scene is not None, "Context must have a scene, got None"

        # Make sure cycles is the current render engine
        if scene.render.engine != "CYCLES":
            scene.render.engine = "CYCLES"  # type: ignore
            self.report({"WARNING"}, "Changed render engine to Cycles")

        scene.render.use_lock_interface = True

        # Get the object to bake
        obj = context.active_object

        # This should be enforces by cls.poll() but is here to be sure
        if obj is None:
            self.report({"ERROR"}, "No active object")
            return {"CANCELLED"}  # canceled because nothing was altered / needs undo

        # This should be enforces by cls.poll() but is here to be sure
        if obj.type != "MESH":
            self.report({"ERROR"}, "Active object must be a mesh")
            return {"CANCELLED"}  # canceled because nothing was altered / needs undo

        # Setup passes for each enabled layer
        props: QuickBakeToolPropertyGroup
        props = scene.QuickBakeToolPropertyGroup  # type: ignore

        # layer name : is data
        passes = []
        if props.diffuse_enabled:
            passes.append(("DIFFUSE", False))
        if props.roughness_enabled:
            passes.append(("ROUGHNESS", False))
        if props.normal_enabled:
            passes.append(("NORMAL", True))
        if props.glossy_enabled:
            passes.append(("GLOSSY", False))
        if props.transmission_enabled:
            passes.append(("TRANSMISSION", False))
        if props.emit_enabled:
            passes.append(("EMIT", False))
        if props.ao_enabled:
            passes.append(("AO", False))
        if props.shadow_enabled:
            passes.append(("SHADOW", False))
        if props.environment_enabled:
            passes.append(("ENVIRONMENT", False))
        if props.position_enabled:
            passes.append(("POSITION", True))
        if props.uv_enabled:
            passes.append(("UV", True))

        # Keeping type hints happy
        assert isinstance(obj.data, bpy.types.Mesh), "Object is not a mesh"
        mesh = obj.data

        uv_layer = self.unwrap_object(mesh)
        bake_nodes = self.create_image_nodes(mesh)
        images = {}

        for layer, is_data in passes:
            self.report({"INFO"}, f"Starting layer {layer}")

            image_name = f"{props.bake_name}_{layer.lower()}"

            # Create image or use existing
            img = bpy.data.images.get(image_name)
            if img is None:
                img = bpy.data.images.new(
                    image_name, props.bake_size, props.bake_size, is_data=is_data
                )
            images[layer] = img

            # Assign image to bake node in all materials
            for mat, texture_node in bake_nodes:
                # TODO type ignore if it works
                texture_node.image = img  # type: ignore
                texture_node.select = True
                mat.node_tree.nodes.active = texture_node  # type: ignore
                # nodes.active = texture_node  # TODO per material

            filepath = ""
            save_mode = "INTERNAL"
            if props.save_img:
                filepath = f"{props.save_path}/{props.bake_name}_{layer}"
                save_mode = "EXTERNAL"

            bpy.ops.object.bake(
                type=layer,  # type: ignore
                pass_filter={"COLOR"},  # TODO change this for other textures
                uv_layer=uv_layer.name,
                use_clear=True,
                save_mode=save_mode,
                filepath=filepath,
            )

        self.cleanup_image_nodes(mesh)

        # Create Material
        mat = bpy.data.materials.get(props.bake_name)
        if mat is None:
            mat = bpy.data.materials.new(props.bake_name)
            mat.use_nodes = True

        # Get shader node (create if not exist)
        principled_mat = PrincipledBSDFWrapper(mat, is_readonly=False)  # pyright: ignore[reportCallIssue]
        principled_node = principled_mat.node_principled_bsdf

        # Keeping type hints happy
        assert mat.node_tree is not None

        shader_nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Texture coordinate node for uv map
        uv_node = shader_nodes.get("Texture Coordinate")
        if uv_node is None:
            uv_node = shader_nodes.new(type="ShaderNodeUVMap")
            uv_node.location.x = -1100
        uv_node.uv_map = uv_layer.name  # type: ignore

        # Mapping node for position, scale, rotation
        mapping_node = shader_nodes.get("Texture Coordinate")
        if mapping_node is None:
            mapping_node = shader_nodes.new(type="ShaderNodeMapping")
            mapping_node.location.x = -900

        # Link uv coordinates to mapping node
        links.new(uv_node.outputs["UV"], mapping_node.inputs["Vector"])

        for layer, _ in passes:
            y = 0
            if layer in self.input_order:
                y = (self.input_order.index(layer) - 1) * -300

            tex_node = mat.node_tree.get(layer)
            if tex_node is None:
                tex_node = shader_nodes.new(type="ShaderNodeTexImage")
                tex_node.location.x = -700
                tex_node.location.y = y

            tex_node.image = images[layer]  # type: ignore
            links.new(mapping_node.outputs["Vector"], tex_node.inputs["Vector"])

            shader_input = self.layer_input_map.get(layer, "")
            if shader_input:
                if layer == "NORMAL":
                    normal_map_node = shader_nodes.get("Normal Map")
                    if normal_map_node is None:
                        normal_map_node = shader_nodes.new(type="ShaderNodeNormalMap")
                        normal_map_node.location.x = -400
                        normal_map_node.location.y = y

                    links.new(
                        tex_node.outputs["Color"], normal_map_node.inputs["Color"]
                    )
                    links.new(
                        normal_map_node.outputs["Normal"],
                        principled_node.inputs[shader_input],
                    )

                else:
                    links.new(
                        tex_node.outputs["Color"], principled_node.inputs[shader_input]
                    )

        # Assign material to object
        if props.use_mat:
            obj.active_material = mat

        return {"FINISHED"}

    def unwrap_object(self, mesh: bpy.types.Mesh) -> bpy.types.MeshUVLoopLayer:
        uv_name = "bake_uv"

        # Use existing or create new uv layer for baking
        bake_uv = mesh.uv_layers.get(uv_name)
        if bake_uv is None:
            bake_uv = mesh.uv_layers.new(name=uv_name)

        # Store currently active layer
        active_layer = None
        for layer in mesh.uv_layers:
            if layer.active:
                active_layer = layer
                break

        # Unwrap the object
        bake_uv.active = True
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(island_margin=0.001)
        bpy.ops.object.mode_set(mode="OBJECT")
        bake_uv.active = False

        # Restore active layer
        if active_layer is not None:
            active_layer.active = True

        return bake_uv

    # TODO node is being created multiple times
    def create_image_nodes(
        self, mesh: bpy.types.Mesh
    ) -> list[tuple[bpy.types.Material, bpy.types.Node]]:
        node_name = "bake_image"

        null_count = 0
        image_nodes = []

        for mat in mesh.materials:
            if mat is None or mat.node_tree is None:
                null_count += 1
                continue

            # Enable nodes if not already
            mat.use_nodes = True

            texture_node = mat.node_tree.get(node_name)
            if texture_node is None:
                texture_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
                texture_node.name = node_name

            image_nodes.append((mat, texture_node))

        # Notify user if any materials were unusable
        if null_count > 0:
            self.report({"WARNING"}, f"Mesh {mesh.name} has {null_count} null material")

        return image_nodes

    def cleanup_image_nodes(self, mesh: bpy.types.Mesh):
        node_name = "bake_image"

        for mat in mesh.materials:
            if mat is None or mat.node_tree is None:
                continue

            node = mat.node_tree.get(node_name)
            if node is not None:
                mat.node_tree.nodes.remove(node)
