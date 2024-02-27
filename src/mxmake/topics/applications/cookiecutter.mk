#:[cookiecutter]
#:title = cookiecutter
#:description = Tool to generate skeletons and configuration from cookiecutter templates.
#:depends = core.packages
#:
#:[target.cookiecutter]
#:description = Install cookiecutter.
#:
#:[target.cookiecutter-dirty]
#:description = Marks cookiecutter dirty.
#:
#:[target.cookiecutter-clean]
#:description = Uninstall cookiecutter.
#:

##############################################################################
# cookiecutter
##############################################################################

COOKIECUTTER_TARGET:=$(SENTINEL_FOLDER)/cookiecutter.sentinel
$(COOKIECUTTER_TARGET): $(MXENV_TARGET)
	@echo "Install cookiecutter"
	@$(PYTHON_PACKAGE_COMMAND) install "cookiecutter>=2.6.0"
	@touch $(COOKIECUTTER_TARGET)

.PHONY: cookiecutter
cookiecutter: $(COOKIECUTTER_TARGET)

.PHONY: cookiecutter-dirty
cookiecutter-dirty:
	@rm -f $(COOKIECUTTER_TARGET)

.PHONY: cookiecutter-clean
cookiecutter-clean: cookiecutter-dirty
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y cookiecutter || :
	@rm -f $(COOKIECUTTER_TARGET)

DIRTY_TARGETS+=cookiecutter-dirty
CLEAN_TARGETS+=cookiecutter-clean
