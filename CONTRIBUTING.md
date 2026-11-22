# Contributing

Contributions are welcome, especially reproducible industrial signal examples, numerical edge cases, documentation improvements, and tests.

Before opening a pull request:

1. Open or find an issue describing the change.
2. Keep numerical behavior explicit; do not silently change rounding or clamping semantics.
3. Add tests for normal values, boundaries, invalid inputs, and precision-sensitive cases.
4. Run `python -m pip install -e ".[test]"` and `pytest`.
5. Update engineering notes and the changelog when behavior changes.

Do not submit credentials, customer information, production records, or proprietary source code. Do not describe untested functionality as production-certified or safety-rated.

By contributing, you agree that your contribution is provided under the repository's MIT license.
