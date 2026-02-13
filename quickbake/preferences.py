# pyright: reportInvalidTypeForm=false
import bpy
from bpy.props import BoolProperty


class QuickBakeAddonPreferences(bpy.types.AddonPreferences):
    # This must match the add-on name, use `__package__`
    # when defining this for add-on extensions or a sub-module of a Python package.
    assert __package__ is not None, "Need __package__"
    bl_idname = __package__

    enable_logging: BoolProperty(
        name="Enable debug logging",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "enable_logging")


def get_preferences(context: bpy.types.Context) -> QuickBakeAddonPreferences:
    preferences = context.preferences
    assert preferences is not None
    assert __package__ is not None
    addon = preferences.addons[__package__]
    assert addon is not None
    addon_prefs: QuickBakeAddonPreferences = addon.preferences  # type: ignore
    assert addon_prefs is not None
    return addon_prefs
