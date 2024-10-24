# Preseeds

It is possible to pass configuration preseeds when creating a new project
with `mxmake init`. This is useful if you have recurring default settings
when creating projects with `mxmake`.

Preseeds are contained in yaml files and have the following format:

```yaml
# topics to include
topics:
  # include topic core
  core:
    # include domain mxenv
    mxenv:
      # set PYTHON_MIN_VERSION and PYTHON_PACKAGE_INSTALLER
      PYTHON_MIN_VERSION: 3.10
      PYTHON_PACKAGE_INSTALLER: uv
  qa:
    # include domains from qa topic but do not override default settings
    ruff:
    test:
    coverage:
# generate mx ini if not exists
mx-ini: true
# generate CI files from templates
ci-templates:
- gh-actions-test
```

Now initialize the project with the preseeds:

```shell
$ mxmake init -p preseeds.yaml
```
