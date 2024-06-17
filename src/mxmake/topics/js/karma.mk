#:[karma]
#:title = Karma tests
#:description = Run JavaScript tests using karma.
#:depends = js.nodejs
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

NODEJS_DEV_PACKAGES+=\
	karma \
	karma-coverage \
	karma-chrome-launcher \
	karma-module-resolver-preprocessor

.PHONY: karma
karma: $(NODEJS_TARGET)
	@karma start $(KARMA_CONFIG) $(KARMA_OPTIONS)
