"""Setup script to install .pth file to site-packages.

This is required because setuptools' pyproject.toml doesn't support
installing .pth files to site-packages root properly.
"""

from setuptools import setup

setup(
    data_files=[(".", ["provide_testkit_setproctitle_blocker.pth"])],
)
