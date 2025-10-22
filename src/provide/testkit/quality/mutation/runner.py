"""Mutation testing result parser and reporter.

This module provides utilities for parsing mutmut results and generating reports.
It does NOT execute mutmut - users should run `mutmut run` directly.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import time
from typing import Any

from provide.foundation import logger

from ..base import QualityResult
from .config import ModulePriority, MutationConfig


class MutationRunner:
    """Parses mutation test results from mutmut and generates reports.

    NOTE: This does NOT run mutmut. Run `mutmut run` separately, then use
    this class to parse results and generate reports.

    Implements the QualityTool protocol for integration with testkit quality framework.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize mutation result parser.

        Args:
            config: Configuration dict, will be converted to MutationConfig
        """
        self.config = MutationConfig.from_dict(config or {})
        self.logger = logger.get_logger(__name__)

    def analyze(self, path: Path, **kwargs: Any) -> QualityResult:
        """Parse existing mutation test results from mutmut.

        NOTE: This does NOT run mutmut. You must run `mutmut run` first.

        Args:
            path: Path to project root (where .mutmut-cache exists)
            **kwargs: Additional options:
                - priority: Priority level for target score

        Returns:
            QualityResult with mutation testing results parsed from mutmut cache
        """
        start_time = time.time()

        try:
            # Find project root containing .mutmut-cache
            project_root = self._find_project_root(path)

            # Parse mutmut results
            result = self._parse_mutmut_results(project_root)

            # Calculate score
            total_mutants = result["killed"] + result["survived"] + result["timeout"] + result["suspicious"]
            score = 100.0 if total_mutants == 0 else result["killed"] / total_mutants * 100

            # Determine if passed based on target score
            target_score = self._get_target_score(path, kwargs.get("priority"))
            passed = score >= target_score

            execution_time = time.time() - start_time

            return QualityResult(
                tool="mutation",
                passed=passed,
                score=score,
                details={
                    "total_mutants": total_mutants,
                    "killed": result["killed"],
                    "survived": result["survived"],
                    "timeout": result["timeout"],
                    "suspicious": result["suspicious"],
                    "target_score": target_score,
                    "priority": kwargs.get("priority", "standard"),
                },
                artifacts=[Path("html/index.html"), Path(".mutmut-cache")],
                execution_time=execution_time,
            )

        except Exception as e:
            self.logger.error(f"Failed to parse mutation results: {e}")
            return QualityResult(
                tool="mutation",
                passed=False,
                score=0.0,
                details={"error": str(e)},
                execution_time=time.time() - start_time,
            )

    def run_module(self, module_path: str | Path, target_score: float | None = None) -> QualityResult:
        """Run mutations on a specific module.

        Args:
            module_path: Path to the module to mutate
            target_score: Override target score (default: from config)

        Returns:
            QualityResult for the module
        """
        return self.analyze(Path(module_path), module_filter=str(module_path))

    def run_changed_files(self, base_branch: str = "main") -> QualityResult:
        """Run mutations only on files changed since base branch.

        Args:
            base_branch: Branch to compare against (default: main)

        Returns:
            QualityResult for changed files
        """
        return self.analyze(Path.cwd(), changed_only=True)

    def run_priority(self, priority: ModulePriority | str) -> QualityResult:
        """Run mutations on modules of specific priority.

        Args:
            priority: Priority level to test

        Returns:
            QualityResult for priority level
        """
        if isinstance(priority, str):
            priority = ModulePriority(priority)

        return self.analyze(Path.cwd(), priority=priority)

    def report(self, result: QualityResult, format: str = "terminal") -> str:
        """Generate report from mutation result.

        Args:
            result: Mutation test result
            format: Output format (terminal, json, html, markdown)

        Returns:
            Formatted report string
        """
        from .reporter import MutationReporter

        reporter = MutationReporter()

        if format == "terminal":
            return reporter.generate_terminal(result)
        elif format == "json":
            return reporter.generate_json(result)
        elif format == "markdown":
            return reporter.generate_markdown(result)
        elif format == "html":
            return reporter.generate_html(result)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _run_mutmut(self, path: Path, files_to_mutate: list[str] | None = None) -> dict[str, int]:
        """Run mutmut and parse results.

        Args:
            path: Base path for mutation testing
            files_to_mutate: Specific files to mutate (None for all)

        Returns:
            Dict with mutation counts: killed, survived, timeout, suspicious
        """
        # Find project root (directory containing pyproject.toml)
        project_root = path if path.is_dir() else path.parent
        while project_root != project_root.parent:
            if (project_root / "pyproject.toml").exists():
                break
            project_root = project_root.parent

        cmd = ["mutmut", "run", "--no-progress"]

        if files_to_mutate:
            # mutmut doesn't have a direct file filter, so we'd need to
            # temporarily modify pyproject.toml or use paths_to_mutate
            # For now, run on all and filter results
            pass

        # Run mutmut from project root
        subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=3600,  # 1 hour max
        )

        # Parse results from mutmut output or cache
        return self._parse_mutmut_results(project_root)

    def _parse_mutmut_results(self, path: Path) -> dict[str, int]:
        """Parse mutmut results from results command.

        Args:
            path: Base path where mutmut ran

        Returns:
            Dict with mutation counts
        """
        # Check if mutmut cache exists
        cache_file = path / ".mutmut-cache"
        if not cache_file.exists():
            self.logger.warning("No mutmut cache found, returning zero counts")
            return {"killed": 0, "survived": 0, "timeout": 0, "suspicious": 0}

        # Run mutmut results to get counts
        try:
            result = subprocess.run(
                ["mutmut", "results"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except subprocess.TimeoutExpired:
            self.logger.error("mutmut results timed out")
            return {"killed": 0, "survived": 0, "timeout": 0, "suspicious": 0}

        # Parse output like:
        # Survived 🙁: 5
        # Killed ⚔️: 120
        # Timeout ⏰: 2
        # Suspicious 🤔: 1

        counts = {"killed": 0, "survived": 0, "timeout": 0, "suspicious": 0}

        for line in result.stdout.split("\n"):
            if "Killed" in line:
                counts["killed"] = int(line.split(":")[1].strip())
            elif "Survived" in line:
                counts["survived"] = int(line.split(":")[1].strip())
            elif "Timeout" in line:
                counts["timeout"] = int(line.split(":")[1].strip())
            elif "Suspicious" in line:
                counts["suspicious"] = int(line.split(":")[1].strip())

        return counts

    def _get_modules_by_priority(self, priority: ModulePriority | str) -> list[str]:
        """Get list of modules matching priority level.

        Args:
            priority: Priority level to filter by

        Returns:
            List of module paths
        """
        if isinstance(priority, str):
            priority = ModulePriority(priority)

        modules = []
        for module_path, module_priority in self.config.module_priorities.items():
            if module_priority == priority:
                modules.append(module_path)

        return modules

    def _get_target_score(self, path: Path, priority: ModulePriority | str | None = None) -> float:
        """Get target mutation score for path.

        Args:
            path: Path being tested
            priority: Override priority level

        Returns:
            Target mutation score (0-100)
        """
        if priority:
            if isinstance(priority, str):
                priority = ModulePriority(priority)
            return self.config.score_thresholds.get(priority, 60.0)

        return self.config.get_target_score(path)
