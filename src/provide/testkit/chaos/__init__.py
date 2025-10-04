"""Chaos testing utilities for property-based testing with Hypothesis.

This module provides reusable Hypothesis strategies and fixtures for chaos engineering
in tests. It enables systematic exploration of edge cases, race conditions, and failure
scenarios that are difficult to test with traditional methods.

Key Features:
    - Property-based testing strategies for common chaos patterns
    - Time manipulation and clock skew simulation
    - Concurrency and race condition triggers
    - I/O failure injection patterns
    - Reusable pytest fixtures for chaos testing

Example:
    ```python
    from hypothesis import given
    from provide.testkit.chaos import chaos_timings, failure_patterns

    @given(
        timing=chaos_timings(),
        failures=failure_patterns()
    )
    async def test_with_chaos(timing, failures):
        # Your chaos test here
        pass
    ```
"""

from __future__ import annotations

from provide.testkit.chaos.strategies import (
    chaos_timings,
    edge_values,
    failure_patterns,
    malformed_inputs,
    resource_limits,
    unicode_chaos,
)

__all__ = [
    "chaos_timings",
    "edge_values",
    "failure_patterns",
    "malformed_inputs",
    "resource_limits",
    "unicode_chaos",
]
