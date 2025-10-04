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

from provide.testkit.chaos.concurrency_strategies import (
    async_event_patterns,
    deadlock_scenarios,
    lock_contention_patterns,
    pid_recycling_scenarios,
    process_pool_patterns,
    race_condition_triggers,
    task_cancellation_patterns,
    thread_counts,
)
from provide.testkit.chaos.io_strategies import (
    buffer_overflow_patterns,
    disk_full_scenarios,
    file_corruption_patterns,
    file_sizes,
    lock_file_scenarios,
    network_error_patterns,
    path_traversal_patterns,
    permission_patterns,
)
from provide.testkit.chaos.strategies import (
    chaos_timings,
    edge_values,
    failure_patterns,
    malformed_inputs,
    resource_limits,
    unicode_chaos,
)
from provide.testkit.chaos.time_strategies import (
    clock_skew,
    deadline_scenarios,
    jitter_patterns,
    rate_burst_patterns,
    retry_backoff_patterns,
    time_advances,
    timeout_patterns,
)

__all__ = [
    # Core strategies
    "chaos_timings",
    "edge_values",
    "failure_patterns",
    "malformed_inputs",
    "resource_limits",
    "unicode_chaos",
    # Time strategies
    "clock_skew",
    "deadline_scenarios",
    "jitter_patterns",
    "rate_burst_patterns",
    "retry_backoff_patterns",
    "time_advances",
    "timeout_patterns",
    # Concurrency strategies
    "async_event_patterns",
    "deadlock_scenarios",
    "lock_contention_patterns",
    "pid_recycling_scenarios",
    "process_pool_patterns",
    "race_condition_triggers",
    "task_cancellation_patterns",
    "thread_counts",
    # I/O strategies
    "buffer_overflow_patterns",
    "disk_full_scenarios",
    "file_corruption_patterns",
    "file_sizes",
    "lock_file_scenarios",
    "network_error_patterns",
    "path_traversal_patterns",
    "permission_patterns",
]
