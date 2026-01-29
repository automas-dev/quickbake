import tomllib
from unittest.mock import patch


def test_import():
    import quickbake


# @patch('quickbake.bpy')
def test_version():
    import quickbake

    with open('pyproject.toml', 'rb') as f:
        t = tomllib.load(f)

    expect_version = tuple(map(int, t['project']['version'].split('.')))

    assert quickbake.version_tuple == expect_version
