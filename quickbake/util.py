import os
import logging

import tomllib


def _get_version():
    if os.path.exists("quickbake/blender_manifest.toml"):
        with open("quickbake/blender_manifest.toml", "rb") as f:
            data = tomllib.load(f)
            return data.get("version")


def is_development():
    return _get_version() == "0.0.0"


def enable_logging():
    log = logging.getLogger(__package__)
    if not log.handlers:
        log.setLevel(logging.DEBUG)
        log.addHandler(logging.StreamHandler())


def disable_logging():
    log = logging.getLogger(__package__)
    log.handlers.clear()
