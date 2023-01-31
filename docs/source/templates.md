# Generate files using templates

The `mxfiles` domain generates files for various purposes based on information from the "mxdev" and "mxmake" environment.

It utilizes [Jinja2]() templates.

It is used for general purpose internal file generation and also can be used for custom file generation.

## Internal templates

Internally it is used to generate base files on `mxmake init`.

General templates, not attached to any domain:

- `Makefile`
- `mx.ini`

General, used in `core.packages` with source package information from `mx.ini`:
- `additional_source_targets.mk`

Used only in Sphinx extension, gets information from topic and domain metadata:
- `topics.md`

Gets information from` mx.ini` and is used by `qa.tests` or `qa.coverage` domains.
- `env.sh`
- `run-tests.sh`
- `run-coverage.sh`

```{todo}
Add detailed documentation of run-tests.sh and run-coverage.sh
```

## How to write custom templates

Custom templates can be defined through the use of either pure Jinja2 templates and the configuration environment in mx.ini or by writing Python code which offers enhanced capabilities.

### Templates defined via mx.ini with Jinja2

```{todo}
Contribute to this documentation!
```

### Templates based on Python code

```{todo}
Contribute to this documentation!
```
