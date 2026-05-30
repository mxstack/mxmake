# Design: Split mxenv into pip and uv environment variants

**Date:** 2026-05-30
**Status:** Approved (pending spec review)
**Target:** New major release (breaking changes permitted)

## Motivation

The current `core.mxenv` domain supports both pip and uv installation in a single
`.mk` file through accumulated runtime `ifeq` branching (uv availability detection,
global-vs-local uv, package-installer selection). A proposed change to run QA tools
via `uvx` added a further orthogonal runtime toggle threaded through every QA tool
file, multiplying the conditional boilerplate.

The accumulated branching is hard to read and maintain. uv is now the common path
for most setups, and the upstream dependency manager gained `uv sync` support, so a
clean separation is timely. pip support is retained as a deliberate fallback (we do
not want to be unable to switch away from uv), not dropped.

## Two separable concerns

The redesign is built on recognizing that two independent concerns were previously
entangled:

1. **Environment + application/dependency provisioning** — installing the software
   that must live *in* the environment to run (the project itself, applications such
   as Zope or a web application, runtime dependencies). This is the pip-vs-uv split.
2. **Dev-tool execution** — running tools that operate *on* the code (ruff, mypy, ty,
   isort, black, …). These need not be part of the runtime and can be executed
   ephemerally. This is the venv-install-vs-uvx mechanism, and it applies only to the
   `qa` tools.

These are orthogonal: an application is always installed via the environment's
installer; a dev tool may be installed or run ephemerally. The previous approach
conflated "using uv" with "running tools via uvx"; they are decoupled here.

## Architecture

### Concern 1: three domains replacing the single mxenv

```
core.mxenv          (base)     <- every other domain depends on this (unchanged)
  core.mxenv-pip    (variant)  depends = core.mxenv
  core.mxenv-uv     (variant)  depends = core.mxenv
```

- **`core.mxenv` (base)** holds everything mode-independent and declares the interface
  the variants fill in:
  - venv path computation, sentinel folder, validation, `MXENV_PYTHON`
  - `INSTALL_TARGETS` / `CHECK_TARGETS` / `FORMAT_TARGETS` / etc. plumbing
  - `MXENV_TARGET := …` (the *variable*, so other domains can list it as a prerequisite)
  - the interface contract macros, defined by the active variant:
    `PYTHON_PACKAGE_COMMAND`, `RUN_TOOL`, `INSTALL_TOOL`, `UNINSTALL_TOOL`
- **`core.mxenv-pip`** — `python -m venv` + `ensurepip`; `pip install` for app/deps;
  QA tools installed into the venv and invoked directly.
- **`core.mxenv-uv`** — `uv venv`; provisioning via `uv pip install` (default) or
  `uv sync` (opt-in), selected by a setting; QA tools executed via `uvx` by default.

**Seam between base and variant:** the base declares `MXENV_TARGET :=` and the macro
*names*; the variant provides the `$(MXENV_TARGET):` rule body and the macro
*definitions*. Because the macros are used only inside recipes (recursively expanded
at run time), the order in which domains are emitted into the Makefile does not affect
correctness.

### Concern 2: QA tool execution via variant-defined macros

QA tool files become uniform and world-agnostic — no `ifeq`, no `eval`,
no per-tool branching:

```makefile
RUFF_TARGET := $(SENTINEL_FOLDER)/ruff.sentinel
$(RUFF_TARGET): $(MXENV_TARGET)
	@$(call INSTALL_TOOL,ruff)
	@touch $@

ruff-check: $(RUFF_TARGET)
	@$(call RUN_TOOL,ruff,$(RUFF_VERSION),check $(RUFF_SRC))

ruff-clean: ruff-dirty
	@$(call UNINSTALL_TOOL,ruff)
	@rm -rf .ruff_cache
```

The variant defines what the macros expand to:

| Mode | `INSTALL_TOOL(name)` | `RUN_TOOL(name,ver,args)` | `UNINSTALL_TOOL(name)` |
|------|----------------------|---------------------------|------------------------|
| pip variant | `$(PYTHON_PACKAGE_COMMAND) install $(1)` | `$(1) $(3)` | pip uninstall |
| uv variant — uvx (default) | `:` (no-op) | `uvx $(1)$(if ver,==ver) $(3)` | `:` (no-op) |
| uv variant — venv (opt-in) | `uv pip install $(1)` | `$(1) $(3)` | uv pip uninstall |

In the uvx default, `INSTALL_TOOL` is a no-op; the sentinel target still exists and is
still touched (an empty marker — harmless) and still depends on `$(MXENV_TARGET)`, so
the environment is guaranteed present before any tool runs.

Applications and runtime dependencies never use these macros; they install via
`PYTHON_PACKAGE_COMMAND` from the active variant.

Only the pure style/format tools (ruff, isort, black, zpretty, pyupgrade) use the
ephemeral-capable macros. Type-checking tools (mypy, ty, pyrefly) always install into
the environment via `PYTHON_PACKAGE_COMMAND` (which becomes `uv pip` in the uv
variant); they are never executed via uvx, because they require the project's
installed dependencies to resolve against.

## Variant selection and enforcement

The base is abstract: selecting it (transitively, via any domain's
`depends = core.mxenv`) does not pull in a variant. Exactly one variant must be
present. The domain system has no built-in "exactly one of" relation, so a small
amount of resolver/init logic is added:

- **init** requires choosing a variant; default `core.mxenv-uv`.
- **update** preserves whichever variant the existing Makefile records.
- If a Makefile records the base with no variant (migration case), inject the default
  variant and emit a warning.
- Reject a selection containing more than one variant.

## Switching between variants

Switching is a domain swap plus an update:

1. Edit the recorded-domains header in the Makefile: change `#: core.mxenv-pip` to
   `#: core.mxenv-uv` (or vice versa).
2. Run `mxmake update`.

The Makefile parser re-reads the `#: <fqn>` header lines, re-resolves dependencies,
and re-renders. Settings belonging only to the previous variant drop out; the new
variant's settings appear with defaults. No parser change is required for the swap
itself — only the enforcement logic above.

## Settings

- New on the uv variant: a setting selecting `uv pip install` (default) vs `uv sync`
  provisioning.
- New on the uv variant: a setting selecting `uvx` (default) vs venv install for QA
  tool execution.
- Per-tool version-pinning settings are deferred (YAGNI). The `RUN_TOOL` macro keeps a
  version parameter in its signature for future use; tool files currently call it with
  an empty value.

## Migration (major release)

- Existing Makefiles list `core.mxenv` with no variant. On the first `mxmake update`
  after this release, the default variant `core.mxenv-uv` is injected. Most existing
  setups already use the uv path, so this matches reality; the pip variant remains
  available by swapping.
- This is a breaking change and requires an entry in `docs/source/migration.md`
  following the repository's migration-guide format (Before/After/Migration steps),
  matching the major version in `CHANGES.md`.
- The previous single-toggle approach to running tools via uvx is superseded by this
  split and is removed.

## Resolved: type checkers and project dependencies

Type-checking tools (mypy, ty, pyrefly) must resolve against the project's installed
dependencies, which an ephemeral uvx environment would not contain. This is resolved
by design: type-checkers are excluded from the uvx path entirely. They always install
into the environment via the active variant's `PYTHON_PACKAGE_COMMAND` (`uv pip` in the
uv variant), so they run against the project venv. Only the pure style/format tools
(ruff, isort, black, zpretty, pyupgrade), which do not need project deps, use the
uvx-capable macros.

## Testing

Use generated-Makefile fixtures where a full rendered comparison adds value (e.g. one
per variant); otherwise prefer focused assertions over snapshot fixtures.

- Per-variant rendered-Makefile fixtures (pip and uv) where a full comparison is
  warranted.
- Parser/template tests covering both variants' settings.
- Verify the swap path: parser reads the new variant, drops old-variant settings, adds
  new-variant defaults.
- Verify dependency resolution pulls in the base plus exactly one variant; verify the
  enforcement rejects zero or two variants.
- Verify QA tool files render identically regardless of variant (only the macro
  expansions differ).
- Verify type-checkers (mypy, ty, pyrefly) install into the environment under the uv
  variant (not executed via uvx).

## Out of scope / follow-ups

- Deeper `uv sync` workflow integration beyond providing it as a provisioning option.
- Reworking non-QA topics; they consume `PYTHON_PACKAGE_COMMAND` and are unaffected
  beyond depending on the base.
