# provide/testkit/pytest_plugin.py
#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Pytest plugin that disables setproctitle to prevent pytest-xdist issues on macOS.

This plugin disables setproctitle at module-import time (not in a hook), ensuring
the mock is injected BEFORE pytest-xdist or any other code can import setproctitle.

On macOS, when setproctitle is installed, pytest-xdist's use of it to set worker
process titles causes the terminal/UX to freeze completely. This plugin prevents
that by mocking out setproctitle before it can be imported.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

# CRITICAL: This must happen at module-level (import time), NOT in a hook.
# Hooks run too late - xdist may have already imported setproctitle by then.
#
# By executing this at import time, we ensure the mock is in sys.modules
# BEFORE pytest-xdist workers initialize and try to import setproctitle.

if "setproctitle" not in sys.modules:
    # Create a comprehensive mock that implements all setproctitle functions
    mock_setproctitle = MagicMock()
    mock_setproctitle.setproctitle = MagicMock(return_value=None)
    mock_setproctitle.getproctitle = MagicMock(return_value="python")
    mock_setproctitle.setthreadtitle = MagicMock(return_value=None)
    mock_setproctitle.getthreadtitle = MagicMock(return_value="")

    # Inject into sys.modules to intercept all imports
    sys.modules["setproctitle"] = mock_setproctitle
else:
    # setproctitle was already imported (edge case)
    # Replace it with a mock to disable functionality
    existing_module = sys.modules["setproctitle"]

    # Replace all callable attributes with no-ops
    if hasattr(existing_module, "setproctitle"):
        existing_module.setproctitle = MagicMock(return_value=None)
    if hasattr(existing_module, "getproctitle"):
        existing_module.getproctitle = MagicMock(return_value="python")
    if hasattr(existing_module, "setthreadtitle"):
        existing_module.setthreadtitle = MagicMock(return_value=None)
    if hasattr(existing_module, "getthreadtitle"):
        existing_module.getthreadtitle = MagicMock(return_value="")


def pytest_load_initial_conftests() -> None:
    """Hook kept for documentation purposes.

    The actual setproctitle mocking happens at module level (above),
    not in this hook, because hooks run too late - xdist imports
    setproctitle before hooks execute.
    """
    pass


# 🔌🚫📋🪄
