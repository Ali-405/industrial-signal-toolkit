# Continuous Integration and quality gates

The CI workflows validate this library on every pull request and every push to `main`.

## Required engineering checks

- Linux test matrix on Python 3.10, 3.11, 3.12, 3.13, and 3.14.
- Windows smoke tests on Python 3.12 and 3.14.
- macOS smoke tests on Python 3.12 and 3.14.
- Ruff static analysis and Bandit security linting of the Python source.
- Unit and Hypothesis property-based tests.
- A minimum total statement coverage of 90%.
- Dependency consistency checks with `pip check`.
- Dependency vulnerability scanning with `pip-audit`.
- Wheel and source distribution builds, metadata validation, isolated installation, and CLI smoke tests.

Coverage XML reports are retained as CI artifacts for 14 days. Built distributions and SHA-256 checksums are retained as CI artifacts for 30 days.

## Security automation

- CodeQL runs on pushes, pull requests, and a weekly schedule using the extended query suite.
- Dependency Review checks dependency changes in pull requests and fails on high-severity advisories.
- OpenSSF Scorecard is not currently enabled because its container image registry rejected pulls due to an upstream billing requirement. The workflow was removed rather than leaving a permanently failing check. Reconsider it when the upstream distribution is accessible without that blocker.
- Dependabot checks Python development dependencies and GitHub Actions weekly.
- Workflows use read-only permissions where possible, avoid persisting checkout credentials, and pin third-party actions to full commit SHAs.

## Property-based invariants

Hypothesis generates deterministic sets of inputs to verify core mathematical properties:

- Scaling followed by inverse scaling returns the original raw value for non-zero gains.
- Linear mapping preserves both endpoints.
- Explicit clamping keeps results within the configured output range, including reversed ranges.
- Display precision affects formatting only and never mutates the engineering value.

These tests provide stronger evidence than a small set of hand-picked examples. They do not replace commissioning, instrument calibration, hardware-in-the-loop testing, or plant-specific validation.

## Reproducing CI locally

```bash
python -m pip install -e ".[test]"
ruff check .
bandit -r src -ll
pytest --cov=industrial_signal_toolkit --cov-report=term-missing --cov-fail-under=90
python -m pip check
```

Package validation:

```bash
python -m pip install build twine
python -m build
python -m twine check dist/*
```
