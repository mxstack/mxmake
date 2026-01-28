# Generate files using templates

The `mxfiles` domain generates files for various purposes based on information from the "mxdev" and "mxmake" environment.

It utilizes [Jinja2]() templates.

It is used for general purpose internal file generation and also can be used for custom file generation.

## Internal templates

Internally it is used to generate base files on `mxmake init` respective `mxmake update`.

General templates, not attached to any domain:

- `Makefile`
- `mx.ini`

Gets information from `mx.ini` and is copied to virtualenv folder by `core.mxfiles` domain if present:
- `pip.conf`

General, used in `core.packages` with source package information from `mx.ini`:
- `additional_source_targets.mk`

Used only in Sphinx extension, gets information from topic and domain metadata:
- `topics.md`

Gets information from `mx.ini` and is used by `qa.tests` or `qa.coverage` domains:
- `env.sh`
- `run-tests.sh`
- `run-coverage.sh`

```{todo}
Add detailed documentation of run-tests.sh and run-coverage.sh
```

## How to write custom templates

Custom templates can be defined through the use of either pure Jinja2 templates and the configuration environment in mx.ini or by writing Python code which offers enhanced capabilities.

### Templates defined via mx.ini with Jinja2

Some templates are configured and triggered via the `mx.ini` file. The most common example is test and coverage scripts.

**Configuration in mx.ini**:

```ini
[settings]
mxmake-templates =
    run-tests
    run-coverage

# Optional: Configure template-specific settings
mxmake-test-path = src
mxmake-source-path = src/mypackage
```

**Available built-in templates**:
- `run-tests` - Generate test runner script
- `run-coverage` - Generate coverage script
- `pip-conf` - Generate pip configuration
- `plone-site` - Generate Plone site creation script

These templates are generated automatically when you run `make install` or `make mxfiles`.

### Templates based on Python code

For advanced use cases, you can create templates using Python code. This provides full control over template generation and allows integration with the mxmake/mxdev environment.

**Basic template class structure**:

```python
from mxmake.templates import template, Template

@template("my-template")
class MyTemplate(Template):
    description: str = "My custom template"
    target_name: str = "output.txt"
    template_name: str = "my-template.j2"
    target_folder = Path("custom")

    @property
    def template_variables(self) -> dict:
        return {
            "project_name": "myproject",
            "custom_value": "example"
        }
```

**Key components**:
- `@template("name")` - Register the template with a unique name
- `target_name` - Filename of the generated file
- `template_name` - Name of the Jinja2 template file in `src/mxmake/templates/`
- `template_variables` - Dictionary of variables available in the template
- `target_folder` - Directory where the file will be generated

**Using MxIniBoundTemplate** for mx.ini integration:

```python
from mxmake.templates import template, MxIniBoundTemplate

@template("custom-conf")
class CustomConf(MxIniBoundTemplate):
    # Access mx.ini settings via self.settings
    @property
    def template_variables(self) -> dict:
        return {
            "packages": self.settings.get("main-package", "")
        }
```

For complete examples, see the [templates.py source code](https://github.com/mxstack/mxmake/blob/main/src/mxmake/templates.py).
