# Extending mxmake

## Topics and domains

The features provided by *mxmake* are organized into "domains," which are grouped together under "topics."
Each domain offers a collection of settings and targets for the make process and may have dependencies on other domains.

## Writing custom domains

*mxmake* treats all files with `.mk` suffix inside a topic folder as a domain.
To extend an existing topic, add a file named `yourdomain.mk`.
It will be integrated automatically.

To create a new `topic` create a folder containing a file named `metadata.ini` providing topic title and description:

```ini
[metadata]
title = Topic title
description = Topic topic description.
```

Then its required to create a `Topic` object in python:

```python
mytopic = Topic(name="mytopic", directory=os.path.join(topics_dir, "mytopic"))
```

And finally this topic needs to be registered as package entry point in `pyproject.toml`:

```toml
[project.entry-points."mxmake.topics"]
mytopic = "mxmake.topics:mytopic"
```

### The domain makefile

The domain file provides a title and description, it's dependencies, the available settings with default values and a set of make targets.

#### The domain header

The documentation and available settings and it's default values are extracted from the domain file header.
Each line starting with `#:` gets interpreted as `ini` format and read with `configparser`.

The essential base information of each domain looks like this:

```makefile
#:[mydomain]
#:title = Domain title
#:description = Domain description
#:depends =
#:    topic.domain
#:    topic.otherdomain
#:soft-depends = topic.domain
```

The main section gets named after the `domain` name, and forms in conjunction with `topic` name the full qualified name, or FQN.

The FQN is used to declare dependencies.
`depends` contain the hard dependencies, which are all domains required to run the domain's targets.
`soft-depends` defines domains which are optional, but if present need to be loaded first to make optional features work properly.

All sections prefixed with `target.`  describe the public API of the domain.
It gets used for generating the documentation and as help text on the CLI.

A target definition looks like this:

```ini
#:[target.mydomain]
#:description = Target description.
```

All sections prefixed with `setting.` define a domain specific setting.
Setting names must be unique among all domains.
Settings usually provide a senceful default.
All settings from all domains gets rendered into the final Makefile before the domains gets rendered.
They are editable, setting values are parsed when updating the Makefile.

A setting definition looks like this:

```ini
#:[setting.SETTING_NAME]
#:description = Setting description. Gets used for documentation generation and as help text on the CLI.
#:default = default_value
```

#### Target naming conventions

All domains included in `mxmake` follow a target naming convention.
You are `encouraged` to follow this convention when writing domains to keep usage of the domain intuitive.

The following naming should be taken into account:

: `domainname`

  : The main target is named after the domain.
    It is responsible to execute the tasks the domain is dedicated to, like running a linter, starting an application, etc.

: `domainname-dirty`

  : Targets postfixed with `-dirty` are supposed to modify the filsystem in a way that next time make runs the main target the domain dependencies are reinstalled.

: `domainname-clean`

  : Targets postfixed with `-clean` are supposed to remove domain related files and uninstall domain related tools.

: `domainname-purge`

  : Targets postfixed with `-purge` are supposed to perform the same steps as the `clean` target does, additionally removing runtime data.

#### The domain sentinel

Since *make* keeps track of file modification timestamps, installation related targets should be bound to some installation related file(s).
This ensures that targets are not run if not necessary.

```{note}
Sometimes there are no reliable files created to depend on, therefor sentinel files are used.
```

[Sentinel files](make-sentinel-files) are created during installation, and removed on `dirty` and `clean`, to mimic the behavior of depending on "real" domain related files.

The basic pattern for using a sentinel file is shown here by installing a python package with pip:

```makefile
# this is our sentinel file
DOMAIN_TARGET:=$(SENTINEL_FOLDER)/domain.sentinel

# The sentinel file is defined as target and depends on the existence of
# the MXENV_TARGET, which ensures the correct execution environment.
# Once we installed our package, we `touch` the sentinel file, which creates
# the file if it not exists. Each make run now skips the install step as long
# as the sentinel file ist not modified or remove.
$(DOMAIN_TARGET): $(MXENV_TARGET)
	@echo "Install Package"
	@$(MXENV_PATH)pip install package
	@touch $(DOMAIN_TARGET)

# The main domain target depends on the sentinel, causing the package to be
# installed if the sentinel not exists or has been modified since last make run.
.PHONY: domain
domain: $(DOMAIN_TARGET)
	@echo "Do something with the installed package"

# In the `dirty` target, we remove the sentinel, which causes make to run the
# install steps next time make builds a target which depends on our sentinel.
.PHONY: domain-dirty
domain-dirty:
	@rm -f $(DOMAIN_TARGET)

# The `clean` target simply depends on the `dirty` target which removes the
# sentinel and additionally uninstalls the installed package.
.PHONY: domain-clean
domain-clean: domain-dirty
	@test -e $(MXENV_PATH)pip && $(MXENV_PATH)pip uninstall -y package || :
```

#### Extending default targets

`mxmake` generates a set of default targets where domain related targets can hook themselves up.

: `install`

  : To cause a domain related target to run on `make install`, `INSTALL_TARGETS` must be extended, e.g. `INSTALL_TARGETS+=domain-install`.

: `deploy`

  : To cause a domain related target to run on `make deploy`, `DEPLOY_TARGETS` must be extended, e.g. `DEPLOY_TARGETS+=domain-deploy`.

: `dirty`

  : To cause a domain related target to run on `make dirty`, `DIRTY_TARGETS` must be extended, e.g. `DIRTY_TARGETS+=domain-dirty`.

: `clean`

  : To cause a domain related target to run on `make clean`, `CLEAN_TARGETS` must be extended, e.g. `CLEAN_TARGETS+=domain-clean`.

: `purge`

  : To cause a domain related target to run on `make purge`, `PURGE_TARGETS` must be extended, e.g. `PURGE_TARGETS+=domain-purge`.

: `check`

  : `check` target is `qa` topic related and only gets generated if one or more domains from the `qa` topic are included.
    To cause a domain related target to run on `make check`, `CHECK_TARGETS` must be extended, e.g. `CHECK_TARGETS+=domain-check`.

: `format`

  : `format` target is `qa` topic related and only gets generated if one or more domains from the `qa` topic are included.
    To cause a domain related target to run on `make format`, `FORMAT_TARGETS` must be extended, e.g. `FORMAT_TARGETS+=domain-format`.
