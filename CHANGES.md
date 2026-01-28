# Changelog

## 2.0.2

- Feature: Add `qa.ty` domain for Astral's ty type checker.
  ty is an extremely fast Python type checker (10-100x faster than mypy).
  Registers with both CHECK_TARGETS and TYPECHECK_TARGETS for fast feedback.
  [jensens]

## 2.0.1

- Enhancement: Use tables in the generated sphinx code for topic/domains.
  [jensens, 02-11-2025]

- Feature: Add `--version` (`-v`) command line flag to display mxmake version.
  [jensens, 02-11-2025]

## 2.0.0 (2025-10-24)

- **Breaking**: Drop Python 3.9 support. Minimum Python version is now 3.10.
- Feature: Modernize codebase to use Python 3.10+ features (PEP 604 union types, built-in generic types).
- **Critical fix**: `SOURCES_TARGET` used mxdev wrongly with `-o` (offline) option.
  The offline option had a bug and was fixed in mxdev [#34](https://github.com/mxstack/mxdev/issues/34) and released with mxdev>=5.
  This fix switches from `-o` to the correct `-f` (no fetch from vcs).
  To update your makefile use `mxmake update` in the folder with your `Makefile`.
- Fix: theme for newer Sphinx 7.x.
- Fix: interactive uv venv, use `--allow-existing` instead.
- Fix: The project was using `pytest` as the test runner all along (as configured in the Makefile and generated test scripts), but `zope.testrunner `was incorrectly listed as the dependency.
- Feature: Add support for Python 3.14.
- Breaking: Removed `MXENV_UV_GLOBAL` setting in favor of automatic UV detection.
  When `PYTHON_PACKAGE_INSTALLER=uv`, mxmake now automatically detects and uses
  a globally installed `uv` if available. To force local installation of uv,
  simply don't install it globally or remove it from PATH.
- Feature: Add `UV_PYTHON` setting to specify Python version for UV-managed virtual
  environments. Defaults to `PRIMARY_PYTHON` for backward compatibility. This
  provides semantic clarity: `PRIMARY_PYTHON` is the system interpreter path
  (e.g., `python3.11`), while `UV_PYTHON` is the version spec for UV
  (e.g., `3.14`, `cpython@3.14`).
- Feature: Automatic detection of global UV installation using simple shell check.
  No manual configuration required.
- Feature: All UV commands now run with `--quiet --no-progress` flags for better
  CI/CD compatibility and cleaner log output.
- Feature: When using global UV, mxmake checks if updates are available using
  `uv self update --dry-run` and displays a helpful non-blocking warning if a
  newer version is available.
- Improvement: Simplified mxenv.mk logic from 3+ nesting levels to 1-2 levels
  using computed intermediate variables (`USE_GLOBAL_UV`, `USE_LOCAL_UV`).
  Code is now more maintainable and easier to extend.
- Tests/CI: Add UV-only CI job testing workflow without Python pre-installation.
  New `uv-only` job in variants workflow verifies that `make install` works
  with only UV installed (no Python) on Python 3.10 and 3.14, proving the
  UV-only team workflow documented in getting-started.md.
- Docs: Complete overhaul of installation documentation. Document UV-only workflow
  requiring no Python pre-installation. Simplify UV configuration examples to show
  only required settings (PYTHON_PACKAGE_INSTALLER and UV_PYTHON). Add migration guide,
  FAQ/troubleshooting section, and clarify when PYTHON_MIN_VERSION/PRIMARY_PYTHON
  settings are needed vs. optional.
- Chore: Migrate to hatch-vcs for automated versioning from git tags.

## 1.3.0 (2025-09-03)

- Introduce testargs for pytest to have more control over the test and pass it args.

## 1.2.2 (2025-06-30)

- Fix `pyrefly` domain.

- Fix pytest related test and coverage script generation bugs introduced in 1.2.1.

## 1.2.1 (2025-06-23)

- Fix test-script to not end with backslash if there is no `testpaths` (which is valid).
  Improve tests to cover more edge cases, i.e. above and multi-line.
- Improve test to read large amount of output from file (Makefile template check).
- Fix Python check for global UV and use PRIMARY_PYTHON for UV as version definition.

## 1.2.0 (2025-06-04)

- add `pyrefly` type checker support.

## 1.1.0 (2025-03-20)

- Chore: Build-system update and minor cleanups.

- Feature: Add help system (make help).

- Feature: Add target `zope-adduser` to create an emergency user.

## 1.0 (2025-02-11)

- Chore: Add release workflow.

- Fix `zope.mk`, wrong config file was passed to zconsole.
  Now zope-debug and zope-runscript are functional.

## 1.0a8 (2024-10-24)

- Fix preseed value reading.

## 1.0a7 (2024-10-24)

- Add proxy target support.

**Breaking changes**

- Rename `npm` domain to `nodejs` and add support for using `pnpm` as
  alternative package manager.

## 1.0a6 (2024-08-02)

- Fix bug in `Template.write` when creating target folders to also create
  parent folders if not exists.

- Add support for preseeds configuration files.

- Add `plone-site` template configuration to `mx.ini` template.

- More fine grained control over plone site creation and purging.

- Drop Python 3.8 and set all defaults to a Python 3.9 minimum.

## 1.0a5 (2024-06-07)

- Export `OS` environment variable in `mxenv` domain to prevent warning on
  sub make calls.

- Add `LINGUA_OPTIONS` setting to `lingua` domain in `i18n` topic. Can be used
  for passing additional command line options to `pot-create`.

- Perform `mxenv` domain related checks inside target to support setups
  which install their own python environment.

- Add `Makefile` as dependency target for `SENTINEL` target to make sure
  target execution if Makefile changes.

- Depend on `mxdev>=4.0.2`, which fixes the deprecation of `pkg_resources` and
  use the provided infrastructure of mxdev to handle entry_points in mxmake.

- Add Plone site creation and purging in new `plone` domain.

## 1.0a4 (2024-03-12)

- Add experimental windows support.

- Support `mxmake update` command, updating the Makefile without prompting for
  settings.

- Use importlib.metadata to load entrypoints.

- Add support for uv as fast alternative to pip #25.

- Remove Python 3.7 from CI. Still works though.

- Run test on GH-Actions on platform macos-latest.

- Use `pathlib.Path` instead of `os.path`.

- Add `EXTRA_PATH` setting to `base` domain in `core` topic. Can be used to
  specify additional directories added to environment `PATH`.

- Export `PATH` with virtual environment and node modules bin folders.

- Get rid of `MXENV_PATH`.

- Rename `PYTHON_BIN` to `PRIMARY_PYTHON` in `mxenv` domain.

- Introduce `MXENV_PYTHON`. It defines the Python executable used for mxmake
  operations.

- Remove ruff cache when running `make ruff-clean` target.

- Fix #20: make VENV_ENABLED=false test does not work.

- Add `wtr` (Web test runner) domain to `js` topic.

- Add pyupgrade based code formatter, see https://pypi.org/project/pyupgrade/.

- Add `ZOPE_TEMPLATE_CHECKOUT` option to zope domain to allow pinning to a tag,
  branch or revision (uses cookiecutter `--checkout`). If empty, do not apply
  `--checkout` option.

- Add phony target `cookiecutter` to be able to just install it.

- Add feature to pass options to zest-releaser commands.

- Change default for venv folder to `.venv`, since this is established practice.

## 1.0a3 (2024-02-06)

- Add `typecheck` target and use it for mypy instead of `check` target.

- Add basic CI config file generation for github actions.

- Add `ruff` domain to `qa` topic.

- Fix exporting path in `jsdoc` target.

## 1.0a2 (2023-07-07)

- Add support for `pip.conf` file.

- Fixes #18: VENV_CREATE is ignored.

- Fix error when new source package gets added to `mx.ini` in
  `Hook.generate_additional_sources_targets`.

- Add `PROJECT_CONFIG` as the dependency target of `SOURCES_TARGET` to make
  sure the target runs when a new source package gets added to `mx.ini`.

## 1.0a1 (2023-05-05)

- Add `zest-releaser` domain to `applications` topic.

- Support custom makefile include.

- Support `pytest` as a test runner and make it default if not configured
  otherwise.

- Add `RUN_TARGET` setting to `base` domain and generate `run` target in
  `Makefile`.

- Create `twisted` domain in `applications` topic.

- Test and coverage templates consider `mxmake-test-path`, `mxmake-source-path`
  and `mxmake-omit-path` in `settings` section of `mx.ini` to support inclusion
  of local package in `run-tests.sh` and `run-coverage.sh` scripts.

- Create `scss` domain in `js` topic.

- Create `gettext` domain in `i18n` topic.

- Create `lingua` domain in `i18n` topic.

- Conditional add local [requirement|constraints}.txt to LOCAL_PACKAGE_FILES.

- Generate one Makefile from snippets instead of including several files from
  subfolder.

- Semantic overhaul. "Domains" become "Topics" and "Makefile" becomes "Domain".

- Use inquirer to configure included domains and targets.

- Generate initial `mx.ini` config file.

- Generate "Topic" and "Domain" docs.

- Change docs format from `rst` to `md`.

- Rename `_SENTINEL` to `_TARGET` in domains.

- generic `install` `dirty` and `clean` targets in main makefile template.

- Rename `.sentinels` folder to `.mxmake-sentinels`.

- Provide a set of default targets and a mechanism to extend it's dependency
  targets in domain make files.

- Rename `install` domain to `packages`.

- Rename `files` domain to `mxfiles`.

- Rename `venv` domain to `mxenv`.

- Extend hook to generate `sources` dependency targets for package reinstall
  (setup.py, setup.cfg, pyproject.toml, requirements.txt, constraints.txt).

- Move `tests` and `coverage` domains to `qa` topic.

- Create `black`, `mypy`, `isort` and domains in `qa` topic.

- Move `system-dependencies` to `system` topic.

- Rename `docs` domain to `sphinx` and move to `docs` topic.

- Create `zpretty` domains in `qa` topic.

- Add topic related metadata containing a topic description.

- Create `npm` domains in `js` topic.

- Create `jsdoc` domain, in `docs` topic.

- Create `rollup` domains in `js` topic.

- Create `karma` domain, in `js` topic.

- Create `zope` domain, in `applications` topic.

- Add `soft-depends` setting in domains to define conditional order of domain
  rendering.

- Make `sources` target an optional dependency.

- Extend makefile parser to provide multi line settings.

- Take local package into account to "dirty" if there (pyproject.toml,
  setup.[cfg|py]

- Check for the existence of pip in `*-clean` targets before uninstalling a
  package, to ensure the targets are working when running via the default
  `clean` target, where the entire virtual env gets removed.

- Remove redundant dependencies from `zope` domain.

- `sources` domain is now a soft dependency of `mxfiles` domain instead of the
  `packages` domain. This ensures source package checkout happens before mxmake
  generates files, because templates might gain information from source
  packages if present.

- `karma` and `rollup` targets depend on `NPM_TARGET` now.

## 0.1 (2022-05-19)

- Initial release.
