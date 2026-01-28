# Contributing

## Source Code

The sources are in a GIT DVCS with its main branches at [Github](https://github.com/mxstack/mxmake).

## Development Setup

### Prerequisites

- Python 3.9 or later
- Git
- make

### Quick Start

Clone the repository and set up the development environment:

```bash
git checkout https://github.com/mxstack/mxmake.git
cd mxmake
make install
```

This will:
- Create a virtual environment (`.venv`)
- Install mxmake in development mode
- Install all development dependencies

### Running Tests

```bash
make test           # Run all tests
make coverage       # Run tests with coverage report
```

### Code Quality

```bash
make check          # Run all QA checks (ruff, isort)
make typecheck      # Run type checking (mypy)
make format         # Auto-format code
```

### Building Documentation

```bash
make docs              # Build Sphinx documentation
make docs-linkcheck    # Check for broken links in docs
```

Documentation will be built in `docs/build/html/`.

## Pull Request Guidelines

### Before Submitting

1. **Run tests**: Ensure all tests pass with `make test`
2. **Check code quality**: Run `make check` and `make typecheck`
3. **Update tests**: Add tests for new features or bug fixes
4. **Update documentation**: Document new features in `docs/source/`

### Commit Messages

- Keep commits concise (max 3 lines preferred)
- Focus on what changed and why
- Write as if a human developer wrote them
- **Never mention AI assistance or Claude in commits**
- Use standard git conventions

**Good examples**:
```
Fix UV_PYTHON default value to prevent empty parameter error

Add migration guide documenting breaking changes
```

**Bad examples**:
```
Fixed stuff with Claude's help

Updated code (generated with AI)
```

### Submitting

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes and commit
3. Push to GitHub: `git push origin feature/my-feature`
4. Open a Pull Request on GitHub
5. Wait for CI to pass and address review feedback

## Copyright & Licence

- Copyright (c) 2022-2025 MXStack Contributors
- under 2-Clause BSD License (aka Simplified BSD License)
- see LICENSE.md

## Contributors

- Robert Niederreiter
- Jens Klein
