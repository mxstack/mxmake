# Changelog

## 1.0a4 (2024-03-12)

- Add experimental windows support.

- Support `mxmake update` command, updating the Makefile without prompting for settings.

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

- Introduce `MXENV_PYTHON`. It defines the Python executable used for mxmake operations.

- Remove ruff cache when running `make ruff-clean` target.

- Fix #20: make VENV_ENABLED=false test does not work.

- Add `wtr` (Web test runner) domain to `js` topic.

- Add pyupgrade based code formatter, see https://pypi.org/project/pyupgrade/.

- Add `ZOPE_TEMPLATE_CHECKOUT` option to zope domain to allow pinning to a tag, branch or revision (uses cookiecutter `--checkout`).
  If empty, do not apply `--checkout` option.

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
