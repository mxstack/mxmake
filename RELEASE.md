# mxmake Release Process Documentation

## Overview

The mxmake project uses **automated versioning via hatch-vcs**, which derives the version number from git tags during build time, eliminating manual version bumps in code.

## Prerequisites

- Commit access to the repository
- PyPI publishing permissions (handled via GitHub Actions)
- All tests passing on the main branch

## Step-by-Step Release Process

### 1. Prepare the Main Branch

Ensure you're on the main branch with all tests passing:

```bash
git checkout main
git pull origin main
make test
make check
make typecheck
git status  # Should be clean
```

### 2. Review Changes

Check what's changed since the last release:

```bash
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

### 3. Update CHANGES.md

Edit the changelog to:
- Change "(unreleased)" to the release date (format: YYYY-MM-DD)
- Add a new unreleased section for future changes
- Maintain format: "## X.Y.Z (YYYY-MM-DD)"
- Optionally include "[author]" at the end of each entry

Commit these changes:

```bash
git add CHANGES.md
git commit -m "Prepare release X.Y.Z"
git push origin main
```

### 4. Create a GitHub Release

1. Navigate to https://github.com/mxstack/mxmake/releases/new
2. Click "Choose a tag" and type the version: `vX.Y.Z` (with the "v" prefix)
3. Click "Create new tag: vX.Y.Z on publish"
4. Set release title: `vX.Y.Z` or `Version X.Y.Z`
5. Copy the relevant CHANGES.md section into the description
6. Click "Publish release"

### 5. Monitor the Release

The GitHub Actions workflow automatically:
- Runs tests across Python 3.9-3.14 on multiple operating systems
- Runs linting, type checking, and variant tests
- Builds the package with the version from the git tag
- Publishes to PyPI if all tests pass

Monitor at: https://github.com/mxstack/mxmake/actions

### 6. Post-Release Verification

- Verify the package appears on PyPI: https://pypi.org/project/mxmake/
- Check the version is correct
- Optionally announce the release

## Version Numbering

**Format**: MAJOR.MINOR.PATCH (e.g., 1.4.0)

- **Git tags**: vMAJOR.MINOR.PATCH (e.g., v1.4.0)
- **Package version**: MAJOR.MINOR.PATCH (v prefix automatically stripped)
- The "v" prefix in tags is **required**

The project follows Semantic Versioning:
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards-compatible)
- **PATCH**: Bug fixes (backwards-compatible)

## Development Versions

Between releases, development builds automatically receive versions like:

```
1.4.0.dev3+g1234abc
```

Where:
- `1.4.0` = next release version from last tag
- `dev3` = 3 commits since last tag
- `g1234abc` = git commit hash

This happens automatically via hatch-vcs with no manual intervention needed.

## Emergency Hotfix Release

For urgent fixes to a released version:

1. Create a branch from the tag:
   ```bash
   git checkout -b hotfix-1.4.1 v1.4.0
   ```

2. Make and commit the fix:
   ```bash
   git add .
   git commit -m "Fix critical bug"
   git push origin hotfix-1.4.1
   ```

3. Create a pull request to main
4. After merge, follow the normal release process with version `v1.4.1`

## Testing a Release (TestPyPI)

### Build Locally from a Tag

```bash
git tag v1.4.0-rc1
python -m build
unzip -p dist/mxmake-*.whl mxmake/_version.py
git tag -d v1.4.0-rc1
```

### Upload to TestPyPI

```bash
pip install twine
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ mxmake
```

## Release Checklist

- [ ] All tests passing on main branch
- [ ] CHANGES.md updated with release date
- [ ] New unreleased section added to CHANGES.md
- [ ] Changes committed and pushed
- [ ] GitHub release created with correct tag (vX.Y.Z format)
- [ ] GitHub Actions workflow completed successfully
- [ ] Package visible on PyPI with correct version
- [ ] Release announced (if applicable)

## Troubleshooting

**Build fails with "version not found"**
- Ensure you're in a git repository with tags fetched
- Run: `git fetch --tags && python -m build`

**Version is wrong in built package**
- Ensure clean checkout at the tagged commit
- Run: `git checkout v1.4.0 && git status && python -m build`

**CI fails to publish to PyPI**
- Check GitHub Actions workflow logs
- Verify PyPI trusted publisher configuration
- Contact repository maintainers

**README doesn't render correctly on PyPI**
- Test locally: `python -m build && twine check dist/*`
- Upload to TestPyPI first
- Fix markdown formatting in relevant files

## Maintainer Notes

### PyPI Trusted Publisher Setup

Uses GitHub Actions OIDC for publishing (no API tokens needed):
- Publisher: GitHub
- Owner: mxstack
- Repository: mxmake
- Workflow: release.yml
- Environment: release-pypi

### GitHub Release Environments

The workflow uses two environments:
- **release-test-pypi**: Auto-publishes development versions to test.pypi.org on every main branch commit
- **release-pypi**: Publishes official releases to pypi.org on GitHub release events

## Changelog Management

### Format

```markdown
## Changes

## X.Y.Z (unreleased)

- Description of change

## X.Y.Z (YYYY-MM-DD)

- Description of change
```

### Key Points

- Version in CHANGES.md is **manual** (you edit it)
- Package version is **automatic** (from git tag via hatch-vcs)
- Format: "## X.Y.Z (YYYY-MM-DD)" for released versions
- Optionally add "[author]" at the end of each change entry

### Why This Works

With hatch-vcs, the package version is determined at build time from git tags. This means:
- Maintain a human-readable changelog manually
- Build system automatically gets the correct version
- No need to sync version numbers across multiple files

## Manual Release (Not Recommended)

For emergency situations only:

```bash
git checkout v1.4.0
python -m build
twine upload dist/*
```

This bypasses CI checks and is not recommended for normal releases.

## Version Management Tools

### Check Current Version

```bash
git describe --tags
python -c "import mxmake; print(mxmake.__version__)"
python -m build && unzip -p dist/mxmake-*.whl mxmake/_version.py
```

### List All Releases

```bash
git tag --list 'v*' --sort=-version:refname | head
pip index versions mxmake
```

## Further Reading

- [Semantic Versioning](https://semver.org/)
- [hatch-vcs Documentation](https://github.com/ofek/hatch-vcs)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [Python Packaging Guide](https://packaging.python.org/)
