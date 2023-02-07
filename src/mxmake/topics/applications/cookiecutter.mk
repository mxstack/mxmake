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
	@$(MXENV_PATH)pip install "cookiecutter>=2.1.1"
	@touch $(COOKIECUTTER_TARGET)

.PHONY: cookiecutter-dirty
cookiecutter-dirty:
	@rm -f $(COOKIECUTTER_TARGET)

.PHONY: cookiecutter-clean
cookiecutter-clean: cookiecutter-dirty
	@test -e $(MXENV_PATH)pip && $(MXENV_PATH)pip uninstall -y cookiecutter || :
	@rm -f $(COOKIECUTTER_TARGET)

DIRTY_TARGETS+=cookiecutter-dirty
CLEAN_TARGETS+=cookiecutter-clean
