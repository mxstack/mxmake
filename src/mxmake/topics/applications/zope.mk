#:[zope]
#:title = zope
#:description = Zope and Plone application related
#:depends = applications.cookiecutter
#:
#:[target.zope-instance]
#:description = Use cookiecutter-zope-instance to create Zope- and its WSGI-configuration from values of the cookiecutter configuration file.
#:
#:[setting.ZOPE_CONFIGURATION_FILE]
#:description = cookiecutter configuration file to use
#:default = instance.yaml
#:
#:[setting.ZOPE_TEMPLATE]
#:description = cookiecutter configuration file to use
#:default = https://github.com/plone/cookiecutter-zope-instance
#:
#:[setting.ZOPE_TEMPLATE_CHECKOUT]
#:description = cookiecutter branch, tag or commit to checkout from the ZOPE_TEMPLATE. If empty, `--checkout` is not passed to cookiecutter.
#:default = main
#:
#:[setting.ZOPE_BASE_FOLDER]
#:description = The Zope folder "instance" will be generated relative to this existing folder.
#:default = .
#:
#:[target.zope-start]
#:description = Start Zope/Plone WSGI server.
#:
#:[target.zope-debug]
#:description = Start Zope/Plone debug console.
#:
#:[target.zope-runscript]
#:description = Run a script within Zope/plone context.
#:   ZOPE_SCRIPTNAME must be set to the script to run.
#:   This can be done by setting the environment variable or by setting the make variable in the header.
#:	 Example: `make ZOPE_SCRIPTNAME=./my-script.py zope-runscript`
#:
#:[setting.ZOPE_SCRIPTNAME]
#:description = script to run
#:
#:[target.zope-dirty]
#:description = Touches the configuration file to force a rebuild of the Zope instance.
#:
#:[target.zope-clean]
#:description = Removes generated configuration files but keeps Zope database.
#:
#:[target.zope-purge]
#:description = Removes the whole Zope instance folder including database.
#:


##############################################################################
# zope
##############################################################################

ZOPE_INSTANCE_FOLDER:=$(ZOPE_BASE_FOLDER)/instance
ZOPE_INSTANCE_TARGET:=$(ZOPE_INSTANCE_FOLDER)/etc/zope.ini $(ZOPE_INSTANCE_FOLDER)/etc/zope.conf $(ZOPE_INSTANCE_FOLDER)/etc/site.zcml

ifeq (,$(ZOPE_TEMPLATE_CHECKOUT))
	ZOPE_COOKIECUTTER_TEMPLATE_OPTIONS=
else
	ZOPE_COOKIECUTTER_TEMPLATE_OPTIONS=--checkout $(ZOPE_TEMPLATE_CHECKOUT)
endif

${ZOPE_CONFIGURATION_FILE}:
	@touch ${ZOPE_CONFIGURATION_FILE}

$(ZOPE_INSTANCE_TARGET): $(COOKIECUTTER_TARGET) $(ZOPE_CONFIGURATION_FILE)
	@echo Create Plone/Zope configuration from $(ZOPE_TEMPLATE) to $(ZOPE_INSTANCE_FOLDER)
	@cookiecutter -f --no-input ${ZOPE_COOKIECUTTER_TEMPLATE_OPTIONS} --config-file $(ZOPE_CONFIGURATION_FILE) --output-dir $(ZOPE_BASE_FOLDER) $(ZOPE_TEMPLATE)

.PHONY: zope-instance
zope-instance: $(ZOPE_INSTANCE_TARGET) $(SOURCES)

.PHONY: zope-start
zope-start: $(ZOPE_INSTANCE_TARGET) $(PACKAGES_TARGET)
	@echo "Start Zope/Plone with configuration in $(ZOPE_INSTANCE_FOLDER)"
	@runwsgi -v "$(ZOPE_INSTANCE_FOLDER)/etc/zope.ini"

.PHONY: zope-debug
zope-debug: $(ZOPE_INSTANCE_TARGET) $(PACKAGES_TARGET)
	@echo "Start Zope/Plone with configuration in $(ZOPE_INSTANCE_FOLDER)"
	@zconsole debug "$(ZOPE_INSTANCE_FOLDER)/etc/zope.ini"

.PHONY: zope-runscript
zope-runscript: $(ZOPE_INSTANCE_TARGET) $(PACKAGES_TARGET)
	@echo "Run Zope/Plone Console Script $(ZOPE_SCRIPTNAME) in $(ZOPE_INSTANCE_FOLDER)"
	@zconsole run "$(ZOPE_INSTANCE_FOLDER)/etc/zope.ini" $(ZOPE_SCRIPTNAME)

.PHONY: zope-dirty
zope-dirty:
	@touch ${ZOPE_CONFIGURATION_FILE}

.PHONY: zope-clean
zope-clean:
	@touch ${ZOPE_CONFIGURATION_FILE}
	@rm -rf $(ZOPE_INSTANCE_FOLDER)/etc $(ZOPE_INSTANCE_FOLDER)/inituser

.PHONY: zope-purge
zope-purge: zope-dirty
	@rm -rf $(ZOPE_INSTANCE_FOLDER)

INSTALL_TARGETS+=zope-instance
DIRTY_TARGETS+=zope-dirty
CLEAN_TARGETS+=zope-clean
