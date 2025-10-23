#!/usr/bin/env python3
# _install_pth.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Post-install script to symlink .pth file to site-packages root.

This script is called automatically via pip's console_scripts entry point
after package installation to ensure the .pth file is in the correct location.
"""

from __future__ import annotations

import os
import site
import sys
from pathlib import Path


def install_pth_file() -> int:
    """Install/symlink .pth file to site-packages root.

    Returns:
        0 on success, 1 on failure
    """
    # Find site-packages directory
    site_packages = None
    if hasattr(site, "getsitepackages"):
        site_dirs = site.getsitepackages()
        if site_dirs:
            site_packages = Path(site_dirs[0])

    if not site_packages:
        # Fallback
        if sys.platform == "win32":
            site_packages = Path(sys.prefix) / "Lib" / "site-packages"
        else:
            python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
            site_packages = Path(sys.prefix) / "lib" / python_version / "site-packages"

    # Source .pth file (in package)
    pth_source = Path(__file__).parent / "provide_testkit_init.pth"

    # Destination .pth file (in site-packages root)
    pth_dest = site_packages / "provide_testkit_init.pth"

    if not pth_source.exists():
        print(f"Error: Source .pth file not found at {pth_source}", file=sys.stderr)
        return 1

    try:
        # Try to create symlink first (preferred)
        if pth_dest.exists() or pth_dest.is_symlink():
            pth_dest.unlink()

        try:
            pth_dest.symlink_to(pth_source)
            print(f"✓ Symlinked {pth_dest} -> {pth_source}")
            return 0
        except (OSError, NotImplementedError):
            # Symlink not supported, copy instead
            import shutil
            shutil.copy2(pth_source, pth_dest)
            print(f"✓ Copied {pth_source} -> {pth_dest}")
            return 0

    except PermissionError:
        print(f"Warning: No permission to write to {pth_dest}", file=sys.stderr)
        print("The setproctitle blocker will use fallback mechanisms", file=sys.stderr)
        return 0  # Don't fail installation
    except Exception as e:
        print(f"Warning: Could not install .pth file: {e}", file=sys.stderr)
        print("The setproctitle blocker will use fallback mechanisms", file=sys.stderr)
        return 0  # Don't fail installation


if __name__ == "__main__":
    sys.exit(install_pth_file())


# 📦🔗⚙️✨
