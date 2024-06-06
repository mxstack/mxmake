#:[plone]
#:title = plone
#:description = Plone application related
#:depends = applications.zope
#:[target.plone-createsite]
#:description = Creates a Plone site using the script provided in `PLONE_CREATESITE_SCRIPT` configuration.
#:
#:[setting.PLONE_CREATESITE_SCRIPT]
#:description = Path to the script to create a Plone site
#:default = .mxmake/files/plone-createsite.py
#:
#:[target.plone-createsite-dirty]
#:description = Touches the sentinel file to force a rebuild of the Plone instance. This will not touch the database.
#:
#:[target.plone-createsite-clean]
#:description = Removes the sentinel file to force files but keeps Plone database.
#:
#:[target.plone-createsite-purge]
#:description = Removes the Plone instance from the database, but the database itself is kept.


##############################################################################
# plone
##############################################################################

PLONE_CREATESITE_SENTINEL:=$(SENTINEL_FOLDER)/plone-createsite.sentinel

PLONE_CREATESITE_TARGET: $(FILES_TARGET) $(ZOPE_RUN_TARGET)

.PHONY: plone-createsite
plone-createsite: PLONE_CREATESITE_TARGET
	@echo "Creating Plone Site"
	@touch $(PLONE_CREATESITE_SENTINEL)
	@zconsole run $(ZOPE_INSTANCE_FOLDER)/etc/zope.conf $(PLONE_CREATESITE_SCRIPT)

.PHONY: plone-createsite-dirty
plone-createsite-dirty:
	@touch $(PLONE_CREATESITE_SENTINEL)

.PHONY: plone-createsite-clean
plone-createsite-clean:
	@touch $(PLONE_CREATESITE_SENTINEL)
