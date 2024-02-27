#:[nvm]
#:title = Node Version Manager
#:description = Provide targets for working with Node Version Manager
#:depends = core.base
#:
#:[target.nvm]
#:description = Ensure nodejs version defined in `NVM_VERSION` is installed and
#:  used.
#:
#:[setting.NVM_VERSION]
#:description = Version of nodejs to use
#:default = v18.19.0

##############################################################################
# nvm
##############################################################################

JS_TARGETS+=nvm

.PHONY: nvm
nvm:
	@. $(HOME)/.nvm/nvm.sh
	@nvm current | grep -q $(NVM_VERSION) || nvm install $(NVM_VERSION)
	@nvm current | grep -q $(NVM_VERSION) || nvm use $(NVM_VERSION)
