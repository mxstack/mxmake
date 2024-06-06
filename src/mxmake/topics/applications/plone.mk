#:[plone]
#:title = plone
#:description = Plone application related
#:depends = applications.zope
#:[target.plone-site-create]
#:description = Creates a Plone site using the script provided in `PLONE_SITE_SCRIPT` configuration.
#:
#:[setting.PLONE_SITE_SCRIPT]
#:description = Path to the script to create or purge a Plone site
#:default = .mxmake/files/plone-site.py
#:
#:[target.plone-site-dirty]
#:description = Touches the sentinel file to force a rebuild of the Plone instance. This will not touch the database.
#:
#:[target.plone-site-clean]
#:description = Removes the sentinel file to force files but keeps Plone database.
#:
#:[target.plone-site-purge]
#:description = Removes the Plone instance from the database, but the database itself is kept.


##############################################################################
# plone
##############################################################################

PLONE_SITE_TARGET: $(FILES_TARGET) $(ZOPE_RUN_TARGET)

.PHONY: plone-site-create
plone-site-create: PLONE_SITE_TARGET
	@echo "Creating Plone Site"
	@zconsole run $(ZOPE_INSTANCE_FOLDER)/etc/zope.conf $(PLONE_SITE_SCRIPT)

plone-site-purge: PLONE_SITE_TARGET
	@echo "Purging Plone Site"
	@export PLONE_SITE_PURGE=True
	@zconsole run $(ZOPE_INSTANCE_FOLDER)/etc/zope.conf $(PLONE_SITE_SCRIPT)

.PHONY: plone-site-dirty
plone-site-dirty:
	@touch $(PLONE_SITE_SENTINEL)

.PHONY: plone-site-clean
plone-site-clean:
	@touch $(PLONE_SITE_SENTINEL)
