#!/usr/bin/env python3
# setup.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Custom setup.py to install .pth file to site-packages root.

This setup.py uses setuptools' data_files feature to install our .pth file
directly to the site-packages directory, ensuring it's loaded during Python's
site initialization (before any user code runs).

Note: This file is necessary because pyproject.toml alone doesn't provide
a way to install files to the site-packages root directory.
"""

from __future__ import annotations

import os
import site
import sys
from pathlib import Path

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install


def get_site_packages_dir() -> str:
    """Get the target site-packages directory for installation.

    Returns:
        Path to site-packages directory where .pth file should be installed
    """
    # For regular install, use the standard site-packages
    if hasattr(site, "getsitepackages"):
        site_dirs = site.getsitepackages()
        if site_dirs:
            return site_dirs[0]

    # Fallback: construct path from sys.prefix
    if sys.platform == "win32":
        return os.path.join(sys.prefix, "Lib", "site-packages")
    else:
        python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        return os.path.join(sys.prefix, "lib", python_version, "site-packages")


def install_pth_file() -> None:
    """Install the .pth file to site-packages."""
    import shutil

    pth_source = Path(__file__).parent / "src" / "provide_testkit_init.pth"
    site_packages = get_site_packages_dir()
    pth_dest = Path(site_packages) / "provide_testkit_init.pth"

    print(f"Installing .pth file: {pth_source} -> {pth_dest}")

    try:
        shutil.copy2(str(pth_source), str(pth_dest))
        print(f"Successfully installed {pth_dest}")
    except Exception as e:
        print(f"Warning: Could not install .pth file: {e}", file=sys.stderr)
        # Don't fail the installation if .pth file can't be installed
        # The fallback mechanisms (pytest11 entry point, __init__.py) will still work


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self) -> None:
        """Run the install command and then install .pth file."""
        install.run(self)
        install_pth_file()


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self) -> None:
        """Run the develop command and then install .pth file."""
        develop.run(self)
        install_pth_file()


# Run setup with custom commands
setup(
    cmdclass={
        "install": PostInstallCommand,
        "develop": PostDevelopCommand,
    },
)


# 📦⚙️🔧✨
