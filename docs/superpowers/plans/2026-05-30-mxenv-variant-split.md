# mxenv pip/uv Variant Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the single, heavily-branched `core.mxenv` domain with a shared base plus two thin environment variants (pip and uv), and move dev-tool execution behind variant-provided macros so QA tool files stay world-agnostic.

**Architecture:** Three domains — `core.mxenv` (base: shared infra + the macro interface), `core.mxenv-pip`, `core.mxenv-uv` (variants: env provisioning + macro definitions). Every other domain keeps `depends = core.mxenv`. Exactly one variant must be selected; the CLI enforces this and emits the selected variant immediately after the base so its parse-time variable definitions are visible to downstream domains. Style/format QA tools run through `RUN_TOOL`/`INSTALL_TOOL`/`UNINSTALL_TOOL` macros; type-checkers always install into the environment.

**Tech Stack:** GNU Make snippet templates (`.mk`), Python 3.10+, Jinja2 templates, pytest.

**Reference spec:** `docs/superpowers/specs/2026-05-30-mxenv-environment-variant-split-design.md`

---

## Background the implementer needs

- Domain snippets live in `src/mxmake/topics/<topic>/<name>.mk`. The file stem is the domain name; metadata is in `#:`-prefixed comment lines at the top. Snippet bodies are emitted **verbatim** (minus `#:` lines) by `src/mxmake/topics.py::Domain.write_to`.
- A domain declares hard deps with `#:depends = <fqn>` and settings with `#:[setting.NAME]` / `#:default = …`. Settings render into the generated Makefile as `NAME?=default` lines.
- Dependency resolution: `collect_missing_dependencies` (adds transitive hard deps), `set_domain_runtime_depends`, then `resolve_domain_dependencies` (topological order). All in `src/mxmake/topics.py`.
- The generated Makefile header lists selected domains as `#: <fqn>` lines (template `src/mxmake/templates/Makefile`, loop `{% for fqn in fqns %}`). The parser reads them back in `src/mxmake/parser.py::parse_fqns`. This is what makes "swap the variant line + `mxmake update`" work.
- `make` reads the entire Makefile before running. Therefore: variables/macros used only inside **recipes** (`$(call …)` on a recipe line) are expanded at run time and are order-independent. Variables used at **parse time** (`:=` assignments, `ifeq`) must be defined earlier in the file. `packages.mk` uses `ifeq ("$(PYTHON_PACKAGE_INSTALLER)","uv")` at parse time, so the variant (which defines `PYTHON_PACKAGE_INSTALLER`) must be emitted before `packages.mk`. Dependency chain: `core.base → core.mxenv → core.mxfiles → core.packages`, and every QA tool depends on `core.mxenv`, so emitting the variant right after `core.mxenv` guarantees it precedes all of them.
- The five **style/format** tools converted to macros: `ruff`, `isort`, `black`, `zpretty`, `pyupgrade`. The three **type-checkers** left installing into the env: `mypy`, `ty`, `pyrefly`. `test` and `coverage` are unchanged.
- Run the test suite with: `uv run pytest src/mxmake/tests/ -q` (or `make test`). Single test: `uv run pytest src/mxmake/tests/test_templates.py::TestTemplates::test_Makefile -q`.

---

## File Structure

**Modified:**
- `src/mxmake/topics/core/mxenv.mk` — becomes the **base**: shared infra + the macro interface declaration. Loses the package-installer detection, uv detection, and the `$(MXENV_TARGET)` recipe (those move to variants).
- `src/mxmake/topics/qa/ruff.mk`, `isort.mk`, `black.mk`, `zpretty.mk`, `pyupgrade.mk` — use the tool macros.
- `src/mxmake/main.py` — call the new enforcement + ordering helpers in `create_config`.
- `src/mxmake/tests/test_templates.py`, `test_parser.py`, `test_topics.py` — cover variants + helpers.
- `src/mxmake/tests/expected/Makefile` — regenerated for the pip variant.
- `CHANGES.md`, `docs/source/migration.md` — major-release notes.

**Created:**
- `src/mxmake/topics/core/mxenv-pip.mk` — pip variant.
- `src/mxmake/topics/core/mxenv-uv.mk` — uv variant.
- `src/mxmake/tests/expected/Makefile-uv` — fixture for the uv variant.

---

## Phase A — Tool-execution macros (non-breaking)

Introduce the macros in the **current single** `mxenv.mk` with definitions that reproduce today's behavior exactly, and route the five style/format tools through them. No behavior change; this isolates the tool-file edits from the structural split.

### Task A1: Add tool-execution macros to mxenv.mk

**Files:**
- Modify: `src/mxmake/topics/core/mxenv.mk` (insert after the package-installer detection block, currently ending at line ~103, before the "Auto-detect global uv" block)

- [ ] **Step 1: Add the macro block**

Insert this block immediately after the `PYTHON_PACKAGE_COMMAND` detection `endif` (after current line 103):

```makefile

##############################################################################
# Dev tool execution macros
##############################################################################

# Control how QA dev tools (ruff, isort, ...) are installed and invoked.
# Default behavior: install the tool into the environment, invoke it directly.
# Environment variants may redefine these (e.g. to run via uvx).
#   INSTALL_TOOL(name)            -> shell command to make the tool available
#   RUN_TOOL(name,version,args)   -> shell command to invoke the tool
#   UNINSTALL_TOOL(name)          -> shell command to remove the tool
INSTALL_TOOL=$(PYTHON_PACKAGE_COMMAND) install $(1)
RUN_TOOL=$(1) $(3)
UNINSTALL_TOOL=test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y $(1) || :
```

- [ ] **Step 2: Regenerate the expected fixture**

The `test_Makefile` fixture renders `core.mxenv` alone, so it must include the new macro block. Regenerate it:

Run: `uv run pytest src/mxmake/tests/test_templates.py::TestTemplates::test_Makefile -q`
Expected: FAIL with a unified diff showing the new macro block missing from the fixture.

- [ ] **Step 3: Update the fixture**

Copy the macro block (verbatim, without the `#:`-free transformation — it has no `#:` lines) into `src/mxmake/tests/expected/Makefile` at the same relative position (after the `PYTHON_PACKAGE_COMMAND` detection block, before the uv auto-detect block). Match indentation/spacing exactly to the generator output shown in the failing diff.

- [ ] **Step 4: Verify the fixture test passes**

Run: `uv run pytest src/mxmake/tests/test_templates.py::TestTemplates::test_Makefile -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/mxmake/topics/core/mxenv.mk src/mxmake/tests/expected/Makefile
git commit -m "Add tool-execution macros to mxenv (no behavior change)"
```

### Task A2: Route ruff through the macros

**Files:**
- Modify: `src/mxmake/topics/qa/ruff.mk`

- [ ] **Step 1: Replace install, invocation, and uninstall lines**

Change the install recipe line:
```makefile
	@$(PYTHON_PACKAGE_COMMAND) install ruff
```
to:
```makefile
	@$(call INSTALL_TOOL,ruff)
```

Change the three invocation lines in `ruff-check` / `ruff-format`:
```makefile
	@ruff check $(RUFF_SRC)
```
to:
```makefile
	@$(call RUN_TOOL,ruff,,check $(RUFF_SRC))
```
and
```makefile
	@ruff format $(RUFF_SRC)
```
to:
```makefile
	@$(call RUN_TOOL,ruff,,format $(RUFF_SRC))
```
and
```makefile
	@ruff check $(RUFF_FIX_FLAGS) $(RUFF_SRC)
```
to:
```makefile
	@$(call RUN_TOOL,ruff,,check $(RUFF_FIX_FLAGS) $(RUFF_SRC))
```

Change the uninstall line in `ruff-clean`:
```makefile
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y ruff || :
```
to:
```makefile
	@$(call UNINSTALL_TOOL,ruff)
```

- [ ] **Step 2: Verify generation still works and the tool runs**

Generate a Makefile exercising ruff in a temp project and run it:

```bash
tmp=$(mktemp -d); cd "$tmp"
printf 'topics:\n  core:\n    base: {}\n    mxenv: {PYTHON_PACKAGE_INSTALLER: pip}\n  qa:\n    ruff: {}\n' > seeds.yaml
uv run --project /home/jensens/ws/cdev/mxmake mxmake init --preseeds seeds.yaml
grep -n "call RUN_TOOL,ruff\|RUN_TOOL=" Makefile
cd - >/dev/null
```
Expected: the generated `Makefile` contains `$(call RUN_TOOL,ruff,,check ...)` and the `RUN_TOOL=$(1) $(3)` definition (so the effective command is `ruff check ...`, unchanged behavior).

- [ ] **Step 3: Run the project's own QA to confirm no regression**

Run: `make check`
Expected: ruff runs and passes as before.

- [ ] **Step 4: Commit**

```bash
git add src/mxmake/topics/qa/ruff.mk
git commit -m "Route ruff through tool-execution macros"
```

### Task A3: Route isort through the macros

**Files:**
- Modify: `src/mxmake/topics/qa/isort.mk`

- [ ] **Step 1: Replace the lines**

`@$(PYTHON_PACKAGE_COMMAND) install isort` → `@$(call INSTALL_TOOL,isort)`
`@isort --check $(ISORT_SRC)` → `@$(call RUN_TOOL,isort,,--check $(ISORT_SRC))`
`@isort $(ISORT_SRC)` → `@$(call RUN_TOOL,isort,,$(ISORT_SRC))`
`@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y isort || :` → `@$(call UNINSTALL_TOOL,isort)`

- [ ] **Step 2: Verify**

Run: `make check`
Expected: isort runs and passes.

- [ ] **Step 3: Commit**

```bash
git add src/mxmake/topics/qa/isort.mk
git commit -m "Route isort through tool-execution macros"
```

### Task A4: Route black through the macros

**Files:**
- Modify: `src/mxmake/topics/qa/black.mk`

- [ ] **Step 1: Replace the lines**

`@$(PYTHON_PACKAGE_COMMAND) install black` → `@$(call INSTALL_TOOL,black)`
`@black --check $(BLACK_SRC)` → `@$(call RUN_TOOL,black,,--check $(BLACK_SRC))`
`@black $(BLACK_SRC)` → `@$(call RUN_TOOL,black,,$(BLACK_SRC))`
`@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y black || :` → `@$(call UNINSTALL_TOOL,black)`

- [ ] **Step 2: Verify generation**

```bash
tmp=$(mktemp -d); cd "$tmp"
printf 'topics:\n  core:\n    base: {}\n    mxenv: {}\n  qa:\n    black: {}\n' > seeds.yaml
uv run --project /home/jensens/ws/cdev/mxmake mxmake init --preseeds seeds.yaml
grep -n "call RUN_TOOL,black\|call INSTALL_TOOL,black" Makefile
cd - >/dev/null
```
Expected: macro calls present for black.

- [ ] **Step 3: Commit**

```bash
git add src/mxmake/topics/qa/black.mk
git commit -m "Route black through tool-execution macros"
```

### Task A5: Route zpretty through the macros

**Files:**
- Modify: `src/mxmake/topics/qa/zpretty.mk`

- [ ] **Step 1: Replace the lines**

`@$(PYTHON_PACKAGE_COMMAND) install zpretty` → `@$(call INSTALL_TOOL,zpretty)`
`@find $(ZPRETTY_SRC) -name '*.zcml' -or -name '*.xml' -exec zpretty --check {} +` → `@find $(ZPRETTY_SRC) -name '*.zcml' -or -name '*.xml' -exec $(call RUN_TOOL,zpretty,,--check {}) +`
`@find $(ZPRETTY_SRC) -name '*.zcml' -or -name '*.xml' -exec zpretty -i {} +` → `@find $(ZPRETTY_SRC) -name '*.zcml' -or -name '*.xml' -exec $(call RUN_TOOL,zpretty,,-i {}) +`
`@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y zpretty || :` → `@$(call UNINSTALL_TOOL,zpretty)`

Note: with the default `RUN_TOOL=$(1) $(3)`, `$(call RUN_TOOL,zpretty,,--check {})` expands to `zpretty --check {}`, identical to today. Under uvx it becomes `uvx zpretty --check {}` per `find ... -exec`, which is correct.

- [ ] **Step 2: Verify generation**

```bash
tmp=$(mktemp -d); cd "$tmp"
printf 'topics:\n  core:\n    base: {}\n    mxenv: {}\n  qa:\n    zpretty: {}\n' > seeds.yaml
uv run --project /home/jensens/ws/cdev/mxmake mxmake init --preseeds seeds.yaml
grep -n "RUN_TOOL,zpretty" Makefile
cd - >/dev/null
```
Expected: `-exec zpretty --check {} +` style line present via the macro.

- [ ] **Step 3: Commit**

```bash
git add src/mxmake/topics/qa/zpretty.mk
git commit -m "Route zpretty through tool-execution macros"
```

### Task A6: Route pyupgrade through the macros

**Files:**
- Modify: `src/mxmake/topics/qa/pyupgrade.mk`

- [ ] **Step 1: Replace the lines**

`@$(PYTHON_PACKAGE_COMMAND) install pyupgrade` → `@$(call INSTALL_TOOL,pyupgrade)`
`@find $(PYUPGRADE_SRC) -name '*.py' -exec pyupgrade $(PYUPGRADE_PARAMETERS) {} +` → `@find $(PYUPGRADE_SRC) -name '*.py' -exec $(call RUN_TOOL,pyupgrade,,$(PYUPGRADE_PARAMETERS) {}) +`
`@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y pyupgrade || :` → `@$(call UNINSTALL_TOOL,pyupgrade)`

- [ ] **Step 2: Run the full suite to confirm Phase A is green**

Run: `uv run pytest src/mxmake/tests/ -q`
Expected: PASS (the only fixture touched was `expected/Makefile` in A1; tool files are not in any fixture).

- [ ] **Step 3: Commit**

```bash
git add src/mxmake/topics/qa/pyupgrade.mk
git commit -m "Route pyupgrade through tool-execution macros"
```

---

## Phase B — Split mxenv into base + pip/uv variants

### Task B1: Reduce mxenv.mk to the shared base

**Files:**
- Modify: `src/mxmake/topics/core/mxenv.mk`

- [ ] **Step 1: Remove the variant-specific settings from the metadata block**

Delete the `#:[setting.PYTHON_PACKAGE_INSTALLER]` block (current lines 36-42) and the `#:[setting.UV_PYTHON]` block (current lines 44-49) from the `#:` header. Keep `PRIMARY_PYTHON`, `PYTHON_MIN_VERSION`, `VENV_ENABLED`, `VENV_CREATE`, `VENV_FOLDER`, `MXDEV`, `MXMAKE`.

- [ ] **Step 2: Remove variant-specific body sections**

Delete from the body:
- the package-installer detection block (`# Determine the package installer …` `ifeq ("$(PYTHON_PACKAGE_INSTALLER)","uv") … endif`, current lines 98-103)
- the uv auto-detect + strategy + outdated blocks (current lines 105-125)
- the entire `$(MXENV_TARGET): $(SENTINEL)` rule and its recipe (current lines 127-173)

Keep: the `MXENV_PYTHON` determination block (lines 82-96), the tool-execution macro block from Task A1, and the phony `mxenv` / `mxenv-dirty` / `mxenv-clean` targets and the `INSTALL_TARGETS`/`DIRTY_TARGETS`/`CLEAN_TARGETS` registrations (lines 175-195).

- [ ] **Step 3: Add the `MXENV_TARGET` variable declaration and an interface comment**

Where the removed rule was, add only the variable declaration plus a comment documenting that variants provide the rule and macros:

```makefile
##############################################################################
# Environment provisioning interface
##############################################################################

# The selected environment variant (core.mxenv-pip or core.mxenv-uv) provides:
#   - PYTHON_PACKAGE_INSTALLER  (pip|uv)
#   - PYTHON_PACKAGE_COMMAND    (installer command)
#   - the $(MXENV_TARGET) rule  (creates the environment)
#   - INSTALL_TOOL / RUN_TOOL / UNINSTALL_TOOL macro definitions
MXENV_TARGET:=$(SENTINEL_FOLDER)/mxenv.sentinel
```

- [ ] **Step 4: Move the default macro definitions OUT of the base**

The macros added in A1 are the *default (pip-style)* definitions; they now belong to the variants. Delete the `INSTALL_TOOL` / `RUN_TOOL` / `UNINSTALL_TOOL` assignment lines from the base macro block, but keep the explanatory comment header (so the base documents the interface). The base must NOT define `PYTHON_PACKAGE_COMMAND` or the macros — variants do.

- [ ] **Step 5: Update the base metadata depends (unchanged) and description**

Change the `#:description` to: `Python environment management. Requires exactly one environment variant (core.mxenv-pip or core.mxenv-uv).` Keep `#:depends = core.base`.

- [ ] **Step 6: Commit (fixtures fixed in B4)**

```bash
git add src/mxmake/topics/core/mxenv.mk
git commit -m "Reduce core.mxenv to shared environment base"
```

### Task B2: Create the pip variant

**Files:**
- Create: `src/mxmake/topics/core/mxenv-pip.mk`

- [ ] **Step 1: Write the pip variant**

```makefile
#:[mxenv-pip]
#:title = MX Environment (pip)
#:description = Provision the Python environment with pip. Legacy/fallback path.
#:depends = core.mxenv
#:soft-depends =
#:  core.mxenv-uv

##############################################################################
# mxenv-pip
##############################################################################

# Internal: identify the active installer for downstream domains.
PYTHON_PACKAGE_INSTALLER:=pip
PYTHON_PACKAGE_COMMAND=$(MXENV_PYTHON) -m pip

# Tool execution: install into the environment, invoke directly.
INSTALL_TOOL=$(PYTHON_PACKAGE_COMMAND) install $(1)
RUN_TOOL=$(1) $(3)
UNINSTALL_TOOL=test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y $(1) || :

$(MXENV_TARGET): $(SENTINEL)
	# Validation: Python version
	@$(PRIMARY_PYTHON) -c "import sys; vi = sys.version_info; sys.exit(1 if (int(vi[0]), int(vi[1])) >= tuple(map(int, '$(PYTHON_MIN_VERSION)'.split('.'))) else 0)" \
		&& echo "Need Python >= $(PYTHON_MIN_VERSION)" && exit 1 || :
	# Validation: VENV_FOLDER set when venv enabled
	@[[ "$(VENV_ENABLED)" == "true" && "$(VENV_FOLDER)" == "" ]] \
		&& echo "VENV_FOLDER must be configured if VENV_ENABLED is true" && exit 1 || :
ifeq ("$(VENV_ENABLED)", "true")
ifeq ("$(VENV_CREATE)", "true")
	@echo "Setup Python Virtual Environment using module 'venv' at '$(VENV_FOLDER)'"
	@$(PRIMARY_PYTHON) -m venv $(VENV_FOLDER)
	@$(MXENV_PYTHON) -m ensurepip -U
endif
else
	@echo "Using system Python interpreter"
endif
	@$(PYTHON_PACKAGE_COMMAND) install -U pip setuptools wheel
	@echo "Install/Update MXStack Python packages"
	@$(PYTHON_PACKAGE_COMMAND) install -U $(MXDEV) $(MXMAKE)
	@touch $(MXENV_TARGET)
```

Note on `soft-depends`: it does not force selection; it only influences ordering when both are present (they never are). The "exactly one" guarantee is enforced in Python (Task B5).

- [ ] **Step 2: Verify the variant loads as a domain**

Run: `uv run python -c "from mxmake.topics import get_domain; d=get_domain('core.mxenv-pip'); print(d.fqn, d.depends)"`
Expected: `core.mxenv-pip ['core.mxenv']`

- [ ] **Step 3: Commit**

```bash
git add src/mxmake/topics/core/mxenv-pip.mk
git commit -m "Add core.mxenv-pip variant"
```

### Task B3: Create the uv variant

**Files:**
- Create: `src/mxmake/topics/core/mxenv-uv.mk`

- [ ] **Step 1: Write the uv variant**

```makefile
#:[mxenv-uv]
#:title = MX Environment (uv)
#:description = Provision the Python environment with uv. Default path.
#:depends = core.mxenv
#:soft-depends =
#:  core.mxenv-pip
#:
#:[setting.UV_PYTHON]
#:description = Python version for uv to install/use when creating the virtual
#:  environment. Passed to `uv venv -p VALUE`. Supports specs like `3.11`,
#:  `3.14`, `cpython@3.14`.
#:default = $(PRIMARY_PYTHON)
#:
#:[setting.UV_PROVISION]
#:description = How uv provisions the environment. `pip` (default) installs
#:  mxdev/mxmake with `uv pip install` (works for existing projects). `sync`
#:  uses `uv sync` against pyproject.toml/uv.lock (project-native, new projects).
#:default = pip
#:
#:[setting.TOOL_EXECUTION]
#:description = How style/format QA tools (ruff, isort, ...) are executed.
#:  `uvx` (default) runs them ephemerally without installing into the venv.
#:  `venv` installs them into the environment with `uv pip install`.
#:default = uvx

##############################################################################
# mxenv-uv
##############################################################################

# Internal: identify the active installer for downstream domains.
PYTHON_PACKAGE_INSTALLER:=uv
PYTHON_PACKAGE_COMMAND=uv pip --no-progress

# Tool execution depends on TOOL_EXECUTION.
ifeq ("$(TOOL_EXECUTION)","uvx")
INSTALL_TOOL=:
RUN_TOOL=uvx $(1)$(if $(strip $(2)),==$(strip $(2)),) $(3)
UNINSTALL_TOOL=:
else
INSTALL_TOOL=$(PYTHON_PACKAGE_COMMAND) install $(1)
RUN_TOOL=$(1) $(3)
UNINSTALL_TOOL=uv pip uninstall $(1) || :
endif

$(MXENV_TARGET): $(SENTINEL)
	# Validation: uv must be available
	@command -v uv >/dev/null 2>&1 \
		|| { echo "uv not found. Install uv or switch to core.mxenv-pip."; exit 1; }
	# Validation: VENV_FOLDER set when venv enabled
	@[[ "$(VENV_ENABLED)" == "true" && "$(VENV_FOLDER)" == "" ]] \
		&& echo "VENV_FOLDER must be configured if VENV_ENABLED is true" && exit 1 || :
ifeq ("$(VENV_ENABLED)", "true")
ifeq ("$(VENV_CREATE)", "true")
	@echo "Setup Python Virtual Environment using uv at '$(VENV_FOLDER)'"
	@uv venv --allow-existing --no-progress -p $(UV_PYTHON) --seed $(VENV_FOLDER)
endif
else
	@echo "Using system Python interpreter"
endif
ifeq ("$(UV_PROVISION)","sync")
	@echo "Provision environment with uv sync"
	@uv sync
else
	@$(PYTHON_PACKAGE_COMMAND) install -U pip setuptools wheel
	@echo "Install/Update MXStack Python packages"
	@$(PYTHON_PACKAGE_COMMAND) install -U $(MXDEV) $(MXMAKE)
endif
	@touch $(MXENV_TARGET)
```

- [ ] **Step 2: Verify the variant loads**

Run: `uv run python -c "from mxmake.topics import get_domain; d=get_domain('core.mxenv-uv'); print(d.fqn, [s.name for s in d.settings])"`
Expected: `core.mxenv-uv ['UV_PYTHON', 'UV_PROVISION', 'TOOL_EXECUTION']`

- [ ] **Step 3: Commit**

```bash
git add src/mxmake/topics/core/mxenv-uv.mk
git commit -m "Add core.mxenv-uv variant"
```

### Task B4: Add variant enforcement and ordering helpers

**Files:**
- Modify: `src/mxmake/topics.py` (add two functions near `collect_missing_dependencies`, around line 276)
- Test: `src/mxmake/tests/test_topics.py`

- [ ] **Step 1: Write failing tests**

Add to `src/mxmake/tests/test_topics.py`:

```python
def test_ensure_environment_variant_injects_default(self):
    from mxmake import topics
    domains = topics.collect_missing_dependencies([topics.get_domain("qa.ruff")])
    fqns_before = {d.fqn for d in domains}
    assert "core.mxenv" in fqns_before
    assert not (fqns_before & {"core.mxenv-pip", "core.mxenv-uv"})
    result = topics.ensure_environment_variant(domains)
    fqns = {d.fqn for d in result}
    assert "core.mxenv-uv" in fqns
    assert "core.mxenv-pip" not in fqns

def test_ensure_environment_variant_preserves_existing(self):
    from mxmake import topics
    domains = topics.collect_missing_dependencies(
        [topics.get_domain("qa.ruff"), topics.get_domain("core.mxenv-pip")]
    )
    result = topics.ensure_environment_variant(domains)
    fqns = {d.fqn for d in result}
    assert "core.mxenv-pip" in fqns
    assert "core.mxenv-uv" not in fqns

def test_ensure_environment_variant_rejects_two(self):
    from mxmake import topics
    domains = [
        topics.get_domain("core.mxenv"),
        topics.get_domain("core.mxenv-pip"),
        topics.get_domain("core.mxenv-uv"),
    ]
    with self.assertRaises(topics.EnvironmentVariantError):
        topics.ensure_environment_variant(domains)

def test_order_environment_variant_after_base(self):
    from mxmake import topics
    domains = topics.collect_missing_dependencies(
        [topics.get_domain("qa.ruff"), topics.get_domain("core.mxenv-uv")]
    )
    topics.set_domain_runtime_depends(domains)
    ordered = topics.resolve_domain_dependencies(domains)
    ordered = topics.order_environment_variant(ordered)
    fqns = [d.fqn for d in ordered]
    assert fqns.index("core.mxenv-uv") == fqns.index("core.mxenv") + 1
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest src/mxmake/tests/test_topics.py -k environment -q`
Expected: FAIL with `AttributeError: module 'mxmake.topics' has no attribute 'ensure_environment_variant'`

- [ ] **Step 3: Implement the helpers**

Add to `src/mxmake/topics.py` (after `collect_missing_dependencies`):

```python
ENVIRONMENT_BASE = "core.mxenv"
ENVIRONMENT_VARIANTS = ("core.mxenv-pip", "core.mxenv-uv")
ENVIRONMENT_DEFAULT_VARIANT = "core.mxenv-uv"


class EnvironmentVariantError(Exception):
    """More than one environment variant selected."""

    def __init__(self, selected: list[str]):
        super().__init__(
            f"Exactly one environment variant required, got: {sorted(selected)}"
        )


def ensure_environment_variant(domains: list[Domain]) -> list[Domain]:
    """Ensure exactly one environment variant is present when the environment
    base is in use. Inject the default variant if none is selected; raise if
    more than one is selected.
    """
    fqns = {domain.fqn for domain in domains}
    if ENVIRONMENT_BASE not in fqns:
        return domains
    selected = [v for v in ENVIRONMENT_VARIANTS if v in fqns]
    if len(selected) > 1:
        raise EnvironmentVariantError(selected)
    if not selected:
        return domains + [get_domain(ENVIRONMENT_DEFAULT_VARIANT)]
    return domains


def order_environment_variant(domains: list[Domain]) -> list[Domain]:
    """Move the selected environment variant immediately after the base so its
    parse-time variable definitions are visible to all downstream domains.
    """
    fqns = [domain.fqn for domain in domains]
    if ENVIRONMENT_BASE not in fqns:
        return domains
    variant = next((v for v in ENVIRONMENT_VARIANTS if v in fqns), None)
    if variant is None:
        return domains
    ordered = [d for d in domains if d.fqn != variant]
    base_idx = [d.fqn for d in ordered].index(ENVIRONMENT_BASE)
    variant_domain = next(d for d in domains if d.fqn == variant)
    ordered.insert(base_idx + 1, variant_domain)
    return ordered
```

- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest src/mxmake/tests/test_topics.py -k environment -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/mxmake/topics.py src/mxmake/tests/test_topics.py
git commit -m "Add environment variant enforcement and ordering helpers"
```

### Task B5: Wire the helpers into create_config

**Files:**
- Modify: `src/mxmake/main.py` (imports near line 7-13; `create_config` around lines 188-190)

- [ ] **Step 1: Add imports**

Add to the topics imports block:
```python
from .topics import ensure_environment_variant
from .topics import order_environment_variant
```

- [ ] **Step 2: Call the helpers in create_config**

Replace (current lines 188-190):
```python
    domains = collect_missing_dependencies(domains)
    set_domain_runtime_depends(domains)
    domains = resolve_domain_dependencies(domains)
```
with:
```python
    domains = collect_missing_dependencies(domains)
    domains = ensure_environment_variant(domains)
    set_domain_runtime_depends(domains)
    domains = resolve_domain_dependencies(domains)
    domains = order_environment_variant(domains)
```

- [ ] **Step 3: Functional check — fresh init picks uv, no variant chosen**

```bash
tmp=$(mktemp -d); cd "$tmp"
printf 'topics:\n  core:\n    base: {}\n    mxenv: {}\n  qa:\n    ruff: {}\n' > seeds.yaml
uv run --project /home/jensens/ws/cdev/mxmake mxmake init --preseeds seeds.yaml
grep -n "^#: core.mxenv" Makefile
cd - >/dev/null
```
Expected: header lists `#: core.mxenv` **and** `#: core.mxenv-uv` (default injected), with `core.mxenv-uv` emitted right after `core.mxenv` in the body (check the `PYTHON_PACKAGE_INSTALLER:=uv` line appears before the `packages` section if qa pulls it in).

- [ ] **Step 4: Commit**

```bash
git add src/mxmake/main.py
git commit -m "Enforce and order environment variant during generation"
```

### Task B6: Update fixtures and template tests for both variants

**Files:**
- Modify: `src/mxmake/tests/test_templates.py` (`test_Makefile`, around lines 551-588)
- Modify: `src/mxmake/tests/expected/Makefile`
- Create: `src/mxmake/tests/expected/Makefile-uv`
- Modify: `src/mxmake/tests/test_parser.py` (the `core.mxenv.*` settings expectations, around lines 27 and 75)

- [ ] **Step 1: Update test_Makefile to render the pip variant explicitly**

Replace the domain setup in `test_Makefile`:
```python
        domains = [topics.get_domain("core.mxenv")]
        domains = topics.collect_missing_dependencies(domains)
        domains = topics.resolve_domain_dependencies(domains)
```
with:
```python
        domains = [topics.get_domain("core.mxenv-pip")]
        domains = topics.collect_missing_dependencies(domains)
        domains = topics.ensure_environment_variant(domains)
        topics.set_domain_runtime_depends(domains)
        domains = topics.resolve_domain_dependencies(domains)
        domains = topics.order_environment_variant(domains)
```

Remove the obsolete settings `core.mxenv.PYTHON_PACKAGE_INSTALLER` and `core.mxenv.UV_PYTHON` from `domain_settings` (those settings no longer exist on the base). Keep the remaining `core.mxenv.*` settings.

- [ ] **Step 2: Run to get the new expected output, then save the fixture**

Run: `uv run pytest src/mxmake/tests/test_templates.py::TestTemplates::test_Makefile -q`
Expected: FAIL with a unified diff. Inspect the diff and the generated file (the test prints `Makefile written to <tmp>`). Verify by eye that: (a) `core.mxenv-pip` body appears immediately after the `core.mxenv` body, (b) `PYTHON_PACKAGE_INSTALLER:=pip` and the macro definitions are present, (c) the `$(MXENV_TARGET)` rule is the linear pip recipe. Then copy the generated file over `src/mxmake/tests/expected/Makefile`.

- [ ] **Step 3: Verify pip fixture passes**

Run: `uv run pytest src/mxmake/tests/test_templates.py::TestTemplates::test_Makefile -q`
Expected: PASS

- [ ] **Step 4: Add a uv-variant test and fixture**

Add a new test method after `test_Makefile`:
```python
    @testing.temp_directory
    def test_Makefile_uv_variant(self, tempdir):
        domains = [topics.get_domain("core.mxenv-uv")]
        domains = topics.collect_missing_dependencies(domains)
        domains = topics.ensure_environment_variant(domains)
        topics.set_domain_runtime_depends(domains)
        domains = topics.resolve_domain_dependencies(domains)
        domains = topics.order_environment_variant(domains)
        domain_settings = {
            "core.base.DEPLOY_TARGETS": "",
            "core.base.RUN_TARGET": "",
            "core.base.CLEAN_FS": "",
            "core.base.INCLUDE_MAKEFILE": "include.mk",
            "core.base.EXTRA_PATH": "",
            "core.base.PROJECT_PATH_PYTHON": "",
            "core.mxenv.PRIMARY_PYTHON": "python3",
            "core.mxenv.PYTHON_MIN_VERSION": "3.10",
            "core.mxenv.VENV_ENABLED": "true",
            "core.mxenv.VENV_CREATE": "true",
            "core.mxenv.VENV_FOLDER": ".venv",
            "core.mxenv.MXDEV": "mxdev",
            "core.mxenv.MXMAKE": "mxmake",
            "core.mxenv-uv.UV_PYTHON": "$(PRIMARY_PYTHON)",
            "core.mxenv-uv.UV_PROVISION": "pip",
            "core.mxenv-uv.TOOL_EXECUTION": "uvx",
        }
        factory = templates.template.lookup("makefile")
        template = factory(
            tempdir, domains, domain_settings, templates.get_template_environment()
        )
        template.write()
        with (
            (tempdir / "Makefile").open() as result,
            (EXPECTED_DIRECTORY / "Makefile-uv").open() as expected,
        ):
            self.checkOutput(
                expected.read(), result.read(), optionflags=doctest.REPORT_UDIFF
            )
```

- [ ] **Step 5: Generate and save the uv fixture**

Run: `uv run pytest src/mxmake/tests/test_templates.py::TestTemplates::test_Makefile_uv_variant -q`
Expected: FAIL (fixture missing). The test writes the Makefile to a temp dir and the open of `Makefile-uv` raises FileNotFoundError. Temporarily add a `print("UV Makefile at", tempdir / "Makefile")` before the comparison if needed, inspect, verify the uv recipe + `TOOL_EXECUTION` macro branch + `PYTHON_PACKAGE_INSTALLER:=uv`, then copy the generated Makefile to `src/mxmake/tests/expected/Makefile-uv`. Remove any temporary print.

- [ ] **Step 6: Verify both fixtures pass**

Run: `uv run pytest src/mxmake/tests/test_templates.py -k Makefile -q`
Expected: PASS

- [ ] **Step 7: Fix test_parser expectations**

In `src/mxmake/tests/test_parser.py`, the two dicts asserting parsed settings include `core.mxenv.*` keys. Remove `core.mxenv.PYTHON_PACKAGE_INSTALLER` / `core.mxenv.UV_PYTHON` if present and remove the `core.mxenv.TOOL_RUNNER` line referenced from the abandoned PR if present. Run the parser tests:

Run: `uv run pytest src/mxmake/tests/test_parser.py -q`
Expected: PASS (adjust expected dicts to match the base's remaining settings if the test constructs a Makefile from `core.mxenv`; if it uses `core.mxenv-pip`, ensure the variant is included via the same helper sequence).

- [ ] **Step 8: Run the whole suite**

Run: `uv run pytest src/mxmake/tests/ -q`
Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add src/mxmake/tests/
git commit -m "Cover pip and uv environment variants in tests and fixtures"
```

### Task B7: Functional end-to-end check for both variants

**Files:** none (verification only)

- [ ] **Step 1: pip variant generates and installs**

```bash
tmp=$(mktemp -d); cd "$tmp"
printf 'topics:\n  core:\n    base: {}\n    mxenv: {}\n    mxenv-pip: {}\n  qa:\n    ruff: {}\n' > seeds.yaml
uv run --project /home/jensens/ws/cdev/mxmake mxmake init --preseeds seeds.yaml
grep -n "PYTHON_PACKAGE_INSTALLER:=pip" Makefile && grep -n "RUN_TOOL,ruff" Makefile
cd - >/dev/null
```
Expected: pip installer line and ruff macro call present; `core.mxenv-pip` body precedes `qa.ruff` body.

- [ ] **Step 2: uv variant generates with uvx default**

```bash
tmp=$(mktemp -d); cd "$tmp"
printf 'topics:\n  core:\n    base: {}\n    mxenv: {}\n    mxenv-uv: {}\n  qa:\n    ruff: {}\n' > seeds.yaml
uv run --project /home/jensens/ws/cdev/mxmake mxmake init --preseeds seeds.yaml
grep -n "PYTHON_PACKAGE_INSTALLER:=uv" Makefile && grep -n "RUN_TOOL=uvx" Makefile
cd - >/dev/null
```
Expected: uv installer line and `RUN_TOOL=uvx ...` (uvx default) present.

- [ ] **Step 3: Swap variant + update flips the world**

```bash
tmp=$(mktemp -d); cd "$tmp"
printf 'topics:\n  core:\n    base: {}\n    mxenv: {}\n    mxenv-pip: {}\n  qa:\n    ruff: {}\n' > seeds.yaml
uv run --project /home/jensens/ws/cdev/mxmake mxmake init --preseeds seeds.yaml
sed -i 's/^#: core.mxenv-pip/#: core.mxenv-uv/' Makefile
uv run --project /home/jensens/ws/cdev/mxmake mxmake update
grep -n "PYTHON_PACKAGE_INSTALLER:=uv" Makefile
cd - >/dev/null
```
Expected: after editing the recorded variant line and running update, the Makefile is regenerated with the uv variant.

- [ ] **Step 4: No commit (verification only). If any step fails, return to the relevant Phase B task.**

---

## Phase C — Documentation and release notes

### Task C1: Update CHANGES.md

**Files:**
- Modify: `CHANGES.md`

- [ ] **Step 1: Replace the abandoned uvx entry with the split entry**

Under the top version heading (bump to the next major, e.g. `## 3.0.0`), add:
```markdown
- Split `core.mxenv` into a shared base plus `core.mxenv-pip` and `core.mxenv-uv`
  environment variants. QA dev-tool execution now runs through environment-provided
  macros; the uv variant runs style/format tools via `uvx` by default.
  [2026-05-30]
```
Remove the superseded `TOOL_RUNNER` changelog entry if it is still present.

- [ ] **Step 2: Commit**

```bash
git add CHANGES.md
git commit -m "Changelog: mxenv variant split"
```

### Task C2: Add migration guide entry

**Files:**
- Modify: `docs/source/migration.md`

- [ ] **Step 1: Add a version section following the repository format**

```markdown
## Version 3.0.0 (unreleased)

### Changed: mxenv split into pip and uv variants

**Breaking Change**: The single `core.mxenv` domain is now a base that requires
exactly one environment variant: `core.mxenv-pip` or `core.mxenv-uv`. The
`PYTHON_PACKAGE_INSTALLER` and `UV_PYTHON` settings were removed from `core.mxenv`;
the installer is now determined by the selected variant.

**Before** (2.x):
```
PYTHON_PACKAGE_INSTALLER?=uv
UV_PYTHON?=3.14
```

**After** (3.0+): select the uv variant; configure `UV_PYTHON` on it.

**Migration**:
- Run `mxmake update`. Existing Makefiles with no variant get `core.mxenv-uv`
  injected automatically (the common case).
- To use pip instead, change `#: core.mxenv-uv` to `#: core.mxenv-pip` in the
  Makefile header and run `mxmake update`.
- Remove any manual `PYTHON_PACKAGE_INSTALLER` setting; it is now implied by the
  variant. Move `UV_PYTHON` to its position under the uv variant settings (update
  regenerates this for you).
- Style/format tools (ruff, isort, black, zpretty, pyupgrade) run via `uvx` by
  default under the uv variant. Set `TOOL_EXECUTION=venv` to install them into the
  environment instead. Type-checkers (mypy, ty, pyrefly) always install into the
  environment.
```

- [ ] **Step 2: Build docs link-check is not required; verify markdown renders by eye.**

- [ ] **Step 3: Commit**

```bash
git add docs/source/migration.md
git commit -m "Migration guide: mxenv variant split"
```

---

## Self-Review notes (for the implementer)

- **Spec coverage:** base+variants (B1-B3), exactly-one enforcement (B4-B5), parse-order safety via ordering (B4-B5), swap+update (B7 step 3), macro-based uniform tool files (A2-A6), uv `pip`/`sync` provisioning (B3 `UV_PROVISION`), uvx default + venv opt-in (B3 `TOOL_EXECUTION`), migration default uv (B4 `ENVIRONMENT_DEFAULT_VARIANT`), docs (C1-C2). Type-checker-under-uvx is resolved by design (type-checkers never use the ephemeral macros).
- **Regenerated fixtures:** `expected/Makefile` and `expected/Makefile-uv` are produced by running the generator and copying output, not hand-written — this avoids transcription errors in long Make output.
- **No new per-tool VERSION settings** (deferred, YAGNI). The `RUN_TOOL` version parameter exists in the macro signature for future use and is currently called with an empty value.
