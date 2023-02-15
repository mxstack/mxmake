# Changelog

## 1.0a1 (unreleased)

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
