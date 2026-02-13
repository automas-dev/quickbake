import logging

import bpy
from bpy_extras.node_shader_utils import PrincipledBSDFWrapper

from .properties import MaterialMode, QuickBakeToolPropertyGroup

_log = logging.getLogger(__name__)


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
        _log.info("Begin execution")

        # Keeping type hints happy, should not be possible
        scene = context.scene
        assert scene is not None, "Context must have a scene, got None"

        # Make sure cycles is the current render engine
        if scene.render.engine != "CYCLES":
            _log.info("Setting render engine to cycles")
            scene.render.engine = "CYCLES"  # type: ignore
            self.report({"WARNING"}, "Changed render engine to Cycles")

        scene.render.use_lock_interface = True

        # Get the object to bake
        obj = context.active_object

        # This should be enforces by cls.poll() but is here to be sure
        if obj is None:
            _log.error("No active object")
            self.report({"ERROR"}, "No active object")
            return {"CANCELLED"}  # canceled because nothing was altered / needs undo

        # This should be enforces by cls.poll() but is here to be sure
        if obj.type != "MESH":
            _log.error("Expected active object to be mesh, got %s", obj.type)
            self.report({"ERROR"}, "Active object must be a mesh")
            return {"CANCELLED"}  # canceled because nothing was altered / needs undo

        # Setup passes for each enabled layer
        props: QuickBakeToolPropertyGroup
        props = scene.QuickBakeToolPropertyGroup  # type: ignore

        # layer name : is data
        passes: list[tuple[str, bool]] = []
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

        _log.debug("Render passes will be %s", passes)

        # Keeping type hints happy
        assert isinstance(obj.data, bpy.types.Mesh), "Object is not a mesh"
        mesh = obj.data

        uv_layer = self.unwrap_object(mesh)
        bake_nodes = self.create_image_nodes(mesh)
        images = {}

        for layer, is_data in passes:
            _log.info("Starting layer %s", layer)
            self.report({"INFO"}, f"Starting layer {layer}")

            image_name = f"{props.bake_name}_{layer.lower()}"

            # Create image or use existing
            img = bpy.data.images.get(image_name)
            if img is None:
                _log.info("Creating image %s", image_name)
                img = bpy.data.images.new(
                    image_name, props.bake_size, props.bake_size, is_data=is_data
                )
            else:
                _log.debug("Using existing image %s", image_name)
            images[layer] = img

            # Assign image to bake node in all materials
            for mat, texture_node in bake_nodes:
                _log.debug(
                    "Assigning image to texture node %s in material %s",
                    texture_node.name,
                    mat.name,
                )
                # TODO type ignore if it works
                texture_node.image = img  # type: ignore
                texture_node.select = True
                mat.node_tree.nodes.active = texture_node  # type: ignore
                # nodes.active = texture_node  # TODO per material

            filepath = ""
            save_mode = "INTERNAL"
            if props.save_img:
                save_mode = "EXTERNAL"
                filepath = f"{props.save_path}/{props.bake_name}_{layer}"
                _log.debug("Images will be saved externally to %s", filepath)

            _log.info("Starting bake for layer %s", layer)
            bpy.ops.object.bake(
                type=layer,  # type: ignore
                pass_filter={"COLOR"},  # TODO change this for other textures
                uv_layer=uv_layer.name,
                use_clear=True,
                save_mode=save_mode,
                filepath=filepath,
            )
            _log.info("Finished bake for layer %s", layer)

        self.cleanup_image_nodes(mesh)

        # Only create images
        if props.mat_mode == MaterialMode.IMAGES:
            return {"FINISHED"}

        mat = self.create_material(props, uv_layer, passes, images)

        # Duplicate object and assign material to new
        if props.mat_mode == MaterialMode.DUPLICATE:
            _log.info("Duplicating object before assigning material")
            bpy.ops.object.duplicate()
            _log.debug("Hiding original object %s", obj.name)
            obj.hide_set(True)
            # Get new object
            obj = context.active_object
            _log.debug(
                "New object is named %s", obj.name if obj is not None else "None"
            )

            # Keeping type hints happy
            assert obj is not None, "Object is None"
            assert isinstance(obj.data, bpy.types.Mesh), "Object is not a mesh"

        # Assign or Copy
        if props.mat_mode != MaterialMode.CREATE:
            _log.info("Assigning material %s to object %s", mat.name, obj.name)
            obj.data.materials.clear()
            obj.active_material = mat

        _log.info("Finished execution")
        return {"FINISHED"}

    def unwrap_object(self, mesh: bpy.types.Mesh) -> bpy.types.MeshUVLoopLayer:
        uv_name = "bake_uv"
        _log.debug("Unwrapping mesh %s with uv layer %s", mesh.name, uv_name)

        # Use existing or create new uv layer for baking
        bake_uv = mesh.uv_layers.get(uv_name)
        if bake_uv is None:
            _log.info("Creating new uv layer %s", uv_name)
            bake_uv = mesh.uv_layers.new(name=uv_name)
        else:
            _log.debug("Reusing existing uv layer %s", uv_name)

        # Store currently active layer
        active_layer = None
        for layer in mesh.uv_layers:
            if layer.active:
                active_layer = layer
                _log.debug("Currently active uv layer is %s", active_layer.name)
                break

        _log.debug("Start unwrapping mesh %s", mesh.name)
        # Unwrap the object
        bake_uv.active = True
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(island_margin=0.001)
        bpy.ops.object.mode_set(mode="OBJECT")
        bake_uv.active = False
        _log.debug("Finished unwrapping mesh %s", mesh.name)

        # Restore active layer
        if active_layer is not None:
            _log.debug("Restoring active uv layer %s", active_layer.name)
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
                _log.warning("Found null material in mesh %s", mesh.name)
                null_count += 1
                continue

            _log.debug("Enabling nodes for material %s", mat.name)
            # Enable nodes if not already
            mat.use_nodes = True

            texture_node = mat.node_tree.get(node_name)
            if texture_node is None:
                _log.info("Creating texture node for material %s", mat.name)
                texture_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
                texture_node.name = node_name

            else:
                _log.debug("Using existing texture node %s", texture_node.name)

            image_nodes.append((mat, texture_node))

        _log.info("Created %d nodes in mesh %s", len(image_nodes), mesh.name)

        # Notify user if any materials were unusable
        if null_count > 0:
            self.report({"WARNING"}, f"Mesh {mesh.name} has {null_count} null material")

        return image_nodes

    def cleanup_image_nodes(self, mesh: bpy.types.Mesh):
        node_name = "bake_image"
        _log.info("Cleaning up bake texture node %s in msh %s", node_name, mesh.name)

        for mat in mesh.materials:
            if mat is None or mat.node_tree is None:
                _log.warning("Found null material in mesh %s", mesh.name)
                continue

            node = mat.node_tree.nodes.get(node_name)
            if node is not None:
                _log.debug("Removing node %s from material %s", node.name, mat.name)
                mat.node_tree.nodes.remove(node)
            else:
                _log.warning(
                    "Failed to find node %s in material %s", node_name, mat.name
                )
                _log.debug(
                    "Material %s has nodes %s", mat.name, list(mat.node_tree.nodes)
                )
                self.report({"WARNING"}, f"Failed to cleanup material {mat.name}")

    def create_material(
        self,
        props: QuickBakeToolPropertyGroup,
        uv_layer: bpy.types.MeshUVLoopLayer,
        passes: list[tuple[str, bool]],
        images: dict,
    ):
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

        return mat
