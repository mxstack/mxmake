#:[wtr]
#:title = Web test runner
#:description = Run JavaScript tests using web test runner.
#:depends = js.nodejs
#:
#:[target.wtr]
#:description = Execute web test runner.
#:
#:[setting.WTR_CONFIG]
#:description = Web test runner config file.
#:default = wtr.config.mjs
#:
#:[setting.WTR_OPTIONS]
#:description = Web test runner additional command line options.
#:default = --coverage

##############################################################################
# web test runner
##############################################################################

NODEJS_DEV_PACKAGES+=\
	@web/test-runner \
	@web/dev-server-import-maps

.PHONY: wtr
wtr: $(NODEJS_TARGET)
	@web-test-runner $(WTR_OPTIONS) --config $(WTR_CONFIG)
