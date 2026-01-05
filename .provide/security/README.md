# Security Configuration

Centralized security tool configuration for provide-testkit.

## Overview

This directory contains configuration files for all security scanning tools used in the provide-testkit ecosystem. These configs are automatically detected by the testkit's security scanner wrappers.

## Configuration Files

| File | Tool | Format | Purpose |
|------|------|--------|---------|
| `gitleaks.toml` | GitLeaks | TOML | Secret detection with allowlists |
| `trufflehog.yml` | TruffleHog | YAML | Deep secret scanning |
| `bandit.toml` | Bandit | TOML | Python SAST configuration |
| `safety-policy.yml` | Safety | YAML | Dependency vulnerability policy |
| `checkov.yml` | Checkov | YAML | IaC security scanning |
| `semgrep.yml` | Semgrep | YAML | Pattern-based SAST rules |

## Usage

### Automatic Detection

The testkit security scanners automatically detect and use these configs:

```python
from provide.testkit.quality.security import GitLeaksScanner

# Automatically uses .provide/security/gitleaks.toml
scanner = GitLeaksScanner()
result = scanner.analyze(path)
```

### CLI Usage with wrknv

```bash
# Uses configs automatically
we security              # Run all security scans
we security.sast         # Static analysis (Bandit + Semgrep)
we security.deps         # Dependency scanning (pip-audit + Safety)
we security.secrets      # Secret detection (GitLeaks + TruffleHog)
we security.iac          # IaC scanning (Checkov)
```

### Direct Tool Invocation

```bash
# Reference configs directly
gitleaks detect --source . --config .provide/security/gitleaks.toml
safety check --policy-file .provide/security/safety-policy.yml
checkov --directory . --config-file .provide/security/checkov.yml
semgrep --config .provide/security/semgrep.yml src/
```

## Configuration Details

### GitLeaks (`gitleaks.toml`)

- **Allowlists**: Ignores test fixtures with sample crypto keys
- **Path exclusions**: Tests, virtual environments, cache directories
- **Custom rules**: High-entropy string detection
- **Stop words**: "test", "example", "sample", etc.

### TruffleHog (`trufflehog.yml`)

- **Excluded paths**: Test files, fixtures, documentation
- **Verification**: Configurable active credential checking
- **Concurrency**: Performance tuning options

### Bandit (`bandit.toml`)

- **Excluded directories**: tests, .venv, build artifacts
- **Severity threshold**: LOW (catches everything)
- **Confidence threshold**: MEDIUM
- **Test-specific overrides**: Less strict for test files

### Safety (`safety-policy.yml`)

- **CVSS thresholds**: Configurable severity levels
- **Package ignores**: Document exceptions with justification
- **Alert levels**: CI/CD failure thresholds
- **Scanning depth**: Dependency tree analysis

### Checkov (`checkov.yml`)

- **Frameworks**: All (Terraform, Dockerfile, K8s, etc.)
- **Skip paths**: Tests, virtual environments
- **Severity threshold**: LOW to HIGH configurable
- **Soft fail**: Optional non-blocking mode

### Semgrep (`semgrep.yml`)

- **Custom rules**: Project-specific security patterns
- **Path exclusions**: Test files, generated code
- **Rule severity**: ERROR, WARNING, INFO levels
- **Metadata**: Confidence and impact scoring

## Customization

### Adding Exceptions

To ignore a known false positive:

1. **GitLeaks**: Add to `[allowlist]` section
2. **Bandit**: Add to `skips` list with test ID
3. **Safety**: Add to `ignore-vulnerabilities` with justification
4. **Checkov**: Add to `skip-check` list
5. **Semgrep**: Add path to `paths.exclude`

### Creating Custom Rules

#### Semgrep Custom Rules

```yaml
rules:
  - id: my-custom-rule
    pattern: dangerous_function(...)
    message: "Don't use dangerous_function"
    languages: [python]
    severity: ERROR
```

#### GitLeaks Custom Rules

```toml
[[rules]]
id = "custom-api-key"
description = "Custom API Key Pattern"
regex = '''MY_API_KEY_[A-Z0-9]{32}'''
keywords = ["MY_API_KEY"]
```

## Best Practices

1. **Version control**: Commit all configs to track policy changes
2. **Document exceptions**: Always add justification for ignores
3. **Regular review**: Periodically audit allowlists and skips
4. **CI/CD integration**: Enforce security gates in pipelines
5. **Baseline management**: Use baseline files for known issues

## Artifacts

Security scan results are stored in `.provide/output/security/` (gitignored):

```
.provide/output/security/
├── bandit.json           # Bandit scan results
├── pip_audit.json        # pip-audit results
├── safety.json           # Safety scan results
├── gitleaks.json         # GitLeaks findings
├── gitleaks_raw.json     # Raw GitLeaks output
├── trufflehog.json       # TruffleHog results
├── checkov.json          # Checkov findings
├── semgrep.json          # Semgrep results
└── *_summary.txt         # Human-readable summaries
```

## Tool Installation

### Python Tools (via uv)

```bash
uv add provide-testkit[security]
# Installs: bandit, safety, pip-audit, semgrep, checkov
```

### External Binaries

```bash
# macOS
brew install gitleaks trufflehog

# Linux
# Download from GitHub releases
# https://github.com/gitleaks/gitleaks/releases
# https://github.com/trufflesecurity/trufflehog/releases
```

## References

- [GitLeaks Documentation](https://github.com/gitleaks/gitleaks)
- [TruffleHog Documentation](https://github.com/trufflesecurity/trufflehog)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Safety Documentation](https://docs.safetycli.com/)
- [Checkov Documentation](https://www.checkov.io/)
- [Semgrep Documentation](https://semgrep.dev/docs/)
