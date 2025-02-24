#:[help]
#:title = Help System
#:description = A system to provide the user of the Makefile an overview of the targets
#:              and all environment variable based arguments.
#:
#:depends = core.mxenv
#:
#:[target.help]
#:description = Print help for the Makefile.
#:
#:[setting.HELP_DOMAIN]
#:description = Request to show all targets, descriptions and arguments for a given domain.
#:default =
#:

##############################################################################
# help
##############################################################################

.PHONY: help
help: $(MXENV_TARGET)
	@mxmake help-generator
