#:[cookiecutter]
#:title = cookiecutter
#:description = Tool to generate skeletons and configuration from cookiecutter templates.
#:depends = core.mxenv
#:
#:[target.cookiecutter]
#:description = Installs cookiecutter.
#:

##############################################################################
# cookiecutter
##############################################################################

COOKIECUTTER_TARGET:=$(SENTINEL_FOLDER)/cookiecutter.sentinel
$(COOKIECUTTER_TARGET): $(MXENV_TARGET)
	@echo "Install cookiecutter"
	@$(MXENV_PATH)pip install "cookiecutter>=2.1.1"
	@touch $(COOKIECUTTER_TARGET)
