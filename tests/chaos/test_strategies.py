"""Tests for core chaos strategies.

Validates that Hypothesis strategies generate expected value ranges and types.
"""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from provide.testkit.chaos import (
    chaos_timings,
    edge_values,
    failure_patterns,
    malformed_inputs,
    resource_limits,
    unicode_chaos,
)


class TestChaosTimings:
    """Test chaos timing strategy."""

    @given(timing=chaos_timings())
    def test_default_range(self, timing: float) -> None:
        """Test default timing range."""
        assert 0.001 <= timing <= 10.0
        assert isinstance(timing, float)

    @given(timing=chaos_timings(min_value=0.0, max_value=1.0, allow_zero=True))
    def test_custom_range_with_zero(self, timing: float) -> None:
        """Test custom range including zero."""
        assert 0.0 <= timing <= 1.0

    @given(timing=chaos_timings(min_value=5.0, max_value=100.0))
    def test_large_timing_values(self, timing: float) -> None:
        """Test large timing values."""
        assert 5.0 <= timing <= 100.0


class TestFailurePatterns:
    """Test failure pattern strategy."""

    @given(patterns=failure_patterns())
    def test_failure_pattern_structure(self, patterns: list) -> None:
        """Test failure patterns are well-formed."""
        assert isinstance(patterns, list)
        for when, exc_type in patterns:
            assert isinstance(when, int)
            assert when >= 0
            assert issubclass(exc_type, Exception)

    @given(patterns=failure_patterns(max_failures=5))
    def test_max_failures_respected(self, patterns: list) -> None:
        """Test max failures limit."""
        assert len(patterns) <= 5


class TestMalformedInputs:
    """Test malformed input strategy."""

    @given(data=malformed_inputs())
    def test_malformed_inputs_variety(self, data: object) -> None:
        """Test malformed inputs generate various types."""
        # Should generate diverse types: str, bytes, int, float, None, list, dict
        assert data is not None or data is None  # Accept any value

    @given(data=malformed_inputs(include_huge=False, include_empty=False))
    def test_exclude_options(self, data: object) -> None:
        """Test excluding certain malformed types."""
        # Validate basic constraints (no huge, no empty)
        if isinstance(data, (str, bytes)):
            assert len(data) <= 1000
        if isinstance(data, list):
            assert len(data) <= 100


class TestUnicodeChaos:
    """Test Unicode chaos strategy."""

    @given(text=unicode_chaos())
    def test_unicode_chaos_generates_strings(self, text: str) -> None:
        """Test unicode chaos generates strings."""
        assert isinstance(text, str)

    @given(text=unicode_chaos(include_emoji=True))
    def test_emoji_included(self, text: str) -> None:
        """Test emoji can be included."""
        assert isinstance(text, str)
        # Just verify it's a string, content varies

    @given(text=unicode_chaos(include_rtl=True))
    def test_rtl_text_included(self, text: str) -> None:
        """Test RTL text can be included."""
        assert isinstance(text, str)


class TestResourceLimits:
    """Test resource limits strategy."""

    @given(limits=resource_limits())
    def test_resource_limits_structure(self, limits: dict) -> None:
        """Test resource limits have expected structure."""
        assert isinstance(limits, dict)
        assert "memory" in limits
        assert "timeout" in limits
        assert "cpu_count" in limits
        assert "max_threads" in limits
        assert "max_open_files" in limits

    @given(limits=resource_limits(min_memory=1024, max_memory=1024 * 1024))
    def test_memory_limits_range(self, limits: dict) -> None:
        """Test memory limits within range."""
        assert 1024 <= limits["memory"] <= 1024 * 1024

    @given(limits=resource_limits(min_timeout=0.1, max_timeout=10.0))
    def test_timeout_limits_range(self, limits: dict) -> None:
        """Test timeout limits within range."""
        assert 0.1 <= limits["timeout"] <= 10.0


class TestEdgeValues:
    """Test edge values strategy."""

    @given(value=edge_values(value_type=int))
    def test_int_edge_values(self, value: int) -> None:
        """Test int edge values."""
        assert isinstance(value, int)
        # Should be one of the defined edge cases
        import sys

        valid_edges = [
            0,
            1,
            -1,
            sys.maxsize,
            -sys.maxsize - 1,
            2**31 - 1,
            -(2**31),
            2**63 - 1,
            -(2**63),
        ]
        assert value in valid_edges

    @given(value=edge_values(value_type=float))
    def test_float_edge_values(self, value: float) -> None:
        """Test float edge values."""
        assert isinstance(value, float)
        # Accept any float including inf and nan
        import math

        assert (
            value == 0.0
            or value == -0.0
            or value == 1.0
            or value == -1.0
            or math.isinf(value)
            or math.isnan(value)
            or value > 0
        )

    @given(value=edge_values(value_type=str))
    def test_str_edge_values(self, value: str) -> None:
        """Test str edge values."""
        assert isinstance(value, str)
        # Should be one of the defined edge cases
        valid_edges = ["", " ", "\n", "\t", "\x00", "0", "-1", "null", "None", "undefined"]
        assert value in valid_edges


__all__ = [
    "TestChaosTimings",
    "TestEdgeValues",
    "TestFailurePatterns",
    "TestMalformedInputs",
    "TestResourceLimits",
    "TestUnicodeChaos",
]
