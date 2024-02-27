#:[lingua]
#:title = Lingua
#:description = Extract translatable texts from your code.
#:depends =
#:    core.mxenv
#:    i18n.gettext
#:
#:[target.lingua-extract]
#:description = Extract translatable texts from your code.
#:
#:[target.lingua]
#:description = Extract translatable texts from your code and create,
#:    update and compile message catalogs.
#:
#:[setting.LINGUA_SEARCH_PATH]
#:description = Path of directory to extract translatable texts from.
#:default = src
#:
#:[setting.LINGUA_PLUGINS]
#:description = Python packages containing lingua extensions.
#:default =

##############################################################################
# lingua
##############################################################################

LINGUA_TARGET:=$(SENTINEL_FOLDER)/lingua.sentinel
$(LINGUA_TARGET): $(MXENV_TARGET)
	@echo "Install Lingua"
	@$(PYTHON_PACKAGE_COMMAND) install chameleon lingua $(LINGUA_PLUGINS)
	@touch $(LINGUA_TARGET)

PHONY: lingua-extract
lingua-extract: $(LINGUA_TARGET)
	@echo "Extract messages"
	@pot-create \
		"$(LINGUA_SEARCH_PATH)" \
		-o "$(GETTEXT_LOCALES_PATH)/$(GETTEXT_DOMAIN).pot"

PHONY: lingua
lingua: gettext-create lingua-extract gettext-update gettext-compile

.PHONY: lingua-dirty
lingua-dirty:
	@rm -f $(LINGUA_TARGET)

.PHONY: lingua-clean
lingua-clean: lingua-dirty
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y \
		chameleon lingua $(LINGUA_PLUGINS) || :

INSTALL_TARGETS+=$(LINGUA_TARGET)
DIRTY_TARGETS+=lingua-dirty
CLEAN_TARGETS+=lingua-clean
