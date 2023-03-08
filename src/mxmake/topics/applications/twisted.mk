#:[twisted]
#:title = Twisted Server
#:description = Install and start Twisted Server.
#:depends = core.packages
#:
#:[target.twisted-start]
#:description = Run Twisted Server
#:
#:[setting.TWISTED_TWISTD_OPTIONS]
#:description = The Twisted Application Configuration file.
#:default = -ny
#:
#:[setting.TWISTED_TAC_FILE]
#:description = The Twisted Application Configuration file.
#:default = twisted.tac

##############################################################################
# twisted
##############################################################################

TWISTED_TARGET:=$(SENTINEL_FOLDER)/twisted.sentinel
$(TWISTED_TARGET): $(MXENV_TARGET)
	@echo "Install twisted"
	@$(MXENV_PATH)pip install Twisted
	@touch $(TWISTED_TARGET)

.PHONY: twisted-start
twisted-start: $(TWISTED_TARGET)
	@echo "Run Twisted"
	@$(MXENV_PATH)twistd $(TWISTED_TWISTD_OPTIONS) $(TWISTED_TAC_FILE)
