#:[karma]
#:title = Karma tests
#:description = Run JavaScript tests using karma.
#:depends = js.npm
#:
#:[target.karma]
#:description = Run karma.
#:
#:[setting.KARMA_CONFIG]
#:description = Karma config file.
#:default = karma.conf.js
#:
#:[setting.KARMA_OPTIONS]
#:description = Karma additional command line options.
#:default = --single-run

##############################################################################
# karma
##############################################################################

# extend npm dev packages
NPM_DEV_PACKAGES+=karma karma-coverage karma-chrome-launcher karma-module-resolver-preprocessor

.PHONY: karma
karma:
	@$(NPM_PREFIX)/node_modules/karma/bin/karma start $(KARMA_CONFIG) $(KARMA_OPTIONS)