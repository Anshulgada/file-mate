# Contributing to FileMate

Thank you for your interest in contributing to FileMate! Your help is welcome—whether it's bug reports, feature requests, code, or documentation improvements.

## How to Contribute

1. **Fork the repository** and create your branch from `main`.
2. **Write clear, descriptive commit messages**.
3. **Add tests** for new features or bug fixes (see `tests/` and use `pytest`).
4. **Format your code** with [black], lint with [ruff], and type-check with [mypy].
5. **Follow the project structure**:
   - CLI entry point: `src/filemate/cli.py`
   - Commands: `src/filemate/commands/`
   - Core logic: `src/filemate/core/`
   - Utilities: `src/filemate/utils/`
   - Tests: `tests/`
   - Documentation: `docs/`
6. **Document your changes** in the relevant Markdown files in `docs/` if needed.
7. **Ensure all tests pass** before submitting a pull request.
8. **Open a pull request** with a clear description of your changes and reference any related issues.

## Code Style & Tools
- Use Python 3.12+
- Use [pydantic] for data validation
- Use [click] for CLI (preferably with [rich-click])
- Use [pytest] for testing
- Use [black] for formatting
- Use [ruff] for linting
- Use [mypy] for type checking
- Use [pre-commit] hooks (see `.pre-commit-config.yaml`)

## Submitting Issues
- Search existing issues before opening a new one.
- Provide clear steps to reproduce bugs.
- Suggest enhancements with use cases and rationale.

## Pull Request Checklist
- [ ] Code is formatted and linted
- [ ] Type checks pass
- [ ] Tests are added/updated and pass
- [ ] Documentation is updated if needed
- [ ] PR description is clear and references issues if applicable

## Community
- Be respectful and constructive in all interactions.
- Follow the project's [Code of Conduct].

Thank you for helping make FileMate better!


<!-- Link references -->
[black]: (https://black.readthedocs.io/en/stable/)
[ruff]: (https://docs.astral.sh/ruff/)
[mypy]: (https://mypy-lang.org/)
[pydantic]: (https://docs.pydantic.dev/)
[click]: (https://click.palletsprojects.com/)
[rich-click]: (https://github.com/ewels/rich-click)
[pytest]: (https://docs.pytest.org/)
[pre-commit]: (https://pre-commit.com/)
[Code of Conduct]: (CODE_OF_CONDUCT.md)
