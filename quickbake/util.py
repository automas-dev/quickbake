import os

import tomllib


def _get_version():
    if os.path.exists("quickbake/blender_manifest.toml"):
        with open("quickbake/blender_manifest.toml", "rb") as f:
            data = tomllib.load(f)
            return data.get("version")


def is_development():
    return _get_version() == "0.0.0"
