# import os
import typing

import bpy

from .properties import BakeMode, SaveMode

if typing.TYPE_CHECKING:
    from .properties import QuickBakeToolPropertyGroup

from .bake import MaterialBaker


class RENDER_OT_bake(bpy.types.Operator):
    """Do the bake."""

    # Blender fields

    bl_idname = "render.quickbake_bake"
    bl_label = "Bake"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Disable baking until a mesh object is selected."""
        obj = context.active_object
        return obj is not None and obj.type == "MESH"

    # Execution fields

    _timer = None
    _baker: MaterialBaker | None = None  # THIS GETS RESET BETWEEN EXECUTION
    _passes: list[str] = []

    # Properties accessed by Panel

    progress = 0.0
    active = False

    # Blender interface

    def modal(self, context: bpy.types.Context, event: bpy.types.Event):
        """Async callback for events like escape and timer."""

        if event.type == "ESC":
            self.cancel(context)
            return {"CANCELLED"}

        if event.type == "TIMER":
            if self._baker is not None:
                if self._baker.layer_done():
                    if len(self._passes) > 0:
                        self.start_pass(context)
                    else:
                        self.finish(context)
                        return {"FINISHED"}

        return {"PASS_THROUGH"}

    def cancel(self, context: bpy.types.Context):
        self.report({"INFO"}, "Baking map cancelled")
        self.__class__.active = False
        self.__class__.progress = 0.0

        self._cleanup(context)

        # TODO cleanup resources like images and nodes

    def finish(self, context: bpy.types.Context):
        self.report({"INFO"}, "Baking complete")
        self.__class__.active = False
        self.__class__.progress = 1.0

        if self._baker is not None:
            if self._baker.bake_mode == BakeMode.CREATE_MATERIAL:
                self._baker.create_material()
            elif self._baker.bake_mode == BakeMode.REPLACE_MATERIAL:
                mat = self._baker.create_material()

                # Get the object to bake
                assert self._baker.bake_uv is not None, "Missing uv after bake"
                self._baker.bake_uv.active = True

                self._baker.obj.active_material = mat

                self.report({"INFO"}, "Material assigned to object")

        self._cleanup(context)

        # TODO cleanup resources like images and nodes

    def _cleanup(self, context: bpy.types.Context):
        self.__class__.active = False
        self.__class__.progress = 1.0

        # Remove any queued passes
        self._passes.clear()

        if self._baker is not None:
            self._baker.cleanup()

        self._stop_timer(context)

    def _start_timer(self, context: bpy.types.Context):
        if self._timer is not None:
            self._stop_timer(context)

        # Keeping type hints happy, should not be possible
        wm = context.window_manager
        assert wm is not None, "Context must have a window manager, got None"

        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)

    def _stop_timer(self, context: bpy.types.Context):
        # Cleanup timer calling modal() method
        if self._timer is None:
            return

        # Keeping type hints happy, should not be possible
        wm = context.window_manager
        assert wm is not None, "Context must have a window manager, got None"

        wm.event_timer_remove(self._timer)
        self._timer = None

    def execute(self, context: bpy.types.Context):
        """Prepare resources for baking and start the first pass."""

        # Setup class properties for reporting status to Panel
        self.__class__.active = True
        self.__class__.progress = 0.0

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

        # These should already be done by init or finish / cancel
        self._cleanup(context)

        if props.diffuse_enabled:
            self._passes.append("DIFFUSE")
        if props.roughness_enabled:
            self._passes.append("ROUGHNESS")
        # if props.normal_enabled:
        #     self._passes.append("NORMAL")
        # if props.metallic_enabled:
        #     # self._passes.append("METALLIC")
        #     self._passes.append("GLOSSY")
        # if props.ao_enabled:
        #     self._passes.append('AO')
        # if props.shadow_enabled:
        #     self._passes.append('SHADOW')
        # if props.position_enabled:
        #     self._passes.append('POSITION')
        # if props.uv_enabled:
        #     self._passes.append('UV')
        # if props.emit_enabled:
        #     self._passes.append('EMIT')
        # if props.environment_enabled:
        #     self._passes.append('ENVIRONMENT')
        # if props.glossy_enabled:
        #     self._passes.append('GLOSSY')
        # if props.transmission_enabled:
        #     self._passes.append('TRANSMISSION')

        self.start_pass(context)
        self._start_timer(context)

        return {"RUNNING_MODAL"}

    def start_pass(self, context):
        if len(self._passes) == 0:
            self.report({"WARNING"}, "How did you get here?")
            return

        obj = context.active_object

        if obj is None:
            self.report({"ERROR"}, "No active object")
            return {"CANCELLED"}

        if obj.type != "MESH":
            self.report({"ERROR"}, "Active object must be a mesh")
            return {"CANCELLED"}

        props: QuickBakeToolPropertyGroup
        props = context.scene.QuickBakeToolPropertyGroup  # type: ignore

        if self._baker is None:
            self._baker = MaterialBaker(
                op=self,
                obj=obj,
                material_name=props.bake_name,
                resolution=props.bake_size,
                save_mode=props.save_mode,
                bake_mode=props.bake_mode,
                save_path=props.save_path,
            )

        pass_type = self._passes.pop(0)
        self.report({"INFO"}, f"Starting bake {pass_type}")

        result = self._baker.start_layer(pass_type)

        print(f"{result=}")
        if result != {"RUNNING_MODAL"}:
            self.report({"WARNING"}, f"Failed to start baking {result!r}")
            return {"FINISHED"}

        return {"RUNNING_MODAL"}
